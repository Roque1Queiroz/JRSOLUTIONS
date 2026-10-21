# Spec — Nosso boleto (conta parcelada)

| Campo | Valor |
|---|---|
| **Versão** | 1.0 |
| **Status** | aprovado — na fila, ainda não implementar |
| **Autor** | José Roque / Hermes |
| **Data** | 2026-10-09 |
| **Módulos afetados** | financeiro |
| **Plano** | todos (o financeiro não está bloqueado no plano básico) |

DECISÃO (José, ok em 2026-10-09): não é boleto bancário. É folha interna para acompanhar gasto parcelado. Fechar a spec e colocar na fila das atualizações. Não codar até ele mandar executar a fila.

---

## 1. Objetivo (por que?)

Gasto que nasce parcelado (empréstimo, compra a prazo, conta) hoje vira lançamento solto ou não é lançado. O gestor precisa ver o que vence, o que já foi pago e o que falta, e imprimir uma folha nossa de cada parcela.

## 2. Contexto / Cenário atual

Inspecionado em `meigestao_app/financeiro/` em 2026-10-09:

- `Transacao` é um lançamento só: tipo, valor, `data_vencimento`, `paga`. Não há parcela nem agrupamento.
- Não existe model, rota ou tela de boleto, empréstimo ou parcelamento.
- `core/asaas.py` cobra só a assinatura do Sistema Gestor (PIX). Não fatura cliente e não gera parcela de empréstimo.
- Quem cria lançamento financeiro é quem pode alterar o módulo `financeiro` (gerente e admin). Vendedor e operador não entram.
- Plano básico bloqueia fiscal, almoxarifado, compras, serviços, produção e relatórios. Financeiro permanece liberado.

## 3. Escopo

- **Incluído:**
  - Cadastrar um compromisso a pagar: descrição, credor, valor total, número de parcelas, primeiro vencimento.
  - O sistema gera as parcelas iguais, com vencimento mês a mês.
  - Cada parcela tem o nosso boleto: folha interna para imprimir, com referência, parcela X de N, valor e vencimento.
  - Marcar e desmarcar parcela como paga.
  - Ao marcar paga, nascer uma despesa no financeiro já existente, ligada à parcela, para o caixa não ficar cego.
  - Tela do compromisso: a vencer, vencida, paga e saldo que falta.
- **Excluído (não-escopo):**
  - Boleto bancário, código de barras, linha digitável, CNAB, convênio, Asaas.
  - Cálculo de juros, tabela Price ou SAC. O valor total informado já é o que será dividido.
  - Parcela de receita / cobrança de cliente.
  - Parcela com valor diferente uma da outra.
  - Pacote de textos do admin e nota discreta.

## 4. Requisitos Funcionais (o que o sistema FAZ)

- RF1 — Gerente ou admin, no financeiro, cadastra o compromisso e o sistema cria as parcelas.
- RF2 — A soma dos valores das parcelas é igual ao valor total. Sobra de centavo fica na última parcela.
- RF3 — O vencimento da parcela 1 é o primeiro vencimento. As seguintes caem no mesmo dia dos meses seguintes. Se o dia não existir naquele mês, cai no último dia do mês.
- RF4 — A lista mostra em aberto, vencida (vencimento anterior a hoje e não paga) e paga, e o saldo que falta.
- RF5 — Abrir o nosso boleto de uma parcela mostra referência, credor, descrição, parcela X de N, valor e vencimento, e dá para imprimir. Sem código de barras.
- RF6 — Marcar como paga grava a data do pagamento e cria uma `Transacao` despesa da mesma empresa, valor e vencimento, já paga, ligada à parcela.
- RF7 — Desmarcar paga deixa a despesa ligada como não paga. Não apaga o histórico.
- RF8 — Não excluir compromisso que tenha parcela paga. Primeiro desmarcar.

## 5. Requisitos Não-Funcionais

- Isolamento por empresa: um usuário não vê nem altera compromisso de outra empresa.
- Mesma permissão do financeiro: ver para quem já vê o módulo; criar, editar e marcar paga para quem já altera; excluir para quem já exclui.
- Nomes em português com acento no admin (`verbose_name` e `verbose_name_plural` explícitos).
- A folha imprime no navegador. Não depende de biblioteca nova.

## 6. Dados / Modelo

Dois modelos novos em `meigestao_app/financeiro/models.py`.

**CompromissoParcelado**

- `empresa` — obrigatório, a empresa do usuário.
- `descricao` — o que é (empréstimo, compra, conta).
- `credor` — quem recebe (banco, loja). Pode ficar em branco.
- `valor_total` — maior que zero, 2 casas.
- `numero_parcelas` — inteiro de 2 a 120.
- `primeiro_vencimento` — data.
- `observacao` — opcional.

**ParcelaCompromisso**

- `compromisso` — vínculo.
- `numero` — 1..N, único dentro do compromisso.
- `valor` — 2 casas.
- `vencimento` — data.
- `paga` — não, por padrão.
- `data_pagamento` — vazia até pagar.
- `transacao` — vínculo opcional com `Transacao`.
- `referencia` — `NB-{id do compromisso}-{número com 2 dígitos}`. Única.

Regras travadas:

- Divisão igual. Última parcela absorve o centavo.
- Sem juros.
- Referência nasce com a parcela e não muda.

## 7. Fluxo / Telas

1. Financeiro → Parcelas → Novo compromisso.
2. Informa descrição, credor, total, quantidade e primeiro vencimento. Salva.
3. Abre o compromisso com a lista de parcelas e o saldo.
4. Em cada parcela: abrir nosso boleto, ou marcar paga.
5. Nosso boleto: página simples, botão imprimir.

Rotas previstas, no app `financeiro`:

- `parcelas/` — lista
- `parcelas/nova/` — criar
- `parcelas/<id>/` — detalhe
- `parcelas/<id>/boleto/<parcela_id>/` — folha
- `parcelas/<id>/pagar/<parcela_id>/` — marcar ou desmarcar

## 8. Segurança / Restrições por Plano e Empresa

- Sempre filtrar pela empresa do usuário logado. Superuser sem perfil continua sem empresa: não cria compromisso (mesmo limite já conhecido do financeiro).
- Plano: todos os que já acessam financeiro, inclusive básico.
- Trial expirado continua bloqueado pelo middleware atual. Esta função não abre exceção.

## 9. Critérios de Aceite (TESTES — o "check")

- CA1 — Criar compromisso de R$ 100,00 em 3 parcelas com primeiro vencimento 31/01 gera parcelas de 33,33 + 33,33 + 33,34, vencendo 31/01, 28/02 (ou 29 em ano bissexto) e 31/03.
- CA2 — A soma das parcelas é exatamente o valor total.
- CA3 — Recusar 1 parcela, 121 parcelas e valor zero.
- CA4 — Usuário da empresa A não vê compromisso da empresa B (lista, detalhe e boleto).
- CA5 — Vendedor recebe 403 ao criar.
- CA6 — Marcar paga cria `Transacao` despesa da mesma empresa, ligada, com `paga=True`. Desmarcar deixa `paga=False` e não apaga a transação.
- CA7 — Excluir compromisso com parcela paga é recusado.
- CA8 — A folha do nosso boleto contém a referência, "parcela X de N", o valor e o vencimento, e não contém código de barras nem linha digitável.
- CA9 — A suíte do financeiro que já existe continua verde.

## 10. Riscos / Dependências

- Risco: despesa da parcela duplicar um lançamento que o usuário já fez na mão. Mitigação: a despesa só nasce ao marcar paga, e a tela deixa claro que o pagamento entra no caixa.
- Não depende de Asaas, banco ou CNPJ.
- Implementar só quando José mandar executar a fila. Método: branch `feature/nosso-boleto-parcelas`, um teste por critério, depois o código mínimo.

---

## Fluxo de trabalho

1. Spec escrita e aprovada em 2026-10-09.
2. Na fila: `docs/SPECS/FILA-ATUALIZACOES.md`.
3. Implementar só sob ordem, com TDD contra os CA.
4. Verificar, deploy com backup, validar ao vivo, então marcar esta spec como `implementado`.
