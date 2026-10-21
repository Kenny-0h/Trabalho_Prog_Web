from datetime import date, datetime, time
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from agenda.models import Especialidade
from atendimento.models import Consulta
from usuarios.models import Medico, Paciente, Usuario


class ConsultaTest(TestCase):
    def setUp(self):
        self.especialidade = Especialidade.objects.create(
            nome="Cardiologia",
            tempo_medio_consulta=30,
        )

        usuario_medico = Usuario.objects.create_user(
            username="medico_teste",
            password="SenhaTeste@123",
            cpf="12345678901",
            nome="Médico de teste",
            endereco="Rua de teste, 123",
            telefone="35999990000",
            data_nascimento=date(1980, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.MEDICO,
        )
        self.medico = Medico.objects.create(
            usuario=usuario_medico,
            crm="CRM-MG-123",
            especialidade=self.especialidade,
        )

        usuario_paciente = Usuario.objects.create_user(
            username="paciente_teste",
            password="SenhaTeste@123",
            cpf="12345678902",
            nome="Paciente de teste",
            endereco="Rua de teste, 456",
            telefone="35999990001",
            data_nascimento=date(1990, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.PACIENTE,
        )
        self.paciente = Paciente.objects.create(
            usuario=usuario_paciente,
        )

        self.data_hora = timezone.make_aware(
            datetime(2026, 11, 10, 9, 0)
        )

    def criar_consulta(self, **kwargs):
        dados = {
            "medico": self.medico,
            "paciente": self.paciente,
            "data_hora": self.data_hora,
        }
        dados.update(kwargs)
        return Consulta.objects.create(**dados)

    def test_consulta_e_criada_com_status_agendada(self):
        consulta = self.criar_consulta()

        self.assertEqual(consulta.status, Consulta.Status.AGENDADA)
        self.assertEqual(consulta.medico, self.medico)
        self.assertEqual(consulta.paciente, self.paciente)

    def test_todos_os_status_previstos_estao_definidos(self):
        status_previstos = {
            "AGENDADA",
            "CONFIRMADA",
            "COMPLETA",
            "CANCELADA",
            "NAO_COMPARECEU",
        }

        status_modelo = {
            escolha for escolha, _ in Consulta.Status.choices
        }

        self.assertSetEqual(status_modelo, status_previstos)

    def test_impede_duas_consultas_do_mesmo_medico_no_mesmo_horario(self):
        self.criar_consulta()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.criar_consulta(
                    paciente=self.paciente,
                )

    def test_permite_consultas_do_mesmo_medico_em_horarios_diferentes(self):
        primeira = self.criar_consulta()
        segunda = self.criar_consulta(
            data_hora=self.data_hora.replace(hour=10),
        )

        self.assertNotEqual(primeira.data_hora, segunda.data_hora)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_permite_medicos_diferentes_no_mesmo_horario(self):
        outro_usuario = Usuario.objects.create_user(
            username="outro_medico",
            password="SenhaTeste@123",
            cpf="12345678903",
            nome="Outro médico",
            endereco="Rua de teste, 789",
            telefone="35999990002",
            data_nascimento=date(1975, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.MEDICO,
        )
        outro_medico = Medico.objects.create(
            usuario=outro_usuario,
            crm="CRM-MG-456",
            especialidade=self.especialidade,
        )

        primeira = self.criar_consulta()
        segunda = self.criar_consulta(medico=outro_medico)

        self.assertEqual(primeira.data_hora, segunda.data_hora)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_especialidade_e_obtida_por_meio_do_medico(self):
        consulta = self.criar_consulta()

        self.assertEqual(
            consulta.medico.especialidade,
            self.especialidade,
        )
        self.assertNotIn(
            "especialidade",
            [campo.name for campo in Consulta._meta.fields],
        )
