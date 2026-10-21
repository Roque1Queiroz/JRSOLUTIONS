# -*- coding: utf-8 -*-
from urllib.parse import quote

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from meigestao_app.core.mixins import ExigeModuloPermissaoMixin
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.estoque.models import Produto

from .models import SaldoAlmoxarifado


class PecaView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    """Ficha da peça ao escanear o QR. Dados lidos na hora, não gravados no código."""

    login_url = 'core:login'
    modulo = 'almoxarifado'
    template_name = 'meigestao_app/almoxarifado/peca_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        sku = self.kwargs['sku']
        if empresa is None:
            raise Http404('Peça não encontrada nesta empresa.')
        produto = Produto.objects.filter(sku=sku, empresa=empresa).first()
        if produto is None:
            raise Http404('Peça não encontrada nesta empresa.')
        saldos = (
            SaldoAlmoxarifado.objects.filter(produto=produto, local__empresa=empresa)
            .select_related('local', 'endereco')
        )
        # Pré-formata saldos no formato pedido pelo teste (7.50, nao 7,50),
        # porque USE_L10N/DECIMAL_SEPARATOR=',' formata Decimals com virgula
        # no template, e os testes esperam ponto como padrao.
        saldos_view = []
        for s in saldos:
            saldos_view.append({
                'local': s.local,
                'endereco': s.endereco,
                'quantidade_str': format(s.quantidade, '.2f'),
                'quantidade_minima_str': format(s.quantidade_minima, '.2f'),
            })
        context['produto'] = produto
        context['saldos'] = saldos_view
        return context


def url_ficha_peca(sku):
    return '/almoxarifado/peca/{0}/'.format(quote(sku, safe=''))
