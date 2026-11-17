"""Testes p/ o empacotador on-premise do Sistema Gestor.

Roda o scripts/empacotar.sh num pacote descartável (versão 'testv') e
valida que o .zip gerado tem a estrutura esperada e NÃO vaza segredos.
Execução:  /opt/data/.venvs/prod-audit-red/bin/pytest test_pacote.py  (deste dir)
"""
import pathlib
import subprocess
import zipfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
VER = "testv"
ZIP = DIST / f"sistema-gestor-cliente-{VER}.zip"
ROOT_IN_ZIP = f"sistema-gestor-cliente-{VER}"

MUST_HAVE = {
    "compose na raiz": f"{ROOT_IN_ZIP}/docker-compose.yml",
    "env-modelo na raiz": f"{ROOT_IN_ZIP}/.env.example",
    "README": f"{ROOT_IN_ZIP}/README_INSTALACAO.md",
    "guia do cliente": f"{ROOT_IN_ZIP}/GUIA_INSTALACAO_CLIENTE.md",
    "instalar.sh": f"{ROOT_IN_ZIP}/scripts/instalar.sh",
    "patch_seguranca.sh": f"{ROOT_IN_ZIP}/scripts/patch_seguranca.sh",
    "app/manage.py": f"{ROOT_IN_ZIP}/app/manage.py",
    "app/Dockerfile": f"{ROOT_IN_ZIP}/app/Dockerfile",
    "app/config/settings.py": f"{ROOT_IN_ZIP}/app/config/settings.py",
    # ── v1.2: trial (30 dias) + pagamento (Asaas) + cadastro self-service ──
    "migracao trial (30d)": f"{ROOT_IN_ZIP}/app/meigestao_app/core/migrations/0006_empresa_trial_expira_em.py",
    "migracao asaas": f"{ROOT_IN_ZIP}/app/meigestao_app/core/migrations/0007_empresa_asaas_customer_id_and_more.py",
    "modulo asaas": f"{ROOT_IN_ZIP}/app/meigestao_app/core/asaas.py",
    "testes de trial": f"{ROOT_IN_ZIP}/app/meigestao_app/core/test_trial.py",
    "view de cadastro": f"{ROOT_IN_ZIP}/app/meigestao_app/core/views.py",
    "template de cadastro": f"{ROOT_IN_ZIP}/app/templates/meigestao_app/core/cadastro.html",
    # ── v1.2 (re-empacotado): login público + logging blindado ──
    "login publico": f"{ROOT_IN_ZIP}/app/templates/meigestao_app/core/login.html",
    "view login (core/views.py tem login_view)": f"{ROOT_IN_ZIP}/app/meigestao_app/core/views.py",
    "rota login (core/urls.py)": f"{ROOT_IN_ZIP}/app/meigestao_app/core/urls.py",
    "handler de logging+telegram": f"{ROOT_IN_ZIP}/app/meigestao_app/core/logging_handlers.py",
    # ── v2.2: páginas legais LGPD (privacidade + termos) ──
    "politica de privacidade": f"{ROOT_IN_ZIP}/app/templates/meigestao_app/core/privacidade.html",
    "termos de uso": f"{ROOT_IN_ZIP}/app/templates/meigestao_app/core/termos.html",
    "base legal": f"{ROOT_IN_ZIP}/app/templates/meigestao_app/core/legal_base.html",
    "view privacidade/termos": f"{ROOT_IN_ZIP}/app/meigestao_app/core/views.py",
    # ── v2.3: modelo CSV de importacao + validacao CPF/CNPJ + demo ──
    "modelos CSV (clientes/estoque)": f"{ROOT_IN_ZIP}/app/meigestao_app/core/utils/csv_modelos.py",
    "importador CSV": f"{ROOT_IN_ZIP}/app/meigestao_app/core/utils/csv_importer.py",
    "rota modelo_csv clientes": f"{ROOT_IN_ZIP}/app/meigestao_app/clientes/urls.py",
    "testes import CSV clientes": f"{ROOT_IN_ZIP}/app/meigestao_app/clientes/test_import_csv.py",
    "testes import CSV estoque": f"{ROOT_IN_ZIP}/app/meigestao_app/estoque/test_import_csv.py",
    "painel demo (landing iframe)": f"{ROOT_IN_ZIP}/app/meigestao_app/core/demo_views.py",
}

MUST_NOT_HAVE = {
    "empacotar.sh não vai ao cliente": f"{ROOT_IN_ZIP}/scripts/empacotar.sh",
    "compose interno em app/": f"{ROOT_IN_ZIP}/app/docker-compose.yml",
    "banco dev db.sqlite3": f"{ROOT_IN_ZIP}/app/db.sqlite3",
    "docs internas": f"{ROOT_IN_ZIP}/app/docs",
    ".git do projeto": f"{ROOT_IN_ZIP}/.git",
    ".git interno em app/": f"{ROOT_IN_ZIP}/app/.git",
}

# ── v2.5: o pacote precisa instalar DE VERDADE numa máquina limpa ──────
# Contexto: o v2.4.1 nunca subiu do zero (loop de restart com exit 127).
# Estes testes travam as correções dos defeitos D1..D8 da spec
# docs/SPECS/pacote-on-premise-v25.md

# CA1 — o entrypoint precisa rodar mesmo sem bit de execução (bind mount)
CA1_ENTRYPOINT_OK = 'ENTRYPOINT ["bash", "/app/scripts/entrypoint.sh"]'

# CA4 — só o web migra
CA4_GATE = "RUN_MIGRATIONS"

# CA5 — cliente sem chave Groq ainda sobe o sistema
CA5_GROQ_VAR = "GROQ_API_KEY"


@pytest.fixture(scope="module")
def zip_build():
    """Empacota a versão de teste e devolve (nomes, {caminho: bytes}).

    Um único fixture para todos os testes: o zip é gerado UMA vez e fica
    em disco durante a sessão do módulo (o `finally` do fixture antigo
    apagava o arquivo antes dos testes v2.5 conseguirem lê-lo).
    """
    if ZIP.exists():
        ZIP.unlink()
    subprocess.run(
        ["bash", "scripts/empacotar.sh", VER], cwd=ROOT, check=True, capture_output=True
    )
    assert ZIP.exists(), "empacotar.sh não produziu o .zip"
    with zipfile.ZipFile(ZIP) as z:
        nomes = z.namelist()
        conteudo = {n: z.read(n) for n in nomes}
        modos = {n: (z.getinfo(n).external_attr >> 16) & 0xFFFF for n in nomes}
    yield nomes, conteudo, modos
    ZIP.unlink(missing_ok=True)  # remove só o pacote de teste, preserva os reais


@pytest.fixture(scope="module")
def zip_names(zip_build) -> list:
    return zip_build[0]


def test_zip_tem_estrutura_obrigatoria(zip_names):
    for rotulo, entry in MUST_HAVE.items():
        assert entry in zip_names, f"faltou no pacote: {rotulo} ({entry})"


def test_zip_nao_vaza_segredos(zip_names):
    for rotulo, entry in MUST_NOT_HAVE.items():
        assert entry not in zip_names, f"vazou no pacote: {rotulo} ({entry})"


def test_nao_ha_zenv_real(zip_names):
    env_nao_exemplo = [n for n in zip_names if n.endswith("/.env")]
    assert env_nao_exemplo == [], f"encontrado .env real: {env_nao_exemplo}"


# ══════════════════════════════════════════════════════════════════════
#  v2.5 — o pacote precisa INSTALAR DE VERDADE (spec pacote-on-premise-v25)
# ══════════════════════════════════════════════════════════════════════


def test_ca1_zip_entrypoint_roda_sem_bit_exec(zip_build):
    """CA1: o entrypoint do app precisa ser chamado via `bash`.

    O zip não guarda o bit de execução e o compose monta `./app:/app`
    por bind mount — um ENTRYPOINT direto em `/app/scripts/entrypoint.sh`
    morre com "permission denied" / "No such file or directory".
    """
    nomes, conteudo, modos = zip_build
    dockerfile = f"{ROOT_IN_ZIP}/app/Dockerfile"
    assert dockerfile in nomes, "app/Dockerfile ausente no pacote"

    texto = conteudo[dockerfile].decode("utf-8", errors="replace")
    linhas_entrypoint = [
        l.strip() for l in texto.splitlines() if l.strip().startswith("ENTRYPOINT")
    ]
    assert linhas_entrypoint, "Dockerfile do app não tem ENTRYPOINT"
    assert CA1_ENTRYPOINT_OK in linhas_entrypoint, (
        "Dockerfile do app precisa de "
        f'{CA1_ENTRYPOINT_OK!r} (achou: {linhas_entrypoint}) — '
        "sem isso o container não sobe porque o zip perde o bit de execução"
    )


def test_ca1_zip_entrypoint_tem_modo_exec_ou_roda_via_bash(zip_build):
    """CA1 (complemento): o script do entrypoint precisa ser executável
    OU ser invocado por um interpretador (bash)."""
    nomes, conteudo, modos = zip_build
    ep = f"{ROOT_IN_ZIP}/app/scripts/entrypoint.sh"
    assert ep in nomes, "app/scripts/entrypoint.sh ausente no pacote"

    modo = modos[ep]
    tem_exec = bool(modo & 0o111)

    if not tem_exec:
        dockerfile = conteudo[f"{ROOT_IN_ZIP}/app/Dockerfile"].decode(
            "utf-8", errors="replace"
        )
        assert "bash" in dockerfile, (
            "entrypoint.sh no zip NÃO tem bit de execução e o Dockerfile "
            "não chama via bash — o container vai falhar no boot"
        )


def test_ca3_env_example_declara_db_type_postgres(zip_build):
    """CA3: o pacote provisiona Postgres, então o .env.example precisa
    pedir Postgres (sem isso o settings cai no default `sqlite` e o
    Postgres do compose fica ocioso)."""
    nomes, conteudo, modos = zip_build
    env_ex = f"{ROOT_IN_ZIP}/.env.example"
    assert env_ex in nomes, ".env.example ausente na raiz do pacote"

    texto = conteudo[env_ex].decode("utf-8", errors="replace")
    linhas = [
        l.strip() for l in texto.splitlines() if l.strip().startswith("DB_TYPE")
    ]
    assert linhas, (
        ".env.example do pacote NÃO declara DB_TYPE — o settings.py usa "
        "default `sqlite` e o app vai ignorar o Postgres do compose"
    )
    valores = [l.split("=", 1)[1].strip() for l in linhas]
    assert "postgres" in valores, (
        f"DB_TYPE do .env.example deveria ser postgres (achou: {valores})"
    )


def test_ca4_somente_web_roda_migrations(zip_build):
    """CA4: só o serviço `web` pode aplicar migrations.

    web/worker/beat sobem pelo mesmo entrypoint; se os três migrarem
    ao mesmo tempo, corre-se no lock do banco.
    """
    nomes, conteudo, modos = zip_build

    ep = f"{ROOT_IN_ZIP}/app/scripts/entrypoint.sh"
    assert ep in nomes, "app/scripts/entrypoint.sh ausente no pacote"
    entrypoint = conteudo[ep].decode("utf-8", errors="replace")
    assert CA4_GATE in entrypoint, (
        "scripts/entrypoint.sh precisa de um gate RUN_MIGRATIONS — "
        "sem ele, web/worker/beat aplicam migration em paralelo"
    )

    compose = conteudo[f"{ROOT_IN_ZIP}/docker-compose.yml"].decode(
        "utf-8", errors="replace"
    )
    assert CA4_GATE in compose, (
        "docker-compose.yml precisa definir RUN_MIGRATIONS por serviço"
    )

    # only_web: só o serviço web pode ter RUN_MIGRATIONS=true
    import re

    blocos = re.split(r"\n  (?=[a-z])", compose)
    com_true = []
    for bloco in blocos:
        nome = bloco.strip().split(":")[0].strip()
        if re.search(r"RUN_MIGRATIONS\s*[:=]\s*[\"']?true", bloco, re.I):
            com_true.append(nome)
    assert com_true == ["web"], (
        f"somente `web` pode ter RUN_MIGRATIONS=true (achou: {com_true})"
    )


def test_ca5_chatbot_nao_derruba_o_compose_sem_groq(zip_build):
    """CA5: `${GROQ_API_KEY:?...}` aborta o `docker compose up` inteiro
    quando a chave está vazia. O cliente sem Groq precisa subir o ERP.

    Apenas o GROQ_API_KEY não pode usar `:?` (chave opcional — sem ela o
    chat responde 503, mas o ERP sobe normalmente). DB_PASSWORD pode
    ficar com `:?` porque sem ele o Postgres do compose nem inicializa.
    """
    nomes, conteudo, modos = zip_build
    compose = conteudo[f"{ROOT_IN_ZIP}/docker-compose.yml"].decode(
        "utf-8", errors="replace")

    # Procura linhas com GROQ_API_KEY e exige `:-` (nunca `:?`).
    for linha in compose.splitlines():
        if "GROQ_API_KEY" not in linha:
            continue
        assert ":?" not in linha, (
            f"docker-compose.yml aborta o `up` se GROQ_API_KEY estiver "
            f"vazia (use `:-` para tornar opcional):\n  {linha.strip()}"
        )
    assert CA5_GROQ_VAR in compose, "compose precisa passar GROQ_API_KEY ao bot"


def test_ca5_chatbot_explica_groq_vazio_no_log(zip_build):
    """CA5 (complemento): o bot avisa que a chave falta, sem morrer."""
    nomes, conteudo, modos = zip_build
    ep = f"{ROOT_IN_ZIP}/chatbot/entrypoint.sh"
    assert ep in nomes, "chatbot/entrypoint.sh ausente no pacote"
    texto = conteudo[ep].decode("utf-8", errors="replace")
    assert CA5_GROQ_VAR in texto, (
        "chatbot/entrypoint.sh deve checar GROQ_API_KEY e avisar no log"
    )


def test_ca7_requirements_sem_pandas_plotly(zip_build):
    """CA7: pandas/plotly não são importados em lugar nenhum do projeto e
    já quebraram o build (Python 3.13). Ficam fora do requirements."""
    nomes, conteudo, modos = zip_build
    req = f"{ROOT_IN_ZIP}/app/requirements.txt"
    assert req in nomes, "app/requirements.txt ausente no pacote"

    texto = conteudo[req].decode("utf-8", errors="replace").lower()
    for pesado in ("pandas", "plotly"):
        assert pesado not in texto, (
            f"requirements.txt ainda traz {pesado} — dependência pesada e "
            "não usada, que já quebrou o build do pacote"
        )


def test_ca8_manual_embot_aparece_uma_vez(zip_build):
    """CA8: o manual do bot não pode vir duplicado (raiz + chatbot/)."""
    nomes, _, _ = zip_build
    manuais = [n for n in nomes if n.endswith("MANUAL_EMBED_BOT.md")]
    assert len(manuais) == 1, (
        f"MANUAL_EMBED_BOT.md deveria aparecer 1x, achou {len(manuais)}: {manuais}"
    )
    assert manuais[0] == f"{ROOT_IN_ZIP}/MANUAL_EMBED_BOT.md", (
        f"o manual deve ficar na raiz (é lá que o compose monta), achou: {manuais[0]}"
    )


# ══════════════════════════════════════════════════════════════════════
#  v2.7 — o bot precisa PERSISTIR no volume, não na camada do container
# ══════════════════════════════════════════════════════════════════════


def test_ca10_rag_persiste_indice_no_volume(zip_build):
    """CA10: o Chroma tem que ser gravado em /data/db (volume do compose).

    O compose monta o volume em /data/db e o entrypoint checa
    /data/db/chroma.sqlite3. Se o rag.py persistir em os.path.dirname(__file__)
    (= /app/db) o índice fica na camada do container: some a cada recriação e
    o manual é reindexado toda vez (o "Chroma já populado" nunca acontece).
    """
    nomes, conteudo, modos = zip_build
    rag = f"{ROOT_IN_ZIP}/chatbot/rag.py"
    assert rag in nomes, "chatbot/rag.py ausente no pacote"
    texto = conteudo[rag].decode("utf-8", errors="replace")
    assert "CHATBOT_DATA_DIR" in texto, (
        "chatbot/rag.py deve resolver PERSIST_DIRECTORY a partir de "
        "CHATBOT_DATA_DIR (volume /data/db), não da pasta do código (/app/db)"
    )


def test_ca10_database_persiste_historico_no_volume(zip_build):
    """CA10: o chat_history.db também precisa ficar no volume (/data/historico)."""
    nomes, conteudo, modos = zip_build
    db = f"{ROOT_IN_ZIP}/chatbot/database.py"
    assert db in nomes, "chatbot/database.py ausente no pacote"
    texto = conteudo[db].decode("utf-8", errors="replace")
    assert "CHATBOT_DATA_DIR" in texto, (
        "chatbot/database.py deve resolver o caminho do histórico a partir de "
        "CHATBOT_DATA_DIR (volume /data/historico), não de /app"
    )
    assert "historico" in texto, (
        "o histórico deve cair em /data/historico, que é o volume que o "
        "docker-compose monta (chatbot_history)"
    )


def test_ca10_entrypoint_nao_derruba_o_bot_se_indexacao_falhar(zip_build):
    """CA10: falha de indexação (ex.: sem internet p/ baixar o modelo de
    embeddings) não pode deixar o container em crash loop.

    O entrypoint roda com `set -e`: se o `python` de indexação falhasse, o
    container morria antes do uvicorn e o ERP recebia "assistente
    indisponível" em vez do 503 explicativo.
    """
    nomes, conteudo, modos = zip_build
    ep = f"{ROOT_IN_ZIP}/chatbot/entrypoint.sh"
    assert ep in nomes, "chatbot/entrypoint.sh ausente no pacote"
    texto = conteudo[ep].decode("utf-8", errors="replace")
    assert "Continuando sem indice" in texto, (
        "chatbot/entrypoint.sh precisa seguir para o uvicorn mesmo se a "
        "indexação do manual falhar (aviso no log + bot sobe)"
    )
