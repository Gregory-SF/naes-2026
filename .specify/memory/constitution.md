<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles: V. Autenticação e Mudanças Seguras -> V. Autenticação e Mudanças Seguras (expanded)
- Added sections: none
- Removed sections: none
- Templates requiring updates: ✅ .specify/templates/plan-template.md; ✅ .specify/templates/spec-template.md; ✅ .specify/templates/tasks-template.md
- Deferred items: none
-->

# NAES 2026 Constitution

## Core Principles

### I. Python e Django Como Base
The project MUST remain implemented in Python and Django. New code must reuse
Django's standard project structure, ORM, forms, templates, middleware, and
authentication system unless an existing module already provides the required
behavior. Any new dependency must fit the current stack and must not replace the
framework.

### II. Templates Django Dinâmicos
HTML must be rendered with Django templates and context-driven views, not with
static pages or a conflicting frontend stack. Templates MUST maximize Django
features such as inheritance, blocks, reusable partials, context variables, and
form rendering. Template changes must preserve the existing structure under
`commex/` and `website/`.

### III. Infraestrutura GCloud e Neon Preservadas
The project MUST keep the current GCloud-oriented static/file deployment shape and
must not introduce technologies or settings that conflict with it. The PostgreSQL
database connection to Neon is the canonical storage backend and must remain the
default data source unless the user explicitly requests a migration. Environment
configuration, static files, and deployment settings must stay compatible with the
current `STATIC_ROOT`, `static_gcloud`, and PostgreSQL assumptions.

### IV. Bibliotecas Existentes São Contratos
Existing dependencies such as `django-crispy-forms`, `crispy-bootstrap5`,
`django-filter`, `django-braces`, `django-autocomplete-light`, and `gunicorn` are
part of the supported stack and must be reused instead of being replaced without
approval. New features MUST integrate with these libraries where they already
solve the problem. Removing or bypassing them requires a clear migration decision.

### V. Autenticação e Mudanças Seguras
Authenticated access must be preserved and extended consistently using Django auth,
LoginRequiredMixin, and request.user.is_authenticated for login-aware redirects, and permission checks where
needed. Changes must be incremental and must not break  existing URLs, templates,
forms, or views. When behavior changes are introduced, prefer the smallest safe
edit that keeps the application runnable end to end.

### VI. Autenticação e Autorização por Feature
Views that require authenticated users MUST use `LoginRequiredMixin`. Views that
require specific group membership MUST use `GroupRequiredMixin`. Authentication and
authorization requirements MUST be decided per feature and explicitly documented in
the feature `plan.md`; there is no global rule that all views require login or that
no views require login.

Templates MUST use `request.user.is_authenticated` to toggle dynamic content such as
menu items and action buttons, ensuring unauthenticated users do not see actions
they cannot execute.

Rationale: explicit per-feature access control avoids over-restricting public flows
and avoids accidental exposure of protected actions.

### VII. Isolamento de Dados por Usuário
For every model that has a foreign key to `User`, corresponding views MUST enforce
owner isolation:

- `CreateView`: assign the `User` foreign key automatically in `form_valid()` and
	never expose this field in the form.
- `UpdateView` and `DeleteView`: override `get_queryset()` to restrict records to
	the authenticated user's records only.
- `ListView`: override `get_queryset()` to list only the authenticated user's
	records.
- `DetailView`: override `get_queryset()` to prevent access to other users' records
	and return 404 instead of 403 for non-owned objects.

Any exception (for example, shared listing among users in the same team) MUST be
explicitly justified in the corresponding feature `plan.md`.

Rationale: URL manipulation must never allow read/write access to third-party data.

### VIII. Performance de Queries
Any queryset that surfaces related fields (`ForeignKey`, `OneToOne`, `ManyToMany`)
in templates MUST use `select_related` for direct relations and/or
`prefetch_related` for reverse and many-to-many relations to prevent N+1 queries.

Django Debug Toolbar MUST be enabled in development environments only (never in
production) and MUST be consulted before declaring a feature ready, with duplicate
query hotspots addressed or explicitly justified.

Rationale: query planning in Django views is a correctness requirement for scale,
not a late optimization.

### IX. UI de Listagens com Paginação
Every `ListView` MUST implement pagination via `paginate_by` and provide pagination
controls in templates (previous, next, and page numbers).

An exception is allowed only when feature business rules guarantee a small, finite
maximum dataset (for example, singleton configuration screens). Each exception MUST
be explicitly justified in the corresponding feature `plan.md`.

Rationale: mandatory pagination prevents accidental performance regression and keeps
list pages usable as data grows.

### X. Reuso de Consultas entre Views
Querysets reused by multiple views (for example, "latest records" or "recent
activity") MUST be centralized in model managers or class methods on the model.
Duplicating the same query logic across multiple views is not allowed unless there
is a documented feature-specific reason.

Rationale: centralized query logic improves consistency, reduces drift, and enables
safe optimization in one place.

## Additional Constraints

- The codebase MUST stay on Python and Django for server-side behavior.
- Views, forms, and templates MUST remain compatible with the current app
	structure.
- Database schema changes are allowed only when they preserve the Neon PostgreSQL
	connection and the existing migration history.
- Automated tests are not mandatory for routine changes in this repository.
	If tests are requested later, they must target the affected behavior only.
- Validation MUST prioritize running the app, checking key pages, and confirming
	templates, forms, and authentication flows still work.

## Development Workflow

- Prefer Django-native solutions before introducing new abstractions.
- Reuse existing app modules and naming patterns rather than creating parallel
	systems.
- Keep template inheritance, form helpers, and admin integration consistent across
	`commex` and `website`.
- Any change that affects login, static assets, or the database must be reviewed
	for compatibility with the current deployment shape before merge.
- Document any deliberate deviation from these principles in the related plan or
	spec.

## Governance
This constitution supersedes informal preferences, local conventions, and ad hoc
patterns. Amendments require a documented reason, a version bump, and an update to
any dependent planning templates when the rules affect them. Versioning follows
semantic versioning: MAJOR for backward-incompatible governance changes, MINOR for
added or substantively expanded principles, and PATCH for clarifications or
wording fixes. Compliance is expected in every feature plan and implementation
review, with special attention to framework compatibility, deployment safety,
authentication, and storage preservation. If a requested change conflicts with
this constitution, the conflict must be called out explicitly before
implementation.

**Version**: 1.1.0 | **Ratified**: 2026-08-05 | **Last Amended**: 2026-08-07
