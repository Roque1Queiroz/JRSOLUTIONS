# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 7: Gestão de Almoxarifado

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão de Estoque > Gestão de Almoxarifado

---

## 📋 Índice deste Capítulo

1. [O que é o Almoxarifado? (Estoque x Almoxarifado)](#1-o-que-é-o-almoxarifado-estoque-x-almoxarifado)
2. [Organizando a Casa: Locais e Endereços](#2-organizando-a-casa-locais-e-endereços)
3. [Entendendo os Setores](#3-entendendo-os-setores)
4. [Como Fazer uma Requisição de Material](#4-como-fazer-uma-requisição-de-material)
5. [O Fluxo de Aprovação de Materiais](#5-o-fluxo-de-aprovação-de-materiais)
6. [Gerando Etiquetas QR Code](#6-gerando-etiquetas-qr-code)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. O que é o Almoxarifado? (Estoque x Almoxarifado)

A primeira regra de ouro deste módulo é não confundir o Almoxarifado com o Estoque de Vendas.

| Módulo | Para que serve? | Exemplo |
|--------|-----------------|---------|
| **Estoque (Produtos)** | Mercadoria que você **VENDE** para clientes. | Capas de celular, camisetas, peças de computador. |
| **Almoxarifado** | Material que sua equipe **CONSOME** para trabalhar. | Papel sulfite, pó de café, ferramentas, EPIs, peças para uso interno. |

O Almoxarifado garante que sua equipe nunca pare de trabalhar por falta de insumos!

> **Acesso:** No Menu Lateral, vá em **Gestão de Estoque** → **Gestão de Almoxarifado**. 
> Se você tem o perfil "Almoxarife", você já entra direto nesta tela ao fazer login!

---

## 2. Organizando a Casa: Locais e Endereços

Antes de colocar as coisas no Almoxarifado, o sistema permite que você mapeie fisicamente o seu depósito para nunca mais perder tempo procurando um parafuso ou um pacote de folha A4.

### Como funciona o mapeamento:

1. **Locais de Armazenamento:** É o galpão ou a sala. (Exemplo: *Almoxarifado Central*, *Depósito Manutenção*).
2. **Endereçamento:** É o "CEP" da prateleira. O sistema organiza isso em 3 níveis:
   - **C**orredor (Ex: A, B, C)
   - **E**stante (Ex: 01, 02)
   - **P**rateleira (Ex: 01, 02, 03)

Ao cadastrar o saldo de um material, você dirá exatamente em qual **Endereço** ele está guardado.

---

## 3. Entendendo os Setores

Para quem você entrega os materiais do almoxarifado? Para os **Setores** da sua empresa.

Você pode cadastrar setores como: *Administração*, *Produção*, *Limpeza*, *Manutenção*.
Cada setor pode ter um **Responsável** vinculado. Isso é importante para os relatórios no fim do mês: o sistema vai te mostrar qual setor está gastando mais copo descartável ou papel, por exemplo!

---

## 4. Como Fazer uma Requisição de Material

Quando um funcionário ou setor precisa de algo, ele faz um pedido oficial no sistema chamado **Requisição**. 

**Passo a passo da Requisição:**

1. Na tela do Almoxarifado, clique no botão para criar uma **Nova Requisição**.
2. Selecione o seu **Setor** (ex: Administração).
3. Selecione o **Local de Origem** (de qual almoxarifado você quer retirar).
4. No campo **Itens**, adicione o material que você precisa e a **Quantidade** desejada.
5. Escreva uma **Justificativa** (ex: "Acabou o papel para a impressora do RH").
6. Clique em **Salvar**.

Pronto! Seu pedido foi enviado para o chefe ou para o almoxarife aprovar. O status inicial será **Solicitado**.

---

## 5. O Fluxo de Aprovação de Materiais

O almoxarifado não é bagunça. Após alguém pedir (Solicitado), o pedido precisa ser avaliado para evitar desperdícios.

### Quem aprova?
O usuário com permissão de Gestor, Administrador ou o próprio Almoxarife (dependendo da regra da sua empresa).

### O Caminho do Pedido (Status):

| Status | O que está acontecendo |
|--------|------------------------|
| 🟡 **Solicitado** | O pedido foi criado e está aguardando o gestor olhar. |
| 🟢 **Aprovado** | O gestor liberou! O funcionário já pode ir no balcão buscar o material. |
| 🔴 **Recusado** | O gestor negou o pedido (ex: pediu 10 canetas, o gestor achou um exagero). |
| 🔵 **Entregue** | O funcionário foi lá, pegou o material e o almoxarife deu baixa oficial no sistema. |

> [!IMPORTANT]
> Apenas quando o status muda para **"Entregue"** é que o sistema realmente retira o item do saldo do Almoxarifado!

---

## 6. Gerando Etiquetas QR Code

Para as empresas que têm um estoque muito grande e organizado, o Sistema Gestor tem uma **Central de Etiquetas**.

Você pode gerar etiquetas com um código quadrado (QR Code) para colar nas suas prateleiras ou caixas de material.

1. Vá na aba de **Endereços**.
2. Selecione os endereços que deseja imprimir.
3. O sistema gerará um PDF pronto para imprimir.

Isso facilita a identificação visual na hora de guardar ou procurar os materiais.

---

## 7. Perguntas Frequentes

### ❓ "Posso usar material do Almoxarifado para fazer uma Venda para um cliente?"
Não! O sistema separa as coisas. Se você comprou algo para uso interno e, de repente, decidiu vender, você precisará dar "Saída Manual" no Almoxarifado e "Entrada Manual" no Estoque de Vendas.

### ❓ "A requisição foi 'Aprovada', o material já saiu do meu saldo?"
Ainda não. A aprovação é apenas a "assinatura" do chefe. O material só sai do saldo do sistema quando o status muda para **"Entregue"**, que significa que o material saiu fisicamente da prateleira.

### ❓ "O que acontece se faltar material no Almoxarifado?"
O sistema possui a mesma inteligência do módulo de Vendas: se um item ficar abaixo da Quantidade Mínima estipulada, ele emitirá um alerta vermelho para que você avise o setor de Compras!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
