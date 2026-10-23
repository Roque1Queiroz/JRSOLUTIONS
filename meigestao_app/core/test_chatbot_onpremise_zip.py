# -*- coding: utf-8 -*-
"""CA3 — Empacotador on-premise nao coloca .env real no zip do cliente.

A cobertura completa esta em `deploy-cliente/test_pacote.py`. Aqui ficam
testes adicionais focados no bot:
- O empacotador exclui o .env real.
- O .env.example presente no zip documenta GROQ_API_KEY e
  CHATBOT_INTERNAL_URL para o cliente preencher.
- Nenhuma chave real (gsk_) vaza no .env.example.
"""
import os
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
EMPACOTADOR = RAIZ / "deploy-cliente" / "scripts" / "empacotar.sh"


def test_ca3_empacotador_exclui_env_real():
    """CA3: o empacotador precisa filtrar o .env real."""
    texto = EMPACOTADOR.read_text(encoding="utf-8", errors="replace")
    # Alguma forma de exclusao (linha `^.env$` no excludes.txt ou --exclude)
    assert ".env" in texto, "empacotador nao trata .env"
    # Garante que a exclusao e para .env real e nao so .env.example
    linhas = texto.splitlines()
    exclui_env = any(
        l.strip() in (".env", "/.env") or l.strip() == "**/.env"
        for l in linhas
    )
    assert exclui_env, "empacotador precisa excluir .env real, nao so .env.example"


@pytest.mark.skipif(not (RAIZ / "deploy-cliente" / "dist").exists(), reason="sem dist/ gerada")
def test_ca3_zip_gerado_nao_contem_env_real():
    """CA3: confere o zip mais recente, se existir."""
    dist = RAIZ / "deploy-cliente" / "dist"
    zips = sorted(dist.glob("*.zip"))
    if not zips:
        pytest.skip("nenhum zip em deploy-cliente/dist")

    zip_path = zips[-1]
    with zipfile.ZipFile(zip_path) as z:
        nomes = z.namelist()

    offenders = [
        n for n in nomes
        if os.path.basename(n) == ".env"
    ]
    assert not offenders, f"Credencial real dentro do pacote: {offenders}"


@pytest.mark.parametrize("onde", [RAIZ, RAIZ / "deploy-cliente"])
def test_ca3_env_example_documenta_chaves(onde):
    """O .env.example presente no pacote precisa de GROQ_API_KEY e
    CHATBOT_INTERNAL_URL, sem chave real."""
    exemplo = onde / ".env.example"
    if not exemplo.exists():
        pytest.skip(f"sem .env.example em {onde}")

    texto = exemplo.read_text(encoding="utf-8", errors="replace")
    assert "GROQ_API_KEY" in texto, f"{exemplo} precisa de GROQ_API_KEY para o bot"
    assert "CHATBOT_INTERNAL_URL" in texto, f"{exemplo} precisa de CHATBOT_INTERNAL_URL"
    assert "gsk_" not in texto, f"{exemplo} nao pode conter chave Groq real"