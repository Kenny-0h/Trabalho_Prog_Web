# AgendaMedica — Sistema de Gerenciamento de Agendamento Médico

Aplicação web desenvolvida para apoiar o gerenciamento de uma clínica médica como parte do Trabalho Prático da disciplina **GAC116 — Programação Web** (UFLA). O projeto utiliza Python e Django (arquitetura MVT) e organiza o domínio em três aplicativos integrados: `usuarios`, `agenda` e `atendimento`.

## Visão geral e perfis de usuário

O sistema gerencia usuários, agendas médicas, disponibilidades, bloqueios, consultas e registros clínicos (prontuários, exames e receitas) contemplando quatro perfis com permissões e áreas distintas:

- **Paciente:** realiza autocadastro público, autentica-se no sistema, acessa seu painel exclusivo e mantém seus dados cadastrais e plano de saúde atualizados.
- **Médico:** possui painel próprio e acesso restrito aos seus horários, suas consultas e prontuários/exames/receitas dos seus pacientes.
- **Funcionário administrativo:** gerencia a operação recepcional da clínica (agendamentos, agendas, bloqueios e cadastro de pacientes), sem acesso a prontuários clínicos sigilosos nem permissão para criar médicos ou administradores.
- **Administrador do sistema:** possui controle global sobre usuários, criação de médicos, funcionários administrativos, administradores e configurações gerais do sistema.

## Aplicativos Django

| Aplicativo | Responsabilidade |
|---|---|
| [`usuarios`](docs/usuarios.md) | Modelo `Usuario` personalizado (`AbstractUser`), autenticação (login/logout), cadastro público de pacientes, redirecionamento e controle de acesso por perfil. |
| [`agenda`](docs/agenda.md) | Especialidades, agendas médicas, disponibilidades recorrentes por dia da semana e bloqueios de agenda com validação contra sobreposição. |
| [`atendimento`](docs/atendimento.md) | Consultas médicas, prontuários clínicos, solicitações de exames e emissão de receitas. |

## Tecnologias utilizadas

- **Python 3.10+**
- **Django 5.2.17**
- **Django Jazzmin 3.0.5** (personalização visual do ambiente administrativo)
- **Bootstrap 5.3.3** (interface responsiva, componentes padronizados e suporte nativo a `data-bs-theme`)
- **HTML5, CSS3 (Variáveis CSS) e JavaScript ES6** (sistema extensível de temas Claro/Escuro persistido via `localStorage`)
- **SQLite 3** (banco de dados relacional padrão para desenvolvimento e testes)
- **Git e GitHub** (controle de versão com branches `main`, `develop` e `feature/*`)

## Estrutura do projeto

```text
Trabalho_Prog_Web/
├── config/                     # Configurações globais (settings, urls, wsgi, asgi)
├── usuarios/                   # Autenticação, perfis, formulários, services e permissões
├── agenda/                     # Especialidades, agendas, disponibilidades e comando popular_dados_demo
├── atendimento/                # Consultas, prontuários, exames e receitas
├── docs/                       # DER e documentação detalhada por aplicativo
├── scripts/
│   └── iniciar.sh              # Script de preparação e inicialização automática (Linux/macOS/Git Bash)
├── static/
│   ├── css/
│   │   ├── site.css            # Estilos gerais da aplicação
│   │   └── themes/             # Arquitetura extensível de temas (light.css, dark.css, custom.css)
│   └── js/
│       └── theme.js            # Alternância e persistência de tema no localStorage
├── templates/
│   ├── base.html               # Layout base compartilhado com navbar adaptativa por perfil
│   ├── 404.html                # Página de erro personalizada
│   └── usuarios/               # Templates de início, login, cadastro, perfil e painéis por perfil
├── CHECKPOINT-2.md             # Checklist de acompanhamento e decisões técnicas do Checkpoint 2
├── manage.py
└── requirements.txt


## Ambiente administrativo e telas de gestão

Os perfis **Administrador do sistema** e **Funcionário administrativo** possuem acesso à opção **Gestão da clínica** no menu. Nela estão disponíveis telas próprias (Bootstrap) para:

- consultar, pesquisar, cadastrar, editar e excluir pacientes;
- consultar, pesquisar e cadastrar/editar médicos (a exclusão de médicos é exclusiva do administrador do sistema);
- consultar agendas e cadastrar, editar e excluir períodos de disponibilidade dos médicos;
- visualizar indicadores gerais e a quantidade de consultas por status.

Cada médico recebe automaticamente uma agenda ao ser cadastrado. A exclusão de pacientes ou médicos que já possuem consultas é bloqueada para preservar o histórico e os relacionamentos do banco.

## Banco de dados de demonstração

O repositório inclui o arquivo `banco_demo.sqlite3`, com registros inteiramente fictícios para apresentação. Para utilizá-lo:

```bash
cp banco_demo.sqlite3 db.sqlite3
python manage.py runserver
```

Se preferir criar o banco do zero:

```bash
python manage.py migrate
python manage.py popular_dados_demo
python manage.py runserver
```

### Contas demonstrativas

Todas as contas de demonstração utilizam a senha `Demo@12345`.

| Perfil | Usuário | Senha |
|---|---|---|
| Administrador do sistema | `demo_admin` | `Demo@12345` |
| Funcionário administrativo | `demo_funcionario` | `Demo@12345` |
| Médico | `demo_medico_ana` | `Demo@12345` |
| Paciente | `demo_paciente_01` | `Demo@12345` |

**Importante:** os dados são exclusivamente fictícios e a senha é pública, destinada apenas à demonstração local. Não utilize essas contas em produção. O arquivo SQLite demonstrativo deve ser tratado como massa de teste, não como banco de produção.


## Organização por perfil e telas CRUD

A área autenticada agora possui um painel inicial por perfil em `/portal/`, com dados básicos do usuário e links de acesso conforme sua função.

- Paciente: consulta de horários e histórico de consultas; cada consulta abre detalhes com abas de prontuário, receitas e exames.
- Médico: agenda própria, cadastro/edição de disponibilidades e solicitação de bloqueios para análise administrativa.
- Administrador e funcionário: consultas, pacientes, médicos, especialidades, agendas e análise de solicitações; também há listas para prontuários, exames e receitas.

As listas usam busca textual e um segundo filtro. As telas genéricas de registro permitem visualizar e, na área administrativa, editar/excluir dados.
