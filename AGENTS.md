

\# AGENTS.md



\## 1. Sobre o projeto



O SIGAD (Sistema de Gestão e Administração de Doações) é uma aplicação web desenvolvida para auxiliar organizações não governamentais (ONGs) no gerenciamento de doações.



O sistema busca facilitar o cadastro, a organização, o controle e a distribuição de doações, contribuindo para uma gestão mais eficiente e transparente.



\## 2. Tecnologias utilizadas



\- Python

\- Django

\- HTML5

\- CSS3

\- JavaScript

\- jQuery

\- Bootstrap

\- SQLite (ambiente de desenvolvimento)

\- Git e GitHub



\## 3. Estrutura do projeto



\- `manage.py`: arquivo principal para executar comandos do Django.

\- `sigad/`: configurações principais do projeto Django.

\- `sigad\_app/`: aplicação principal do sistema.

\- `sigad\_app/templates/`: páginas HTML e templates.

\- `sigad\_app/static/`: arquivos CSS, JavaScript e imagens.

\- `requirements.txt`: dependências Python do projeto.

\- `staticfiles/`: arquivos estáticos coletados pelo Django.



Antes de criar novos arquivos ou pastas, verifique a estrutura existente e siga o padrão utilizado no projeto.



\## 4. Orientações para desenvolvimento



\- Antes de modificar qualquer arquivo, analise sua implementação atual.

\- Preserve funcionalidades que já estão funcionando.

\- Evite duplicar códigos e funcionalidades.

\- Utilize os padrões já existentes no projeto.

\- Mantenha o código organizado e de fácil compreensão.

\- Utilize nomes claros para variáveis, funções e classes.

\- Faça alterações pequenas e relacionadas ao requisito solicitado.

\- Não remova funcionalidades sem autorização.



\## 5. Orientações para Django



\- Utilize o padrão de arquitetura do Django.

\- Mantenha as rotas organizadas nos arquivos `urls.py`.

\- Utilize views para controlar as requisições.

\- Utilize templates para apresentar as páginas.

\- Utilize models para representar os dados do sistema.

\- Crie migrations sempre que houver alterações nos models.

\- Utilize os recursos de autenticação e permissões do Django quando necessário.



\## 6. Front-end



\- Utilize HTML semântico.

\- Mantenha os arquivos CSS separados dos templates sempre que possível.

\- Organize os arquivos JavaScript em suas pastas correspondentes.

\- Preserve a identidade visual existente do SIGAD.

\- Utilize Bootstrap e jQuery seguindo os padrões já adotados.

\- Verifique a responsividade das páginas após alterações visuais.



\## 7. Segurança



\- Nunca exponha senhas, tokens ou chaves secretas.

\- Não envie arquivos `.env` para o GitHub.

\- Não desative mecanismos de autenticação sem autorização.

\- Valide os dados recebidos dos formulários.

\- Utilize proteção CSRF nos formulários Django.

\- Não altere configurações de segurança sem necessidade.



\## 8. Comandos importantes



Executar o servidor:



```bash

python manage.py runserver

```



Aplicar migrations:



```bash

python manage.py migrate

```



Criar migrations:



```bash

python manage.py makemigrations

```



Verificar problemas no projeto:



```bash

python manage.py check

```



Coletar arquivos estáticos:



```bash

python manage.py collectstatic --noinput

```



Instalar dependências:



```bash

python -m pip install -r requirements.txt

```



\## 9. Banco de dados



\- Não apague o banco de dados sem autorização.

\- Não remova migrations existentes sem analisar suas consequências.

\- Preserve os dados cadastrados durante as alterações.

\- Utilize migrations para modificar a estrutura do banco.



\## 10. Git e commits



\- Utilize commits com mensagens claras e objetivas.

\- Faça commits relacionados a alterações específicas.

\- Não envie arquivos desnecessários ao repositório.

\- Não execute `git push` sem autorização explícita.

\- Não altere commits existentes sem autorização.



\## 11. Validação das alterações



Após implementar uma funcionalidade:



1\. Verifique se o código não apresenta erros.

2\. Execute `python manage.py check`.

3\. Execute as migrations, caso necessário.

4\. Teste a funcionalidade no navegador.

5\. Verifique se as funcionalidades anteriores continuam funcionando.



\## 12. Regra principal



Toda alteração deve respeitar a estrutura e os padrões existentes no SIGAD.



A prioridade é manter o sistema funcional, seguro, organizado e de fácil manutenção, evitando mudanças desnecessárias.



