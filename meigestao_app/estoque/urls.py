from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    # Categorias
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/criar/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/', views.CategoriaDetailView.as_view(), name='categoria_detail'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/deletar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    
    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produto_list'),
    path('produtos/criar/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/importar/', views.ProdutoImportView.as_view(), name='produto_import'),
    path('produtos/importar/modelo/', views.modelo_produtos_csv, name='modelo_csv'),
    path('produtos/<int:pk>/', views.ProdutoDetailView.as_view(), name='produto_detail'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/deletar/', views.ProdutoDeleteView.as_view(), name='produto_delete'),
    
    # Estoque
    path('produtos/<int:pk>/estoque/', views.EstoqueDetailView.as_view(), name='estoque_detail'),
    path('produtos/<int:pk>/estoque/editar/', views.EstoqueUpdateView.as_view(), name='estoque_update'),
    
    # Movimentações
    path('movimentacoes/', views.MovimentacaoEstoqueListView.as_view(), name='movimentacao_list'),
    path('produtos/<int:produto_id>/movimentacao/', views.MovimentacaoEstoqueCreateView.as_view(), name='movimentacao_create'),
    
    # Relatório
    path('relatorio/', views.EstoqueRelatorioView.as_view(), name='estoque_relatorio'),
]