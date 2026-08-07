# Implementation Plan: Gerenciamento de Projetos

**Branch**: `001-gerenciamento-de-projetos` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-gerenciamento-projetos/spec.md`

## Summary

Evoluir o app Django existente para suportar CRUD de Projetos com repositórios
GitHub vinculados, preservando o stack atual baseado em templates server-side,
crispy forms, PostgreSQL no Neon e a infraestrutura de static files para GCloud.
A implementação deve reutilizar o app `commex`, proteger as telas com autenticação
do Django e validar links do GitHub antes de persistir os vínculos.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.x, django-crispy-forms, crispy-bootstrap5,
psycopg2-binary, django-filter, django-braces, gunicorn; client HTTP leve para
validação GitHub se necessário

**Storage**: PostgreSQL no Neon, mantendo a conexão atual e a histórica de
migrations

**Testing**: Não obrigatório para este plano; validação manual via fluxo web e
checagem de páginas autenticadas

**Target Platform**: Aplicação web Django com HTML renderizado no servidor

**Performance Goals**: Cadastro e validação de link devem permanecer interativos
e responder em tempo curto o bastante para uso humano direto

**Constraints**: Manter compatibilidade com GCloud/static_gcloud, não introduzir
stack frontend conflitante, preservar os deps existentes e não alterar a base de
dados para fora de PostgreSQL/Neon

**Scale/Scope**: Uso acadêmico e institucional, com baixo volume de projetos e
repositórios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Python e Django permanecem como base da aplicação
- ✅ Templates server-side continuam sendo o mecanismo principal de UI
- ✅ GCloud/static_gcloud e PostgreSQL/Neon são preservados
- ✅ Bibliotecas existentes como crispy forms continuam em uso
- ✅ Autenticação será aplicada às telas de CRUD com o stack nativo do Django
- ✅ Testes automatizados não são mandatórios neste plano

## Access, Ownership, Pagination and Query Decisions

### View Access Matrix

| View | LoginRequiredMixin | GroupRequiredMixin | Decision |
|---|---|---|---|
| `ProjetoCreate` | Sim | Sim | Apenas Product Owner ou Desenvolvedor pode criar projeto, conforme a spec |
| `ProjetoUpdate` | Sim | Sim | Apenas Product Owner ou Desenvolvedor pode editar projeto |
| `ProjetoDelete` | Sim | Sim | Apenas Product Owner ou Desenvolvedor pode excluir projeto |
| `ProjetoList` | Sim | Sim | Listagem é parte da área protegida de gestão de projetos |
| `ProjetoDetail` | Sim | Sim | Detalhe mostra informações de gestão restritas à mesma área protegida |
| `IndexView` | Sim | Sim | Dashboard inicial da feature segue a mesma regra de acesso do cadastro |

### User Ownership / `User` ForeignKey

- Nenhum model desta feature possui `ForeignKey` para `User`.
- Portanto, não há `form_valid()` para preencher owner nem `get_queryset()` para isolar registros por usuário nesta feature.
- A regra de isolamento por usuário da constitution não se aplica aqui.

### ListView Pagination

- `ProjetoList`: `paginate_by = 20`, porque é uma listagem de gestão que pode crescer e já exibe tabela com ações.
- `IndexView`: `paginate_by = 5`, porque funciona como recorte curto da lista de projetos na página inicial.

### Templates que Consultam `request.user.is_authenticated`

- `commex/base.html` para alternar menu público/protegido.
- `commex/index.html` para mostrar atalhos de ação apenas quando o usuário estiver autenticado.
- `commex/list/projeto.html` para exibir ações de editar/excluir/nova entrada apenas para quem pode agir.
- `commex/detail/projeto.html` para exibir botões de editar/excluir apenas para usuário autenticado.
- `commex/form.html` e variações de formulário para esconder chamadas de ação que não se aplicam a usuário não autenticado.

### Querysets com Relações em Template

- `ProjetoList` deve usar `prefetch_related('repositorios')` porque o template exibe `projeto.repositorios.count` por linha.
- `ProjetoDetail` deve usar `prefetch_related('repositorios')` porque o template percorre `object.repositorios.all`.
- Se a implementação de edição exibir vínculos com sprints no contexto do mesmo queryset, também deve usar `prefetch_related('sprints')`.
- Não há `select_related` necessário para relações diretas nesta feature, porque o acesso relevante é em M2M.

## Project Structure

### Documentation (this feature)

```text
specs/001-gerenciamento-projetos/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code (repository root)

```text
manage.py
naes2026/
├── settings.py
├── urls.py
└── wsgi.py
commex/
├── models.py
├── forms.py
├── views.py
├── urls.py
└── templates/
    └── commex/
        ├── base.html
        ├── form.html
        ├── index.html
        ├── list/
        │   └── projeto.html
        └── detail/
            └── projeto.html
static/
static_gcloud/
```

**Structure Decision**: Manter uma única aplicação Django server-rendered, com a
feature implementada dentro de `commex` e sem separar backend/frontend. Não há
contratos de API externos nesta entrega porque a interface do recurso é composta
por páginas e formulários Django.

## Phase 0: Outline & Research

### Unknowns to resolve in `research.md`

1. Como validar links GitHub sem trocar o stack atual ou adicionar uma camada API
   separada.
2. Como encaixar autenticação nas views de CRUD sem quebrar as URLs atuais.
3. Como adaptar a modelagem atual, que hoje usa um relacionamento amplo, para o
   vínculo de projeto e repositório pedido pela spec.
4. Como preservar compatibilidade com Neon, migrations existentes e static files
   de GCloud.

### Research decisions to document

- Reutilizar o app `commex` e as class-based views já existentes.
- Aplicar `LoginRequiredMixin` ou proteção equivalente nas telas de criação,
  edição, exclusão e detalhe.
- Validar GitHub em uma camada de formulário/serviço pequena, mantendo a UI
  orientada a templates.
- Preservar a configuração atual de banco e arquivos estáticos sem introduzir
  um segundo framework.

**Output**: `research.md` com as decisões acima fechadas e sem marcadores de
esclarecimento.

## Phase 1: Design & Contracts

1. **`data-model.md`** — descrever a evolução dos dados atuais:
   - `Projeto`: nome, status, ano atual do cadastro já existente, link da
     organização/conta GitHub, timestamps e vínculo com repositórios
   - `Repositorio`: nome, link GitHub, atributos já existentes para exibição e
     relação de pertencimento ao projeto
   - Regras: unicidade de vínculo por projeto, validação de formato/existência do
     link GitHub e remoção individual de repositório sem excluir o projeto

2. **Contracts** — não aplicável nesta entrega.
   - O recurso é entregue como fluxo web com páginas Django, não como API pública.

3. **`quickstart.md`** — documentar como rodar e validar o fluxo manualmente:
   - preparar o ambiente Python atual
   - aplicar migrations
   - criar usuário autenticado
   - acessar listagem, cadastro, edição, detalhe e exclusão de projetos

4. Atualizar o contexto do agente somente se necessário para manter coerência com
   o stack atual. Neste workspace, o script automático não pôde ser executado
   porque depende de `pwsh`, então a atualização fica registrada como não
   aplicável.

## Complexity Tracking

| Violation/Risk | Justificativa | Alternative rejected |
|---|---|---|
| Validação externa do GitHub | A spec exige confirmar formato e existência real dos links | Apenas regex local, rejeitada por não provar existência |
| Mudança da relação Projeto/Repositório | O modelo atual não representa o vínculo 1:N pedido pela spec | Manter relacionamento genérico sem dono explícito, rejeitado por dificultar validação e manutenção |

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`

**STOP** — Este plan encerra na Fase 1. A Fase 2 (`tasks.md`) é gerada pelo
comando `/speckit.tasks`.