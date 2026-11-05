from django.core.exceptions import ValidationError
from django.db import transaction

from usuarios.models import (
    AdministradorSistema,
    FuncionarioAdministrativo,
    Medico,
    Paciente,
    Usuario,
)


@transaction.atomic
def criar_usuario_com_perfil(*, dados_usuario, dados_perfil=None):
    dados_perfil = dados_perfil or {}

    tipos_perfis = {
        Usuario.TipoUsuario.PACIENTE: Paciente,
        Usuario.TipoUsuario.MEDICO: Medico,
        Usuario.TipoUsuario.FUNCIONARIO: FuncionarioAdministrativo,
        Usuario.TipoUsuario.ADMINISTRADOR: AdministradorSistema,
    }

    tipo_usuario = dados_usuario.get("tipo_usuario")
    modelo_perfil = tipos_perfis.get(tipo_usuario)

    if modelo_perfil is None:
        raise ValidationError("Tipo de usuário inválido.")

    if tipo_usuario == Usuario.TipoUsuario.MEDICO:
        campos_obrigatorios = ("crm", "especialidade")
        faltantes = [
            campo for campo in campos_obrigatorios
            if not dados_perfil.get(campo)
        ]
        if faltantes:
            raise ValidationError({
                campo: "Este campo é obrigatório."
                for campo in faltantes
            })

    usuario = Usuario.objects.create_user(**dados_usuario)
    usuario.full_clean()
    usuario.save()

    perfil = modelo_perfil(
        usuario=usuario,
        **dados_perfil,
    )
    perfil.full_clean()
    perfil.save()

    return usuario
