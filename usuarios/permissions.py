from functools import wraps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse

from .models import Usuario


def obter_url_redirecionamento_perfil(user):
    """Retorna a URL inicial correspondente ao perfil do usuário autenticado."""
    if not user.is_authenticated:
        return reverse("login")

    mapa_rotas = {
        Usuario.TipoUsuario.PACIENTE: "painel_paciente",
        Usuario.TipoUsuario.MEDICO: "painel_medico",
        Usuario.TipoUsuario.FUNCIONARIO: "painel_funcionario",
        Usuario.TipoUsuario.ADMINISTRADOR: "painel_administrador",
    }
    nome_rota = mapa_rotas.get(getattr(user, "tipo_usuario", None))
    if nome_rota:
        return reverse(nome_rota)
    if user.is_superuser or user.is_staff:
        return reverse("admin:index")
    return reverse("inicio")


def perfil_requerido(*tipos_permitidos):
    """
    Decorator que exige autenticação e verifica se user.tipo_usuario
    pertence aos perfis autorizados. Bloqueia acesso direto via URL.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Faça login para acessar esta página.")
                return redirect_to_login(request.get_full_path())

            if request.user.tipo_usuario not in tipos_permitidos:
                messages.error(
                    request,
                    "Acesso negado: seu perfil não possui permissão para acessar esta área.",
                )
                return redirect(obter_url_redirecionamento_perfil(request.user))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator