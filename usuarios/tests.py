from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from usuarios.services import criar_usuario_com_perfil

from agenda.models import Especialidade
from usuarios.models import (
    AdministradorSistema,
    FuncionarioAdministrativo,
    Medico,
    Paciente,
    Usuario,
)


class ModelagemUsuariosTest(TestCase):
    def criar_usuario(self, cpf, tipo, username):
        return Usuario.objects.create_user(
            username=username,
            password="SenhaTeste@123",
            cpf=cpf,
            nome=f"Usuário {username}",
            endereco="Rua de teste, 123",
            telefone="35999990000",
            data_nascimento=date(1990, 1, 1),
            tipo_usuario=tipo,
        )

    def test_cpf_deve_ser_unico(self):
        self.criar_usuario("12345678901", Usuario.TipoUsuario.PACIENTE, "paciente1")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.criar_usuario(
                    "12345678901",
                    Usuario.TipoUsuario.PACIENTE,
                    "paciente2",
                )

    def test_medico_deve_ter_especialidade(self):
        usuario = self.criar_usuario(
            "12345678902",
            Usuario.TipoUsuario.MEDICO,
            "medico1",
        )
        especialidade = Especialidade.objects.create(
            nome="Cardiologia",
            tempo_medio_consulta=30,
        )

        medico = Medico.objects.create(
            usuario=usuario,
            crm="CRM-MG-123",
            especialidade=especialidade,
        )

        self.assertEqual(medico.especialidade.nome, "Cardiologia")

    def test_crm_deve_ser_unico(self):
        especialidade = Especialidade.objects.create(
            nome="Dermatologia",
            tempo_medio_consulta=20,
        )
        usuario1 = self.criar_usuario(
            "12345678903",
            Usuario.TipoUsuario.MEDICO,
            "medico2",
        )
        usuario2 = self.criar_usuario(
            "12345678904",
            Usuario.TipoUsuario.MEDICO,
            "medico3",
        )

        Medico.objects.create(
            usuario=usuario1,
            crm="CRM-MG-456",
            especialidade=especialidade,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Medico.objects.create(
                    usuario=usuario2,
                    crm="CRM-MG-456",
                    especialidade=especialidade,
                )

    def test_perfil_paciente_relacionado_ao_usuario(self):
        usuario = self.criar_usuario(
            "12345678905",
            Usuario.TipoUsuario.PACIENTE,
            "paciente3",
        )

        perfil = Paciente.objects.create(
            usuario=usuario,
            plano_medico="Plano de teste",
        )

        self.assertEqual(usuario.perfil_paciente, perfil)

    def test_usuario_nao_deve_ter_perfis_incompativeis(self):
        usuario = self.criar_usuario(
            "12345678906",
            Usuario.TipoUsuario.PACIENTE,
            "paciente4",
        )
        Paciente.objects.create(usuario=usuario)

        usuario.tipo_usuario = Usuario.TipoUsuario.MEDICO

        with self.assertRaises(ValidationError):
            usuario.full_clean()


class ServicoCadastroTest(TestCase):
    def dados_usuario(self, tipo, username, cpf):
        return {
            "username": username,
            "password": "SenhaTeste@123",
            "cpf": cpf,
            "nome": f"Usuário {username}",
            "endereco": "Rua de teste, 123",
            "telefone": "35999990000",
            "data_nascimento": date(1990, 1, 1),
            "tipo_usuario": tipo,
        }

    def test_cria_usuario_e_perfil_paciente(self):
        usuario = criar_usuario_com_perfil(
            dados_usuario=self.dados_usuario(
                Usuario.TipoUsuario.PACIENTE,
                "paciente_servico",
                "12345678001",
            ),
            dados_perfil={"plano_medico": "Plano Teste"},
        )

        self.assertTrue(Paciente.objects.filter(usuario=usuario).exists())
        self.assertEqual(usuario.perfil_paciente.plano_medico, "Plano Teste")

    def test_cria_usuario_e_perfil_medico(self):
        especialidade = Especialidade.objects.create(
            nome="Neurologia",
            tempo_medio_consulta=40,
        )

        usuario = criar_usuario_com_perfil(
            dados_usuario=self.dados_usuario(
                Usuario.TipoUsuario.MEDICO,
                "medico_servico",
                "12345678002",
            ),
            dados_perfil={
                "crm": "CRM-MG-999",
                "especialidade": especialidade,
            },
        )

        self.assertEqual(usuario.perfil_medico.especialidade, especialidade)

    def test_reverte_usuario_se_perfil_falhar(self):
        dados = self.dados_usuario(
            Usuario.TipoUsuario.MEDICO,
            "medico_invalido",
            "12345678003",
        )

        with self.assertRaises(ValidationError):
            criar_usuario_com_perfil(
                dados_usuario=dados,
                dados_perfil={},  # Faltam CRM e especialidade.
            )

        self.assertFalse(
            Usuario.objects.filter(username="medico_invalido").exists()
        )
