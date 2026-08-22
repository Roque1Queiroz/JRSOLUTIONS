"""Patch idempotente: insere LOGGING profissional + ADMINS/email + Telegram na
VM de produção (config/settings.py). NÃO sobrescreve o arquivo; insere, com backup.

Modo de uso (na VM):
    python3 patch_telegram_logging_vm.py   # idempotente: rodar de novo não duplica

Bloqueios:
    * telegrafa: se já existir a marca '# ADMINS + Email (aviso de erro 500',
      não faz nada (protege contra dupla execução).
"""
import os
import time

SETTINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'config', 'settings.py')
# caminho real do projeto (script ficará em docs/ na VM)
alt = '/home/ubuntu/Sistema_Gestor/config/settings.py'
if not os.path.exists(SETTINGS) and os.path.exists(alt):
    SETTINGS = alt

MARK = "# ADMINS + Email (aviso de erro 500 em produção)"

BLOCK_LOG_DIR = """# Diretório de logs (criado no boot — não some ao recriar o container)
LOG_DIR = Path(env('DJANGO_LOG_DIR', default=str(BASE_DIR / 'logs')))
LOG_DIR.mkdir(parents=True, exist_ok=True)
"""

BLOCK_MAIN = """
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
            'class': 'django.utils.log.AdminEmailHandler',
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
"""


def patch(path: str) -> bool:
    if not os.path.exists(path):
        print(f"ERRO: {path} não existe")
        return False
    src = open(path, encoding='utf-8').read()
    if MARK in src:
        print(f"OK (idempotente): já aplicado em {path} — nada a fazer.")
        return True
    # backup com timestamp
    bak = path + '.bak_telegram_' + time.strftime('%Y%m%d_%H%M%S')
    open(bak, 'w', encoding='utf-8').write(src)
    # 1) LOG_DIR após BASE_DIR
    anchor_base = "BASE_DIR = Path(__file__).resolve().parent.parent\n"
    if "LOG_DIR = Path(env('DJANGO_LOG_DIR'" not in src and anchor_base in src:
        src = src.replace(anchor_base, anchor_base + "\n" + BLOCK_LOG_DIR, 1)
    # 2) Bloco ADMINS/EMAIL/LOGGING antes de INSTALLED_APPS
    anchor_ia = "INSTALLED_APPS = [\n"
    if anchor_ia in src:
        src = src.replace(anchor_ia, BLOCK_MAIN + "\n" + anchor_ia, 1)
    else:
        print("ERRO: âncora INSTALLED_APPS não encontrada — abortando (backup salvo)")
        return False
    open(path, 'w', encoding='utf-8').write(src)
    print(f"OK: patch aplicado em {path}")
    print(f"   backup: {bak}")
    return True


if __name__ == '__main__':
    patch(SETTINGS)
