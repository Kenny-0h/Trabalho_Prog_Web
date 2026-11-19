from django.contrib import admin

from usuarios.models import Usuario
from .models import (
    Agenda,
    BloqueioAgenda,
    Disponibilidade,
    Especialidade,
)


def _perfil_usuario(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return Usuario.TipoUsuario.ADMINISTRADOR
    return getattr(user, "tipo_usuario", None)


class ClassPermissoesAgendaMixin:
    """Controla o acesso aos modelos de agenda conforme o perfil do utilizador."""

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
            Usuario.TipoUsuario.MEDICO,
        )

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return _perfil_usuario(request.user) in (
            Usuario.TipoUsuario.ADMINISTRADOR,
            Usuario.TipoUsuario.FUNCIONARIO,
        )


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "tempo_medio_consulta")
    list_filter = ("tempo_medio_consulta",)
    search_fields = ("nome",)
    ordering = ("nome",)

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
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return _perfil_usuario(request.user) == Usuario.TipoUsuario.ADMINISTRADOR


class DisponibilidadeInline(admin.TabularInline):
    model = Disponibilidade
    extra = 1
    ordering = ("dia_semana", "horario_inicio")


@admin.register(Agenda)
class AgendaAdmin(ClassPermissoesAgendaMixin, admin.ModelAdmin):
    list_display = ("medico",)
    list_filter = ("medico__especialidade",)
    search_fields = (
        "medico__usuario__nome",
        "medico__crm",
        "medico__especialidade__nome",
    )
    ordering = ("medico__usuario__nome",)
    autocomplete_fields = ("medico",)
    inlines = (DisponibilidadeInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(medico__usuario=request.user)
        return qs


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(ClassPermissoesAgendaMixin, admin.ModelAdmin):
    list_display = (
        "agenda",
        "dia_semana",
        "horario_inicio",
        "horario_fim",
    )
    list_filter = ("dia_semana", "agenda__medico__especialidade")
    search_fields = (
        "agenda__medico__usuario__nome",
        "agenda__medico__crm",
    )
    autocomplete_fields = ("agenda",)
    ordering = ("dia_semana", "horario_inicio")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(agenda__medico__usuario=request.user)
        return qs


@admin.register(BloqueioAgenda)
class BloqueioAgendaAdmin(ClassPermissoesAgendaMixin, admin.ModelAdmin):
    list_display = (
        "agenda",
        "data_hora_inicio",
        "data_hora_fim",
        "tipo",
        "status",
    )
    list_filter = ("status", "tipo", "agenda__medico__especialidade")
    search_fields = (
        "agenda__medico__usuario__nome",
        "agenda__medico__crm",
        "justificativa",
    )
    autocomplete_fields = ("agenda",)
    date_hierarchy = "data_hora_inicio"
    readonly_fields = ("criado_em",)
    ordering = ("data_hora_inicio",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if _perfil_usuario(request.user) == Usuario.TipoUsuario.MEDICO:
            return qs.filter(agenda__medico__usuario=request.user)
        return qs