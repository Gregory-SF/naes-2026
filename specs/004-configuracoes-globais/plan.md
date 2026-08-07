# Implementation Plan: Configurações Globais do Sistema

**Branch**: `004-configuracoes-globais` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Implementar tela de configurações globais para token GitHub e dias de aula,
com token protegido em repouso e exibição mascarada por padrão.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: Django 5.x, biblioteca de criptografia simétrica
**Storage**: PostgreSQL (Neon)
**Testing**: Não obrigatório; validação manual
**Target Platform**: Django server-rendered

## Constitution Check

- ✅ Mantém stack e autenticação nativos
- ✅ Mantém compatibilidade com configuração atual

## Access, Ownership, Pagination and Query Decisions

### View Access Matrix

| View | LoginRequiredMixin | GroupRequiredMixin | Decision |
|---|---|---|---|
| `ConfiguracaoGlobalUpdate` | Sim | Não | Configurações globais são sensíveis e devem ser alteradas por usuário autenticado |
| `ConfiguracaoGlobalDetail` (se implementada) | Sim | Não | Visualização da configuração segue a mesma área protegida |
| `ConfiguracaoGlobalCreate` | Não aplicável | Não aplicável | A feature é singleton e não prevê criação separada quando a configuração não existe |
| `ConfiguracaoGlobalDelete` | Não aplicável | Não aplicável | A spec trata de salvar/substituir/remover token, não de excluir o objeto singleton |
| `ConfiguracaoGlobalList` | Não aplicável | Não aplicável | Não há listagem de múltiplos registros nesta feature |

### User Ownership / `User` ForeignKey

- Nenhum model desta feature possui `ForeignKey` para `User`.
- A configuração é global, não individual por usuário.
- Não há `form_valid()` de owner nem `get_queryset()` de isolamento por usuário.

### ListView Pagination

- Não há `ListView` nesta feature.
- A exceção da constitution se aplica porque a tela é singleton e o volume é pequeno e finito por regra de negócio.

### Templates que Consultam `request.user.is_authenticated`

- `commex/base.html` para mostrar o acesso às Configurações apenas para usuários autenticados.
- A template da tela de configurações deve esconder o token, revelar/ocultar o valor e habilitar a troca/remoção apenas quando o usuário estiver autenticado.

### Querysets com Relações em Template

- A consulta da singleton deve carregar os dias selecionados para exibição na tela.
- O queryset da configuração deve usar `prefetch_related('diaaula_set')` (ou o related name definitivo, caso seja ajustado) para evitar consultas repetidas ao renderizar os dias de aula.
- Não há `select_related` necessário porque o acesso relevante é uma coleção relacionada simples da configuração singleton.

## Project Structure

```text
specs/004-configuracoes-globais/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

## Phase 0: Outline & Research

1. Definir estratégia de criptografia e segredo
2. Definir máscara/revelação segura de token
3. Definir persistência singleton de configuração global

## Phase 1: Design & Contracts

1. `data-model.md` com ConfiguracaoGlobal e DiaAula
2. Contracts não aplicável
3. `quickstart.md` para validação de salvar/atualizar/remover token e dias

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`
