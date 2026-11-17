# 🖥️ Guia de Instalação — Sistema Gestor no Cliente

> Este passo a passo é para a **pessoa que vai instalar o sistema** na máquina
> ou servidor da empresa do cliente. Não é preciso ser programador.
> Tempo estimado: **30 a 60 minutos** na primeira vez.

---

## O que você vai precisar

| Item | Onde encontrar |
|---|---|
| ☑️ Este pacote (`sistema-gestor-cliente-vX.Y.zip`) | Enviado pelo José |
| ☑️ **Docker Desktop** (Windows/Mac) ou **Docker** (Linux) | `https://www.docker.com/products/docker-desktop` |
| ☑️ Um terminal (Prompt de Comando / PowerShell / Terminal) | Já vem no sistema |
| ☑️ ~2 GB livres no disco | — |

> 💡 **Dica:** a instalação pode ser feita numa máquina comum da empresa.
> Para ficar ainda mais seguro, o ideal é um computador/servidor dedicado
> e que fique ligado quando precisarem acessar.

---

## Passo 1 — Extrair o pacote

1. Clique com o botão direito no arquivo `.zip`.
2. Escolha **"Extrair tudo..."** (Windows) ou o descompactador de sua preferência.
3. Vai aparecer a pasta **`sistema-gestor-cliente-vX.Y`**.

> Anote o caminho dessa pasta — você vai usá-lo nos próximos passos.
> Exemplo (Windows): `C:\Users\SeuUsuario\Downloads\sistema-gestor-cliente-v1.0`

---

## Passo 2 — Instalar o Docker

- **Windows / Mac:** instale o **Docker Desktop** e abra o programa.
  (ele cria um pequeno ícone 🐳 na barra de tarefas; aguarde ficar "Powered up").
- **Linux:** instale o pacote `docker` e o plugin `docker compose`.

> Para seu ambiente de trabalho recomendo: **Windows + Docker Desktop**.

---

## Passo 3 — Colocar o código do sistema na pasta `app`

Dentro da pasta extraída existe uma subpasta **`app`** vazia.
O José te enviará o **código do Sistema Gestor** em outra pasta/arquivo.

1. Copie **o conteúdo** do código do sistema.
2. Cole **dentro** da pasta `app`.

Ao final deve estar assim (veja que existe `manage.py` e `Dockerfile`):

```
sistema-gestor-cliente-vX.Y/
├── app/
│   ├── manage.py
│   ├── Dockerfile
│   ├── config/          ...
│   ├── meigestao_app/   ...
│   └── ...
├── docker-compose.yml
├── .env.example
├── GUIA_INSTALACAO_CLIENTE.md
└── scripts/  (instalar.sh + patch_seguranca.sh)
```

> ⚠️ **Importante:** não troque o conteúdo de outras pastas. Só a `app/` é para o código.

---

## Passo 4 — Rodar o instalador

### 🪟 No Windows (Prompt de Comando / PowerShell)

Abra o terminal e navegue até a pasta do pacote. Exemplo:

```cmd
cd C:\Users\SeuUsuario\Downloads\sistema-gestor-cliente-v1.0
```

Depois rode:

```cmd
scripts\instalar.bat
```

> 👷 Jurandir... digo, **o José pode te enviar o `instalar.bat`** já pronto,
> para não precisar digitar comandos. Se preferir usar o Linux/macOS,
> rode `bash scripts/instalar.sh`.

O instalador, **sozinho**, vai:
1. verificar o Docker;
2. aplicar o ajuste de segurança (com backup);
3. **gerar chaves de segurança novas** (senha do banco etc.);
4. detectar o IP da máquina e liberar o acesso;
5. construir e subir o sistema (a primeira vez demora alguns minutos).

No final, aparece na tela o endereço de acesso e as credenciais.

---

## Passo 5 — Criar o administrador

Ainda no terminal, rode:

```cmd
docker compose exec web python manage.py createsuperuser
```

Ele pergunta:
- **Username** → ex.: `admin`
- **Email** → endereço da empresa
- **Password** / **Password (again)** → uma senha forte
  (não aparece o que você digita — é normal)

> Anote usuário e senha: é o acesso de **administrador** da empresa.

---

## Passo 6 — Acessar o sistema

Abra o navegador e digite:

- Nesta máquina: `http://localhost:8000`
- De outra máquina da mesma rede: `http://IP_DA_MAQUINA:8000`
  *(o instalador mostra o IP no final)*

Pronto! Faça login com o administrador que você criou. 🎉

> 🎁 **Teste grátis de 30 dias:** para a empresa do cliente começar já com acesso
> total sem depender de cadastro manual, use o endereço `http://<IP da máquina>:<porta>/cadastro/`
> e preencha os dados da empresa. A conta nasce com **30 dias de teste grátis**.
> Ao terminar o prazo, o sistema pede a escolha de um plano para continuar
> (no seu caso, a liberação é combinada direto com o José).

---

## Uso do dia a dia

| Para... | Comando (no terminal, dentro da pasta) |
|---|---|
| Iniciar o sistema | `docker compose up -d` |
| Parar o sistema | `docker compose down` |
| Ver os registros | `docker compose logs -f web` |
| Fazer backup do banco | `docker compose exec db pg_dump -U gestor gestor > backup.sql` |
| Atualizar o sistema | substitua o conteúdo de `app/` pelo novo e rode `docker compose up -d --build` |

> **Backup:** combine com o José uma rotina de backup (ex.: rodar o comando de
> backup toda semana e guardar o arquivo `backup.sql` num pendrive ou nuvem).

---

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Erro `DB_PASSWORD ... required variable` | Faltou o `.env`. Rode o instalador (Passo 4). |
| Não abre em outro computador | Deixe `localhost` no `DJANGO_ALLOWED_HOSTS` **e** o IP da máquina; libere a porta `8000` no firewall. |
| Login "não segura" a sessão / recarrega e desloga | O instalador corrige isso; se ainda ocorrer, fale com o José. |
| Primeira vez muito lenta | Normal: está baixando e montando as imagens do Docker. |

---

## Quando chamar o José (suporte)

- Instalação numa **outra máquina específica** ou **servidor**.
- Querer **HTTPS** (cadeado 🔒) de verdade no endereço.
- Precisar de **backup automático** ou **novas versões**.
- Qualquer tela de erro que você não entendeu.

**Pergunte sempre por: versão do pacote, sistema (Windows/Linux) e o print da tela de erro.**

---

_© Sistema Gestor — pacote de instalação on-premise._
