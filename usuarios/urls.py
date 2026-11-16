from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("entrar/", views.EntrarView.as_view(), name="login"),
    path("cadastro/", views.cadastro_paciente, name="cadastro"),
    path("sair/", views.sair, name="logout"),
]
