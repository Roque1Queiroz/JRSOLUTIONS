# Guia Técnico de Implantação: SISTEMA GESTOR (PME/SaaS)

Este documento fornece as diretrizes técnicas para a implantação, configuração e manutenção do **SISTEMA GESTOR**, utilizando a arquitetura híbrida conteinerizada (Docker) com suporte SaaS multi-tenant.

---

## 🏗️ Arquitetura do Sistema

O SISTEMA GESTOR foi projetado para ser resiliente e escalável, operando sob uma pilha tecnológica moderna:

- **Core:** Django 4.2 (Python 3.11)
- **Banco de Dados:** PostgreSQL 15 (Produção) / SQLite (Desenvolvimento rápido)
- **Cache & Mensageria:** Redis
- **Background Workers:** Celery (para tarefas pesadas e relatórios)
- **Servidor Web:** Gunicorn + WhiteNoise (otimização de arquivos estáticos)
- **Orquestração:** Docker & Docker Compose

---

## 💼 Modelo SaaS — Planos e Limites

O sistema possui três planos de assinatura gerenciados diretamente via Django Admin (`/admin/ → Empresas`):

| Plano            | Preço Mensal | Preço Anual | Usuários | Módulos            | Suporte         | White Label | IA | APIs Custom | Atualizações  |
|------------------|-------------|-------------|----------|--------------------|-----------------|-------------|-----|-------------|----------------|
| **Básico**       | R$ 79/mês   | R$ 948/ano  | 2        | Clientes, Vendas, Estoque, Financeiro | E-mail | ✗ | ✗ | ✗ | Automática |
| **Profissional** | R$ 199/mês  | R$ 2.388/ano| 5        | Todos              | E-mail & Chat   | ✔ | ✔ | ✗ | Automática |
| **Enterprise**   | R$ 499/mês  | R$ 5.988/ano| 20       | Todos              | E-mail & Chat   | ✔ | ✔ | ✔ | Sob Demanda  |

> Para alterar o plano de uma empresa, acesse: **Django Admin → Core → Empresas → (selecionar empresa) → Plano Contratado**.

---

## 📋 Requisitos de Sistema (Servidor na Nuvem)

Para rodar o sistema na nuvem o servidor deve ter:

- **Docker Engine** instalado (Linux recomendado: Ubuntu 22.04 LTS).
- **Docker Compose** (V2 recomendado).
- Mínimo de **2 GB de RAM** disponível (recomendado 4 GB para Enterprise).
- **20 GB de espaço em disco** (para banco + mídias + logs).
- Um **domínio próprio** apontando para o IP do servidor.
- Proxy reverso **Nginx** ou **Traefik** com **certificado SSL (HTTPS)** via Let's Encrypt.

---

## 📁 O que NÃO é enviado ao container (`.dockerignore`)

Os seguintes arquivos/pastas são ignorados no build de produção para segurança e leveza da imagem:

- `venv/` — Ambiente virtual Python local.
- `.env` — Arquivo de variáveis de ambiente (segredos não ficam na imagem).
- `db.sqlite3` / `*.bak` — Banco de dados local e backups.
- `.git/`, `.vscode/` — Histórico e configurações de IDE.
- `media/`, `staticfiles/` — Gerenciados por volumes Docker persistentes.

---

## 🚀 Checklist de Deploy em Nuvem

### 1. Variáveis de Ambiente obrigatórias (`.env` no servidor)

```bash
# Django — Segurança
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=sua-chave-secreta-forte-e-unica-aqui
DJANGO_ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br
DJANGO_CSRF_TRUSTED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br
DJANGO_SECURE_SSL_REDIRECT=True

# Banco de Dados PostgreSQL
DB_TYPE=postgres
DB_NAME=gestor_db
DB_USER=postgres
DB_PASSWORD=senha-forte-do-banco
DB_HOST=db
DB_PORT=5432

# Redis / Celery
REDIS_URL=redis://redis:6379/1
```

> [!CAUTION]
> **NUNCA** commite o arquivo `.env` de produção no Git. Use um gerenciador de segredos (ex: AWS Secrets Manager, Railway Variables, Vault) em ambientes avançados.

### 2. Subindo os containers

```bash
# 1. Clone o repositório (branch de produção)
git clone https://github.com/seu-usuario/mei_gestao.git
git checkout feature/saas-planos

# 2. Copie e configure o .env
cp .env.example .env
nano .env   # Edite com suas variáveis reais

# 3. Suba todos os containers
docker-compose up -d --build

# 4. Verifique os logs
docker-compose logs -f web
```

> [!IMPORTANT]
> O `entrypoint.sh` já executa automaticamente:
> - `manage.py migrate` — Criação/atualização do banco de dados.
> - `manage.py collectstatic` — Coleta dos arquivos CSS/JS.
> O Gunicorn é iniciado automaticamente quando `DJANGO_DEBUG=False`.

### 3. Criar o superusuário inicial

```bash
docker exec -it mei_gestao_app python manage.py createsuperuser
```

### 4. Configurar o Nginx como Proxy Reverso

Exemplo de configuração `/etc/nginx/sites-available/gestor`:

```nginx
server {
    listen 80;
    server_name seudominio.com.br www.seudominio.com.br;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com.br www.seudominio.com.br;

    ssl_certificate /etc/letsencrypt/live/seudominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com.br/privkey.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🛠️ Manutenção e Comandos Úteis

### Realizar Backup do Banco de Dados

```bash
docker exec mei_gestao_db pg_dump -U postgres gestor_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Backup

```bash
cat backup_data.sql | docker exec -i mei_gestao_db psql -U postgres gestor_db
```

### Consultar Logs de Erro

```bash
docker-compose logs -f web
docker-compose logs -f worker
```

### Reiniciar apenas o container da aplicação

```bash
docker-compose restart web
```

### Atualizar o sistema (deploy de nova versão)

```bash
git pull origin feature/saas-planos
docker-compose up -d --build web
```

---

## 🛡️ Segurança e Boas Práticas

- **HTTPS obrigatório**: Use sempre certificado SSL (Let's Encrypt via Certbot é gratuito).
- **Cookies seguros**: `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` são ativados automaticamente quando `DJANGO_DEBUG=False`.
- **CSRF em produção**: Configure `DJANGO_CSRF_TRUSTED_ORIGINS` com o(s) domínio(s) do sistema.
- **Volumes**: Os dados do PostgreSQL e os arquivos de mídia estão em volumes Docker nomeados. **Nunca remova esses volumes sem backup.**
- **Gerenciamento de planos**: Feito via Django Admin pelo administrador do sistema. Sem código extra ou gateway de pagamento necessário no lançamento.

---

## 📊 Arquitetura de Controle de Acesso (SaaS)

```
Requisição HTTP
      │
      ▼
SecurityMiddleware → SessionMiddleware → AuthenticationMiddleware
      │
      ▼
SaaSPlanRestrictionMiddleware
  ├── Usuário não autenticado? → Passa sem verificar
  ├── is_staff / is_superuser? → Passa sem verificar (acesso irrestrito)
  ├── Plano Básico + rota restrita? → Redireciona para dashboard + mensagem
  ├── Plano Básico/Profissional + API customizada? → Redireciona + mensagem
  └── Demais casos → Passa normalmente
      │
      ▼
   View Django
```

---

**SISTEMA GESTOR — Tecnologia para o crescimento do PME brasileiro.**
