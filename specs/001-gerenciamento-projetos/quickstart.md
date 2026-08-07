# Quickstart: Gerenciamento de Projetos

## Prerequisites

- Python disponível no ambiente do workspace
- Dependências do projeto instaladas a partir de `requirements.txt`
- Acesso ao banco PostgreSQL configurado no projeto

## Run Locally

1. Ative o ambiente Python usado pelo workspace.
2. Instale as dependências do projeto, se ainda não estiverem instaladas.
3. Rode as migrations existentes:
   ```bash
   python manage.py migrate
   ```
4. Crie um usuário para acessar as telas protegidas:
   ```bash
   python manage.py createsuperuser
   ```
5. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

## Manual Validation

1. Acesse a aplicação no navegador.
2. Faça login com o usuário criado.
3. Abra a listagem de projetos.
4. Cadastre um projeto com nome, link GitHub da organização/conta e um ou mais
   repositórios válidos.
5. Confirme que o projeto aparece na listagem e que os detalhes exibem a
   organização e os repositórios vinculados.
6. Edite o projeto, adicione um repositório novo e remova um repositório já
   vinculado.
7. Tente usar links inválidos ou de outra plataforma e confirme que a validação
   bloqueia o salvamento.

## Expected Outcome

- O fluxo de CRUD funciona com autenticação.
- Os links GitHub são validados antes da gravação.
- A interface continua baseada nas templates Django do app `commex`.
- A base PostgreSQL atual e a configuração de static files permanecem intactas.