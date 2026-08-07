# Research Notes: Geração de Análise de Commits

## Decisão 1: Execução assíncrona

**Decision**: Executar importação em background com status consultável.

**Rationale**: Evita timeout e permite progresso incremental ao usuário.

## Decisão 2: Branch estruturada por repositório

**Decision**: Persistir branches retornadas da API como entidade própria por
repositório.

**Rationale**: Reuso em análises futuras e eliminação de texto livre por execução.

## Decisão 3: Persistência mínima de campos de commit

**Decision**: Salvar apenas campos relevantes para análise posterior.

**Rationale**: Reduz custo de armazenamento e ruído de dados.

## Decisão 4: Associação por apelido GitHub

**Decision**: Resolver `aluno_id` a partir do login do autor e apelidos
cadastrados.

**Rationale**: Mantém rastreabilidade com base no que já existe na spec 002.
