# Sistema de Gerenciamento de Agendamento Médico

Aplicação em desenvolvimento para apoiar o gerenciamento de uma clínica médica, como parte do Trabalho Prático da disciplina **GAC116 — Programação Web**. O projeto utiliza Python e Django e organiza os dados em três aplicativos: `usuarios`, `agenda` e `atendimento`.

## Visão geral

O domínio do sistema envolve quatro perfis de usuário:

- **Paciente:** pessoa atendida pela clínica.
- **Médico:** profissional associado a uma especialidade e a uma agenda.
- **Funcionário administrativo:** pessoa que apoia a operação da clínica.
- **Administrador do sistema:** perfil administrativo com responsabilidade geral sobre o sistema.

O objetivo do projeto é estruturar os dados e os processos relacionados a usuários, agendas médicas, consultas e registros de atendimento. A implementação atual está em uma etapa inicial: os modelos de domínio e suas configurações no Django Admin estão presentes, mas a interface própria para os usuários finais e os fluxos completos de negócio ainda não foram implementados.

## Aplicativos Django

| Aplicativo | Responsabilidade atual |
|---|---|
| [`usuarios`](docs/usuarios.md) | Usuário personalizado, dados pessoais e perfis de paciente, médico, funcionário e administrador. |
| [`agenda`](docs/agenda.md) | Especialidades, agendas médicas, disponibilidades recorrentes e bloqueios de agenda. |
| [`atendimento`](docs/atendimento.md) | Consultas, prontuários, exames e receitas. |


## Tecnologias

- Python
- Django 5.2.17
- Django Jazzmin 3.0.5, para personalização visual do Django Admin
- SQLite, banco de dados configurado atualmente
- HTML, CSS e JavaScript (estrutura de diretórios preparada; interface própria ainda não implementada)
- Git e GitHub

As dependências Python estão listadas em [`requirements.txt`](requirements.txt).

## Estrutura do projeto

```text
Trabalho_Prog_Web/
├── config/                 # Configurações gerais do Django
├── usuarios/               # Usuários e perfis
├── agenda/                 # Especialidades e organização das agendas
├── atendimento/            # Consultas e registros clínicos
├── docs/                   # Documentação do projeto
├── scripts/
│   └── iniciar.sh          # Preparação do ambiente e inicialização local
├── static/                 # Arquivos estáticos
├── templates/              # Templates compartilhados
├── manage.py
└── requirements.txt
```

## Como executar localmente

### Pré-requisitos

- Python 3.10 ou superior (recomendado para este projeto).
- `venv` disponível na instalação do Python.
- Acesso à internet na primeira instalação das dependências.

### Inicialização rápida — Linux/macOS

Na raiz do projeto, execute:

```bash
chmod +x scripts/iniciar.sh
./scripts/iniciar.sh
```

O script cria o ambiente virtual `.venv` caso ainda não exista, instala as dependências, aplica as migrações, executa `manage.py check` e inicia o servidor em `http://127.0.0.1:8000/`.

### Inicialização manual

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Para acessar o ambiente administrativo, abra `http://127.0.0.1:8000/admin/`.

Na primeira execução, crie um usuário administrador em outro terminal, com o ambiente virtual ativado:

```bash
python manage.py createsuperuser
```

O banco configurado atualmente é SQLite. O arquivo `db.sqlite3` é criado na raiz do projeto quando as migrações são aplicadas; não é necessário compartilhar um banco de dados preenchido para iniciar a aplicação.

## Funcionalidades presentes no código

- Modelo de usuário personalizado baseado em `AbstractUser`.
- Tipos de usuário para paciente, médico, funcionário administrativo e administrador do sistema.
- Perfis relacionados individualmente ao usuário.
- Cadastro transacional de usuário com perfil por meio do serviço `criar_usuario_com_perfil`.
- Cadastro de especialidades e associação de médicos a especialidades.
- Uma agenda por médico e disponibilidades recorrentes por dia da semana.
- Bloqueios de agenda com tipo e status.
- Modelo de consulta com estados definidos e restrição para impedir dois registros do mesmo médico no mesmo horário.
- Prontuário associado individualmente a uma consulta, com exames e receitas.
- Configuração do Django Jazzmin e telas de administração dos modelos.
- Testes automatizados nos três aplicativos.

## O que ainda está em desenvolvimento

Na versão analisada, as rotas do projeto apontam somente para o Django Admin. Os arquivos `views.py` dos aplicativos ainda contêm estruturas iniciais, e não há `urls.py` próprios para os aplicativos. Portanto, ainda não estão disponíveis uma interface de agendamento para pacientes, dashboards por perfil, nem fluxos completos de autenticação e autorização fora do Admin.

Também não se deve interpretar a existência de um campo `tipo_usuario` como implementação completa de permissões por perfil. As regras de autorização e os fluxos de negócio precisam ser implementados e testados nas próximas etapas.

Para executar os testes automatizados:

```bash
python manage.py test
```

## Integrantes

| Integrante | GitHub |
|---|---|
| Luís Kennedy Gervásio Turola | @Kenny-0h |
| Milena de Lourdes Barbosa| @MilenaBarbosa23 |

## Disciplina

**GAC116 — Programação Web**  
Trabalho Prático: Projeto de Implementação com Django.

## Documentação por aplicativo

- [Aplicativo `usuarios`](docs/usuarios.md)
- [Aplicativo `agenda`](docs/agenda.md)
- [Aplicativo `atendimento`](docs/atendimento.md)