
from django.core.exceptions import ValidationError
from django.db import models


class Especialidade(models.Model):
    nome = models.CharField(max_length=30, unique=True)
    tempo_medio_consulta = models.PositiveIntegerField(
        help_text="Tempo médio da consulta em minutos."
    )

    def clean(self):
        super().clean()
        if self.tempo_medio_consulta <= 0:
            raise ValidationError({
                "tempo_medio_consulta": "O tempo médio deve ser maior que zero."
            })

    def __str__(self):
        return self.nome


class Agenda(models.Model):
    medico = models.OneToOneField(
        "usuarios.Medico",
        on_delete=models.CASCADE,
        related_name="agenda",
    )

    def __str__(self):
        return f"Agenda de {self.medico}"


class Disponibilidade(models.Model):
    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 0, "Segunda-feira"
        TERCA = 1, "Terça-feira"
        QUARTA = 2, "Quarta-feira"
        QUINTA = 3, "Quinta-feira"
        SEXTA = 4, "Sexta-feira"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    agenda = models.ForeignKey(
        Agenda,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
    )
    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    class Meta:
        ordering = ["dia_semana", "horario_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["agenda", "dia_semana", "horario_inicio", "horario_fim"],
                name="disponibilidade_semana_unica",
            ),
        ]

    def clean(self):
        super().clean()

        if self.horario_inicio and self.horario_fim:
            if self.horario_inicio >= self.horario_fim:
                raise ValidationError({
                    "horario_fim": "O horário final deve ser posterior ao inicial."
                })

    def __str__(self):
        return (
            f"{self.agenda} - {self.get_dia_semana_display()} "
            f"({self.horario_inicio} às {self.horario_fim})"
        )
