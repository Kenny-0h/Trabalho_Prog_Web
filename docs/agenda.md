# Aplicativo `agenda`

## Objetivo e responsabilidade

O aplicativo `agenda` organiza os dados relacionados às especialidades médicas, às agendas dos médicos, às disponibilidades recorrentes e aos bloqueios de horários.

**Importante:** na implementação atual, o modelo `Consulta` não está neste aplicativo; ele está definido em `atendimento`.

## Modelos

### `Especialidade`

Representa uma especialidade médica.

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `CharField(30)`, único | Nome da especialidade. |
| `tempo_medio_consulta` | `PositiveIntegerField` | Duração média da consulta em minutos. |

O método `clean()` valida que o tempo médio seja maior que zero.

### `Agenda`

Possui uma relação `OneToOneField` com `usuarios.Medico`, garantindo que cada médico tenha no máximo uma agenda.

### `Disponibilidade`

Representa um intervalo recorrente de disponibilidade em um dia da semana.

| Campo | Tipo | Descrição |
|---|---|---|
| `agenda` | `ForeignKey` | Agenda à qual a disponibilidade pertence. |
| `dia_semana` | `IntegerField` com opções | Dia da semana, de segunda-feira (0) a domingo (6). |
| `horario_inicio` | `TimeField` | Início do intervalo. |
| `horario_fim` | `TimeField` | Fim do intervalo. |

A ordenação padrão é por dia da semana e horário inicial. Há uma restrição de unicidade para a combinação de agenda, dia e horários.

O método `clean()` verifica que o horário final seja posterior ao inicial e rejeita sobreposição com outra disponibilidade da mesma agenda e do mesmo dia. Além dessa validação no modelo, a migração `0004_impedir_sobreposicao_disponibilidade.py` cria triggers no banco SQLite para impedir sobreposições também em operações de inserção e atualização. Essa migração utiliza sintaxe específica do SQLite e deve ser revista caso o projeto passe a utilizar outro SGBD.

### `BloqueioAgenda`

Representa um período em que a agenda fica bloqueada.

Campos principais:

- `agenda`: agenda relacionada;
- `data_hora_inicio` e `data_hora_fim`: intervalo do bloqueio;
- `justificativa`: motivo informado;
- `tipo`: `OUTRO`, `AUSENCIA` ou `FERIAS`;
- `status`: `PENDENTE`, `APROVADO` ou `REJEITADO`;
- `criado_em`: data e hora de criação, preenchida automaticamente.

O modelo possui uma restrição de banco para exigir que o fim seja posterior ao início. O método `clean()` também realiza essa validação.

## Administração

O arquivo `admin.py` registra:

- `Especialidade`, com listagem, pesquisa e ordenação;
- `Agenda`, com pesquisa por médico e edição inline das disponibilidades;
- `Disponibilidade`, com filtro por dia da semana;
- `BloqueioAgenda`, com filtros por status e tipo, pesquisa e hierarquia por data.

## Relações com outros aplicativos

- `Agenda.medico` referencia `usuarios.Medico`.
- `Disponibilidade.agenda` referencia `agenda.Agenda`.
- `BloqueioAgenda.agenda` referencia `agenda.Agenda`.
- `usuarios.Medico.especialidade` referencia `agenda.Especialidade`.

## Testes existentes

`agenda/tests.py` contém testes para unicidade de agenda por médico, múltiplas disponibilidades, validação de horários, prevenção de sobreposições, disponibilidades consecutivas e validações de bloqueios.

## Limites da implementação atual

- `views.py` ainda não implementa páginas ou fluxos próprios.
- Não há arquivo `urls.py` neste aplicativo.
- O código modela disponibilidades e bloqueios, mas ainda não implementa uma interface pública para consultar horários livres ou solicitar agendamentos.
- A geração de horários a partir da duração média da especialidade não está implementada nos arquivos analisados.
- O modelo de consulta está em `atendimento`, conforme descrito em [atendimento.md](atendimento.md).