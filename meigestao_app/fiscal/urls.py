from django.urls import path
from . import views

app_name = 'fiscal'

urlpatterns = [
    path('notas-fiscais/', views.NotaFiscalListView.as_view(), name='nota_fiscal_list'),
    path('notas-fiscais/criar/', views.NotaFiscalCreateView.as_view(), name='nota_fiscal_create'),
    path('notas-fiscais/criar-da-venda/<int:venda_id>/', views.NotaFiscalCreateFromVendaView.as_view(), name='nota_fiscal_create_from_venda'),
    path('notas-fiscais/<int:pk>/', views.NotaFiscalDetailView.as_view(), name='nota_fiscal_detail'),
    path('notas-fiscais/<int:pk>/editar/', views.NotaFiscalUpdateView.as_view(), name='nota_fiscal_update'),
    path('notas-fiscais/<int:pk>/deletar/', views.NotaFiscalDeleteView.as_view(), name='nota_fiscal_delete'),
    path('notas-fiscais/<int:pk>/pdf/', views.NotaFiscalPDFView.as_view(), name='nota_fiscal_pdf'),
    path('relatorio/', views.NotaFiscalRelatorioView.as_view(), name='nota_fiscal_relatorio'),
]
