# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 4: Gestão de Produtos e Estoque

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão de Estoque > Gestão de Produtos

---

## 📋 Índice deste Capítulo

1. [Visão Geral do Estoque](#1-visão-geral-do-estoque)
2. [Como Cadastrar um Novo Produto](#2-como-cadastrar-um-novo-produto)
3. [Entendendo a Margem de Lucro](#3-entendendo-a-margem-de-lucro)
4. [Como Funciona o Controle de Estoque](#4-como-funciona-o-controle-de-estoque)
5. [Fazendo Movimentações (Entradas e Saídas manuais)](#5-fazendo-movimentações-entradas-e-saídas-manuais)
6. [O que significa "Estoque Baixo"?](#6-o-que-significa-estoque-baixo)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. Visão Geral do Estoque

O módulo de **Produtos** é o seu catálogo. Aqui você cadastra tudo o que sua empresa vende para os clientes.

> **Importante:** Não confunda este módulo com o **Almoxarifado**! 
> - **Gestão de Produtos:** É o que você **VENDE** e dá lucro (ex: Capa de Celular, Consulta Médica, Cadeira).
> - **Almoxarifado:** É o que você **CONSOME** trabalhando (ex: Papel A4, Café, Ferramentas de uso interno).

> **Acesso:** No Menu Lateral, vá em **Gestão de Estoque** → **Gestão de Produtos**.

---

## 2. Como Cadastrar um Novo Produto

Para que você possa vender algo no sistema, o produto precisa existir aqui primeiro.

1. Na tela de Produtos, clique no botão azul **"Novo Produto"**.
2. Preencha o formulário com bastante atenção:

### Campos do Cadastro:

| Campo | O que é | Exemplo / Dica |
|-------|---------|----------------|
| **Nome** | O nome oficial do produto. | `Camiseta Branca Básica M` |
| **SKU** | O "Código de Barras" ou código interno. | `CAM-BR-M-001`. Se você deixar em branco, o sistema cria um automaticamente para você! |
| **Categoria** | Para organizar seu catálogo. | `Roupas`, `Eletrônicos`, `Serviços` |
| **Preço de Custo** | Quanto você pagou para seu fornecedor. | `R$ 20,00` |
| **Preço de Venda** | Por quanto você vai vender para o cliente. | `R$ 50,00` |
| **Ativo** | Se o produto está disponível para venda. | Deixe marcado. |

3. Clique em **"Salvar"**.

---

## 3. Entendendo a Margem de Lucro

Ao preencher o Preço de Custo e o Preço de Venda, o sistema calcula a sua **Margem de Lucro** automaticamente na tela de detalhes do produto.

A fórmula que o sistema usa é:
`((Preço Venda - Preço Custo) / Preço Custo) × 100`

**Exemplo:**
- Você compra uma capinha por **R$ 10,00** (Custo)
- Vende por **R$ 25,00** (Venda)
- O sistema te mostrará um lucro de **150%**.

> [!WARNING]
> O sistema não deixa você colocar o Preço de Venda **MENOR** que o Preço de Custo. Se tentar, ele dará um erro, pois você estaria vendendo com prejuízo!

---

## 4. Como Funciona o Controle de Estoque

Cada produto que você cadastra ganha uma "ficha de estoque". Nela, você controla:

- **Quantidade Atual:** Quantos você tem hoje.
- **Quantidade Mínima:** Qual é o número de "alerta". (Ex: Se a qtde mínima é 5, quando chegar em 5 o sistema vai apitar avisando para comprar mais).
- **Localização:** Em qual prateleira ou corredor o produto está guardado fisicamente.

---

## 5. Fazendo Movimentações (Entradas e Saídas manuais)

No Capítulo 3, vimos que a Venda dá saída no estoque sozinha. Mas e quando você **compra** mercadoria do fornecedor ou **perde** uma mercadoria (ex: quebrou)? Você precisa fazer uma movimentação manual.

1. Clique no nome do Produto na lista.
2. Na aba de Estoque, clique em **"Nova Movimentação"**.
3. Escolha o tipo de movimento:

| Tipo | O que faz no saldo | Quando usar |
|------|--------------------|-------------|
| 🟢 **Entrada** | AUMENTA o saldo | Chegou mercadoria nova do fornecedor. |
| 🔴 **Saída** | DIMINUI o saldo | O produto quebrou, estragou, ou foi doado. |
| 🟡 **Ajuste** | MUDA para o número digitado | Fez contagem (inventário) e descobriu que tinha menos ou mais do que o sistema marcava. |
| 🔵 **Devolução**| AUMENTA o saldo | O cliente devolveu um produto de uma venda passada. |

4. Informe a **Quantidade** e o **Motivo** (ex: "Reposição de fornecedor X").
5. Salve. O saldo atualizará na hora.

---

## 6. O que significa "Estoque Baixo"?

Lembra da **Quantidade Mínima** que explicamos no item 4?

Se o saldo atual do seu produto chegar ou ficar abaixo desse número, o produto ganha uma etiqueta vermelha de alerta.

Além disso, lá no **Dashboard (Visão Geral)**, o indicador de **Estoque Baixo** mostrará um número maior, avisando que é hora de ligar para o fornecedor.

---

## 7. Perguntas Frequentes

### ❓ "Eu vendo SERVIÇOS (ex: Instalação, Consulta). Como faço?"
Cadastre o serviço como se fosse um produto normal!
- No campo **SKU**, coloque algo como `SRV-01`.
- Na hora do estoque, você pode deixar o saldo muito alto (ex: 9999) ou simplesmente ignorar o alerta de estoque, pois serviço não se esgota.

### ❓ "Tentei fazer uma 'Saída' manual de 10 unidades, mas deu erro."
O sistema te impede de ficar com "estoque negativo". Se você só tem 5 unidades no sistema, não pode dar saída manual de 10. Ele bloqueará a ação.

### ❓ "Por que preciso colocar o Preço de Custo?"
Para que o módulo de **BI de Resultados** (os relatórios) consiga calcular o quanto sua empresa está dando de lucro real no fim do mês!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
