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
