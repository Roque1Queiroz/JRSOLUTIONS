#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backup automatizado e consistente do banco SQLite do Sistema Gestor.

Por que em Python e não `gzip -c db.sqlite3`:
  - `cp`/`gzip` direto do arquivo enquanto o Django grava pode capturar o banco
    num estado inconsistente (backup corrompido que não abre / perde dados).
  - Usamos a API de backup ONLINE do SQLite (`Connection.backup`), que produz um
    snapshot consistente mesmo com o app escrevendo ao mesmo tempo.
Verifica integridade (PRAGMA integrity_check), compacta, mantém N dias de
retenção e o backup mais recente; devolve o caminho do arquivo criado.

Agendamento sugerido (root, diario as 03:00):
  0 3 * * * /usr/bin/python3 <projeto>/scripts/backup_gestor.py >> /var/log/backup_gestor.log 2>&1
"""
import datetime
import glob
import gzip
import os
import shutil
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

PROJETO = "/home/ubuntu/Sistema_Gestor"
DATABASE = os.environ.get("BACKUP_DB", os.path.join(PROJETO, "db.sqlite3"))
BACKUP_DIR = os.environ.get("BACKUP_DIR", "/home/ubuntu/backups/gestor")
RETAIN_DAYS = int(os.environ.get("BACKUP_RETAIN_DAYS", "30"))
ENV_FILE = os.path.join(PROJETO, ".env")


def _env(var, default=""):
    val = os.environ.get(var)
    if val:
        return val
    # fallback: lê do .env do projeto sem expandir $ (evita mangle)
    try:
        for line in open(ENV_FILE, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith(var + "="):
                return line.split("=", 1)[1].strip().strip("'\"")
    except Exception:
        pass
    return default


def _notify_telegram(text: str) -> None:
    """Aviso opcional no Telegram (guardado: só se houver token/chat)."""
    token = _env("TELEGRAM_BOT_TOKEN")
    chat = _env("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": chat,
            "text": text[:3000],
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        with urllib.request.urlopen(urllib.request.Request(url, data=payload), timeout=15):
            pass
    except Exception as e:  # nunca derruba o backup por falha de notificação
        print(f"  [!] aviso telegram falhou: {e}", flush=True)


def _integrity_ok(path: str) -> bool:
    try:
        con = sqlite3.connect(path)
        try:
            return con.execute("PRAGMA integrity_check;").fetchone()[0] == "ok"
        finally:
            con.close()
    except Exception:
        return False


def main() -> int:
    if not os.path.exists(DATABASE):
        msg = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] ERRO: banco {DATABASE} nao encontrado."
        print(msg, flush=True); _notify_telegram("🚨 *BACKUP FALHOU*: banco não encontrado.\n" + DATABASE)
        return 1

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp = os.path.join(BACKUP_DIR, f".gestor_tmp_{stamp}.sqlite3")
    out = os.path.join(BACKUP_DIR, f"gestor_{stamp}.sqlite3.gz")
    latest = os.path.join(BACKUP_DIR, "gestor_ultimo.sqlite3.gz")

    try:
        # 1) snapshot online consistente
        src = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
        dst = sqlite3.connect(tmp)
        try:
            with dst:
                src.backup(dst)
        finally:
            dst.close(); src.close()

        # 2) valida integridade do snapshot
        if not _integrity_ok(tmp):
            raise RuntimeError("PRAGMA integrity_check reprovado no snapshot")
        size_raw = os.path.getsize(tmp)

        # 3) compacta
        with open(tmp, "rb") as f_in, gzip.GzipFile(out, "wb", compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out, 1024 * 1024)
        os.remove(tmp)
        size_gz = os.path.getsize(out)

        # 4) 'gestor_ultimo' sempre no mais novo (cópia simples)
        shutil.copyfile(out, latest)

        # 5) retenção (apaga antigos)
        cutoff = time.time() - RETAIN_DAYS * 86400
        removed = 0
        for f in glob.glob(os.path.join(BACKUP_DIR, "gestor_[0-9]*.sqlite3.gz")):
            if os.path.getmtime(f) < cutoff:
                os.remove(f); removed += 1

        line = (f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] OK backup: {os.path.basename(out)} "
                f"({size_raw/1024:.0f} KB -> {size_gz/1024:.0f} KB gz), integridade ok, "
                f"{removed} antigo(s) removido(s).")
        print(line, flush=True)
        _notify_telegram(f"✅ *Backup diário concluído* — Sistema Gestor\n"
                         f"📦 {os.path.basename(out)}\n"
                         f"💾 {size_gz/1024:.0f} KB · integridade ok · retenção {RETAIN_DAYS}d")
        return 0

    except Exception as e:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass
        msg = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] ERRO: {e}"
        print(msg, flush=True)
        _notify_telegram(f"🚨 *BACKUP FALHOU* — Sistema Gestor\n{msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
