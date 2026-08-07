# Implementation Plan: Autenticacao de Usuario

**Branch**: `006-autenticacao-usuario` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Implementar os fluxos de autenticacao local com login, logout e alteracao de senha
usando componentes nativos do Django auth, com redirecionamento por `next`,
mensagens seguras contra enumeracao de usuario e validadores padrao de senha.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: Django 5.2.x (`django.contrib.auth`, `django.contrib.sessions`, templates)
**Storage**: PostgreSQL (Neon), sem novas tabelas de dominio nesta feature
**Testing**: Nao obrigatorio; validacao manual orientada por quickstart
**Target Platform**: Aplicacao web Django server-rendered
**Project Type**: Monolito Django
**Performance Goals**: p95 de autenticacao interativa sem regressao perceptivel para usuario final
**Constraints**: manter stack atual, sem OAuth, sem cadastro publico, sem recuperacao por email
**Scale/Scope**: login/logout/alteracao de senha para usuarios existentes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Access Scope Gate: PASS
  - Login: nao exige `LoginRequiredMixin` nem `GroupRequiredMixin` (rota publica por regra de negocio).
  - Logout: exige usuario autenticado (`LoginRequiredMixin` em view customizada ou uso de `@login_required` equivalente).
  - Alteracao de senha: exige usuario autenticado (`LoginRequiredMixin`), sem grupo.
  - Group-based authorization: nao aplicavel nesta feature.
- Owner Isolation Gate: PASS
  - Nenhum model novo da feature possui `ForeignKey` para `User`.
  - Feature opera sobre conta autenticada corrente (`request.user`) e formularios de auth nativos.
  - Regra de isolamento CRUD por owner fica explicitamente marcada como nao aplicavel ao escopo.
- Query Performance Gate: PASS
  - Fluxos de auth desta feature nao possuem ListView/DetailView de entidades com FK/M2M renderizadas em template.
  - Nao ha queryset relacional novo exigindo `select_related`/`prefetch_related` nesta feature.
- Pagination Gate: PASS
  - Nao existe ListView de negocio no escopo da feature.
  - Excecao aplicada por inexistencia de tela de listagem nesta entrega.
- Query Reuse Gate: PASS
  - Nao ha query compartilhada nova entre multiplas views no escopo de autenticacao.
- Dev Validation Gate: PASS
  - Validar com Django Debug Toolbar ativo em desenvolvimento para garantir ausencia de regressao acidental em queries.
  - Confirmar toolbar desativada em producao.

## Decisoes Explicitas de Acesso e Consulta (Constitution 1.1.0)

### 1) Matriz de acesso por view desta feature

| View da feature | Tipo funcional | LoginRequiredMixin | GroupRequiredMixin | Justificativa de negocio |
|---|---|---|---|---|
| LoginView (`/accounts/login/`) | Autenticacao | Nao | Nao | Rota precisa ser publica para usuarios anonimos conseguirem entrar |
| LogoutView (`/accounts/logout/`) | Encerramento de sessao | Sim | Nao | Apenas usuario autenticado possui sessao para encerrar |
| PasswordChangeView (`/accounts/password_change/`) | Atualizacao da propria credencial | Sim | Nao | Alteracao de senha e acao sensivel restrita ao dono da sessao |

Observacao sobre CRUD (Create/Update/Delete/List/Detail): esta feature nao introduz CRUD de entidade de dominio.

### 2) Isolamento por usuario (FK para User)

- Verificacao de modelo: nao ha novo model de dominio nesta feature com `ForeignKey` para `User`.
- Conclusao: o padrao `form_valid()` para atribuicao de owner e `get_queryset()` para isolamento CRUD nao se aplica neste escopo.
- Registro explicito de conformidade: qualquer extensao futura da feature que introduza entidade com owner deve adotar integralmente o padrao da constitution.

### 3) Paginacao de ListView

- Nao ha ListView de negocio nesta feature.
- Portanto, `paginate_by` nao se aplica aqui por ausencia de listagem de registros.

### 4) Templates que devem usar `request.user.is_authenticated`

- `commex/templates/commex/base.html`
  - Exibir `Entrar` quando anonimo.
  - Exibir `Sair` e acoes protegidas quando autenticado.
- `templates/registration/login.html`
  - Opcionalmente redirecionar/ocultar formulario para usuario ja autenticado para evitar fluxo redundante.
- Templates de navegacao global que contenham botoes de acao protegida
  - Garantir que links para alteracao de senha/logout aparecam apenas para usuario autenticado.

### 5) Querysets com relacoes exibidas em template

- Nesta feature, nao ha queryset novo de dominio com FK/M2M exibido em templates.
- Consequencia: nao existe exigencia de `select_related`/`prefetch_related` nova no escopo de autenticacao.

## Project Structure

### Documentation (this feature)

```text
specs/006-autenticacao-usuario/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── auth-endpoints.md
└── tasks.md
```

### Source Code (repository root)

```text
naes2026/
├── settings.py
└── urls.py

commex/
├── templates/commex/base.html
└── views.py

templates/
└── registration/
   └── login.html
```

**Structure Decision**: Aplicar implementacao dentro do monolito Django existente,
reutilizando `django.contrib.auth.urls`, templates atuais e configuracoes em
`naes2026/settings.py`.

## Phase 0: Outline & Research

1. Confirmar uso de views/forms nativos (`LoginView`, `LogoutView`, `PasswordChangeView`, `PasswordChangeForm`).
2. Definir politica de erro de login sem enumeracao de usuario.
3. Confirmar politica de redirecionamento por `next` e fallback seguro.
4. Confirmar que nao ha CRUD com owner nesta feature e registrar explicitamente no plano.

## Phase 1: Design & Contracts

1. `data-model.md`: registrar entidades logicas sem nova migracao de schema.
2. `contracts/auth-endpoints.md`: mapear URLs, metodos, parametros e comportamento esperado.
3. `quickstart.md`: validacao manual de login, logout e alteracao de senha.
4. Atualizacao de contexto do agente: script dedicado nao identificado em `.specify/scripts/powershell`; manter sincronizacao via artefatos gerados.

## Post-Design Constitution Check

- Access Scope Gate: PASS (matriz de mixins declarada e justificada)
- Owner Isolation Gate: PASS (nao aplicavel e explicitamente documentado)
- Pagination Gate: PASS (sem ListView no escopo)
- Template Auth Gate: PASS (templates-alvo identificados)
- Query Performance Gate: PASS (sem queryset relacional novo na feature)

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Nenhuma | N/A | N/A |

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, contracts e quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`
