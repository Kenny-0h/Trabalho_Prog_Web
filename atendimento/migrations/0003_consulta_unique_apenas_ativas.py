# Allow a cancelled consultation's time slot to be reused.
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("atendimento", "0002_prontuario_exame_receita"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="consulta",
            name="consulta_medico_horario_unico",
        ),
        migrations.AddConstraint(
            model_name="consulta",
            constraint=models.UniqueConstraint(
                fields=("medico", "data_hora"),
                condition=~Q(status="CANCELADA"),
                name="consulta_medico_horario_unico",
            ),
        ),
    ]
