# -*- coding: utf-8 -*-
"""
Testes da infraestrutura central de permissões (RBAC leve).

Cobre:
1. Coerência da matriz em core.permissoes (funções x ver/alterar/excluir).
2. Aplicação dos mixins nas views: acesso negado por função e por escrita.
"""

from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from meigestao_app.clientes.models import Cliente
from meigestao_app.core.models import Empresa
from meigestao_app.core.permissoes import (
    funcao_pode_alterar_modulo,
    funcao_pode_excluir_modulo,
    funcao_pode_ver_modulo,
    modulos_que_ve,
)
from meigestao_app.usuarios.models import Perfil
from meigestao_app.vendas.models import Venda


@pytest.fixture
def empresa():
    return Empresa.objects.create(nome="Empresa Permissao", cnpj="33.333.333/0001-33")


@pytest.fixture
def empresa_profissional():
    # Plano profissional libera os módulos expandidos (fiscal/almoxarifado/compras/
    # producao) no middleware SaaS, deixando o RBAC decidir o acesso por função.
    return Empresa.objects.create(
        nome="Empresa Permissao Profissional",
        cnpj="44.444.444/0001-44",
        plano="profissional",
    )


@pytest.fixture
def usuario_com_permissao(db, empresa, permissao):
    usuario = User.objects.create_user(
        username=f"cli_{permissao}", password="senha-forte-teste"
    )
    Perfil.objects.create(
        usuario=usuario, empresa=empresa, permissao=permissao, data_admissao=date.today()
    )
    return usuario


# ───────────────────────────── 1) MATRIZ (unidade) ─────────────────────────────

def test_vendedor_ve_e_altera_clientes_mas_nao_exclui():
    assert funcao_pode_ver_modulo('vendedor', 'clientes')
    assert funcao_pode_alterar_modulo('vendedor', 'clientes')
    assert not funcao_pode_excluir_modulo('vendedor', 'clientes')


def test_vendedor_nao_ve_financeiro():
    assert not funcao_pode_ver_modulo('vendedor', 'financeiro')
    assert not funcao_pode_alterar_modulo('vendedor', 'financeiro')


def test_operador_so_leitura_basica():
    # Operador só vê dashboard + clientes, e NÃO altera nada além do básico.
    assert funcao_pode_ver_modulo('operador', 'clientes')
    assert not funcao_pode_ver_modulo('operador', 'vendas')
    assert not funcao_pode_ver_modulo('operador', 'financeiro')
    assert not funcao_pode_alterar_modulo('operador', 'clientes')


def test_almoxarife_controla_estoque_mas_nao_exclui():
    assert funcao_pode_ver_modulo('almoxarife', 'estoque')
    assert funcao_pode_alterar_modulo('almoxarife', 'estoque')
    assert not funcao_pode_excluir_modulo('almoxarife', 'estoque')


def test_gerente_e_admin_tem_acesso_amplo():
    assert len(modulos_que_ve('gerente')) == len(modulos_que_ve('admin'))
    assert funcao_pode_alterar_modulo('gerente', 'financeiro')
    assert funcao_pode_excluir_modulo('admin', 'vendas')
    assert funcao_pode_ver_modulo('admin', 'fiscal')


def test_funcao_desconhecida_nao_tem_acesso():
    assert not funcao_pode_ver_modulo('inexistente', 'vendas')
    assert not funcao_pode_alterar_modulo('inexistente', 'vendas')


# ───────────────────────── 2) APLICAÇÃO NAS VIEWS (integração) ─────────────────────────

class TestAcessoViewsPorFuncao:
    @pytest.mark.parametrize("permissao,esperado", [
        ('admin', 200),
        ('gerente', 200),
        ('vendedor', 200),
        ('operador', 403),  # operador não vê vendas
    ])
    @pytest.mark.django_db
    def test_venda_list(self, client, usuario_com_permissao, permissao, esperado, empresa):
        cliente = Cliente.objects.create(
            empresa=empresa, nome="C1", cpf_cnpj="111.222.333-44", email="c1@x.com"
        )
        Venda.objects.create(empresa=empresa, cliente=cliente, status="rascunho")
        client.force_login(usuario_com_permissao)
        resp = client.get(reverse("vendas:venda_list"))
        assert resp.status_code == esperado

    @pytest.mark.parametrize("permissao,esperado", [
        ('admin', 200),
        ('gerente', 200),
        ('vendedor', 200),
        ('operador', 200),  # operador vê clientes (leitura básica), mas não altera
    ])
    @pytest.mark.django_db
    def test_cliente_list(self, client, usuario_com_permissao, permissao, esperado, empresa):
        Cliente.objects.create(empresa=empresa, nome="C2", cpf_cnpj="555.666.777-88", email="c2@x.com")
        client.force_login(usuario_com_permissao)
        resp = client.get(reverse("clientes:cliente_list"))
        assert resp.status_code == esperado

    @pytest.mark.parametrize("permissao,esperado", [
        ('admin', 200),
        ('gerente', 200),
        ('vendedor', 403),   # vendedor NÃO vê financeiro
        ('operador', 403),
    ])
    @pytest.mark.django_db
    def test_financeiro_restrito(self, client, usuario_com_permissao, permissao, esperado, empresa):
        client.force_login(usuario_com_permissao)
        resp = client.get(reverse("financeiro:transacao_lista"))
        assert resp.status_code == esperado

    @pytest.mark.django_db
    def test_operador_nao_cria_cliente_via_get(self, client, empresa):
        usu = User.objects.create_user(username="op_criar", password="x")
        Perfil.objects.create(usuario=usu, empresa=empresa, permissao="operador", data_admissao=date.today())
        client.force_login(usu)
        resp = client.get(reverse("clientes:cliente_create"))
        assert resp.status_code == 403


class TestEscritaEDeletePorFuncao:
    @pytest.mark.django_db
    def test_operador_nao_altera_cliente(self, client, empresa):
        usu = User.objects.create_user(username="op_alt", password="x")
        Perfil.objects.create(usuario=usu, empresa=empresa, permissao="operador", data_admissao=date.today())
        cliente = Cliente.objects.create(
            empresa=empresa, nome="C operador", cpf_cnpj="000.111.222-33", email="o@x.com"
        )
        client.force_login(usu)  # operador
        resp = client.get(reverse("clientes:cliente_update", args=[cliente.pk]))
        assert resp.status_code == 403

    @pytest.mark.django_db
    def test_vendedor_nao_exclui_cliente(self, client, empresa):
        usu = User.objects.create_user(username="vend_exc", password="x")
        Perfil.objects.create(usuario=usu, empresa=empresa, permissao="vendedor", data_admissao=date.today())
        cliente = Cliente.objects.create(
            empresa=empresa, nome="C vend", cpf_cnpj="999.888.777-66", email="v@x.com"
        )
        client.force_login(usu)
        # Vendedor pode ver, mas NÃO pode excluir (matriz).
        resp_get = client.get(reverse("clientes:cliente_delete", args=[cliente.pk]))
        assert resp_get.status_code == 403


# ───────────────────── 3) RBAC NOS MÓDULOS EXPANDIDOS ─────────────────────
# almoxarifado, compras, fiscal, produção — mesma infraestrutura dos 4 núcleos.


class TestRBACModulosExpandidos:
    """Acesso por função aos módulos que receberam RBAC (19/08/2026)."""

    def _usu(self, client, empresa, permissao, tag):
        usu = User.objects.create_user(username=f"{tag}_{permissao}", password="x")
        Perfil.objects.create(
            usuario=usu, empresa=empresa, permissao=permissao, data_admissao=date.today()
        )
        client.force_login(usu)
        return usu

    @pytest.mark.django_db
    def test_operador_nao_ve_compras_em_get(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "operador", "op_c")
        assert client.get(reverse("compras:dashboard")).status_code == 403

    @pytest.mark.django_db
    def test_vendedor_nao_ve_fiscal(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "vendedor", "v_f")
        assert client.get(reverse("fiscal:nota_fiscal_list")).status_code == 403

    @pytest.mark.django_db
    def test_operador_nao_ve_almoxarifado(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "operador", "op_a")
        assert client.get(reverse("almoxarifado:dashboard")).status_code == 403

    @pytest.mark.django_db
    def test_vendedor_nao_ve_producao(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "vendedor", "v_p")
        assert client.get(reverse("producao:dashboard")).status_code == 403

    @pytest.mark.django_db
    def test_almoxarife_ve_almoxarifado_e_compras(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "almoxarife", "almox_g")
        assert client.get(reverse("almoxarifado:dashboard")).status_code == 200
        assert client.get(reverse("compras:dashboard")).status_code == 200

    @pytest.mark.django_db
    def test_producao_ve_producao_mas_nao_edita_compras(self, client, empresa_profissional):
        self._usu(client, empresa_profissional, "producao", "func_p")
        assert client.get(reverse("producao:dashboard")).status_code == 200
        # producao NÃO altera compras (leitura lá apenas; escrita negada)
        assert client.get(reverse("compras:fornecedor_create")).status_code == 403

    @pytest.mark.django_db
    def test_gerente_e_admin_abrem_todos_os_novos_modulos(self, client, empresa_profissional):
        for nome, permissao in (("ger_novos", "gerente"), ("adm_novos", "admin")):
            self._usu(client, empresa_profissional, permissao, nome)
            assert client.get(reverse("compras:dashboard")).status_code == 200, nome
            assert client.get(reverse("fiscal:nota_fiscal_list")).status_code == 200, nome
            assert client.get(reverse("almoxarifado:dashboard")).status_code == 200, nome
            assert client.get(reverse("producao:dashboard")).status_code == 200, nome


