from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulário de autenticação com classes Bootstrap 5.3 e mensagens claras."""

    username = forms.CharField(
        label="Nome de usuário",
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "placeholder": "Seu usuário"}
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "Sua senha"}
        ),
    )

    error_messages = {
        "invalid_login": "Usuário ou senha inválidos. Verifique os dados e tente novamente.",
        "inactive": "Esta conta está inativa.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            classes = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = f"{classes} form-control".strip()
        if self.is_bound:
            for nome in self.fields:
                if self[nome].errors or self.non_field_errors():
                    self.fields[nome].widget.attrs["class"] += " is-invalid"


class CadastroPacienteForm(forms.Form):
    """Dados necessários para criar uma conta pública de paciente."""

    username = forms.CharField(
        label="Nome de usuário",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username", "placeholder": "Escolha um nome de usuário"}),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "voce@exemplo.com"}),
    )
    nome = forms.CharField(
        label="Nome completo",
        max_length=70,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    cpf = forms.CharField(
        label="CPF",
        max_length=11,
        min_length=11,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "maxlength": "11", "placeholder": "Somente números"}),
        help_text="Informe os 11 números, sem pontos ou traços.",
    )
    telefone = forms.CharField(
        label="Telefone",
        max_length=20,
        widget=forms.TelInput(attrs={"autocomplete": "tel"}),
    )
    data_nascimento = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(attrs={"type": "date", "autocomplete": "bday"}),
        input_formats=["%Y-%m-%d"],
    )
    endereco = forms.CharField(
        label="Endereço",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "street-address"}),
    )
    plano_medico = forms.CharField(
        label="Plano de saúde (opcional)",
        max_length=100,
        required=False,
    )
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Use uma senha difícil de adivinhar.",
    )
    password2 = forms.CharField(
        label="Confirme a senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            classes = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = f"{classes} form-control".strip()
        if self.is_bound:
            for nome in self.fields:
                if self[nome].errors:
                    self.fields[nome].widget.attrs["class"] += " is-invalid"

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        if not cpf.isdigit():
            raise forms.ValidationError("O CPF deve conter somente números.")
        if Usuario.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Já existe uma conta cadastrada com este CPF.")
        return cpf

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta cadastrada com este e-mail.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas informadas não coincidem.")
        elif password1:
            try:
                validate_password(password1)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned_data

    def criar_paciente(self):
        """Cria usuário e perfil usando o serviço transacional do domínio."""
        from .services import criar_usuario_com_perfil

        dados = self.cleaned_data
        return criar_usuario_com_perfil(
            dados_usuario={
                "username": dados["username"],
                "email": dados["email"],
                "password": dados["password1"],
                "cpf": dados["cpf"],
                "nome": dados["nome"],
                "telefone": dados["telefone"],
                "data_nascimento": dados["data_nascimento"],
                "endereco": dados["endereco"],
                "tipo_usuario": Usuario.TipoUsuario.PACIENTE,
            },
            dados_perfil={"plano_medico": dados.get("plano_medico", "")},
        )


class EditarPerfilForm(forms.ModelForm):
    """
    Permite ao usuário autenticado editar apenas seus dados cadastrais permitidos
    (bloqueia alteração de CPF, username e tipo_usuario).
    """

    plano_medico = forms.CharField(
        label="Plano de saúde (opcional)",
        max_length=100,
        required=False,
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email", "telefone", "endereco"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
            perfil = getattr(self.instance, "perfil_paciente", None)
            if perfil:
                self.fields["plano_medico"].initial = perfil.plano_medico
        else:
            self.fields.pop("plano_medico", None)

        for campo in self.fields.values():
            classes = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = f"{classes} form-control".strip()
        if self.is_bound:
            for nome in self.fields:
                if self[nome].errors:
                    self.fields[nome].widget.attrs["class"] += " is-invalid"

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe outra conta cadastrada com este e-mail.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit and usuario.tipo_usuario == Usuario.TipoUsuario.PACIENTE:
            perfil = getattr(usuario, "perfil_paciente", None)
            if perfil and "plano_medico" in self.cleaned_data:
                perfil.plano_medico = self.cleaned_data["plano_medico"]
                perfil.save(update_fields=["plano_medico"])
        return usuario