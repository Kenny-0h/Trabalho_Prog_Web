from atendimento.models import Consulta, Exame, Receita
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CadastroPacienteForm, EditarPerfilForm, LoginForm
from .models import Usuario
from .permissions import obter_url_redirecionamento_perfil, perfil_requerido

class EntrarView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Login realizado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível entrar. Confira seu usuário e senha.")
        return super().form_invalid(form)

    def get_default_redirect_url(self):
        return obter_url_redirecionamento_perfil(self.request.user)


def inicio(request):
    return render(request, "usuarios/inicio.html")


def cadastro_paciente(request):
    if request.user.is_authenticated:
        return redirect(obter_url_redirecionamento_perfil(request.user))

    form = CadastroPacienteForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            try:
                form.criar_paciente()
            except ValidationError as error:
                if hasattr(error, "message_dict"):
                    for campo, erros in error.message_dict.items():
                        destino = campo if campo in form.fields else None
                        for mensagem in erros:
                            form.add_error(destino, mensagem)
                else:
                    form.add_error(None, error.messages)
                messages.error(request, "Corrija os erros indicados no formulário.")
            else:
                messages.success(request, "Cadastro realizado! Entre com seu usuário e senha.")
                return redirect("login")
        else:
            messages.error(request, "Corrija os campos destacados antes de continuar.")

    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def meu_perfil(request):
    """Permite ao usuário autenticado consultar e atualizar apenas seus próprios dados."""
    form = EditarPerfilForm(request.POST or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Seus dados foram atualizados com sucesso.")
            return redirect("meu_perfil")
        messages.error(request, "Verifique os erros no formulário antes de salvar.")

    return render(request, "usuarios/perfil.html", {"form": form})


@perfil_requerido(Usuario.TipoUsuario.PACIENTE)
def painel_paciente(request):
    consultas = (
        Consulta.objects.filter(paciente__usuario=request.user)
        .select_related("medico__usuario", "medico__especialidade", "prontuario")
        .order_by("-data_hora")
    )
    exames = (
        Exame.objects.filter(prontuario__consulta__paciente__usuario=request.user)
        .select_related("prontuario__consulta__medico__usuario")
        .order_by("-data_solicitacao")
    )
    receitas = (
        Receita.objects.filter(prontuario__consulta__paciente__usuario=request.user)
        .select_related("prontuario__consulta__medico__usuario")
        .order_by("-data_emissao")
    )
    return render(request, "usuarios/painel_perfil.html", {
        "titulo_painel": "Área do Paciente",
        "descricao_painel": "Acompanhe suas consultas agendadas, histórico de atendimentos, exames e receitas.",
        "consultas": consultas,
        "exames": exames,
        "receitas": receitas,
    })


@perfil_requerido(Usuario.TipoUsuario.MEDICO)
def painel_medico(request):
    consultas = (
        Consulta.objects.filter(medico__usuario=request.user)
        .select_related("paciente__usuario", "medico__especialidade")
        .order_by("-data_hora")
    )
    return render(request, "usuarios/painel_perfil.html", {
        "titulo_painel": "Área do Médico",
        "descricao_painel": "Acompanhe suas consultas agendadas e acesse o painel para registrar prontuários.",
        "consultas": consultas,
    })


@perfil_requerido(Usuario.TipoUsuario.FUNCIONARIO)
def painel_funcionario(request):
    consultas = (
        Consulta.objects.select_related(
            "paciente__usuario",
            "medico__usuario",
            "medico__especialidade",
        )
        .order_by("-data_hora")[:15]
    )
    return render(request, "usuarios/painel_perfil.html", {
        "titulo_painel": "Área Administrativa da Clínica",
        "descricao_painel": "Acompanhe as consultas recentes da clínica e gerencie agendamentos e agendas.",
        "consultas": consultas,
    })

@perfil_requerido(Usuario.TipoUsuario.ADMINISTRADOR)
def painel_administrador(request):
    return render(request, "usuarios/painel_perfil.html", {
        "titulo_painel": "Administração do Sistema",
        "descricao_painel": "Gerencie contas de médicos, funcionários administrativos e configurações globais.",
    })


@require_POST
@login_required
def sair(request):
    auth_logout(request)
    messages.success(request, "Você saiu do sistema.")
    return redirect("inicio")