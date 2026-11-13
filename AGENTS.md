# AGENTS.md

Guia para agentes de IA (Claude Code, Copilot, etc.) que trabalham neste repositório.
Idioma do projeto: **português do Brasil** (código de domínio, mensagens, commits e documentação).

## Visão geral

Sistema web em Django para gestão de projetos, equipes, sprints e análise de commits do GitHub
(NAES 2026). Interface server-side com Bootstrap 5 e jQuery.

- Django 5.2, Python 3.12 (runtime do App Engine).
- Banco: PostgreSQL no Neon via variável `DATABASE_URL`; sem ela, usa SQLite local (`db_local.sqlite3`).
- Apps instalados: `commex` (domínio), `ia` (única porta de entrada para a IA: `ia.servico.chamar_ia`, auditoria,
  cota mensal, telas) e `assistente` (chat que usa `chamar_ia`; contexto em `contexto_projeto.md`).
  O app `website` existe, mas não está em `INSTALLED_APPS`.
- Pacotes: `django-braces`, `django-crispy-forms` + `crispy-bootstrap5`, `django-filter`,
  `django-debug-toolbar`, `django-autocomplete-light`, `gunicorn`, `psycopg2-binary`.
- Front-end: Bootstrap 5.3 (CDN), jQuery 3.7, DataTables, jQuery Mask. Layout base em
  `commex/templates/commex/base.html`.

## Comandos

```bash
pip install -r requirements.txt
python manage.py runserver
python manage.py makemigrations commex
python manage.py migrate
python manage.py test
python manage.py collectstatic --noinput   # gera static_gcloud/ para o App Engine
gcloud app deploy                          # deploy (ver skill deploy-app-engine)
```

## Cuidados importantes

- **O banco remoto é o Neon** (só com `DATABASE_URL` definida). Com ela, `migrate` e qualquer escrita afetam dados
  reais. Nunca rode comandos destrutivos (`flush`, `migrate zero`, deletes em massa) sem confirmar
  com o usuário.
- **`commex/migrations/` está no `.gitignore`**, mas `0001_initial.py` é versionada. Uma nova migração
  só entra no commit com `git add -f commex/migrations/<arquivo>.py`.
- Segredos (`SECRET_KEY`, `DATABASE_URL`, `IA_API_KEY`) vêm de variáveis de ambiente; em produção, de
  `env_variables.yaml` (ignorado pelo git; modelo em `env_variables.yaml.example`). Nunca os coloque em
  código, logs, commits ou respostas. `DEBUG` é `1` por padrão localmente e `0` no `app.yaml`.
- **Autoria**: `Projeto`, `Equipe` e `Sprint` têm `cadastrado_por`. Toda view filtra por `request.user`
  (404 para registros de outros); ao criar, atribua o dono. Use `DonoQuerysetMixin` em CBVs.
- **Listas**: filtros com django-filter (`commex/filters.py`) e paginação com `{% url_params page=... %}`
  (`commex/templatetags/paginacao_tags.py`) via `commex/includes/paginacao.html`.
- **IA**: nunca chame provedores direto; use sempre `ia.servico.chamar_ia`.
- Não edite `static_gcloud/` à mão: é saída do `collectstatic`. O CSS próprio fica em `static/css/`.
- Ignore `commex/urls copy.py` (resíduo) e não o importe.

## Convenções de código

- **Views**: class-based. Controle de acesso com `GroupRequiredMixin` (django-braces) e
  `group_required` para o grupo de acesso: `Coordenadores` escreve, `Professores` só consulta.
  Os nomes dos grupos vêm de `settings.GRUPO_COORDENADORES` e `settings.GRUPO_PROFESSORES`.
- **URLs** (`commex/urls.py`): caminho em português (`cadastrar/<entidade>/`, `atualizar/...`,
  `excluir/...`, `listar/...`, `detalhar/...`) e `name` no padrão `<entidade>-<acao>`
  (`projeto-create`, `equipe-update`, `sprint-list`...).
- **Templates**: `commex/templates/commex/<entidade>/` estendendo `commex/base.html`.
  Listas usam card + `table-responsive` + DataTables; formulários usam crispy ou `form.html`.
- **Mensagens**: use `django.contrib.messages` em toda criação, alteração e exclusão
  (`messages.success` / `messages.error`), em português e com acentos.
- **Queries**: toda lista/detalhe que acessa relação no template deve usar `select_related`
  (FK) ou `prefetch_related` (M2M / reverso). Verifique com o Debug Toolbar (skill otimizar-queries).
- **Models**: `cadastrado_em` (`auto_now_add`) e `atualizado_em` (`auto_now`); `Meta.ordering`;
  constraints de unicidade nomeadas.
- **Estilo**: siga o código vizinho (nomes, densidade de comentários, idioma). Não refatore código
  fora do escopo do pedido.

## Fluxo de trabalho

1. Leia o código relacionado antes de alterar; prefira editar arquivos existentes a criar novos.
2. Use as skills em `.claude/skills/` quando a tarefa se encaixar:
   - `commit-padrao`: mensagens de commit (obrigatória antes de qualquer commit).
   - `novo-crud-django`: nova entidade/tela no padrão do projeto.
   - `otimizar-queries`: achar e corrigir queries repetidas.
   - `deploy-app-engine`: checklist e comandos de deploy.
3. Após mudar models, gere a migração e confirme o `git add -f` dela.
4. Rode `python manage.py check` e `python manage.py test` antes de concluir.
5. Só faça commit ou push quando o usuário pedir.

## Specs

A pasta `specs/` e `.specify/` (Spec Kit) guarda as especificações por feature
(`001-gerenciamento-projetos` até `006-autenticacao-usuario`). Consulte o `spec.md` e o `plan.md`
da feature antes de alterar o comportamento dela, e respeite `.specify/memory/constitution.md`.
