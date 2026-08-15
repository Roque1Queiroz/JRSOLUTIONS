# MANUAL DO SISTEMA GESTOR

Este manual é a base de conhecimento oficial do assistente virtual (chatbot) do Sistema Gestor. Ele consolida, em um único documento limpo, o funcionamento de todos os módulos da plataforma: acesso e login, dashboard, clientes, vendas, produtos e estoque, financeiro, fiscal, almoxarifado, produção, ordens de serviço e compras. Todo o conteúdo foi escrito em português brasileiro, com tom direto e didático, para orientar o usuário final (operadores, vendedores, gerentes e administradores).

O Sistema Gestor é uma plataforma completa de gestão empresarial (também chamada de MEI Gestão), desenvolvida pela JR Solutions Tecnologia. Com ela o usuário controla, em um único lugar acessível pelo navegador: clientes, vendas, estoque, financeiro, fiscal, produção, serviços, compras e relatórios. Funciona 100% pelo navegador de internet, sem necessidade de instalar nenhum programa.

---

## 1. Acesso e Login

O usuário cria a conta por meio do Administrador do Sistema, que informa o nome de usuário, uma senha inicial e define o perfil de permissão.

### Perfis de permissão

- **Administrador:** acesso total a todos os módulos.
- **Gerente:** relatórios, aprovações e visão geral.
- **Vendedor:** clientes, vendas e consulta de estoque.
- **Operador:** produção, serviços e movimentações.
- **Almoxarife:** acesso exclusivo ao Almoxarifado. Ao fazer login, o almoxarife é levado direto ao Dashboard do Almoxarifado (em vez do dashboard geral).

### Requisitos de acesso

- Um navegador de internet (Google Chrome, Microsoft Edge, Firefox ou Safari).
- O endereço do sistema, fornecido pelo administrador (ex.: `http://192.168.1.100:8000` para rede local, ou um endereço HTTPS para acesso pela internet).
- Nome de usuário e senha pessoal.

### Como fazer login

1. Abra o navegador e digite o endereço do sistema na barra de endereço.
2. Na tela de login, preencha o campo **Usuário** com seu nome de usuário.
3. Preencha o campo **Senha** (os caracteres aparecem como pontinhos por segurança).
4. Clique no botão **Iniciar sessão**.
5. Você será levado automaticamente ao Painel Principal (Dashboard).

Se o login falhar, verifique se o Caps Lock está desligado, se as credenciais estão corretas (há diferença entre maiúsculas e minúsculas) ou contate o administrador.

### Como trocar a senha

1. Após fazer login, acesse `/admin/password_change/` na barra de endereço.
2. Preencha a senha antiga, a nova senha e a confirmação.
3. Clique em **Alterar minha senha**.

Recomenda-se usar senha com pelo menos 8 caracteres, misturando letras, números e símbolos, e não reutilizar senhas óbvias (ex.: `123456`).

### Como sair do sistema

1. Clique no seu nome (canto superior direito).
2. No menu exibido, clique em **Sair do Sistema**.
3. Você volta para a tela de login. Atalho direto: `/admin/logout/`.

É importante sempre fazer logout ao sair para proteger os dados, especialmente em computadores compartilhados. O sistema pode ser usado em vários dispositivos ao mesmo tempo; alterações podem exigir atualizar a página (F5) para aparecer em outro dispositivo.

### Recuperação de senha

O sistema não tem recuperação automática de senha. O usuário deve contatar o administrador, que redefine a senha pelo painel administrativo.

### Usando no celular ou tablet

O sistema é 100% responsivo. No celular, o menu lateral fica escondido; toque no ícone de três linhas no canto superior esquerdo para abri-lo.

### Recurso de permissão e configurações

O painel administrativo (`/admin/`) é a área de configuração avançada, acessível apenas por administradores. Por ele é possível criar usuários, definir permissões e gerenciar configurações. O sistema também permite a **Personalização de Marca (White Label)**, em que a empresa define o logo e o nome exibidos no topo do menu.

### Planos do sistema e recursos disponíveis

Cada empresa possui um plano contratado, que define permissões, limites e acesso a módulos:

- **Plano Básico:** foco no uso essencial. Permite até **2 usuários** vinculados.
- **Plano Profissional (PME):** permite até **5 usuários** e inclui recursos de IA e personalização de marca (White Label).
- **Plano Enterprise (Indústria):** permite até **20 usuários**, abrange todos os recursos do Profissional e inclui também **APIs customizadas** para integrações.

Regras importantes:

- **Limitador de usuários:** o limite de usuários vinculados de uma empresa é controlado pelo plano. Ao tentar criar um usuário além do limite, o sistema bloqueia a criação e avisa que o limite do plano foi atingido.
- **Assistente de IA (chatbot do Sistema Gestor):** o chat de suporte inteligente **só aparece nos planos Profissional e Enterprise**. Em planos Básicos o widget do assistente não é exibido.
- **White Label:** logo e nome personalizados da empresa estão disponíveis nos planos Profissional e Enterprise.
- **APIs customizadas:** disponíveis somente no plano Enterprise.

---

## 2. Dashboard (Visão Geral)

Após o login, o usuário vê o Painel Principal (Dashboard), organizado em três grandes áreas: a Barra Superior (topbar), o Menu Lateral (sidebar) e a Área de Conteúdo.

### Indicadores (KPIs) do Dashboard

- **Total de Clientes:** quantidade de clientes cadastrados.
- **Total de Produtos:** quantidade de produtos no catálogo.
- **Total de Vendas:** número de vendas realizadas.
- **Faturamento do Mês:** valor vendido no mês atual (R$).
- **Saldo em Caixa:** soma dos saldos das contas bancárias cadastradas.
- **Estoque Baixo:** produtos com estoque abaixo do mínimo definido.
- **Clientes Novos:** clientes cadastrados no mês atual.

O Dashboard também exibe gráfico de faturamento, vendas recentes e lembretes. Ele atualiza automaticamente a cada acesso e funciona como um "resumo diário" do negócio.

O Dashboard principal também exibe no topo o **relatório diário do Cientista Financeiro** (veja a seção 6.1).

### Menu Lateral (Sidebar)

O menu fica à esquerda e está organizado em seções:

- **Menu Principal:** Visão Geral (dashboard) e BI de Resultados.
- **Gestão Comercial:** Gestão de Clientes e Gestão de Vendas.
- **Gestão de Estoque:** Gestão de Produtos e Gestão de Almoxarifado.
- **Gestão Operacional:** Gestão de Produção (PCP), Ordens de Serviço (O.S.) e Gestão de Compras.
- **Gestão Financeira:** Gestão de Caixa, Gestão de Receitas e Gestão de Reembolsos.
- **Gestão Fiscal:** Gestão de Notas.
- **Configurações:** Gestão de Sistema.

O item ativo fica destacado na cor roxa. Para voltar ao início, clique em **Visão Geral** ou no logo **SISTEMA GESTOR**.

### Barra Superior (Topbar)

- **Título da Página:** mostra o nome da seção em que o usuário está.
- **Notificações (sino):** alertas de reembolsos pendentes; aparece somente quando há pendências.
- **Alternar Tema:** troca entre Modo Claro e Modo Escuro (a preferência é salva automaticamente no navegador).
- **Menu do Usuário:** o nome do usuário e opções de conta (Personalizar Marca, Ajustes e Sair do Sistema).

---

## 3. Gestão de Clientes

A Gestão de Clientes centraliza os dados das pessoas e empresas que compram do negócio. Esses dados são usados em todo o sistema: para gerar vendas e orçamentos, emitir Ordens de Serviço e preencher automaticamente as Notas Fiscais.

**Acesso:** Gestão Comercial → Gestão de Clientes.

### Listagem de clientes

A tela mostra todos os clientes cadastrados, com ferramentas de:
- **Busca/pesquisa:** por nome, CPF/CNPJ ou telefone.
- **Status:** uma etiqueta verde indica cliente Ativo; uma etiqueta cinza indica Inativo.
- **Novo Cliente:** botão para iniciar um cadastro.
- **Coluna Ações:** botões de Editar (lápis) e Excluir (lixeira).

### Cadastro de novo cliente

1. Clique no botão **Novo Cliente**.
2. Preencha os dados obrigatórios:
   - **Nome:** nome completo ou razão social.
   - **Tipo:** Pessoa Física ou Pessoa Jurídica.
   - **CPF/CNPJ:** apenas os números (o sistema formata automaticamente). O documento não pode se repetir em outro cadastro.
   - **Status Ativo:** marcado para o cliente aparecer na hora de fazer uma venda.
3. Preencha contato e endereço (opcionais, mas recomendados): e-mail, telefone e endereço completo (necessário para emitir nota fiscal).
4. Clique em **Salvar**.

### Pessoa Física versus Pessoa Jurídica

- **PF:** exige CPF (11 dígitos); ideal para consumidor final (varejo).
- **PJ:** exige CNPJ (14 dígitos); ao emitir nota para PJ, preencha o endereço completo e verifique a Inscrição Estadual (IE).

O sistema não permite cadastrar dois clientes com o mesmo CPF ou CNPJ.

### Editar, detalhes e histórico

- Para editar, use o ícone de lápis na coluna Ações.
- Para ver o histórico, clique no nome do cliente: abre uma tela com os dados completos e o **Histórico de Vendas** (tabela com todas as vendas feitas, status e valores totais).

### Inativar versus excluir

- **Excluir (lixeira):** apaga permanentemente o cadastro. Use apenas quando o cadastro foi feito por engano. Não é possível excluir um cliente que já possui Venda ou Ordem de Serviço registrada, para preservar o histórico financeiro.
- **Inativar:** mantém o histórico salvo, mas o cliente deixa de aparecer na lista de novas vendas. Basta desmarcar a caixa **Ativo** na edição. É a melhor prática para clientes antigos ou problemáticos.

---

## 4. Gestão de Vendas

O módulo de Vendas é o gatilho que movimenta toda a empresa: ao registrar uma venda, o sistema dá baixa no estoque e lança a receita no financeiro automaticamente.

**Acesso:** Gestão Comercial → Gestão de Vendas.

### Status da venda

- **Rascunho (amarelo):** é apenas um orçamento. Não tira produto do estoque e não gera receita. Pode ser editado à vontade.
- **Confirmada (verde):** o negócio fechou. O sistema TIRA o produto do estoque e CRIA uma Receita no financeiro.
- **Entregue (azul):** o cliente recebeu a mercadoria. Financeiramente e no estoque é igual a Confirmada.
- **Cancelada (vermelho):** a venda deu errado. O sistema DEVOLVE o produto ao estoque e ESTORNA o lançamento no financeiro.

### Como registrar uma nova venda

1. Clique no botão **Nova Venda**.
2. Selecione o cliente (cadastre-o antes no módulo de Clientes, se for novo).
3. Informe a data da venda (pré-preenchida com hoje) e o status.
4. Adicione os itens: escolha o produto, informe a quantidade e ajuste o preço unitário se necessário. O subtotal é calculado automaticamente.
5. No fechamento, informe o desconto (R$) se houver; o valor total é calculado (Subtotal - Desconto).
6. Clique em **Salvar**.

### Automação de estoque e financeiro

Ao salvar a venda como **Confirmada**, o sistema automaticamente:
- Dá baixa nas quantidades vendidas no estoque (ex.: se havia 10 cadernos e vendeu 2, o estoque cai para 8).
- Cria um registro de **Receita** no módulo de Gestão de Caixa, vinculando o valor ao cliente, e o faturamento do Dashboard sobe imediatamente.

### Nota fiscal da venda

Na tela de detalhes da venda, há o botão **Gerar Nota Fiscal**. Ao clicar, o sistema puxa automaticamente os dados do cliente, os produtos e os valores, preenchendo a NF no módulo Fiscal, onde basta conferir os impostos e emitir. Para a nota sair certa, o cliente precisa ter CPF/CNPJ e endereço preenchidos no cadastro.

### Cancelar ou excluir venda

- **Cancelar (mudar status para Cancelada):** mantém o histórico e o sistema devolve os itens ao estoque e estorna a receita. É a opção correta.
- **Excluir (lixeira):** remove a venda para sempre, mas o sistema também desfaz estoque e financeiro; use apenas para vendas de teste ou lançadas em duplicidade.

### Regras importantes

- Venda com **estoque insuficiente** é bloqueada; é preciso dar entrada na quantidade antes.
- Orçamentos devem ser criados como **Rascunho** (não mexem no estoque nem no caixa).
- O preço de um item pode ser alterado apenas naquela venda, sem mudar o cadastro do produto.
- Receita só é gerada para status **Confirmada** ou **Entregue**; Rascunho e Cancelada não geram receita.

---

## 5. Gestão de Produtos e Estoque

O módulo de Produtos é o catálogo do que a empresa vende. Não deve ser confundido com o Almoxarifado:
- **Gestão de Produtos:** o que se VENDE e dá lucro (ex.: capa de celular, consulta médica, cadeira).
- **Almoxarifado:** o que se CONSOME trabalhando (ex.: papel A4, café, ferramentas internas).

**Acesso:** Gestão de Estoque → Gestão de Produtos.

### Cadastro de novo produto

1. Clique em **Novo Produto**.
2. Preencha os campos:
   - **Nome:** nome oficial do produto.
   - **SKU:** código de barras ou código interno; se deixar em branco, o sistema gera automaticamente.
   - **Categoria:** para organizar o catálogo (ex.: Roupas, Eletrônicos, Serviços).
   - **Preço de Custo:** quanto pagou ao fornecedor.
   - **Preço de Venda:** por quanto será vendido.
   - **Ativo:** se o produto está disponível para venda.
3. Clique em **Salvar**.

Há um alerta caso o Preço de Venda seja MENOR que o Preço de Custo (impede vender com prejuízo).

### Margem de lucro

O sistema calcula automaticamente a margem de lucro na tela de detalhes do produto:

`((Preço de Venda - Preço de Custo) / Preço de Custo) × 100`

### Ficha de estoque

Cada produto tem uma ficha de estoque com:
- **Quantidade Atual:** quantos existem hoje.
- **Quantidade Mínima:** o número de alerta (ex.: mínima 5; ao atingir 5, o sistema alerta para comprar mais).
- **Localização:** prateleira ou corredor onde o produto está.

### Movimentações manuais

Abaixo de Estoque do produto, clique em **Nova Movimentação** e escolha o tipo:
- **Entrada:** AUMENTA o saldo (chegou mercadoria do fornecedor).
- **Saída:** DIMINUI o saldo (produto quebrou, estragou ou foi doado).
- **Ajuste:** MUDA para o número digitado (contagem/inventário).
- **Devolução:** AUMENTA o saldo (cliente devolveu produto de venda passada).

Informe a quantidade e o motivo, e salve. O sistema impede saldo negativo: não é possível dar saída maior do que o saldo existente.

### Estoque baixo

Se o saldo atual chegar ou ficar abaixo da **Quantidade Mínima**, o produto ganha etiqueta vermelha de alerta, e o Dashboard mostra o indicador de **Estoque Baixo**.

### Serviços no catálogo

Serviços (ex.: instalação, consulta) podem ser cadastrados como produto normal. Use um SKU como `SRV-01`; o alerta de estoque pode ser ignorado, pois serviço não se esgota.

---

## 6. Gestão Financeira

O módulo financeiro controla todo o dinheiro que entra (Receitas), sai (Despesas) e os pedidos de Reembolso da equipe. É o "cofre" da empresa.

**Acesso:** seção **Gestão Financeira** do menu, com três opções:
- **Gestão de Caixa:** visão completa de tudo.
- **Gestão de Receitas:** apenas as entradas de dinheiro.
- **Gestão de Reembolsos:** controle de despesas da equipe.

### Contas bancárias

Antes de lançar valores, é ideal cadastrar as contas da empresa (menu de configurações administrativas, restrito a administradores). O sistema já vem com a conta padrão "Caixa Interno". Os saldos de todas as contas são somados e exibidos como **Saldo em Caixa** no Dashboard.

### Gestão de Caixa (Receitas e Despesas)

A tela de Gestão de Caixa é um extrato com toda a movimentação:
- **Receita (verde):** dinheiro que entrou (vendas, serviços prestados, rendimentos).
- **Despesa (vermelho):** dinheiro que saiu (fornecedores, contas, aluguel, salários).

Vendas confirmadas geram receitas automaticamente. Para lançar uma despesa manual:

1. Clique em **Nova Transação**.
2. Escolha o tipo **Despesa**.
3. Preencha descrição, valor, data da transação, categoria e conta bancária.
4. Marque a caixa **Paga** (se já paga) e salve.

Se for uma compra futura, é possível lançar com a **Data de Vencimento** e deixar "Paga" desmarcada, criando o controle de "Contas a Pagar".

### Gestão de Reembolsos

Quando um colaborador compra algo para a empresa com o próprio dinheiro, ele pede reembolso:

1. Acesse **Gestão de Reembolsos** e clique em **Novo Reembolso**.
2. Preencha colaborador/solicitante, item/descrição, valor, data da compra, prioridade (alta, média ou baixa) e anexe o comprovante (foto ou PDF).
3. Salve. O status fica **Pendente** até o gestor financeiro pagar.

### Sino de alerta de reembolsos

Se houver reembolso pendente, um sino vermelho pisca na barra superior. Clicando no sino, o usuário vê quantos reembolsos aguardam pagamento e pode acessar o botão **Gerar Reembolsos** para ir à tela de aprovação. Após pagar, o gestor marca a caixa **Reembolsado?** e o pedido sai da fila de pendentes.

### Regras financeiras

- Venda feita a prazo gera receita **Pendente (Não Paga)**; quando o dinheiro cair, edite a receita e marque como **Paga**.
- O Saldo em Caixa pode divergir do banco se houver taxas ou movimentações não lançadas; é preciso lançar essas pequenas despesas.

---

## 6.1 Cientista Financeiro (Relatório Diário Automático)

O Sistema Gestor conta com um **Cientista Financeiro**, responsável por gerar automaticamente um relatório diário de saúde financeira para a empresa.

### Como funciona o processamento

- O processamento roda **em background**, em um worker **Celery**.
- Ele é acionado por um agendador (**beat**) que executa a tarefa **diariamente à meia-noite**, no fuso horário **America/Sao_Paulo**.

### O que o relatório contém

Para **cada empresa ativa**, o sistema calcula e persiste um relatório com os seguintes campos:

- **data:** a data do relatório.
- **entradas_hoje:** total de entradas previstas para o dia.
- **saidas_hoje:** total de saídas previstas para o dia.
- **projecao:** a projeção de saldo do dia, calculada como `saldo + entradas_hoje - saidas_hoje`.
- **status:** a classificação da saúde financeira do dia.
- **mensagem:** um texto de apoio gerado pelo sistema.

### Status possíveis

- **SUCESSO:** a saúde financeira é estável (o caixa deve fechar o dia no azul).
- **ALERTA:** o saldo deve diminuir hoje.
- **PERIGO:** as despesas do dia superam o saldo disponível.

### Exibição no Dashboard e fallback

O **dashboard principal** exibe o relatório do dia **logo no topo**, logo após a abertura da tela.

Se o relatório do dia ainda não existir (por exemplo, antes da primeira execução do agendador), o sistema **calcula o relatório na hora, como fallback**, garantindo que o dashboard nunca fique sem o dado.

### Exemplo de mensagem

Em um status **SUCESSO**, a mensagem de apoio pode ser:

> "Saúde financeira estável. O caixa deve fechar o dia no azul."

---

## 7. Gestão Fiscal (Notas Fiscais)

A Gestão Fiscal é o controle legal das notas fiscais. Diferente de vendas e orçamentos (controle interno), a Nota Fiscal é o comprovante legal para o Governo. O sistema ajuda a calcular impostos básicos e organizar os documentos.

**Acesso:** Gestão Fiscal → Gestão de Notas.

### Ciclo de vida da Nota Fiscal

- **Rascunho:** fase de digitação. A nota ainda não tem validade fiscal; pode ser editada ou apagada livremente.
- **Emitida (verde):** a nota vale, compõe o faturamento fiscal oficial e **não pode mais ser editada**; se algo estiver errado, deve ser cancelada.
- **Cancelada (vermelho):** o negócio foi desfeito; o valor zera nos relatórios fiscais.

### Gerar NF a partir da venda

A forma mais rápida é pelo módulo de Vendas:

1. Vá em Gestão Comercial → Gestão de Vendas.
2. Abra a venda desejada.
3. Clique em **Gerar Nota Fiscal**.

O sistema puxa automaticamente cliente, data, produtos, subtotal e valor total, e já vincula a NF à venda. Basta revisar e confirmar a emissão.

### Nota fiscal avulsa (manual)

1. Vá em Gestão Fiscal → Gestão de Notas.
2. Clique em **Nova Nota Fiscal**.
3. Preencha cliente (obrigatório), número e série, data de emissão e saída, descrição dos itens e impostos (ICMS/IPI), se necessário.
4. O sistema calcula o total: `(Subtotal - Desconto) + ICMS + IPI`.
5. Salve (a nota é criada como Rascunho) e depois abra e clique em **Emitir NF**.

### Cancelar nota fiscal

Uma vez emitida, a nota trava para edições. Clique em **Cancelar NF**; o status muda para Cancelada e o valor deixa de somar nos relatórios.

### Regras e validações

- Não são permitidos valores negativos.
- O desconto não pode ser maior que o subtotal.
- A data de saída não pode ser antes da data de emissão.
- Notas Emitidas não podem ser excluídas, apenas canceladas; só notas em Rascunho podem ser apagadas.

### Observações

- O sistema gera o controle e o cálculo fiscal interno. Para transmissão direta de XML à Receita Federal/Sefaz, consulte o plano contratado ou repasse o relatório fiscal ao contador.
- O faturamento principal do Dashboard vem do módulo de Vendas e da Gestão de Caixa; o módulo Fiscal é um controle paralelo exigido por lei. As vendas devem ser feitas no módulo comercial.

---

## 8. Gestão de Almoxarifado

O Almoxarifado controla os materiais que a equipe consome para trabalhar (papel sulfite, café, ferramentas, EPIs), garantindo que o time nunca pare por falta de insumo. Não confundir com o Estoque de Vendas:
- **Estoque (Produtos):** mercadoria que se vende a clientes.
- **Almoxarifado:** material que a equipe consome no trabalho.

**Acesso:** Gestão de Estoque → Gestão de Almoxarifado. Quem tem perfil Almoxarife entra direto nessa tela ao fazer login.

### Locais e endereços

O sistema permite mapear fisicamente o depósito:
- **Locais de Armazenamento:** o galpão ou a sala (ex.: Almoxarifado Central, Depósito Manutenção).
- **Endereçamento:** a "localização" da prateleira em 3 níveis — Corredor (A, B, C), Estante (01, 02) e Prateleira (01, 02, 03).

Ao cadastrar o saldo de um material, informa-se em qual endereço ele está.

### Setores

Os materiais são entregues aos **Setores** da empresa (Administração, Produção, Limpeza, Manutenção). Cada setor pode ter um responsável vinculado, permitindo relatórios mensais de consumo por setor.

### Requisição de material

1. Clique para criar uma **Nova Requisição**.
2. Selecione o **Setor**, o **Local de Origem** e adicione os **Itens** com as quantidades.
3. Escreva uma **Justificativa**.
4. Salve. O status inicial é **Solicitado**.

### Fluxo de aprovação

- **Solicitado (amarelo):** pedido criado, aguardando o gestor.
- **Aprovado (verde):** o gestor liberou; o funcionário pode buscar o material.
- **Recusado (vermelho):** o gestor negou o pedido.
- **Entregue (azul):** o material foi retirado e o almoxarife deu baixa no sistema.

Somente quando o status muda para **Entregue** é que o sistema retira o item do saldo do Almoxarifado.

### Etiquetas QR Code

Pela **Central de Etiquetas**, é possível gerar etiquetas com QR Code para prateleiras ou caixas de material: vá na aba de Endereços, selecione os endereços e o sistema gera um PDF pronto para imprimir.

### Regras e dicas

- Não é possível usar material do Almoxarifado diretamente em uma venda; é preciso dar Saída manual no Almoxarifado e Entrada manual no Estoque de Vendas.
- A aprovação não retira o material do saldo; apenas o status **Entregue** dá baixa.
- Se um item ficar abaixo da quantidade mínima, o sistema emite alerta vermelho para acionar o setor de Compras.

---

## 9. Gestão de Produção (PCP)

O módulo de Produção atende empresas que montam, fabricam ou transformam materiais em produto final. A lógica é: pegar matéria-prima do Almoxarifado, transformar e gerar um produto pronto no Estoque de Vendas. Para isso, o sistema usa a **Ficha Técnica** (a "receita") e a **Ordem de Produção** (a ordem de execução).

**Acesso:** Gestão Operacional → Gestão de Produção (PCP).

### Passo 1: Ficha Técnica

A Ficha Técnica define exatamente o que se gasta para produzir 1 unidade do produto:

1. Na área de **Fichas Técnicas**, clique em **Nova Ficha**.
2. Selecione o **Produto Final** (já cadastrado no Estoque).
3. Descreva o manual de montagem ou os passos da produção.
4. Informe o **Tempo Estimado** (minutos por unidade).
5. Adicione os **Insumos/Matéria-Prima** (ex.: para montar 1 computador: 1 placa-mãe, 1 processador, 2 memórias RAM).

O sistema calcula automaticamente o **Custo Total de Materiais** da ficha com base nos preços pagos pelos insumos.

### Passo 2: Ordem de Produção (OP)

1. Clique em **Nova Ordem de Produção**.
2. Escolha a **Ficha Técnica**.
3. Informe a **Quantidade Planejada** (ex.: fazer 5 computadores).
4. Opcional: informe o custo de mão de obra do lote.
5. Salve. O status começa como **Aberta/Planejada**. Quando a equipe começa a trabalhar, mude para **Em Produção**.

### Automação quando a OP é finalizada

Ao mudar a OP para **Finalizada**, o sistema:
- Dá saída das matérias-primas usadas no Almoxarifado.
- Gera as unidades do Produto Final, prontas para a Vendas, no Estoque de Vendas.
- Recalcula o preço de custo real do produto com base no que foi gasto.

Existe uma trava de segurança: se faltar matéria-prima no Almoxarifado para cobrir a produção, o sistema bloqueia a finalização e avisa quantas unidades faltam da peça.

### Regras

- A Ficha Técnica é obrigatória para que o sistema saiba o que retirar do Almoxarifado e o que gerar no Estoque.
- Se a produção der errado, a OP pode ser cancelada, mas a matéria-prima perdida deve ser baixada manualmente no Almoxarifado (opção "Saída", motivo "Perda na produção").
- O Dashboard do PCP mostra indicadores de tempo estimado versus produzido e o histórico de OPs.

---

## 10. Ordens de Serviço (O.S.) e Gestão de Compras

### O que é uma Ordem de Serviço

A O.S. é um trabalho que leva tempo para ser feito (consertar o carro de um cliente, instalar um ar-condicionado, arrumar uma máquina). Ela registra o que estragou, quem vai consertar, quanto tempo levará e quais peças foram usadas.

**Acesso:** Gestão Operacional → Ordens de Serviço (O.S.).

### Tipos de O.S.

- **Serviço ao Cliente:** trabalho pago feito para alguém de fora (ex.: conserto da geladeira de um cliente).
- **Manufatura Interna:** adaptação de peças internas (ex.: montagem de estante do galpão).
- **Manutenção Interna:** conserto de algo da própria empresa (ex.: máquina de solda).

### Como preencher uma O.S.

1. Clique em **Nova O.S.**.
2. Dados iniciais: cliente (obrigatório para serviço externo), responsável (técnico) e descrição do problema.
3. Execução: laudo técnico (o que foi feito), valor do serviço (mão de obra) e itens consumidos (peças do estoque).
4. O sistema calcula automaticamente o **Valor Total** somando mão de obra + peças.

### Fluxo da O.S.

`Aberta` (cliente trouxe) → `Em Execução` (técnico trabalhando) → `Finalizada` (pronta) ou `Cancelada`.

Ao finalizar a O.S. com itens consumidos, o sistema atualiza o estoque automaticamente.

### Gestão de Compras

Usada quando o estoque fica baixo ou a equipe pede algo no Almoxarifado que acabou.

**Acesso:** Gestão Operacional → Gestão de Compras.

### Processo de compra

1. Cadastre os **Fornecedores** (nome, CNPJ, telefone).
2. Crie o **Pedido de Compra** (clique em **Novo Pedido**), adicione os itens e a data limite. O status começa como **Solicitado**.
3. Na chegada da mercadoria, mude o status para **Recebido**.

### Cotação (Mapas de Cotação)

1. Abra um pedido em status **Em Cotação**.
2. Adicione as ofertas dos fornecedores (valores e prazos de entrega) e anexe o PDF do orçamento.
3. **Marque o Vencedor** — o fornecedor que ganhou a concorrência.
4. Mude o status do pedido para **Aprovado**.

Quando a mercadoria chega, o usuário abre o pedido e muda para **Recebido**. Para gerar a conta a pagar do fornecedor vencedor, crie uma **Despesa** em nome dele no módulo Financeiro (Gestão de Caixa) com a data combinada.

---

## 11. Relatórios e BI

O sistema oferece a área **BI de Resultados** (Menu Principal), de relatórios avançados e gráficos gerenciais. O BI de Resultados usa o **preço de custo** dos produtos para calcular o lucro real da empresa no fim do mês. Complementarmente, o sistema dispõe de relatórios gerenciais e da DRE, além dos relatórios fiscais gerados pelo módulo Fiscal, que podem ser repassados ao contador.

---

## Suporte

Se houver dúvidas não resolvidas neste manual:
1. Consulte novamente este manual e tente os passos descritos.
2. Contate o administrador do sistema da empresa.
3. Contate o suporte técnico da JR Solutions Tecnologia.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.
> © 2026 JR Solutions Tecnologia. Todos os direitos reservados.
