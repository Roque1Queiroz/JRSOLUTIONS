# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 6: Gestão Fiscal (Notas Fiscais)

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Fiscal > Gestão de Notas

---

## 📋 Índice deste Capítulo

1. [Visão Geral do Módulo Fiscal](#1-visão-geral-do-módulo-fiscal)
2. [O Ciclo de Vida de uma Nota Fiscal](#2-o-ciclo-de-vida-de-uma-nota-fiscal)
3. [O Truque de Ouro: Gerar NF a partir da Venda](#3-o-truque-de-ouro-gerar-nf-a-partir-da-venda)
4. [Como Criar uma Nota Fiscal Avulsa (Manual)](#4-como-criar-uma-nota-fiscal-avulsa-manual)
5. [Como Cancelar uma Nota Fiscal](#5-como-cancelar-uma-nota-fiscal)
6. [Regras e Validações do Sistema](#6-regras-e-validações-do-sistema)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. Visão Geral do Módulo Fiscal

A Gestão Fiscal é a parte mais "séria" do sistema. Diferente das Vendas e Orçamentos que servem para controle interno, a Nota Fiscal é o seu comprovante legal para o Governo.

O sistema ajuda você a não esquecer os números, calcular impostos básicos e organizar os documentos sem precisar usar aquelas antigas planilhas do Excel.

> **Acesso:** No Menu Lateral, vá em **Gestão Fiscal** → **Gestão de Notas**.

---

## 2. O Ciclo de Vida de uma Nota Fiscal

Assim como as vendas, as Notas Fiscais passam por estágios. Você não pode simplesmente "excluir" uma nota oficial. Entenda os três status:

| Status | Como aparece | O que você pode fazer |
|--------|--------------|-----------------------|
| 📝 **Rascunho** | Cinza/Amarelo | É a fase de digitação. A nota **ainda não tem validade fiscal**. Você pode editar valores, cliente, impostos livremente ou até apagar. |
| ✅ **Emitida** | Verde | A nota "valeu". Ela passa a compor seu faturamento fiscal oficial. **Você não pode mais editar uma nota Emitida**. Se algo estiver errado, você precisará cancelá-la. |
| ❌ **Cancelada**| Vermelho | O negócio foi desfeito. O valor dela "zera" nos seus relatórios fiscais. |

---

## 3. O Truque de Ouro: Gerar NF a partir da Venda

A forma mais fácil e rápida de criar uma Nota Fiscal no Sistema Gestor é **NÃO** usando o Módulo Fiscal!

Em vez de digitar tudo de novo, use a inteligência do sistema a seu favor:

1. Vá em **Gestão Comercial** → **Gestão de Vendas**.
2. Abra a Venda (clicando nela) para a qual você quer emitir a nota.
3. Clique no botão mágico **"Gerar Nota Fiscal"**.

**O que o sistema faz?**
Ele pula o trabalho pesado! O sistema puxa automaticamente: o Cliente, a Data, os Produtos, o Subtotal e o Valor Total. E o melhor: ele já deixa a NF vinculada àquela Venda. Tudo o que você precisa fazer é revisar e confirmar a Emissão.

---

## 4. Como Criar uma Nota Fiscal Avulsa (Manual)

Se você precisa emitir uma NF que não está atrelada a uma Venda específica (ex: uma nota de demonstração ou correção):

1. Vá em **Gestão Fiscal** → **Gestão de Notas**.
2. Clique no botão **"Nova Nota Fiscal"**.
3. Preencha o formulário:
   - **Cliente:** Selecione na lista (Obrigatório).
   - **Venda vinculada:** (Pode deixar em branco neste caso).
   - **Número e Série:** Digite a numeração fiscal sequencial da sua empresa (Obrigatório).
   - **Data de Emissão e Saída:** Quando a nota foi gerada e quando o produto saiu.
   - **Descrição dos Itens:** Detalhe o que está sendo faturado.
   - **Impostos (ICMS / IPI):** Se a sua contabilidade exigir, digite os valores em Reais (R$).
4. O sistema calcula a matemática final sozinho: `(Subtotal - Desconto) + ICMS + IPI`.
5. Salve. A nota será criada como **Rascunho**.
6. Para finalizar, abra a nota salva e clique no botão **"Emitir NF"**.

---

## 5. Como Cancelar uma Nota Fiscal

Uma vez emitida, a nota trava para edições para evitar fraudes. Se o cliente desistiu da compra ou você digitou algo errado:

1. Abra a Nota Fiscal (que está com o status ✅ **Emitida**).
2. Clique no botão **"Cancelar NF"**.
3. O status dela mudará para ❌ **Cancelada** e o valor não somará mais nos seus relatórios.

---

## 6. Regras e Validações do Sistema

O módulo fiscal te impede de cometer erros matemáticos ou contábeis graves:

- 🛑 **Você não pode ter valores negativos.**
- 🛑 **O Desconto não pode ser maior que o Subtotal** (o sistema não deixa você dar um desconto maior do que o valor do produto em uma NF).
- 🛑 **Viagem no tempo:** A "Data de Saída" não pode ser *antes* da "Data de Emissão".

Se você tentar fazer alguma destas coisas, o sistema bloqueará a ação e mostrará um erro vermelho pedindo para você corrigir.

---

## 7. Perguntas Frequentes

### ❓ "Por que não tem botão de Lixeira (Excluir) na minha Nota Fiscal?"
Por regras contábeis, documentos fiscais oficiais não "somem". Se a nota já foi Emitida, ela deve ser **Cancelada**. Você só consegue excluir (apagar do sistema) notas que ainda estejam na fase de **Rascunho**.

### ❓ "O sistema envia a nota direto para a Receita Federal / Sefaz?"
Na versão atual, o sistema gera o controle e o cálculo financeiro/fiscal interno da sua empresa. Para a transmissão direta de arquivos XML, consulte o plano contratado da sua empresa ou repasse o Relatório Fiscal gerado pelo sistema para o seu contador.

### ❓ "A nota não aparece no meu faturamento do Dashboard. Por quê?"
Lembre-se da regra de ouro: O faturamento principal no Dashboard é puxado do módulo de **Vendas** e da **Gestão de Caixa**. A tela Fiscal é um controle paralelo exigido por lei. Sempre faça Vendas no módulo comercial!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
