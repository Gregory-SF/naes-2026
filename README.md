# NAES 2026 - Gestão de Projetos

Sistema Django para projetos, equipes, sprints, análise de commits do GitHub e assistente de IA.

**Link da aplicação (Google App Engine):** _preencha após o deploy: `https://SEU-PROJETO.appspot.com`_

## Rodando localmente
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Sem `DATABASE_URL`, usa SQLite local. Para o Neon, defina `DATABASE_URL`.

## Deploy
1. Copie `env_variables.yaml.example` para `env_variables.yaml` e preencha.
2. `python manage.py collectstatic --noinput`
3. `gcloud app deploy`
4. Rode `python manage.py migrate` apontando para o banco de produção.
