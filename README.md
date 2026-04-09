# SIGAD - Sistema de Gestão de Doações

Projeto Django criado com base nas telas enviadas.

## Como executar

1. Crie um ambiente virtual:
   python -m venv venv

2. Ative o ambiente virtual:
   - Windows: venv\Scripts\activate
   - Linux/macOS: source venv/bin/activate

3. Instale as dependências:
   pip install -r requirements.txt

4. Aplique as migrações:
   python manage.py migrate

5. Rode o servidor:
   python manage.py runserver

6. Acesse:
   http://127.0.0.1:8000/

## Rotas
- /
- /registrar-item/
- /registrar-distribuicao/
- /estoque/
- /beneficiarios/
- /relatorios/

## Observação
Os dados estão mockados nas views para facilitar sua apresentação inicial. Depois você pode conectar com os models e formulários reais.
