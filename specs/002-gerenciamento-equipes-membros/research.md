# Research Notes: Gerenciamento de Equipes e Membros

## Decisão 1: Fluxo único de equipe e membro

**Decision**: Reutilizar formulário de equipe com suporte a seleção de aluno
existente e criação on-the-fly.

**Rationale**: Evita tela isolada de aluno e atende o fluxo principal da spec.

**Alternatives considered**: Cadastro separado de aluno, rejeitado por sair do
escopo.

## Decisão 2: Unicidade de apelido GitHub

**Decision**: Garantir unicidade global de apelido no nível de persistência e
validação de formulário.

**Rationale**: Evita ambiguidades na associação de commits em specs futuras.

**Alternatives considered**: Unicidade por equipe, rejeitado por gerar conflito
na associação de autoria.

## Decisão 3: Troca de papéis críticos

**Decision**: Implementar troca de Scrum Master/Product Owner como ação dedicada
em transação única.

**Rationale**: Garante que a equipe não fique sem papel obrigatório em estado
intermediário.

**Alternatives considered**: Remoção e inclusão em etapas separadas, rejeitado
por risco de inconsistência temporária.
