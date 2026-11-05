from datetime import date, time, datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from agenda.models import Agenda, BloqueioAgenda, Disponibilidade, Especialidade
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

    def test_nao_permite_horarios_sobrepostos(self):
        Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
        )

        casos_sobrepostos = [
            (time(7, 0), time(9, 0)),  # Sobreposição no início
            (time(11, 0), time(13, 0)),  # Sobreposição no fim
            (time(9, 0), time(10, 0)),  # Intervalo contido
            (time(7, 0), time(13, 0)),  # Intervalo que contém o existente
        ]

        for inicio, fim in casos_sobrepostos:
            with self.subTest(inicio=inicio, fim=fim):
                disponibilidade = Disponibilidade(
                    agenda=self.agenda,
                    dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
                    horario_inicio=inicio,
                    horario_fim=fim,
                )

                with self.assertRaises(ValidationError):
                    disponibilidade.full_clean()

    def test_permite_horarios_consecutivos(self):
        Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(8, 0),
            horario_fim=time(9, 0),
        )

        disponibilidade = Disponibilidade(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(9, 0),
            horario_fim=time(10, 0),
        )

        disponibilidade.full_clean()
        disponibilidade.save()

        self.assertEqual(self.agenda.disponibilidades.count(), 2)

    def test_banco_rejeita_disponibilidade_sobreposta(self):
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
                    horario_inicio=time(10, 0),
                    horario_fim=time(14, 0),
                )


class BloqueioAgendaTest(TestCase):
    def setUp(self):
        self.especialidade = Especialidade.objects.create(
            nome="Cardiologia",
            tempo_medio_consulta=30,
        )

        usuario = Usuario.objects.create_user(
            username="medico_bloqueio",
            password="SenhaTeste@123",
            cpf="12345678904",
            nome="Médico de bloqueio",
            endereco="Rua de teste, 123",
            telefone="35999990000",
            data_nascimento=date(1980, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.MEDICO,
        )

        self.medico = Medico.objects.create(
            usuario=usuario,
            crm="CRM-MG-789",
            especialidade=self.especialidade,
        )
        self.agenda = Agenda.objects.create(medico=self.medico)

        self.inicio = timezone.make_aware(
            datetime(2026, 11, 10, 9, 0)
        )
        self.fim = timezone.make_aware(
            datetime(2026, 11, 10, 12, 0)
        )

    def criar_bloqueio(self, **kwargs):
        dados = {
            "agenda": self.agenda,
            "data_hora_inicio": self.inicio,
            "data_hora_fim": self.fim,
            "justificativa": "Compromisso pessoal",
        }
        dados.update(kwargs)
        return BloqueioAgenda.objects.create(**dados)

    def test_bloqueio_e_criado_com_status_pendente(self):
        bloqueio = self.criar_bloqueio()

        self.assertEqual(bloqueio.status, BloqueioAgenda.Status.PENDENTE)
        self.assertEqual(bloqueio.agenda, self.agenda)
        self.assertEqual(bloqueio.justificativa, "Compromisso pessoal")

    def test_status_previstos_estao_definidos(self):
        status_previstos = {
            "PENDENTE",
            "APROVADO",
            "REJEITADO",
        }
        status_modelo = {
            escolha for escolha, _ in BloqueioAgenda.Status.choices
        }

        self.assertSetEqual(status_modelo, status_previstos)

    def test_tipos_previstos_estao_definidos(self):
        tipos_previstos = {"OUTRO", "AUSENCIA", "FERIAS"}
        tipos_modelo = {
            escolha for escolha, _ in BloqueioAgenda.Tipo.choices
        }

        self.assertSetEqual(tipos_modelo, tipos_previstos)

    def test_aceita_bloqueio_valido(self):
        bloqueio = BloqueioAgenda(
            agenda=self.agenda,
            data_hora_inicio=self.inicio,
            data_hora_fim=self.fim,
            justificativa="Férias",
            tipo=BloqueioAgenda.Tipo.FERIAS,
        )

        bloqueio.full_clean()
        bloqueio.save()

        self.assertEqual(self.agenda.bloqueios.count(), 1)

    def test_rejeita_periodo_com_fim_igual_ao_inicio(self):
        bloqueio = BloqueioAgenda(
            agenda=self.agenda,
            data_hora_inicio=self.inicio,
            data_hora_fim=self.inicio,
            justificativa="Período inválido",
        )

        with self.assertRaises(ValidationError):
            bloqueio.full_clean()

    def test_banco_impede_periodo_invalido(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.criar_bloqueio(
                    data_hora_fim=self.inicio,
                )

    def test_aceita_bloqueio_que_atravessa_dias(self):
        fim = timezone.make_aware(
            datetime(2026, 11, 11, 12, 0)
        )
        bloqueio = self.criar_bloqueio(data_hora_fim=fim)

        self.assertGreater(
            bloqueio.data_hora_fim,
            bloqueio.data_hora_inicio,
        )
