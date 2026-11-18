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

