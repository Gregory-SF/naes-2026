# Tasks: Autenticação de Usuário

**Input**: Design docs from `/specs/006-autenticacao-usuario/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are optional and were not explicitly requested for this feature. The tasks below focus on implementation and manual validation via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align shared auth settings with the feature's public and authenticated redirects.

- [X] T001 Update `naes2026/settings.py` so `LOGOUT_REDIRECT_URL` points to the public login page while keeping `LOGIN_REDIRECT_URL` on `index` for the authenticated home.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared UI behavior that every auth story depends on.

**Independent Test**: Anonymous users should only see public navigation, while authenticated users should see protected actions plus password-change and logout links.

- [X] T002 [P] Update `commex/templates/commex/base.html` to gate protected project actions behind `request.user.is_authenticated` and expose `Alterar senha` and `Sair` only to authenticated users.

**Checkpoint**: Shared auth navigation and redirect settings are ready for the user stories.

---

## Phase 3: User Story 1 - Autenticar com usuário e senha (Priority: P1) 🎯 MVP

**Goal**: Allow public users to log in, preserve `next`, and redirect authenticated users away from the login form.

**Independent Test**: Open `/accounts/login/`, authenticate with valid credentials, confirm redirect to `next` when present or `index` when absent, and verify invalid credentials show only the generic login error.

### Implementation for User Story 1

- [X] T003 Add an explicit login route override in `naes2026/urls.py` using `LoginView.as_view(redirect_authenticated_user=True)` while keeping `django.contrib.auth.urls` available for the remaining auth endpoints.
- [X] T004 [P] Update `templates/registration/login.html` to preserve the submitted `next` value, keep the entered username after validation failure, and render only the generic login error message.

**Checkpoint**: User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Encerrar sessão autenticada (Priority: P2)

**Goal**: Allow authenticated users to end their session and return to a public page.

**Independent Test**: Trigger logout while authenticated and confirm the session is cleared and the browser lands on the public login page.

### Implementation for User Story 2

- [X] T005 Add an explicit logout route override in `naes2026/urls.py` using `LogoutView.as_view(next_page='login')` so logout always returns to a public destination.

**Checkpoint**: User Story 2 should be independently usable once the shared auth base is in place.

---

## Phase 5: User Story 3 - Alterar a própria senha com validações (Priority: P3)

**Goal**: Let authenticated users change their own password with current-password and password-policy validation.

**Independent Test**: Open the password-change page while authenticated, submit a valid old password plus a valid new password and confirmation, and confirm the success message; invalid old password or invalid new password must block the change.

### Implementation for User Story 3

- [X] T006 [P] [US3] Create `templates/registration/password_change_form.html` with `old_password`, `new_password1`, `new_password2`, and Django form error rendering.
- [X] T007 [P] [US3] Create `templates/registration/password_change_done.html` to confirm the password update and link the user back to the authenticated home.

**Checkpoint**: User Story 3 should be fully functional and testable independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep the documented validation path aligned with the implemented auth flow.

- [X] T008 Update `specs/006-autenticacao-usuario/quickstart.md` to match the final login, logout, and password-change flow, including `next` redirection and the public logout destination.
- [X] T009 Validate the feature manually against `specs/006-autenticacao-usuario/quickstart.md` and fix any mismatch in `naes2026/settings.py`, `naes2026/urls.py`, `commex/templates/commex/base.html`, or `templates/registration/*.html`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Stories (Phase 3+)**: Depend on the Foundational phase completion.
- **Polish (Final Phase)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after the Foundational phase - no dependency on other user stories.
- **User Story 2 (P2)**: Can start after the Foundational phase - independent of login and password-change work.
- **User Story 3 (P3)**: Can start after the Foundational phase - independent of login/logout flow beyond shared auth navigation.

### Within Each User Story

- Shared auth settings before route-specific behavior.
- Route configuration before template polish where applicable.
- Base navigation changes before final manual validation.

### Parallel Opportunities

- T002 can run in parallel with T001 because they touch different files.
- T004 can run in parallel with T003 because the login template and login route override are separate files.
- T006 and T007 can run in parallel because they create different password-change templates.
- T008 can run after implementation is stable and does not block code changes.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate login, `next` redirection, and the generic invalid-credential message.
5. Stop and demo if the login flow is ready.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 and verify login works end to end.
3. Add User Story 2 and verify logout returns to the public login page.
4. Add User Story 3 and verify password change validation and success feedback.
5. Finish with the quickstart update and manual validation.

### Parallel Team Strategy

1. One developer can handle settings and route overrides.
2. Another developer can update the base navigation and auth templates.
3. Password-change templates can be created in parallel once the shared auth shell is ready.
