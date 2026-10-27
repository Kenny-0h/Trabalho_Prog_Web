from django.db import models
from django.core.exceptions import ValidationError


class Consulta(models.Model):
    class Status(models.TextChoices):
        AGENDADA = "AGENDADA", "Agendada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        COMPLETA = "COMPLETA", "Completa"
        CANCELADA = "CANCELADA", "Cancelada"
        NAO_COMPARECEU = "NAO_COMPARECEU", "Não compareceu"

    medico = models.ForeignKey(
        "usuarios.Medico",
        on_delete=models.PROTECT,
        related_name="consultas",
    )
    paciente = models.ForeignKey(
        "usuarios.Paciente",
        on_delete=models.PROTECT,
        related_name="consultas",
    )
    data_hora = models.DateTimeField(verbose_name="Data e horário")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADA,
    )

    class Meta:
        ordering = ["data_hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["medico", "data_hora"],
                name="consulta_medico_horario_unico",
            ),
        ]

    def clean(self):
        super().clean()

        if self.data_hora and self.data_hora.minute % 1 != 0:
            raise ValidationError({
                "data_hora": "Informe um horário válido."
            })

    def __str__(self):
        return (
            f"Consulta de {self.paciente} com {self.medico} "
            f"em {self.data_hora:%d/%m/%Y %H:%M}"
        )


class Prontuario(models.Model):
    consulta = models.OneToOneField(
        Consulta,
        on_delete=models.PROTECT,
        related_name="prontuario",
    )
    anamnese = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário da consulta {self.consulta_id}"


class Exame(models.Model):
    prontuario = models.ForeignKey(
        Prontuario,
        on_delete=models.CASCADE,
        related_name="exames",
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_solicitacao = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome


class Receita(models.Model):
    prontuario = models.ForeignKey(
        Prontuario,
        on_delete=models.CASCADE,
        related_name="receitas",
    )
    descricao = models.TextField()
    data_emissao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Receita do prontuário {self.prontuario_id}"
