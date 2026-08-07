# Feature Specification: Geração de Análise de Commits

**Feature Branch**: `005-geracao-analise-commits`

**Created**: 2026-08-07

**Status**: Draft

**Input**: User description: "Spec 005 — Geração de Análise de Commits (Importação via API do GitHub)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preparar a análise escolhendo projeto, repositório, branch e período (Priority: P1)

Como usuário autorizado, quero selecionar um projeto, um repositório vinculado, uma branch e um período de análise, para iniciar a importação de commits de forma consistente com a sprint escolhida ou com um intervalo manual.

**Why this priority**: Este é o fluxo central da feature e define a base da importação de commits.

**Independent Test**: Um usuário consegue escolher projeto, repositório, branch e período, e iniciar a execução de análise com status registrado.

**Acceptance Scenarios**:

1. **Given** que existem um projeto, um repositório vinculado e ao menos uma branch cadastrada, **When** o usuário seleciona esses dados e confirma o início da análise, **Then** o sistema cria uma nova execução de análise.
2. **Given** que o usuário escolhe uma sprint já cadastrada como período, **When** ele confirma o início da análise, **Then** o sistema usa automaticamente as datas de início e fim da sprint.
3. **Given** que o usuário informa manualmente um período válido, **When** ele confirma o início da análise, **Then** o sistema aceita o intervalo e inicia a busca de commits.
4. **Given** que o usuário informa data final anterior à data de início, **When** ele confirma a análise, **Then** o sistema bloqueia o salvamento e exibe erro de validação.

---

### User Story 2 - Buscar e cadastrar branches do repositório (Priority: P2)

Como usuário autorizado, quero buscar as branches existentes de um repositório e cadastrá-las para reutilização, para não depender de texto livre a cada nova análise.

**Why this priority**: A branch estruturada é um pré-requisito para análises futuras consistentes.

**Independent Test**: Um usuário consegue buscar branches do GitHub para um repositório, adicionar uma branch e impedir duplicidade no mesmo repositório.

**Acceptance Scenarios**:

1. **Given** que o repositório selecionado possui branches no GitHub, **When** o usuário aciona a busca de branches, **Then** o sistema lista as branches existentes.
2. **Given** que o usuário seleciona uma branch retornada pela busca, **When** ele confirma a adição, **Then** a branch é persistida vinculada ao repositório.
3. **Given** que a branch já foi adicionada ao repositório, **When** o usuário tenta adicioná-la novamente, **Then** o sistema bloqueia a duplicidade.
4. **Given** que o repositório não possui branches cadastradas localmente, **When** o usuário busca branches novamente, **Then** o sistema mantém a possibilidade de adicionar novas branches retornadas pela API.

---

### User Story 3 - Importar e persistir commits analisados (Priority: P3)

Como usuário autorizado, quero executar a importação de commits em um período definido, para registrar apenas os dados relevantes e associar os autores aos alunos quando possível.

**Why this priority**: A importação dos commits é o objetivo principal da análise e depende dos dados de branch, sprint e token.

**Independent Test**: Um usuário dispara uma análise e acompanha a execução até a conclusão, verificando os commits importados e suas associações.

**Acceptance Scenarios**:

1. **Given** que o token do GitHub está configurado e a branch foi selecionada, **When** o usuário inicia a análise, **Then** o sistema busca os commits do período informado e registra a execução.
2. **Given** que a API do GitHub retorna commits com muitos campos, **When** o sistema processa os dados, **Then** ele persiste apenas os campos relevantes definidos pela spec.
3. **Given** que o autor do commit possui um apelido GitHub cadastrado, **When** o commit é processado, **Then** o sistema associa o commit ao aluno correspondente.
4. **Given** que não existe aluno correspondente para o login do autor, **When** o commit é processado, **Then** o commit é salvo sem aluno associado.
5. **Given** que a mesma combinação de projeto, repositório, branch e período já foi analisada anteriormente, **When** o usuário dispara uma nova análise, **Then** o sistema cria uma nova execução independente.

---

## Non-Goals

- Exibição dos dados importados em dashboards, gráficos ou filtros de visualização.
- Busca e persistência de Pull Requests.
- Reprocessamento automático agendado.
- Análise de qualidade da mensagem de commit.
- Cálculo de novas HUs por dia.

### Edge Cases

- O token do GitHub ausente deve bloquear a busca de branches e o início da análise.
- Repositório sem branch cadastrada localmente não deve permitir iniciar a análise até haver ao menos uma branch persistida.
- Branch removida no GitHub deve gerar erro de execução, sem apagar o registro local da branch.
- Commit sem login de GitHub associado deve ser persistido sem aluno vinculado.
- Rate limit do GitHub deve pausar e retomar a busca sem falhar a execução isoladamente.
- Nenhum commit no período deve resultar em execução concluída com zero commits importados.
- Falhas de rede ou autenticação devem ser registradas na execução com status de erro e mensagem adequada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema deve permitir selecionar um projeto cadastrado como ponto de partida da análise.
- **FR-002**: O sistema deve permitir selecionar um repositório vinculado ao projeto escolhido.
- **FR-003**: O sistema deve permitir buscar as branches existentes do repositório selecionado.
- **FR-004**: O sistema deve permitir persistir uma ou mais branches retornadas como entidades reutilizáveis vinculadas ao repositório.
- **FR-005**: O sistema deve impedir a duplicidade de uma branch já adicionada ao mesmo repositório.
- **FR-006**: O sistema deve permitir selecionar, entre as branches já adicionadas, qual branch será usada na análise.
- **FR-007**: O sistema deve permitir selecionar o período da análise por sprint cadastrada ou por intervalo manual de datas.
- **FR-008**: O sistema deve validar que a data final é posterior ou igual à data de início.
- **FR-009**: O sistema deve usar o token do GitHub armazenado nas Configurações Globais para autenticar as chamadas à API do GitHub.
- **FR-010**: Na ausência de token configurado, o sistema deve bloquear a busca de branches e o início da análise.
- **FR-011**: O sistema deve consultar a API do GitHub para obter todos os commits da branch selecionada dentro do período escolhido.
- **FR-012**: O sistema deve tratar paginação da API do GitHub até obter todos os commits do período.
- **FR-013**: O sistema deve persistir apenas os dados relevantes de cada commit definidos nesta spec.
- **FR-014**: O sistema deve tentar associar automaticamente cada commit importado a um aluno cadastrado por meio do apelido GitHub do autor.
- **FR-015**: O sistema deve registrar uma execução de análise para cada busca disparada, com status de início, processamento, conclusão ou erro.
- **FR-016**: O sistema deve permitir acompanhar o status da execução em andamento.
- **FR-017**: O sistema deve permitir disparar novas execuções para o mesmo projeto, repositório, branch e período sem apagar execuções anteriores.
- **FR-018**: O sistema deve respeitar os limites de taxa da API do GitHub durante a busca.

### Key Entities *(include if feature involves data)*

- **Branch**: Representa uma branch persistida e reutilizável vinculada a um repositório.
- **ExecucaoAnalise**: Representa uma execução manual de importação de commits para um conjunto de parâmetros selecionados.
- **CommitAnalisado**: Representa um commit importado com apenas os campos relevantes persistidos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem iniciar uma análise válida em menos de 3 minutos na primeira tentativa.
- **SC-002**: 100% das tentativas de iniciar análise sem token configurado são bloqueadas com mensagem clara.
- **SC-003**: 100% das branches duplicadas no mesmo repositório são rejeitadas.
- **SC-004**: 100% dos commits importados armazenam apenas os campos relevantes definidos pela spec.
- **SC-005**: Usuários conseguem acompanhar o andamento de uma execução até sua conclusão sem perder a análise anterior.
- **SC-006**: Pelo menos 90% dos usuários de teste conseguem selecionar parâmetros, iniciar a análise e entender o resultado da execução sem assistência adicional.

## Assumptions

- O usuário que executa a análise já possui acesso autenticado ao sistema.
- A Spec 001 fornece projetos, repositórios e sprints.
- A Spec 002 fornece alunos e apelidos GitHub para associação automática.
- A Spec 003 fornece sprints e seus vínculos com projetos.
- A Spec 004 fornece o token GitHub global configurado.
- A aplicação continua usando o stack atual de Django com templates server-rendered e as bibliotecas já presentes no projeto.
