from pathlib import Path
import environ
import os
from celery.schedules import crontab

# Inicializa as variáveis de ambiente
env = environ.Env(
    # valores padrão
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DB_TYPE=(str, 'sqlite')
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório de logs (criado no boot — não some ao recriar o container)
LOG_DIR = Path(env('DJANGO_LOG_DIR', default=str(BASE_DIR / 'logs')))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Lê o arquivo .env se ele existir
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-seu-segredo-padrao')

DEBUG = env('DJANGO_DEBUG')

# Impede que produção rode acidentalmente com a chave placeholder ou em DEBUG.
# Em produção é obrigatório informar DJANGO_SECRET_KEY e DJANGO_DEBUG=False.
if not DEBUG and SECRET_KEY == 'django-insecure-seu-segredo-padrao':
    raise RuntimeError(
        'Ambiente de produção: defina uma DJANGO_SECRET_KEY forte no .env '
        '(e DJANGO_DEBUG=False) antes de iniciar o serviço.'
    )

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')

# Confia nos domínios informados para requisições seguras (CSRF) em produção
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])

# Configurações de Segurança e HTTPS para Produção
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------------------
# ADMINS + Email (aviso de erro 500 em produção)  —  item 2
#   Configure DJANGO_ADMIN_EMAILS no .env com os emails separados por vírgula.
# ---------------------------------------------------------------------------
_ADMIN_EMAILS = [e.strip() for e in env('DJANGO_ADMIN_EMAILS', default='')
                 .split(',') if e.strip()]
ADMINS = [('Administrador', e) for e in _ADMIN_EMAILS]
MANAGERS = ADMINS

# Backend de email. Padrão = console (não entrega de verdade; escreve no log do
# processo). Para o aviso de erro CHEGAR no seu email, configure um SMTP no .env:
#   EMAIL_HOST_USER / EMAIL_HOST_PASSWORD (ex.: app password do Gmail) e
#   DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND = env(
    'DJANGO_EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL',
                         default='sistema@jrsolutions.com.br')
SERVER_EMAIL = env('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# ---------------------------------------------------------------------------
# LOGGING profissional (arquivos com rotação diária + console + email) — item 1
#   Gera logs/gestor.log  (tudo, rotaciona a cada 30 dias)
#   Gera logs/gestor_errors.log  (só erros, retém 60 dias — histórico p/ achar erro)
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} '
                      '{filename}:{lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': str(LOG_DIR / 'gestor.log'),
            'when': 'midnight',
            'backupCount': 30,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_errors': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': str(LOG_DIR / 'gestor_errors.log'),
            'when': 'midnight',
            'backupCount': 60,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'level': 'ERROR',
        },
        'mail_admins': {
            'class': 'meigestao_app.core.logging_handlers.SafeAdminEmailHandler',
            'formatter': 'verbose',
        },
        'telegram': {
            'class': 'meigestao_app.core.logging_handlers.TelegramBotHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_errors', 'mail_admins', 'telegram'],
            'level': 'ERROR',
            'propagate': False,
        },
        'meigestao_app': {
            'handlers': ['console', 'file', 'file_errors', 'telegram'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
        '': {  # root / fallback
            'handlers': ['console', 'file', 'file_errors'],
            'level': 'WARNING',
        },
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Local apps
    'meigestao_app.core',
    'meigestao_app.vendas',
    'meigestao_app.clientes',
    'meigestao_app.estoque',
    'meigestao_app.financeiro',
    'meigestao_app.fiscal',
    'meigestao_app.usuarios',
    'meigestao_app.almoxarifado',
    'meigestao_app.compras',
    'meigestao_app.servicos',
    'meigestao_app.producao',
    'meigestao_app.relatorios',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'meigestao_app.core.middleware.SaaSPlanRestrictionMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'meigestao_app.core.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Configuração Dinâmica de Banco de Dados
if env('DB_TYPE') == 'postgres':
    DATABASES = {
        'default': env.db(),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # Timeout para evitar 'database is locked' em operacoes concorrentes.
            # Padrao do Django e 5s; em testes com threads precisamos de mais.
            'OPTIONS': {
                'timeout': 20,
            },
            'TEST': {
                'NAME': BASE_DIR / 'test_db.sqlite3',
            },
        },
    }

    # Aplica PRAGMA journal_mode=WAL no SQLite para permitir leituras
    # durante escritas (testes com threads concorrentes).
    from django.db.backends.signals import connection_created

    def _ativar_wal(sender, connection, **kwargs):
        if connection.vendor == 'sqlite':
            cursor = connection.cursor()
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')

    connection_created.connect(_ativar_wal)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

LANGUAGES = [
    ('pt-br', 'Português Brasileiro'),
]

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [BASE_DIR / 'static']

# Configuração para WhiteNoise servir arquivos compactados e com cache longo
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'core:login'

LOGIN_REDIRECT_URL = '/'

# ---------------------------------------------------------------------------
# Celery (worker + agendador/beat)
# ---------------------------------------------------------------------------
# O broker e o result backend usam o mesmo Redis. Em produção a URL vem da
# variável de ambiente REDIS_URL (definida no docker-compose.yml).
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/1')
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Relatório financeiro noturno (Cientista Financeiro), diário à 00:00.
CELERY_BEAT_SCHEDULE = {
    'bi-financeiro-noturno': {
        'task': 'meigestao_app.financeiro.tasks.processar_bi_financeiro_noturno',
        'schedule': crontab(hour=0, minute=0),
    },
}

# ─── Asaas (pagamentos / cobrança) ───────────────────────────────────────
# Chave de API (produção 'aact_prod_...' ou sandbox). Lida direto de os.environ
# porque o helper env() do django-environ usa cache tirado antes do read_env(.env).
ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY', '')
ASAAS_BASE_URL = os.environ.get('ASAAS_BASE_URL', 'https://api.asaas.com/v3')
# Autenticação do webhook (opcional; mesmo vazio, validamos re-consultando a API).
ASAAS_WEBHOOK_TOKEN = os.environ.get('ASAAS_WEBHOOK_TOKEN', '')
