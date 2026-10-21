from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from typing import Optional, Dict, Any

from database import init_db, get_db
from models import ChatSession, ChatMessage
from rag import process_and_index_document, get_chat_chain, formatar_empresa_dados


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco de dados ao subir o servidor."""
    init_db()
    yield

app = FastAPI(title="Chatbot Gestor API", lifespan=lifespan)

# ── CORS — permite que o Sistema Gestor acesse esta API ────────────
# Em produção, troque "*" pelo domínio real do seu sistema
# Ex.: allow_origins=["https://meusite.com"]
import os
ALLOWED_ORIGIN = os.getenv("CHATBOT_ALLOWED_ORIGIN", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    # Dados agregados e SEGUROS da empresa autenticada, enviados pelo Sistema
    # Gestor. São apenas leitura e filtrados por empresa; o bot usa como
    # contexto opcional além do manual. Nunca são usados para autenticar.
    empresa_dados: Optional[Dict[str, Any]] = None


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Faz upload do manual (PDF ou MD) e indexa no ChromaDB.
    Só precisa ser feito uma vez, ou quando o manual for atualizado.
    """
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.md')):
        raise HTTPException(status_code=400, detail="Somente arquivos PDF ou MD são aceitos.")

    content = await file.read()
    process_and_index_document(content, file.filename)
    return {"message": f"Arquivo '{file.filename}' indexado com sucesso!"}


@app.post("/chat")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """Recebe a mensagem do usuário e retorna a resposta da IA."""

    # Busca ou cria a sessão
    session = db.query(ChatSession).filter(ChatSession.session_id == req.session_id).first()
    if not session:
        session = ChatSession(session_id=req.session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Carrega o histórico para o Langchain
    db_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    chat_history = []
    for msg in db_messages:
        if msg.role == 'user':
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == 'assistant':
            chat_history.append(AIMessage(content=msg.content))

    # Obtém a chain RAG
    chain = get_chat_chain()
    if not chain:
        raise HTTPException(
            status_code=503,
            detail="Manual ainda não indexado. Faça o upload do PDF primeiro via POST /upload."
        )

    # Gera a resposta, incluindo dados da empresa como contexto extra.
    # `dados_empresa` deve casar com a variável {dados_empresa} do prompt do rag.
    dados_empresa = formatar_empresa_dados(req.empresa_dados)
    response = chain.invoke({
        "input": req.message,
        "chat_history": chat_history,
        "dados_empresa": dados_empresa,
    })
    answer = response["answer"]

    # Salva no banco
    db.add(ChatMessage(session_id=session.id, role='user', content=req.message))
    db.add(ChatMessage(session_id=session.id, role='assistant', content=answer))
    db.commit()

    return {"answer": answer}


@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Retorna o histórico de mensagens de uma sessão."""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        return {"messages": []}

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return {
        "messages": [
            {"role": m.role, "content": m.content, "time": str(m.created_at)}
            for m in messages
        ]
    }


@app.get("/health")
def health_check():
    """Endpoint para verificar se o servidor está rodando."""
    return {"status": "ok"}
