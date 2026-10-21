# -*- coding: utf-8 -*-
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView

from meigestao_app.core.mixins import (
    ExigeEscritaModuloMixin,
    ExigeExclusaoModuloMixin,
    ExigeModuloPermissaoMixin,
)
from meigestao_app.core.utils.helpers import get_empresa_do_usuario

from .forms import CompromissoParceladoForm
from .models import CompromissoParcelado, ParcelaCompromisso, Transacao


MODULO = 'financeiro'


def _empresa_ou_recusa(user):
    empresa = get_empresa_do_usuario(user)
    if empresa is None:
        raise PermissionDenied('Usuário sem empresa não cria compromisso.')
    return empresa


def _resumo(compromisso, hoje=None):
    hoje = hoje or timezone.localdate()
    parcelas = list(compromisso.parcelas.all())
    abertas = [p for p in parcelas if (not p.paga) and p.vencimento >= hoje]
    vencidas = [p for p in parcelas if (not p.paga) and p.vencimento < hoje]
    pagas = [p for p in parcelas if p.paga]
    saldo = sum((p.valor for p in parcelas if not p.paga), Decimal('0.00'))
    return {
        'qtd_aberta': len(abertas),
        'qtd_vencida': len(vencidas),
        'qtd_paga': len(pagas),
        'saldo_falta': saldo,
        'parcelas': parcelas,
    }


class CompromissoListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    login_url = 'core:login'
    modulo = MODULO
    template_name = 'meigestao_app/financeiro/compromisso_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        itens = []
        if empresa is not None:
            qs = CompromissoParcelado.objects.filter(empresa=empresa).prefetch_related('parcelas')
            hoje = timezone.localdate()
            for compromisso in qs:
                dados = _resumo(compromisso, hoje)
                compromisso.qtd_aberta = dados['qtd_aberta']
                compromisso.qtd_vencida = dados['qtd_vencida']
                compromisso.qtd_paga = dados['qtd_paga']
                compromisso.saldo_falta = dados['saldo_falta']
                itens.append(compromisso)
        context['compromissos'] = itens
        return context


class CompromissoCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):
    login_url = 'core:login'
    modulo = MODULO
    model = CompromissoParcelado
    form_class = CompromissoParceladoForm
    template_name = 'meigestao_app/financeiro/compromisso_form.html'

    def form_valid(self, form):
        empresa = _empresa_ou_recusa(self.request.user)
        form.instance.empresa = empresa
        messages.success(self.request, 'Compromisso criado. O pagamento entra no caixa ao marcar a parcela como paga.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('financeiro:compromisso_detalhe', kwargs={'pk': self.object.pk})


class CompromissoDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):
    login_url = 'core:login'
    modulo = MODULO
    model = CompromissoParcelado
    template_name = 'meigestao_app/financeiro/compromisso_detail.html'
    context_object_name = 'compromisso'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        if empresa is None:
            return CompromissoParcelado.objects.none()
        return CompromissoParcelado.objects.filter(empresa=empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_resumo(self.object))
        return context


class NossoBoletoView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    login_url = 'core:login'
    modulo = MODULO
    template_name = 'meigestao_app/financeiro/nosso_boleto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        if empresa is None:
            raise Http404
        compromisso = get_object_or_404(
            CompromissoParcelado, pk=self.kwargs['pk'], empresa=empresa
        )
        parcela = get_object_or_404(
            ParcelaCompromisso, pk=self.kwargs['parcela_id'], compromisso=compromisso
        )
        context['compromisso'] = compromisso
        context['parcela'] = parcela
        return context


class ParcelaPagarView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):
    login_url = 'core:login'
    modulo = MODULO

    def post(self, request, pk, parcela_id):
        empresa = _empresa_ou_recusa(request.user)
        compromisso = get_object_or_404(CompromissoParcelado, pk=pk, empresa=empresa)
        parcela = get_object_or_404(
            ParcelaCompromisso, pk=parcela_id, compromisso=compromisso
        )
        with transaction.atomic():
            parcela = ParcelaCompromisso.objects.select_for_update().get(pk=parcela.pk)
            if parcela.paga:
                parcela.paga = False
                parcela.data_pagamento = None
                if parcela.transacao_id:
                    transacao = parcela.transacao
                    transacao.paga = False
                    transacao.save(update_fields=['paga', 'atualizado_em'])
                parcela.save(update_fields=['paga', 'data_pagamento', 'atualizado_em'])
                messages.success(request, 'Parcela desmarcada. A despesa continua no histórico, agora em aberto.')
            else:
                hoje = timezone.localdate()
                parcela.paga = True
                parcela.data_pagamento = hoje
                if parcela.transacao_id:
                    transacao = parcela.transacao
                    transacao.paga = True
                    transacao.valor = parcela.valor
                    transacao.data_vencimento = parcela.vencimento
                    transacao.empresa = compromisso.empresa
                    transacao.save(update_fields=[
                        'paga', 'valor', 'data_vencimento', 'empresa', 'atualizado_em'
                    ])
                else:
                    transacao = Transacao.objects.create(
                        empresa=compromisso.empresa,
                        tipo='despesa',
                        categoria='Compromisso parcelado',
                        descricao='{0} — {1}'.format(compromisso.descricao, parcela.referencia),
                        valor=parcela.valor,
                        data_transacao=hoje,
                        data_vencimento=parcela.vencimento,
                        paga=True,
                    )
                    parcela.transacao = transacao
                parcela.save(update_fields=[
                    'paga', 'data_pagamento', 'transacao', 'atualizado_em'
                ])
                messages.success(request, 'Parcela paga. A despesa entrou no caixa.')
        return redirect('financeiro:compromisso_detalhe', pk=compromisso.pk)


class CompromissoDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, View):
    login_url = 'core:login'
    modulo = MODULO

    def post(self, request, pk):
        empresa = _empresa_ou_recusa(request.user)
        compromisso = get_object_or_404(CompromissoParcelado, pk=pk, empresa=empresa)
        if compromisso.parcelas.filter(paga=True).exists():
            messages.error(
                request,
                'Não é possível excluir compromisso com parcela paga. Desmarque antes.',
            )
            return redirect('financeiro:compromisso_detalhe', pk=compromisso.pk)
        compromisso.delete()
        messages.success(request, 'Compromisso excluído.')
        return redirect('financeiro:compromisso_lista')
