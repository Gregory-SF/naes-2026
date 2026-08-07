# Contracts: Authentication Endpoints

## Overview

Contratos funcionais de interface para login, logout e alteracao de senha
no contexto de aplicacao web server-rendered com Django.

## 1. Login

- Route: `/accounts/login/`
- Method: `GET`, `POST`
- Access: Publico
- Input (POST):
  - `username` (obrigatorio)
  - `password` (obrigatorio)
  - `next` (opcional)
- Success behavior:
  - Credenciais validas autenticam sessao
  - Redireciona para `next` valido ou para rota padrao pos-login
- Error behavior:
  - Credenciais invalidas retornam mensagem generica sem revelar campo incorreto

## 2. Logout

- Route: `/accounts/logout/`
- Method: `POST` (preferencial no fluxo de UI)
- Access: Requer usuario autenticado
- Input: sem payload funcional adicional
- Success behavior:
  - Sessao encerrada
  - Redireciona para pagina publica configurada
- Error behavior:
  - Usuario anonimo deve ser redirecionado conforme politica de acesso (ex.: login)

## 3. Alteracao de senha

- Route: `/accounts/password_change/`
- Method: `GET`, `POST`
- Access: Requer usuario autenticado
- Input (POST):
  - `old_password` (obrigatorio)
  - `new_password1` (obrigatorio)
  - `new_password2` (obrigatorio)
- Validation rules:
  - `old_password` deve corresponder a senha do usuario autenticado
  - `new_password1` deve cumprir `AUTH_PASSWORD_VALIDATORS`
  - `new_password2` deve coincidir com `new_password1`
- Success behavior:
  - Senha do usuario atualizada
  - Usuario recebe confirmacao de sucesso
- Error behavior:
  - Campos invalidos retornam erros de formulario sem alterar senha

## Security Guarantees

- Mensagem de login invalido nao distingue usuario inexistente de senha incorreta
- Rotas protegidas redirecionam anonimos para login com preservacao de retorno via `next` quando aplicavel
- Sem provedores externos/OAuth nesta feature
