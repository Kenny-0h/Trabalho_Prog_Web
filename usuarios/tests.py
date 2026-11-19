from datetime import date

from django.test import TestCase
from django.urls import reverse

from agenda.models import Especialidade
from usuarios.models import Paciente, Usuario
from usuarios.services import criar_usuario_com_perfil


class AutenticacaoEPermissoesViewsTest(TestCase):
    def setUp(self):
        self.senha = "SenhaForte@123"
        self.especialidade = Especialidade.objects.create(
            nome="Clínica Geral",
            tempo_medio_consulta=30,
        )

        self.paciente = criar_usuario_com_perfil(
            dados_usuario={
                "username": "paciente_teste",
                "email": "paciente@teste.com",
                "password": self.senha,
                "cpf": "11122233344",
                "nome": "Paciente Teste",
                "telefone": "35999991111",
                "data_nascimento": date(1998, 5, 10),
                "endereco": "Rua A, 10",
                "tipo_usuario": Usuario.TipoUsuario.PACIENTE,
            },
            dados_perfil={"plano_medico": "Unimed"},
        )

        self.medico = criar_usuario_com_perfil(
            dados_usuario={
                "username": "medico_teste",
                "email": "medico@teste.com",
                "password": self.senha,
                "cpf": "22233344455",
                "nome": "Médico Teste",
                "telefone": "35999992222",
                "data_nascimento": date(1985, 3, 20),
                "endereco": "Rua B, 20",
                "tipo_usuario": Usuario.TipoUsuario.MEDICO,
            },
            dados_perfil={
                "crm": "CRM-MG-1010",
                "especialidade": self.especialidade,
            },
        )

        self.funcionario = criar_usuario_com_perfil(
            dados_usuario={
                "username": "funcionario_teste",
                "email": "funcionario@teste.com",
                "password": self.senha,
                "cpf": "33344455566",
                "nome": "Funcionário Teste",
                "telefone": "35999993333",
                "data_nascimento": date(1992, 7, 15),
                "endereco": "Rua C, 30",
                "tipo_usuario": Usuario.TipoUsuario.FUNCIONARIO,
                "is_staff": True,
            },
        )

        self.admin = criar_usuario_com_perfil(
            dados_usuario={
                "username": "admin_teste",
                "email": "admin@teste.com",
                "password": self.senha,
                "cpf": "44455566677",
                "nome": "Admin Teste",
                "telefone": "35999994444",
                "data_nascimento": date(1990, 1, 1),
                "endereco": "Rua D, 40",
                "tipo_usuario": Usuario.TipoUsuario.ADMINISTRADOR,
                "is_staff": True,
                "is_superuser": True,
            },
        )

    def test_login_credenciais_validas_redireciona_por_perfil(self):
        pares = [
            ("paciente_teste", reverse("painel_paciente")),
            ("medico_teste", reverse("painel_medico")),
            ("funcionario_teste", reverse("painel_funcionario")),
            ("admin_teste", reverse("painel_administrador")),
        ]
        for username, url_esperada in pares:
            with self.subTest(username=username):
                resposta = self.client.post(
                    reverse("login"),
                    {"username": username, "password": self.senha},
                )
                self.assertRedirects(resposta, url_esperada)
                self.client.logout()

    def test_login_credenciais_invalidas_exibe_mensagem_erro(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "paciente_teste", "password": "SenhaErrada"},
            follow=True,
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(resposta.context["user"].is_authenticated)
        self.assertContains(resposta, "Não foi possível entrar")

    def test_logout_encerra_sessao_via_post(self):
        self.client.login(username="paciente_teste", password=self.senha)
        resposta = self.client.post(reverse("logout"), follow=True)
        self.assertRedirects(resposta, reverse("login"))
        self.assertFalse(resposta.context["user"].is_authenticated)

    def test_cadastro_publico_cria_apenas_paciente(self):
        dados = {
            "username": "novo_paciente",
            "email": "novo@paciente.com",
            "nome": "Novo Paciente",
            "cpf": "55566677788",
            "telefone": "35988887777",
            "data_nascimento": "2001-09-12",
            "endereco": "Av. Central, 100",
            "plano_medico": "Bradesco Saúde",
            "password1": "SenhaSegura@2026",
            "password2": "SenhaSegura@2026",
            "tipo_usuario": Usuario.TipoUsuario.ADMINISTRADOR,  # Tentativa de injeção de perfil
        }
        resposta = self.client.post(reverse("cadastro"), dados)
        self.assertRedirects(resposta, reverse("login"))

        usuario_criado = Usuario.objects.get(username="novo_paciente")
        self.assertEqual(usuario_criado.tipo_usuario, Usuario.TipoUsuario.PACIENTE)
        self.assertTrue(Paciente.objects.filter(usuario=usuario_criado).exists())

    def test_acesso_anonimo_a_paginas_protegidas_redireciona_para_login(self):
        rotas_protegidas = [
            reverse("meu_perfil"),
            reverse("painel_paciente"),
            reverse("painel_medico"),
            reverse("painel_funcionario"),
            reverse("painel_administrador"),
        ]
        for rota in rotas_protegidas:
            with self.subTest(rota=rota):
                resposta = self.client.get(rota)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(reverse("login"), resposta.url)

    def test_usuario_nao_acessa_painel_de_outro_perfil_pela_url(self):
        self.client.login(username="paciente_teste", password=self.senha)
        for rota_proibida in [
            reverse("painel_medico"),
            reverse("painel_funcionario"),
            reverse("painel_administrador"),
        ]:
            resposta = self.client.get(rota_proibida)
            self.assertRedirects(resposta, reverse("painel_paciente"))

    def test_edicao_de_perfil_atualiza_dados_permitidos_e_ignora_cpf_e_tipo(self):
        self.client.login(username="paciente_teste", password=self.senha)
        resposta = self.client.post(
            reverse("meu_perfil"),
            {
                "nome": "Paciente Nome Atualizado",
                "email": "paciente_novo@teste.com",
                "telefone": "35977776666",
                "endereco": "Rua Nova, 999",
                "plano_medico": "SulAmérica",
                "cpf": "99999999999",
                "tipo_usuario": Usuario.TipoUsuario.ADMINISTRADOR,
            },
        )
        self.assertRedirects(resposta, reverse("meu_perfil"))
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nome, "Paciente Nome Atualizado")
        self.assertEqual(self.paciente.cpf, "11122233344")
        self.assertEqual(self.paciente.tipo_usuario, Usuario.TipoUsuario.PACIENTE)

    def test_restricoes_de_acesso_ao_django_admin(self):
        # Paciente não acessa o Django Admin
        self.client.login(username="paciente_teste", password=self.senha)
        resp_paciente = self.client.get(reverse("admin:index"))
        self.assertEqual(resp_paciente.status_code, 302)
        self.client.logout()

        # Funcionário não pode adicionar usuários (médicos/admins) nem ver prontuários
        self.client.login(username="funcionario_teste", password=self.senha)
        resp_add_user = self.client.get(reverse("admin:usuarios_usuario_add"))
        self.assertEqual(resp_add_user.status_code, 403)
        resp_prontuario = self.client.get(reverse("admin:atendimento_prontuario_changelist"))
        self.assertEqual(resp_prontuario.status_code, 403)
        self.client.logout()

        # Administrador do sistema possui acesso à criação de usuários no Admin
        self.client.login(username="admin_teste", password=self.senha)
        resp_admin = self.client.get(reverse("admin:usuarios_usuario_add"))
        self.assertEqual(resp_admin.status_code, 200)