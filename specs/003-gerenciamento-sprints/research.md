# Research Notes: Gerenciamento de Sprints

## Decisão 1: Pré-vínculo com projetos existentes

**Decision**: Ao criar sprint, iniciar com todos os projetos atuais vinculados,
permitindo desmarcar antes de salvar.

**Rationale**: Atende o fluxo principal e reduz retrabalho no cadastro inicial.

## Decisão 2: Edição reversível de vínculos

**Decision**: Marcar/desmarcar vínculos de sprint e projeto de forma idempotente.

**Rationale**: Permite ajustes contínuos sem estado definitivo de bloqueio.

## Decisão 3: Sem bloqueio por nome duplicado

**Decision**: Nome de sprint pode se repetir.

**Rationale**: A diferenciação pode ocorrer por período e contexto de projeto.
