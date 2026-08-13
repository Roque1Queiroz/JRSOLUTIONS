# Contexto Atual

## Projeto
MEI Gestao

## Data de referencia
2026-04-15

## Etapa atual
Financeiro

## Tarefa atual
F1 - iniciar o fluxo dedicado de Receitas no modulo financeiro

## Skills instaladas no Codex
- 1-hm-init
- 2-hm-designer
- 3-hm-engineer
- 4-hm-qa
- 5-hm-deploy

## Skill preferida para a proxima sessao
- 3-hm-engineer para implementacao
- 4-hm-qa para revisao

## Estado atual do projeto
- As skills personalizadas foram copiadas para `C:\Users\roque\.codex\skills`.
- O financeiro atual usa o modelo `Transacao` para receitas e despesas.
- O menu atual aponta para `financeiro:transacao_lista`.
- A documentacao antiga indica que o primeiro bloco em aberto e o CRUD completo de Receitas.
- Os testes atuais de `meigestao_app\financeiro\test_financeiro.py` passaram no ambiente local.

## Hipotese de trabalho para F1
Criar um recorte dedicado de Receitas em cima do modelo `Transacao`, sem quebrar:
- fluxo de caixa atual
- integracao com vendas
- integracao com reembolsos
- testes existentes do financeiro

## Arquivos relevantes
- `meigestao_app/financeiro/models.py`
- `meigestao_app/financeiro/views.py`
- `meigestao_app/financeiro/forms.py`
- `meigestao_app/financeiro/urls.py`
- `templates/meigestao_app/financeiro/transacao_list.html`
- `templates/meigestao_app/financeiro/transacao_form.html`
- `templates/meigestao_app/financeiro/transacao_detail.html`
- `templates/base.html`
- `meigestao_app/financeiro/test_financeiro.py`

## Proximo passo recomendado
Implementar a F1 criando listagem, cadastro, detalhe e edicao de Receitas como views/rotas dedicadas, reaproveitando `Transacao` com filtro `tipo='receita'`.

## Prompt sugerido para nova sessao
Leia `docs/CONTEXTO_ATUAL.md` e continue a tarefa F1 usando a skill `3-hm-engineer`.

