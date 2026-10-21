from datetime import date, time

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from agenda.models import Agenda, Disponibilidade, Especialidade
from usuarios.models import Medico, Usuario


class AgendaDisponibilidadeTest(TestCase):
    def setUp(self):
        self.especialidade = Especialidade.objects.create(
            nome="Cardiologia",
            tempo_medio_consulta=30,
        )

        self.usuario = Usuario.objects.create_user(
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
            usuario=self.usuario,
            crm="CRM-MG-123",
            especialidade=self.especialidade,
        )

        self.agenda = Agenda.objects.create(medico=self.medico)

    def test_medico_deve_ter_uma_unica_agenda(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Agenda.objects.create(medico=self.medico)

    def test_agenda_pode_ter_varias_disponibilidades(self):
        disponibilidade1 = Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
        )
        disponibilidade2 = Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.QUARTA,
            horario_inicio=time(13, 0),
            horario_fim=time(17, 0),
        )

        self.assertEqual(self.agenda.disponibilidades.count(), 2)
        self.assertIn(disponibilidade1, self.agenda.disponibilidades.all())
        self.assertIn(disponibilidade2, self.agenda.disponibilidades.all())

    def test_horario_final_deve_ser_posterior_ao_inicial(self):
        disponibilidade = Disponibilidade(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(12, 0),
            horario_fim=time(12, 0),
        )

        with self.assertRaises(ValidationError):
            disponibilidade.full_clean()

    def test_aceita_disponibilidade_com_horarios_validos(self):
        disponibilidade = Disponibilidade(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEXTA,
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
        )

        disponibilidade.full_clean()
        disponibilidade.save()

        self.assertEqual(self.agenda.disponibilidades.count(), 1)

    def test_disponibilidade_e_recorrente_por_dia_da_semana(self):
        disponibilidade = Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.TERCA,
            horario_inicio=time(9, 0),
            horario_fim=time(11, 0),
        )

        self.assertEqual(
            disponibilidade.dia_semana,
            Disponibilidade.DiaSemana.TERCA,
        )

    def test_nao_permite_disponibilidade_exatamente_duplicada(self):
        Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Disponibilidade.objects.create(
                    agenda=self.agenda,
                    dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
                    horario_inicio=time(8, 0),
                    horario_fim=time(12, 0),
                )
