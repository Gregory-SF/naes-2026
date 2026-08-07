# Data Model: Gerenciamento de Projetos

## Projeto

**Purpose**: Representa o projeto acadêmico que será exibido, editado e removido
pelos usuários autenticados.

**Fields**:

- `id`: identificador primário
- `nome`: nome do projeto, obrigatório
- `status`: estado do projeto, com apoio aos estados já existentes no app
- `ano`: campo já existente no app, mantido por compatibilidade com a estrutura
  atual
- `link_organizacao_github`: URL da organização ou conta GitHub associada ao
  projeto, obrigatória
- `cadastrado_em`: data de criação
- `atualizado_em`: data da última alteração

**Relationships**:

- Possui vários `Repositorio`

**Validation Rules**:

- `nome` não pode ser vazio
- `link_organizacao_github` deve ser um link GitHub válido e representar uma
  conta existente
- o projeto deve permanecer acessível para seleção em outras telas apenas quando
  estiver ativo

## Repositorio

**Purpose**: Representa um repositório GitHub vinculado a um projeto.

**Fields**:

- `id`: identificador primário
- `projeto`: projeto ao qual o repositório pertence
- `nome`: nome exibido do repositório, obrigatório
- `link`: URL do repositório GitHub, obrigatória
- `alias`: rótulo curto opcional para exibição
- `linguagem_principal`: campo opcional já existente no app
- `tipo`: campo opcional já existente no app
- `cadastrado_em`: data de criação
- `atualizado_em`: data da última alteração

**Relationships**:

- Pertence a exatamente um `Projeto`

**Validation Rules**:

- `nome` e `link` são obrigatórios
- o link deve ser válido no GitHub
- o mesmo link não pode se repetir dentro do mesmo projeto
- o owner do repositório deve bater com o contexto da organização/conta do
  projeto

## Authenticated User

**Purpose**: Representa quem executa as ações de CRUD.

**Fields**:

- `id`
- `username`
- permissões de acesso às telas protegidas

**Relationships**:

- Nenhuma relação de domínio específica para esta feature, além do controle de
  acesso às views

## State Notes

- `Projeto.status = ATIVO` permite seleção em outras telas
- `Projeto.status = INATIVO` impede uso em dropdowns, mas mantém o cadastro para
  consulta histórica
