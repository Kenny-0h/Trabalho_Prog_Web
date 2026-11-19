from django.contrib import admin

from usuarios.models import Usuario
from .models import Consulta, Exame, Prontuario, Receita


def _perfil_usuario(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return Usuario.TipoUsuario.ADMINISTRADOR
    return getattr(user, "tipo_usuario", None)


class HorarioInicioFilter(admin.SimpleListFilter):
    title = "horário de início"
    parameter_name = "hora_inicio"

    def lookups(self, request, model_admin):
        return [(str(hora), f"{hora:02d}:00") for hora in range(24)]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(data_hora__hour=int(self.value()))
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
            return queryset.filter(medico__especialidade_id=self.value())
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

    def has_module_permission(self, request):
        return _perfil_usuario(request.user) in (
            Usuario.TipoUsuario.ADMINISTRADOR,
            Usuario.TipoUsuario.FUNCIONARIO,
            Usuario.TipoUsuario.MEDICO,
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return _perfil_usuario(request.user) in (
            Usuario.TipoUsuario.ADMINISTRADOR,
            Usuario.TipoUsuario.FUNCIONARIO,
        )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return _perfil_usuario(request.user) in (
            Usuario.TipoUsuario.ADMINISTRADOR,
            Usuario.TipoUsuario.FUNCIONARIO,
        )

    def get_inlines(self, request, obj=None):
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.FUNCIONARIO:
            return ()
        return self.inlines

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(medico__usuario=request.user)
        return qs


class ClinicoRestritoAdminBase(admin.ModelAdmin):
    """Restringe modelos clínicos (Prontuário, Exame e Receita) a Médicos e Administradores."""

    def has_module_permission(self, request):
        return _perfil_usuario(request.user) in (
            Usuario.TipoUsuario.ADMINISTRADOR,
            Usuario.TipoUsuario.MEDICO,
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return _perfil_usuario(request.user) == Usuario.TipoUsuario.ADMINISTRADOR


@admin.register(Prontuario)
class ProntuarioAdmin(ClinicoRestritoAdminBase):
    list_display = ("consulta", "criado_em")
    list_filter = ("criado_em", "consulta__medico__especialidade")
    search_fields = (
        "consulta__medico__usuario__nome",
        "consulta__paciente__usuario__nome",
        "consulta__paciente__usuario__cpf",
    )
    ordering = ("-criado_em",)
    autocomplete_fields = ("consulta",)
    readonly_fields = ("criado_em",)
    inlines = (ExameInline, ReceitaInline)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(consulta__medico__usuario=request.user)
        return qs


@admin.register(Exame)
class ExameAdmin(ClinicoRestritoAdminBase):
    list_display = ("nome", "prontuario", "data_solicitacao")
    list_filter = ("data_solicitacao",)
    search_fields = (
        "nome",
        "prontuario__consulta__paciente__usuario__nome",
        "prontuario__consulta__medico__usuario__nome",
    )
    ordering = ("-data_solicitacao",)
    autocomplete_fields = ("prontuario",)
    date_hierarchy = "data_solicitacao"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(prontuario__consulta__medico__usuario=request.user)
        return qs


@admin.register(Receita)
class ReceitaAdmin(ClinicoRestritoAdminBase):
    list_display = ("prontuario", "data_emissao")
    list_filter = ("data_emissao",)
    search_fields = (
        "descricao",
        "prontuario__consulta__paciente__usuario__nome",
        "prontuario__consulta__medico__usuario__nome",
    )
    ordering = ("-data_emissao",)
    autocomplete_fields = ("prontuario",)
    readonly_fields = ("data_emissao",)
    date_hierarchy = "data_emissao"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(prontuario__consulta__medico__usuario=request.user)
        return qs