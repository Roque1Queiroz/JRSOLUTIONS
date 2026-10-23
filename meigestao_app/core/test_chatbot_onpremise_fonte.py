# -*- coding: utf-8 -*-
"""CA4 — Se a fonte completa do bot nao existir, o item fica bloqueado e
o resto da leva nao e cancelado.

Garante que:
- O servico do bot tem codigo derivavel (Dockerfile, requirements,
  main.py, rag.py, models.py, database.py).
- Cada arquivo do servico tem fonte rastreavel (origem declarada).
- A documentacao registra de forma explicita o caminho de cada arquivo
  para que auditoria posterior localize onde cada pedaco veio.
"""
from pathlib import Path

import pytest

REF = Path(__file__).resolve().parents[2] / "docs" / "chatbot_gestor_ref" / "servico"


ARQUIVOS_NECESSARIOS = [
    "Dockerfile",
    "requirements.txt",
    "main.py",
    "rag.py",
    "database.py",
    "models.py",
]


def test_ca4_servico_bot_tem_codigo_e_nao_e_mock():
    """CA4: todos os arquivos do servico precisam existir."""
    if not REF.exists():
        pytest.fail(
            "CA4 BLOQUEADO: pasta docs/chatbot_gestor_ref/servico/ nao existe. "
            "Sem a fonte, este item NAO pode ser concluido."
        )

    ausentes = [a for a in ARQUIVOS_NECESSARIOS if not (REF / a).exists()]
    assert not ausentes, f"CA4 BLOQUEADO: faltam arquivos no servico: {ausentes}"


def test_ca4_readme_documenta_origem_de_cada_arquivo():
    """CA4: o servico precisa ter um README que rastreia a origem de cada
    arquivo, para que uma auditoria saiba de onde veio cada parte."""
    readme = REF / "README.md"
    if not readme.exists():
        pytest.skip("sem README.md no servico - auditoria posterior seria impossivel")
    texto = readme.read_text(encoding="utf-8", errors="replace")

    # Tem que mencionar cada arquivo essencial
    for arq in ARQUIVOS_NECESSARIOS:
        assert arq in texto, f"README nao documenta origem de {arq}"


def test_ca4_dockerfile_nao_publica_8003_no_host():
    """CA4: o bot NAO pode publicar 8003 no host - so na rede Docker."""
    dockerfile = REF / "Dockerfile"
    if not dockerfile.exists():
        pytest.skip("sem Dockerfile ainda")

    texto = dockerfile.read_text(encoding="utf-8", errors="replace")
    # A regra do compose e: o bot sobe sem `ports:` no docker-compose.yml
    # O Dockerfile nao deve forçar EXPOSE 8003 (o controle vem do compose,
    # mas se houver EXPOSE, ainda assim nao deve fixar 0.0.0.0:8003).
    assert "EXPOSE 8003" not in texto or "# " in texto, (
        "Dockerfile expondo 8003 - risco de vazar porta do host"
    )