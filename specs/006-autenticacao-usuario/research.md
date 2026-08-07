# Research: Autenticacao de Usuario

## Decision 1: Reutilizar views/forms nativos do Django auth

- Decision: Usar `LoginView`, `LogoutView` e `PasswordChangeView` com formularios nativos (`AuthenticationForm` e `PasswordChangeForm`) como base do fluxo.
- Rationale: Reduz risco de implementacao insegura, respeita validadores configurados e aproveita comportamento consolidado do framework.
- Alternatives considered:
  - Implementar views/forms custom do zero: descartado por aumentar superficie de erro de seguranca.
  - Bibliotecas externas de auth: descartado por nao serem necessarias para o escopo e por contrariar simplicidade da feature.

## Decision 2: Tratar erro de login com mensagem generica

- Decision: Em credenciais invalidas, exibir mensagem unica sem diferenciar usuario inexistente de senha incorreta.
- Rationale: Mitiga enumeracao de usuarios e atende diretamente ao requisito funcional de seguranca.
- Alternatives considered:
  - Mensagens especificas por campo: rejeitado por facilitar enumeracao.
  - Suprimir mensagem de erro: rejeitado por piorar usabilidade.

## Decision 3: Redirecionamento pos-login via `next` com fallback seguro

- Decision: Priorizar redirecionamento para `next` quando valido e, caso ausente/invalido, usar `LOGIN_REDIRECT_URL`.
- Rationale: Preserva jornada do usuario apos tentativa de acesso a rota protegida.
- Alternatives considered:
  - Ignorar `next` sempre: rejeitado por quebrar fluxo esperado.
  - Aceitar qualquer URL externa em `next`: rejeitado por risco de open redirect.

## Decision 4: Escopo sem modelo de dominio owner-based

- Decision: Registrar explicitamente que a feature nao cria CRUD de entidade com `ForeignKey` para `User`.
- Rationale: O escopo e autenticacao de conta existente e sessao, nao gerenciamento de dados de dominio por proprietario.
- Alternatives considered:
  - Criar modelo proprio para credenciais/sessao: rejeitado por duplicar mecanismos nativos do Django sem necessidade.

## Decision 5: Paginacao e otimizacao de query nao aplicaveis ao escopo

- Decision: Declarar inexistencia de ListView de negocio e ausencia de querysets relacionais novos para essa feature.
- Rationale: Os fluxos sao formulario de login/logout/troca de senha, sem listagem de registros de dominio.
- Alternatives considered:
  - Forcar ListView apenas para cumprir regra: rejeitado por nao ter valor de negocio.

## Decision 6: Templates com condicional de autenticacao

- Decision: Aplicar `request.user.is_authenticated` na navegacao global para alternar entradas como `Entrar`, `Sair` e links protegidos.
- Rationale: Atende principle constitucional de nao exibir acoes que usuario anonimo nao pode executar.
- Alternatives considered:
  - Deixar sempre visivel e bloquear so no backend: rejeitado por UX inconsistente e sinalizacao indevida de acoes.
