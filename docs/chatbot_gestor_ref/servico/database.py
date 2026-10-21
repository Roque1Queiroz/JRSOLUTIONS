# -*- coding: utf-8 -*-
# database.py — RECONSTRUÍDO a partir de dump de sessão
#
# ATENÇÃO: este arquivo NÃO é a fonte original.
# A fonte original estava em /home/ubuntu/chatbot_gestor/database.py na VM.
# Após a faxina da VM em 2026-09-28, esse caminho sumiu.
# Este arquivo foi RECONSTRUÍDO por Hermes a partir do dump de sessão
# request_dump_20260811_..._20261010_...json (tag: "recriado — original perdido
# na migração de 28/09"), mantendo o esquema SQLite + SQLAlchemy original.
#
# Se você tiver acesso à fonte original em backup, SOBRESCREVA este arquivo.
#
# Esquema compatível com o chat_history.db original:
# - SQLite local em chat_history.db
# - SQLAlchemy 1.x (clássica) com declarative_base
# - Função init_db() idempotente
# - Função get_db() como dependency do FastAPI

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Cria as tabelas na inicialização (idempotente)."""
    # importa aqui para garantir que os models sejam registrados no Base
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency do FastAPI: abre sessão e garante fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
