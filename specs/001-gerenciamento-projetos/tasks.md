# Tasks: Gerenciamento de Projetos

**Input**: Design documents from `/specs/001-gerenciamento-projetos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are not requested for this feature. Focus on implementation tasks and manual validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when the task touches different files and has no dependency on an incomplete task
- **[Story]**: Which user story the task belongs to. Use `US1`, `US2`, `US3` only for story phases
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare reusable infrastructure needed by the project feature before the CRUD changes land.

- [X] T001 [P] Create a reusable GitHub validation helper package in commex/services/github.py and commex/services/__init__.py
- [X] T002 [P] Create reusable repository form partials in commex/templates/commex/form/repository-fields.html and commex/templates/commex/form/repository-summary.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Refactor the existing Django app so the new project workflow has the right data model, auth, and form foundations.

- [X] T003 Refactor commex/models.py so Repositorio belongs to exactly one Projeto and Projeto stores the GitHub organization/conta link required by the spec
- [X] T004 Create the supporting migration in commex/migrations/0003_project_github_refactor.py to persist the new Projeto and Repositorio shape
- [X] T005 [P] Rework commex/forms.py to separate project fields from repository fields and validate the GitHub link inputs
- [X] T006 [P] Protect the project CRUD views with login requirements in commex/views.py using Django auth guards
- [X] T007 Add Django auth route support in naes2026/urls.py, create the login template in templates/registration/login.html, and add login/logout navigation in commex/templates/commex/base.html

**Checkpoint**: The codebase has the correct data shape, protected views, and auth entry points needed before user stories can be completed.

---

## Phase 3: User Story 1 - Criar e listar projeto com GitHub validado (Priority: P1) 🎯 MVP

**Goal**: Allow an authenticated user to create a project with a validated GitHub organization/account link, associate repositories, and see the project in listing/detail views.

**Independent Test**: An authenticated user can create a valid project, see it in the list, and open its details with the organization and repositories shown.

### Implementation for User Story 1

- [X] T008 [P] [US1] Update ProjetoCreate and ProjetoList behavior in commex/views.py for the authenticated create and list flow
- [X] T009 [P] [US1] Update commex/templates/commex/list/projeto.html to display the organization link and repository summary for each project
- [X] T010 [P] [US1] Update commex/templates/commex/detail/projeto.html to display the organization link and repository links in the project detail view
- [X] T011 [P] [US1] Update commex/templates/commex/form.html to render the organization and repository inputs with validation feedback
- [X] T012 [US1] Implement create-time GitHub existence validation and save logic in commex/forms.py and commex/services/github.py

**Checkpoint**: User Story 1 is complete when an authenticated user can create and inspect a valid project without breaking the current Django flow.

---

## Phase 4: User Story 2 - Editar e manter repositórios vinculados (Priority: P2)

**Goal**: Allow an authenticated user to edit project data, add repositories later, and remove a repository without deleting the project.

**Independent Test**: An authenticated user can edit a project, add a new repository, remove an existing repository, and verify the project still exists afterward.

### Implementation for User Story 2

- [X] T013 [P] [US2] Update ProjetoUpdate and ProjetoDelete behavior in commex/views.py for edit, confirmation, and repository removal flows
- [X] T014 [P] [US2] Extend commex/forms.py to support adding and removing repository rows during project editing
- [X] T015 [P] [US2] Update commex/templates/commex/form.html and commex/templates/commex/detail/projeto.html for inline repository management and delete confirmation
- [X] T016 [US2] Enforce duplicate repository-link and owner-mismatch rules in commex/models.py and commex/forms.py

**Checkpoint**: User Story 2 is complete when repository maintenance works independently of project creation.

---

## Phase 5: User Story 3 - Selecionar projeto em outras telas (Priority: P3)

**Goal**: Show only active projects in selection fields used by other screens so users can reuse existing project records safely.

**Independent Test**: In any screen that selects a project, only active projects appear and the selected project is carried through correctly.

### Implementation for User Story 3

- [X] T017 [P] [US3] Restrict project choice querysets to active projects in commex/views.py for EquipeCreate and EquipeUpdate
- [X] T018 [P] [US3] Add a shared active-project queryset helper in commex/forms.py for any future project-selection forms
- [X] T019 [US3] Update commex/templates/commex/detail/equipe.html and commex/templates/commex/list/equipe.html so project selection and display stay consistent with the active-project rule

**Checkpoint**: User Story 3 is complete when other screens can select active projects without exposing inactive records.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep the feature consistent across templates and documentation after the main workflows are in place.

- [X] T020 [P] Harmonize labels and navigation in commex/templates/commex/base.html, commex/templates/commex/index.html, and commex/templates/commex/list/projeto.html
- [X] T021 Clean up unused project assumptions and legacy repository handling in commex/models.py and commex/forms.py after the refactor
- [X] T022 Review specs/001-gerenciamento-projetos/quickstart.md against the final workflow and update it if the manual steps changed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Final Phase)**: Depends on the desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational and does not depend on other stories
- **User Story 2 (P2)**: Starts after Foundational and may reuse Story 1 components, but remains independently testable
- **User Story 3 (P3)**: Starts after Foundational and may reuse Story 1/2 selectors, but remains independently testable

### Within Each User Story

- Form and validation logic should be ready before the related view/template finish-up
- Templates can be updated in parallel when they touch different files
- Any shared helper created in Setup or Foundational must exist before the stories that consume it
- Story completion should be validated before moving to the next priority if the team is working sequentially

### Parallel Opportunities

- Setup tasks T001 and T002 can run in parallel
- Foundational tasks T005 and T006 can run in parallel after T003 and T004
- Story 1 tasks T008, T009, T010, and T011 can run in parallel once the Phase 2 field names and validation rules are in place; T012 then finalizes the create-time validation behavior
- Story 2 tasks T013, T014, and T015 can run in parallel once the repository ownership model is fixed; T016 follows the refactor rules
- Story 3 tasks T017 and T018 can run in parallel after the foundational queryset rules are defined; T019 follows the selector behavior update
- Polish task T020 can run alongside T021 and T022 because they touch different files

---

## Parallel Example: User Story 1

```text
Task: T009 [P] [US1] Update commex/templates/commex/list/projeto.html
Task: T010 [P] [US1] Update commex/templates/commex/detail/projeto.html
Task: T011 [P] [US1] Update commex/templates/commex/form.html
```

## Parallel Example: User Story 2

```text
Task: T013 [P] [US2] Update commex/views.py for edit and delete flows
Task: T014 [P] [US2] Extend commex/forms.py for repository maintenance
Task: T015 [P] [US2] Update commex/templates/commex/form.html and commex/templates/commex/detail/projeto.html
```

## Parallel Example: User Story 3

```text
Task: T017 [P] [US3] Restrict project querysets in commex/views.py
Task: T018 [P] [US3] Add shared active-project queryset helper in commex/forms.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the create/list/detail flow manually
5. Stop and demo if this is enough value for release

### Incremental Delivery

1. Complete Setup + Foundational so the app shape is ready
2. Deliver User Story 1 as the MVP
3. Add User Story 2 to support maintenance of repositories
4. Add User Story 3 to make project selection safe in other screens
5. Finish with polish and documentation cleanup

### Parallel Team Strategy

- One developer can own the model/migration refactor while another prepares the templates and auth entry points
- After the foundation is complete, one developer can handle Story 1 while another starts Story 2
- Story 3 can be completed once the shared project queryset rule is clear

---

## Notes

- [P] tasks use different files and should not wait on incomplete work in the same phase
- Story labels map tasks to the feature stories from spec.md
- The plan intentionally avoids introducing a REST API because the current app is a Django server-rendered project
- Manual validation is the default verification path for this feature
