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

## Decisão 4: Padrão de UI para composição de membros no formulário [Revisão 2026-08-10]

**Decision**: Substituir o formset genérico com dropdown de papel
(`MembroEquipeFormSet`) por campos de texto livre dedicados por papel: um campo
fixo "Nome do Scrum Master", um campo fixo "Nome do Product Owner" e um ou mais
campos repetíveis "Nome do Desenvolvedor", controlados por JavaScript no cliente
via botão "+". O formulário abre com os três campos já visíveis sem nenhuma
ação do usuário. A resolução de aluno acontece no save: busca case-insensitive
por nome exato → reutiliza se encontrar um único resultado → cria implicitamente
se não encontrar → retorna erro de ambiguidade se encontrar mais de um resultado.
Os campos seguem o padrão de nomes `membros_sm_nome`, `membros_po_nome`,
`membros_total_devs`, `membros_dev_<index>_nome`, lidos manualmente na view sem
management form do Django formset.

**Rationale**: A abordagem de formset genérico com seleção de aluno via dropdown
e seleção de papel via select gera UX confusa ("Novo repos json" / erros de
TOTAL_FORMS/INITIAL_FORMS na abertura) e não traduz o modelo mental de "insira
o nome do Scrum Master". O padrão de coleção manual já foi validado na feature
001 (`RepositorioCardCollection`) e resolve os mesmos problemas sem adicionar
dependência nova.

**Alternatives considered**:
- Manter `MembroEquipeFormSet` com campo `aluno` (dropdown) e campo `papel`
	(select): rejeitado porque gera UX confusa, não mapeia o modelo mental por
	papel e já apresentou bugs de management form documentados na feature 001.
- Autocomplete AJAX para busca de aluno: rejeitado por adicionar complexidade de
	frontend (biblioteca `django-autocomplete-light` já existe mas adiciona
	dependência de configuração por view) sem ganho significativo para o volume
	acadêmico esperado.
- Campo de texto com sugestão via `datalist` HTML: considerado como melhoria
	futura, não mandatório nesta iteração.
