# Data Model: Configurações Globais

## ConfiguracaoGlobal

- `id`
- `github_token_criptografado`
- `atualizado_em`

Regras:
- singleton (um registro ativo)
- token opcional

## DiaAula

- `id`
- `configuracao_id`
- `dia_semana` (SEGUNDA a SEXTA)

Regras:
- seleção múltipla
- pode ficar vazio
