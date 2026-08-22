# -*- coding: utf-8 -*-
"""
Aplica RBAC nas views da VM (clientes, vendas, estoque, financeiro) de forma
idempotente. Insere os mixins ExigeModuloPermissao/Escrita/Exclusao e a linha
`modulo = X` em cada view, preservando o resto do arquivo exatamente.
Cria backups .bak_rbac antes de alterar.
"""
import os, re, shutil, sys

BASE = "/home/ubuntu/Sistema_Gestor/meigestao_app"

# (arquivo, modulo, lista de [regex assinatura, novo_texto])
# Padrão: usa replace de strings simples por serem determinísticas na VM.

JOBS = {
    "clientes": {
        "modulo": "clientes",
        "import_line": "from meigestao_app.core.utils.csv_importer import CSVImportService",
        "import_add": ("from meigestao_app.core.mixins import ("
                       "ExigeModuloPermissaoMixin, ExigeEscritaModuloMixin, ExigeExclusaoModuloMixin)\n"
                       "MODULO_CLIENTES = 'clientes'"),
        "views": [
            ("class ClienteListView(LoginRequiredMixin, ListView):",
             "class ClienteListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = MODULO_CLIENTES"),
            ("class ClienteCreateView(LoginRequiredMixin, CreateView):",
             "class ClienteCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = MODULO_CLIENTES"),
            ("class ClienteDetailView(LoginRequiredMixin, DetailView):",
             "class ClienteDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = MODULO_CLIENTES"),
            ("class ClienteUpdateView(LoginRequiredMixin, UpdateView):",
             "class ClienteUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = MODULO_CLIENTES"),
            ("class ClienteDeleteView(LoginRequiredMixin, DeleteView):",
             "class ClienteDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):\n    modulo = MODULO_CLIENTES"),
            ("class ClienteImportView(LoginRequiredMixin, View):",
             "class ClienteImportView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):\n    modulo = MODULO_CLIENTES"),
        ],
    },
    "vendas": {
        "modulo": "vendas",
        "import_line": "logger = logging.getLogger(__name__)",
        "import_add": ("from meigestao_app.core.mixins import ("
                       "ExigeModuloPermissaoMixin, ExigeEscritaModuloMixin, ExigeExclusaoModuloMixin)\n"
                       "MODULO_VENDAS = 'vendas'"),
        "views": [
            ("class VendaListView(LoginRequiredMixin, ListView):",
             "class VendaListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = MODULO_VENDAS"),
            ("class VendaCreateView(LoginRequiredMixin, CreateView):",
             "class VendaCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = MODULO_VENDAS"),
            ("class VendaDetailView(LoginRequiredMixin, DetailView):",
             "class VendaDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = MODULO_VENDAS"),
            ("class VendaUpdateView(LoginRequiredMixin, UpdateView):",
             "class VendaUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = MODULO_VENDAS"),
            ("class VendaDeleteView(LoginRequiredMixin, DeleteView):",
             "class VendaDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):\n    modulo = MODULO_VENDAS"),
        ],
    },
    "estoque": {
        "modulo": "estoque",
        "import_line": "from meigestao_app.core.utils.helpers import get_empresa_do_usuario",
        "import_add": ("from meigestao_app.core.mixins import ("
                       "ExigeModuloPermissaoMixin, ExigeEscritaModuloMixin, ExigeExclusaoModuloMixin)\n"
                       "MODULO_ESTOQUE = 'estoque'"),
        "views": [
            ("class CategoriaListView(LoginRequiredMixin, ListView):",
             "class CategoriaListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = MODULO_ESTOQUE"),
            ("class CategoriaCreateView(LoginRequiredMixin, CreateView):",
             "class CategoriaCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = MODULO_ESTOQUE"),
            ("class CategoriaDetailView(LoginRequiredMixin, DetailView):",
             "class CategoriaDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = MODULO_ESTOQUE"),
            ("class CategoriaUpdateView(LoginRequiredMixin, UpdateView):",
             "class CategoriaUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = MODULO_ESTOQUE"),
            ("class CategoriaDeleteView(LoginRequiredMixin, DeleteView):",
             "class CategoriaDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoListView(LoginRequiredMixin, ListView):",
             "class ProdutoListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoCreateView(LoginRequiredMixin, CreateView):",
             "class ProdutoCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoDetailView(LoginRequiredMixin, DetailView):",
             "class ProdutoDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoUpdateView(LoginRequiredMixin, UpdateView):",
             "class ProdutoUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoDeleteView(LoginRequiredMixin, DeleteView):",
             "class ProdutoDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):\n    modulo = MODULO_ESTOQUE"),
            ("class EstoqueDetailView(LoginRequiredMixin, DetailView):",
             "class EstoqueDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = MODULO_ESTOQUE"),
            ("class EstoqueUpdateView(LoginRequiredMixin, UpdateView):",
             "class EstoqueUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = MODULO_ESTOQUE"),
            ("class MovimentacaoEstoqueCreateView(LoginRequiredMixin, CreateView):",
             "class MovimentacaoEstoqueCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = MODULO_ESTOQUE"),
            ("class MovimentacaoEstoqueListView(LoginRequiredMixin, ListView):",
             "class MovimentacaoEstoqueListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = MODULO_ESTOQUE"),
            ("class EstoqueRelatorioView(LoginRequiredMixin, TemplateView):",
             "class EstoqueRelatorioView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):\n    modulo = MODULO_ESTOQUE"),
            ("class ProdutoImportView(LoginRequiredMixin, View):",
             "class ProdutoImportView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):\n    modulo = MODULO_ESTOQUE"),
        ],
    },
    "financeiro": {
        "modulo": "financeiro",
        "import_line": "from meigestao_app.core.utils.helpers import get_empresa_do_usuario",
        "import_add": ("from meigestao_app.core.mixins import ("
                       "ExigeModuloPermissaoMixin, ExigeEscritaModuloMixin, ExigeExclusaoModuloMixin)"),
        "views": [
            ("class TransacaoListView(FluxoTransacaoMixin, LoginRequiredMixin, ListView):",
             "class TransacaoListView(FluxoTransacaoMixin, LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):\n    modulo = 'financeiro'"),
            ("class TransacaoDetailView(FluxoTransacaoMixin, LoginRequiredMixin, DetailView):",
             "class TransacaoDetailView(FluxoTransacaoMixin, LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):\n    modulo = 'financeiro'"),
            ("class TransacaoCreateView(FluxoTransacaoMixin, LoginRequiredMixin, CreateView):",
             "class TransacaoCreateView(FluxoTransacaoMixin, LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):\n    modulo = 'financeiro'"),
            ("class TransacaoUpdateView(FluxoTransacaoMixin, LoginRequiredMixin, UpdateView):",
             "class TransacaoUpdateView(FluxoTransacaoMixin, LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):\n    modulo = 'financeiro'"),
            ("class TransacaoDeleteView(FluxoTransacaoMixin, LoginRequiredMixin, DeleteView):",
             "class TransacaoDeleteView(FluxoTransacaoMixin, LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):\n    modulo = 'financeiro'"),
        ],
    },
}


def main():
    for app, job in JOBS.items():
        path = os.path.join(BASE, app, "views.py")
        s = open(path, encoding="utf-8").read()
        orig = s

        # backup
        bak = path + ".bak_rbac"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)

        # import
        if "core.mixins import" not in s:
            assert job["import_line"] in s, f"[{app}] linha de import nao achada"
            s = s.replace(job["import_line"], job["import_line"] + "\n" + job["import_add"], 1)
            print(f"[{app}] import adicionado")

        # views
        for old, new in job["views"]:
            if "Exige" in s.split(old, 1)[0].split(old)[0] if old in s else True:
                pass
            if old in s:
                # evita duplicar: se a linha seguinte ja tem modulo =, pula
                idx = s.find(old)
                after = s[idx+len(old):]
                if 'modulo =' in after[:40]:
                    continue
                s = s.replace(old, new, 1)
                print(f"[{app}] patcheada: {old.strip()[:60]}...")

        if s == orig:
            print(f"[{app}] SEM MUDANCAS (já patcheado ou nada a fazer)")
        else:
            open(path, "w", encoding="utf-8").write(s)
    print("DONE")


if __name__ == "__main__":
    main()
