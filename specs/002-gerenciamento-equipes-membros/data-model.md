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

## Mapeamento de campos do formulário para entidades [Revisão 2026-08-10]

O formulário de equipe não usa formset genérico nem dropdown de papel. Os campos
de texto seguem a convenção abaixo, lida manualmente na view:

| Campo no formulário | Papel em `MembroEquipe` | Cardinalidade |
|---|---|---|
| `membros_sm_nome` | `SCRUM_MASTER` | Exatamente 1, fixo, sempre visível |
| `membros_po_nome` | `PRODUCT_OWNER` | Exatamente 1, fixo, sempre visível |
| `membros_dev_<index>_nome` | `DESENVOLVEDOR` | 1..N, repetível via botão "+" |
| `membros_total_devs` | — (contador de campos DEV) | Inteiro >= 1 |

### Regra de resolução de `Aluno` no save

1. Buscar `Aluno` por `nome__iexact` com o texto digitado.
2. Se encontrar exatamente 1 resultado → reutilizar o registro existente.
3. Se não encontrar nenhum resultado → criar novo `Aluno` com `nome` igual ao
	texto digitado.
4. Se encontrar mais de 1 resultado → retornar erro de ambiguidade no campo
	correspondente, com mensagem orientando o usuário a usar o apelido GitHub
	para distinguir.
