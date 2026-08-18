from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta

from .models import Categoria, Produto, Estoque, MovimentacaoEstoque
from .forms import CategoriaForm, ProdutoForm, EstoqueForm, MovimentacaoEstoqueForm
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.core.mixins import (
    EmpresaFormMixin,
    EmpresaQuerysetMixin,
    PerfilPermissaoMixin,
    ExigeModuloPermissaoMixin,
    ExigeEscritaModuloMixin,
    ExigeExclusaoModuloMixin,
)

MODULO_ESTOQUE = 'estoque'


class CategoriaListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = MODULO_ESTOQUE

    """Lista todas as categorias"""
    model = Categoria
    template_name = 'meigestao_app/estoque/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 10
    
    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        queryset = Categoria.objects.filter(empresa=empresa)
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset


class CategoriaCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):
    modulo = MODULO_ESTOQUE

    """Cria uma nova categoria"""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'meigestao_app/estoque/categoria_form.html'
    success_url = reverse_lazy('estoque:categoria_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)


class CategoriaDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = MODULO_ESTOQUE

    """Detalhes da categoria"""
    model = Categoria
    template_name = 'meigestao_app/estoque/categoria_detail.html'
    context_object_name = 'categoria'


class CategoriaUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaQuerysetMixin, UpdateView):
    modulo = MODULO_ESTOQUE

    """Editar categoria"""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'meigestao_app/estoque/categoria_form.html'
    success_url = reverse_lazy('estoque:categoria_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, EmpresaQuerysetMixin, DeleteView):
    modulo = MODULO_ESTOQUE

    """Deletar categoria"""
    model = Categoria
    template_name = 'meigestao_app/estoque/categoria_confirm_delete.html'
    success_url = reverse_lazy('estoque:categoria_list')


class ProdutoListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = MODULO_ESTOQUE

    """Lista todos os produtos com filtros"""
    model = Produto
    template_name = 'meigestao_app/estoque/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 20
    
    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        queryset = Produto.objects.filter(empresa=empresa).select_related('categoria', 'estoque')
        
        # Filtro por categoria
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Filtro por status (ativo/inativo)
        ativo = self.request.GET.get('ativo')
        if ativo == 'true':
            queryset = queryset.filter(ativo=True)
        elif ativo == 'false':
            queryset = queryset.filter(ativo=False)
        
        # Busca por nome ou SKU
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) | Q(sku__icontains=busca)
            )
        
        # Filtro por estoque baixo
        estoque_baixo = self.request.GET.get('estoque_baixo')
        if estoque_baixo == 'true':
            queryset = queryset.filter(estoque__quantidade__lte=F('estoque__quantidade_minima'))
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        context['categorias'] = Categoria.objects.filter(empresa=empresa)
        context['total_produtos'] = Produto.objects.filter(empresa=empresa).count()
        context['produtos_inativos'] = Produto.objects.filter(empresa=empresa, ativo=False).count()
        context['estoque_baixo'] = Estoque.objects.filter(produto__empresa=empresa, quantidade__lte=F('quantidade_minima')).count()
        # KPI: Valor total do estoque
        context['valor_estoque'] = sum(e.valor_total() for e in Estoque.objects.filter(produto__empresa=empresa))
        return context


class ProdutoCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaFormMixin, CreateView):
    modulo = MODULO_ESTOQUE

    """Criar novo produto"""
    model = Produto
    form_class = ProdutoForm
    template_name = 'meigestao_app/estoque/produto_form.html'
    success_url = reverse_lazy('estoque:produto_list')
    
    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        response = super().form_valid(form)
        # Criar estoque automaticamente
        Estoque.objects.get_or_create(produto=self.object)
        return response


class ProdutoDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = MODULO_ESTOQUE

    """Detalhes do produto"""
    model = Produto
    template_name = 'meigestao_app/estoque/produto_detail.html'
    context_object_name = 'produto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        context['movimentacoes'] = self.object.movimentacoes.all()[:10]
        context['margem_lucro'] = self.object.margem_lucro()
        return context


class ProdutoUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaQuerysetMixin, EmpresaFormMixin, UpdateView):
    modulo = MODULO_ESTOQUE

    """Editar produto"""
    model = Produto
    form_class = ProdutoForm
    template_name = 'meigestao_app/estoque/produto_form.html'
    success_url = reverse_lazy('estoque:produto_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)


class ProdutoDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, EmpresaQuerysetMixin, DeleteView):
    modulo = MODULO_ESTOQUE

    """Deletar produto"""
    model = Produto
    template_name = 'meigestao_app/estoque/produto_confirm_delete.html'
    success_url = reverse_lazy('estoque:produto_list')


class EstoqueDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, EmpresaQuerysetMixin, DetailView):
    modulo = MODULO_ESTOQUE

    """Detalhes do estoque de um produto (pk na URL = pk do Produto)"""
    model = Estoque
    template_name = 'meigestao_app/estoque/estoque_detail.html'
    context_object_name = 'estoque'
    empresa_lookup = 'produto__empresa'

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        produto_pk = self.kwargs.get('pk')
        return get_object_or_404(self.get_queryset(), produto__pk=produto_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimentacoes'] = self.object.produto.movimentacoes.all()[:15]
        context['valor_total'] = self.object.valor_total()
        return context


class EstoqueUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, EmpresaQuerysetMixin, UpdateView):
    modulo = MODULO_ESTOQUE

    """Editar configurações de estoque (pk na URL = pk do Produto)"""
    model = Estoque
    form_class = EstoqueForm
    template_name = 'meigestao_app/estoque/estoque_form.html'
    empresa_lookup = 'produto__empresa'

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        produto_pk = self.kwargs.get('pk')
        return get_object_or_404(self.get_queryset(), produto__pk=produto_pk)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona para a página de detalhe usando o pk do PRODUTO
        return reverse_lazy('estoque:estoque_detail', kwargs={'pk': self.object.produto.pk})


class MovimentacaoEstoqueCreateView(
    LoginRequiredMixin,
    PerfilPermissaoMixin,
    CreateView,
):
    """Registrar movimentação de estoque"""
    permissoes_permitidas = ('admin', 'gerente', 'almoxarife')
    model = MovimentacaoEstoque
    form_class = MovimentacaoEstoqueForm
    template_name = 'meigestao_app/estoque/movimentacao_form.html'

    def get_produto(self):
        from django.shortcuts import get_object_or_404

        produto_id = self.kwargs.get('produto_id')
        if produto_id:
            return get_object_or_404(
                Produto,
                pk=produto_id,
                empresa=get_empresa_do_usuario(self.request.user),
            )
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produto'] = self.get_produto()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        produto = self.get_produto()
        if produto:
            form.instance.produto = produto
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return form

    def form_valid(self, form):
        if (
            form.cleaned_data.get('tipo_movimento') == 'ajuste'
            and not self.request.user.is_superuser
            and self.request.user.perfil.permissao not in ('admin', 'gerente')
        ):
            raise PermissionDenied(
                'Somente administrador ou gerente pode fazer ajuste absoluto de saldo.'
            )
        # Os atributos já foram vinculados no get_form
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        produto = self.get_produto()
        if produto:
            initial['produto'] = produto
        return initial

    def get_success_url(self):
        produto = self.get_produto()
        if produto:
            return reverse_lazy('estoque:estoque_detail', kwargs={'pk': produto.pk})
        return reverse_lazy('estoque:movimentacao_list')



class MovimentacaoEstoqueListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = MODULO_ESTOQUE

    """Lista histórico de movimentações"""
    model = MovimentacaoEstoque
    template_name = 'meigestao_app/estoque/movimentacao_list.html'
    context_object_name = 'movimentacoes'
    paginate_by = 20
    
    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        queryset = MovimentacaoEstoque.objects.filter(empresa=empresa).select_related('produto')
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_movimento=tipo)
        
        # Filtro por período
        periodo = self.request.GET.get('periodo')
        if periodo == 'hoje':
            queryset = queryset.filter(data_movimento__date=timezone.now().date())
        elif periodo == 'semana':
            data_inicio = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(data_movimento__gte=data_inicio)
        elif periodo == 'mes':
            data_inicio = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(data_movimento__gte=data_inicio)
        
        return queryset.order_by('-data_movimento')


class EstoqueRelatorioView(LoginRequiredMixin, ExigeModuloPermissaoMixin, TemplateView):
    modulo = MODULO_ESTOQUE

    """Relatório completo de estoque"""
    template_name = 'meigestao_app/estoque/estoque_relatorio.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_empresa_do_usuario(self.request.user)
        
        # Estatísticas gerais
        context['total_produtos'] = Produto.objects.filter(empresa=empresa).count()
        context['produtos_ativos'] = Produto.objects.filter(empresa=empresa, ativo=True).count()
        context['produtos_inativos'] = Produto.objects.filter(empresa=empresa, ativo=False).count()
        
        # Estoque
        context['valor_total_estoque'] = sum(
            e.valor_total() for e in Estoque.objects.filter(produto__empresa=empresa)
        )
        
        # Produtos em falta
        context['produtos_em_falta'] = Estoque.objects.filter(
            produto__empresa=empresa,
            quantidade__lte=F('quantidade_minima')
        ).select_related('produto')
        
        # Top 10 produtos por valor
        context['top_produtos'] = Estoque.objects.filter(produto__empresa=empresa).order_by('-quantidade')[:10]
        
        # Movimentações recentes
        context['movimentacoes_recentes'] = MovimentacaoEstoque.objects.filter(produto__empresa=empresa).select_related(
            'produto'
        ).order_by('-data_movimento')[:10]
        
        return context

class ProdutoImportView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):
    modulo = MODULO_ESTOQUE

    """
    View para processar a importação de produtos via CSV.
    """
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Nenhum arquivo enviado.')
            return redirect('estoque:produto_list')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'O arquivo deve ser um CSV.')
            return redirect('estoque:produto_list')

        # Define os campos obrigatórios
        required = ['nome', 'sku', 'preco_venda']
        
        from meigestao_app.core.utils.csv_importer import CSVImportService
        from decimal import Decimal

        def save_produto(row):
            sku = row.get('sku')
            nome = row.get('nome')
            
            if not sku or not nome:
                return False, "Nome ou SKU ausente na linha."

            # Busca empresa do perfil do usuário
            empresa = get_empresa_do_usuario(request.user)
            
            if Produto.objects.filter(empresa=empresa, sku=sku).exists():
                return False, f"Produto com SKU {sku} já cadastrado."

            try:
                # 1. Tratar Categoria
                cat_nome = row.get('categoria', 'Geral')
                categoria, _ = Categoria.objects.get_or_create(empresa=empresa, nome=cat_nome)

                # 3. Criar Produto
                produto = Produto.objects.create(
                    empresa=empresa,
                    categoria=categoria,
                    nome=nome,
                    sku=sku,
                    preco_custo=Decimal(row.get('preco_custo', '0').replace(',', '.')),
                    preco_venda=Decimal(row.get('preco_venda', '0').replace(',', '.')),
                    descricao=row.get('descricao', ''),
                    ativo=True
                )

                # 4. Inicializar Estoque
                qtd_inicial_str = row.get('estoque_inicial', '0')
                qtd_inicial = int(float(qtd_inicial_str.replace(',', '.'))) if qtd_inicial_str else 0
                
                estoque, _ = Estoque.objects.get_or_create(produto=produto)
                if qtd_inicial > 0:
                    estoque.quantidade = qtd_inicial
                    estoque.save()
                    
                    # Registrar movimentação inicial se houver estoque
                    MovimentacaoEstoque.objects.create(
                        produto=produto,
                        tipo_movimento='entrada',
                        quantidade=qtd_inicial,
                        motivo='Importação Inicial CSV'
                    )

                return True, ""
            except Exception as e:
                return False, str(e)

        importer = CSVImportService(csv_file.read(), required)
        importer.process(save_produto)
        
        summary = importer.get_summary()
        
        if summary['success'] > 0:
            messages.success(request, f"{summary['success']} produtos importados com sucesso!")
        
        if summary['has_errors']:
            err_msg = f"Ocorreram {summary['total_errors']} erros durante a importação."
            if summary['errors']:
                err_details = "; ".join([f"Linha {e['line']}: {e['error']}" for e in summary['errors']])
                err_msg += f" Detalhes: {err_details}"
            messages.warning(request, err_msg)

        return redirect('estoque:produto_list')