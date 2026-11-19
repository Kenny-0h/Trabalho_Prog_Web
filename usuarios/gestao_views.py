from datetime import date

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from agenda.models import Agenda, Disponibilidade, Especialidade
from atendimento.models import Consulta
from .models import (
    AdministradorSistema, FuncionarioAdministrativo, Medico, Paciente, Usuario,
)
from .services import criar_usuario_com_perfil


PERFIS_GESTAO = (
    Usuario.TipoUsuario.ADMINISTRADOR,
    Usuario.TipoUsuario.FUNCIONARIO,
)


def gestao_requerida(view):
    """Protege as telas de gestão contra qualquer perfil que não seja administrativo."""
    from functools import wraps

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.tipo_usuario not in PERFIS_GESTAO:
            messages.error(request, "Você não possui permissão para acessar esta área.")
            return redirect("inicio")
        return view(request, *args, **kwargs)
    return wrapper


class UsuarioBaseForm(forms.Form):
    username = forms.CharField(label="Usuário", max_length=150)
    nome = forms.CharField(label="Nome completo", max_length=70)
    cpf = forms.CharField(label="CPF (11 números)", max_length=11, min_length=11)
    email = forms.EmailField(label="E-mail")
    telefone = forms.CharField(label="Telefone", max_length=20)
    data_nascimento = forms.DateField(label="Data de nascimento", widget=forms.DateInput(attrs={"type": "date"}))
    endereco = forms.CharField(label="Endereço", max_length=100)
    senha = forms.CharField(label="Senha", required=False, widget=forms.PasswordInput,
                            help_text="Obrigatória ao cadastrar; em branco mantém a senha atual.")

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        initial = kwargs.pop("initial", {})
        if instance:
            initial.update({
                "username": instance.username, "nome": instance.nome, "cpf": instance.cpf,
                "email": instance.email, "telefone": instance.telefone,
                "data_nascimento": instance.data_nascimento, "endereco": instance.endereco,
            })
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        if not cpf.isdigit():
            raise forms.ValidationError("Informe somente números.")
        qs = Usuario.objects.filter(cpf=cpf)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um usuário com este CPF.")
        return cpf

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = Usuario.objects.filter(username__iexact=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = Usuario.objects.filter(email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def save_usuario(self, tipo, dados_perfil=None):
        data = self.cleaned_data
        if self.instance:
            usuario = self.instance
            for field in ("username", "nome", "cpf", "email", "telefone", "data_nascimento", "endereco"):
                setattr(usuario, field, data[field])
            if data.get("senha"):
                usuario.set_password(data["senha"])
            usuario.save()
            return usuario
        if not data.get("senha"):
            raise ValidationError({"senha": "Informe uma senha para o novo usuário."})
        return criar_usuario_com_perfil(
            dados_usuario={
                "username": data["username"], "nome": data["nome"], "cpf": data["cpf"],
                "email": data["email"], "telefone": data["telefone"],
                "data_nascimento": data["data_nascimento"], "endereco": data["endereco"],
                "password": data["senha"], "tipo_usuario": tipo,
            },
            dados_perfil=dados_perfil or {},
        )


class PacienteAdminForm(UsuarioBaseForm):
    plano_medico = forms.CharField(label="Plano de saúde", max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.pop("initial", {})
        if instance and hasattr(instance, "perfil_paciente"):
            initial["plano_medico"] = instance.perfil_paciente.plano_medico
        super().__init__(*args, initial=initial, **kwargs)
        self.fields["plano_medico"].widget.attrs["class"] = "form-control"

    @transaction.atomic
    def save(self):
        usuario = self.save_usuario(Usuario.TipoUsuario.PACIENTE)
        perfil, _ = Paciente.objects.get_or_create(usuario=usuario)
        perfil.plano_medico = self.cleaned_data["plano_medico"]
        perfil.save()
        return usuario


class MedicoAdminForm(UsuarioBaseForm):
    crm = forms.CharField(label="CRM", max_length=12)
    rqe = forms.CharField(label="RQE", max_length=12, required=False)
    especialidade = forms.ModelChoiceField(label="Especialidade", queryset=Especialidade.objects.order_by("nome"))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.pop("initial", {})
        if instance and hasattr(instance, "perfil_medico"):
            perfil = instance.perfil_medico
            initial.update({"crm": perfil.crm, "rqe": perfil.rqe, "especialidade": perfil.especialidade_id})
        super().__init__(*args, initial=initial, **kwargs)

    def clean_crm(self):
        crm = self.cleaned_data["crm"]
        qs = Medico.objects.filter(crm=crm)
        if self.instance:
            qs = qs.exclude(usuario=self.instance)
        if qs.exists():
            raise forms.ValidationError("Este CRM já está cadastrado.")
        return crm

    @transaction.atomic
    def save(self):
        usuario = self.save_usuario(Usuario.TipoUsuario.MEDICO, {
            "crm": self.cleaned_data["crm"],
            "rqe": self.cleaned_data["rqe"],
            "especialidade": self.cleaned_data["especialidade"],
        })
        perfil, _ = Medico.objects.get_or_create(usuario=usuario, defaults={"crm": self.cleaned_data["crm"], "especialidade": self.cleaned_data["especialidade"]})
        perfil.crm = self.cleaned_data["crm"]
        perfil.rqe = self.cleaned_data["rqe"]
        perfil.especialidade = self.cleaned_data["especialidade"]
        perfil.save()
        Agenda.objects.get_or_create(medico=perfil)
        return usuario


class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = Disponibilidade
        fields = ("agenda", "dia_semana", "horario_inicio", "horario_fim")
        widgets = {
            "horario_inicio": forms.TimeInput(attrs={"type": "time"}),
            "horario_fim": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


def _render_form(request, form, titulo, voltar, template="gestao/form.html"):
    return render(request, template, {"form": form, "titulo": titulo, "voltar": voltar})


@gestao_requerida
def gestao_inicio(request):
    consultas_por_status = {
        label: Consulta.objects.filter(status=value).count()
        for value, label in Consulta.Status.choices
    }
    return render(request, "gestao/inicio.html", {
        "total_pacientes": Paciente.objects.count(),
        "total_medicos": Medico.objects.count(),
        "total_agendas": Agenda.objects.count(),
        "total_consultas": Consulta.objects.count(),
        "consultas_por_status": consultas_por_status,
    })


@gestao_requerida
def pacientes_lista(request):
    pacientes = Paciente.objects.select_related("usuario").order_by("usuario__nome")
    termo = request.GET.get("q", "").strip()
    if termo:
        from django.db.models import Q
        pacientes = pacientes.filter(Q(usuario__nome__icontains=termo) | Q(usuario__cpf__icontains=termo) | Q(usuario__email__icontains=termo))
    return render(request, "gestao/pacientes_lista.html", {"pacientes": pacientes, "termo": termo})


@gestao_requerida
def paciente_novo(request):
    form = PacienteAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except (ValidationError, ValueError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Paciente cadastrado com sucesso.")
            return redirect("gestao_pacientes")
    return _render_form(request, form, "Cadastrar paciente", reverse("gestao_pacientes"))


@gestao_requerida
def paciente_editar(request, pk):
    paciente = get_object_or_404(Paciente.objects.select_related("usuario"), pk=pk)
    form = PacienteAdminForm(request.POST or None, instance=paciente.usuario)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dados do paciente atualizados.")
        return redirect("gestao_pacientes")
    return _render_form(request, form, "Editar paciente", reverse("gestao_pacientes"))


@gestao_requerida
def paciente_excluir(request, pk):
    paciente = get_object_or_404(Paciente.objects.select_related("usuario"), pk=pk)
    if request.method == "POST":
        try:
            paciente.usuario.delete()
        except ProtectedError:
            messages.error(request, "Este paciente possui consultas registradas e não pode ser excluído.")
            return redirect("gestao_pacientes")
        messages.success(request, "Paciente excluído.")
        return redirect("gestao_pacientes")
    return render(request, "gestao/confirmar_exclusao.html", {"objeto": paciente, "titulo": "Excluir paciente", "voltar": reverse("gestao_pacientes")})


@gestao_requerida
def medicos_lista(request):
    medicos = Medico.objects.select_related("usuario", "especialidade").order_by("usuario__nome")
    termo = request.GET.get("q", "").strip()
    if termo:
        from django.db.models import Q
        medicos = medicos.filter(Q(usuario__nome__icontains=termo) | Q(crm__icontains=termo) | Q(especialidade__nome__icontains=termo))
    return render(request, "gestao/medicos_lista.html", {"medicos": medicos, "termo": termo})


@gestao_requerida
def medico_novo(request):
    form = MedicoAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except (ValidationError, ValueError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Médico cadastrado e agenda criada.")
            return redirect("gestao_medicos")
    return _render_form(request, form, "Cadastrar médico", reverse("gestao_medicos"))


@gestao_requerida
def medico_editar(request, pk):
    medico = get_object_or_404(Medico.objects.select_related("usuario"), pk=pk)
    form = MedicoAdminForm(request.POST or None, instance=medico.usuario)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except (ValidationError, ValueError) as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Dados do médico atualizados.")
            return redirect("gestao_medicos")
    return _render_form(request, form, "Editar médico", reverse("gestao_medicos"))


@gestao_requerida
def medico_excluir(request, pk):
    if request.user.tipo_usuario != Usuario.TipoUsuario.ADMINISTRADOR:
        messages.error(request, "Somente o administrador do sistema pode excluir médicos.")
        return redirect("gestao_medicos")
    medico = get_object_or_404(Medico.objects.select_related("usuario"), pk=pk)
    if request.method == "POST":
        try:
            medico.usuario.delete()
        except ProtectedError:
            messages.error(request, "Este médico possui consultas registradas e não pode ser excluído.")
            return redirect("gestao_medicos")
        messages.success(request, "Médico excluído.")
        return redirect("gestao_medicos")
    return render(request, "gestao/confirmar_exclusao.html", {"objeto": medico, "titulo": "Excluir médico", "voltar": reverse("gestao_medicos")})


@gestao_requerida
def agendas_lista(request):
    agendas = Agenda.objects.select_related("medico__usuario", "medico__especialidade").prefetch_related("disponibilidades").order_by("medico__usuario__nome")
    termo = request.GET.get("q", "").strip()
    if termo:
        agendas = agendas.filter(medico__usuario__nome__icontains=termo)
    return render(request, "gestao/agendas_lista.html", {"agendas": agendas, "termo": termo})


@gestao_requerida
def agenda_editar(request, pk):
    agenda = get_object_or_404(Agenda.objects.select_related("medico__usuario"), pk=pk)
    if request.method == "POST":
        form = DisponibilidadeForm(request.POST)
        if form.is_valid():
            disponibilidade = form.save(commit=False)
            disponibilidade.agenda = agenda
            try:
                disponibilidade.full_clean()
                disponibilidade.save()
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Disponibilidade adicionada à agenda.")
                return redirect("gestao_agendas")
    else:
        form = DisponibilidadeForm(initial={"agenda": agenda})
    form.fields["agenda"].queryset = Agenda.objects.filter(pk=agenda.pk)
    return _render_form(request, form, f"Adicionar horário — {agenda.medico.usuario.nome}", reverse("gestao_agendas"))


@gestao_requerida
def disponibilidade_editar(request, pk):
    disponibilidade = get_object_or_404(Disponibilidade.objects.select_related("agenda__medico__usuario"), pk=pk)
    form = DisponibilidadeForm(request.POST or None, instance=disponibilidade)
    form.fields["agenda"].queryset = Agenda.objects.filter(pk=disponibilidade.agenda_id)
    if request.method == "POST" and form.is_valid():
        try:
            form.instance.full_clean()
            form.save()
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Disponibilidade atualizada.")
            return redirect("gestao_agendas")
    return _render_form(request, form, "Editar disponibilidade", reverse("gestao_agendas"))


@gestao_requerida
def disponibilidade_excluir(request, pk):
    disponibilidade = get_object_or_404(Disponibilidade, pk=pk)
    if request.method == "POST":
        disponibilidade.delete()
        messages.success(request, "Disponibilidade removida.")
        return redirect("gestao_agendas")
    return render(request, "gestao/confirmar_exclusao.html", {"objeto": disponibilidade, "titulo": "Excluir disponibilidade", "voltar": reverse("gestao_agendas")})
