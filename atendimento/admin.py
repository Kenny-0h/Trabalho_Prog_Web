from django.contrib import admin

from .models import Consulta, Prontuario, Exame, Receita


class HorarioInicioFilter(admin.SimpleListFilter):
    title = "horário de início"
    parameter_name = "hora_inicio"

    def lookups(self, request, model_admin):
        return [
            (str(hora), f"{hora:02d}:00")
            for hora in range(24)
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(
                data_hora__hour=int(self.value())
            )
        return queryset


class EspecialidadeConsultaFilter(admin.SimpleListFilter):
    title = "especialidade"
    parameter_name = "especialidade"

    def lookups(self, request, model_admin):
        from agenda.models import Especialidade

        especialidades = Especialidade.objects.order_by("nome")
        return [
            (str(especialidade.pk), especialidade.nome)
            for especialidade in especialidades
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                medico__especialidade_id=self.value()
            )
        return queryset


class ProntuarioInline(admin.StackedInline):
    model = Prontuario
    extra = 0
    max_num = 1
    show_change_link = True


class ExameInline(admin.TabularInline):
    model = Exame
    extra = 0


class ReceitaInline(admin.TabularInline):
    model = Receita
    extra = 0


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = (
        "data_hora",
        "medico",
        "paciente",
        "status",
    )

    list_filter = (
        "data_hora",
        HorarioInicioFilter,
        "medico",
        "paciente",
        EspecialidadeConsultaFilter,
        "status",
    )

    search_fields = (
        "medico__usuario__nome",
        "medico__crm",
        "paciente__usuario__nome",
        "paciente__usuario__cpf",
    )

    autocomplete_fields = ("medico", "paciente")
    date_hierarchy = "data_hora"
    ordering = ("data_hora",)
    list_per_page = 25
    inlines = (ProntuarioInline,)


@admin.register(Prontuario)
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ("consulta", "criado_em")
    search_fields = (
        "consulta__medico__usuario__nome",
        "consulta__paciente__usuario__nome",
        "consulta__paciente__usuario__cpf",
    )
    autocomplete_fields = ("consulta",)
    readonly_fields = ("criado_em",)
    inlines = (ExameInline, ReceitaInline)


@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ("nome", "prontuario", "data_solicitacao")
    list_filter = ("data_solicitacao",)
    search_fields = (
        "nome",
        "prontuario__consulta__paciente__usuario__nome",
        "prontuario__consulta__medico__usuario__nome",
    )
    autocomplete_fields = ("prontuario",)
    date_hierarchy = "data_solicitacao"


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ("prontuario", "data_emissao")
    search_fields = (
        "descricao",
        "prontuario__consulta__paciente__usuario__nome",
        "prontuario__consulta__medico__usuario__nome",
    )
    autocomplete_fields = ("prontuario",)
    readonly_fields = ("data_emissao",)
    date_hierarchy = "data_emissao"
