# Feature Specification: Gerenciamento de Projetos

**Feature Branch**: `001-gerenciamento-projetos`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "Spec 001 — Gerenciamento de Projetos"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar e listar projeto com GitHub validado (Priority: P1)

Como Product Owner ou Desenvolvedor, quero cadastrar um projeto acadêmico com nome, link da organização/conta GitHub e ao menos um repositório vinculado, para registrar a base do projeto e consultá-lo depois.

**Why this priority**: Este é o fluxo central da feature e entrega o valor principal para o usuário.

**Independent Test**: Um usuário autenticado consegue criar um projeto com dados válidos, vê o projeto na listagem e consegue abrir seus detalhes com a organização e os repositórios vinculados.

**Acceptance Scenarios**:

1. **Given** que o usuário está na tela de novo projeto, **When** ele informa um nome válido, um link válido de organização/conta GitHub e um ou mais repositórios válidos, **Then** o sistema salva o projeto e exibe-o na listagem.
2. **Given** que o usuário informa um link de GitHub inválido ou inexistente, **When** ele confirma o cadastro, **Then** o sistema bloqueia o salvamento e exibe uma mensagem clara de erro.
3. **Given** que o usuário informa um repositório que não pertence ao mesmo contexto GitHub do projeto, **When** ele confirma o cadastro, **Then** o sistema bloqueia a associação e orienta o usuário sobre o problema.

---

### User Story 2 - Editar e manter repositórios vinculados (Priority: P2)

Como Product Owner ou Desenvolvedor, quero editar um projeto e adicionar ou remover repositórios vinculados, para manter o cadastro atualizado sem recriar o projeto.

**Why this priority**: A manutenção do cadastro é essencial depois da criação inicial e evita retrabalho.

**Independent Test**: Um usuário autenticado consegue editar nome e link do projeto, adicionar novos repositórios, remover repositórios existentes e confirmar a persistência das mudanças.

**Acceptance Scenarios**:

1. **Given** que um projeto já existe, **When** o usuário altera o nome ou o link da organização/conta GitHub e confirma a edição, **Then** o sistema salva as alterações.
2. **Given** que um projeto já existe, **When** o usuário adiciona um novo repositório válido, **Then** o projeto passa a exibir o novo repositório nos detalhes.
3. **Given** que um projeto já existe com repositórios vinculados, **When** o usuário remove um repositório, **Then** o projeto continua disponível e os demais vínculos permanecem intactos.
4. **Given** que o usuário tenta cadastrar dois repositórios com o mesmo link no mesmo projeto, **When** ele confirma a alteração, **Then** o sistema bloqueia a duplicidade.

---

### User Story 3 - Integrar projeto com sprints existentes (Priority: P3)

Como usuário autorizado, quero ajustar o vínculo de um projeto com sprints existentes na tela de edição do projeto, para manter a relação entre planejamento e execução sempre atualizada.

**Why this priority**: A integração com sprints amplia o cadastro de projeto sem alterar o fluxo principal de criação e edição de dados básicos.

**Independent Test**: Um usuário consegue abrir a edição de um projeto, ver todas as sprints existentes pré-marcadas conforme o vínculo atual e marcar ou desmarcar sprints sem afetar outras associações.

**Acceptance Scenarios**:

1. **Given** que existem sprints cadastradas, **When** o usuário abre a tela de edição de um projeto, **Then** o sistema exibe um dropdown com todas as sprints existentes pré-marcadas conforme o vínculo atual em SprintProjeto.
2. **Given** que o projeto estava desvinculado de uma sprint específica, **When** o usuário marca novamente essa sprint no dropdown e salva a edição, **Then** o vínculo correspondente é recriado em SprintProjeto.
3. **Given** que o usuário desmarca uma sprint já vinculada ao projeto, **When** ele salva a edição, **Then** o vínculo correspondente é removido sem excluir a sprint nem afetar seu vínculo com outros projetos.

---

### User Story 4 - Vincular branch ao repositório (Priority: P4)

Como usuário autorizado, quero informar o nome de uma branch junto com o repositório, para registrar a branch principal usada na organização do projeto sem precisar cadastrar dados adicionais da branch.

**Why this priority**: O vínculo por branch complementa o cadastro do repositório sem alterar o fluxo central de projeto, repositório e sprint.

**Independent Test**: Um usuário consegue adicionar ou editar um repositório informando apenas o nome da branch, e o sistema salva essa informação junto ao repositório correspondente.

**Acceptance Scenarios**:

1. **Given** que o usuário está adicionando ou editando um repositório de um projeto, **When** ele informa o nome de uma branch, **Then** o sistema salva a branch junto ao repositório correspondente.
2. **Given** que o usuário informa um nome de branch vazio, **When** ele confirma o salvamento, **Then** o sistema bloqueia a operação e informa que o nome da branch é obrigatório.
3. **Given** que o usuário edita o repositório e altera somente o nome da branch, **When** ele salva a alteração, **Then** o sistema atualiza apenas a branch e mantém os demais dados do repositório.

---

## Non-Goals

- Sincronização automática de dados do GitHub como commits, issues e pull requests.
- Gerenciamento completo do ciclo de vida de sprints (criação, listagem, filtros e governança), que pertence à Spec 003.
- Permissões granulares por repositório.
- Busca e cadastro estruturado de branches via API do GitHub; nesta spec, a branch permanece apenas como nome textual associado ao repositório.

### Edge Cases

- Link da organização pode representar uma organização ou uma conta individual do GitHub, desde que a conta exista e seja válida.
- Links de plataformas diferentes de GitHub devem ser rejeitados.
- Repositórios com owner diferente do projeto devem ser bloqueados.
- O sistema deve impedir duplicidade do mesmo link de repositório dentro do mesmo projeto.
- Se a validação do GitHub não puder ser concluída com segurança, o cadastro não deve ser finalizado.
- Cada repositório deve permitir o registro de um nome de branch principal informado apenas pelo nome, sem exigir metadados adicionais da branch.
- Se não houver sprints cadastradas, a edição de projeto deve exibir a seleção de sprints vazia e permitir salvar sem vínculos.
- O vínculo ou desvínculo de sprint pela edição de projeto não deve alterar os dados da sprint em si, apenas a associação SprintProjeto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema deve permitir criar um projeto com nome obrigatório.
- **FR-002**: O sistema deve permitir informar o link da organização ou conta GitHub do projeto como dado obrigatório.
- **FR-003**: O sistema deve validar se o link informado pertence ao GitHub e representa uma organização ou conta existente.
- **FR-004**: O sistema deve permitir associar um ou mais repositórios ao projeto durante a criação ou em edição posterior.
- **FR-005**: Cada repositório vinculado deve possuir nome obrigatório e link GitHub obrigatório.
- **FR-006**: O sistema deve validar se cada link de repositório pertence ao GitHub e representa um repositório existente.
- **FR-007**: O sistema deve impedir que um repositório seja associado a um projeto quando seu owner não corresponde ao contexto GitHub informado para o projeto.
- **FR-008**: O sistema deve permitir listar projetos cadastrados com acesso aos dados principais do projeto.
- **FR-009**: O sistema deve permitir editar nome do projeto, link da organização ou conta GitHub e repositórios vinculados.
- **FR-010**: O sistema deve permitir remover um repositório vinculado sem excluir o projeto.
- **FR-011**: O sistema deve permitir excluir um projeto com confirmação explícita do usuário.
- **FR-012**: O sistema deve exibir mensagens claras quando uma validação de link ou vínculo falhar.
- **FR-013**: Na tela de edição de um projeto, o sistema deve exibir um dropdown com todas as sprints existentes, pré-marcadas conforme o vínculo atual em SprintProjeto, permitindo ao usuário marcar ou desmarcar livremente as sprints às quais aquele projeto deve ou não pertencer.
- **FR-014**: Ao alterar o estado de uma sprint no dropdown da tela de edição de projeto, o sistema deve atualizar o vínculo correspondente em SprintProjeto sem excluir a sprint nem afetar seu vínculo com outros projetos.
- **FR-015**: O sistema deve permitir informar e salvar o nome de uma branch associado a cada repositório.
- **FR-016**: O sistema deve exigir que o nome da branch seja informado como texto simples, sem dados adicionais obrigatórios além do nome.
- **FR-017**: O sistema deve permitir editar apenas o nome da branch de um repositório sem alterar os demais dados do repositório.



### Key Entities *(include if feature involves data)*

- **Projeto**: Representa um projeto acadêmico cadastrado, com nome, link da organização ou conta GitHub, status e data de criação.
- **Repositório**: Representa um repositório vinculado a um projeto, com nome, link GitHub e vínculo com o projeto pai.
- **Branch**: Representa o nome da branch principal associada a um repositório, informada apenas como texto simples.
- **Sprint**: Representa uma sprint existente no sistema, usada como opção de vínculo na edição de projeto.
- **SprintProjeto**: Representa o vínculo entre sprint e projeto, refletindo as sprints às quais o projeto pertence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários autenticados conseguem concluir o cadastro de um projeto válido em menos de 3 minutos na primeira tentativa.
- **SC-002**: 100% dos links fora do GitHub são rejeitados com mensagem de erro compreensível.
- **SC-003**: Usuários conseguem adicionar ou remover repositórios vinculados sem perder os dados já salvos do projeto.
- **SC-004**: A seleção de projeto em outras telas mostra os projetos ativos corretamente e permite localizar um projeto pelo nome sem ambiguidade.
- **SC-005**: Pelo menos 90% dos usuários de teste conseguem criar, editar e consultar um projeto sem assistência adicional.
- **SC-006**: Usuários conseguem revisar e atualizar os vínculos de sprints de um projeto pela tela de edição sem perder vínculos já existentes com outros projetos.
- **SC-007**: Usuários conseguem registrar o nome de uma branch junto ao repositório sem precisar preencher dados adicionais de branch.
- **SC-008**: Usuários conseguem editar o nome da branch de um repositório sem afetar os demais dados do projeto.

## Assumptions

- O público-alvo desta feature já está autenticado no sistema ou acessa a área protegida por login.
- Links válidos podem apontar para contas individuais ou organizações do GitHub, desde que sejam reais e acessíveis.
- Os dados do projeto permanecem armazenados na base já configurada e os vínculos existentes devem continuar compatíveis com o histórico atual.
- A experiência visual e o comportamento dos formulários permanecem consistentes com o restante do sistema.
- A integração com sprints depende da Spec 003 e do vínculo SprintProjeto definido nela.
- O nome da branch é um campo textual simples associado ao repositório, sem estrutura adicional de metadados.
- A busca estruturada de branches e seu reuso como entidades separadas serão tratados na Spec 005.
