---
name: deploy-app-engine
description: Checklist e comandos para publicar o projeto no Google App Engine (app.yaml, collectstatic, segredos, ALLOWED_HOSTS). Use quando o usuário pedir deploy, preparar para produção ou revisar a configuração do App Engine.
---

# Deploy no Google App Engine

Arquivos envolvidos: `app.yaml` (runtime `python312`, gunicorn, handler `/static` ->
`static_gcloud/`), `.gcloudignore`, `requirements.txt` e `naes2026/settings.py`.

## Antes de publicar

1. **Segredos**: `SECRET_KEY` e a URL do banco Neon estão hard-coded em `settings.py`. Antes do
   deploy, leia-os de variáveis de ambiente (`os.getenv`) e defina-as em `app.yaml`
   (`env_variables`) ou no Secret Manager. Nunca versione o valor real.
2. **DEBUG**: use `DEBUG = os.getenv('DEBUG', 'False') == 'True'`. Com `DEBUG = False` o Debug
   Toolbar não é carregado.
3. **ALLOWED_HOSTS**: troque `['*']` pelo domínio `<projeto>.appspot.com` (e o domínio próprio, se houver).
4. **CSRF**: se houver erro 403 em formulários em produção, adicione
   `CSRF_TRUSTED_ORIGINS = ['https://<projeto>.appspot.com']`.
5. **Estáticos**: `python manage.py collectstatic --noinput` e confirme que `static_gcloud/` está atualizado.
6. **Migrações**: `python manage.py migrate` (o banco é o Neon, compartilhado; confirme com o usuário).
7. `python manage.py check --deploy` e corrija os avisos relevantes.

## Publicar

```bash
gcloud config set project <ID_DO_PROJETO>
gcloud app deploy app.yaml
gcloud app browse        # abre/mostra o link de acesso
gcloud app logs tail -s default
```

## Depois

- Teste login, listagens e uma criação com mensagem de sucesso no link público.
- Registre o link de acesso no `README.md` (requisito do trabalho: disponibilizar o link).
- Commit no padrão da skill `commit-padrao` (ex.: `chore(deploy): ...`).
