# -*- coding: utf-8 -*-
"""CA6 — O serviço do bot é importável no layout do container.

Contexto (spec docs/SPECS/pacote-on-premise-v25.md, defeito D6):

O `Dockerfile` do chatbot faz `COPY main.py rag.py database.py models.py /app/`
(tudo achatado em `/app`) e roda `uvicorn main:app`. Mas o `main.py` faz
`from .database import ...` — import relativo. Import relativo em módulo
solto (sem `__init__.py` em volta) **não funciona**:

    ImportError: attempted relative import with no known parent package

O bot nunca sobe na instalação on-premise.

A correção mais simples (e menos invasiva) é trocar os imports relativos
em `main.py` por absolutos (`from database import ...`). Verificamos isso
via AST, sem precisar rodar o Python — não dependemos de fastapi/etc no
venv de teste.
"""
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
CHATBOT = RAIZ / "deploy-cliente" / "chatbot"


@pytest.mark.parametrize("modulo", ["main.py", "rag.py", "models.py", "database.py"])
def test_ca6_sem_import_relativo(modulo):
    """CA6: nenhum arquivo do bot pode ter `from .xxx` (import relativo).

    Os módulos do bot vão achatados em `/app` dentro do container (sem
    `__init__.py` no diretório). Import relativo só funciona quando o
    módulo faz parte de um package — não quando é um .py solto.
    """
    path = CHATBOT / modulo
    if not path.exists():
        pytest.skip(f"{modulo} ausente em {CHATBOT}")
    texto = path.read_text(encoding="utf-8", errors="replace")

    relativos = []
    for lin in texto.splitlines():
        l = lin.strip()
        if not l or l.startswith("#"):
            continue
        if l.startswith("from ."):
            relativos.append(l)

    assert not relativos, (
        f"{modulo} usa import relativo — quebra no layout do container "
        "(arquivos achatados em /app, sem __init__.py):\n  "
        + "\n  ".join(relativos)
        + "\nTroque para imports absolutos (ex.: `from database import ...`)."
    )
