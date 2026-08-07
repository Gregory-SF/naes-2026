# Tasks: Gerenciamento de Sprints

**Input**: Design documents from `/specs/003-gerenciamento-sprints/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are not requested for this feature. Validation will be manual via sprint create/edit/link/list flows.

**Organization**: Tasks are grouped by user story for independent verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable task
- **[Story]**: Story label for story phases (`[US1]`, `[US2]`, `[US3]`)
- Tasks include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare sprint templates and route placeholders.

- [X] T001 [P] Create sprint templates structure in `commex/templates/commex/sprints/`
- [X] T002 [P] Create project-link templates structure in `commex/templates/commex/sprints/projetos/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the data and route baseline for all sprint stories.

- [X] T003 Implement/adjust `Sprint` and sprint-project linkage constraints in `commex/models.py`
- [X] T004 Create migration for sprint and linkage adjustments in `commex/migrations/0004_sprints_relacoes.py`
- [X] T005 [P] Implement shared sprint forms in `commex/forms.py`
- [X] T006 Add sprint URL patterns and view stubs in `commex/urls.py` and `commex/views.py`

**Checkpoint**: Sprint entities, constraints, and routes are ready.

---

## Phase 3: User Story 1 - Cadastrar e editar sprints (Priority: P1) 🎯 MVP

**Goal**: Create and edit sprint records with consistent date and naming rules.

**Independent Test**: User creates and edits sprint with valid period and sees validation for invalid ranges.

### Implementation for User Story 1

- [X] T007 [P] [US1] Implement sprint create/edit views in `commex/views.py`
- [X] T008 [P] [US1] Implement sprint date/name validations in `commex/forms.py` and `commex/models.py`
- [X] T009 [P] [US1] Create sprint form template in `commex/templates/commex/sprints/form.html`
- [X] T010 [US1] Add validation feedback and success messaging in `commex/views.py` and `commex/templates/commex/sprints/form.html`

**Checkpoint**: Sprint authoring flow is operational.

---

## Phase 4: User Story 2 - Vincular projetos às sprints (Priority: P2)

**Goal**: Associate one or more projects with a sprint and manage these links.

**Independent Test**: User links projects to sprint, avoids duplicate links, and updates associations.

### Implementation for User Story 2

- [X] T011 [P] [US2] Implement sprint-project linkage form and duplicate-link validation in `commex/forms.py` and `commex/models.py`
- [X] T012 [P] [US2] Implement linkage create/remove views in `commex/views.py`
- [X] T013 [P] [US2] Create linkage management template in `commex/templates/commex/sprints/projetos/manage.html`
- [X] T014 [US2] Add contextual messages and redirect flow after link operations in `commex/views.py`

**Checkpoint**: Project associations are manageable and consistent.

---

## Phase 5: User Story 3 - Consultar sprints e seus vínculos (Priority: P3)

**Goal**: List and inspect sprints including linked projects and period metadata.

**Independent Test**: User filters/list sprints and opens details showing associated projects and dates.

### Implementation for User Story 3

- [X] T015 [P] [US3] Implement sprint list/detail queries with related prefetch in `commex/views.py`
- [X] T016 [P] [US3] Create sprint list template with period fields in `commex/templates/commex/sprints/list.html`
- [X] T017 [P] [US3] Create sprint detail template with linked projects in `commex/templates/commex/sprints/detail.html`
- [X] T018 [US3] Implement filters by name/date/project in `commex/forms.py` and `commex/views.py`

**Checkpoint**: Sprint consultation is complete and supports common filters.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize UX consistency and operational docs.

- [X] T019 [P] Add sprint navigation entry in `commex/templates/commex/base.html`
- [X] T020 [P] Improve labels/help text for sprint date and linkage rules in `commex/forms.py` and `commex/templates/commex/sprints/`
- [X] T021 Align manual validation scenarios with implementation in `specs/003-gerenciamento-sprints/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): none
- Foundational (Phase 2): depends on Setup; blocks all stories
- Story Phases (3-5): depend on Foundational
- Polish (Phase 6): depends on story completion

### User Story Dependencies

- US1 (P1): MVP
- US2 (P2): depends on sprint records from US1
- US3 (P3): depends on baseline sprint/link data for meaningful consultation

### Parallel Opportunities

- T001 and T002
- T007, T008, and T009
- T011, T012, and T013
- T015, T016, and T017
- T019 and T021

---

## Parallel Example: User Story 2

```text
Task: T011 [P] [US2] Implement sprint-project linkage validation
Task: T012 [P] [US2] Implement linkage create/remove views
Task: T013 [P] [US2] Create linkage management template
```

## Implementation Strategy

### MVP First (US1)

1. Complete Setup and Foundational
2. Deliver sprint create/edit flow
3. Validate date-range rules manually

### Incremental Delivery

1. Add sprint-project linking (US2)
2. Add consultation/filtering (US3)
3. Finalize polish

---

## Notes

- No automated tests were added because tests are optional and not requested
- Tasks follow the required checklist format and explicit file paths
