from django.shortcuts import render, get_object_or_404, redirect
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Min, Q
from django.utils import timezone
from meigestao_app.core.mixins import EmpresaQuerysetMixin
from meigestao_app.estoque.models import Produto
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from .models import Fornecedor, PedidoCompra, Cotacao, ItemPedidoCompra

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'meigestao_app/compras/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        context['empresa'] = empresa
        
        qs_pedidos = PedidoCompra.objects.filter(empresa=empresa)
        context['pedidos_abertos'] = qs_pedidos.filter(status='SOLICITADO').count()
        context['em_cotacao'] = qs_pedidos.filter(status='COTACAO').count()
        context['aprovados'] = qs_pedidos.filter(status='APROVADO').count()
        context['fornecedores_ativos'] = Fornecedor.objects.filter(empresa=empresa, ativo=True).count()
        
        context['ultimos_pedidos'] = qs_pedidos.order_by('-criado_em')[:5]
        return context

class FornecedorListView(LoginRequiredMixin, ListView):
    model = Fornecedor
    template_name = 'meigestao_app/compras/fornecedor_list.html'
    context_object_name = 'fornecedores'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Fornecedor.objects.filter(empresa=empresa)

class FornecedorCreateView(LoginRequiredMixin, CreateView):
    model = Fornecedor
    template_name = 'meigestao_app/compras/fornecedor_form.html'
    fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco', 'ativo']
    success_url = reverse_lazy('compras:fornecedor_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, "Fornecedor cadastrado com sucesso!")
        return super().form_valid(form)

class FornecedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Fornecedor
    template_name = 'meigestao_app/compras/fornecedor_form.html'
    fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco', 'ativo']
    success_url = reverse_lazy('compras:fornecedor_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)

    def get_queryset(self):
        return Fornecedor.objects.filter(empresa=get_empresa_do_usuario(self.request.user))

class PedidoCompraCreateView(LoginRequiredMixin, CreateView):
    model = PedidoCompra
    template_name = 'meigestao_app/compras/pedido_form.html'
    fields = ['observacoes', 'data_prevista']
    success_url = reverse_lazy('compras:dashboard')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, "Solicitação de compra criada!")
        return super().form_valid(form)

class PedidoCompraDetailView(LoginRequiredMixin, EmpresaQuerysetMixin, DetailView):
    model = PedidoCompra
    template_name = 'meigestao_app/compras/pedido_detail.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Mapa de Cotação
        cotacoes = self.object.cotacoes.all().select_related('fornecedor')
        context['cotacoes'] = cotacoes
        
        # Lógica de Sugestão (Menor Preço e Menor Prazo)
        if cotacoes.exists():
            context['sugestao_preco'] = cotacoes.order_by('valor_total').first()
            context['sugestao_prazo'] = cotacoes.order_by('prazo_entrega_dias').first()
            
        context['fornecedores'] = Fornecedor.objects.filter(empresa=empresa, ativo=True)
        context['produtos'] = Produto.objects.filter(empresa=empresa, ativo=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Ação 0: Adicionar Item
        if 'add_item' in request.POST:
            produto_id = request.POST.get('produto_id')
            quantidade = request.POST.get('quantidade')
            produto = get_object_or_404(
                Produto,
                pk=produto_id,
                empresa=self.object.empresa,
            )
            ItemPedidoCompra.objects.create(
                pedido_compra=self.object,
                produto=produto,
                quantidade=quantidade
            )
            messages.success(request, "Item adicionado ao pedido.")

        # Ação 1: Adicionar Cotação
        if 'add_cotacao' in request.POST:
            fornecedor_id = request.POST.get('fornecedor_id')
            valor_total = request.POST.get('valor_total')
            prazo = request.POST.get('prazo')
            condicoes = request.POST.get('condicoes')
            anexo = request.FILES.get('anexo')
            fornecedor = get_object_or_404(
                Fornecedor,
                pk=fornecedor_id,
                empresa=self.object.empresa,
            )
            
            Cotacao.objects.create(
                pedido_compra=self.object,
                fornecedor=fornecedor,
                valor_total=valor_total,
                prazo_entrega_dias=prazo,
                condicoes_pagamento=condicoes,
                arquivo_anexo=anexo
            )
            
            # Muda status para COTACAO se ainda estiver SOLICITADO
            if self.object.status == 'SOLICITADO':
                self.object.status = 'COTACAO'
                self.object.save()
                
            messages.success(request, "Cotação adicionada com sucesso!")

        # Ação 2: Aprovar Cotação
        cotacao_id = request.POST.get('aprovar_cotacao')
        if cotacao_id:
            # Reseta outros vencedores
            self.object.cotacoes.update(vencedor=False)
            cotacao = get_object_or_404(Cotacao, pk=cotacao_id, pedido_compra=self.object)
            cotacao.vencedor = True
            cotacao.save()
            
            self.object.status = 'APROVADO'
            self.object.save()
            messages.success(request, f"Cotação do fornecedor {cotacao.fornecedor.nome} aprovada!")

        # Ação 3: Receber Mercadoria
        if 'receber_mercadoria' in request.POST:
            self.processar_recebimento()
            self.object.status = 'RECEBIDO'
            self.object.save()
            messages.success(request, "Mercadoria recebida! Estoque e Financeiro atualizados.")
            
        return redirect('compras:pedido_detail', pk=self.object.pk)

    def processar_recebimento(self):
        """Atualiza o estoque e cria a transação financeira."""
        from meigestao_app.estoque.models import MovimentacaoEstoque
        from meigestao_app.financeiro.models import Transacao
        from decimal import Decimal
        
        vencedor = self.object.cotacoes.filter(vencedor=True).first()
        valor_total = vencedor.valor_total if vencedor else Decimal('0.00')
        fornecedor_nome = vencedor.fornecedor.nome if vencedor else "Fornecedor"

        # 1. Atualiza Estoque para cada item
        for item in self.object.itens.all():
            MovimentacaoEstoque.objects.create(
                produto=item.produto,
                tipo_movimento='entrada',
                quantidade=item.quantidade,
                motivo=f"Entrada por Pedido de Compra #{self.object.id}"
            )
            
        # 2. Cria Lançamento Financeiro (Despesa)
        Transacao.objects.create(
            empresa=self.object.empresa,
            tipo='despesa',
            categoria='Compras',
            descricao=f"Compra #{self.object.id} - Fornecedor: {fornecedor_nome}",
            valor=valor_total,
            data_transacao=timezone.now().date(),
            paga=False
        )
