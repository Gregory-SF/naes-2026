# Feature Specification: Autenticação de Usuário

**Feature Branch**: `006-autenticacao-usuario`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Crie uma spec para a funcionalidade de Autenticação de Usuário do sistema"

## Feature

Autenticação de Usuário do sistema com login, logout e alteração de senha para usuários autenticados.

## Descrição

Esta feature define o fluxo de autenticação local do sistema para permitir acesso seguro às áreas protegidas, encerramento de sessão e atualização da própria senha. O comportamento deve preservar segurança básica contra enumeração de usuários em falha de login, respeitar redirecionamento por `next` após autenticação e garantir validação da senha atual e das regras mínimas de senha na alteração.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticar com usuário e senha (Priority: P1)

Como usuário do sistema, quero informar minhas credenciais em uma tela de login para acessar áreas protegidas com segurança.

**Why this priority**: Sem login funcional, não há acesso controlado ao sistema.

**Independent Test**: Acessar a URL de login, autenticar com credenciais válidas e confirmar redirecionamento correto; tentar credenciais inválidas e validar mensagem genérica.

---

### User Story 2 - Encerrar sessão autenticada (Priority: P2)

Como usuário autenticado, quero encerrar minha sessão para evitar uso indevido da minha conta.

**Why this priority**: Logout reduz risco de sessão ativa indevida em ambiente compartilhado.

**Independent Test**: Acionar a URL de logout e confirmar que a sessão foi encerrada e o usuário foi redirecionado para página pública.

---

### User Story 3 - Alterar a própria senha com validações (Priority: P3)

Como usuário autenticado, quero alterar minha senha informando a senha atual e a nova senha para manter a conta segura.

**Why this priority**: Mudança de senha é essencial para manutenção de segurança da conta.

**Independent Test**: Acessar tela de alteração autenticado, informar senha atual correta e nova senha válida, confirmar atualização; validar bloqueio para senha atual incorreta e para nova senha fora dos validadores.

---

## Non-Goals

- Cadastro público de novos usuários.
- Recuperação de senha por e-mail ("esqueci minha senha").
- Autenticação por provedores externos (OAuth, GitHub login ou similares).

## Entidades envolvidas

- **Usuário (User)**: conta autenticável existente no sistema, com credenciais de acesso.
- **Sessão autenticada**: estado de autenticação do usuário durante navegação.
- **Credenciais de login**: par usuário/senha informado na autenticação.
- **Solicitação de troca de senha**: operação composta por senha atual, nova senha e confirmação.

## Requirements *(mandatory)*

### Requisitos Funcionais (RF)

- **RF-001**: O sistema DEVE disponibilizar uma URL pública de login com formulário de usuário e senha.
- **RF-002**: O sistema DEVE autenticar o usuário quando credenciais válidas forem informadas.
- **RF-003**: Em falha de autenticação, o sistema DEVE exibir mensagem genérica sem indicar se erro foi no usuário ou na senha.
- **RF-004**: Após login bem-sucedido, o sistema DEVE redirecionar para o parâmetro `next` quando presente e válido.
- **RF-005**: Na ausência de `next`, o sistema DEVE redirecionar para página inicial definida para usuários autenticados.
- **RF-006**: O sistema DEVE disponibilizar URL de logout para encerrar sessão autenticada.
- **RF-007**: Após logout, o sistema DEVE redirecionar para página pública definida (home pública ou login).
- **RF-008**: O sistema DEVE disponibilizar URL/tela de alteração de senha acessível apenas por usuário autenticado.
- **RF-009**: A alteração de senha DEVE exigir senha atual, nova senha e confirmação da nova senha.
- **RF-010**: O sistema DEVE validar que a senha atual informada corresponde à senha do usuário autenticado.
- **RF-011**: O sistema DEVE validar a nova senha com os validadores padrão de segurança já configurados no projeto.
- **RF-012**: O sistema DEVE impedir alteração quando confirmação da nova senha divergir.
- **RF-013**: Em alteração de senha bem-sucedida, o sistema DEVE exibir confirmação clara ao usuário.
- **RF-014**: O sistema DEVE negar acesso às telas protegidas para usuários não autenticados e redirecionar ao login preservando a intenção de retorno via `next`.
- **RF-015**: O sistema DEVE manter login, logout e alteração de senha compatíveis com navegação por templates dinâmicos, exibindo ações conforme estado de autenticação.

### Critérios de Aceite em Gherkin

1. **Login com sucesso e redirecionamento por next**
   - **Dado** que o usuário não está autenticado e tenta acessar uma página protegida
   - **Quando** ele é redirecionado ao login, informa credenciais válidas e envia o formulário
   - **Então** o sistema autentica o usuário e o redireciona para a página originalmente solicitada

2. **Falha de login com mensagem genérica**
   - **Dado** que o usuário acessa a página de login
   - **Quando** informa credenciais inválidas
   - **Então** o sistema mantém o usuário não autenticado e exibe mensagem genérica de credenciais inválidas

3. **Logout com redirecionamento público**
   - **Dado** que o usuário está autenticado
   - **Quando** aciona a URL de logout
   - **Então** a sessão é encerrada e o usuário é redirecionado para uma página pública

4. **Alteração de senha com validação da senha atual**
   - **Dado** que o usuário está autenticado na tela de alteração de senha
   - **Quando** informa senha atual incorreta e tenta salvar
   - **Então** o sistema rejeita a alteração e informa erro sem alterar a senha

5. **Alteração de senha com validadores padrão**
   - **Dado** que o usuário está autenticado na tela de alteração de senha
   - **Quando** informa senha atual correta e nova senha que viola critério mínimo
   - **Então** o sistema rejeita a alteração e apresenta os erros de validação aplicáveis

6. **Alteração de senha com sucesso**
   - **Dado** que o usuário está autenticado na tela de alteração de senha
   - **Quando** informa senha atual correta, nova senha válida e confirmação correspondente
   - **Então** o sistema altera a senha e exibe mensagem de sucesso

### Casos de Borda

| Caso | Condição | Resultado Esperado |
|------|----------|--------------------|
| CB-001 | `next` ausente no login | Redirecionar para página inicial autenticada |
| CB-002 | `next` informado para rota inválida | Ignorar destino inválido e usar redirecionamento seguro padrão |
| CB-003 | Usuário autenticado acessa tela de login | Exibir comportamento consistente definido para usuários logados (ex.: redirecionar para home autenticada) |
| CB-004 | Sessão expirada durante tentativa de alteração de senha | Requerer novo login antes de concluir alteração |
| CB-005 | Nova senha igual à senha atual e bloqueada por política configurada | Rejeitar alteração com mensagem de validação apropriada |
| CB-006 | Confirmação de senha não confere | Rejeitar alteração e solicitar correção |

### Requisitos Não-Funcionais (RNF)

- **RNF-001 (Segurança)**: Mensagens de erro de login não devem permitir enumeração de usuários.
- **RNF-002 (Segurança)**: Endpoints/telas de alteração de senha devem ser acessíveis somente com sessão autenticada ativa.
- **RNF-003 (Usabilidade)**: Fluxo de login e alteração de senha deve informar erros de forma clara e orientada à correção.
- **RNF-004 (Compatibilidade)**: Funcionalidade deve operar dentro do stack atual de Django e templates server-rendered do projeto.
- **RNF-005 (Navegação)**: Redirecionamentos pós-login e pós-logout devem ser previsíveis e consistentes com a navegação pública/protegida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos usuários de teste com credenciais válidas conseguem autenticar com sucesso.
- **SC-002**: 100% das tentativas com credenciais inválidas retornam mensagem genérica sem detalhar qual campo falhou.
- **SC-003**: 100% dos acessos não autenticados a páginas protegidas são redirecionados ao login com preservação da intenção de retorno quando aplicável.
- **SC-004**: 100% das tentativas de alteração de senha com senha atual incorreta são bloqueadas.
- **SC-005**: 100% das tentativas de alteração de senha com nova senha válida e confirmação correta são concluídas com sucesso.

## Assumptions

- Usuários já existem no sistema (via admin ou outra spec) e possuem credenciais válidas.
- Política de validadores de senha padrão do Django está configurada no ambiente atual do projeto.
- A página pública de destino após logout será definida como home pública ou tela de login, conforme configuração do projeto.
- Não haverá fluxo de recuperação de senha por e-mail nesta entrega.

## Access, Ownership, and Listing Constraints *(mandatory)*

- **Acesso autenticado por jornada**: login é público; logout e alteração de senha exigem usuário autenticado.
- **Autorização por grupo**: não há regra de grupo nesta feature; sem uso obrigatório de grupos para os fluxos definidos.
- **Isolamento por proprietário**: não há modelo novo de dados de domínio com FK para `User` nesta spec; o escopo é autenticação de conta já existente.
- **Listagens/paginação**: esta feature não inclui ListView de entidades de negócio, portanto não há paginação aplicável neste escopo.
