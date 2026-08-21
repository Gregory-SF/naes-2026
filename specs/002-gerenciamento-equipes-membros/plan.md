# Implementation Plan: Gerenciamento de Equipes e Membros

**Branch**: `002-gerenciamento-equipes-membros` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-gerenciamento-equipes-membros/spec.md`

## Summary

Implementar o gerenciamento de equipes em fluxo único com composição de membros,
papéis e apelidos GitHub, reaproveitando as entidades existentes em `commex`.
O foco é garantir cardinalidade dos papéis e cadastro/reuso de alunos no contexto
da equipe, sem criar tela isolada de aluno.

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: Django 5.x, crispy forms, bootstrap5

**Storage**: PostgreSQL (Neon)

**Testing**: Não obrigatório por padrão; validação manual por fluxos de UI

**Target Platform**: Aplicação web Django server-rendered

**Performance Goals**: Busca por aluno e apelido com resposta interativa para
uso em formulário

**Constraints**: Preservar stack atual, autenticação Django e URLs existentes;
não quebrar fluxo atual de equipe/projeto

**Scale/Scope**: Ambiente acadêmico com volume moderado de equipes e membros

## Constitution Check

- ✅ Python/Django mantidos
- ✅ Templates server-rendered mantidos
- ✅ PostgreSQL/Neon mantido
- ✅ Bibliotecas atuais preservadas
- ✅ Autenticação nativa mantida
- ✅ Testes automatizados não mandatórios

## Project Structure

### Documentation (this feature)

```text
specs/002-gerenciamento-equipes-membros/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code (repository root)

```text
commex/
├── models.py
├── forms.py
├── views.py
├── urls.py
└── templates/commex/
    ├── form.html
    ├── list/equipe.html
    └── detail/equipe.html
```

**Structure Decision**: Implementação concentrada no app `commex`, sem criar app
novo e sem API pública adicional.

## Phase 0: Outline & Research

1. Definir fluxo único de cadastro de equipe com criação e seleção de aluno
2. Definir estratégia de unicidade global de apelido GitHub
3. Definir regras transacionais para troca de Scrum Master/Product Owner

**Output**: `research.md` com decisões fechadas

## Phase 1: Design & Contracts

1. `data-model.md` com entidades Aluno, ApelidoGithub, Equipe, MembroEquipe
2. Contracts não aplicável (fluxo interno web)
3. `quickstart.md` com validação manual fim a fim

## Complexity Tracking

| Violation/Risk | Justificativa | Alternative rejected |
|---|---|---|
| Cardinalidade rígida de papéis | Regra de negócio central da spec | Aceitar composição flexível, rejeitado por violar RFs |

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`
# Implementation Plan: Gerenciamento de Equipes e Membros

**Branch**: `002-gerenciamento-equipes-membros` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-gerenciamento-equipes-membros/spec.md`

## Summary

Evoluir o app Django atual para permitir cadastro de equipes em um único fluxo,
com alunos criados implicitamente, apelidos GitHub únicos e composição por
papéis. A feature deve reaproveitar a aplicação `commex`, manter a experiência
server-rendered e preservar compatibilidade com as demais áreas do sistema.

**Revisão 2026-08-10 — Novo padrão de UI para membros**: A abordagem de
formulário de membros foi revisada para eliminar o formset genérico com dropdown
de papel (`MembroEquipeFormSet`). O novo design usa campos de texto livre
dedicados por papel, visíveis imediatamente na abertura do formulário, seguindo
o padrão de coleção de cards repetíveis já adotado no formulário de repositórios
do projeto (`RepositorioCardCollection` em `commex/forms.py`). Campos de Scrum
Master e Product Owner são fixos (1 campo cada, sempre visíveis); campos de
Desenvolvedor são repetíveis via botão "+", com o botão de remover ocultado
quando restar apenas um campo de Desenvolvedor.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django 5.2.x, django-crispy-forms, crispy-bootstrap5,
django-braces, django-filter, psycopg2-binary, gunicorn; suporte leve a busca/autocomplete se necessário

**Storage**: PostgreSQL no Neon, preservando migrações existentes e o histórico de dados

**Testing**: Não obrigatório neste plano; validação manual do fluxo de equipe e composição

**Target Platform**: Aplicação web Django com HTML renderizado no servidor

**Performance Goals**: Formulário de busca por aluno/apelido responsivo o bastante para uso interativo do cadastro de equipe

**Constraints**: Manter compatibilidade com GCloud/static_gcloud, não introduzir
frontend conflitado, preservar as bibliotecas já presentes e não quebrar os
vínculos atuais de equipes/analises. O controle dinâmico de campos de
Desenvolvedor é feito com jQuery (já presente no projeto via Bootstrap 5 bundle),
sem adicionar dependência nova. Os campos usam `name` com padrão
`membros_sm_nome`, `membros_po_nome`, `membros_dev_<index>_nome` e
`membros_total_devs`, lidos manualmente na view — sem management form do Django
formset — conforme o padrão adotado em `RepositorioCardCollection`.

**Scale/Scope**: Uso acadêmico e institucional, com volume baixo a moderado de equipes e membros

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Python e Django permanecem como base da aplicação
- ✅ Templates server-side continuam sendo o mecanismo principal de UI
- ✅ GCloud/static_gcloud e PostgreSQL/Neon são preservados
- ✅ Bibliotecas existentes como crispy forms continuam em uso
- ✅ Autenticação será aplicada ao fluxo de CRUD das equipes
- ✅ Testes automatizados não são mandatórios neste plano

## Access, Ownership, Pagination and Query Decisions

### View Access Matrix

| View | LoginRequiredMixin | GroupRequiredMixin | Decision |
|---|---|---|---|
| `EquipeCreate` | Sim | Não | A feature é para usuário autorizado autenticado; não há restrição por grupo na spec |
| `EquipeUpdate` | Sim | Não | Atualização de equipe é permitida ao usuário autenticado da área |
| `EquipeDelete` | Sim | Não | Exclusão segue a mesma regra de acesso autenticado |
| `EquipeList` | Sim | Não | Consulta de equipes não exige grupo específico |
| `EquipeDetail` | Sim | Não | Detalhe é parte da área autenticada de equipes |

### User Ownership / `User` ForeignKey

- Nenhum model desta feature possui `ForeignKey` para `User`.
- Não há necessidade de `form_valid()` preenchendo owner nem de `get_queryset()` restringindo por usuário autenticado.
- A regra de isolamento por usuário da constitution não se aplica neste escopo.

### ListView Pagination

- `EquipeList` implementa `paginate_by = 20`.
- Justificativa: a listagem mostra cartões/tabela de composição de equipes e pode crescer com o uso acadêmico; não é um singleton nem um conjunto finito pequeno.

### Templates que Consultam `request.user.is_authenticated`

- `commex/base.html` para alternar entre entradas públicas e ações de equipe.
- `commex/list/equipe.html` para mostrar/ocultar botões de criar, editar e excluir.
- `commex/detail/equipe.html` para mostrar botões de ação apenas quando o usuário está autenticado.
- Templates de formulário de equipe em `commex/form.html` e variações específicas para evitar exibição de ações indevidas a usuários anônimos.

### Querysets com Relações em Template

- `EquipeList` deve usar `select_related('projeto')` porque o template exibe `equipe.projeto.nome`.
- `EquipeList` deve usar `prefetch_related('alunos')` ou a relação equivalente disponível para evitar contagens e acessos repetidos ao aluno por equipe.
- `EquipeDetail` deve usar `select_related('projeto')` porque o template mostra o projeto relacionado.
- `EquipeDetail` deve usar `prefetch_related('membros__aluno')` e, se necessário, `prefetch_related('membros')` porque o template percorre membros e acessa `membro.aluno.nome`.
- Não há `GroupRequiredMixin` nesta feature porque a spec define usuário autorizado, sem regra de grupo.

## Project Structure

### Documentation (this feature)

```text
specs/002-gerenciamento-equipes-membros/
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
        ├── detail/
        └── list/
static/
static_gcloud/
```

**Structure Decision**: Reutilizar a aplicação `commex` existente e adaptar o fluxo de equipes para um formulário único com membros, sem criar um novo app.

## Phase 0: Outline & Research

### Unknowns to resolve in `research.md`

1. Melhor forma de montar o formulário único de equipe com membros, papéis e apelidos no stack atual.
2. Estratégia para busca por nome/apelido sem romper a experiência server-rendered.
3. Regras de transação para manter Scrum Master, Product Owner e Desenvolvedor sempre válidos.
4. Forma de preservar a exclusão da equipe sem apagar alunos/apelidos reutilizáveis.

### Research decisions to document

- Reaproveitar `commex` com views e forms dedicados ao fluxo de equipe.
- **[REVISADO]** Substituir formset genérico por coleção manual de campos
   nomeados por papel, lida na view sem management form, seguindo o padrão
   `RepositorioCardCollection`. Ver Decisão 4 em `research.md`.
- Campos SM e PO: fixos, um por papel, sem botão de adicionar.
- Campos DEV: repetíveis via botão "+"; remoção do último campo bloqueada no
   cliente por JavaScript.
- Resolução de aluno: busca por nome exato (case-insensitive); se não encontrar,
   cria implicitamente. Se houver mais de um resultado, retornar erro de
   ambiguidade com instrução ao usuário.
- Manter a unicidade de apelidos no banco para suportar busca e reuso.
- Preservar alunos e apelidos quando a equipe for excluída.

**Output**: `research.md` com as decisões acima fechadas e sem marcadores de esclarecimento.

## Phase 1: Design & Contracts

1. **`data-model.md`** — descrever as entidades e vínculos:
   - `Aluno`: nome e identificação interna
   - `ApelidoGithub`: nickname único associado a um aluno
   - `Equipe`: nome único e composição
   - `MembroEquipe`: aluno, equipe e papel
   - `Papel`: SCRUM_MASTER, PRODUCT_OWNER, DESENVOLVEDOR

2. **Contracts** — não aplicável nesta entrega.
   - O recurso é entregue como fluxo web com páginas Django, não como API pública.

3. **`quickstart.md`** — documentar validação manual:
   - criar equipe com composição válida
   - reutilizar aluno por nome/apelido
   - bloquear apelido duplicado
   - editar e excluir equipe mantendo alunos/apelidos

4. Atualizar o contexto do agente somente se necessário para manter coerência com
   o stack atual.

1. **`data-model.md`** — descrever as entidades e vínculos:
   - `Aluno`: nome e identificação interna
   - `ApelidoGithub`: nickname único associado a um aluno
   - `Equipe`: nome único e composição
   - `MembroEquipe`: aluno, equipe e papel
   - `Papel`: SCRUM_MASTER, PRODUCT_OWNER, DESENVOLVEDOR
   - **[NOVO]** Anotar no data-model a estratégia de resolução de aluno por nome
     no momento do save: busca case-insensitive, criação implícita se inexistente,
     erro de ambiguidade se múltiplos resultados.

2. **Contracts** — não aplicável nesta entrega.
   - O recurso é entregue como fluxo web com páginas Django, não como API pública.

3. **`quickstart.md`** — documentar validação manual:
   - abrir formulário de nova equipe e confirmar que SM, PO e um campo DEV já
     aparecem sem nenhuma ação prévia
   - adicionar segundo Desenvolvedor via botão "+"
   - tentar remover o único campo de Desenvolvedor e confirmar que é bloqueado
   - criar equipe com composição válida usando nomes de alunos novos
   - criar equipe reutilizando aluno existente pelo nome
   - bloquear apelido duplicado
   - editar equipe — confirmar que formulário carrega pré-preenchido
   - excluir equipe mantendo alunos/apelidos

4. Atualizar o contexto do agente somente se necessário para manter coerência com
   o stack atual.

## Complexity Tracking

| Violation/Risk | Justificativa | Alternative rejected |
|---|---|---|
| Formulário único com membros dinâmicos | A spec exige criação em um único fluxo, com alunos novos e existentes | Tela separada de aluno, rejeitada por violar a spec |
| Validação de cardinalidade em tempo real | As regras de 1 Scrum Master, 1 Product Owner e >=1 Desenvolvedor são obrigatórias | Permitir salvar e corrigir depois, rejeitado por deixar a equipe inválida |
| Campos de texto livre em vez de dropdown de papel | A spec revisada define que o formulário deve ter campos nomeados por papel (FR-002); dropdown genérico foi considerado mas gera UX confusa e já foi descartado pelo usuário | Manter `MembroEquipeFormSet` com campo `aluno` (dropdown) e campo `papel` (select): rejeitado porque exige interação extra e não mapeia naturalmente para "insira o nome do Scrum Master" |
| Resolução de aluno por nome no save | Texto livre é mais natural do que autocomplete no contexto atual; a resolução acontece no backend no momento do save | Autocomplete via AJAX: rejeitado por adicionar complexidade de frontend sem biblioteca já presente |
| Campos de Desenvolvedor dinâmicos sem management form | Padrão já validado em `RepositorioCardCollection`; evita os bugs de TOTAL_FORMS/INITIAL_FORMS na abertura do form | Reutilizar `MembroEquipeFormSet` com formset padrão do Django: rejeitado porque o mesmo problema de management form já ocorreu e foi resolvido na feature 001 |

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Revisão 2026-08-10: novo padrão de UI de membros documentado no plan, research e data-model
- [ ] tasks.md atualizado para refletir o novo padrão (via `/speckit.tasks`)

**STOP** — Este plan encerra na Fase 1. A Fase 2 (`tasks.md`) é gerada pelo comando `/speckit.tasks`.
