from django.contrib import admin

from .models import (
    Especialidade,
    Agenda,
    Disponibilidade,
    BloqueioAgenda,
)


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "tempo_medio_consulta")
    search_fields = ("nome",)
    ordering = ("nome",)


class DisponibilidadeInline(admin.TabularInline):
    model = Disponibilidade
    extra = 1
    ordering = ("dia_semana", "horario_inicio")


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ("medico",)
    search_fields = (
        "medico__usuario__nome",
        "medico__crm",
    )
    autocomplete_fields = ("medico",)
    inlines = (DisponibilidadeInline,)


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = (
        "agenda",
        "dia_semana",
        "horario_inicio",
        "horario_fim",
    )
    list_filter = ("dia_semana",)
    search_fields = (
        "agenda__medico__usuario__nome",
        "agenda__medico__crm",
    )
    autocomplete_fields = ("agenda",)
    ordering = ("dia_semana", "horario_inicio")


@admin.register(BloqueioAgenda)
class BloqueioAgendaAdmin(admin.ModelAdmin):
    list_display = (
        "agenda",
        "data_hora_inicio",
        "data_hora_fim",
        "tipo",
        "status",
    )
    list_filter = ("status", "tipo")
    search_fields = (
        "agenda__medico__usuario__nome",
        "agenda__medico__crm",
        "justificativa",
    )
    autocomplete_fields = ("agenda",)
    date_hierarchy = "data_hora_inicio"
    readonly_fields = ("criado_em",)
    ordering = ("data_hora_inicio",)
