from datetime import date

from django.test import TestCase
from django.urls import reverse

from usuarios.models import Paciente, Usuario


class AutenticacaoViewsTest(TestCase):
    def test_inicio_fica_disponivel_sem_login(self):
        response = self.client.get(reverse("inicio"))
        self.assertRedirects(response, reverse("login"))

    def test_login_exibe_formulario(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/login.html")

    def test_cadastro_exibe_formulario(self):
        response = self.client.get(reverse("cadastro"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/cadastro.html")

    def test_cadastro_cria_somente_perfil_de_paciente(self):
        response = self.client.post(reverse("cadastro"), {
            "username": "paciente_novo",
            "email": "paciente@example.com",
            "nome": "Paciente Novo",
            "cpf": "12345678901",
            "telefone": "35999990000",
            "data_nascimento": "1990-01-01",
            "endereco": "Rua de teste, 123",
            "plano_medico": "",
            "password1": "SenhaForte!2026",
            "password2": "SenhaForte!2026",
        })
        self.assertRedirects(response, reverse("login"))
        usuario = Usuario.objects.get(username="paciente_novo")
        self.assertEqual(usuario.tipo_usuario, Usuario.TipoUsuario.PACIENTE)
        self.assertTrue(Paciente.objects.filter(usuario=usuario).exists())

    def test_logout_exige_post(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_encerra_sessao(self):
        usuario = Usuario.objects.create_user(
            username="paciente_logado",
            password="SenhaForte!2026",
            cpf="12345678902",
            nome="Paciente Logado",
            endereco="Rua de teste, 123",
            telefone="35999990000",
            data_nascimento=date(1990, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.PACIENTE,
        )
        self.client.force_login(usuario)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
