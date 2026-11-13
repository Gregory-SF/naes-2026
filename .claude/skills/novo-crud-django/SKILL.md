---
name: novo-crud-django
description: Cria ou altera telas de cadastro, listagem, detalhe, edição e exclusão no app commex seguindo os padrões do projeto (class-based views, GroupRequiredMixin, mensagens, templates Bootstrap, nomes de URL). Use ao adicionar uma nova entidade ou tela CRUD.
---

# Novo CRUD no padrão do projeto

Referência viva: `Projeto` e `Sprint` em `commex/views.py`, `commex/urls.py` e
`commex/templates/commex/`. Releia o equivalente mais próximo antes de escrever.

## Passos

1. **Model** (`commex/models.py`): inclua `cadastrado_em` (`auto_now_add`), `atualizado_em`
   (`auto_now`), `Meta.ordering` e `__str__`. Rode `python manage.py makemigrations commex` e
   adicione a migração com `git add -f` (a pasta está no `.gitignore`).
2. **Form** (`commex/forms.py`): `ModelForm` simples; validações no `clean_*`.
3. **Views** (`commex/views.py`):
   - Escrita (criar/alterar/excluir): `GroupRequiredMixin` com `group_required = GRUPO_COORDENADORES`.
   - Leitura (listar/detalhar): `group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]`.
   - `ListView` com `paginate_by = 20` e queryset já otimizado (`select_related` / `prefetch_related`).
   - Em `form_valid` e na exclusão, chame `messages.success(...)`; em falha de regra de negócio,
     `messages.error(...)`. Textos em português, com acentos.
4. **URLs** (`commex/urls.py`): `cadastrar/<entidade>/`, `atualizar/<entidade>/<int:pk>/`,
   `excluir/<entidade>/<int:pk>/`, `listar/<entidade>/`, `detalhar/<entidade>/<int:pk>/`, com
   `name='<entidade>-create|update|delete|list|detail'`.
5. **Templates** em `commex/templates/commex/<entidade>/`, estendendo `commex/base.html`:
   - lista: cabeçalho com botão "Novo", card + `table-responsive`, DataTables no `extra_js`,
     bloco `{% empty %}` e paginação;
   - formulário: crispy forms (`{% load crispy_forms_tags %}`) e botões Salvar/Cancelar;
   - exclusão: tela de confirmação com POST e `{% csrf_token %}`.
6. **Navegação**: adicione o link no menu de `base.html` e use `{% url %}` com os nomes acima.
7. **Verificação**: `python manage.py check`, abra as telas no navegador, confirme as mensagens e
   confira as queries no Debug Toolbar.

## Checklist final

- [ ] Permissão por grupo em todas as views
- [ ] Mensagem em criar, alterar e excluir
- [ ] Sem N+1 na lista e no detalhe
- [ ] Migração criada e adicionada com `git add -f`
- [ ] Commit no padrão da skill `commit-padrao`
