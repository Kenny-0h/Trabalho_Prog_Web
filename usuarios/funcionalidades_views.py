from datetime import datetime, timedelta

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from agenda.models import (
    Agenda,
    BloqueioAgenda,
    Disponibilidade,
    Especialidade,
    SolicitacaoDisponibilidade,
)
from atendimento.models import Consulta
from .models import Medico, Paciente, Usuario
from .permissions import perfil_requerido

ADMINISTRATIVOS = (
    Usuario.TipoUsuario.ADMINISTRADOR,
    Usuario.TipoUsuario.FUNCIONARIO,
)


def _aplicar_estilo(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs["class"] = "form-check-input"
        else:
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class DisponibilidadeMedicoForm(forms.ModelForm):
    class Meta:
        model = Disponibilidade
        fields = ("dia_semana", "horario_inicio", "horario_fim")
        widgets = {
            "horario_inicio": forms.TimeInput(attrs={"type": "time"}),
            "horario_fim": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilo(self)


class SolicitacaoAlteracaoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoDisponibilidade
        fields = ("disponibilidade", "dia_semana", "horario_inicio", "horario_fim", "justificativa")
        widgets = {
            "horario_inicio": forms.TimeInput(attrs={"type": "time"}),
            "horario_fim": forms.TimeInput(attrs={"type": "time"}),
            "justificativa": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {"disponibilidade": "Horário atual que deseja alterar"}

    def __init__(self, *args, agenda, **kwargs):
        self.agenda = agenda
        super().__init__(*args, **kwargs)
        self.fields["disponibilidade"].queryset = Disponibilidade.objects.filter(agenda=agenda).order_by("dia_semana", "horario_inicio")
        self.fields["disponibilidade"].empty_label = "Selecione o horário atual"
        self.fields["disponibilidade"].required = True
        _aplicar_estilo(self)

    def clean(self):
        cleaned = super().clean()
        disponibilidade = cleaned.get("disponibilidade")
        if disponibilidade and disponibilidade.agenda_id != self.agenda.pk:
            self.add_error("disponibilidade", "Selecione um horário da sua própria agenda.")
        return cleaned


class SolicitacaoBloqueioForm(forms.ModelForm):
    data_hora_inicio = forms.DateTimeField(
        label="Início do bloqueio",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    data_hora_fim = forms.DateTimeField(
        label="Fim do bloqueio",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = BloqueioAgenda
        fields = ("data_hora_inicio", "data_hora_fim", "tipo", "justificativa")
        widgets = {"justificativa": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilo(self)

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("data_hora_inicio")
        fim = cleaned.get("data_hora_fim")
        if inicio and inicio < timezone.now():
            self.add_error("data_hora_inicio", "O início do bloqueio deve estar no futuro.")
        if inicio and fim and fim <= inicio:
            self.add_error("data_hora_fim", "O fim deve ser posterior ao início.")
        return cleaned


class ConsultaForm(forms.ModelForm):
    data_hora = forms.DateTimeField(
        label="Data e horário",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local", "step": "60"}),
    )

    class Meta:
        model = Consulta
        fields = ("paciente", "medico", "data_hora", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["paciente"].queryset = Paciente.objects.select_related("usuario").order_by("usuario__nome")
        self.fields["medico"].queryset = Medico.objects.select_related("usuario", "especialidade").order_by("usuario__nome")
        self.fields["paciente"].label_from_instance = lambda obj: obj.usuario.nome
        self.fields["medico"].label_from_instance = lambda obj: f"{obj.usuario.nome} — {obj.especialidade.nome}"
        _aplicar_estilo(self)

    def clean(self):
        cleaned = super().clean()
        medico = cleaned.get("medico")
        paciente = cleaned.get("paciente")
        data_hora = cleaned.get("data_hora")
        status = cleaned.get("status")
        if not (medico and paciente and data_hora and status):
            return cleaned

        if data_hora.second or data_hora.microsecond:
            self.add_error("data_hora", "Informe o horário sem segundos.")
            return cleaned

        if status == Consulta.Status.CANCELADA:
            return cleaned
        if status in (Consulta.Status.AGENDADA, Consulta.Status.CONFIRMADA) and data_hora < timezone.now():
            self.add_error("data_hora", "Não é possível agendar uma consulta em uma data passada.")

        agenda = Agenda.objects.filter(medico=medico).first()
        if not agenda:
            self.add_error("medico", "Este médico ainda não possui uma agenda cadastrada.")
            return cleaned

        local_inicio = timezone.localtime(data_hora) if timezone.is_aware(data_hora) else data_hora
        duracao = timedelta(minutes=medico.especialidade.tempo_medio_consulta)
        fim = local_inicio + duracao
        disponibilidade = Disponibilidade.objects.filter(
            agenda=agenda,
            dia_semana=local_inicio.weekday(),
            horario_inicio__lte=local_inicio.time(),
            horario_fim__gte=fim.time(),
        ).first()
        if not disponibilidade:
            self.add_error("data_hora", "O horário não está dentro da disponibilidade cadastrada para este médico.")
        else:
            minutos_desde_inicio = (
                local_inicio.hour * 60 + local_inicio.minute
                - (disponibilidade.horario_inicio.hour * 60 + disponibilidade.horario_inicio.minute)
            )
            if minutos_desde_inicio % medico.especialidade.tempo_medio_consulta:
                self.add_error("data_hora", "Escolha um horário alinhado aos intervalos de consulta da especialidade.")

        inicio_aware = timezone.make_aware(local_inicio, timezone.get_current_timezone()) if timezone.is_naive(local_inicio) else data_hora
        fim_aware = inicio_aware + duracao
        bloqueado = BloqueioAgenda.objects.filter(
            agenda=agenda,
            status=BloqueioAgenda.Status.APROVADO,
            data_hora_inicio__lt=fim_aware,
            data_hora_fim__gt=inicio_aware,
        ).exists()
        if bloqueado:
            self.add_error("data_hora", "O horário está dentro de um período bloqueado.")

        consultas_medico = Consulta.objects.filter(
            medico=medico,
            data_hora__date=local_inicio.date(),
        ).exclude(status=Consulta.Status.CANCELADA).select_related("medico__especialidade")
        consultas_paciente = Consulta.objects.filter(
            paciente=paciente,
            data_hora__date=local_inicio.date(),
        ).exclude(status=Consulta.Status.CANCELADA).select_related("medico__especialidade")
        if self.instance.pk:
            consultas_medico = consultas_medico.exclude(pk=self.instance.pk)
            consultas_paciente = consultas_paciente.exclude(pk=self.instance.pk)

        def possui_sobreposicao(consultas):
            for consulta_existente in consultas:
                inicio_existente = timezone.localtime(consulta_existente.data_hora)
                fim_existente = inicio_existente + timedelta(
                    minutes=consulta_existente.medico.especialidade.tempo_medio_consulta
                )
                if inicio_existente < fim and fim_existente > local_inicio:
                    return True
            return False

        if possui_sobreposicao(consultas_medico):
            self.add_error("data_hora", "Este médico já possui uma consulta que ocupa esse período.")
        if possui_sobreposicao(consultas_paciente):
            self.add_error("paciente", "Este paciente já possui uma consulta que ocupa esse período.")
        return cleaned


@perfil_requerido(Usuario.TipoUsuario.PACIENTE)
def disponibilidade_medicos(request):
    especialidade_id = request.GET.get("especialidade", "")
    medicos = Medico.objects.select_related("usuario", "especialidade").filter(agenda__isnull=False).prefetch_related("agenda__disponibilidades", "agenda__bloqueios")
    if especialidade_id.isdigit():
        medicos = medicos.filter(especialidade_id=int(especialidade_id))

    hoje = timezone.localdate()
    limite = hoje + timedelta(days=30)
    slots_por_medico = []
    for medico in medicos.order_by("usuario__nome"):
        agenda = medico.agenda
        duracao = timedelta(minutes=medico.especialidade.tempo_medio_consulta)
        slots = []
        disponibilidades = list(agenda.disponibilidades.all())
        bloqueios = list(agenda.bloqueios.filter(status=BloqueioAgenda.Status.APROVADO))
        consultas_existentes = list(
            Consulta.objects.filter(
                medico=medico,
                data_hora__date__range=(hoje, limite),
            ).exclude(status=Consulta.Status.CANCELADA).select_related("medico__especialidade")
        )
        for offset in range(31):
            dia = hoje + timedelta(days=offset)
            for disponibilidade in disponibilidades:
                if disponibilidade.dia_semana != dia.weekday():
                    continue
                cursor = datetime.combine(dia, disponibilidade.horario_inicio)
                fim_expediente = datetime.combine(dia, disponibilidade.horario_fim)
                while cursor + duracao <= fim_expediente:
                    inicio_naive = cursor
                    fim_naive = cursor + duracao
                    inicio = timezone.make_aware(inicio_naive, timezone.get_current_timezone())
                    fim = timezone.make_aware(fim_naive, timezone.get_current_timezone())
                    ocupado = any(
                        timezone.localtime(consulta.data_hora) < fim
                        and timezone.localtime(consulta.data_hora)
                        + timedelta(minutes=consulta.medico.especialidade.tempo_medio_consulta) > inicio
                        for consulta in consultas_existentes
                    )
                    bloqueado = any(
                        b.data_hora_inicio < fim and b.data_hora_fim > inicio
                        for b in bloqueios
                    )
                    agora_local = timezone.localtime(timezone.now())
                    if inicio >= agora_local and not ocupado and not bloqueado:
                        slots.append({"data": dia, "inicio": cursor.time(), "fim": (cursor + duracao).time()})
                    cursor += duracao
        slots_por_medico.append({"medico": medico, "slots": slots})

    return render(request, "agenda/disponibilidade_medicos.html", {
        "slots_por_medico": slots_por_medico,
        "especialidades": Especialidade.objects.order_by("nome"),
        "especialidade_selecionada": especialidade_id,
        "data_inicio": hoje,
        "data_fim": limite,
    })


@perfil_requerido(Usuario.TipoUsuario.MEDICO)
def agenda_do_medico(request):
    medico = get_object_or_404(Medico.objects.select_related("especialidade"), usuario=request.user)
    agenda, _ = Agenda.objects.get_or_create(medico=medico)
    disponibilidades = agenda.disponibilidades.all()
    bloqueios = agenda.bloqueios.all()
    solicitacoes = agenda.solicitacoes_disponibilidade.select_related("disponibilidade", "analisado_por").all()
    consultas = Consulta.objects.filter(medico=medico).select_related("paciente__usuario").order_by("data_hora")
    return render(request, "agenda/agenda_medico.html", {
        "agenda": agenda,
        "disponibilidades": disponibilidades,
        "bloqueios": bloqueios,
        "solicitacoes": solicitacoes,
        "consultas": consultas,
        "form_disponibilidade": DisponibilidadeMedicoForm(),
        "form_alteracao": SolicitacaoAlteracaoForm(agenda=agenda),
        "form_bloqueio": SolicitacaoBloqueioForm(),
    })


@perfil_requerido(Usuario.TipoUsuario.MEDICO)
def adicionar_disponibilidade_medico(request):
    if request.method != "POST":
        return redirect("agenda_medico")
    medico = get_object_or_404(Medico, usuario=request.user)
    agenda, _ = Agenda.objects.get_or_create(medico=medico)
    form = DisponibilidadeMedicoForm(request.POST)
    if form.is_valid():
        disponibilidade = form.save(commit=False)
        disponibilidade.agenda = agenda
        try:
            disponibilidade.full_clean()
            disponibilidade.save()
        except (ValidationError, IntegrityError):
            form.add_error(None, "Não foi possível cadastrar o horário. Verifique se ele se sobrepõe a outro.")
        else:
            messages.success(request, "Disponibilidade cadastrada com sucesso.")
            return redirect("agenda_medico")
    for erro in form.errors.values():
        messages.error(request, " ".join(str(item) for item in erro))
    return redirect("agenda_medico")


@perfil_requerido(Usuario.TipoUsuario.MEDICO)
def solicitar_alteracao_disponibilidade(request):
    if request.method != "POST":
        return redirect("agenda_medico")
    medico = get_object_or_404(Medico, usuario=request.user)
    agenda, _ = Agenda.objects.get_or_create(medico=medico)
    form = SolicitacaoAlteracaoForm(request.POST, agenda=agenda)
    if form.is_valid():
        solicitacao = form.save(commit=False)
        solicitacao.agenda = agenda
        try:
            solicitacao.full_clean()
            solicitacao.save()
        except ValidationError as error:
            for erro in error.messages:
                messages.error(request, erro)
        else:
            messages.success(request, "Solicitação de alteração enviada para análise administrativa.")
            return redirect("agenda_medico")
    else:
        messages.error(request, "Confira os dados da solicitação de alteração.")
    return redirect("agenda_medico")


@perfil_requerido(Usuario.TipoUsuario.MEDICO)
def solicitar_bloqueio_medico(request):
    if request.method != "POST":
        return redirect("agenda_medico")
    medico = get_object_or_404(Medico, usuario=request.user)
    agenda, _ = Agenda.objects.get_or_create(medico=medico)
    form = SolicitacaoBloqueioForm(request.POST)
    if form.is_valid():
        bloqueio = form.save(commit=False)
        bloqueio.agenda = agenda
        bloqueio.status = BloqueioAgenda.Status.PENDENTE
        try:
            bloqueio.full_clean()
            bloqueio.save()
        except ValidationError as error:
            for erro in error.messages:
                messages.error(request, erro)
        else:
            messages.success(request, "Solicitação de bloqueio enviada para análise administrativa.")
            return redirect("agenda_medico")
    else:
        messages.error(request, "Confira os dados da solicitação de bloqueio.")
    return redirect("agenda_medico")


@perfil_requerido(*ADMINISTRATIVOS)
def consultas_lista(request):
    consultas = Consulta.objects.select_related(
        "medico__usuario", "medico__especialidade", "paciente__usuario"
    ).order_by("-data_hora")
    termo = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if termo:
        consultas = consultas.filter(
            Q(medico__usuario__nome__icontains=termo)
            | Q(paciente__usuario__nome__icontains=termo)
        )
    if status in Consulta.Status.values:
        consultas = consultas.filter(status=status)
    return render(request, "gestao/consultas_lista.html", {
        "consultas": consultas,
        "termo": termo,
        "status_selecionado": status,
        "status_choices": Consulta.Status.choices,
    })


@perfil_requerido(*ADMINISTRATIVOS)
def consulta_nova(request):
    form = ConsultaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            consulta = form.save(commit=False)
            consulta.full_clean()
            consulta.save()
        except (ValidationError, IntegrityError) as error:
            for campo, erros in getattr(error, "message_dict", {}).items():
                for erro in erros:
                    form.add_error(campo if campo in form.fields else None, erro)
            if not getattr(error, "message_dict", None):
                form.add_error(None, error)
        else:
            messages.success(request, "Consulta cadastrada com sucesso.")
            return redirect("gestao_consultas")
    return render(request, "gestao/consulta_form.html", {"form": form, "titulo": "Cadastrar consulta", "voltar": reverse("gestao_consultas")})


@perfil_requerido(*ADMINISTRATIVOS)
def consulta_editar(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    form = ConsultaForm(request.POST or None, instance=consulta)
    if request.method == "POST" and form.is_valid():
        try:
            consulta = form.save(commit=False)
            consulta.full_clean()
            consulta.save()
        except (ValidationError, IntegrityError) as error:
            for campo, erros in getattr(error, "message_dict", {}).items():
                for erro in erros:
                    form.add_error(campo if campo in form.fields else None, erro)
            if not getattr(error, "message_dict", None):
                form.add_error(None, error)
        else:
            messages.success(request, "Consulta atualizada com sucesso.")
            return redirect("gestao_consultas")
    return render(request, "gestao/consulta_form.html", {"form": form, "titulo": "Editar consulta", "voltar": reverse("gestao_consultas")})


@perfil_requerido(*ADMINISTRATIVOS)
def consulta_excluir(request, pk):
    consulta = get_object_or_404(Consulta.objects.select_related("paciente__usuario", "medico__usuario"), pk=pk)
    if request.method == "POST":
        try:
            consulta.delete()
        except ProtectedError:
            messages.error(request, "Esta consulta possui prontuário associado e não pode ser excluída. Altere seu status para cancelada.")
            return redirect("gestao_consultas")
        messages.success(request, "Consulta excluída.")
        return redirect("gestao_consultas")
    return render(request, "gestao/confirmar_exclusao.html", {
        "objeto": consulta,
        "titulo": "Excluir consulta",
        "voltar": reverse("gestao_consultas"),
    })


@perfil_requerido(*ADMINISTRATIVOS)
def solicitacoes_agenda_lista(request):
    alteracoes = SolicitacaoDisponibilidade.objects.select_related(
        "agenda__medico__usuario", "disponibilidade", "analisado_por"
    ).order_by("status", "-criado_em")
    bloqueios = BloqueioAgenda.objects.select_related("agenda__medico__usuario").order_by("status", "-criado_em")
    return render(request, "gestao/solicitacoes_agenda.html", {
        "alteracoes": alteracoes,
        "bloqueios": bloqueios,
    })


@require_POST
@perfil_requerido(*ADMINISTRATIVOS)
def analisar_solicitacao_alteracao(request, pk, acao):
    solicitacao = get_object_or_404(SolicitacaoDisponibilidade.objects.select_related("disponibilidade"), pk=pk)
    if solicitacao.status != SolicitacaoDisponibilidade.Status.PENDENTE:
        messages.warning(request, "Esta solicitação já foi analisada.")
        return redirect("gestao_solicitacoes_agenda")
    if acao == "aprovar":
        disponibilidade = solicitacao.disponibilidade
        if disponibilidade is None:
            messages.error(request, "O horário original não existe mais; não é possível aprovar a alteração.")
            return redirect("gestao_solicitacoes_agenda")
        disponibilidade.dia_semana = solicitacao.dia_semana
        disponibilidade.horario_inicio = solicitacao.horario_inicio
        disponibilidade.horario_fim = solicitacao.horario_fim
        try:
            disponibilidade.full_clean()
            consultas_futuras = Consulta.objects.filter(
                medico=solicitacao.agenda.medico,
                data_hora__gte=timezone.now(),
            ).exclude(status=Consulta.Status.CANCELADA).select_related("medico__especialidade")
            for consulta in consultas_futuras:
                inicio_consulta = timezone.localtime(consulta.data_hora)
                fim_consulta = inicio_consulta + timedelta(
                    minutes=consulta.medico.especialidade.tempo_medio_consulta
                )
                coberta_pela_alterada = (
                    inicio_consulta.weekday() == disponibilidade.dia_semana
                    and disponibilidade.horario_inicio <= inicio_consulta.time()
                    and disponibilidade.horario_fim >= fim_consulta.time()
                )
                coberta_por_outra = Disponibilidade.objects.filter(
                    agenda=solicitacao.agenda,
                    dia_semana=inicio_consulta.weekday(),
                    horario_inicio__lte=inicio_consulta.time(),
                    horario_fim__gte=fim_consulta.time(),
                ).exclude(pk=disponibilidade.pk).exists()
                if not coberta_pela_alterada and not coberta_por_outra:
                    messages.error(
                        request,
                        "A alteração deixaria uma consulta futura fora da disponibilidade. Reorganize os atendimentos antes de aprovar.",
                    )
                    return redirect("gestao_solicitacoes_agenda")
            disponibilidade.save()
        except (ValidationError, IntegrityError):
            messages.error(request, "A alteração geraria um conflito com outra disponibilidade. Solicitação mantida como pendente.")
            return redirect("gestao_solicitacoes_agenda")
        solicitacao.status = SolicitacaoDisponibilidade.Status.APROVADA
    elif acao == "rejeitar":
        solicitacao.status = SolicitacaoDisponibilidade.Status.REJEITADA
    else:
        messages.error(request, "Ação inválida.")
        return redirect("gestao_solicitacoes_agenda")
    solicitacao.analisado_por = request.user
    solicitacao.analisado_em = timezone.now()
    solicitacao.save(update_fields=["status", "analisado_por", "analisado_em"])
    messages.success(request, "Solicitação analisada.")
    return redirect("gestao_solicitacoes_agenda")


@require_POST
@perfil_requerido(*ADMINISTRATIVOS)
def analisar_bloqueio_agenda(request, pk, acao):
    bloqueio = get_object_or_404(BloqueioAgenda, pk=pk)
    if bloqueio.status != BloqueioAgenda.Status.PENDENTE:
        messages.warning(request, "Este bloqueio já foi analisado.")
    elif acao == "aprovar":
        consultas_no_periodo = Consulta.objects.filter(
            medico=bloqueio.agenda.medico,
            data_hora__date__range=(
                timezone.localtime(bloqueio.data_hora_inicio).date(),
                timezone.localtime(bloqueio.data_hora_fim).date(),
            ),
        ).exclude(status=Consulta.Status.CANCELADA).select_related("medico__especialidade")
        conflito = any(
            timezone.localtime(consulta.data_hora) < bloqueio.data_hora_fim
            and timezone.localtime(consulta.data_hora)
            + timedelta(minutes=consulta.medico.especialidade.tempo_medio_consulta)
            > bloqueio.data_hora_inicio
            for consulta in consultas_no_periodo
        )
        if conflito:
            messages.error(request, "Há consultas agendadas dentro desse período. Reorganize os atendimentos antes de aprovar o bloqueio.")
            return redirect("gestao_solicitacoes_agenda")
        bloqueio.status = BloqueioAgenda.Status.APROVADO
        bloqueio.save(update_fields=["status"])
        messages.success(request, "Bloqueio aprovado.")
    elif acao == "rejeitar":
        bloqueio.status = BloqueioAgenda.Status.REJEITADO
        bloqueio.save(update_fields=["status"])
        messages.success(request, "Bloqueio rejeitado.")
    else:
        messages.error(request, "Ação inválida.")
    return redirect("gestao_solicitacoes_agenda")
