import os
import tempfile
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pegando a chave do Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if GROQ_API_KEY:
    os.environ['GROQ_API_KEY'] = GROQ_API_KEY

PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'db')


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


from langchain_community.document_loaders import PyPDFLoader, TextLoader


def process_and_index_document(file_content, filename="temp.pdf"):
    """
    Processa o documento (PDF ou MD em bytes) e adiciona ao banco vetorial.
    """
    ext = os.path.splitext(filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    if ext == '.pdf':
        loader = PyPDFLoader(temp_file_path)
    else:
        loader = TextLoader(temp_file_path, encoding='utf-8')

    docs = loader.load()
    os.remove(temp_file_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
    )
    chunks = text_splitter.split_documents(documents=docs)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=PERSIST_DIRECTORY,
    )
    return vector_store


def get_vector_store():
    if os.path.exists(PERSIST_DIRECTORY):
        return Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=get_embeddings(),
        )
    return None


def formatar_empresa_dados(dados):
    """
    Converte o objeto empresa_dados (enviado pelo Sistema Gestor) em um texto
    curto e instruído, usado como contexto extra pelo assistente.
    Não autentica nem persiste: é apenas contexto read-only.
    """
    if not dados:
        return ""
    try:
        nome = dados.get("empresa", "")
        fat_mes = dados.get("faturamento_mes")
        fat_hoje = dados.get("faturamento_hoje")
        n_vendas = dados.get("total_vendas_mes")
        pend = dados.get("vendas_pendentes")
        return (
            "Dados atuais da empresa do usuário (só desta empresa, agregados e "
            "confiáveis):\n"
            f"- Empresa: {nome or 'não informada'}\n"
            f"- Faturamento do mês (vendas confirmadas): R$ {fat_mes:,.2f}".replace(",", ".")
        )
    except Exception:
        return str(dados)


def get_chat_chain(model_name='openai/gpt-oss-120b'):
    """
    Usa o LLaMA 3 hospedado na Groq como cérebro LLM.
    """
    vector_store = get_vector_store()
    if not vector_store:
        return None

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    llm = ChatGroq(model=model_name, temperature=0)

    # 1. Prompt para reformular a pergunta com base no histórico
    contextualize_q_system_prompt = (
        "Dada uma conversa e a última pergunta do usuário "
        "que pode fazer referência ao contexto anterior, "
        "formule uma pergunta autônoma que possa ser compreendida "
        "sem o histórico de chat. Não responda à pergunta, "
        "apenas reformule-a se necessário; caso contrário, retorne como está."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # 2. Prompt para o QA (Responder com base em manual + dados da empresa)
    system_prompt = (
        "Você é um assistente útil para tirar dúvidas do Sistema Gestor. "
        "Use os seguintes trechos de contexto recuperados para responder à pergunta. "
        "Se você não sabe a resposta, diga que não sabe. Responda sempre em Português do Brasil. "
        "Ao responder, SEMPRE corrija os erros de digitação e ortografia do usuário e use a grafia "
        "correta das palavras (o usuário pode digitar errado, ex.: \"cadastru\", \"clinete\"); nunca "
        "repita a palavra digitada errada. Atenda apenas dúvidas sobre o Sistema Gestor (acesso, "
        "dashboard, clientes, vendas, estoque, financeiro, fiscal, almoxarifado, produção, ordens de "
        "serviço, compras, relatórios e planos).\n\n"
        "Quando o usuário perguntar sobre dados/faturamento/vendas da empresa dele, use os "
        "\"Dados atuais da empresa\" abaixo como fonte confiável — mas apenas os fornecidos; "
        "nunca invente valores e nunca fale de outras empresas.\n\n"
        "{dados_empresa}\n\n"
        "Contexto:\n{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    # `dados_empresa` é uma variável de entrada opcional, formatada a partir de
    # empresa_dados; se ausente, entra como string vazia (nada quebra).
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain,
    )
    return rag_chain
