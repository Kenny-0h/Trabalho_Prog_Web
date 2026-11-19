# AgendaMedica — Sistema de Gerenciamento de Agendamento Médico

Aplicação web desenvolvida para apoiar o gerenciamento de uma clínica médica, como parte do Trabalho Prático da disciplina **GAC116 — Programação Web**, da Universidade Federal de Lavras (UFLA).

O sistema foi desenvolvido em Python com Django, utilizando a arquitetura MVT e três aplicativos principais: `usuarios`, `agenda` e `atendimento`.

## Equipe

> **Integrantes:** preencher com os nomes dos integrantes do grupo.

## Tecnologias utilizadas

- **Python 3.10 ou superior**
- **Django 5.2.17**
- **Django Jazzmin 3.0.5**, para personalização do Django Admin
- **SQLite 3**, banco de dados relacional utilizado por padrão
- **HTML5, CSS3 e JavaScript**
- **Bootstrap 5.3**, para os componentes e a responsividade da interface
- **Git e GitHub**, para controle de versão

## Funcionalidades

O sistema contempla quatro perfis de usuário, com áreas e permissões distintas:

- **Paciente:** cadastro, autenticação, acesso ao portal, consulta de disponibilidades e visualização de suas consultas e respectivos registros clínicos.
- **Médico:** acesso à própria agenda, gerenciamento de disponibilidades e solicitação de bloqueios ou alterações de agenda.
- **Funcionário administrativo:** gerenciamento de pacientes, médicos, agendas e consultas, além da análise de solicitações administrativas.
- **Administrador do sistema:** acesso administrativo ampliado, incluindo o gerenciamento de usuários e configurações pelo Django Admin.

Entre as funcionalidades implementadas estão:

- autenticação, logout e cadastro público de pacientes;
- redirecionamento e controle de acesso conforme o perfil;
- gestão de pacientes e médicos;
- cadastro e manutenção de especialidades;
- agendas médicas, disponibilidades e bloqueios de horários;
- gerenciamento de consultas e seus estados;
- registros clínicos associados às consultas, incluindo prontuários, exames e receitas;
- painel administrativo personalizado com Jazzmin;
- interface com tema claro e escuro.

## Organização dos aplicativos

| Aplicativo | Responsabilidade |
|---|---|
| `usuarios` | Modelo de usuário personalizado, perfis, autenticação, formulários, permissões, portal e telas de gestão. |
| `agenda` | Especialidades, agendas médicas, disponibilidades recorrentes e bloqueios de agenda. |
| `atendimento` | Consultas, prontuários, exames e receitas. |

A documentação técnica dos modelos e relacionamentos está disponível em [`docs/`](docs/).

## Estrutura do projeto

```text
Trabalho_Prog_Web/
├── config/                 # Configurações globais do Django
├── usuarios/               # Usuários, perfis, autenticação e permissões
├── agenda/                 # Especialidades, agendas e disponibilidades
├── atendimento/            # Consultas e registros clínicos
├── docs/                   # Documentação técnica e DER
├── scripts/
│   └── iniciar.sh          # Preparação do ambiente e inicialização (Linux/macOS)
├── static/
│   ├── css/                # Estilos da aplicação e temas
│   └── js/                 # JavaScript da interface
├── templates/              # Templates HTML
├── banco_demo.sqlite3      # Banco separado com dados fictícios para demonstração
├── db.sqlite3              # Banco SQLite utilizado por padrão no projeto
├── manage.py               # Utilitário de gerenciamento do Django
└── requirements.txt        # Dependências Python
```

## Requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.10 ou superior;
- `pip`, para instalar as dependências;
- `venv`, para criar o ambiente virtual.

No Ubuntu/Pop!_OS, caso o módulo `venv` não esteja instalado, execute:

```bash
sudo apt install python3-venv
```

## Instalação e execução

### Opção 1 — Linux ou macOS: script de inicialização

Na raiz do projeto, execute:

```bash
chmod +x scripts/iniciar.sh
./scripts/iniciar.sh
```

O script cria o ambiente virtual `.venv` caso ele ainda não exista, instala as dependências de `requirements.txt`, aplica as migrações, verifica a configuração do Django e inicia o servidor local em `http://127.0.0.1:8000/`.

### Opção 2 — Instalação manual

Na raiz do projeto, execute os comandos abaixo.

**1. Criar o ambiente virtual:**

```bash
python3 -m venv .venv
```

**2. Ativar o ambiente virtual:**

Linux ou macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

**3. Instalar as dependências:**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**4. Aplicar as migrações do banco de dados:**

```bash
python manage.py migrate
```

**5. (Opcional) Criar um usuário administrador:**

```bash
python manage.py createsuperuser
```

Siga as instruções do terminal para informar nome de usuário, e-mail e senha.

**6. Iniciar o servidor:**

```bash
python manage.py runserver
```

A aplicação ficará disponível em:

- Site: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

Para encerrar o servidor, pressione `Ctrl+C` no terminal.

## Banco de dados

O projeto utiliza **SQLite**. A configuração em `config/settings.py` define `db.sqlite3`, localizado na raiz do projeto, como banco de dados padrão.

O repositório também contém `banco_demo.sqlite3`, um banco separado com registros fictícios para demonstração.

### Usar o banco padrão do projeto

Com as dependências instaladas, execute:

```bash
python manage.py migrate
```

Esse comando aplica as migrações pendentes no banco `db.sqlite3`.

### Usar o banco de demonstração

Se quiser iniciar com os dados fictícios, faça uma cópia do banco de demonstração para o nome esperado pela configuração do Django. Na raiz do projeto:

Linux ou macOS:

```bash
cp banco_demo.sqlite3 db.sqlite3
```

Windows (PowerShell):

```powershell
Copy-Item banco_demo.sqlite3 db.sqlite3
```

**Atenção:** esses comandos substituem o arquivo `db.sqlite3` caso ele já exista. Se quiser preservar seu banco atual, faça uma cópia de segurança antes.

### Contas demonstrativas

As contas abaixo estão disponíveis no banco `banco_demo.sqlite3`. Todas utilizam a senha `Demo@12345`.

| Perfil | Usuário | Senha |
|---|---|---|
| Administrador do sistema | `demo_admin` | `Demo@12345` |
| Funcionário administrativo | `demo_funcionario` | `Demo@12345` |
| Médico | `demo_medico_ana` | `Demo@12345` |
| Paciente | `demo_paciente_01` | `Demo@12345` |

Os dados são fictícios e destinados somente à demonstração local. Não utilize essas contas em produção.

## Testes

Para executar os testes automatizados dos aplicativos:

```bash
python manage.py test
```

Para verificar a configuração do projeto:

```bash
python manage.py check
```

## Observações de segurança

As configurações presentes no projeto são voltadas ao desenvolvimento local. Antes de publicar a aplicação em produção, é necessário, entre outras medidas, configurar uma `SECRET_KEY` segura fora do código, desativar `DEBUG`, definir `ALLOWED_HOSTS` adequadamente e revisar as configurações de segurança do Django.

O banco SQLite de demonstração contém somente dados fictícios. Não utilize dados pessoais ou clínicos reais nesse banco.