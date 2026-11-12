
---
name: padronizacao-commits
description: "Padroniza mensagens de commit do SIGAD usando Conventional Commits. Use ao criar, revisar ou corrigir mensagens de commit."
argument-hint: "Descreva as mudanças que serão commitadas"
---

# Padronização de commits

## Quando usar

- Criar mensagens para alterações no projeto.
- Revisar mensagens antes de executar git commit.
- Padronizar o histórico do Git.
- Preparar commits de código, documentação, testes, configurações e estilos.

## Formato obrigatório

Utilize o seguinte formato:

tipo(escopo): descrição curta no imperativo

O escopo é opcional.

## Tipos permitidos

- feat: adiciona uma funcionalidade.
- fix: corrige um problema.
- docs: altera documentação.
- test: adiciona ou modifica testes.
- refactor: reorganiza o código sem alterar seu comportamento.
- perf: melhora o desempenho.
- style: altera formatação ou estilos.
- build: altera dependências ou processo de build.
- ci: altera automações.
- chore: realiza tarefas de manutenção.

## Regras

- Escrever a mensagem em letras minúsculas.
- Utilizar até 72 caracteres quando possível.
- Não terminar a descrição com ponto final.
- Utilizar verbos no imperativo.
- Descrever a finalidade da alteração.
- Evitar mensagens genéricas como "alterações" ou "atualizações".

## Procedimento

1. Verificar o git status.
2. Analisar as alterações com git diff.
3. Identificar o objetivo principal das mudanças.
4. Escolher o tipo de commit adequado.
5. Definir um escopo relacionado ao projeto.
6. Criar uma mensagem curta e objetiva.
7. Revisar a mensagem antes de utilizá-la.

## Exemplos

feat(doacoes): adiciona cadastro de doações

fix(usuarios): corrige validação do formulário

docs: atualiza documentação do SIGAD

style(landing): ajusta layout da página inicial

build: atualiza dependências do projeto

## Checklist final

- A mensagem representa corretamente a alteração.
- O tipo está adequado.
- A descrição está em letras minúsculas.
- A mensagem é objetiva.
- Não contém senhas, tokens ou informações confidenciais.
- Não executar git add, git commit ou git push sem autorização explícita.
