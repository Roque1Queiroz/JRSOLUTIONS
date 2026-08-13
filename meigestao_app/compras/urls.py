from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('fornecedores/', views.FornecedorListView.as_view(), name='fornecedor_list'),
    path('fornecedores/novo/', views.FornecedorCreateView.as_view(), name='fornecedor_create'),
    path('fornecedores/<int:pk>/editar/', views.FornecedorUpdateView.as_view(), name='fornecedor_edit'),
    path('pedido/novo/', views.PedidoCompraCreateView.as_view(), name='pedido_create'),
    path('pedido/<int:pk>/', views.PedidoCompraDetailView.as_view(), name='pedido_detail'),
]
