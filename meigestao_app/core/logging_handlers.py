"""Handler de log que envia avisos de erro críticos direto para o Telegram.

Padrão de mercado p/ "achar erro fácil": quando o sistema quebra (erro 500 ou
exception não tratada), além de gravar em arquivo, o Django dispara este handler
e você recebe o aviso na hora no Telegram — sem depender de SMPT configurado.

Ativação (env):
    TELEGRAM_BOT_TOKEN = token do bot que vai enviar (BotFather)
    TELEGRAM_CHAT_ID   = seu chat id no Telegram (ex.: @userinfobot informa)
    TELEGRAM_ALERT_MIN_INTERVAL = segundos mínimos entre avisos (padrão 30)

Se TELEGRAM_BOT_TOKEN/CHAT_ID não estiverem setados, o handler desliga sozinho
(sem erro) — útil no pacote on-premise, onde o cliente não responde ao seu bot.
Nunca deixa uma falha de rede/TG derrubar o app (try/except em tudo).
"""
import json
import logging
import os
import time
import traceback
import urllib.parse
import urllib.request

# Fallback de chat_id por empresa na mesma requisição (opcional). Boa evolução
# futura: rotear por tenant. Por ora envia para um único chat do dono.
_DEFAULT_CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


class TelegramBotHandler(logging.Handler):
    """Logger que envia a mensagem formatada via Bot API (sendMessage)."""

    def __init__(self, level=logging.ERROR):
        super().__init__(level)
        self.token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
        self.chat_id = (os.environ.get(_DEFAULT_CHAT_ID_ENV) or "").strip()
        try:
            self._min_interval = float(
                os.environ.get("TELEGRAM_ALERT_MIN_INTERVAL") or 30
            )
        except ValueError:
            self._min_interval = 30.0
        self._last_sent = 0.0
        self._enabled = bool(self.token and self.chat_id)
        if not self._enabled:
            logging.getLogger(__name__).warning(
                "TelegramBotHandler desativado: defina TELEGRAM_BOT_TOKEN e "
                "TELEGRAM_CHAT_ID para receber avisos de erro no Telegram."
            )

    # ------------------------------------------------------------------ #
    def emit(self, record: logging.LogRecord) -> None:
        if not self._enabled:
            return
        now = time.time()
        # Anti-enxurrada: no máx. 1 aviso a cada N segundos (limite do Bot API
        # e evita spam se o sistema quebrar em loop).
        if now - self._last_sent < self._min_interval:
            return
        try:
            text = self._format(record)
            self._send(text)
            self._last_sent = now
        except Exception:
            # Nunca deixa o handler quebrar o pedido que está sendo tratado.
            self.handleError(record)

    # ------------------------------------------------------------------ #
    def _format(self, record: logging.LogRecord) -> str:
        ts = self.formatter.formatTime(record, "%d/%m %H:%M:%S") if self.formatter \
            else time.strftime("%d/%m %H:%M:%S")
        chatter = "🚨" if record.levelno >= logging.ERROR else "⚠️"
        lines = [
            f"{chatter} [Sistema Gestor] {record.levelname} em {record.name}",
            f"🕐 {ts}",
        ]
        # caminho/rota requisitada (se o record tiver request)
        req = getattr(record, "request", None)
        if getattr(req, "path", None):
            lines.append(f"📍 {req.method} {req.path}")
            if getattr(req, "user", None) and req.user.is_authenticated:
                lines.append(f"👤 {req.user.username}")
        # traceback / área do erro (últimas linhas, as mais úteis)
        if record.exc_info and record.exc_info[2]:
            tb = "".join(traceback.format_exception(*record.exc_info))
            lines.append("─── stack ───")
            lines.extend(tb.strip().splitlines()[-14:])
        else:
            lines.append(record.getMessage())
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    def _send(self, text: str) -> None:
        if not self._enabled:
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": self.chat_id,
            "text": text[:4000],
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
