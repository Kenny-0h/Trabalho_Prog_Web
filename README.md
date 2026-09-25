# 🏥 Sistema de Gerenciamento de Agendamento Médico

Sistema web para gerenciamento de consultas médicas, desenvolvido como Trabalho Prático da disciplina **GAC116 — Programação Web**, utilizando o framework Django.

> **Status:** 🚧 Em desenvolvimento

---

## 📋 Sobre o projeto

O projeto consiste no desenvolvimento de uma aplicação web para gerenciamento de uma clínica médica, contemplando o cadastro e gerenciamento de pacientes, médicos, funcionários administrativos, especialidades, agendas, consultas e informações relacionadas aos atendimentos.

A aplicação foi projetada para possuir diferentes níveis de acesso de acordo com o perfil do usuário, permitindo que cada papel tenha acesso somente às funcionalidades correspondentes às suas responsabilidades.

O sistema será desenvolvido utilizando a arquitetura **MVT (Model-View-Template)** do Django e um banco de dados relacional.

O projeto também busca aplicar os principais conceitos abordados na disciplina, incluindo:

* desenvolvimento web com Django;
* autenticação de usuários;
* controle de acesso e permissões;
* persistência de dados;
* modelagem de banco de dados;
* desenvolvimento de interfaces web;
* utilização de Git e GitHub;
* organização e desenvolvimento colaborativo.

O trabalho exige, entre outros requisitos, autenticação, operações CRUD, diferentes perfis de usuários, área administrativa protegida, área destinada aos usuários finais e uma interface responsiva com tema claro e escuro.

---

## 🎯 Objetivos

### Objetivo acadêmico

Aplicar os conhecimentos adquiridos na disciplina de Programação Web no desenvolvimento de uma aplicação Django completa, organizada e funcional.

### Objetivo do sistema

Disponibilizar uma plataforma para gerenciamento dos processos básicos de uma clínica médica, permitindo:

* gerenciamento de usuários;
* gerenciamento de médicos;
* gerenciamento de pacientes;
* gerenciamento de especialidades;
* gerenciamento das agendas médicas;
* gerenciamento de disponibilidades;
* agendamento de consultas;
* cancelamento de consultas;
* confirmação e acompanhamento de consultas;
* registro de prontuários;
* registro de exames;
* registro de receitas;
* gerenciamento de bloqueios de horários;
* visualização de informações através de dashboards.

---

## 👥 Perfis de usuário

O sistema possui quatro perfis principais:

| Perfil                         | Descrição                                                                                                        |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Paciente**                   | Usuário que realiza e acompanha seus próprios agendamentos e acessa informações permitidas de seus atendimentos. |
| **Médico**                     | Profissional responsável pelos atendimentos e pelos registros relacionados às consultas que realiza.             |
| **Funcionário Administrativo** | Responsável pela administração operacional da clínica.                                                           |
| **Administrador do Sistema**   | Usuário com nível administrativo superior e acesso geral ao sistema.                                             |

Cada usuário possui **um único perfil** dentro do sistema.

A estrutura de usuários segue o conceito de uma entidade base `Usuário`, especializada de acordo com o papel desempenhado no sistema.

---

## 🩺 Principais funcionalidades

### Autenticação

* Cadastro de pacientes;
* Login;
* Logout;
* Autenticação por usuário e senha;
* Controle de acesso por perfil;
* Proteção das áreas autenticadas.

### Usuários

* Cadastro de pacientes;
* Cadastro de médicos;
* Gerenciamento de funcionários administrativos;
* Gerenciamento de administradores do sistema;
* Controle de permissões.

### Médicos

* Cadastro de informações profissionais;
* Associação com uma especialidade;
* Agenda própria;
* Definição de disponibilidade;
* Visualização de consultas;
* Confirmação de consultas;
* Registro de prontuários.

### Agendamento

O fluxo principal de agendamento será:

```text
Paciente
   ↓
Escolhe especialidade
   ↓
Escolhe médico
   ↓
Escolhe data/horário disponível
   ↓
Confirma agendamento
   ↓
Consulta registrada
```

O sistema deverá impedir que dois pacientes ocupem o mesmo horário de um mesmo médico.

Não haverá operação de remarcação. Para alterar um agendamento, a consulta existente deverá ser cancelada e uma nova consulta deverá ser criada.

### Consultas

As consultas possuirão os seguintes estados:

```text
AGENDADA
CONFIRMADA
COMPLETA
CANCELADA
NAO_COMPARECEU
```

O ciclo de vida principal será:

```text
AGENDADA
   ├──→ CONFIRMADA ───→ COMPLETA
   │          ├───────→ CANCELADA
   │          └───────→ NAO_COMPARECEU
   │
   └──→ CANCELADA
```

### Prontuários

Cada consulta poderá possuir um prontuário associado.

O prontuário poderá conter:

* diagnóstico;
* observações;
* exames;
* receitas.

O acesso às informações será controlado de acordo com o perfil do usuário.

### Dashboards

Serão disponibilizados dashboards específicos para os diferentes perfis, apresentando informações relevantes de acordo com suas responsabilidades no sistema.

---

## 🏗️ Arquitetura

O projeto será organizado em aplicativos Django separados por **responsabilidade de domínio**, e não por perfil de usuário.

```text
projeto/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── usuarios/
│
├── agenda/
│
├── atendimento/
│
├── templates/
│
├── static/
│
└── manage.py
```

### `usuarios`

Responsável por:

* usuário base;
* autenticação;
* perfis;
* dados pessoais;
* controle relacionado à identidade dos usuários.

### `agenda`

Responsável por:

* especialidades;
* agendas;
* disponibilidades;
* bloqueios;
* consultas;
* geração de horários;
* regras de agendamento;
* cancelamentos;
* confirmações.

### `atendimento`

Responsável por:

* prontuários;
* exames;
* receitas.

A divisão em três aplicativos mantém as responsabilidades separadas sem criar um aplicativo independente para cada perfil de usuário.

---

## 🗄️ Modelo conceitual

A estrutura principal do sistema pode ser representada da seguinte maneira:

```text
                         ┌──────────────┐
                         │    Usuário   │
                         └──────┬───────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
         Paciente            Médico        Funcionário /
                                             Administrador
                                │
                                ▼
                         Especialidade
                                │
                                ▼
                             Agenda
                                │
                                ▼
                        Disponibilidade


Paciente ───────────────┐
                        │
                        ▼
                     Consulta ◄──────── Médico
                        │
                        ▼
                    Prontuário
                     /       \
                    ▼         ▼
                 Exame      Receita
```

Algumas decisões importantes de modelagem:

* CPF é único, mas não é a chave primária;
* `Usuário` é a entidade base;
* cada usuário possui apenas um perfil;
* cada médico possui uma especialidade;
* uma consulta não armazena diretamente sua especialidade;
* a especialidade é obtida através do médico;
* o prontuário pertence a uma consulta;
* o prontuário não duplica os relacionamentos com paciente e médico;
* as disponibilidades são recorrentes;
* a duração dos horários é determinada pela especialidade.

---

## 🛠️ Tecnologias

As tecnologias previstas para o projeto são:

* **Python**
* **Django**
* **PostgreSQL**
* **HTML5**
* **CSS3**
* **JavaScript**
* **Framework CSS** — a definir
* **Django Admin**
* **Git**
* **GitHub**

O trabalho exige a utilização do Django e de um banco de dados relacional, além de pelo menos dois aplicativos Django no projeto.

A interface deverá utilizar um framework CSS, ser responsiva e possuir tema claro e escuro.

---

## ⚙️ Instalação

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

### 2. Criar um ambiente virtual

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Criar o arquivo `.env` conforme o modelo disponibilizado no projeto.

> A estrutura definitiva das variáveis de ambiente será definida durante a configuração do projeto.

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Criar um superusuário

```bash
python manage.py createsuperuser
```

### 7. Executar o servidor

```bash
python manage.py runserver
```

A aplicação poderá então ser acessada localmente através do endereço informado pelo Django no terminal.

---

## 🧪 Testes

Os testes automatizados serão adicionados progressivamente durante o desenvolvimento.

A intenção é testar principalmente:

* regras de agendamento;
* disponibilidade de horários;
* bloqueios;
* cancelamentos;
* permissões;
* transições de estado das consultas;
* acesso aos prontuários;
* regras específicas de cada perfil.

---

## 🌿 Estratégia de desenvolvimento com Git

O desenvolvimento será realizado de forma colaborativa utilizando Git e GitHub.

O repositório deverá possuir, no mínimo, as branches exigidas pelo trabalho:

```text
main
develop
feature/*
```

O fluxo adotado pelo projeto será:

```text
main
  ↑
develop
  ↑
feature/*
```

Novas funcionalidades serão desenvolvidas em branches derivadas de `develop`.

Exemplo:

```text
feature/autenticacao
feature/modelagem-usuarios
feature/agendamento-consultas
feature/prontuario
```

Também poderão ser utilizadas outras categorias quando necessário:

```text
bugfix/*
hotfix/*
refactor/*
```

As tarefas serão organizadas através de **Issues do GitHub**. Cada integrante deverá assumir as tarefas atribuídas ou disponíveis e desenvolver sua implementação em uma branch própria.

---

## 📌 Convenção de desenvolvimento

Antes de iniciar uma implementação:

1. Verificar a Issue correspondente;
2. Atualizar a branch `develop`;
3. Criar uma branch específica para a tarefa;
4. Implementar a funcionalidade;
5. Realizar os testes necessários;
6. Fazer commits relacionados à tarefa;
7. Abrir Pull Request para `develop`;
8. Revisar a implementação;
9. Realizar o merge após validação.

Exemplo:

```bash
git checkout develop
git pull origin develop

git checkout -b feature/nome-da-feature
```

---

## 📚 Documentação do projeto

Além deste README, o projeto possui documentos de referência utilizados durante o desenvolvimento.

### Documento de Estrutura e Modelagem

Define as entidades, relacionamentos, cardinalidades e principais regras de negócio do sistema.

Ele funciona como a **fonte de verdade da modelagem** do projeto.

### Documento de Arquitetura Django

Define como as responsabilidades serão distribuídas dentro do projeto Django, incluindo os aplicativos:

```text
usuarios
agenda
atendimento
```

A arquitetura foi definida para separar responsabilidades de domínio sem criar um aplicativo específico para cada perfil de usuário.

---

## 👨‍💻 Integrantes

| Integrante                 | GitHub     |
| -------------------------- | ---------- |
| **[Nome do integrante 1]** | [@usuario] |
| **[Nome do integrante 2]** | [@usuario] |

Todos os integrantes deverão constar como colaboradores do repositório e realizar pelo menos dois commits durante o desenvolvimento, conforme especificado no enunciado.

---

## 📅 Cronograma acadêmico

O projeto será desenvolvido considerando os checkpoints definidos na atividade.

### Checkpoint 1 — 05/11

Entre os itens avaliados estão:

* modelagem completa do banco de dados;
* ambiente administrativo configurado;
* sistema de templates do ambiente administrativo;
* filtros no ambiente administrativo;
* repositório organizado no GitHub;
* complexidade do projeto.

### Checkpoint 2 — 19/11

A aplicação deverá estar concluída, contemplando os requisitos definidos no enunciado, incluindo:

* login;
* logout;
* cadastro;
* banco de dados integrado ao ambiente administrativo;
* framework CSS;
* interface amigável;
* documentação;
* demais funcionalidades previstas no projeto.

---

## 🚧 Status atual

### Planejamento

* [x] Definição do domínio do sistema
* [x] Definição dos perfis de usuário
* [x] Definição das principais regras de negócio
* [x] Definição da modelagem conceitual
* [x] Definição da arquitetura Django
* [x] Definição inicial da estratégia de branches
* [ ] Criação do projeto Django
* [ ] Configuração do ambiente de desenvolvimento
* [ ] Configuração do banco de dados
* [ ] Implementação dos usuários
* [ ] Implementação das agendas
* [ ] Implementação das consultas
* [ ] Implementação dos atendimentos
* [ ] Implementação do Django Admin
* [ ] Implementação da interface
* [ ] Implementação dos dashboards
* [ ] Testes
* [ ] Revisão final
* [ ] Deploy/apresentação

---

## 📖 Referência

Projeto desenvolvido para a disciplina:

**GAC116 — Programação Web**

**Trabalho Prático: Projeto de Implementação com Django**

O trabalho possui valor total de 45 pontos e exige o desenvolvimento colaborativo utilizando Django, banco de dados relacional, Git e GitHub.

---

> **Nota:** Este README representa o estado inicial do projeto. Conforme decisões técnicas forem tomadas durante a implementação, as informações deverão ser atualizadas para permanecerem alinhadas à documentação de arquitetura e às decisões do grupo.
