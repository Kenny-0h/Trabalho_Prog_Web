from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CadastroPacienteForm


class EntrarView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Login realizado com sucesso.")
        return super().form_valid(form)


def inicio(request):
    return render(request, "usuarios/inicio.html")


def cadastro_paciente(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    form = CadastroPacienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            usuario = form.criar_paciente()
        except ValidationError as error:
            if hasattr(error, "message_dict"):
                for campo, erros in error.message_dict.items():
                    destino = campo if campo in form.fields else None
                    for mensagem in erros:
                        form.add_error(destino, mensagem)
            else:
                form.add_error(None, error.messages)
        else:
            messages.success(request, "Cadastro realizado! Entre com seu usuário e senha.")
            return redirect("login")

    return render(request, "usuarios/cadastro.html", {"form": form})


@require_POST
@login_required
def sair(request):
    auth_logout(request)
    messages.success(request, "Você saiu do sistema.")
    return redirect("inicio")
