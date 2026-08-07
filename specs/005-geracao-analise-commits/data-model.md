# Data Model: Geração de Análise de Commits

## Branch

- `id`
- `repositorio_id`
- `nome_branch`
- `adicionada_em`

Regras:
- unicidade de `nome_branch` por repositório

## ExecucaoAnalise

- `id`
- `projeto_id`
- `repositorio_id`
- `branch_id`
- `sprint_id` (nullable)
- `data_inicio`
- `data_fim`
- `status` (PENDENTE, PROCESSANDO, CONCLUIDA, ERRO)
- `iniciada_em`
- `concluida_em`
- `total_commits_importados`
- `mensagem_erro` (nullable)

## CommitAnalisado

- `id`
- `execucao_id`
- `hash_commit`
- `autor_nome`
- `autor_login_github`
- `autor_email`
- `mensagem_commit`
- `data_commit`
- `quantidade_arquivos_alterados`
- `linhas_adicionadas`
- `linhas_removidas`
- `aluno_id` (nullable)
