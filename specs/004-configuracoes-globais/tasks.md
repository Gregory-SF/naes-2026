# Tasks: Configurações Globais do Sistema

**Input**: Design documents from `/specs/004-configuracoes-globais/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are not requested for this feature. Validation will be manual through UI and persistence checks.

**Organization**: Tasks are grouped by user story to keep each story independently implementable and verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unfinished dependency overlap)
- **[Story]**: User story label for story-phase tasks (`[US1]`, `[US2]`, `[US3]`)
- All task descriptions include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline modules and UI entry points for global settings.

- [X] T001 [P] Create service module skeleton for global settings in `commex/services/global_settings.py` and `commex/services/__init__.py`
- [X] T002 [P] Add menu placeholder for global settings access in `commex/templates/commex/base.html`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create core persistence and security foundations required by all stories.

- [X] T003 Implement `ConfiguracaoGlobal` and `DiaAula` models in `commex/models.py`
- [X] T004 Create migration for global settings entities in `commex/migrations/0003_configuracao_global_dia_aula.py`
- [X] T005 [P] Add token protection and masking helpers in `commex/services/global_settings.py`
- [X] T006 [P] Add environment-backed encryption key handling in `naes2026/settings.py`
- [X] T007 Create base settings URL routes in `commex/urls.py` and wire view import points in `commex/views.py`

**Checkpoint**: Data model, migration, security helpers, and route foundations are ready.

---

## Phase 3: User Story 1 - Acessar e salvar configurações globais (Priority: P1) 🎯 MVP

**Goal**: Allow users to open settings and save token/dias de aula in one global record.

**Independent Test**: User opens settings page, saves token and selected weekdays, and sees persisted state after reload.

### Implementation for User Story 1

- [X] T008 [P] [US1] Create settings form with token input and multi-select weekdays in `commex/forms.py`
- [X] T009 [P] [US1] Implement settings create/update view flow in `commex/views.py`
- [X] T010 [P] [US1] Create settings template with token status and weekday selector in `commex/templates/commex/form/configuracoes.html`
- [X] T011 [US1] Persist singleton settings behavior and saved-state loading in `commex/services/global_settings.py` and `commex/views.py`

**Checkpoint**: User can save and reload global settings state.

---

## Phase 4: User Story 2 - Visualizar, substituir e remover token (Priority: P2)

**Goal**: Manage token lifecycle securely with masked default view and controlled reveal.

**Independent Test**: User can see masked token, reveal temporarily, replace value, and remove token cleanly.

### Implementation for User Story 2

- [X] T012 [P] [US2] Add token masking/reveal UI interactions in `commex/templates/commex/form/configuracoes.html` and `static/js/configuracoes.js`
- [X] T013 [P] [US2] Implement token replace/remove actions in `commex/views.py` and `commex/services/global_settings.py`
- [X] T014 [US2] Enforce no-plain-text persistence and non-logging of token values in `commex/services/global_settings.py`

**Checkpoint**: Token can be safely viewed, replaced, and removed without exposing raw value at rest.

---

## Phase 5: User Story 3 - Atualizar dias de aula (Priority: P3)

**Goal**: Allow idempotent weekday selection updates, including empty selection.

**Independent Test**: User marks/unmarks weekdays, saves repeatedly, and always sees accurate persisted state.

### Implementation for User Story 3

- [X] T015 [P] [US3] Implement idempotent weekday update logic in `commex/forms.py` and `commex/services/global_settings.py`
- [X] T016 [P] [US3] Add settings summary display for selected weekdays in `commex/templates/commex/form/configuracoes.html`
- [X] T017 [US3] Ensure empty-weekdays state is accepted and rendered correctly in `commex/views.py` and `commex/forms.py`

**Checkpoint**: Weekday configuration updates are reversible, repeatable, and stable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency and manual validation pass across UX and docs.

- [X] T018 [P] Refine navigation labels and settings entry visibility in `commex/templates/commex/base.html`
- [X] T019 Run quickstart validation updates in `specs/004-configuracoes-globais/quickstart.md` based on implemented flow
- [X] T020 Verify migration naming/version consistency and update references in `specs/004-configuracoes-globais/plan.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can begin immediately
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on completion of selected story phases

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; delivers MVP
- **US2 (P2)**: Starts after Foundational; builds on saved token flow from US1
- **US3 (P3)**: Starts after Foundational; can proceed in parallel with US2 after US1 baseline form/view exists

### Within Each User Story

- Forms/services logic before final view/template completion
- Template/UI tasks can run in parallel where files differ
- Singleton persistence behavior must be settled before replacement/removal edge actions

### Parallel Opportunities

- T001 and T002
- T005 and T006
- T008, T009, T010
- T012 and T013
- T015 and T016
- T018 and T019

---

## Parallel Example: User Story 1

```text
Task: T008 [P] [US1] Create settings form in commex/forms.py
Task: T009 [P] [US1] Implement settings view flow in commex/views.py
Task: T010 [P] [US1] Create settings template in commex/templates/commex/form/configuracoes.html
```

## Parallel Example: User Story 2

```text
Task: T012 [P] [US2] Add token masking/reveal UI
Task: T013 [P] [US2] Implement token replace/remove actions
```

## Parallel Example: User Story 3

```text
Task: T015 [P] [US3] Implement idempotent weekday update logic
Task: T016 [P] [US3] Add selected-weekdays summary display
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2
2. Complete US1 tasks (T008-T011)
3. Validate persisted state load/reload
4. Stop and demo MVP

### Incremental Delivery

1. Deliver US1 (save/load global settings)
2. Deliver US2 (secure token lifecycle)
3. Deliver US3 (weekday update stability)
4. Run polish and documentation checks

### Parallel Team Strategy

- Developer A: models/migrations/services (T003-T006)
- Developer B: views/routes/templates (T007-T010)
- After foundation: split US2 UI/security and US3 weekdays logic

---

## Notes

- No automated test tasks were added because tests are optional and not requested in this spec
- [P] tasks are scoped to minimize file conflicts
- Story labels map directly to spec user stories for traceability
