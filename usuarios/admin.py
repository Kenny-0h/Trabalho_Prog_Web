from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Usuario,
    Paciente,
    Medico,
    FuncionarioAdministrativo,
    AdministradorSistema,
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


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "plano_medico")
    search_fields = ("usuario__nome", "usuario__cpf", "plano_medico")
    autocomplete_fields = ("usuario",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "crm", "rqe", "especialidade")
    list_filter = ("especialidade",)
    search_fields = (
        "usuario__nome",
        "usuario__cpf",
        "crm",
        "rqe",
        "especialidade__nome",
    )
    autocomplete_fields = ("usuario", "especialidade")


@admin.register(FuncionarioAdministrativo)
class FuncionarioAdministrativoAdmin(admin.ModelAdmin):
    list_display = ("usuario",)
    search_fields = ("usuario__nome", "usuario__cpf")
    autocomplete_fields = ("usuario",)


@admin.register(AdministradorSistema)
class AdministradorSistemaAdmin(admin.ModelAdmin):
    list_display = ("usuario",)
    search_fields = ("usuario__nome", "usuario__cpf")
    autocomplete_fields = ("usuario",)
