---
name: otimizar-queries
description: Identifica queries repetidas (N+1) com o Django Debug Toolbar e as corrige com select_related, prefetch_related ou annotate. Use ao revisar desempenho de listas/detalhes, ao criar telas que acessam relações, ou quando o usuário mencionar queries lentas ou repetidas.
---

# Otimização de queries com o Debug Toolbar

O Debug Toolbar já está configurado (`settings.py`: ativo só com `DEBUG = True`, `INTERNAL_IPS` com
`127.0.0.1` e `localhost`; rota `__debug__/` em `naes2026/urls.py`).

## Procedimento

1. Suba o servidor (`python manage.py runserver`) e abra a tela em `http://127.0.0.1:8000/`
   (use esse host, o toolbar não aparece em outros).
2. Abra o painel **SQL** do toolbar. Veja a contagem de queries e as marcadas como
   **"similar"** ou **"duplicate"**: são os candidatos a N+1.
3. Descubra qual acesso no template ou na view gera cada query (o painel mostra o traceback).
4. Corrija no `get_queryset()` / `get_object()` da view:
   - FK ou OneToOne acessada no loop -> `select_related('projeto', 'projeto__x')`
   - M2M ou relação reversa -> `prefetch_related('membros__aluno')`
   - contagem por linha (`obj.relacao.count`) -> `annotate(total=Count('relacao', distinct=True))`
   - filtrar o prefetch -> `Prefetch('relacao', queryset=..., to_attr='...')`
5. Recarregue e compare: o número de queries deve cair e não crescer com o número de linhas.
6. Registre antes/depois na descrição do commit (ex.: "de 41 para 6 queries").

## Atenção neste projeto

- `IndexView` faz várias queries independentes (listas recentes e `count()`); considere agrupá-las.
- `SprintDetail` não define queryset: avalie `prefetch_related('projetos')`.
- Em métodos `__str__` que acessam FK (`Equipe.__str__` usa `projeto.nome`), o `select_related`
  é necessário em qualquer lista que imprima o objeto.
- Não use `.count()` dentro de loops de template; use `annotate` ou `len` sobre resultado já carregado.
- Não deixe `select_related` desnecessário: só otimize relações realmente usadas na tela.
