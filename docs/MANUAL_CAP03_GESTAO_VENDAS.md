# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 3: Gestão de Vendas

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Comercial > Gestão de Vendas

---

## 📋 Índice deste Capítulo

1. [Visão Geral: O Coração do Negócio](#1-visão-geral-o-coração-do-negócio)
2. [Entendendo os Status da Venda](#2-entendendo-os-status-da-venda)
3. [Como Registrar uma Nova Venda](#3-como-registrar-uma-nova-venda)
4. [A Mágica da Automação (Estoque e Financeiro)](#4-a-mágica-da-automação-estoque-e-financeiro)
5. [Como Gerar Nota Fiscal da Venda](#5-como-gerar-nota-fiscal-da-venda)
6. [Cancelando ou Excluindo uma Venda](#6-cancelando-ou-excluindo-uma-venda)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. Visão Geral: O Coração do Negócio

A **Gestão de Vendas** é o módulo onde o dinheiro entra. Ele não é apenas um "bloco de pedidos", ele é o gatilho que movimenta toda a sua empresa.

Ao fazer uma venda no sistema, você não precisa dar baixa manual no estoque nem lançar o valor manual no financeiro: **o sistema faz tudo isso sozinho**.

> **Acesso:** No Menu Lateral, vá em **Gestão Comercial** → **Gestão de Vendas**.

---

## 2. Entendendo os Status da Venda

Toda venda possui um "Status" (situação atual). É muito importante entender a diferença entre eles, pois o sistema reage de forma diferente para cada um:

| Status | Como aparece | O que significa e o que faz no sistema |
|--------|--------------|----------------------------------------|
| **Rascunho** | 🟡 Amarelo | É apenas um orçamento. **NÃO** tira produto do estoque e **NÃO** gera receita no financeiro. Você pode editar à vontade. |
| **Confirmada** | 🟢 Verde | O cliente fechou negócio! O sistema **TIRA** o produto do estoque e **CRIA** uma transação de Receita no Financeiro. |
| **Entregue** | 🔵 Azul | O cliente já recebeu a mercadoria. Financeiramente e no estoque, é a mesma coisa que "Confirmada". |
| **Cancelada** | 🔴 Vermelho | A venda deu errado. O sistema **DEVOLVE** o produto para o estoque e **ESTORNA** (cancela) o lançamento no Financeiro. |

> [!TIP]
> Se um cliente pediu um orçamento, crie a venda como **Rascunho**. Quando ele aprovar e pagar, basta editar a venda e mudar para **Confirmada**!

---

## 3. Como Registrar uma Nova Venda

Para registrar uma venda (ou orçamento), siga o passo a passo:

### Passo 1: Iniciar
Na tela de Vendas, clique no botão azul **"Nova Venda"**.

### Passo 2: Dados Principais
- **Cliente:** Selecione o cliente na lista. (Se o cliente for novo, você precisa cadastrá-lo primeiro no módulo de Clientes).
- **Data da Venda:** O sistema preenche com a data de hoje automaticamente, mas você pode mudar se estiver lançando uma venda retroativa.
- **Status:** Escolha o status (Rascunho, Confirmada, etc).

### Passo 3: Adicionar Produtos (Itens da Venda)
Esta é a parte mais importante. Você vai adicionar os produtos que o cliente está comprando:

1. No campo **Produto**, escolha o produto do seu estoque ou digite o nome do item.
2. Informe a **Quantidade**.
3. O **Preço Unitário** virá automaticamente do cadastro do produto (mas você pode alterar o valor na hora da venda, se quiser dar um desconto específico no item).
4. O sistema calculará o **Subtotal** (Qtd × Preço).
5. Para adicionar mais produtos, clique em **"+ Adicionar Item"**.

### Passo 4: Fechamento
- O **Subtotal** da venda é somado automaticamente.
- **Desconto (R$):** Se quiser dar um desconto no valor final, digite aqui.
- O **Valor Total** é calculado sozinho (Subtotal - Desconto).

Clique em **"Salvar"**.

---

## 4. A Mágica da Automação (Estoque e Financeiro)

Como dito na visão geral, a venda automatiza o trabalho chato. 

### O que acontece no exato segundo que você salva uma venda como "Confirmada"?

✅ **No Estoque:** O sistema vai silenciosamente até o módulo de estoque e dá baixa nas quantidades vendidas.
*Exemplo: Se você tinha 10 cadernos e vendeu 2, o estoque cai para 8 na hora.*

✅ **No Financeiro:** O sistema vai ao módulo de Gestão de Caixa e cria um registro de "Receita", vinculando o valor ao cliente. O faturamento no seu Dashboard vai subir imediatamente!

---

## 5. Como Gerar Nota Fiscal da Venda

Você fechou a venda e agora o cliente quer a Nota Fiscal? É simples:

1. Abra a venda que você acabou de salvar.
2. Na tela de detalhes da venda, haverá um botão chamado **"Gerar Nota Fiscal"**.
3. Clique nele.
4. O sistema vai pegar **todos os dados do cliente, os produtos e os valores** e preencher a Nota Fiscal para você no módulo Fiscal.
5. Lá, você só precisará conferir os impostos e clicar em "Emitir".

> [!IMPORTANT]
> Para a Nota Fiscal sair certinha, o cliente precisa estar com CPF/CNPJ e Endereço devidamente preenchidos no cadastro dele!

---

## 6. Cancelando ou Excluindo uma Venda

Errar é humano. Se você registrou uma venda errada, você tem duas opções:

### A opção correta: Cancelar (Mudar Status)
Abra a venda, clique em **Editar** e mude o status para **Cancelada**. 
Por que isso é melhor?
1. Fica o registro histórico de que a venda existiu mas não deu certo.
2. O sistema inteligentemente **devolve** os itens para o estoque.
3. O sistema **estorna** a entrada de dinheiro no caixa.

### A opção drástica: Excluir (Lixeira 🗑️)
Se você clicar no ícone de lixeira, a venda some para sempre. O sistema também tem inteligência para desfazer o estoque e o financeiro caso você faça isso, mas você perde o histórico. Use apenas para vendas "teste" ou lançadas em duplicidade por erro.

---

## 7. Perguntas Frequentes

### ❓ "Tentei vender um produto e deu erro dizendo 'Estoque insuficiente'."
O sistema te protege de vender algo que você não tem. Se o erro aparecer, você precisa primeiro ir no módulo de **Produtos** e dar "Entrada" na quantidade deste item no estoque.

### ❓ "O cliente pediu um orçamento, mas ainda não vai pagar. O que eu faço?"
Crie a Venda e marque o Status como **Rascunho**. O rascunho não mexe no seu estoque nem no seu caixa.

### ❓ "O preço do meu produto mudou só pra esse cliente. Preciso mudar o cadastro do produto?"
Não! Na hora de adicionar o "Item da Venda", você pode apagar o Preço Unitário sugerido e digitar o preço novo. Isso afeta **apenas esta venda**.

### ❓ "A venda não gerou receita no financeiro, por quê?"
Verifique o **Status** da venda. Vendas em "Rascunho" ou "Cancelada" não geram receita. Apenas "Confirmada" ou "Entregue".

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
