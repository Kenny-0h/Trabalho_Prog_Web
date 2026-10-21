from django.db import models


class Especialidade(models.Model):
    nome = models.CharField(max_length=30, unique=True)
    tempo_medio_consulta = models.PositiveIntegerField(
        help_text="Tempo médio da consulta em minutos."
    )

    def __str__(self):
        return self.nome
