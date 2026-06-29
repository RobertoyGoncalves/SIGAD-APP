# SIGAD-APP

Sistema Django de gestão de doações — estoque, beneficiários, beneficiados, distribuições e relatórios.

## Glossário

| Termo | Papel |
|-------|-------|
| **Beneficiário** | Quem **DOA** itens ao estoque |
| **Beneficiado** | Quem **RECEBE** itens na distribuição |
| **Doação** | Entrada de itens no estoque trazida por um beneficiário |
| **Distribuição** | Saída de itens do estoque para um beneficiado |

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

| URL | Nome | Descrição |
|-----|------|-----------|
| `/` | `landing` | Landing page pública |
| `/dashboard/` | `dashboard` | Painel do sistema |
| `/registrar-item/` | `registrar_item` | Cadastrar item no estoque (com select de beneficiário) |
| `/estoque/` | `estoque` | Estoque com busca e filtro por categoria |
| `/listar/itens-estoque/` | `item_estoque_list` | Listagem CRUD do estoque |
| `/beneficiarios/` | `beneficiario_list` | Beneficiários com histórico de doações + criar inline |
| `/editar/beneficiario/<pk>/` | `beneficiario_update` | Editar beneficiário |
| `/excluir/beneficiario/<pk>/` | `beneficiario_delete` | Excluir beneficiário |
| `/beneficiados/` | `beneficiado_list` | Listagem de beneficiados com busca |
| `/cadastrar/beneficiado/` | `beneficiado_create` | Cadastrar beneficiado |
| `/ver/beneficiado/<pk>/` | `beneficiado_detail` | Detalhe do beneficiado + histórico de distribuições |
| `/editar/beneficiado/<pk>/` | `beneficiado_update` | Editar beneficiado |
| `/excluir/beneficiado/<pk>/` | `beneficiado_delete` | Excluir beneficiado |
| `/registrar-distribuicao/` | `registrar_distribuicao` | Registrar distribuição (select beneficiado + criar inline + baixa estoque) |
| `/listar/distribuicoes/` | `distribuicao_list` | Listagem de distribuições |
| `/ver/distribuicao/<pk>/` | `distribuicao_detail` | Detalhe da distribuição |
| `/listar/linhas-distribuicao/` | `linha_distribuicao_list` | Linhas de distribuição |
| `/relatorios/` | `relatorios` | Relatórios: semanal, mensal, por beneficiário, beneficiado e categoria + export xlsx |
| `/admin/` | — | Django Admin |

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
7. Aguardar o deploy
8. (Opcional) Criar admin:
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

## Histórico de refatorações

| Versão | O que mudou |
|--------|-------------|
| v1.1 | `Beneficiario` (antigo, quem recebia) renomeado para `Beneficiado`; novo modelo `Beneficiario` criado para quem doa; `ItemEstoque.doador` (CharField) substituído por `ItemEstoque.beneficiario` (FK); `Distribuicao.beneficiario` renomeado para `Distribuicao.beneficiado`; tela de registrar distribuição reconectada com baixa atômica de estoque e criação inline de beneficiado |
