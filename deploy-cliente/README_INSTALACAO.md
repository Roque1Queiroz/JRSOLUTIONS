# 📦 Sistema Gestor — Instalação On-premise (pacote do cliente)

Este pacote instala o **Sistema Gestor** na máquina/servidor do próprio cliente.
Tudo roda isolado em contêineres Docker — **não precisa instalar Python, banco,
Redis ou Celery no sistema operacional**.

---

## 1. O que vem neste pacote

```
deploy-cliente/
│
├── docker-compose.yml        ← orquestra os 5 serviços
├── .env.example              ← modelo de configuração
├── .gitignore
├── app/                      ← PASTA PARA O CÓDIGO DO SISTEMA (você cola aqui)
├── README_INSTALACAO.md      ← este arquivo
└── scripts/
    ├── instalar.sh           ← instalador automático (1 comando)
    ├── atualizar.sh          ← atualizador Linux/macOS
    ├── atualizar.bat         ← atualizador Windows (duplo clique)
    └── patch_seguranca.sh    ← ajuste p/ HTTP local (com backup)
```

Ao subir, são criados **6 contêineres**:

| Serviço | Função |
|---|---|
| `web` | Django + Gunicorn — o sistema em si |
| `db` | PostgreSQL 15 (banco de dados) |
| `redis` | Fila do Celery |
| `worker` | Processa tarefas em segundo plano |
| `beat` | Agenda tarefas periódicas |
| `chatbot` | Assistente de IA do sistema (FastAPI + Groq) — porta 8003 **só na rede interna** |

> O `chatbot` não publica porta no host: quem conversa com ele é o Django
> (`/chatbot-api/*`), via `CHATBOT_INTERNAL_URL`. Nunca exponha a 8003.

---

## 2. Guia rápido (para o cliente)

> Requisito: **Docker** instalado e funcionando
> (Windows/Mac: use o **Docker Desktop**; Linux: `docker` + plugin `docker compose`).

### Passo 1 — Colocar o código
Copie o **código completo do Sistema Gestor** para a pasta `app/`,
mantendo a estrutura do projeto (a pasta `app/` deve ter `manage.py` e `Dockerfile`).

```
deploy-cliente/app/
   ├── manage.py
   ├── Dockerfile
   ├── config/  ...
   ├── meigestao_app/  ...
   └── ...
```

### Passo 2 — Instalar (automatizado)
Abra um terminal nesta pasta e rode:

```bash
cd deploy-cliente
bash scripts/instalar.sh
```

O instalador, sozinho:
1. verifica o Docker;
2. aplica o ajuste de segurança para HTTP local (com backup);
3. **gera um `.env` novo** (chave secreta e senha do banco aleatórios);
4. detecta o IP da máquina e preenche `DJANGO_ALLOWED_HOSTS`;
5. constrói as imagens e sobe tudo.

No final ele mostra o endereço de acesso e as credenciais geradas.

### Passo 3 — Criar o administrador
```bash
docker compose exec web python manage.py createsuperuser
```

### Passo 4 — Acessar
- Nesta máquina: `http://localhost:8000`
- De outra máquina da rede: `http://IP_DA_MAQUINA:8000`

---

## 3. Configuração manual (o que está no `.env`)

Se preferir ajustar na mão, esses são os campos importantes:

| Variável | O que é | Exemplo |
|---|---|---|
| `DJANGO_ALLOWED_HOSTS` | Endereços liberados | `localhost,127.0.0.1,192.168.0.10` |
| `DJANGO_SECRET_KEY` | Chave de segurança (única por instalação) | — |
| `DB_PASSWORD` | Senha do banco | — |
| `APP_PORT` | Porta de acesso do sistema | `8000` |
| `DJANGO_DEBUG` | `False` = produção (Gunicorn) | — |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirecionar para https | `False` em rede local |
| `DJANGO_SESSION_COOKIE_SECURE` | Cookie seguro | `False` em rede local |
| `DJANGO_CSRF_COOKIE_SECURE` | Cookie CSRF seguro | `False` em rede local |
| `GROQ_API_KEY` | Chave da Groq — liga o assistente de IA (vazio = chat desligado) | `gsk_...` |
| `CHATBOT_INTERNAL_URL` | Endereço interno do assistente | `http://chatbot:8003` |

> ⚠️ **Depois de editar o `.env`, recrie os containers:**
> `docker compose up -d --force-recreate`
> `docker restart` **não** basta — o `.env` só é lido na criação do container.

---

## 3.1 Assistente de IA (chatbot) — como ligar

O botão de chat do sistema só funciona se **duas** variáveis estiverem no `.env`
e se os containers forem **recriados** depois de preenchê-las:

```bash
# 1) edite o .env e garanta as duas linhas (sem aspas, sem espaço em volta do =)
GROQ_API_KEY=gsk_sua_chave_aqui
CHATBOT_INTERNAL_URL=http://chatbot:8003

# 2) recrie os containers que leem essas variáveis
docker compose up -d --force-recreate web chatbot

# 3) confira o log do bot (na 1ª subida ele indexa o manual do sistema)
docker compose logs --tail 30 chatbot
```

O que cada uma faz:

- **`GROQ_API_KEY`** — é a chave do modelo de IA (obtida em
  https://console.groq.com/keys). Sem ela o sistema **funciona normalmente**,
  mas o chat responde *"Assistente não configurado"*.
- **`CHATBOT_INTERNAL_URL`** — é o endereço do bot dentro da rede Docker.
  Sem ela o Django responde *"Assistente não configurado nesta instalação"*,
  mesmo com a chave preenchida (foi o erro mais comum na instalação).

Na primeira subida o bot baixa o modelo de embeddings (~470 MB) e indexa o
`MANUAL_EMBED_BOT.md` — **precisa de internet** nesse momento. Se falhar, o
sistema continua no ar e o bot tenta de novo na próxima vez que o container
subir (`docker compose restart chatbot`).

---

## 4. Comandos do dia a dia

```bash
docker compose ps            # status dos serviços
docker compose logs -f web   # ver logs do sistema
docker compose up -d         # iniciar (após reiniciar a máquina)
docker compose down          # parar tudo
docker compose exec web python manage.py migrate   # aplicar atualizações
docker compose exec db pg_dump -U gestor gestor > backup.sql   # backup
```

---

## 5. ⚠️ O que você (José) precisa decidir antes de entregar

### a) Como vai atualizar os clientes on-premise?

O cliente recebe o novo `sistema-gestor-cliente-vX.zip`, extrai só a pasta
`app/` por cima da antiga, e roda **uma** destas opções:

- **Windows:** duplo clique em `scripts/atualizar.bat`
- **Linux/macOS:** `bash scripts/atualizar.sh`

O script faz backup automático do banco (`backup_AAAAMMDD.sql`) e do `.env`
(`.env.bak`), reconstrói as imagens Docker e aplica as migrations. O
`.env`, os volumes Docker e todos os dados ficam intactos — só o código
muda.
(ex.: reenviar um `zip` numerado `v2.0`, `v2.1`...).

### b) Backup
O banco fica no volume `postgres_data` do cliente. Inclua um backup automático
no contrato (o projeto já tem `scripts/backup_banco.sh` — vale adaptar).

### c) Suporte e login inicial — e o teste grátis de 30 dias
O sistema tem uma **página de login público** em `http://<IP>:<PORT>/entrar/` (e
`/core/entrar/`). Entenda o fluxo de acesso inicial:
- A tela de login tem o link **"Criar conta grátis"** que leva ao **cadastro
  self-service** em `http://<IP>:<PORT>/cadastro/`: o visitante preenche os dados
  da empresa e já ganha **30 dias de teste grátis** (acesso total).
- Se preferir controle total, você (Jose) pode criar uma empresa/usuário
  manualmente (multi-tenant: a empresa precisa ser criada antes dos usuários).
- Após o prazo do teste, sem plano, o sistema mostra a tela de escolha de plano.

Após se cadastrar ou receber o usuário, **o login é sempre pelo `/entrar/`**.

### d) Pagamento (Asaas) no on-premise
O código de **pagamento Asaas (mensal)** está incluído, mas ele foi desenhado
para a nuvem (usa um webhook público para confirmar o pagamento). Numa
instalação local em rede privada, o webhook normalmente não é alcançável —
então o modelo mais simples é **licença direta**: você libera o acesso/converte
o plano pelo painel ao receber do cliente. Mantenha as variáveis `ASAAS_*` do
`.env.example` vazias nesse cenário.

### e) Versão nuvem vs. local
Ao gerar o pacote para um cliente, **não reutilize** a `DJANGO_SECRET_KEY`,
a senha do banco nem o IP. Cada instalação tem segredos próprios (o `instalar.sh`
já gera tudo novo de forma automática).

---

## 6. Solução de problemas

| Sintoma | Provável causa / correção |
|---|---|
| `ports: ... : required variable DB_PASSWORD` | Faltou gerar o `.env`. Rode `bash scripts/instalar.sh` |
| Não acessa de outra máquina | `DJANGO_ALLOWED_HOSTS` sem o IP + firewall com porta `APP_PORT` aberta |
| Tela de login não "segura" a sessão | Patch de segurança não aplicado — rode `bash scripts/patch_seguranca.sh` |
| Demora muito no 1º acesso | Normal na primeira vez (compila as imagens) |
| Chat responde "Assistente não configurado nesta instalação" | Falta `CHATBOT_INTERNAL_URL=http://chatbot:8003` no `.env` (ou o `web` não foi recriado) |
| Chat responde "Assistente não configurado" | Falta `GROQ_API_KEY` no `.env` |
| Chat responde "assistente indisponível" | Container `chatbot` parado/build quebrado — veja `docker compose logs chatbot` |
| Container `chatbot` reiniciando em loop | Sem internet para baixar o modelo de embeddings; veja o log acima |
| Chat "esquece" o histórico em toda atualização | Corrigido no v2.7 (histórico passou a ficar no volume) |
