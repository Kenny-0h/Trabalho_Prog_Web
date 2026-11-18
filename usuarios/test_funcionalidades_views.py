from datetime import date, datetime, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agenda.models import Agenda, BloqueioAgenda, Disponibilidade, Especialidade, SolicitacaoDisponibilidade
from atendimento.models import Consulta
from usuarios.models import FuncionarioAdministrativo, Medico, Paciente, Usuario


class TelasPorPerfilTest(TestCase):
    def setUp(self):
        self.especialidade = Especialidade.objects.create(
            nome="Cardiologia",
            tempo_medio_consulta=30,
        )
        self.usuario_medico = Usuario.objects.create_user(
            username="medico_fluxo",
            password="SenhaTeste@123",
            cpf="11111111111",
            nome="Médico Fluxo",
            endereco="Rua A, 10",
            telefone="35999990000",
            data_nascimento=date(1980, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.MEDICO,
        )
        self.medico = Medico.objects.create(
            usuario=self.usuario_medico,
            crm="CRM-FLUXO-1",
            especialidade=self.especialidade,
        )
        self.agenda = Agenda.objects.create(medico=self.medico)
        self.disponibilidade = Disponibilidade.objects.create(
            agenda=self.agenda,
            dia_semana=Disponibilidade.DiaSemana.SEGUNDA,
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
        )

        self.usuario_paciente = Usuario.objects.create_user(
            username="paciente_fluxo",
            password="SenhaTeste@123",
            cpf="22222222222",
            nome="Paciente Fluxo",
            endereco="Rua B, 20",
            telefone="35999990001",
            data_nascimento=date(1990, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.PACIENTE,
        )
        self.paciente = Paciente.objects.create(usuario=self.usuario_paciente)

        self.usuario_funcionario = Usuario.objects.create_user(
            username="funcionario_fluxo",
            password="SenhaTeste@123",
            cpf="33333333333",
            nome="Funcionário Fluxo",
            endereco="Rua C, 30",
            telefone="35999990002",
            data_nascimento=date(1985, 1, 1),
            tipo_usuario=Usuario.TipoUsuario.FUNCIONARIO,
        )
        FuncionarioAdministrativo.objects.create(usuario=self.usuario_funcionario)

    def proxima_segunda(self):
        hoje = timezone.localdate()
        dias = (7 - hoje.weekday()) % 7 or 7
        return hoje + timedelta(days=dias)

    def test_paciente_consulta_disponibilidade_e_nao_acessa_gestao(self):
        self.client.force_login(self.usuario_paciente)
        response = self.client.get(reverse("disponibilidade_medicos"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "agenda/disponibilidade_medicos.html")

        response = self.client.get(reverse("gestao_consultas"))
        self.assertEqual(response.status_code, 302)

    def test_medico_acessa_sua_agenda_e_cadastra_disponibilidade(self):
        self.client.force_login(self.usuario_medico)
        response = self.client.get(reverse("agenda_medico"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("medico_disponibilidade_nova"), {
            "dia_semana": Disponibilidade.DiaSemana.SEXTA,
            "horario_inicio": "08:00",
            "horario_fim": "10:00",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.agenda.disponibilidades.filter(dia_semana=Disponibilidade.DiaSemana.SEXTA).exists())

    def test_medico_solicita_alteracao_e_bloqueio_e_funcionario_aprova(self):
        self.client.force_login(self.usuario_medico)
        response = self.client.post(reverse("medico_solicitar_alteracao"), {
            "disponibilidade": self.disponibilidade.pk,
            "dia_semana": Disponibilidade.DiaSemana.SEGUNDA,
            "horario_inicio": "08:00",
            "horario_fim": "11:30",
            "justificativa": "Ajuste de expediente",
        })
        self.assertEqual(response.status_code, 302)
        solicitacao = SolicitacaoDisponibilidade.objects.get(agenda=self.agenda)
        self.assertEqual(solicitacao.status, SolicitacaoDisponibilidade.Status.PENDENTE)

        inicio = timezone.localtime(timezone.now()).replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=14)
        fim = inicio + timedelta(hours=2)
        self.client.post(reverse("medico_solicitar_bloqueio"), {
            "data_hora_inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
            "data_hora_fim": fim.strftime("%Y-%m-%dT%H:%M"),
            "tipo": BloqueioAgenda.Tipo.AUSENCIA,
            "justificativa": "Ausência programada",
        })
        bloqueio = BloqueioAgenda.objects.get(agenda=self.agenda)
        self.assertEqual(bloqueio.status, BloqueioAgenda.Status.PENDENTE)

        self.client.force_login(self.usuario_funcionario)
        self.client.post(reverse("gestao_analisar_alteracao", args=[solicitacao.pk, "aprovar"]))
        self.client.post(reverse("gestao_analisar_bloqueio", args=[bloqueio.pk, "aprovar"]))
        solicitacao.refresh_from_db()
        bloqueio.refresh_from_db()
        self.disponibilidade.refresh_from_db()
        self.assertEqual(solicitacao.status, SolicitacaoDisponibilidade.Status.APROVADA)
        self.assertEqual(bloqueio.status, BloqueioAgenda.Status.APROVADO)
        self.assertEqual(self.disponibilidade.horario_fim, time(11, 30))

    def test_funcionario_realiza_crud_de_consulta(self):
        self.client.force_login(self.usuario_funcionario)
        dia = self.proxima_segunda()
        data_hora = datetime.combine(dia, time(8, 0)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(reverse("gestao_consulta_nova"), {
            "paciente": self.paciente.pk,
            "medico": self.medico.pk,
            "data_hora": data_hora,
            "status": Consulta.Status.AGENDADA,
        })
        self.assertEqual(response.status_code, 302)
        consulta = Consulta.objects.get(medico=self.medico, paciente=self.paciente)

        response = self.client.post(reverse("gestao_consulta_editar", args=[consulta.pk]), {
            "paciente": self.paciente.pk,
            "medico": self.medico.pk,
            "data_hora": datetime.combine(dia, time(8, 30)).strftime("%Y-%m-%dT%H:%M"),
            "status": Consulta.Status.CONFIRMADA,
        })
        self.assertEqual(response.status_code, 302)
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, Consulta.Status.CONFIRMADA)

        response = self.client.post(reverse("gestao_consulta_excluir", args=[consulta.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Consulta.objects.filter(pk=consulta.pk).exists())
