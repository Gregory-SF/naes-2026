# Research Notes: Gerenciamento de Projetos

## 1. Validação de links GitHub sem mudar o stack

**Decision**: Reutilizar Django e o app `commex`, adicionando a validação em uma
camada pequena de formulário/serviço, chamada pelas views de criação e edição.

**Rationale**: O repositório já é um Django server-rendered com forms e views
class-based. Isso permite validar antes do `save()` sem introduzir DRF, sem criar
uma segunda superfície de interface e sem conflitar com crispy forms ou com os
templates atuais.

**Alternatives considered**:

- Criar uma API REST com DRF. Rejeitado porque não corresponde à estrutura atual
  do projeto e aumentaria o escopo sem necessidade.
- Validar apenas o formato da URL com regex. Rejeitado porque a spec exige
  existência real do link no GitHub.

## 2. Autenticação para as telas do CRUD

**Decision**: Proteger as views de projeto com autenticação nativa do Django,
preferencialmente via `LoginRequiredMixin` nas CBVs e fluxo padrão de login do
framework.

**Rationale**: O projeto já inclui middleware de autenticação e redirects de
login/logout nas settings. Isso mantém a solução coerente com o stack atual e
evita dependências extras.

**Alternatives considered**:

- JWT ou outra autenticação tokenizada. Rejeitado por ser excessivo para um CRUD
  web tradicional baseado em templates.
- Manter o CRUD público. Rejeitado porque a feature pressupõe uso por PO/Dev e o
  projeto já tem suporte nativo à autenticação.

## 3. Relação entre Projeto e Repositório

**Decision**: Evoluir a modelagem atual para que o vínculo de repositório fique
explícito e fácil de validar no contexto do projeto, preservando o restante das
entidades já existentes no app.

**Rationale**: A implementação atual usa um relacionamento amplo e campos que não
representam a necessidade da spec. Tornar o vínculo explícito reduz risco de
inconsistência, facilita a exclusão individual de repositórios e simplifica a
validação do owner GitHub.

**Alternatives considered**:

- Manter o relacionamento amplo atual sem ajuste. Rejeitado por não expressar o
  1:N pedido pela feature.
- Criar um app novo só para a feature. Rejeitado porque o repositório já possui o
  domínio e as telas relevantes em `commex`.

## 4. Banco de dados e deploy

**Decision**: Preservar PostgreSQL no Neon e manter a configuração de static
files compatível com `static_gcloud`.

**Rationale**: Isso respeita a constituição do projeto e evita regressões de
deploy. O código já aponta para esse ambiente e a feature não precisa alterar a
infraestrutura para entregar valor.

**Alternatives considered**:

- Migrar para outro banco ou reconfigurar o deploy. Rejeitado porque não há
  demanda funcional para isso e aumentaria o risco.
