# Migration adding physician availability-change requests.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agenda", "0004_impedir_sobreposicao_disponibilidade"),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacaoDisponibilidade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dia_semana", models.IntegerField(choices=[(0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"), (3, "Quinta-feira"), (4, "Sexta-feira"), (5, "Sábado"), (6, "Domingo")])),
                ("horario_inicio", models.TimeField()),
                ("horario_fim", models.TimeField()),
                ("justificativa", models.TextField()),
                ("status", models.CharField(choices=[("PENDENTE", "Pendente"), ("APROVADA", "Aprovada"), ("REJEITADA", "Rejeitada")], default="PENDENTE", max_length=20)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("agenda", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="solicitacoes_disponibilidade", to="agenda.agenda")),
                ("disponibilidade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="solicitacoes", to="agenda.disponibilidade")),
            ],
            options={"ordering": ["-criado_em"]},
        ),
    ]
