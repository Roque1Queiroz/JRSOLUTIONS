from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('bi/', views.PainelBIView.as_view(), name='dashboard_bi'),
    path('bi/exportar/', views.DREExportPDFView.as_view(), name='dre_pdf'),
    path('almoxarifado/consumo/', views.RelatorioConsumoView.as_view(), name='relatorio_consumo'),
]
