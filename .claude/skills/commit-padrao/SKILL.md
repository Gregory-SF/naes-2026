---
name: commit-padrao
description: Padroniza mensagens de commit do projeto (Conventional Commits em português). Use sempre que for criar, sugerir ou revisar uma mensagem de commit, ou quando o usuário pedir para commitar.
---

# Padrão de mensagens de commit

Formato (Conventional Commits, em português do Brasil):

```
<tipo>(<escopo>): <descrição curta no imperativo>

<corpo opcional: o que mudou e por quê>
```

## Regras

1. **Tipo** (obrigatório), um destes:
   - `feat`: nova funcionalidade
   - `fix`: correção de bug
   - `refactor`: mudança de código sem alterar comportamento
   - `perf`: otimização (ex.: `select_related`, queries)
   - `style`: formatação/CSS/templates sem lógica
   - `docs`: documentação (AGENTS.md, specs, skills)
   - `test`: testes
   - `chore`: configuração, dependências, build, deploy
2. **Escopo** (recomendado): `commex`, `ia`, `settings`, `templates`, `deps`, `deploy`, `specs`,
   `agents`. Use o app ou área afetada.
3. **Descrição**: minúscula, sem ponto final, verbo no imperativo ("adiciona", "corrige",
   "remove"), até 72 caracteres.
4. **Corpo** (quando a mudança não é óbvia): linha em branco após o título, linhas de até
   ~80 caracteres, explicando o porquê. Mudança incompatível: rodapé `BREAKING CHANGE: ...`.
5. Um commit = uma mudança lógica. Não misture feature, refactor e formatação.
6. Nunca inclua segredos (senhas, tokens, `SECRET_KEY`, URL do banco) na mensagem.
7. Evite mensagens vagas como "ajustes", "recu", "teste" ou "update".

## Passos ao commitar

1. `git status` e `git diff --staged` para ver o que entra.
2. Se houve mudança em models, confirme que a migração está no stage. `commex/migrations/` está no
   `.gitignore`, então use `git add -f commex/migrations/<arquivo>.py`.
3. Escolha tipo e escopo pelo conteúdo do diff e escreva a mensagem.
4. Commit só quando o usuário pedir.

## Exemplos

```
feat(commex): adiciona filtro por projeto e nome na lista de sprints
fix(commex): exibe mensagens de sucesso no base.html
perf(commex): usa select_related em SprintDetail para evitar N+1
chore(settings): move SECRET_KEY e credenciais do banco para variáveis de ambiente
docs(agents): cria AGENTS.md e skills dos agentes
```
