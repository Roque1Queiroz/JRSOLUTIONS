# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 1: Como Acessar o Sistema

**Versão:** 1.0 — Maio/2026  
**Desenvolvido por:** JR Solutions Tecnologia  
**Público-alvo:** Usuário final (operadores, vendedores, gerentes e administradores)

---

## ðŸ“‹ Ãndice deste Capítulo

1. [O que é o Sistema Gestor?](#1-o-que-é-o-sistema-gestor)
2. [O que você precisa para acessar](#2-o-que-você-precisa-para-acessar)
3. [Passo a Passo: Abrindo o Sistema](#3-passo-a-passo-abrindo-o-sistema)
4. [Passo a Passo: Fazendo Login](#4-passo-a-passo-fazendo-login)
5. [A Tela Principal (Dashboard)](#5-a-tela-principal-dashboard)
6. [Conhecendo o Menu Lateral (Sidebar)](#6-conhecendo-o-menu-lateral-sidebar)
7. [Conhecendo a Barra Superior (Topbar)](#7-conhecendo-a-barra-superior-topbar)
8. [Como Sair do Sistema](#8-como-sair-do-sistema)
9. [Primeiro Acesso — Senha Inicial](#9-primeiro-acesso--senha-inicial)
10. [Como Trocar sua Senha](#10-como-trocar-sua-senha)
11. [Usando no Celular ou Tablet](#11-usando-no-celular-ou-tablet)
12. [Perguntas Frequentes](#12-perguntas-frequentes)

---

## 1. O que é o Sistema Gestor?

O **SISTEMA GESTOR** é a plataforma completa de gestão da sua empresa. Com ele, você controla:

| Módulo | O que faz |
|--------|-----------|
| ðŸ“‹ **Clientes** | Cadastro e consulta de todos os seus clientes |
| ðŸ›’ **Vendas** | Registro de vendas, orçamentos e acompanhamento |
| ðŸ“¦ **Estoque** | Controle de produtos, quantidades e alertas |
| ðŸ’° **Financeiro** | Receitas, despesas, caixa e reembolsos |
| ðŸ“„ **Fiscal** | Emissão e controle de notas fiscais |
| ðŸ­ **Produção** | Fichas técnicas e ordens de produção |
| ðŸ”§ **Serviços** | Ordens de serviço e manutençÃµes |
| ðŸ›ï¸ **Compras** | Pedidos de compra e cotaçÃµes com fornecedores |
| ðŸ“Š **Relatórios** | BI, DRE e relatórios gerenciais |

> [!TIP]
> Tudo isso em um único lugar, acessível pelo navegador do seu computador, celular ou tablet!

---

## 2. O que você precisa para acessar

Para acessar o Sistema Gestor, você precisa apenas de:

| Item | Detalhes |
|------|----------|
| ðŸŒ **Navegador de Internet** | Google Chrome, Microsoft Edge, Firefox ou Safari |
| ðŸ”— **Endereço do Sistema** | Fornecido pelo administrador (ex: `http://192.168.1.100:8000`) |
| ðŸ‘¤ **Usuário** | Seu nome de usuário (fornecido pelo administrador) |
| ðŸ”‘ **Senha** | Sua senha pessoal |

> [!IMPORTANT]
> **Não é necessário instalar nenhum programa!** O sistema funciona 100% pelo navegador de internet.

### Navegadores Recomendados

| Navegador | Versão Mínima | Recomendação |
|-----------|--------------|--------------|
| Google Chrome | 90+ | â­ **Recomendado** |
| Microsoft Edge | 90+ | âœ… Ã“timo |
| Mozilla Firefox | 88+ | âœ… Bom |
| Safari (Mac/iPhone) | 14+ | âœ… Bom |

---

## 3. Passo a Passo: Abrindo o Sistema

### Passo 1 — Abra o navegador

Clique no ícone do seu navegador de internet (Google Chrome, Edge, etc.).

### Passo 2 — Digite o endereço

Na **barra de endereço** (a barra no topo do navegador), digite o endereço que foi fornecido pelo seu administrador.

**Exemplos comuns de endereço:**
- `http://192.168.1.100:8000` — acesso pela rede local da empresa
- `http://meuservidor:8000` — acesso pelo nome do servidor
- `https://sistema.minhaempresa.com.br` — acesso pela internet (nuvem)

### Passo 3 — Pressione ENTER

Após digitar o endereço, pressione a tecla **Enter** no teclado.

> [!NOTE]
> Se o endereço estiver correto, o sistema abrirá a **tela de login**. Se aparecer um erro, verifique:
> - Se o endereço está digitado corretamente
> - Se o servidor do sistema está ligado
> - Se seu computador está conectado Ã  mesma rede

---

## 4. Passo a Passo: Fazendo Login

Ao abrir o sistema pela primeira vez (ou quando sua sessão expirar), você verá a **tela de login**:

![Tela de Login do Sistema Gestor](manual pdf/01_tela_login.png)

### Como preencher o login:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚     Administração do Django          â”‚
â”‚                                      â”‚
â”‚  Usuário: [________________]         â”‚
â”‚                                      â”‚
â”‚  Senha:   [________________]         â”‚
â”‚                                      â”‚
â”‚        [ Iniciar sessão ]            â”‚
â”‚                                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

| Campo | O que preencher | Exemplo |
|-------|----------------|---------|
| **Usuário** | O nome de usuário que o administrador criou para você | `maria`, `joao.vendas`, `admin` |
| **Senha** | A senha fornecida pelo administrador (ou a que você alterou) | `****` |

### Passo a Passo:

1. âœï¸ No campo **"Usuário"**, digite seu nome de usuário
2. ðŸ”‘ No campo **"Senha"**, digite sua senha (os caracteres aparecerão como pontinhos â€¢â€¢â€¢â€¢ por segurança)
3. ðŸ–±ï¸ Clique no botão **"Iniciar sessão"**
4. âœ… Pronto! Você será levado automaticamente para o **Painel Principal**

> [!WARNING]
> **Se o login falhar:**
> - Verifique se o **Caps Lock** (tecla de maiúsculas) está desligado
> - Confira se o usuário e senha estão corretos (diferenciam maiúsculas de minúsculas)
> - Se esqueceu a senha, entre em contato com o administrador do sistema

---

## 5. A Tela Principal (Dashboard)

Após fazer login com sucesso, você verá o **Painel Principal (Dashboard)** — a tela inicial do sistema:

![Dashboard do Sistema Gestor](manual pdf/02_tela_dashboard.png)

### O que você encontra no Dashboard:

A tela principal tem **3 grandes áreas**:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚        â”‚  BARRA SUPERIOR (Topbar)                 â”‚
â”‚  MENU  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚        â”‚                                          â”‚
â”‚ LATERALâ”‚  ÃREA DE CONTEÃšDO                        â”‚
â”‚        â”‚                                          â”‚
â”‚(Sidebarâ”‚  â€¢ Cards com indicadores (KPIs)          â”‚
â”‚        â”‚  â€¢ Gráfico de Faturamento                â”‚
â”‚        â”‚  â€¢ Vendas Recentes                       â”‚
â”‚        â”‚  â€¢ Lembretes                             â”‚
â”‚        â”‚                                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Indicadores (KPIs) do Dashboard:

| Indicador | O que mostra |
|-----------|-------------|
| ðŸ‘¥ **Total de Clientes** | Quantos clientes estão cadastrados |
| ðŸ“¦ **Total de Produtos** | Quantos produtos você tem no catálogo |
| ðŸ›’ **Total de Vendas** | Número de vendas realizadas |
| ðŸ’° **Faturamento do Mês** | Quanto você vendeu no mês atual (R$) |
| ðŸ¦ **Saldo em Caixa** | Soma dos saldos das suas contas bancárias |
| âš ï¸ **Estoque Baixo** | Produtos com estoque abaixo do mínimo |
| ðŸ†• **Clientes Novos** | Clientes cadastrados neste mês |

> [!TIP]
> O Dashboard atualiza automaticamente toda vez que você acessa. Ã‰ seu "resumo diário" do negócio!

---

## 6. Conhecendo o Menu Lateral (Sidebar)

O **Menu Lateral** fica Ã  esquerda da tela e dá acesso a todas as funçÃµes do sistema:

![Menu Lateral do Sistema Gestor](manual pdf/04_sidebar_menu.png)

### Estrutura do Menu:

O menu está organizado em **seçÃµes** para facilitar a navegação:

| Seção | Itens do Menu | Para que serve |
|-------|--------------|----------------|
| **Menu Principal** | ðŸ“Š Visão Geral | Painel de controle (Dashboard) |
| | ðŸ“ˆ BI de Resultados | Relatórios avançados e gráficos |
| **Gestão Comercial** | ðŸ‘¥ Gestão de Clientes | Cadastrar e consultar clientes |
| | ðŸ›’ Gestão de Vendas | Registrar e acompanhar vendas |
| **Gestão de Estoque** | ðŸ“¦ Gestão de Produtos | Cadastrar e controlar produtos |
| | ðŸ—ï¸ Gestão de Almoxarifado | Materiais de uso interno |
| **Gestão Operacional** | âš™ï¸ Gestão de Produção (PCP) | Fichas técnicas e ordens de produção |
| | ðŸ”§ Ordens de Serviço (O.S.) | Serviços e manutençÃµes |
| | ðŸ›ï¸ Gestão de Compras | Pedidos de compra e cotaçÃµes |
| **Gestão Financeira** | ðŸ’³ Gestão de Caixa | Entradas e saídas de dinheiro |
| | ðŸ’¹ Gestão de Receitas | Receitas do negócio |
| | ðŸ“‹ Gestão de Reembolsos | Reembolsos de colaboradores |
| **Gestão Fiscal** | ðŸ§¾ Gestão de Notas | Notas fiscais |
| **ConfiguraçÃµes** | âš™ï¸ Gestão de Sistema | ConfiguraçÃµes avançadas |

### Como navegar:

1. **Clique** em qualquer item do menu para abrir a tela correspondente
2. O item ativo fica destacado em **roxo** para você saber onde está
3. Para voltar ao início, clique em **"Visão Geral"** ou no logo **"SISTEMA GESTOR"** no topo do menu

> [!NOTE]
> Se a sua empresa configurou uma marca personalizada (White Label), o logo e nome da empresa aparecerão no topo do menu lateral.

---

## 7. Conhecendo a Barra Superior (Topbar)

No topo da tela, você encontra a **Barra Superior** com funçÃµes rápidas:

![Barra Superior e Menu do Usuário](manual pdf/03_topbar_menu.png)

### Elementos da Barra Superior:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ“„ Título da Página          ðŸ””  ðŸŒ™ Escuro   ðŸ‘¤ admin â–¼     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

| Elemento | Ãcone | O que faz |
|----------|-------|-----------|
| **Título da Página** | ðŸ“„ | Mostra o nome da seção em que você está |
| **NotificaçÃµes** | ðŸ”” | Alertas de reembolsos pendentes (aparece só quando há pendências) |
| **Alternar Tema** | ðŸŒ™ / â˜€ï¸ | Troca entre **Modo Claro** e **Modo Escuro** |
| **Menu do Usuário** | ðŸ‘¤ | Seu nome e opçÃµes de conta |

### Menu do Usuário (ao clicar no seu nome):

| Opção | O que faz |
|-------|-----------|
| ðŸŽ¨ **Personalizar Marca** | Configura o nome e logo da sua empresa no sistema |
| âš™ï¸ **Ajustes** | ConfiguraçÃµes da conta |
| ðŸšª **Sair do Sistema** | Faz logout e volta para a tela de login |

### Modo Escuro / Claro:

O sistema oferece dois temas visuais:

| Tema | Descrição | Quando usar |
|------|-----------|-------------|
| â˜€ï¸ **Claro** | Fundo branco, texto escuro | Ambientes bem iluminados |
| ðŸŒ™ **Escuro** | Fundo escuro, texto claro | Ambientes com pouca luz / preferência pessoal |

> [!TIP]
> A sua preferência de tema é **salva automaticamente** no seu navegador. Na próxima vez que acessar, o sistema lembrará da sua escolha!

---

## 8. Como Sair do Sistema

Para sair do sistema com segurança, siga estes passos:

1. ðŸ‘¤ Clique no **seu nome** (canto superior direito)
2. ðŸ“‹ Um menu aparecerá com opçÃµes
3. ðŸšª Clique em **"Sair do Sistema"** (texto em vermelho)
4. âœ… Você será desconectado e levado de volta Ã  tela de login

> [!IMPORTANT]
> **Sempre faça logout ao sair!** Isso protege seus dados, especialmente em computadores compartilhados.

### Atalho rápido:
Você também pode sair acessando diretamente: `/admin/logout/` na barra de endereço.

---

## 9. Primeiro Acesso — Senha Inicial

Se é a **primeira vez** que você acessa o sistema:

### Quem cria sua conta?

O **Administrador do Sistema** cria sua conta de usuário. Solicite a ele:

| Informação | Descrição |
|-----------|-----------|
| ðŸ‘¤ **Nome de Usuário** | Seu login para acessar (ex: `maria`, `joao.vendas`) |
| ðŸ”‘ **Senha Inicial** | Uma senha temporária para o primeiro acesso |
| ðŸŽ¯ **Perfil de Permissão** | Define o que você pode acessar no sistema |

### Perfis de Permissão:

| Perfil | O que pode acessar |
|--------|-------------------|
| ðŸ‘‘ **Administrador** | Tudo — acesso total a todos os módulos |
| ðŸ“Š **Gerente** | Relatórios, aprovaçÃµes e visão geral |
| ðŸ›’ **Vendedor** | Clientes, vendas e consulta de estoque |
| âš™ï¸ **Operador** | Produção, serviços e movimentaçÃµes |
| ðŸ—ï¸ **Almoxarife** | Acesso exclusivo ao Almoxarifado |

> [!NOTE]
> Se você tem perfil **Almoxarife**, ao fazer login será levado diretamente para o **Dashboard do Almoxarifado** (em vez do Dashboard geral).

---

## 10. Como Trocar sua Senha

Recomendamos trocar sua senha após o primeiro acesso:

### Passo a Passo:

1. Após fazer login, acesse na barra de endereço: `/admin/password_change/`
2. Preencha os campos:
   - **Senha antiga:** sua senha atual
   - **Nova senha:** a senha que deseja usar
   - **Confirmação:** repita a nova senha
3. Clique em **"Alterar minha senha"**

### Dicas para criar uma boa senha:

| âœ… Faça | âŒ Não faça |
|---------|------------|
| Use pelo menos 8 caracteres | Não use `123456` ou `senha123` |
| Misture letras, números e símbolos | Não use seu nome ou data de nascimento |
| Use uma frase que só você sabe | Não compartilhe com outras pessoas |

---

## 11. Usando no Celular ou Tablet

O Sistema Gestor é **100% responsivo** — funciona em qualquer tamanho de tela!

### No celular/tablet:

- O **menu lateral** fica escondido para economizar espaço
- Toque no ícone **â˜°** (três linhas, canto superior esquerdo) para abrir o menu
- Toque em qualquer opção do menu para navegar
- Toque fora do menu (ou no fundo escuro) para fechá-lo

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ â˜°  Visão Geral     ðŸ‘¤ â–¼ â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                          â”‚
â”‚  Cards de KPIs           â”‚
â”‚  (empilhados             â”‚
â”‚   verticalmente)         â”‚
â”‚                          â”‚
â”‚  Gráfico                 â”‚
â”‚                          â”‚
â”‚  Vendas Recentes         â”‚
â”‚                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

> [!TIP]
> Para a melhor experiência no celular, use o navegador **Google Chrome** e segure o celular na **posição vertical** (retrato).

---

## 12. Perguntas Frequentes

### â“ "Não consigo acessar o sistema. O que faço?"

Verifique os seguintes pontos:

| Problema | Solução |
|----------|---------|
| Página não carrega | Verifique se o endereço está correto e se o servidor está ligado |
| "Conexão recusada" | O servidor pode estar desligado. Contate o administrador |
| "Página não encontrada" | Verifique se digitou o endereço correto (sem espaços) |
| Login e senha não funcionam | Verifique o Caps Lock e se as credenciais estão corretas |

### â“ "Esqueci minha senha. Como recupero?"

O sistema não possui recuperação automática de senha. Entre em contato com o **administrador do sistema** para que ele redefina sua senha pelo painel administrativo.

### â“ "Posso usar em mais de um computador ao mesmo tempo?"

**Sim!** Você pode estar logado em vários dispositivos ao mesmo tempo. Porém, alteraçÃµes feitas em um dispositivo podem não aparecer instantaneamente no outro até que você **atualize a página** (F5).

### â“ "O sistema funciona sem internet?"

Depende da configuração:
- **Rede Local:** Sim, funciona sem internet, desde que seu computador esteja na mesma rede que o servidor
- **Nuvem (SaaS):** Não, necessita de conexão com a internet

### â“ "O que é o 'Painel Administrativo' (/admin/)?"

Ã‰ a área de configuração avançada do sistema, acessível apenas por **Administradores**. Nele é possível criar usuários, definir permissÃµes e gerenciar configuraçÃµes do sistema.

### â“ "Minha tela está diferente das imagens do manual. Por que?"

Se a sua empresa configurou a **Personalização de Marca (White Label)**, o logo e o nome da empresa podem ser diferentes. As funcionalidades, porém, são as mesmas.

---

## ðŸ“ž Suporte

Se você tiver dúvidas ou problemas que não foram resolvidos por este manual:

1. **Primeiro:** Consulte este manual e tente os passos descritos
2. **Segundo:** Entre em contato com o administrador do sistema da sua empresa
3. **Terceiro:** Contate o suporte técnico da **JR Solutions Tecnologia**

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 2: Gestão de Clientes

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Comercial > Gestão de Clientes

---

## ðŸ“‹ Ãndice deste Capítulo

1. [Visão Geral do Módulo](#1-visão-geral-do-módulo)
2. [A Tela de Clientes (Listagem)](#2-a-tela-de-clientes-listagem)
3. [Como Cadastrar um Novo Cliente](#3-como-cadastrar-um-novo-cliente)
4. [Dicas de Preenchimento: PF vs PJ](#4-dicas-de-preenchimento-pf-vs-pj)
5. [Como Editar um Cliente](#5-como-editar-um-cliente)
6. [Detalhes e Histórico do Cliente](#6-detalhes-e-histórico-do-cliente)
7. [Inativar vs Excluir](#7-inativar-vs-excluir)
8. [Perguntas Frequentes](#8-perguntas-frequentes)

---

## 1. Visão Geral do Módulo

A **Gestão de Clientes** é o coração do setor comercial. Neste módulo, você centraliza todas as informaçÃµes das pessoas e empresas que compram de você.

Manter este cadastro atualizado é fundamental porque os dados daqui são usados em todo o sistema:
- Para gerar vendas e orçamentos
- Para emitir Ordens de Serviço
- Para preencher automaticamente as Notas Fiscais

> **Acesso:** No Menu Lateral, vá em **Gestão Comercial** â†’ **Gestão de Clientes**.

---

## 2. A Tela de Clientes (Listagem)

Ao abrir o módulo, você verá a lista com todos os seus clientes cadastrados:

![Tela de Lista de Clientes](manual pdf/05_tela_lista_clientes.png)

### Ferramentas disponíveis na tela:

| Ferramenta | O que faz |
|------------|-----------|
| ðŸ” **Busca (Pesquisa)** | Digite parte do nome, CPF/CNPJ ou telefone para encontrar um cliente rapidamente. |
| ðŸŸ¢ **Status** | Uma etiqueta verde indica que o cliente está **Ativo**. Uma cinza indica que está **Inativo**. |
| âž• **Botão "Novo Cliente"** | Inicia o cadastro de um novo cliente. |
| âš™ï¸ **Coluna "AçÃµes"** | BotÃµes rápidos para **Editar** (âœï¸ lápis) ou **Excluir** (ðŸ—‘ï¸ lixeira). |

> [!TIP]
> Use a barra de busca para verificar se um cliente já está cadastrado antes de criar um novo, evitando cadastros duplicados!

---

## 3. Como Cadastrar um Novo Cliente

Para adicionar um cliente ao sistema:

1. Na tela de Clientes, clique no botão azul **"Novo Cliente"**.
2. O formulário de cadastro se abrirá:

![Tela de Cadastro de Cliente](manual pdf/06_tela_cadastro_cliente.png)

### Passo a passo do preenchimento:

**Dados Principais (Obrigatórios):**
- **Nome:** Digite o nome completo ou a Razão Social.
- **Tipo:** Escolha entre **Pessoa Física** ou **Pessoa Jurídica**.
- **CPF / CNPJ:** Digite apenas os números (o sistema colocará os pontos e traços automaticamente). Este número não pode se repetir em outro cadastro!
- **Status Ativo:** Deixe marcado para que o cliente apareça na hora de fazer uma venda.

**Contato & Endereço (Opcionais, mas recomendados):**
- **E-mail:** Importante para enviar orçamentos e NFs.
- **Telefone:** Principal meio de contato (WhatsApp).
- **Endereço Completo:** Rua, número, bairro, cidade, estado e CEP (obrigatório se for emitir Nota Fiscal no futuro).

3. Após preencher, clique no botão **"Salvar"**.
4. Uma mensagem verde de sucesso aparecerá e o cliente já estará na sua lista.

---

## 4. Dicas de Preenchimento: PF vs PJ

O sistema adapta algumas regras dependendo se o seu cliente é uma Pessoa Física (PF) ou Pessoa Jurídica (PJ).

| Tipo | Documento Exigido | Dica para Notas Fiscais |
|------|-------------------|-------------------------|
| **Pessoa Física (PF)** | CPF (11 dígitos) | Ideal para consumidor final (varejo). |
| **Pessoa Jurídica (PJ)** | CNPJ (14 dígitos) | Além do CNPJ, ao emitir nota para PJ, preencha corretamente o endereço completo e verifique se a empresa possui Inscrição Estadual (IE). |

> [!IMPORTANT]
> O sistema não permite cadastrar **dois clientes com o mesmo CPF ou CNPJ**. Se você tentar, o sistema mostrará um erro avisando que o documento já existe.

---

## 5. Como Editar um Cliente

Se você digitou algo errado ou se o cliente mudou de telefone/endereço:

1. Encontre o cliente na lista.
2. Na coluna **AçÃµes**, clique no ícone de **Lápis (âœï¸)**.
3. Altere as informaçÃµes necessárias no formulário.
4. Clique em **"Salvar"**.

---

## 6. Detalhes e Histórico do Cliente

Você quer saber o que este cliente já comprou? 

1. Na lista de clientes, clique em cima do **Nome do Cliente** (ele funciona como um link).
2. Uma nova tela se abrirá mostrando:
   - Os dados completos do cliente em formato de cartão.
   - **Histórico de Vendas:** Uma tabela com todas as vendas já feitas para ele, com status (Confirmada, Entregue, etc.) e valores totais.

Esta visão é excelente para entender o perfil de compra do seu cliente!

---

## 7. Inativar vs Excluir

Com o tempo, sua base de clientes pode crescer muito. Como lidar com clientes antigos?

### Excluir (ðŸ—‘ï¸ Lixeira)
- **O que faz:** Apaga permanentemente o cadastro.
- **Quando usar:** Quando você cadastrou algo errado por engano.
- **Limitação:** Você **NÃƒO** pode excluir um cliente que já possui uma Venda ou Ordem de Serviço registrada no nome dele. O sistema protegerá esses dados para não quebrar seu histórico financeiro.

### Inativar (Desmarcar "Ativo")
- **O que faz:** Mantém o histórico do cliente salvo, mas ele deixa de aparecer na lista na hora de fazer novas vendas.
- **Como fazer:** Clique em Editar (âœï¸) e desmarque a caixinha **"Ativo"**, depois salve.
- **Quando usar:** Esta é a **melhor prática** para clientes antigos, problemáticos ou que fecharam as portas.

---

## 8. Perguntas Frequentes

### â“ "Estou tentando salvar, mas aparece 'CPF/CNPJ já cadastrado'. E agora?"
Isso significa que este documento já existe na sua base. Use a barra de busca na lista de clientes, digite o CPF/CNPJ e você encontrará o cadastro original para editá-lo.

### â“ "Não consigo excluir um cliente, o botão de lixeira dá erro."
Se o cliente tiver feito qualquer compra (Venda) com você no passado, a exclusão é bloqueada por segurança. A solução correta é **Inativar** o cliente (veja a seção 7).

### â“ "O CEP busca o endereço automaticamente?"
Na versão atual, o preenchimento de endereço é manual, mas recomendamos preencher no formato completo (Rua X, 123 - Bairro Y) para evitar problemas na emissão de Notas Fiscais depois.

### â“ "Posso cadastrar um cliente sem CPF?"
Para usar todas as funcionalidades do sistema (especialmente vendas oficiais e notas fiscais), o CPF/CNPJ é o identificador único exigido.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 3: Gestão de Vendas

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Comercial > Gestão de Vendas

---

## ðŸ“‹ Ãndice deste Capítulo

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

> **Acesso:** No Menu Lateral, vá em **Gestão Comercial** â†’ **Gestão de Vendas**.

---

## 2. Entendendo os Status da Venda

Toda venda possui um "Status" (situação atual). Ã‰ muito importante entender a diferença entre eles, pois o sistema reage de forma diferente para cada um:

| Status | Como aparece | O que significa e o que faz no sistema |
|--------|--------------|----------------------------------------|
| **Rascunho** | ðŸŸ¡ Amarelo | Ã‰ apenas um orçamento. **NÃƒO** tira produto do estoque e **NÃƒO** gera receita no financeiro. Você pode editar Ã  vontade. |
| **Confirmada** | ðŸŸ¢ Verde | O cliente fechou negócio! O sistema **TIRA** o produto do estoque e **CRIA** uma transação de Receita no Financeiro. |
| **Entregue** | ðŸ”µ Azul | O cliente já recebeu a mercadoria. Financeiramente e no estoque, é a mesma coisa que "Confirmada". |
| **Cancelada** | ðŸ”´ Vermelho | A venda deu errado. O sistema **DEVOLVE** o produto para o estoque e **ESTORNA** (cancela) o lançamento no Financeiro. |

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
4. O sistema calculará o **Subtotal** (Qtd Ã— Preço).
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

âœ… **No Estoque:** O sistema vai silenciosamente até o módulo de estoque e dá baixa nas quantidades vendidas.
*Exemplo: Se você tinha 10 cadernos e vendeu 2, o estoque cai para 8 na hora.*

âœ… **No Financeiro:** O sistema vai ao módulo de Gestão de Caixa e cria um registro de "Receita", vinculando o valor ao cliente. O faturamento no seu Dashboard vai subir imediatamente!

---

## 5. Como Gerar Nota Fiscal da Venda

Você fechou a venda e agora o cliente quer a Nota Fiscal? Ã‰ simples:

1. Abra a venda que você acabou de salvar.
2. Na tela de detalhes da venda, haverá um botão chamado **"Gerar Nota Fiscal"**.
3. Clique nele.
4. O sistema vai pegar **todos os dados do cliente, os produtos e os valores** e preencher a Nota Fiscal para você no módulo Fiscal.
5. Lá, você só precisará conferir os impostos e clicar em "Emitir".

> [!IMPORTANT]
> Para a Nota Fiscal sair certinha, o cliente precisa estar com CPF/CNPJ e Endereço devidamente preenchidos no cadastro dele!

---

## 6. Cancelando ou Excluindo uma Venda

Errar é humano. Se você registrou uma venda errada, você tem duas opçÃµes:

### A opção correta: Cancelar (Mudar Status)
Abra a venda, clique em **Editar** e mude o status para **Cancelada**. 
Por que isso é melhor?
1. Fica o registro histórico de que a venda existiu mas não deu certo.
2. O sistema inteligentemente **devolve** os itens para o estoque.
3. O sistema **estorna** a entrada de dinheiro no caixa.

### A opção drástica: Excluir (Lixeira ðŸ—‘ï¸)
Se você clicar no ícone de lixeira, a venda some para sempre. O sistema também tem inteligência para desfazer o estoque e o financeiro caso você faça isso, mas você perde o histórico. Use apenas para vendas "teste" ou lançadas em duplicidade por erro.

---

## 7. Perguntas Frequentes

### â“ "Tentei vender um produto e deu erro dizendo 'Estoque insuficiente'."
O sistema te protege de vender algo que você não tem. Se o erro aparecer, você precisa primeiro ir no módulo de **Produtos** e dar "Entrada" na quantidade deste item no estoque.

### â“ "O cliente pediu um orçamento, mas ainda não vai pagar. O que eu faço?"
Crie a Venda e marque o Status como **Rascunho**. O rascunho não mexe no seu estoque nem no seu caixa.

### â“ "O preço do meu produto mudou só pra esse cliente. Preciso mudar o cadastro do produto?"
Não! Na hora de adicionar o "Item da Venda", você pode apagar o Preço Unitário sugerido e digitar o preço novo. Isso afeta **apenas esta venda**.

### â“ "A venda não gerou receita no financeiro, por quê?"
Verifique o **Status** da venda. Vendas em "Rascunho" ou "Cancelada" não geram receita. Apenas "Confirmada" ou "Entregue".

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 4: Gestão de Produtos e Estoque

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão de Estoque > Gestão de Produtos

---

## ðŸ“‹ Ãndice deste Capítulo

1. [Visão Geral do Estoque](#1-visão-geral-do-estoque)
2. [Como Cadastrar um Novo Produto](#2-como-cadastrar-um-novo-produto)
3. [Entendendo a Margem de Lucro](#3-entendendo-a-margem-de-lucro)
4. [Como Funciona o Controle de Estoque](#4-como-funciona-o-controle-de-estoque)
5. [Fazendo MovimentaçÃµes (Entradas e Saídas manuais)](#5-fazendo-movimentaçÃµes-entradas-e-saídas-manuais)
6. [O que significa "Estoque Baixo"?](#6-o-que-significa-estoque-baixo)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. Visão Geral do Estoque

O módulo de **Produtos** é o seu catálogo. Aqui você cadastra tudo o que sua empresa vende para os clientes.

> **Importante:** Não confunda este módulo com o **Almoxarifado**! 
> - **Gestão de Produtos:** Ã‰ o que você **VENDE** e dá lucro (ex: Capa de Celular, Consulta Médica, Cadeira).
> - **Almoxarifado:** Ã‰ o que você **CONSOME** trabalhando (ex: Papel A4, Café, Ferramentas de uso interno).

> **Acesso:** No Menu Lateral, vá em **Gestão de Estoque** â†’ **Gestão de Produtos**.

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
| **Categoria** | Para organizar seu catálogo. | `Roupas`, `EletrÃ´nicos`, `Serviços` |
| **Preço de Custo** | Quanto você pagou para seu fornecedor. | `R$ 20,00` |
| **Preço de Venda** | Por quanto você vai vender para o cliente. | `R$ 50,00` |
| **Ativo** | Se o produto está disponível para venda. | Deixe marcado. |

3. Clique em **"Salvar"**.

---

## 3. Entendendo a Margem de Lucro

Ao preencher o Preço de Custo e o Preço de Venda, o sistema calcula a sua **Margem de Lucro** automaticamente na tela de detalhes do produto.

A fórmula que o sistema usa é:
`((Preço Venda - Preço Custo) / Preço Custo) Ã— 100`

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

## 5. Fazendo MovimentaçÃµes (Entradas e Saídas manuais)

No Capítulo 3, vimos que a Venda dá saída no estoque sozinha. Mas e quando você **compra** mercadoria do fornecedor ou **perde** uma mercadoria (ex: quebrou)? Você precisa fazer uma movimentação manual.

1. Clique no nome do Produto na lista.
2. Na aba de Estoque, clique em **"Nova Movimentação"**.
3. Escolha o tipo de movimento:

| Tipo | O que faz no saldo | Quando usar |
|------|--------------------|-------------|
| ðŸŸ¢ **Entrada** | AUMENTA o saldo | Chegou mercadoria nova do fornecedor. |
| ðŸ”´ **Saída** | DIMINUI o saldo | O produto quebrou, estragou, ou foi doado. |
| ðŸŸ¡ **Ajuste** | MUDA para o número digitado | Fez contagem (inventário) e descobriu que tinha menos ou mais do que o sistema marcava. |
| ðŸ”µ **Devolução**| AUMENTA o saldo | O cliente devolveu um produto de uma venda passada. |

4. Informe a **Quantidade** e o **Motivo** (ex: "Reposição de fornecedor X").
5. Salve. O saldo atualizará na hora.

---

## 6. O que significa "Estoque Baixo"?

Lembra da **Quantidade Mínima** que explicamos no item 4?

Se o saldo atual do seu produto chegar ou ficar abaixo desse número, o produto ganha uma etiqueta vermelha de alerta.

Além disso, lá no **Dashboard (Visão Geral)**, o indicador de **Estoque Baixo** mostrará um número maior, avisando que é hora de ligar para o fornecedor.

---

## 7. Perguntas Frequentes

### â“ "Eu vendo SERVIÃ‡OS (ex: Instalação, Consulta). Como faço?"
Cadastre o serviço como se fosse um produto normal!
- No campo **SKU**, coloque algo como `SRV-01`.
- Na hora do estoque, você pode deixar o saldo muito alto (ex: 9999) ou simplesmente ignorar o alerta de estoque, pois serviço não se esgota.

### â“ "Tentei fazer uma 'Saída' manual de 10 unidades, mas deu erro."
O sistema te impede de ficar com "estoque negativo". Se você só tem 5 unidades no sistema, não pode dar saída manual de 10. Ele bloqueará a ação.

### â“ "Por que preciso colocar o Preço de Custo?"
Para que o módulo de **BI de Resultados** (os relatórios) consiga calcular o quanto sua empresa está dando de lucro real no fim do mês!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 5: Gestão Financeira e Caixa

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Financeira

---

## ðŸ“‹ Ãndice deste Capítulo

1. [Visão Geral do Financeiro](#1-visão-geral-do-financeiro)
2. [Gestão de Contas Bancárias](#2-gestão-de-contas-bancárias)
3. [Gestão de Caixa (Receitas e Despesas)](#3-gestão-de-caixa-receitas-e-despesas)
4. [Gestão de Reembolsos (Colaboradores)](#4-gestão-de-reembolsos-colaboradores)
5. [O Sino de Alerta de Reembolsos ðŸ””](#5-o-sino-de-alerta-de-reembolsos)
6. [Perguntas Frequentes](#6-perguntas-frequentes)

---

## 1. Visão Geral do Financeiro

O módulo financeiro é o cofre da empresa. Ã‰ aqui que você controla todo o dinheiro que **entra** (Receitas), todo o dinheiro que **sai** (Despesas), e gerencia os pedidos de **Reembolso** da sua equipe.

**Onde acessar?**  
No Menu Lateral, você verá a seção **Gestão Financeira** com três opçÃµes:
- ðŸ’³ **Gestão de Caixa** (Visão completa de tudo)
- ðŸ’¹ **Gestão de Receitas** (Mostra apenas as entradas de dinheiro)
- ðŸ“‹ **Gestão de Reembolsos** (Controle de despesas da equipe)

---

## 2. Gestão de Contas Bancárias

Antes de lançar valores, é ideal ter as contas da empresa cadastradas. O sistema já vem com uma conta padrão chamada "Caixa Interno", mas você pode cadastrar suas contas do banco.

> **Acesso:** Menu de ConfiguraçÃµes Administrativas (Restrito a Administradores).

Ao cadastrar uma conta bancária (Banco do Brasil, Nubank, Itaú), o sistema somará os saldos de todas elas e mostrará o **"Saldo em Caixa"** total lá no Dashboard principal!

---

## 3. Gestão de Caixa (Receitas e Despesas)

Na tela de **Gestão de Caixa**, você verá uma lista (extrato) com toda a movimentação da empresa.

### Tipos de Transação
O sistema usa cores para facilitar a identificação:
- ðŸŸ¢ **Receita:** Dinheiro que entrou (vendas, serviços prestados, rendimentos).
- ðŸ”´ **Despesa:** Dinheiro que saiu (pagamento de fornecedores, contas de luz, aluguel, salários).

### Como lançar uma movimentação manual:

Lembre-se que as Vendas (quando marcadas como Confirmadas) já geram Receitas automaticamente. Mas se você pagou a conta de luz, precisa lançar a Despesa na mão:

1. Clique em **"Nova Transação"**.
2. Escolha o **Tipo:** `Despesa`.
3. Preencha os campos essenciais:
   - **Descrição:** Ex: "Conta de Energia - Maio".
   - **Valor:** Ex: 150,00.
   - **Data da Transação:** Quando o pagamento foi feito.
   - **Categoria:** Ex: "Despesas Operacionais".
   - **Conta Bancária:** De qual conta o dinheiro saiu.
4. Marque a caixinha **"Paga"** (se já foi paga) e clique em **"Salvar"**.

> [!TIP]
> Se a conta for para o mês que vem, você pode lançar agora, preencher a **"Data de Vencimento"** e deixar a caixinha "Paga" **desmarcada**. Assim você cria um controle de "Contas a Pagar"!

---

## 4. Gestão de Reembolsos (Colaboradores)

Quando um funcionário compra algo para a empresa com o próprio dinheiro (ex: gasolina, pedágio, almoço com cliente), ele precisa ser reembolsado. O sistema tem uma tela exclusiva só para isso!

### Como pedir um reembolso:

1. Acesse **Gestão de Reembolsos**.
2. Clique em **"Novo Reembolso"**.
3. Preencha:
   - **Colaborador / Solicitante:** Quem está pedindo o dinheiro.
   - **Item/Descrição:** O que foi comprado (ex: "Abastecimento Carro Empresa").
   - **Valor:** R$ gasto.
   - **Data da Compra:** Quando a despesa ocorreu.
   - **Prioridade:** ðŸ”´ Alta (urgente), ðŸŸ¡ Média ou ðŸŸ¢ Baixa.
   - **Comprovante:** Anexe a foto da notinha fiscal ou o PDF do recibo (Obrigatório em muitas empresas!).
4. Clique em **"Salvar"**.

O status ficará como **"Pendente"** até o gestor financeiro pagar.

---

## 5. O Sino de Alerta de Reembolsos ðŸ””

Para o financeiro não esquecer de pagar a equipe, o sistema conta com uma notificação inteligente.

Se existir qualquer reembolso pendente no sistema, um **sino vermelho ðŸ””** começará a piscar lá na barra superior (no topo da tela, perto do seu nome).

1. Clique no sino.
2. Uma janelinha se abrirá mostrando **quantos** reembolsos estão aguardando pagamento.
3. Clique no botão azul "Gerar Reembolsos" para ir direto para a tela de aprovação.

### Como dar o reembolso como pago:
O gestor financeiro abre o pedido, confere o valor e a foto do comprovante e, após fazer o PIX/Transferência para o colaborador, edita o pedido e marca a caixinha **"Reembolsado?"**. 
O pedido sai da fila de pendentes e o sino para de piscar.

---

## 6. Perguntas Frequentes

### â“ "A venda que fiz gerou uma receita, mas o valor ficou 'Pendente' (Não Paga). Por quê?"
Isso acontece se o cliente fez a venda, mas disse que ia pagar depois (fiado ou boleto). Quando o dinheiro efetivamente cair na conta, você deve vir na Gestão de Caixa, editar a Receita e marcar como **"Paga"**.

### â“ "Posso excluir um reembolso depois que ele foi pago?"
Sim, mas não é recomendado. O ideal é manter o histórico. Se houve um erro, edite o valor ou adicione uma observação no campo apropriado.

### â“ "Como anexo a foto do comprovante no celular?"
Na hora de criar o reembolso, clique no botão "Escolher Arquivo". O celular abrirá a opção para "Tirar uma foto" na hora com a cÃ¢mera ou escolher uma foto da galeria de imagens.

### â“ "O Saldo em Caixa do sistema não está batendo com o do meu banco."
Isso ocorre quando existem transaçÃµes que aconteceram no banco, mas esqueceram de ser lançadas no sistema (ex: taxas bancárias de R$ 15,00). Você precisa lançar essas pequenas despesas no sistema para os valores baterem.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 6: Gestão Fiscal (Notas Fiscais)

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Fiscal > Gestão de Notas

---

## ðŸ“‹ Ãndice deste Capítulo

1. [Visão Geral do Módulo Fiscal](#1-visão-geral-do-módulo-fiscal)
2. [O Ciclo de Vida de uma Nota Fiscal](#2-o-ciclo-de-vida-de-uma-nota-fiscal)
3. [O Truque de Ouro: Gerar NF a partir da Venda](#3-o-truque-de-ouro-gerar-nf-a-partir-da-venda)
4. [Como Criar uma Nota Fiscal Avulsa (Manual)](#4-como-criar-uma-nota-fiscal-avulsa-manual)
5. [Como Cancelar uma Nota Fiscal](#5-como-cancelar-uma-nota-fiscal)
6. [Regras e ValidaçÃµes do Sistema](#6-regras-e-validaçÃµes-do-sistema)
7. [Perguntas Frequentes](#7-perguntas-frequentes)

---

## 1. Visão Geral do Módulo Fiscal

A Gestão Fiscal é a parte mais "séria" do sistema. Diferente das Vendas e Orçamentos que servem para controle interno, a Nota Fiscal é o seu comprovante legal para o Governo.

O sistema ajuda você a não esquecer os números, calcular impostos básicos e organizar os documentos sem precisar usar aquelas antigas planilhas do Excel.

> **Acesso:** No Menu Lateral, vá em **Gestão Fiscal** â†’ **Gestão de Notas**.

---

## 2. O Ciclo de Vida de uma Nota Fiscal

Assim como as vendas, as Notas Fiscais passam por estágios. Você não pode simplesmente "excluir" uma nota oficial. Entenda os três status:

| Status | Como aparece | O que você pode fazer |
|--------|--------------|-----------------------|
| ðŸ“ **Rascunho** | Cinza/Amarelo | Ã‰ a fase de digitação. A nota **ainda não tem validade fiscal**. Você pode editar valores, cliente, impostos livremente ou até apagar. |
| âœ… **Emitida** | Verde | A nota "valeu". Ela passa a compor seu faturamento fiscal oficial. **Você não pode mais editar uma nota Emitida**. Se algo estiver errado, você precisará cancelá-la. |
| âŒ **Cancelada**| Vermelho | O negócio foi desfeito. O valor dela "zera" nos seus relatórios fiscais. |

---

## 3. O Truque de Ouro: Gerar NF a partir da Venda

A forma mais fácil e rápida de criar uma Nota Fiscal no Sistema Gestor é **NÃƒO** usando o Módulo Fiscal!

Em vez de digitar tudo de novo, use a inteligência do sistema a seu favor:

1. Vá em **Gestão Comercial** â†’ **Gestão de Vendas**.
2. Abra a Venda (clicando nela) para a qual você quer emitir a nota.
3. Clique no botão mágico **"Gerar Nota Fiscal"**.

**O que o sistema faz?**
Ele pula o trabalho pesado! O sistema puxa automaticamente: o Cliente, a Data, os Produtos, o Subtotal e o Valor Total. E o melhor: ele já deixa a NF vinculada Ã quela Venda. Tudo o que você precisa fazer é revisar e confirmar a Emissão.

---

## 4. Como Criar uma Nota Fiscal Avulsa (Manual)

Se você precisa emitir uma NF que não está atrelada a uma Venda específica (ex: uma nota de demonstração ou correção):

1. Vá em **Gestão Fiscal** â†’ **Gestão de Notas**.
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

Uma vez emitida, a nota trava para ediçÃµes para evitar fraudes. Se o cliente desistiu da compra ou você digitou algo errado:

1. Abra a Nota Fiscal (que está com o status âœ… **Emitida**).
2. Clique no botão **"Cancelar NF"**.
3. O status dela mudará para âŒ **Cancelada** e o valor não somará mais nos seus relatórios.

---

## 6. Regras e ValidaçÃµes do Sistema

O módulo fiscal te impede de cometer erros matemáticos ou contábeis graves:

- ðŸ›‘ **Você não pode ter valores negativos.**
- ðŸ›‘ **O Desconto não pode ser maior que o Subtotal** (o sistema não deixa você dar um desconto maior do que o valor do produto em uma NF).
- ðŸ›‘ **Viagem no tempo:** A "Data de Saída" não pode ser *antes* da "Data de Emissão".

Se você tentar fazer alguma destas coisas, o sistema bloqueará a ação e mostrará um erro vermelho pedindo para você corrigir.

---

## 7. Perguntas Frequentes

### â“ "Por que não tem botão de Lixeira (Excluir) na minha Nota Fiscal?"
Por regras contábeis, documentos fiscais oficiais não "somem". Se a nota já foi Emitida, ela deve ser **Cancelada**. Você só consegue excluir (apagar do sistema) notas que ainda estejam na fase de **Rascunho**.

### â“ "O sistema envia a nota direto para a Receita Federal / Sefaz?"
Na versão atual, o sistema gera o controle e o cálculo financeiro/fiscal interno da sua empresa. Para a transmissão direta de arquivos XML, consulte o plano contratado da sua empresa ou repasse o Relatório Fiscal gerado pelo sistema para o seu contador.

### â“ "A nota não aparece no meu faturamento do Dashboard. Por quê?"
Lembre-se da regra de ouro: O faturamento principal no Dashboard é puxado do módulo de **Vendas** e da **Gestão de Caixa**. A tela Fiscal é um controle paralelo exigido por lei. Sempre faça Vendas no módulo comercial!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 7: Gestão de Almoxarifado

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão de Estoque > Gestão de Almoxarifado

---

## ðŸ“‹ Ãndice deste Capítulo

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

> **Acesso:** No Menu Lateral, vá em **Gestão de Estoque** â†’ **Gestão de Almoxarifado**. 
> Se você tem o perfil "Almoxarife", você já entra direto nesta tela ao fazer login!

---

## 2. Organizando a Casa: Locais e Endereços

Antes de colocar as coisas no Almoxarifado, o sistema permite que você mapeie fisicamente o seu depósito para nunca mais perder tempo procurando um parafuso ou um pacote de folha A4.

### Como funciona o mapeamento:

1. **Locais de Armazenamento:** Ã‰ o galpão ou a sala. (Exemplo: *Almoxarifado Central*, *Depósito Manutenção*).
2. **Endereçamento:** Ã‰ o "CEP" da prateleira. O sistema organiza isso em 3 níveis:
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
| ðŸŸ¡ **Solicitado** | O pedido foi criado e está aguardando o gestor olhar. |
| ðŸŸ¢ **Aprovado** | O gestor liberou! O funcionário já pode ir no balcão buscar o material. |
| ðŸ”´ **Recusado** | O gestor negou o pedido (ex: pediu 10 canetas, o gestor achou um exagero). |
| ðŸ”µ **Entregue** | O funcionário foi lá, pegou o material e o almoxarife deu baixa oficial no sistema. |

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

### â“ "Posso usar material do Almoxarifado para fazer uma Venda para um cliente?"
Não! O sistema separa as coisas. Se você comprou algo para uso interno e, de repente, decidiu vender, você precisará dar "Saída Manual" no Almoxarifado e "Entrada Manual" no Estoque de Vendas.

### â“ "A requisição foi 'Aprovada', o material já saiu do meu saldo?"
Ainda não. A aprovação é apenas a "assinatura" do chefe. O material só sai do saldo do sistema quando o status muda para **"Entregue"**, que significa que o material saiu fisicamente da prateleira.

### â“ "O que acontece se faltar material no Almoxarifado?"
O sistema possui a mesma inteligência do módulo de Vendas: se um item ficar abaixo da Quantidade Mínima estipulada, ele emitirá um alerta vermelho para que você avise o setor de Compras!

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 8: Gestão de Produção (PCP)

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Operacional > Gestão de Produção (PCP)

---

## ðŸ“‹ Ãndice deste Capítulo

1. [Visão Geral: Como o sistema entende a Produção?](#1-visão-geral-como-o-sistema-entende-a-produção)
2. [O Passo 1: A Ficha Técnica (A "Receita")](#2-o-passo-1-a-ficha-técnica-a-receita)
3. [O Passo 2: A Ordem de Produção (OP)](#3-o-passo-2-a-ordem-de-produção-op)
4. [A Mágica da Automação de Produção](#4-a-mágica-da-automação-de-produção)
5. [Perguntas Frequentes](#5-perguntas-frequentes)

---

## 1. Visão Geral: Como o sistema entende a Produção?

Se a sua empresa **monta**, **fábrica**, ou **transforma** materiais em um produto final antes de vender, você precisa deste módulo.

O sistema trabalha com a seguinte lógica:
Você pega "Matéria-Prima" do Almoxarifado âž¡ï¸ Transforma âž¡ï¸ Gera um "Produto Pronto" no Estoque de Vendas.

Para que o sistema saiba fazer isso sozinho, ele precisa de duas coisas: a Ficha Técnica (a receita do bolo) e a Ordem de Produção (a ordem para a cozinha começar a fazer o bolo).

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** â†’ **Gestão de Produção (PCP)**.

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

1. ðŸ­ **No Almoxarifado:** Ele vai "roubar" silenciosamente as matérias-primas que foram usadas e dar saída delas no sistema.
2. ðŸ“¦ **No Estoque de Vendas:** Ele vai gerar as unidades novas do Produto Final e colocá-las prontas para a equipe de Vendas vender.
3. ðŸ’° **No Financeiro/Custo:** Ele vai recalcular o preço de custo real do seu produto com base no que foi gasto na produção.

> [!WARNING]
> **A Trava de Segurança:** O sistema não é bobo. Se você mandar "Finalizar" a OP, mas não tiver matéria-prima suficiente no Almoxarifado para cobrir a produção, **ele dará um erro e bloqueará a finalização**. Ele vai te avisar: "Faltam X unidades da peça Y".

---

## 5. Perguntas Frequentes

### â“ "A produção deu errado e perdi material. E agora?"
Se a OP não deu certo, você pode cancelá-la. Mas a matéria-prima que foi perdida (estragou/quebrou) deve ser baixada manualmente lá no módulo de **Almoxarifado** usando a opção "Saída" e escrevendo no motivo: "Perda na produção".

### â“ "Posso fabricar algo sem fazer Ficha Técnica antes?"
Não. A Ficha Técnica é obrigatória para que a inteligência do sistema saiba o que deve ser retirado do Almoxarifado e o que deve ser gerado no Estoque. Se o produto é "exclusivo/único", crie uma ficha técnica simples para ele.

### â“ "Onde eu vejo o tempo que a minha equipe gastou em todas as OPs?"
No **Dashboard do PCP** (Painel principal de Produção), você tem indicadores de tempo estimado versus produzido e um histórico de todas as OPs em andamento.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
# ðŸ“˜ MANUAL DO USUÃRIO — SISTEMA GESTOR

### Capítulo 9: Ordens de Serviço (O.S.) e Gestão de Compras

**Versão:** 1.0 — Maio/2026  
**Módulo:** Gestão Operacional > O.S. e Compras

---

## ðŸ“‹ Ãndice deste Capítulo

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

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** â†’ **Ordens de Serviço (O.S.)**.

---

## 2. Tipos de Ordem de Serviço

O sistema permite que você gerencie diferentes tipos de serviço:

| Tipo | O que é | Exemplo |
|------|---------|---------|
| ðŸ”§ **Serviço ao Cliente** | Um trabalho pago feito para alguém de fora. | "Conserto da geladeira do Sr. João." |
| ðŸ—ï¸ **Manufatura Interna** | Serviço de adaptação de peças internas. | "Montagem da estante do galpão." |
| âš ï¸ **Manutenção Interna** | Conserto de algo da sua própria empresa. | "Arrumar a máquina de solda." |

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
`Aberta` (cliente trouxe) âž¡ï¸ `Em Execução` (técnico trabalhando) âž¡ï¸ `Finalizada` (pronta) ou `Cancelada`.

---

## 4. Gestão de Compras: Do Pedido ao Fornecedor

Quando o seu estoque fica baixo ou a equipe pede algo no Almoxarifado que acabou, é hora de comprar.

> **Acesso:** No Menu Lateral, vá em **Gestão Operacional** â†’ **Gestão de Compras**.

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

### â“ "A O.S. dá baixa no estoque das peças que eu usei no conserto?"
Sim! Assim que a O.S. é finalizada com itens consumidos listados, o sistema entende que aquelas peças foram gastas e atualiza o seu estoque automaticamente.

### â“ "Posso usar a Gestão de Compras só para registrar o que já comprei?"
Pode. Você pode criar o pedido e imediatamente colocá-lo como "Recebido". Porém, usar as ferramentas de Cotação e Status vai te dar muito mais controle e economia no futuro.

### â“ "Como crio uma conta a pagar para o Fornecedor que ganhou a cotação?"
Vá no módulo **Financeiro**, clique em "Gestão de Caixa" e crie uma nova "Despesa" em nome do fornecedor com a data combinada.

---

> **SISTEMA GESTOR** — Tecnologia para o crescimento do PME brasileiro.  
> Â© 2026 JR Solutions Tecnologia. Todos os direitos reservados.
