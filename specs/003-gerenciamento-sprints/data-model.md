# Data Model: Gerenciamento de Sprints

## Sprint

- `id`
- `nome`
- `data_inicio`
- `data_fim`
- `descricao` (opcional)

Regras:
- `data_fim >= data_inicio`

## SprintProjeto

- `id`
- `sprint_id`
- `projeto_id`

Regras:
- vínculo reversível por edição
- remoção em cascata ao excluir sprint ou projeto
