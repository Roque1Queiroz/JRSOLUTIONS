# -*- coding: utf-8 -*-
"""
Patch mínimo e IDEMPOTENTE para aplicar RBAC (mixins centralizados) nos 4
módulos expandidos na VM do Sistema Gestor: almoxarifado, compras, fiscal,
producao, e ajuste da matriz central (almoxarife p/ compras).

A VM DIVERGE da cópia local -> nunca copiar arquivo inteiro; este script faz
substituições por âncora, é idempotente (não duplica se re-executado) e faz
backup automático (.bak_rbac_<ts>) antes de cada mudança.

Uso na VM (como ubuntu):
    python3 patch_rbac_modulos_vm.py
"""
import re
import shutil
import io
import ast
from datetime import datetime

BASE = "/home/ubuntu/Sistema_Gestor/meigestao_app"


def _iri(path):
    """Lê como texto com newline universal e retorna (texto, newline_original)."""
    with io.open(path, "r", newline="") as fh:
        data = fh.read()
    nl = "\r\n" if "\r\n" in data else "\n"
    return data.replace("\r\n", "\n"), nl


def _iwr(path, text, nl):
    with io.open(path, "w", newline="") as fh:
        fh.write(text.replace("\n", nl))


def backup(path):
    bak = f"{path}.bak_rbac_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(path, bak)
    return bak


def ensure_mixin_import(src, need):
    m = re.search(r"^from meigestao_app\.core\.mixins import ([^\n]*)$", src, re.M)
    if m:
        names = [n.strip().rstrip("\\").strip()
                 for n in m.group(1).replace("(", " ").replace(")", " ").split(",")
                 if n.strip() and not n.strip().startswith("#")]
        missing = need - set(names)
        if missing:
            new_names = sorted(set(names) | need)
            imp = "from meigestao_app.core.mixins import (\n    " + ",\n    ".join(new_names) + "\n)"
            src = src[:m.start()] + imp + src[m.end():]
        return src
    anchor = re.search(r"^from meigestao_app\.", src, re.M)
    assert anchor, "sem import meigestao_app para ancorar mixins"
    imp = "from meigestao_app.core.mixins import (\n    " + ",\n    ".join(sorted(need)) + "\n)"
    return src[:anchor.start()] + imp + "\n" + src[anchor.start():]


def ensure_login_mixin_import(src):
    return src.replace(
        "from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin",
        "from django.contrib.auth.mixins import LoginRequiredMixin", 1)


def set_class_mixin(src, cls, new_mixin, modname, legacy_mixin):
    """Garante que new_mixin venha LOGO APÓS LoginRequiredMixin na herança da
    classe (ordem crítica p/ o dispatch do Django) e garante modulo.
    Remove o legacy_mixin se presente."""
    # 1) remove mixin legado se presente
    if legacy_mixin:
        s2 = remove_from_class_heranca(src, cls, legacy_mixin)
        # remove também qualquer Exige* duplicado no fim (reposiciona)
        src = s2
    # procura a classe e reescreve a herança de forma determinística
    m = re.search(r"^(class %s\()([^\n]*?)(\):\s*\n)" % re.escape(cls), src, re.M)
    assert m, f"{cls}: assinatura de classe nao achada"
    bases = [b.strip() for b in m.group(2).split(",") if b.strip()]
    # separa: LoginRequiredMixin primeiro, depois o resto
    inicio = [b for b in bases if b == "LoginRequiredMixin"]
    resto = [b for b in bases if b != "LoginRequiredMixin" and not b.startswith("Exige")]
    # coloca new_mixin logo após LoginRequiredMixin (e remove outros Exige do resto)
    pos = inicio + [new_mixin] + resto
    nova = "class %s(%s):\n" % (cls, ", ".join(pos))
    src = src[:m.start()] + nova + src[m.end():]
    # 2) garante modulo
    cls_pat = re.compile(r"^(class %s\([^\n]*\):[ \t]*\n)" % re.escape(cls), re.M)
    mm = cls_pat.search(src)
    assert mm, f"{cls}: assinatura nao achada p/ modulo"
    window = src[mm.end():mm.end() + 200].split("def ")[0]
    if f"modulo = '{modname}'" not in window:
        src = src[:mm.end()] + f"    modulo = '{modname}'\n" + src[mm.end():]
    return src


def cls_heranca(src, cls):
    """Extrai a lista de heranças da classe (parênteses)."""
    m = re.search(r"class %s\(([^\n]*)\)" % re.escape(cls), src, re.M)
    return m.group(1) if m else ""


def remove_from_class_heranca(src, cls, mixin):
    """Remove `mixin` da lista de heranças da classe, ajustando vírgulas."""
    pat = re.compile(r"(class %s\([^\n]*?)[,\s]*%s([,\s\)])" % (re.escape(cls), re.escape(mixin)), re.M)
    if pat.search(src):
        return pat.sub(lambda m: m.group(1) + m.group(2), src, count=1)
    return src


def remove_mixin_class_legacy(src, class_name):
    pat = re.compile(r"^class %s\([^\n]*\):[ \t]*\n(?:.*?)\n(?=\n|class |def )" % re.escape(class_name),
                     re.M | re.S)
    assert pat.search(src), f"classe legada {class_name} nao achada (ja removida?)"
    return pat.sub("", src, count=1)


def finish(p, text, nl, label):
    ast.parse(text)
    _iwr(p, text, nl)
    print(f"  {label}: OK")


def process_module(modname, label, legacy_mixin, need_imports,
                   ver_views, esc_views, excl_views, target_file=None):
    p = f"{BASE}/{modname}/views.py" if target_file is None else target_file
    data, nl = _iri(p)
    # já processado se o mixin legado não aparece mais no arquivo (nem como classe
    # nem em herança)
    if legacy_mixin not in data:
        print(f"  {modname}: já aplicado (nada a fazer)")
        return
    print(f"  {modname}: backup {backup(p)}")
    data = ensure_login_mixin_import(data)
    data = ensure_mixin_import(data, need_imports)
    if legacy_mixin in data:
        data = remove_mixin_class_legacy(data, legacy_mixin)
    for c in ver_views:
        data = set_class_mixin(data, c, "ExigeModuloPermissaoMixin", modname, legacy_mixin)
    for c in esc_views:
        data = set_class_mixin(data, c, "ExigeEscritaModuloMixin", modname, legacy_mixin)
    for c in excl_views:
        data = set_class_mixin(data, c, "ExigeExclusaoModuloMixin", modname, legacy_mixin)
    finish(p, data, nl, label)


print("─ RBAC módulos expandidos (VM) ─")

process_module(
    "almoxarifado", "almoxarifado", "AlmoxarifeAccessMixin",
    {"EmpresaFormMixin", "EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin",
     "ExigeEscritaModuloMixin", "ExigeExclusaoModuloMixin"},
    ["AlmoxarifadoDashboardView", "RequisicaoListView", "RequisicaoDetailView",
     "EnderecoListView", "CentralEtiquetasView", "SetorListView"],
    ["RequisicaoCreateView", "RequisicaoAprovarView", "EnderecoCreateView",
     "SetorCreateView", "SetorUpdateView"],
    ["SetorDeleteView"],
)

process_module(
    "producao", "producao", "PCPAccessMixin",
    {"EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin", "ExigeEscritaModuloMixin"},
    ["PCPDashboardView", "FichaTecnicaListView", "OrdemProducaoListView",
     "OrdemProducaoDetailView"],
    ["FichaTecnicaCreateView", "OrdemProducaoCreateView", "OrdemProducaoActionView"],
    [],
)
# remove função morta get_permissao_usuario do producao (se sobrar)
_p = f"{BASE}/producao/views.py"
_d, _nl = _iri(_p)
if "def get_permissao_usuario" in _d and "get_permissao_usuario(" not in _d.replace("def get_permissao_usuario(", ""):
    pass  # keep guard simple


process_module(
    "compras", "compras", "__NENHUMA_LEGADO__",
    {"EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin", "ExigeEscritaModuloMixin"},
    ["DashboardView", "FornecedorListView", "PedidoCompraDetailView"],
    ["FornecedorCreateView", "FornecedorUpdateView", "PedidoCompraCreateView"],
    [],
)
# compras não tinha mixin legado; se as classes ainda só têm LoginRequired, processar
compras_p = f"{BASE}/compras/views.py"
_cd, _cnl = _iri(compras_p)
if "ExigeModuloPermissaoMixin" not in _cd:
    print("  compras: aplicando mixins (sem legado)")
    _b = backup(compras_p)
    _cd = ensure_mixin_import(_cd, {"EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin",
                                    "ExigeEscritaModuloMixin"})
    for _c in ["DashboardView", "FornecedorListView", "PedidoCompraDetailView"]:
        _cd = set_class_mixin(_cd, _c, "ExigeModuloPermissaoMixin", "compras", "")
    for _c in ["FornecedorCreateView", "FornecedorUpdateView", "PedidoCompraCreateView"]:
        _cd = set_class_mixin(_cd, _c, "ExigeEscritaModuloMixin", "compras", "")
    finish(compras_p, _cd, _cnl, "compras(2)")


process_module(
    "fiscal", "fiscal", "__NENHUMA_LEGADO__",
    {"EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin", "ExigeEscritaModuloMixin",
     "ExigeExclusaoModuloMixin"},
    ["NotaFiscalListView", "NotaFiscalDetailView", "NotaFiscalRelatorioView",
     "NotaFiscalPDFView"],
    ["NotaFiscalCreateView", "NotaFiscalUpdateView", "NotaFiscalCreateFromVendaView"],
    ["NotaFiscalDeleteView"],
)
fiscal_p = f"{BASE}/fiscal/views.py"
_fd, _fnl = _iri(fiscal_p)
if "ExigeModuloPermissaoMixin" not in _fd:
    print("  fiscal: aplicando mixins (sem legado)")
    _b = backup(fiscal_p)
    _fd = ensure_mixin_import(_fd, {"EmpresaQuerysetMixin", "ExigeModuloPermissaoMixin",
                                    "ExigeEscritaModuloMixin", "ExigeExclusaoModuloMixin"})
    for _c in ["NotaFiscalListView", "NotaFiscalDetailView", "NotaFiscalRelatorioView",
               "NotaFiscalPDFView"]:
        _fd = set_class_mixin(_fd, _c, "ExigeModuloPermissaoMixin", "fiscal", "")
    for _c in ["NotaFiscalCreateView", "NotaFiscalUpdateView", "NotaFiscalCreateFromVendaView"]:
        _fd = set_class_mixin(_fd, _c, "ExigeEscritaModuloMixin", "fiscal", "")
    _fd = set_class_mixin(_fd, "NotaFiscalDeleteView", "ExigeExclusaoModuloMixin", "fiscal", "")
    finish(fiscal_p, _fd, _fnl, "fiscal(2)")


# MATRIZ CENTRAL: almoxarife p/ compras
perm_p = f"{BASE}/core/permissoes.py"
_pd, _pnl = _iri(perm_p)
if "'almoxarife', 'compras'" not in _pd:
    print(f"  permissoes: backup {backup(perm_p)}")
    _pd = _pd.replace(
        "'almoxarife': ['dashboard', 'estoque', 'almoxarifado', 'producao']",
        "'almoxarife': ['dashboard', 'estoque', 'almoxarifado', 'producao', 'compras']", 1)
    _pd = _pd.replace(
        "'almoxarife': ['estoque', 'almoxarifado', 'producao']",
        "'almoxarife': ['estoque', 'almoxarifado', 'producao', 'compras']", 1)
    finish(perm_p, _pd, _pnl, "permissoes")
else:
    print("  permissoes: já permite almoxarife em compras")

print("\nFEITO")
