# Tasks: Gerenciamento de Equipes e Membros

**Input**: Design documents from `/specs/002-gerenciamento-equipes-membros/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are not requested for this feature. Validation will be manual through create/edit/list/remove flows.

**Organization**: Tasks are grouped by user story to preserve independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable task
- **[Story]**: Story label for story phases (`[US1]`, `[US2]`, `[US3]`)
- Tasks include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared forms, pages and navigation anchors.

- [X] T001 [P] Create teams templates structure in `commex/templates/commex/equipes/`
- [X] T002 [P] Create members templates structure in `commex/templates/commex/membros/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build base entities and shared constraints used by all stories.

- [X] T003 Implement `Equipe`, `Aluno`, and `MembroEquipe` model constraints in `commex/models.py`
- [X] T004 Create migration for team/member refinements in `commex/migrations/0004_equipes_membros_constraints.py`
- [X] T005 [P] Create shared forms for team and member operations in `commex/forms.py`
- [X] T006 Add team/member routes and view stubs in `commex/urls.py` and `commex/views.py`

**Checkpoint**: Core entities and routes are ready.

---

## Phase 3: User Story 1 - Criar e editar equipes com membros (Priority: P1) 🎯 MVP

**Goal**: Create and edit teams including member assignment and role constraints.

**Independent Test**: User creates a team, adds members with roles, and blocked role conflicts are enforced.

### Implementation for User Story 1

- [X] T007 [P] [US1] Implement team create/edit views with member inline handling in `commex/views.py`
- [X] T008 [P] [US1] Implement member role validation rules (1 LIDER, 1 VICE_LIDER) in `commex/forms.py` and `commex/models.py`
- [X] T009 [P] [US1] Create team create/edit templates in `commex/templates/commex/equipes/form.html`
- [X] T010 [US1] Add user-facing validation feedback for role conflicts in `commex/templates/commex/equipes/form.html` and `commex/views.py`

**Checkpoint**: Team authoring flow is functional and constrained correctly.

---

## Phase 4: User Story 2 - Listar e consultar composição da equipe (Priority: P2)

**Goal**: View teams and inspect membership composition clearly.

**Independent Test**: User opens team list and detail and sees complete composition with roles and ordering.

### Implementation for User Story 2

- [X] T011 [P] [US2] Implement team list and detail queries with optimized related loading in `commex/views.py`
- [X] T012 [P] [US2] Create team list template in `commex/templates/commex/equipes/list.html`
- [X] T013 [P] [US2] Create team detail template with members/roles in `commex/templates/commex/equipes/detail.html`
- [X] T014 [US2] Add ordering/filter behavior for better consultation in `commex/views.py` and `commex/forms.py`

**Checkpoint**: Team consultation is complete and readable.

---

## Phase 5: User Story 3 - Remover membros e inativar equipes com segurança (Priority: P3)

**Goal**: Remove members and deactivate teams while preserving consistency rules.

**Independent Test**: User removes a member and deactivates a team with safeguards preventing invalid states.

### Implementation for User Story 3

- [X] T015 [P] [US3] Implement member removal flow with team consistency checks in `commex/views.py` and `commex/forms.py`
- [X] T016 [P] [US3] Implement team deactivation flow preserving historical references in `commex/views.py` and `commex/models.py`
- [X] T017 [P] [US3] Create confirmation templates for member removal and team deactivation in `commex/templates/commex/membros/confirm_delete.html` and `commex/templates/commex/equipes/confirm_disable.html`
- [X] T018 [US3] Add guardrails to block invalid deactivation/removal transitions in `commex/views.py`

**Checkpoint**: Safe removal/deactivation works with explicit confirmations.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve consistency, UX, and documentation.

- [X] T019 [P] Add teams/members navigation entries in `commex/templates/commex/base.html`
- [X] T020 [P] Standardize form/help text for roles and membership rules in `commex/forms.py` and templates under `commex/templates/commex/equipes/`
- [X] T021 Align usage scenarios with implemented flow in `specs/002-gerenciamento-equipes-membros/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): none
- Foundational (Phase 2): depends on Setup; blocks all stories
- Story Phases (3-5): depend on Foundational
- Polish (Phase 6): depends on story completion

### User Story Dependencies

- US1 (P1): first deliverable and MVP
- US2 (P2): depends on team/member data from US1 for meaningful display
- US3 (P3): depends on established membership data and team lifecycle

### Parallel Opportunities

- T001 and T002
- T007, T008, and T009
- T011, T012, and T013
- T015, T016, and T017
- T019 and T021

---

## Parallel Example: User Story 1

```text
Task: T007 [P] [US1] Implement team create/edit views
Task: T008 [P] [US1] Implement member role validation rules
Task: T009 [P] [US1] Create team create/edit templates
```

## Implementation Strategy

### MVP First (US1)

1. Complete Setup and Foundational
2. Deliver US1
3. Validate role constraints and assignment flow

### Incremental Delivery

1. Add listing/detail consultation (US2)
2. Add safe removal/deactivation (US3)
3. Apply final polish

---

## Notes

- No automated tests were added because tests were not explicitly requested
- Tasks are implementation-ready and reference concrete files
