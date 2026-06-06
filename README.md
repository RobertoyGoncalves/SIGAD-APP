# SIGAD-APP

projeto django com telas para estoque, beneficiarios e distribuicoes.

## como executar

1. ambiente virtual:
   `python -m venv venv`

2. ativar:
   - windows: `venv\Scripts\activate`
   - linux/macos: `source venv/bin/activate`

3. dependencias:
   `pip install -r requirements.txt`

4. migracoes:
   `python manage.py migrate`

5. servidor:
   `python manage.py runserver`

6. abrir:
   `http://127.0.0.1:8000/`

## rotas principais

- `/`
- `/registrar-item/`
- `/registrar-distribuicao/`
- `/estoque/`
- `/beneficiarios/`
- `/relatorios/`
- `/admin/`

## observacao

os dados ficam no banco configurado (sqlite local ou postgres via `database_url` no `.env`).
