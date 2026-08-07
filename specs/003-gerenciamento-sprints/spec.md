# Feature Specification: Gerenciamento de Sprints

**Feature Branch**: `003-gerenciamento-sprints`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "Spec 003 — Gerenciamento de Sprints"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar sprint com vínculo automático aos projetos existentes (Priority: P1)

Como usuário autorizado, quero criar uma sprint com nome, datas e descrição, já vinculada aos projetos existentes, para registrar rapidamente uma nova iteração sem perder a associação com o portfólio atual.

**Why this priority**: Este é o fluxo central da feature e entrega o valor principal do cadastro de sprint.

**Independent Test**: Um usuário consegue criar uma sprint válida, confirma que ela já nasce vinculada aos projetos existentes e a visualiza na listagem.

**Acceptance Scenarios**:

1. **Given** que existem projetos cadastrados, **When** o usuário cria uma sprint com nome, data de início, data final e descrição opcional, **Then** a sprint é criada e vinculada aos projetos existentes.
2. **Given** que o usuário informa data final anterior à data de início, **When** ele confirma a criação, **Then** o sistema bloqueia o salvamento e informa que a data final deve ser posterior à data de início.
3. **Given** que não existem projetos cadastrados, **When** o usuário cria uma sprint, **Then** a sprint é criada sem vínculos iniciais e pode ser ajustada posteriormente.
4. **Given** que o usuário cria uma sprint com datas iguais, **When** ele confirma a criação, **Then** o sistema aceita a sprint como válida de um dia.

---

### User Story 2 - Editar sprint e ajustar os projetos vinculados (Priority: P2)

Como usuário autorizado, quero editar uma sprint e marcar ou desmarcar os projetos aos quais ela se aplica, para manter o vínculo atualizado ao longo do tempo.

**Why this priority**: A manutenção dos vínculos é essencial depois da criação inicial da sprint.

**Independent Test**: Um usuário consegue abrir uma sprint existente, alterar seus dados e modificar a lista de projetos vinculados sem quebrar os vínculos já salvos.

**Acceptance Scenarios**:

1. **Given** que uma sprint já existe, **When** o usuário altera o nome, as datas ou a descrição e salva, **Then** a sprint é atualizada.
2. **Given** que a sprint está vinculada a vários projetos, **When** o usuário desmarca um projeto no dropdown e salva, **Then** a sprint deixa de se aplicar a esse projeto.
3. **Given** que a sprint possui poucos projetos vinculados, **When** o usuário marca novamente um projeto antes desmarcado e salva, **Then** o vínculo é restabelecido.
4. **Given** que o usuário desmarca todos os projetos, **When** ele salva a edição, **Then** a sprint permanece sem vínculos ativos.

---

### User Story 3 - Listar e consultar sprints por projeto e período (Priority: P3)

Como usuário autorizado, quero listar sprints com filtros por projeto e intervalo de datas e consultar seus vínculos, para localizar rapidamente a sprint correta e entender sua aplicação.

**Why this priority**: A listagem e a consulta dão visibilidade operacional ao calendário de sprints sem depender da edição.

**Independent Test**: Um usuário consegue filtrar a lista por projeto e por datas, abrir uma sprint e ver quais projetos estão vinculados a ela.

**Acceptance Scenarios**:

1. **Given** que existem sprints cadastradas, **When** o usuário filtra por projeto, **Then** apenas as sprints associadas ao projeto selecionado são exibidas.
2. **Given** que existem sprints cadastradas, **When** o usuário filtra por intervalo de datas, **Then** apenas as sprints dentro do intervalo são exibidas.
3. **Given** que o usuário abre o detalhe de uma sprint, **When** a página é carregada, **Then** os projetos vinculados a essa sprint são exibidos.
4. **Given** que o usuário exclui uma sprint, **When** a exclusão é confirmada, **Then** a sprint deixa de existir e nenhum projeto continua apontando para ela.

---

## Non-Goals

- Vínculo automático de sprint a novos projetos criados depois da sprint.
- Sobreposição ou conflito de datas entre sprints.
- Controle de permissões granular por sprint.
- Auditoria histórica de alterações de vínculo.

### Edge Cases

- Se não houver projetos cadastrados, a sprint pode ser criada sem vínculos iniciais.
- Data de início igual à data final deve ser aceita.
- Desmarcar todos os projetos ao editar uma sprint deve ser permitido.
- Nome de sprint duplicado é permitido, desde que o vínculo e as datas permaneçam corretos.
- Excluir um projeto deve remover automaticamente seu vínculo com as sprints.
- Re-marcação de um projeto previamente desmarcado deve ser idempotente e reversível.
- Uma sprint sem projetos vinculados continua válida e editável.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema deve permitir criar uma sprint com nome obrigatório, data de início obrigatória, data final obrigatória e descrição opcional.
- **FR-002**: O sistema deve validar que a data final seja posterior ou igual à data de início.
- **FR-003**: Ao criar uma sprint, o sistema deve vinculá-la automaticamente a todos os projetos existentes no momento da criação.
- **FR-004**: O sistema deve exibir, no formulário de criação e edição da sprint, todos os projetos existentes pré-selecionados para permitir marcar ou desmarcar os vínculos.
- **FR-005**: O sistema deve permitir editar nome, datas, descrição e projetos vinculados de uma sprint já existente.
- **FR-006**: O sistema deve permitir excluir uma sprint e remover todos os vínculos com projetos.
- **FR-007**: O sistema deve permitir listar sprints com filtro por projeto e por intervalo de datas.
- **FR-008**: O sistema deve permitir visualizar, no detalhe da sprint, todos os projetos atualmente vinculados a ela.
- **FR-009**: O sistema deve remover os vínculos de sprint ao excluir um projeto, sem deixar referências órfãs.
- **FR-010**: O sistema deve manter a alteração de vínculos entre sprint e projetos como uma operação reversível ao editar a sprint.

### Key Entities *(include if feature involves data)*

- **Sprint**: Representa uma iteração planejada, com nome, datas, descrição e status de vínculo com projetos.
- **Projeto**: Representa um projeto existente no sistema que pode ser associado a uma ou mais sprints.
- **SprintProjeto**: Representa o vínculo entre sprint e projeto, armazenando quais projetos estão aplicados a uma sprint específica.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem criar uma sprint válida e vinculá-la aos projetos existentes em menos de 3 minutos na primeira tentativa.
- **SC-002**: 100% das tentativas de salvar sprint com data final anterior à data de início são bloqueadas com mensagem clara.
- **SC-003**: A listagem de sprints permite encontrar uma sprint por projeto ou por período sem depender da edição manual.
- **SC-004**: Usuários conseguem revisar os projetos vinculados a uma sprint em uma única tela de detalhe.
- **SC-005**: A exclusão de sprint remove todos os vínculos com projetos em todos os casos verificados.
- **SC-006**: Pelo menos 90% dos usuários de teste conseguem criar, editar, filtrar e consultar sprints sem assistência adicional.

## Assumptions

- O usuário que administra sprints já possui acesso autenticado ao sistema.
- A sprint pode ser criada mesmo quando não houver projetos cadastrados, desde que a edição futura permita ajustar vínculos.
- A sprint usa o conjunto atual de projetos do sistema como base de vínculo.
- A aplicação continua usando o stack atual de Django com templates server-rendered e as bibliotecas já presentes no projeto.
- A exclusão de projeto remove apenas o vínculo com sprints, não a própria sprint.
