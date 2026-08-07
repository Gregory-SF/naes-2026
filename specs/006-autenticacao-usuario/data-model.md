# Data Model: Autenticacao de Usuario

## Overview

Esta feature nao introduz novas tabelas de dominio nem novas migracoes.
Ela reutiliza entidades nativas do Django para autenticacao e sessao.

## Entidades logicas envolvidas

### 1. User (Django auth)

- Origem: `django.contrib.auth.models.User`
- Responsabilidade: identidade autenticavel (username/senha) do sistema
- Campos usados no escopo: `username`, hash de senha e metadados de autenticacao
- Regras relevantes:
  - Deve existir previamente (cadastro publico fora de escopo)
  - Senha deve obedecer validadores configurados em `AUTH_PASSWORD_VALIDATORS`

### 2. Session (Django sessions)

- Origem: backend de sessao do Django
- Responsabilidade: manter estado autenticado apos login e invalidar no logout
- Regras relevantes:
  - Logout encerra sessao autenticada vigente
  - Acesso a rotas protegidas sem sessao valida redireciona para login

### 3. Password Change Request (entidade de processo)

- Origem: formulario de alteracao de senha
- Campos de processo: senha atual, nova senha, confirmacao
- Regras relevantes:
  - Senha atual deve corresponder ao usuario autenticado
  - Nova senha deve passar nos validadores padrao
  - Confirmacao deve ser identica a nova senha

## Relacionamentos

- `User` -> `Session`: 1:N logico (um usuario pode ter sessoes em multiplos contextos)
- Nenhum novo relacionamento de dominio com `ForeignKey` para `User` e criado por esta feature

## Impacto de schema

- Nenhuma alteracao de schema planejada
- Nenhuma migration nova requerida

## Owner Isolation Assessment (Constitution)

- Regra de isolamento por owner em CRUD nao se aplica neste escopo, pois nao ha
  modelo novo com `ForeignKey` para `User` e nao ha CRUD de entidade de dominio.
