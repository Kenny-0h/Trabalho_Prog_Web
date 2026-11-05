# Aplicativo `usuarios`

## Objetivo e responsabilidade

O aplicativo `usuarios` concentra a identidade das pessoas que utilizam o sistema e os dados associados aos quatro tipos de perfil previstos: paciente, médico, funcionário administrativo e administrador do sistema.

A implementação utiliza um modelo de usuário personalizado do Django e modelos separados para os dados específicos de cada perfil.

## Modelos

### `Usuario`

`Usuario` herda de `django.contrib.auth.models.AbstractUser`, reutilizando os recursos de autenticação do Django.

Além dos campos herdados, possui:

| Campo | Tipo | Descrição |
|---|---|---|
| `cpf` | `CharField(11)`, único | CPF do usuário. |
| `nome` | `CharField(70)` | Nome da pessoa. |
| `endereco` | `CharField(100)` | Endereço. |
| `telefone` | `CharField(20)` | Telefone. |
| `data_nascimento` | `DateField` | Data de nascimento. |
| `tipo_usuario` | `CharField` com opções | Papel do usuário no sistema. |

As opções de `tipo_usuario` são `PACIENTE`, `MEDICO`, `FUNCIONARIO` e `ADMINISTRADOR`.

O projeto configura esse modelo como modelo de autenticação principal por meio de `AUTH_USER_MODEL = 'usuarios.Usuario'` em `config/settings.py`.

O método `clean()` verifica a coerência entre o tipo informado e os perfis relacionados já existentes e impede que mais de um perfil seja associado ao mesmo usuário. A validação não exige, por si só, que todo usuário já tenha um perfil.

### `Paciente`

Possui uma relação `OneToOneField` com `Usuario` e o campo opcional `plano_medico`.

### `Medico`

Possui uma relação `OneToOneField` com `Usuario` e os campos:

- `crm`: registro profissional, único;
- `rqe`: registro de qualificação de especialista, opcional;
- `especialidade`: chave estrangeira para `agenda.Especialidade`, protegida contra exclusão enquanto houver médicos associados (`PROTECT`).

### `FuncionarioAdministrativo` e `AdministradorSistema`

Cada um possui uma relação `OneToOneField` com `Usuario`. No código atual, não possuem outros campos específicos.

## Serviço de criação

O arquivo `services.py` implementa `criar_usuario_com_perfil(...)`.

Esse serviço:

1. recebe os dados do usuário e do perfil;
2. identifica o modelo de perfil a partir de `tipo_usuario`;
3. verifica os campos obrigatórios do perfil médico (`crm` e `especialidade`);
4. cria o usuário e o perfil dentro de uma transação (`transaction.atomic`);
5. executa `full_clean()` antes de salvar os objetos.

Se a criação do perfil falhar, a transação desfaz também a criação do usuário.

## Administração

O arquivo `admin.py` registra `Usuario` com uma classe baseada em `UserAdmin` e apresenta dados pessoais, tipo de usuário, situação da conta e informações de pesquisa e filtragem.

Os quatro modelos de perfil também são registrados no Admin. Os perfis são apresentados como inlines na edição de usuários; o perfil médico permite selecionar a especialidade por autocomplete.

## Relações com outros aplicativos

- `Medico.especialidade` referencia `agenda.Especialidade`.
- `Medico` é referenciado por `agenda.Agenda` e por `atendimento.Consulta`.
- `Paciente` é referenciado por `atendimento.Consulta`.

## Testes existentes

`usuarios/tests.py` contém testes para unicidade de CPF e CRM, associação de perfis, validação de perfis incompatíveis e criação transacional de usuários e perfis.

## Limites da implementação atual

- `views.py` ainda não implementa páginas ou fluxos próprios.
- Não há arquivo `urls.py` neste aplicativo.
- O tipo de usuário está modelado, mas não há, neste estágio, uma camada completa de autorização que restrinja todas as operações de acordo com cada perfil.
- A documentação não presume que o cadastro público de pacientes ou os dashboards já estejam disponíveis.