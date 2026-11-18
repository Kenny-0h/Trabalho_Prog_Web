from django.urls import path
from . import funcionalidades_views as funcionalidades

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", views.EntrarView.as_view(), name="login"),
    path("cadastro/", views.cadastro_paciente, name="cadastro"),
    path("sair/", views.sair, name="logout"),
    path("perfil/", views.meu_perfil, name="meu_perfil"),
    path("painel/paciente/", views.painel_paciente, name="painel_paciente"),
    path("painel/medico/", views.painel_medico, name="painel_medico"),
    path("painel/funcionario/", views.painel_funcionario, name="painel_funcionario"),
    path("painel/administrador/", views.painel_administrador, name="painel_administrador"),
    path("paciente/disponibilidade-medicos/", funcionalidades.disponibilidade_medicos, name="disponibilidade_medicos"),
    path("medico/agenda/", funcionalidades.agenda_do_medico, name="agenda_medico"),
    path("medico/agenda/disponibilidade/nova/", funcionalidades.adicionar_disponibilidade_medico, name="medico_disponibilidade_nova"),
]