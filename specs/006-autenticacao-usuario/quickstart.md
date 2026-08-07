# Quickstart: Validacao da Feature de Autenticacao

## Prerequisitos

- Dependencias instaladas (`pip install -r requirements.txt`)
- Banco configurado e acessivel
- Ao menos um usuario existente no sistema (via admin)
- Ambiente de desenvolvimento com DEBUG ativo

## Subir aplicacao

```bash
python manage.py runserver
```

## Cenario 1: Login com sucesso

1. Acesse `/accounts/login/`
2. Informe credenciais validas
3. Clique em Entrar
4. Esperado:
   - Sessao autenticada criada
   - Redirecionamento para `next` (quando presente) ou para URL padrao pos-login

## Cenario 2: Login invalido com mensagem segura

1. Acesse `/accounts/login/`
2. Informe usuario/senha invalida
3. Envie formulario
4. Esperado:
   - Permanecer nao autenticado
   - Mensagem generica sem indicar se o erro foi no usuario ou na senha

## Cenario 3: Logout

1. Com usuario autenticado, acione logout
2. Esperado:
   - Sessao encerrada
   - Redirecionamento para a pagina publica de login

## Cenario 4: Alteracao de senha com sucesso

1. Com usuario autenticado, acesse URL de alteracao de senha
2. Informe senha atual correta
3. Informe nova senha valida + confirmacao
4. Envie formulario
5. Esperado:
   - Senha atualizada
   - Mensagem de sucesso exibida

## Cenario 5: Alteracao de senha com erro de validacao

1. Com usuario autenticado, informe senha atual incorreta
2. Informe nova senha qualquer
3. Esperado:
   - Alteracao bloqueada
   - Erro claro no formulario

4. Repita com senha atual correta e nova senha invalida (ex.: muito curta)
5. Esperado:
   - Alteracao bloqueada
   - Mensagens dos validadores padrao do Django

## Validacao de Constitution (desenvolvimento)

- Confirmar no template base que links de autenticacao usam condicional por `request.user.is_authenticated`
- Confirmar que a navegação autenticada exibe `Alterar senha` e `Sair`, enquanto usuarios anonimos veem apenas `Entrar`
- Confirmar no Django Debug Toolbar que o fluxo nao introduziu regressao de queries
- Confirmar que Debug Toolbar esta apenas em desenvolvimento
