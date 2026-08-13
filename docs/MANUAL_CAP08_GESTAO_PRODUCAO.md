
# 📘 MANUAL DO USUÁRIO — SISTEMA GESTOR

### Capítulo 8: Gestão de Produção (PCP)

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Operacional > Gestão de Produção (PCP)

---

## 📋 Índice deste Capítulo

1. [Visão Geral: Como o sistema entende a Produção?](#1-visão-geral-como-o-sistema-entende-a-produção)
2. [O Passo 1: A Ficha Técnica (A "Receita")](#2-o-passo-1-a-ficha-técnica-a-receita)
3. [O Passo 2: A Ordem de Produção (OP)](#3-o-passo-2-a-ordem-de-produção-op)
4. [A Mágica da Automação de Produção](#4-a-mágica-da-automação-de-produção)
5. [Perguntas Frequentes](#5-perguntas-frequentes)

---

## 1. Visão Geral: Como o sistema entende a Produção?

Se a sua empresa **monta**, **fábrica**, ou **transforma** materiais em um produto final antes de vender, você precisa deste módulo.

O sistema trabalha com a seguinte lógica:
Você pega "Matéria-Prima" do Almoxarifado ➡️ Transforma ➡️ Gera um "Produto Pronto" no Estoque de Vendas.

Para que o sistema saiba fazer isso sozinho, ele precisa de duas coisas: a Ficha Técnica (a receita do bolo) e a Ordem de Produção (a ordem para a cozinha começar a fazer o bolo).

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** → **Gestão de Produção (PCP)**.

---

## 2. O Passo 1: A Ficha Técnica (A "Receita")

A Ficha Técnica diz ao sistema **exatamente o que gasta** para fazer 1 (uma) unidade do seu produto.

### Como criar uma Ficha Técnica:
1. Na tela do PCP, procure pela área de **Fichas Técnicas** e clique em **Nova Ficha**.
2. **Produto Final:** Selecione qual produto (que já deve estar cadastrado no Estoque) você vai fabricar.
3. **Descrição:** Coloque o manual de montagem ou os passos da produção.
4. **Tempo Estimado:** Quanto tempo (em minutos) demora para fazer uma unidade.
5. **Insumos / Matéria-Prima:** Adicione um por um os materiais que serão usados. (Exemplo: Para montar 1 Computador, gasta-se 1 Placa Mãe, 1 Processador, 2 Memórias RAM, etc).

> **O Sistema é inteligente:** Ao preencher os insumos, o sistema já calcula automaticamente o **Custo Total de Materiais** da sua Ficha Técnica, baseando-se no preço que você pagou por eles!

---

## 3. O Passo 2: A Ordem de Produção (OP)

Agora que o sistema já sabe a receita, você precisa emitir uma Ordem de Produção (OP) para o chão de fábrica começar a trabalhar.

### Como criar uma OP:
1. Vá em **Nova Ordem de Produção**.
2. Escolha qual **Ficha Técnica** será usada.
3. Informe a **Quantidade Planejada**. (Ex: "Fazer 5 computadores").
4. (Opcional) Você pode colocar o **Custo de Mão de Obra**, se tiver calculado quanto vai pagar para o funcionário por este lote.
5. Salve. O status da OP começará como **"Aberta/Planejada"**.

### Mudando o Status da OP:
Quando a equipe começar a trabalhar, você edita a OP e muda o status para **"Em Produção"**. 
Isso avisa a todos no sistema que aquela mercadoria está no processo de fabricação.

---

## 4. A Mágica da Automação de Produção

O que acontece quando o produto fica pronto e você muda o status da OP para **"Finalizada"**?

O sistema vai trabalhar dobrado por você:

1. 🏭 **No Almoxarifado:** Ele vai "roubar" silenciosamente as matérias-primas que foram usadas e dar saída delas no sistema.
2. 📦 **No Estoque de Vendas:** Ele vai gerar as unidades novas do Produto Final e colocá-las prontas para a equipe de Vendas vender.
3. 💰 **No Financeiro/Custo:** Ele vai recalcular o preço de custo real do seu produto com base no que foi gasto na produção.

> [!WARNING]
> **A Trava de Segurança:** O sistema não é bobo. Se você mandar "Finalizar" a OP, mas não tiver matéria-prima suficiente no Almoxarifado para cobrir a produção, **ele dará um erro e bloqueará a finalização**. Ele vai te avisar: "Faltam X unidades da peça Y".

---

## 5. Perguntas Frequentes

### ❓ "A produção deu errado e perdi material. E agora?"
Se a OP não deu certo, você pode cancelá-la. Mas a matéria-prima que foi perdida (estragou/quebrou) deve ser baixada manualmente lá no módulo de **Almoxarifado** usando a opção "Saída" e escrevendo no motivo: "Perda na produção".

### ❓ "Posso fabricar algo sem fazer Ficha Técnica antes?"
Não. A Ficha Técnica é obrigatória para que a inteligência do sistema saiba o que deve ser retirado do Almoxarifado e o que deve ser gerado no Estoque. Se o produto é "exclusivo/único", crie uma ficha técnica simples para ele.

### ❓ "Onde eu vejo o tempo que a minha equipe gastou em todas as OPs?"
No **Dashboard do PCP** (Painel principal de Produção), você tem indicadores de tempo estimado versus produzido e um histórico de todas as OPs em andamento.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
