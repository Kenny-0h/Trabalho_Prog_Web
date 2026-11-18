# Checkpoint 2 --- AgendaMedica

> **Prazo:** 19/11/2026\
> **Objetivo:** implementar autenticação e cadastro, consolidar a
> integração com o Django Admin e melhorar a interface do sistema.

## 1. Autenticação

-   [X] Implementar página de login.
-   [X] Implementar logout.
-   [X] Implementar cadastro público de pacientes.
-   [ ] Validar os dados dos formulários e apresentar mensagens claras
    de erro e sucesso.
-   [ ] Proteger páginas que exigem autenticação.
-   [ ] Redirecionar o usuário após o login de acordo com seu perfil.
-   [ ] Garantir que o usuário consiga encerrar a sessão corretamente.

## 2. Usuários, perfis e permissões

-   [ ] Manter os tipos de usuário definidos no planejamento: Médico,
    Paciente, Administrador do Sistema e Administrador (funcionário da
    clínica).
-   [ ] Permitir que qualquer visitante faça cadastro somente como
    paciente.
-   [ ] Restringir a criação de médicos e administradores aos perfis
    autorizados.
-   [ ] Aplicar as permissões de cada perfil às páginas e operações
    correspondentes.
-   [ ] Restringir a edição de dados de usuários conforme as regras de
    negócio.
-   [ ] Verificar que usuários não consigam acessar operações de outros
    perfis apenas alterando URLs.

## 3. Django Admin

-   [ ] Consolidar a integração dos modelos com o Django Admin.
-   [ ] Adotar uma personalização visual do painel administrativo
    (decisão: **Jazzmin**, sujeita à compatibilidade com a versão do
    projeto).
-   [ ] Registrar os modelos relevantes no painel.
-   [ ] Configurar colunas úteis (`list_display`).
-   [ ] Configurar filtros (`list_filter`).
-   [ ] Configurar pesquisa (`search_fields`).
-   [ ] Configurar ordenação quando pertinente.
-   [ ] Restringir ações e acesso aos modelos de acordo com as
    permissões.
-   [ ] Verificar que o painel administrativo não fique acessível a
    usuários sem autorização.

## 4. Interface e experiência do usuário

-   [ ] Utilizar **Bootstrap 5.3** como framework CSS.
-   [ ] Criar um template-base compartilhado pelas páginas.
-   [ ] Implementar navegação coerente com o perfil autenticado.
-   [ ] Tornar as páginas responsivas para desktop, tablet e celular.
-   [ ] Padronizar formulários, tabelas, botões, alertas e mensagens.
-   [ ] Implementar tema claro e tema escuro.
-   [ ] Permitir alternar entre os temas pela interface.
-   [ ] Persistir a preferência de tema no navegador.
-   [ ] Definir o tema claro como padrão quando ainda não houver
    preferência salva.
-   [ ] Estruturar os temas para permitir adicionar outros futuramente
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

-   [ ] Criar ou atualizar o `README.md`.
-   [ ] Informar o nome do projeto.
-   [ ] Informar os integrantes da equipe.
-   [ ] Descrever brevemente o sistema.
-   [ ] Listar as tecnologias utilizadas.
-   [ ] Documentar os requisitos e as instruções de instalação.
-   [ ] Documentar como executar o projeto localmente.
-   [ ] Descrever as funcionalidades implementadas.
-   [ ] Apresentar a estrutura de diretórios e aplicações do projeto.
-   [ ] Registrar decisões relevantes e limitações conhecidas.

## 6. Testes e validação

-   [ ] Testar login com credenciais válidas e inválidas.
-   [ ] Testar logout.
-   [ ] Testar cadastro de paciente e validação dos campos.
-   [ ] Testar acesso anônimo a páginas protegidas.
-   [ ] Testar permissões de cada tipo de usuário.
-   [ ] Testar criação e gerenciamento de usuários pelo painel
    administrativo.
-   [ ] Testar filtros e pesquisas do Django Admin.
-   [ ] Testar a interface em diferentes larguras de tela.
-   [ ] Testar alternância entre tema claro e escuro.
-   [ ] Verificar se a preferência de tema permanece após atualizar ou
    reabrir a página.
-   [ ] Executar as migrações em um ambiente limpo e verificar a
    configuração do banco.
-   [ ] Conferir se o projeto pode ser instalado e executado seguindo
    somente o README.

------------------------------------------------------------------------

## Decisões registradas

  -----------------------------------------------------------------------
  Assunto                             Decisão
  ----------------------------------- -----------------------------------
  Framework CSS                       Bootstrap 5.3

  Temas                               Claro e escuro, com estrutura
                                      extensível

  Tema padrão                         Claro

  Persistência da preferência         `localStorage`

  Alternância de tema                 `data-bs-theme` e JavaScript
                                      próprio

  Painel administrativo               Django Admin personalizado com
                                      Jazzmin

  Cadastro público                    Somente para pacientes

  Criação de médicos e                Restrita aos perfis autorizados
  administradores                     

  Organização do trabalho             Checklist em Markdown, sem abertura
                                      de issues no GitHub

  Fluxo de desenvolvimento            Manter a forma de trabalho já
                                      adotada pela equipe; revisar os
                                      arquivos existentes antes de propor
                                      alterações
  -----------------------------------------------------------------------

## Forma de trabalho

1.  Antes de alterar código, revisar os arquivos e a estrutura atual do
    projeto.
2.  Fazer alterações compatíveis com a arquitetura e as decisões já
    adotadas pela equipe.
3.  Evitar mudanças arquiteturais sem conversar e obter concordância
    antes.
4.  Ao propor alterações, indicar os arquivos envolvidos e fornecer o
    conteúdo completo ou um patch claro.
5.  Explicar o que foi alterado e como testar.
6.  Atualizar este checklist conforme os itens forem concluídos ou as
    decisões forem revistas.

## Registro de andamento

Use esta seção para anotar decisões novas, impedimentos e mudanças
importantes durante o Checkpoint 2.

  -----------------------------------------------------------------------
  Data                                Registro
  ----------------------------------- -----------------------------------
  16/11/2026                          Checklist inicial e decisões de
                                      implementação consolidadas com a
                                      equipe.

  -----------------------------------------------------------------------
