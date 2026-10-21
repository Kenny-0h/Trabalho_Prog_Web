from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        PACIENTE = "PACIENTE", "Paciente"
        MEDICO = "MEDICO", "Médico"
        FUNCIONARIO = "FUNCIONARIO", "Funcionário administrativo"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador do sistema"

    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF")
    nome = models.CharField(max_length=70, verbose_name="Nome")
    endereco = models.CharField(max_length=100, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    data_nascimento = models.DateField(verbose_name="Data de nascimento")
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        verbose_name="Tipo de usuário",
    )

    def clean(self):
        super().clean()

        if not self.pk:
            return

        perfis = {
            self.TipoUsuario.PACIENTE: Paciente,
            self.TipoUsuario.MEDICO: Medico,
            self.TipoUsuario.FUNCIONARIO: FuncionarioAdministrativo,
            self.TipoUsuario.ADMINISTRADOR: AdministradorSistema,
        }

        perfil_esperado = perfis.get(self.tipo_usuario)
        if perfil_esperado is None:
            raise ValidationError({
                "tipo_usuario": "Selecione um tipo de usuário válido."
            })

        modelos_perfil = (
            Paciente,
            Medico,
            FuncionarioAdministrativo,
            AdministradorSistema,
        )

        perfis_existentes = [
            modelo for modelo in modelos_perfil
            if modelo.objects.filter(usuario_id=self.pk).exists()
        ]

        if len(perfis_existentes) > 1:
            raise ValidationError(
                "O usuário não pode possuir mais de um perfil."
            )

        if perfis_existentes and perfis_existentes[0] != perfil_esperado:
            raise ValidationError({
                "tipo_usuario": "O tipo de usuário não corresponde ao perfil cadastrado."
            })

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


class Paciente(models.Model):
    usuario = models.OneToOneField(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="perfil_paciente",
    )
    plano_medico = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Paciente: {self.usuario.nome}"


class Medico(models.Model):
    usuario = models.OneToOneField(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="perfil_medico",
    )
    crm = models.CharField(max_length=12, unique=True)
    rqe = models.CharField(max_length=12, blank=True)
    especialidade = models.ForeignKey(
        "agenda.Especialidade",
        on_delete=models.PROTECT,
        related_name="medicos",
    )

    def __str__(self):
        return f"Dr(a). {self.usuario.nome} - CRM {self.crm}"


class FuncionarioAdministrativo(models.Model):
    usuario = models.OneToOneField(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="perfil_funcionario",
    )

    def __str__(self):
        return self.usuario.nome


class AdministradorSistema(models.Model):
    usuario = models.OneToOneField(
        "usuarios.Usuario",
        on_delete=models.CASCADE,
        related_name="perfil_administrador",
    )

    def __str__(self):
        return self.usuario.nome
