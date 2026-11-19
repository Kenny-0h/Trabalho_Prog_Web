# Aplicativo `atendimento`

## Objetivo e responsabilidade

O aplicativo `atendimento` reúne os registros de consultas e as informações clínicas vinculadas aos atendimentos: prontuários, exames e receitas.

Na implementação atual, este aplicativo também contém o modelo `Consulta`. Isso é relevante porque a proposta inicial de arquitetura descrevia consultas dentro de `agenda`, mas o código foi implementado em `atendimento`.

## Modelos

### `Consulta`

Representa uma consulta entre um médico e um paciente.

| Campo | Tipo | Descrição |
|---|---|---|
| `medico` | `ForeignKey` | Médico responsável, relacionado a `usuarios.Medico`. |
| `paciente` | `ForeignKey` | Paciente atendido, relacionado a `usuarios.Paciente`. |
| `data_hora` | `DateTimeField` | Data e horário da consulta. |
| `status` | `CharField` com opções | Situação atual da consulta. |

Os estados disponíveis são:

- `AGENDADA`
- `CONFIRMADA`
- `COMPLETA`
- `CANCELADA`
- `NAO_COMPARECEU`

O estado inicial é `AGENDADA`. A ordenação padrão é cronológica. Uma restrição de unicidade impede que o mesmo médico tenha duas consultas registradas no mesmo instante (`medico`, `data_hora`).

O método `clean()` rejeita horários que contenham segundos diferentes de zero. Essa validação é executada quando `full_clean()` é chamado; ela não constitui, isoladamente, uma regra automática de transição entre estados.

A especialidade da consulta é obtida por meio do médico associado; não existe um campo `especialidade` diretamente em `Consulta`.

### `Prontuario`

Possui uma relação `OneToOneField` com `Consulta`, portanto cada consulta pode ter no máximo um prontuário.

Campos:

- `anamnese`: texto opcional;
- `diagnostico`: texto opcional;
- `observacoes`: texto opcional;
- `criado_em`: data e hora de criação automática.

O prontuário não duplica os relacionamentos com paciente e médico: esses dados são acessados por meio da consulta.

### `Exame`

Possui uma relação `ForeignKey` com `Prontuario`, permitindo vários exames para o mesmo prontuário.

Campos:

- `nome`;
- `descricao`, opcional;
- `data_solicitacao`, opcional.

### `Receita`

Possui uma relação `ForeignKey` com `Prontuario`, permitindo várias receitas para o mesmo prontuário.

Campos:

- `descricao`;
- `data_emissao`, preenchida automaticamente.

## Administração

O arquivo `admin.py` registra os quatro modelos.

Na administração de consultas, há filtros por data, horário, médico, paciente, especialidade e status, além de pesquisa por nomes, CPF e CRM. O prontuário pode ser editado como inline da consulta.

Na administração de prontuários, exames e receitas são apresentados como inlines. Os registros de criação/emissão são exibidos como campos somente de leitura quando configurado no Admin.

## Relações com outros aplicativos

- `Consulta.medico` referencia `usuarios.Medico`.
- `Consulta.paciente` referencia `usuarios.Paciente`.
- `Prontuario.consulta` referencia `atendimento.Consulta`.
- `Exame.prontuario` referencia `atendimento.Prontuario`.
- `Receita.prontuario` referencia `atendimento.Prontuario`.
- A especialidade de uma consulta pode ser obtida por `consulta.medico.especialidade`.

## Testes existentes

`atendimento/tests.py` contém testes para o estado inicial da consulta, estados disponíveis, unicidade do horário por médico, relações entre consulta e prontuário, multiplicidade de exames e receitas e acesso aos dados do médico e do paciente pela consulta.

## Limites da implementação atual

- `views.py` ainda não implementa páginas ou fluxos próprios.
- Não há arquivo `urls.py` neste aplicativo.
- Os estados estão definidos no modelo, mas não há, nos arquivos analisados, serviços que controlem formalmente as transições permitidas.
- Não há fluxo de interface para criar, visualizar ou editar consultas e registros clínicos fora do Django Admin.
- A regra de antecedência mínima para cancelamento descrita na proposta do sistema ainda não aparece implementada nos modelos ou serviços analisados.