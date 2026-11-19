from django.urls import path
from . import gestao_views as views

urlpatterns = [
    path("gestao/", views.gestao_inicio, name="gestao_inicio"),
    path("gestao/pacientes/", views.pacientes_lista, name="gestao_pacientes"),
    path("gestao/pacientes/novo/", views.paciente_novo, name="gestao_paciente_novo"),
    path("gestao/pacientes/<int:pk>/editar/", views.paciente_editar, name="gestao_paciente_editar"),
    path("gestao/pacientes/<int:pk>/excluir/", views.paciente_excluir, name="gestao_paciente_excluir"),
    path("gestao/medicos/", views.medicos_lista, name="gestao_medicos"),
    path("gestao/medicos/novo/", views.medico_novo, name="gestao_medico_novo"),
    path("gestao/medicos/<int:pk>/editar/", views.medico_editar, name="gestao_medico_editar"),
    path("gestao/medicos/<int:pk>/excluir/", views.medico_excluir, name="gestao_medico_excluir"),
    path("gestao/agendas/", views.agendas_lista, name="gestao_agendas"),
    path("gestao/agendas/<int:pk>/disponibilidade/nova/", views.agenda_editar, name="gestao_disponibilidade_nova"),
    path("gestao/disponibilidades/<int:pk>/editar/", views.disponibilidade_editar, name="gestao_disponibilidade_editar"),
    path("gestao/disponibilidades/<int:pk>/excluir/", views.disponibilidade_excluir, name="gestao_disponibilidade_excluir"),
]
