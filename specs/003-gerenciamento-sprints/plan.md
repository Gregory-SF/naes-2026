# Implementation Plan: Gerenciamento de Sprints

**Branch**: `003-gerenciamento-sprints` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-gerenciamento-sprints/spec.md`

## Summary

Implementar CRUD de sprints com vínculo N:N a projetos, mantendo o comportamento
de pré-seleção de projetos e atualização reversível dos vínculos.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: Django 5.x, crispy forms
**Storage**: PostgreSQL (Neon)
**Testing**: Não obrigatório; validação manual
**Target Platform**: Django server-rendered
**Constraints**: Preservar relacionamento com Projeto e fluxo existente

## Constitution Check

- ✅ Alinhado com Python/Django
- ✅ Sem conflito com infra e banco atuais

## Access, Ownership, Pagination and Query Decisions

### View Access Matrix

| View | LoginRequiredMixin | GroupRequiredMixin | Decision |
|---|---|---|---|
| `SprintCreate` | Sim | Não | A spec pede usuário autorizado, sem restrição por grupo |
| `SprintUpdate` | Sim | Não | Edição de sprint é operação protegida, mas não grupal |
| `SprintDelete` | Sim | Não | Exclusão segue o mesmo controle de acesso autenticado |
| `SprintList` | Sim | Não | Consulta de sprints é interna à área autenticada |
| `SprintDetail` | Sim | Não | Detalhe da sprint é parte do mesmo fluxo protegido |

### User Ownership / `User` ForeignKey

- Nenhum model desta feature possui `ForeignKey` para `User`.
- Não há owner para preencher em `form_valid()` e não há `get_queryset()` de isolamento por usuário.
- A regra constitucional de isolamento por usuário não se aplica aqui.

### ListView Pagination

- `SprintList` implementa `paginate_by = 20`.
- Justificativa: a lista de sprints é uma coleção operacional que pode crescer ao longo dos semestres e precisa permanecer navegável.

### Templates que Consultam `request.user.is_authenticated`

- `commex/base.html` para alternar menu/ações protegidas.
- `commex/list/sprint.html` para exibir botões de criar/editar/excluir apenas a usuários autenticados.
- `commex/detail/sprint.html` para exibir ações sensíveis conforme o estado autenticado.
- Templates de formulário de sprint para esconder ou mostrar ações de confirmação conforme autenticação.

### Querysets com Relações em Template

- `SprintList` e `SprintDetail` devem usar `prefetch_related('projetos')` porque a feature exibe os projetos vinculados à sprint.
- Se a listagem mostrar contagem ou nomes dos projetos, essa prefetch é obrigatória para evitar consultas repetidas.
- Não há `select_related` obrigatório para este escopo porque o relacionamento principal é M2M via `SprintProjeto`.

## Project Structure

```text
specs/003-gerenciamento-sprints/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

## Phase 0: Outline & Research

1. Confirmar regra de vínculo automático inicial
2. Confirmar filtros por projeto e período
3. Confirmar comportamento de desvínculo total permitido

## Phase 1: Design & Contracts

1. `data-model.md` com Sprint e SprintProjeto
2. Contracts não aplicável
3. `quickstart.md` com validação do fluxo de marcação/desmarcação

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`
