
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("agenda", "0003_bloqueioagenda"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                create trigger IMPEDIR_SOBREPOSICAO_DISPONIBILIDADE_INSERT
                    before insert
                    on AGENDA_DISPONIBILIDADE
                    for each row
                    when exists (select 1
                                 from AGENDA_DISPONIBILIDADE as EXISTENTE
                                 where EXISTENTE.AGENDA_ID = NEW.AGENDA_ID
                                   and EXISTENTE.DIA_SEMANA = NEW.DIA_SEMANA
                                   and EXISTENTE.HORARIO_INICIO < NEW.HORARIO_FIM
                                   and EXISTENTE.HORARIO_FIM > NEW.HORARIO_INICIO)
                begin
                select RAISE(
                               ABORT,
                               'Disponibilidade sobreposta para a mesma agenda e dia.'
                       );
                end;
                """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS
                impedir_sobreposicao_disponibilidade_insert;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER impedir_sobreposicao_disponibilidade_update
                    BEFORE UPDATE ON agenda_disponibilidade
                    FOR EACH ROW
                    WHEN EXISTS (
                        SELECT 1
                        FROM agenda_disponibilidade AS existente
                        WHERE existente.agenda_id = NEW.agenda_id
                          AND existente.dia_semana = NEW.dia_semana
                          AND existente.horario_inicio < NEW.horario_fim
                          AND existente.horario_fim > NEW.horario_inicio
                          AND existente.id != OLD.id
                    )
                BEGIN
                SELECT RAISE(
                               ABORT,
                               'Disponibilidade sobreposta para a mesma agenda e dia.'
                       );
                END;
                """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS
                impedir_sobreposicao_disponibilidade_update;
            """,
        ),
    ]
