# Data Model: Gerenciamento de Equipes e Membros

## Equipe

- `id`
- `nome` (único)

Relacionamentos:
- N:N com `Aluno` por `MembroEquipe`

Regras:
- Exatamente 1 Scrum Master
- Exatamente 1 Product Owner
- Pelo menos 1 Desenvolvedor

## Aluno

- `id`
- `nome`

Relacionamentos:
- 1:N com `ApelidoGithub`
- N:N com `Equipe` por `MembroEquipe`

Regras:
- Nome não é único globalmente

## ApelidoGithub

- `id`
- `aluno_id`
- `nickname`

Regras:
- `nickname` único global

## MembroEquipe

- `id`
- `equipe_id`
- `aluno_id`
- `papel` (SCRUM_MASTER, PRODUCT_OWNER, DESENVOLVEDOR)

Regras:
- Um aluno não pode ter mais de um papel na mesma equipe
