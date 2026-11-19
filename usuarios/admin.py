from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AdministradorSistema,
    FuncionarioAdministrativo,
    Medico,
    Paciente,
    Usuario,
)


def eh_admin_sistema(user):
    return bool(
        user.is_authenticated
        and (
            user.is_superuser
            or getattr(user, "tipo_usuario", None) == Usuario.TipoUsuario.ADMINISTRADOR
        )
    )


def eh_funcionario_clinica(user):
    return bool(
        user.is_authenticated
        and getattr(user, "tipo_usuario", None) == Usuario.TipoUsuario.FUNCIONARIO
    )


class PerfilInlineBase(admin.StackedInline):
    extra = 0
    max_num = 1


class PacienteInline(PerfilInlineBase):
    model = Paciente


class MedicoInline(PerfilInlineBase):
    model = Medico
    autocomplete_fields = ("especialidade",)


class FuncionarioInline(PerfilInlineBase):
    model = FuncionarioAdministrativo


class AdministradorInline(PerfilInlineBase):
    model = AdministradorSistema


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        "username",
        "nome",
        "cpf",
        "tipo_usuario",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "tipo_usuario",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "username",
        "nome",
        "cpf",
        "email",
        "telefone",
    )
    ordering = ("nome",)
    list_per_page = 25

    fieldsets = UserAdmin.fieldsets + (
        (
            "Dados pessoais",
            {
                "fields": (
                    "cpf",
                    "nome",
                    "endereco",
                    "telefone",
                    "data_nascimento",
                    "tipo_usuario",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Dados pessoais",
            {
                "fields": (
                    "cpf",
                    "nome",
                    "endereco",
                    "telefone",
                    "data_nascimento",
                    "tipo_usuario",
                )
            },
        ),
    )

    inlines = (
        PacienteInline,
        MedicoInline,
        FuncionarioInline,
        AdministradorInline,
    )

    def has_module_permission(self, request):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_view_permission(self, request, obj=None):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_add_permission(self, request):
        return eh_admin_sistema(request.user)

    def has_change_permission(self, request, obj=None):
        if eh_admin_sistema(request.user):
            return True
        if eh_funcionario_clinica(request.user):
            if obj is None:
                return True
            return obj.tipo_usuario == Usuario.TipoUsuario.PACIENTE
        return False

    def has_delete_permission(self, request, obj=None):
        return eh_admin_sistema(request.user)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not eh_admin_sistema(request.user):
            readonly.extend([
                "is_superuser",
                "is_staff",
                "groups",
                "user_permissions",
                "tipo_usuario",
                "last_login",
                "date_joined",
            ])
        return tuple(dict.fromkeys(readonly))

    def get_inlines(self, request, obj=None):
        if eh_admin_sistema(request.user):
            return self.inlines
        if eh_funcionario_clinica(request.user):
            return (PacienteInline,)
        return ()


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "plano_medico")
    list_filter = ("plano_medico",)
    search_fields = ("usuario__nome", "usuario__cpf", "plano_medico")
    ordering = ("usuario__nome",)
    autocomplete_fields = ("usuario",)

    def has_module_permission(self, request):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_view_permission(self, request, obj=None):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_add_permission(self, request):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_change_permission(self, request, obj=None):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_delete_permission(self, request, obj=None):
        return eh_admin_sistema(request.user)


class PerfilRestritoAdminBase(admin.ModelAdmin):
    """Restringe criação, edição e exclusão de perfis internos ao Administrador do Sistema."""

    def has_module_permission(self, request):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_view_permission(self, request, obj=None):
        return eh_admin_sistema(request.user) or eh_funcionario_clinica(request.user)

    def has_add_permission(self, request):
        return eh_admin_sistema(request.user)

    def has_change_permission(self, request, obj=None):
        return eh_admin_sistema(request.user)

    def has_delete_permission(self, request, obj=None):
        return eh_admin_sistema(request.user)


@admin.register(Medico)
class MedicoAdmin(PerfilRestritoAdminBase):
    list_display = ("usuario", "crm", "rqe", "especialidade")
    list_filter = ("especialidade",)
    search_fields = (
        "usuario__nome",
        "usuario__cpf",
        "crm",
        "rqe",
        "especialidade__nome",
    )
    ordering = ("usuario__nome",)
    autocomplete_fields = ("usuario", "especialidade")


@admin.register(FuncionarioAdministrativo)
class FuncionarioAdministrativoAdmin(PerfilRestritoAdminBase):
    list_display = ("usuario",)
    list_filter = ("usuario__is_active",)
    search_fields = ("usuario__nome", "usuario__cpf")
    ordering = ("usuario__nome",)
    autocomplete_fields = ("usuario",)


@admin.register(AdministradorSistema)
class AdministradorSistemaAdmin(PerfilRestritoAdminBase):
    list_display = ("usuario",)
    list_filter = ("usuario__is_active",)
    search_fields = ("usuario__nome", "usuario__cpf")
    ordering = ("usuario__nome",)
    autocomplete_fields = ("usuario",)