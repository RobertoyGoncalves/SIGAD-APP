# SIGAD-APP

Sistema Django de gestão de doações — estoque, beneficiários, distribuições e relatórios.

## Executar localmente

1. Ambiente virtual: `python -m venv venv`
2. Ativar:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
3. Dependências: `pip install -r requirements.txt`
4. (Opcional) Copie `.env.example` para `.env` e configure `DATABASE_URL`
5. Migrações: `python manage.py migrate`
6. Servidor: `python manage.py runserver`
7. Abrir: http://127.0.0.1:8000/

## Rotas principais

- `/` — landing page
- `/dashboard/` — painel do sistema
- `/registrar-item/`
- `/registrar-distribuicao/`
- `/estoque/`
- `/beneficiarios/`
- `/relatorios/`
- `/admin/`

## Deploy no Railway

O projeto inclui `railway.toml` e `Procfile` prontos para produção.

### O que o repositório já configura

- Gunicorn + Whitenoise (arquivos estáticos)
- PostgreSQL via `DATABASE_URL`
- Host e CSRF automáticos com `RAILWAY_PUBLIC_DOMAIN`
- `collectstatic` + `migrate` no build

### Passos no painel Railway (só você)

1. Criar conta em https://railway.app
2. **New Project** → **Deploy from GitHub** → selecionar este repositório
3. **+ New** → **Database** → **PostgreSQL**
4. Na service **web**, em **Variables** → **Add Reference** → ligar `DATABASE_URL` ao Postgres
5. Adicionar variáveis:
   - `SECRET_KEY` — chave aleatória longa (obrigatório)
   - `DEBUG` — `False`
6. **Settings** → **Networking** → **Generate Domain**
7. Aguardar o deploy (o domínio entra em `ALLOWED_HOSTS` e `CSRF` automaticamente)
8. (Opcional) Criar admin: **Settings** → abrir shell/one-off ou usar CLI:
   ```bash
   python manage.py createsuperuser
   ```

Gerar `SECRET_KEY` localmente:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Deploy no Render

O arquivo `render.yaml` continua disponível como alternativa ao Railway.

## Banco de dados

- **Local:** SQLite (padrão sem `DATABASE_URL`)
- **Produção:** PostgreSQL via `DATABASE_URL`
