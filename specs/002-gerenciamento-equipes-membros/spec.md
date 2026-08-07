# Feature Specification: Gerenciamento de Equipes e Membros

**Feature Branch**: `002-gerenciamento-equipes-membros`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "Spec 002 — Gerenciamento de Equipes e Membros"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar equipe com membros e papéis em um único fluxo (Priority: P1)

Como usuário autorizado, quero criar uma equipe em um único formulário com nome, membros e papéis, para cadastrar rapidamente uma composição válida sem alternar entre telas separadas.

**Why this priority**: Este é o fluxo principal da feature e entrega o valor central do cadastro de equipes.

**Independent Test**: Um usuário consegue criar uma equipe válida com Scrum Master, Product Owner e pelo menos um Desenvolvedor, e a equipe aparece salva com a composição correta.

**Acceptance Scenarios**:

1. **Given** que o usuário está no formulário de nova equipe, **When** ele informa o nome da equipe e adiciona membros com papéis válidos, **Then** a equipe é criada com sucesso.
2. **Given** que o usuário cria uma equipe sem Scrum Master, **When** ele confirma o cadastro, **Then** o sistema bloqueia o salvamento e informa que a equipe precisa de exatamente um Scrum Master.
3. **Given** que o usuário cria uma equipe sem Product Owner, **When** ele confirma o cadastro, **Then** o sistema bloqueia o salvamento e informa que a equipe precisa de exatamente um Product Owner.
4. **Given** que o usuário cria uma equipe sem Desenvolvedor, **When** ele confirma o cadastro, **Then** o sistema bloqueia o salvamento e informa que a equipe precisa de pelo menos um Desenvolvedor.

---

### User Story 2 - Reutilizar e cadastrar alunos com apelidos GitHub (Priority: P2)

Como usuário autorizado, quero adicionar alunos já existentes ou criar novos alunos durante o cadastro da equipe, incluindo apelidos GitHub opcionais, para montar a equipe sem telas separadas de cadastro de aluno.

**Why this priority**: O cadastro implícito de alunos e a busca por apelidos são essenciais para completar o fluxo da equipe.

**Independent Test**: Um usuário consegue vincular um aluno já existente por nome ou apelido, criar um novo aluno no mesmo fluxo e impedir apelidos duplicados.

**Acceptance Scenarios**:

1. **Given** que um aluno já existe, **When** o usuário busca por nome ou apelido e o seleciona na composição da equipe, **Then** o aluno é reutilizado sem criar um novo cadastro.
2. **Given** que o aluno ainda não existe, **When** o usuário informa nome e opcionalmente um ou mais apelidos GitHub, **Then** o aluno é criado implicitamente e vinculado à equipe.
3. **Given** que o usuário tenta cadastrar um apelido GitHub já vinculado a outro aluno, **When** ele confirma o cadastro, **Then** o sistema bloqueia o salvamento e informa a duplicidade.

---

### User Story 3 - Editar equipe, listar membros e manter regras de cardinalidade (Priority: P3)

Como usuário autorizado, quero editar o nome da equipe, listar membros por papel e trocar ou remover integrantes com segurança, para manter a equipe consistente ao longo do tempo.

**Why this priority**: Depois da criação, a manutenção da composição precisa respeitar as regras de cardinalidade sem deixar a equipe em estado inválido.

**Independent Test**: Um usuário consegue editar a equipe, visualizar os membros agrupados por papel e executar trocas ou remoções respeitando as regras da composição.

**Acceptance Scenarios**:

1. **Given** que uma equipe já existe, **When** o usuário altera o nome e confirma a edição, **Then** a equipe é atualizada.
2. **Given** que a equipe possui membros distribuídos por papel, **When** o usuário visualiza os detalhes, **Then** os membros aparecem agrupados por Scrum Master, Product Owner e Desenvolvedor.
3. **Given** que o usuário aciona a troca do Scrum Master ou do Product Owner, **When** ele seleciona um novo membro para assumir o papel, **Then** a equipe permanece com exatamente um membro naquele papel durante a operação.
4. **Given** que a equipe possui apenas um Desenvolvedor, **When** o usuário tenta removê-lo pela ação padrão, **Then** o sistema bloqueia a remoção e informa que a equipe deve manter pelo menos um Desenvolvedor.

---

## Non-Goals

- Tela dedicada de cadastro ou listagem de alunos fora do contexto da equipe.
- Papéis adicionais além de Scrum Master, Product Owner e Desenvolvedor.
- Vínculo entre Equipe e Projeto.
- Histórico de troca de papel ao longo do tempo.
- Autenticação ou login do aluno no sistema.

### Edge Cases

- O mesmo aluno não pode ocupar mais de um papel dentro da mesma equipe.
- Nome de equipe duplicado deve ser bloqueado de forma case-insensitive.
- Um aluno pode participar de mais de uma equipe em papéis diferentes.
- Cadastrar um aluno sem apelidos GitHub é permitido.
- Dois alunos com o mesmo nome completo são permitidos, desde que os apelidos GitHub e os identificadores internos continuem distintos.
- A exclusão de uma equipe remove apenas os vínculos da equipe, mantendo alunos e apelidos para reuso.
- Trocar Scrum Master ou Product Owner pelo mesmo aluno que já ocupa outro papel na equipe deve ser bloqueado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema deve permitir criar uma equipe em um único formulário com nome obrigatório e único, e seus membros.
- **FR-002**: Ao adicionar um membro, o sistema deve permitir selecionar um aluno já existente por nome ou apelido, ou cadastrar um novo aluno no mesmo fluxo.
- **FR-003**: O sistema deve permitir criar um novo aluno com nome obrigatório e um ou mais apelidos GitHub opcionais.
- **FR-004**: O sistema deve impedir que um apelido GitHub já vinculado a outro aluno seja salvo em duplicidade.
- **FR-005**: O sistema deve exigir exatamente um Scrum Master, exatamente um Product Owner e pelo menos um Desenvolvedor para confirmar a criação de uma equipe.
- **FR-006**: O sistema deve impedir que o mesmo aluno assuma mais de um papel dentro da mesma equipe.
- **FR-007**: O sistema deve permitir trocar o Scrum Master ou o Product Owner por meio de uma ação dedicada de substituição sem deixar a equipe temporariamente sem esse papel.
- **FR-008**: O sistema deve impedir a remoção direta do único Scrum Master ou do único Product Owner fora da ação de substituição.
- **FR-009**: O sistema deve permitir adicionar ou remover Desenvolvedores livremente, desde que a equipe mantenha ao menos um Desenvolvedor após a remoção.
- **FR-010**: O sistema deve permitir editar o nome da equipe e sua composição, respeitando as regras de cardinalidade e unicidade definidas nesta spec.
- **FR-011**: O sistema deve permitir listar os membros de uma equipe agrupados por papel.
- **FR-012**: O sistema deve permitir buscar um aluno a partir de qualquer apelido GitHub cadastrado.
- **FR-013**: O sistema deve remover os vínculos da equipe ao excluir a equipe, preservando alunos e apelidos para reuso futuro.

### Key Entities *(include if feature involves data)*

- **Aluno**: Representa a pessoa cadastrada implicitamente durante a composição da equipe, com nome e possíveis apelidos GitHub.
- **ApelidoGithub**: Representa um nickname GitHub vinculado a um aluno, com unicidade global.
- **Equipe**: Representa o grupo acadêmico cadastrado, com nome único e composição por membros.
- **MembroEquipe**: Representa o vínculo entre aluno e equipe, com o papel desempenhado pelo aluno naquela equipe.
- **Papel**: Representa a função de um membro na equipe: Scrum Master, Product Owner ou Desenvolvedor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem criar uma equipe válida com seus membros e papéis em menos de 3 minutos na primeira tentativa.
- **SC-002**: 100% das tentativas de salvar uma equipe sem Scrum Master, sem Product Owner ou sem Desenvolvedor são bloqueadas com mensagem clara.
- **SC-003**: 100% das tentativas de salvar apelidos GitHub duplicados são bloqueadas.
- **SC-004**: Usuários conseguem localizar um aluno por nome ou apelido GitHub sem precisar de uma tela separada de cadastro de aluno.
- **SC-005**: Usuários conseguem trocar Scrum Master ou Product Owner sem deixar a equipe em estado inválido durante a operação.
- **SC-006**: A listagem detalhada de uma equipe mostra a composição por papel de forma clara e consistente em 100% das consultas.

## Assumptions

- O usuário que administra as equipes já possui acesso autenticado ao sistema.
- O cadastro de aluno é implícito e vinculado ao fluxo de criação ou edição da equipe.
- O nome do aluno não precisa ser único; apelidos GitHub e identificadores internos resolvem a distinção.
- A exclusão de equipe não remove alunos nem apelidos, apenas os vínculos da equipe.
- A aplicação continua usando o stack atual de Django com templates server-rendered e as bibliotecas já presentes no projeto.
