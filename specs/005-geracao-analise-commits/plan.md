# Implementation Plan: Geração de Análise de Commits

**Branch**: `005-geracao-analise-commits` | **Date**: 2026-08-07 | **Spec**: [spec.md](spec.md)

## Summary

Implementar fluxo manual de importação de commits via API do GitHub com seleção
de projeto/repositório/branch/período, execução rastreável e persistência dos
dados relevantes com associação opcional a aluno.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: Django 5.x, cliente HTTP, suporte a background job
**Storage**: PostgreSQL (Neon)
**Testing**: Não obrigatório por padrão; validação manual orientada por cenário
**Target Platform**: Django server-rendered
**Constraints**: Depende das specs 001-004; não expor token em logs

## Constitution Check

- ✅ Stack preservado
- ✅ Integração com auth existente
- ✅ Compatível com banco/infra atuais

## Access, Ownership, Pagination and Query Decisions

### View Access Matrix

| View | LoginRequiredMixin | GroupRequiredMixin | Decision |
|---|---|---|---|
| `ExecucaoAnaliseCreate` / tela de início da análise | Sim | Não | Apenas usuário autenticado deve disparar importações de commits |
| `ExecucaoAnaliseList` | Sim | Não | Histórico de execuções é parte da área protegida |
| `ExecucaoAnaliseDetail` / status da execução | Sim | Não | Status e resultados pertencem ao usuário autenticado que opera a análise |
| `BranchFetch/Add` (ações de buscar/cadastrar branch) | Sim | Não | Operações de branch dependem de token e contexto autenticado |
| `BranchList` / `BranchDetail` / `BranchUpdate` / `BranchDelete` | Não aplicável | Não aplicável | A spec não define CRUD separado de branch; a gestão é feita por ações dentro do fluxo de análise |

### User Ownership / `User` ForeignKey

- Nenhum model desta feature possui `ForeignKey` para `User`.
- `Branch`, `ExecucaoAnalise` e `CommitAnalisado` pertencem ao contexto da análise, não ao usuário como owner persistido.
- Não há `form_valid()` para preencher owner nem `get_queryset()` para restringir dados por usuário autenticado.

### ListView Pagination

- `ExecucaoAnaliseList` deve implementar `paginate_by = 20`.
- Justificativa: histórico de execuções pode crescer continuamente e a lista precisa permanecer navegável.
- Não há paginação necessária para listas pequenas/locais de branches dentro do formulário de análise; essas listas são contextuais e finitas por repositório.

### Templates que Consultam `request.user.is_authenticated`

- `commex/base.html` para alternar menu e ações protegidas de análise.
- Template de início da análise para mostrar botão de execução apenas a usuários autenticados.
- Template de status/detalhe da execução para controlar ações como reexecutar, atualizar ou abrir histórico.
- Templates/partials de seleção de branch devem condicionar ações de adicionar/buscar à autenticação.

### Querysets com Relações em Template

- `ExecucaoAnaliseList` e `ExecucaoAnaliseDetail` devem usar `select_related('projeto', 'repositorio', 'branch', 'sprint')` porque o status e o histórico exibem esses relacionamentos diretos.
- `ExecucaoAnaliseDetail` deve usar `prefetch_related('commitanalisado_set', 'commitanalisado_set__aluno')` porque a página de resultado pode listar commits e associação com aluno.
- Se a tela contextual de branches exibir o repositório pai, o queryset de branch também deve usar `select_related('repositorio')`.
- Não há relação com `User` a ser isolada nesta feature.

## Project Structure

```text
specs/005-geracao-analise-commits/
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

## Phase 0: Outline & Research

1. Estratégia de importação assíncrona
2. Paginação e rate limit da API GitHub
3. Mapeamento de aluno por apelido GitHub
4. Política de reexecução sem sobrescrita

## Phase 1: Design & Contracts

1. `data-model.md` com Branch, ExecucaoAnalise, CommitAnalisado
2. Contracts não aplicável (fluxo interno)
3. `quickstart.md` com cenários de importação e erro

## Complexity Tracking

| Violation/Risk | Justificativa | Alternative rejected |
|---|---|---|
| Dependência de API externa | Requisito essencial de importação | Mock fixo local sem API, rejeitado |
| Processamento assíncrono | Volume e tempo imprevisíveis de commits | Execução síncrona simples, rejeitada por timeout |

## Progress Tracking

- [x] Initial Constitution Check
- [x] Phase 0: research.md gerado
- [x] Phase 1: data-model.md, quickstart.md gerados
- [x] Post-Design Constitution Check
- [x] Pronto para `/speckit.tasks`
