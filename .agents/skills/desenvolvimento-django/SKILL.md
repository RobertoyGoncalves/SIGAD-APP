
---
name: desenvolvimento-django
description: "Orienta a criação, manutenção e correção de funcionalidades Django no SIGAD."
---

# Skill de desenvolvimento Django

## Objetivo

Padronizar o desenvolvimento e a manutenção do sistema SIGAD utilizando Django.

## Regras gerais

- Analisar os arquivos existentes antes de realizar alterações.
- Preservar funcionalidades já implementadas.
- Seguir a estrutura atual do projeto.
- Evitar duplicação de código.
- Utilizar nomes claros para classes, funções e variáveis.

## Models

- Utilizar models para representar os dados do sistema.
- Definir corretamente os campos e relacionamentos.
- Criar migrations após alterações nos models.
- Não excluir campos ou tabelas sem autorização.

## Views

- Utilizar views para processar requisições.
- Separar responsabilidades sempre que possível.
- Validar dados recebidos dos formulários.
- Aplicar autenticação e permissões quando necessário.

## Templates

- Reutilizar templates base existentes.
- Utilizar a linguagem de templates do Django.
- Manter HTML organizado e semântico.
- Preservar a identidade visual do SIGAD.

## URLs

- Manter as rotas organizadas.
- Utilizar nomes para as URLs.
- Evitar conflitos entre caminhos existentes.

## Segurança

- Preservar a proteção CSRF.
- Nunca expor senhas ou chaves secretas.
- Não desativar autenticação sem autorização.
- Validar dados antes de salvar no banco.

## Testes

Após alterações:

1. Executar `python manage.py check`.
2. Executar migrations, se necessário.
3. Testar as funcionalidades modificadas.
4. Verificar se outras funcionalidades continuam funcionando.
