from datetime import date, datetime, time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from usuarios.models import Usuario, Medico, Paciente
from agenda.models import (
    Especialidade,
    Agenda,
    Disponibilidade,
    BloqueioAgenda,
)
from atendimento.models import Consulta, Prontuario, Exame, Receita


class Command(BaseCommand):
    help = "Cria dados de demonstração para o Django Admin."

    def criar_usuario(self, dados):
        usuario, criado = Usuario.objects.get_or_create(
            username=dados["username"],
            defaults={
                "cpf": dados["cpf"],
                "nome": dados["nome"],
                "email": dados["email"],
                "endereco": dados["endereco"],
                "telefone": dados["telefone"],
                "data_nascimento": date.fromisoformat(
                    dados["nascimento"]
                ),
                "tipo_usuario": dados["tipo"],
                "is_active": True,
            },
        )

        if criado:
            usuario.set_unusable_password()
            usuario.save(update_fields=["password"])

        return usuario

    def criar_consulta(self, dados, medicos, pacientes):
        data_hora = datetime.combine(
            date.fromisoformat(dados["data"]),
            time.fromisoformat(dados["hora"]),
        )
        data_hora = timezone.make_aware(
            data_hora,
            timezone.get_current_timezone(),
        )

        consulta, _ = Consulta.objects.get_or_create(
            medico=medicos[dados["medico"]],
            data_hora=data_hora,
            defaults={
                "paciente": pacientes[dados["paciente"]],
                "status": dados["status"],
            },
        )

        return consulta

    @transaction.atomic
    def handle(self, *args, **options):
        especialidades_dados = [
            ("Cardiologia", 30),
            ("Dermatologia", 30),
            ("Pediatria", 20),
            ("Ortopedia", 30),
        ]

        especialidades = {}

        for nome, duracao in especialidades_dados:
            especialidade, _ = Especialidade.objects.get_or_create(
                nome=nome,
                defaults={"tempo_medio_consulta": duracao},
            )
            especialidades[nome] = especialidade

        medicos_dados = [
            {
                "username": "demo_medico_ana",
                "cpf": "90000000001",
                "nome": "Ana Martins",
                "email": "ana.demo@example.com",
                "endereco": "Rua das Flores, 100",
                "telefone": "(35) 90000-0001",
                "nascimento": "1980-03-15",
                "crm": "DEMO900001",
                "rqe": "DEMO100001",
                "especialidade": "Cardiologia",
            },
            {
                "username": "demo_medico_bruno",
                "cpf": "90000000002",
                "nome": "Bruno Almeida",
                "email": "bruno.demo@example.com",
                "endereco": "Avenida Central, 200",
                "telefone": "(35) 90000-0002",
                "nascimento": "1978-07-22",
                "crm": "DEMO900002",
                "rqe": "DEMO100002",
                "especialidade": "Dermatologia",
            },
            {
                "username": "demo_medico_carla",
                "cpf": "90000000003",
                "nome": "Carla Ribeiro",
                "email": "carla.demo@example.com",
                "endereco": "Rua do Comércio, 300",
                "telefone": "(35) 90000-0003",
                "nascimento": "1985-11-09",
                "crm": "DEMO900003",
                "rqe": "DEMO100003",
                "especialidade": "Pediatria",
            },
            {
                "username": "demo_medico_diego",
                "cpf": "90000000004",
                "nome": "Diego Costa",
                "email": "diego.demo@example.com",
                "endereco": "Rua da Saúde, 400",
                "telefone": "(35) 90000-0004",
                "nascimento": "1982-05-18",
                "crm": "DEMO900004",
                "rqe": "DEMO100004",
                "especialidade": "Ortopedia",
            },
        ]

        medicos = {}

        for dados in medicos_dados:
            usuario = self.criar_usuario({
                **dados,
                "tipo": Usuario.TipoUsuario.MEDICO,
            })

            medico, _ = Medico.objects.get_or_create(
                usuario=usuario,
                defaults={
                    "crm": dados["crm"],
                    "rqe": dados["rqe"],
                    "especialidade": especialidades[
                        dados["especialidade"]
                    ],
                },
            )
            medicos[dados["username"]] = medico

        pacientes_dados = [
            {
                "username": "demo_paciente_01",
                "cpf": "90000000011",
                "nome": "Mariana Souza",
                "email": "mariana.demo@example.com",
                "endereco": "Rua A, 10",
                "telefone": "(35) 90000-0011",
                "nascimento": "1992-02-12",
                "plano": "Plano Vida",
            },
            {
                "username": "demo_paciente_02",
                "cpf": "90000000012",
                "nome": "Pedro Santos",
                "email": "pedro.demo@example.com",
                "endereco": "Rua B, 20",
                "telefone": "(35) 90000-0012",
                "nascimento": "1988-06-24",
                "plano": "Saúde Mais",
            },
            {
                "username": "demo_paciente_03",
                "cpf": "90000000013",
                "nome": "Julia Ferreira",
                "email": "julia.demo@example.com",
                "endereco": "Rua C, 30",
                "telefone": "(35) 90000-0013",
                "nascimento": "2001-09-03",
                "plano": "Particular",
            },
            {
                "username": "demo_paciente_04",
                "cpf": "90000000014",
                "nome": "Rafael Oliveira",
                "email": "rafael.demo@example.com",
                "endereco": "Rua D, 40",
                "telefone": "(35) 90000-0014",
                "nascimento": "1975-12-17",
                "plano": "Plano Vida",
            },
            {
                "username": "demo_paciente_05",
                "cpf": "90000000015",
                "nome": "Beatriz Lima",
                "email": "beatriz.demo@example.com",
                "endereco": "Rua E, 50",
                "telefone": "(35) 90000-0015",
                "nascimento": "2010-04-28",
                "plano": "Saúde Mais",
            },
        ]

        pacientes = {}

        for dados in pacientes_dados:
            usuario = self.criar_usuario({
                **dados,
                "tipo": Usuario.TipoUsuario.PACIENTE,
            })

            paciente, _ = Paciente.objects.get_or_create(
                usuario=usuario,
                defaults={"plano_medico": dados["plano"]},
            )
            pacientes[dados["username"]] = paciente

        # Cada médico possui uma única agenda.
        agendas = {}

        for username, medico in medicos.items():
            agenda, _ = Agenda.objects.get_or_create(medico=medico)
            agendas[username] = agenda

        # Disponibilidades recorrentes, sem sobreposição.
        disponibilidades = [
            ("demo_medico_ana", 0, "08:00", "12:00"),
            ("demo_medico_ana", 2, "13:00", "17:00"),
            ("demo_medico_bruno", 1, "08:00", "12:00"),
            ("demo_medico_bruno", 3, "13:00", "17:00"),
            ("demo_medico_carla", 0, "13:00", "17:00"),
            ("demo_medico_carla", 4, "08:00", "12:00"),
            ("demo_medico_diego", 2, "08:00", "12:00"),
            ("demo_medico_diego", 4, "13:00", "17:00"),
        ]

        for username, dia, inicio, fim in disponibilidades:
            Disponibilidade.objects.get_or_create(
                agenda=agendas[username],
                dia_semana=dia,
                horario_inicio=time.fromisoformat(inicio),
                horario_fim=time.fromisoformat(fim),
            )

        # Bloqueios em datas fixas para manter a execução reproduzível.
        bloqueios = [
            {
                "medico": "demo_medico_ana",
                "inicio": "2026-11-10T08:00",
                "fim": "2026-11-10T12:00",
                "tipo": BloqueioAgenda.Tipo.AUSENCIA,
                "status": BloqueioAgenda.Status.APROVADO,
                "justificativa": "Ausência demonstrativa.",
            },
            {
                "medico": "demo_medico_bruno",
                "inicio": "2026-11-12T13:00",
                "fim": "2026-11-12T17:00",
                "tipo": BloqueioAgenda.Tipo.FERIAS,
                "status": BloqueioAgenda.Status.PENDENTE,
                "justificativa": "Solicitação demonstrativa de bloqueio.",
            },
            {
                "medico": "demo_medico_carla",
                "inicio": "2026-11-14T08:00",
                "fim": "2026-11-14T12:00",
                "tipo": BloqueioAgenda.Tipo.OUTRO,
                "status": BloqueioAgenda.Status.REJEITADO,
                "justificativa": "Bloqueio demonstrativo rejeitado.",
            },
        ]

        for dados in bloqueios:
            inicio = timezone.make_aware(
                datetime.fromisoformat(dados["inicio"]),
                timezone.get_current_timezone(),
            )
            fim = timezone.make_aware(
                datetime.fromisoformat(dados["fim"]),
                timezone.get_current_timezone(),
            )

            BloqueioAgenda.objects.get_or_create(
                agenda=agendas[dados["medico"]],
                data_hora_inicio=inicio,
                data_hora_fim=fim,
                defaults={
                    "tipo": dados["tipo"],
                    "status": dados["status"],
                    "justificativa": dados["justificativa"],
                },
            )

        # Datas fixas: a reexecução não cria novas consultas a cada dia.
        consultas_dados = [
            {
                "medico": "demo_medico_ana",
                "paciente": "demo_paciente_01",
                "data": "2026-09-03",
                "hora": "08:00",
                "status": Consulta.Status.COMPLETA,
            },
            {
                "medico": "demo_medico_ana",
                "paciente": "demo_paciente_02",
                "data": "2026-09-10",
                "hora": "09:00",
                "status": Consulta.Status.COMPLETA,
            },
            {
                "medico": "demo_medico_bruno",
                "paciente": "demo_paciente_03",
                "data": "2026-09-15",
                "hora": "10:00",
                "status": Consulta.Status.NAO_COMPARECEU,
            },
            {
                "medico": "demo_medico_bruno",
                "paciente": "demo_paciente_04",
                "data": "2026-09-18",
                "hora": "11:00",
                "status": Consulta.Status.CANCELADA,
            },
            {
                "medico": "demo_medico_carla",
                "paciente": "demo_paciente_05",
                "data": "2026-10-02",
                "hora": "14:00",
                "status": Consulta.Status.COMPLETA,
            },
            {
                "medico": "demo_medico_diego",
                "paciente": "demo_paciente_01",
                "data": "2026-10-07",
                "hora": "09:00",
                "status": Consulta.Status.CONFIRMADA,
            },
            {
                "medico": "demo_medico_ana",
                "paciente": "demo_paciente_03",
                "data": "2026-11-05",
                "hora": "10:00",
                "status": Consulta.Status.AGENDADA,
            },
            {
                "medico": "demo_medico_carla",
                "paciente": "demo_paciente_02",
                "data": "2026-11-06",
                "hora": "15:00",
                "status": Consulta.Status.AGENDADA,
            },
        ]

        consultas = []

        for dados in consultas_dados:
            consulta = self.criar_consulta(dados, medicos, pacientes)
            consultas.append(consulta)

        # Prontuários, exames e receitas para consultas completas.
        registros_clinicos = [
            {
                "consulta": consultas[0],
                "anamnese": "Paciente relata acompanhamento de rotina.",
                "diagnostico": "Avaliação clínica de rotina.",
                "observacoes": "Dados fictícios para demonstração.",
                "exame": "Eletrocardiograma",
                "descricao_exame": "Exame demonstrativo.",
                "receita": "Prescrição fictícia para demonstração.",
            },
            {
                "consulta": consultas[1],
                "anamnese": "Paciente relata cansaço recente.",
                "diagnostico": "Avaliação clínica realizada.",
                "observacoes": "Registro fictício.",
                "exame": "Hemograma",
                "descricao_exame": "Solicitação demonstrativa.",
                "receita": "Orientações fictícias para demonstração.",
            },
            {
                "consulta": consultas[4],
                "anamnese": "Consulta pediátrica de rotina.",
                "diagnostico": "Avaliação de acompanhamento.",
                "observacoes": "Registro fictício para apresentação.",
                "exame": "Hemograma",
                "descricao_exame": "Exame de exemplo.",
                "receita": "Receita fictícia para apresentação.",
            },
        ]

        for dados in registros_clinicos:
            prontuario, _ = Prontuario.objects.get_or_create(
                consulta=dados["consulta"],
                defaults={
                    "anamnese": dados["anamnese"],
                    "diagnostico": dados["diagnostico"],
                    "observacoes": dados["observacoes"],
                },
            )

            Exame.objects.get_or_create(
                prontuario=prontuario,
                nome=dados["exame"],
                defaults={
                    "descricao": dados["descricao_exame"],
                    "data_solicitacao": dados["consulta"].data_hora.date(),
                },
            )

            Receita.objects.get_or_create(
                prontuario=prontuario,
                descricao=dados["receita"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Dados de demonstração criados ou já existentes."
            )
        )
