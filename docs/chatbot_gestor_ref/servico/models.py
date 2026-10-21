# -*- coding: utf-8 -*-
# models.py — RECONSTRUÍDO a partir de dump de sessão
#
# ATENÇÃO: este arquivo NÃO é a fonte original.
# Ver cabeçalho de database.py para o contexto completo.
#
# Esquema compatível com o chat_history.db original:
#   chat_sessions(id, session_id, created_at)
#   chat_messages(id, session_id FK, role, content, created_at)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func

from database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)   # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
