# Feature Specification: Configurações Globais do Sistema

**Feature Branch**: `004-configuracoes-globais`

**Created**: 2026-08-06

**Status**: Draft

**Input**: User description: "Spec 004 — Configurações Globais do Sistema"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acessar e salvar configurações globais do sistema (Priority: P1)

Como usuário autorizado, quero acessar uma tela de Configurações para salvar o token do GitHub e os dias de aula, para centralizar dados globais que serão usados por outras partes do sistema.

**Why this priority**: Esta é a base da feature e entrega o valor principal do armazenamento global.

**Independent Test**: Um usuário consegue abrir a tela de Configurações, salvar um token do GitHub e selecionar dias de aula, e depois reabrir a tela vendo o mesmo estado salvo.

**Acceptance Scenarios**:

1. **Given** que o usuário abre a tela de Configurações, **When** ele informa um token válido do GitHub e seleciona um ou mais dias de aula, **Then** o sistema salva as configurações com sucesso.
2. **Given** que o usuário reabre a tela de Configurações, **When** a página é carregada, **Then** o token aparece como configurado e os dias de aula previamente selecionados ficam visíveis.
3. **Given** que o usuário tenta salvar um token em formato claramente inválido, **When** ele confirma o salvamento, **Then** o sistema bloqueia a operação e informa o problema.

---

### User Story 2 - Visualizar, substituir e remover o token do GitHub (Priority: P2)

Como usuário autorizado, quero ver o token de forma mascarada, revelar seu conteúdo quando necessário e substituí-lo ou removê-lo, para manter o acesso ao GitHub sob controle sem expor o valor em repouso.

**Why this priority**: O ciclo de vida do token é uma parte sensível da configuração global e precisa ser tratada separadamente.

**Independent Test**: Um usuário consegue ver o token mascarado, alternar a visibilidade temporariamente, trocar o token salvo e removê-lo, sem perder o restante das configurações.

**Acceptance Scenarios**:

1. **Given** que existe um token salvo, **When** o usuário abre a tela de Configurações, **Then** o token é mostrado de forma mascarada por padrão.
2. **Given** que existe um token mascarado na tela, **When** o usuário aciona o botão de visualização, **Then** o token é exibido em texto plano enquanto a ação estiver ativa.
3. **Given** que existe um token salvo, **When** o usuário substitui o valor por um novo token e salva, **Then** o token anterior é substituído.
4. **Given** que existe um token salvo, **When** o usuário remove o token e confirma a ação, **Then** o sistema volta ao estado sem token configurado.

---

### User Story 3 - Manter os dias de aula atualizáveis (Priority: P3)

Como usuário autorizado, quero marcar e desmarcar os dias da semana usados como dias de aula, para manter essa configuração sempre alinhada ao calendário acadêmico.

**Why this priority**: Os dias de aula são uma configuração global importante, mas complementar ao armazenamento do token.

**Independent Test**: Um usuário consegue alterar livremente a seleção dos dias de aula e ver o novo estado salvo ao reabrir a tela.

**Acceptance Scenarios**:

1. **Given** que a tela de Configurações está aberta, **When** o usuário seleciona um ou mais dias da semana e salva, **Then** o sistema registra os dias selecionados.
2. **Given** que já existem dias configurados, **When** o usuário marca e desmarca dias livremente e salva, **Then** o sistema atualiza a seleção de forma idempotente.
3. **Given** que o usuário desmarca todos os dias, **When** ele salva a configuração, **Then** o sistema aceita o estado sem dias de aula configurados.

---

## Non-Goals

- Uso efetivo do token para consultar commits.
- Uso efetivo dos dias de aula em cálculos ou relatórios.
- Suporte a múltiplos usuários com configurações individuais.
- Rotação automática ou expiração do token.

### Edge Cases

- Salvar a configuração sem token é permitido, desde que o sistema permaneça funcional.
- Um token com formato claramente inválido deve ser tratado como entrada inválida.
- Falha ao criptografar o token deve impedir o salvamento e preservar o estado anterior.
- Revelar o token deve ser uma ação explícita do usuário e a exibição em texto plano deve ser temporária.
- A ausência de qualquer dia selecionado deve ser um estado válido.
- Dois salvamentos concorrentes devem seguir o comportamento de última gravação prevalece.
- Reabrir a tela após sair dela deve retornar o token ao estado mascarado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema deve exibir um menu ou ícone de Configurações acessível a partir de qualquer tela do sistema.
- **FR-002**: O sistema deve permitir informar e salvar o token de acesso pessoal do GitHub na tela de Configurações.
- **FR-003**: O sistema deve armazenar o token de forma protegida em repouso, sem expô-lo em texto plano na persistência.
- **FR-004**: O sistema deve exibir o token de forma mascarada por padrão e permitir que o usuário o revele temporariamente por ação explícita.
- **FR-005**: O sistema deve permitir substituir o token salvo sem exigir a exibição do valor anterior.
- **FR-006**: O sistema deve permitir remover o token salvo e voltar ao estado sem token configurado.
- **FR-007**: O sistema deve disponibilizar internamente o token em texto plano para consumo por módulos do sistema que precisem dele, sem expô-lo fora do fluxo de visualização autorizado.
- **FR-008**: O sistema deve permitir selecionar um ou mais dias da semana como dias de aula por meio de múltipla escolha.
- **FR-009**: O sistema deve permitir alterar os dias de aula a qualquer momento, marcando e desmarcando livremente as opções disponíveis.
- **FR-010**: O sistema deve permitir que nenhum dia esteja selecionado como estado válido.
- **FR-011**: O sistema deve exibir, ao abrir a tela de Configurações, o estado atual salvo do token e dos dias de aula.
- **FR-012**: O sistema deve validar entradas de token claramente inválidas antes de salvar a configuração.

### Key Entities *(include if feature involves data)*

- **ConfiguracaoGlobal**: Representa a configuração única do sistema, incluindo o token do GitHub e a data da última atualização.
- **DiaAula**: Representa cada dia da semana selecionado como dia de aula para a configuração global.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem salvar a configuração global completa em menos de 2 minutos na primeira tentativa.
- **SC-002**: 100% das tentativas de salvar tokens claramente inválidos são bloqueadas com mensagem clara.
- **SC-003**: O token salvo não aparece em texto plano ao reabrir a tela de Configurações, exceto quando o usuário aciona a visualização explícita.
- **SC-004**: Usuários conseguem alterar os dias de aula e ver o estado persistido corretamente ao reabrir a tela.
- **SC-005**: Usuários conseguem remover o token e retornar ao estado sem token configurado sem afetar os demais dados salvos.
- **SC-006**: Pelo menos 90% dos usuários de teste conseguem identificar e atualizar as configurações globais sem assistência adicional.

## Assumptions

- O público-alvo desta feature já possui acesso autorizado ao sistema.
- O token do GitHub é uma configuração global única, não individual por usuário.
- A tela de Configurações preserva o restante da interface e continua acessível por navegação comum do sistema.
- Os dias de aula são limitados de segunda a sexta.
- A aplicação continua usando o stack atual de Django com templates server-rendered e as bibliotecas já presentes no projeto.
