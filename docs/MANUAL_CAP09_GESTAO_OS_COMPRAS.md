# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 9: Ordens de Serviço (O.S.) e Gestão de Compras

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Operacional > O.S. e Compras

---

## 📋 Índice deste Capítulo

1. [O que é uma Ordem de Serviço (O.S.)?](#1-o-que-é-uma-ordem-de-serviço-os)
2. [Tipos de Ordem de Serviço](#2-tipos-de-ordem-de-serviço)
3. [Como preencher uma O.S.](#3-como-preencher-uma-os)
4. [Gestão de Compras: Do Pedido ao Fornecedor](#4-gestão-de-compras-do-pedido-ao-fornecedor)
5. [A Mágica da Cotação (Mapas de Cotação)](#5-a-mágica-da-cotação-mapas-de-cotação)
6. [Perguntas Frequentes](#6-perguntas-frequentes)

---

## 1. O que é uma Ordem de Serviço (O.S.)?

Diferente de uma Venda normal (onde você entrega um produto e recebe dinheiro na hora), a **Ordem de Serviço (O.S.)** é um trabalho que leva um tempo para ser feito.

Pode ser consertar o carro de um cliente, instalar um ar condicionado, ou até mesmo arrumar uma máquina quebrada dentro da própria empresa.

A O.S. é o documento que registra tudo: **O que estragou, quem vai consertar, quanto tempo vai levar e quais peças foram usadas.**

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** → **Ordens de Serviço (O.S.)**.

---

## 2. Tipos de Ordem de Serviço

O sistema permite que você gerencie diferentes tipos de serviço:

| Tipo | O que é | Exemplo |
|------|---------|---------|
| 🔧 **Serviço ao Cliente** | Um trabalho pago feito para alguém de fora. | "Conserto da geladeira do Sr. João." |
| 🏗️ **Manufatura Interna** | Serviço de adaptação de peças internas. | "Montagem da estante do galpão." |
| ⚠️ **Manutenção Interna** | Conserto de algo da sua própria empresa. | "Arrumar a máquina de solda." |

---

## 3. Como preencher uma O.S.

1. Na tela de O.S., clique em **Nova O.S.**
2. Preencha os **Dados Iniciais:**
   - **Cliente:** (Obrigatório se for serviço externo).
   - **Responsável:** Quem é o técnico que fará o trabalho.
   - **Descrição do Problema:** O que o cliente relatou ("Fazendo barulho ao ligar").
3. Preencha a **Execução:**
   - **Laudo Técnico:** O que o técnico descobriu e fez ("Trocada a correia do motor").
   - **Valor do Serviço:** R$ da mão de obra.
   - **Itens consumidos:** Adicione as peças (do estoque) que foram gastas no conserto.
4. O sistema vai calcular automaticamente o **Valor Total** somando a Mão de Obra + Peças!

### O Fluxo da O.S.:
`Aberta` (cliente trouxe) ➡️ `Em Execução` (técnico trabalhando) ➡️ `Finalizada` (pronta) ou `Cancelada`.

---

## 4. Gestão de Compras: Do Pedido ao Fornecedor

Quando o seu estoque fica baixo ou a equipe pede algo no Almoxarifado que acabou, é hora de comprar.

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** → **Gestão de Compras**.

### Como funciona o processo de compra ideal:
1. Vá em **Fornecedores** e cadastre de quem você costuma comprar (Nome, CNPJ, Telefone).
2. Vá em **Pedidos de Compra** e clique em **Novo Pedido**.
3. Adicione os itens que você precisa e a data limite. O status começa como **Solicitado**.

---

## 5. A Mágica da Cotação (Mapas de Cotação)

Uma boa gestão financeira exige que você compare preços. Em vez de ficar com papéis espalhados pela mesa, use o **Mapa de Cotação** do sistema!

1. Abra um Pedido de Compra (que está com status "Em Cotação").
2. Adicione as ofertas dos fornecedores:
   - *Fornecedor A cobrou R$ 100 com entrega em 2 dias.*
   - *Fornecedor B cobrou R$ 80 com entrega em 5 dias.*
3. O sistema permite você anexar o PDF do orçamento deles!
4. **Marque o Vencedor:** Escolha qual fornecedor ganhou a concorrência.
5. Mude o status do Pedido para **Aprovado**.

Quando a mercadoria chegar na sua porta, você abre o pedido e muda o status para **"Recebido"**.

---

## 6. Perguntas Frequentes

### ❓ "A O.S. dá baixa no estoque das peças que eu usei no conserto?"
Sim! Assim que a O.S. é finalizada com itens consumidos listados, o sistema entende que aquelas peças foram gastas e atualiza o seu estoque automaticamente.

### ❓ "Posso usar a Gestão de Compras só para registrar o que já comprei?"
Pode. Você pode criar o pedido e imediatamente colocá-lo como "Recebido". Porém, usar as ferramentas de Cotação e Status vai te dar muito mais controle e economia no futuro.

### ❓ "Como crio uma conta a pagar para o Fornecedor que ganhou a cotação?"
Vá no módulo **Financeiro**, clique em "Gestão de Caixa" e crie uma nova "Despesa" em nome do fornecedor com a data combinada.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
