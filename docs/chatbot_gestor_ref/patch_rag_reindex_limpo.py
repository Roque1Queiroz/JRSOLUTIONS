# -*- coding: utf-8 -*-
"""
Patch mínimo e idempotente no rag.py da VM do chatbot_gestor:
faz a re-indexação LIMPAR a coleção ChromaDB antes de adicionar chunks novos.

Problema corrigido: Chroma.from_documents só ADICIONA chunks quando a pasta de
persistência já existe, então re-indexar várias vezes acumulava chunks antigos
(com texto desatualizado) no índice. Isso fazia o bot responder info errada
(ex.: "chat de IA só em Profissional/Enterprise") mesmo depois de o manual no
disco estar atualizado ("chat de IA em TODOS os planos").

Rodar na VM:
    cp /home/ubuntu/chatbot_gestor/rag.py /home/ubuntu/chatbot_gestor/rag.py.bak_reindex
    python3 patch_rag_reindex_limpo.py
    sudo systemctl restart chatbot-gestor
"""
import re

p = "/home/ubuntu/chatbot_gestor/rag.py"
s = open(p, encoding="utf-8").read()

marker = "vector_store = Chroma.from_documents("
assert marker in s and s.count(marker) == 1, "anchors nao unico"

# Injeta limpeza antes do Chroma.from_documents, imediatamente apos o split.
old_block = "    chunks = text_splitter.split_documents(documents=docs)\n\n    vector_store = Chroma.from_documents("
new_block = (
    "    chunks = text_splitter.split_documents(documents=docs)\n"
    "\n"
    "    # Limpa a colecao antes de re-indexar, evitando acumulo de chunks antigos.\n"
    "    # (Chroma.from_documents so ADICIONA quando a pasta ja existe; sem limpar,\n"
    "    #  re-indexar varias vezes acumulava texto desatualizado e o bot respondia errado.)\n"
    "    try:\n"
    "        _store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=get_embeddings())\n"
    "        _ids = _store._collection.get()[\"ids\"]\n"
    "        if _ids:\n"
    "            _store._collection.delete(ids=_ids)\n"
    "            print(f\"removidos {len(_ids)} chunks antigos antes de re-indexar\")\n"
    "    except Exception as _exc:\n"
    "        print(\"colecao vazia/nao existia; seguindo para indexar\", _exc)\n"
    "\n"
    "    vector_store = Chroma.from_documents("
)
assert old_block in s, "bloco de ancoragem nao encontrado"
s = s.replace(old_block, new_block, 1)

open(p, "w", encoding="utf-8").write(s)
import ast
ast.parse(s)
print("OK: rag.py atualizado — re-indexa com limpeza (idempotente)")
