# Tasks: Geração de Análise de Commits

**Input**: Design documents from `/specs/005-geracao-analise-commits/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are not requested for this feature. Validation will be manual using execution status and imported commit records.

**Organization**: Tasks are grouped by user story to enable independent delivery and verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable task (different files and no unfinished dependency conflict)
- **[Story]**: Story label for story phases (`[US1]`, `[US2]`, `[US3]`)
- Every task includes exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared modules and route scaffolding for commit analysis flows.

- [X] T001 [P] Create analysis service package skeleton in `commex/services/analysis.py` and `commex/services/__init__.py`
- [X] T002 [P] Create base analysis templates directory structure in `commex/templates/commex/analysis/` with placeholder files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the core data and execution infrastructure that all stories depend on.

- [X] T003 Implement `Branch`, `ExecucaoAnalise`, and `CommitAnalisado` models in `commex/models.py`
- [X] T004 Create migration for analysis entities in `commex/migrations/0004_execucao_analise_commit.py`
- [X] T005 [P] Add GitHub token retrieval integration from global settings in `commex/services/global_settings.py` and `commex/services/analysis.py`
- [X] T006 [P] Add branch uniqueness and repository linkage validation in `commex/models.py` and `commex/forms.py`
- [X] T007 Add analysis routes and view entry points in `commex/urls.py` and `commex/views.py`

**Checkpoint**: Models, migration, token integration, and route foundations are ready.

---

## Phase 3: User Story 1 - Selecionar parâmetros e iniciar análise (Priority: P1) 🎯 MVP

**Goal**: Let users pick project/repository/branch/period and start an execution with tracked status.

**Independent Test**: User selects parameters, starts execution, and sees a created execution record with processing lifecycle.

### Implementation for User Story 1

- [X] T008 [P] [US1] Create analysis parameter form (project, repository, branch, sprint/manual dates) in `commex/forms.py`
- [X] T009 [P] [US1] Implement analysis start view and execution bootstrap in `commex/views.py`
- [X] T010 [P] [US1] Create analysis start template in `commex/templates/commex/analysis/start.html`
- [X] T011 [US1] Add period validation logic (manual vs sprint dates) in `commex/forms.py` and `commex/services/analysis.py`

**Checkpoint**: Execution can be started through UI with valid parameters.

---

## Phase 4: User Story 2 - Buscar e persistir branches do repositório (Priority: P2)

**Goal**: Fetch branches from GitHub and persist selected branches for reuse.

**Independent Test**: User fetches remote branches, adds one, and duplicate add is blocked for same repository.

### Implementation for User Story 2

- [X] T012 [P] [US2] Implement GitHub branch-fetch service with token-auth request in `commex/services/analysis.py`
- [X] T013 [P] [US2] Implement branch fetch/add views in `commex/views.py`
- [X] T014 [P] [US2] Create branch management template in `commex/templates/commex/analysis/branches.html`
- [X] T015 [US2] Enforce duplicate branch protection and user feedback in `commex/forms.py` and `commex/views.py`

**Checkpoint**: Branches are reusable local entities linked to repositories.

---

## Phase 5: User Story 3 - Importar commits e persistir dados relevantes (Priority: P3)

**Goal**: Import paginated commits, persist only relevant fields, and link authors to students when possible.

**Independent Test**: A run imports commits for selected period, updates execution progress/status, and stores expected fields.

### Implementation for User Story 3

- [X] T016 [P] [US3] Implement paginated commit-fetch pipeline with since/until and rate-limit handling in `commex/services/analysis.py`
- [X] T017 [P] [US3] Implement commit-field extraction/persistence mapping in `commex/services/analysis.py` and `commex/models.py`
- [X] T018 [P] [US3] Implement author-to-student association by GitHub nickname in `commex/services/analysis.py` and `commex/models.py`
- [X] T019 [US3] Implement execution status/progress updates and error recording in `commex/services/analysis.py` and `commex/views.py`
- [X] T020 [US3] Create execution status/history template in `commex/templates/commex/analysis/status.html`

**Checkpoint**: Commit import runs end-to-end with status tracking and reusable history.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, resilience checks, and docs alignment.

- [X] T021 [P] Add analysis navigation entry and access consistency in `commex/templates/commex/base.html`
- [X] T022 Harden sensitive logging paths to avoid token leakage in `commex/services/analysis.py` and `commex/services/global_settings.py`
- [X] T023 Align manual runbook with implemented flow in `specs/005-geracao-analise-commits/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks all stories
- **Story Phases (3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on story completion

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and delivers MVP
- **US2 (P2)**: Starts after Foundational and reuses token/repository context
- **US3 (P3)**: Starts after Foundational and depends on branch availability from US2 for full value

### Within Each User Story

- Forms and validation before final view/template completion
- Service layer logic should be settled before UI status wiring
- Persistence mapping must be complete before progress/history polish

### Parallel Opportunities

- T001 and T002
- T005 and T006
- T008, T009, and T010
- T012 and T013
- T016, T017, and T018
- T021 and T023

---

## Parallel Example: User Story 1

```text
Task: T008 [P] [US1] Create analysis parameter form in commex/forms.py
Task: T009 [P] [US1] Implement analysis start view in commex/views.py
Task: T010 [P] [US1] Create analysis start template in commex/templates/commex/analysis/start.html
```

## Parallel Example: User Story 2

```text
Task: T012 [P] [US2] Implement branch-fetch service in commex/services/analysis.py
Task: T013 [P] [US2] Implement branch fetch/add views in commex/views.py
Task: T014 [P] [US2] Create branch management template
```

## Parallel Example: User Story 3

```text
Task: T016 [P] [US3] Implement paginated commit-fetch pipeline
Task: T017 [P] [US3] Implement commit-field extraction/persistence mapping
Task: T018 [P] [US3] Implement author-to-student association
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and 2
2. Deliver US1
3. Validate execution creation and parameter validation
4. Demo minimal usable flow

### Incremental Delivery

1. Add branch fetch/persist (US2)
2. Add import and persistence pipeline (US3)
3. Finish polish and runbook updates

### Parallel Team Strategy

- Team A: models/migrations/services foundation
- Team B: views/templates for start and status flows
- Then split US2 (branch) and US3 (import pipeline)

---

## Notes

- No automated test tasks were added because tests are optional and not requested
- Story labels map directly to spec stories
- Task order is execution-oriented for incremental delivery
