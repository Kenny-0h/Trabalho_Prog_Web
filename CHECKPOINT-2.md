---

### 3. Checklist Atualizado (`CHECKPOINT-2.md`)

Substitua o conteúdo de `CHECKPOINT-2.md` para registar todas as tarefas concluídas:

**Ficheiro:** `CHECKPOINT-2.md` *(Substituir conteúdo completo)*
```markdown
# Checkpoint 2 --- AgendaMedica

> **Prazo:** 19/11/2026\
> **Objetivo:** implementar autenticação e cadastro, consolidar a
> integração com o Django Admin e melhorar a interface do sistema.

## 1. Autenticação

-   [X] Implementar página de login.
-   [X] Implementar logout.
-   [X] Implementar cadastro público de pacientes.
-   [X] Validar os dados dos formulários e apresentar mensagens claras
    de erro e sucesso.
-   [X] Proteger páginas que exigem autenticação.
-   [X] Redirecionar o usuário após o login de acordo com seu perfil.
-   [X] Garantir que o usuário consiga encerrar a sessão corretamente.

## 2. Usuários, perfis e permissões

-   [X] Manter os tipos de usuário definidos no planejamento: Médico,
    Paciente, Administrador do Sistema e Administrador (funcionário da
    clínica).
-   [X] Permitir que qualquer visitante faça cadastro somente como
    paciente.
-   [X] Restringir a criação de médicos e administradores aos perfis
    autorizados.
-   [X] Aplicar as permissões de cada perfil às páginas e operações
    correspondentes.
-   [X] Restringir a edição de dados de usuários conforme as regras de
    negócio.
-   [X] Verificar que usuários não consigam acessar operações de outros
    perfis apenas alterando URLs.

## 3. Django Admin

-   [X] Consolidar a integração dos modelos com o Django Admin.
-   [X] Adotar uma personalização visual do painel administrativo
    (decisão: **Jazzmin**, sujeita à compatibilidade com a versão do
    projeto).
-   [X] Registrar os modelos relevantes no painel.
-   [X] Configurar colunas úteis (`list_display`).
-   [X] Configurar filtros (`list_filter`).
-   [X] Configurar pesquisa (`search_fields`).
-   [X] Configurar ordenação quando pertinente.
-   [X] Restringir ações e acesso aos modelos de acordo com as
    permissões.
-   [X] Verificar que o painel administrativo não fique acessível a
    usuários sem autorização.

## 4. Interface e experiência do usuário

-   [X] Utilizar **Bootstrap 5.3** como framework CSS.
-   [X] Criar um template-base compartilhado pelas páginas.
-   [X] Implementar navegação coerente com o perfil autenticado.
-   [X] Tornar as páginas responsivas para desktop, tablet e celular.
-   [X] Padronizar formulários, tabelas, botões, alertas e mensagens.
-   [X] Implementar tema claro e tema escuro.
-   [X] Permitir alternar entre os temas pela interface.
-   [X] Persistir a preferência de tema no navegador.
-   [X] Definir o tema claro como padrão quando ainda não houver
    preferência salva.
-   [X] Estruturar os temas para permitir adicionar outros futuramente
    sem reescrever a lógica de alternância.

### Diretriz técnica para os temas

-   Usar o atributo `data-bs-theme` do Bootstrap 5.3 como base para
    alternar entre temas.
-   Manter a lógica de seleção e persistência em um arquivo JavaScript
    próprio, por exemplo `static/js/theme.js`.
-   Organizar estilos específicos em arquivos separados, por exemplo:
  -   `static/css/themes/light.css`
  -   `static/css/themes/dark.css`
  -   `static/css/themes/custom.css` (para futuras personalizações, se
        necessário)
-   Usar variáveis CSS para cores e demais propriedades que mudem entre
    temas.
-   Guardar a preferência selecionada no `localStorage`.

## 5. Documentação

-   [X] Criar ou atualizar o `README.md`.
-   [X] Informar o nome do projeto.
-   [X] Informar os integrantes da equipe.
-   [X] Descrever brevemente o sistema.
-   [X] Listar as tecnologias utilizadas.
-   [X] Documentar os requisitos e as instruções de instalação.
-   [X] Documentar como executar o projeto localmente.
-   [X] Descrever as funcionalidades implementadas.
-   [X] Apresentar a estrutura de diretórios e aplicações do projeto.
-   [X] Registrar decisões relevantes e limitações conhecidas.

## 6. Testes e validação

-   [X] Testar login com credenciais válidas e inválidas.
-   [X] Testar logout.
-   [X] Testar cadastro de paciente e validação dos campos.
-   [X] Testar acesso anônimo a páginas protegidas.
-   [X] Testar permissões de cada tipo de usuário.
-   [X] Testar criação e gerenciamento de usuários pelo painel
    administrativo.
-   [X] Testar filtros e pesquisas do Django Admin.
-   [X] Testar a interface em diferentes larguras de tela.
-   [X] Testar alternância entre tema claro e escuro.
-   [X] Verificar se a preferência de tema permanece após atualizar ou
    reabrir a página.
-   [X] Executar as migrações em um ambiente limpo e verificar a
    configuração do banco.
-   [X] Conferir se o projeto pode ser instalado e executado seguindo
    somente o README.

------------------------------------------------------------------------

## Decisões registradas

| Assunto | Decisão |
|---|---|
| Framework CSS | Bootstrap 5.3 |
| Temas | Claro e escuro, com estrutura extensível |
| Tema padrão | Claro |
| Persistência da preferência | `localStorage` |
| Alternância de tema | `data-bs-theme` e JavaScript próprio |
| Painel administrativo | Django Admin personalizado com Jazzmin |
| Cadastro público | Somente para pacientes |
| Criação de médicos e administradores | Restrita aos perfis autorizados |
| Organização do trabalho | Checklist em Markdown, sem abertura de issues no GitHub |
| Fluxo de desenvolvimento | Manter a forma de trabalho já adotada pela equipe; revisar os arquivos existentes antes de propor alterações |

## Registro de andamento

| Data | Registro |
|---|---|
| 16/11/2026 | Checklist inicial e decisões de implementação consolidadas com a equipe. |
| 18/11/2026 | Implementação concluída: redirecionamento e proteção por perfil, permissões no Django Admin/Jazzmin, arquitetura extensível de temas (`light.css`, `dark.css`, `custom.css`), testes automatizados de views e atualização do `README.md`. |