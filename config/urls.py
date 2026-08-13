# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from meigestao_app.core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('core/', include('meigestao_app.core.urls')),
    path('vendas/', include('meigestao_app.vendas.urls')),
    path('clientes/', include('meigestao_app.clientes.urls')),
    path('estoque/', include('meigestao_app.estoque.urls')),
    path('financeiro/', include('meigestao_app.financeiro.urls')),
    path('fiscal/', include('meigestao_app.fiscal.urls', namespace='fiscal')),
    path('usuarios/', include('meigestao_app.usuarios.urls')),
    path('almoxarifado/', include('meigestao_app.almoxarifado.urls', namespace='almoxarifado')),
    path('compras/', include('meigestao_app.compras.urls', namespace='compras')),
    path('servicos/', include('meigestao_app.servicos.urls', namespace='servicos')),
    path('producao/', include('meigestao_app.producao.urls', namespace='producao')),
    path('relatorios/', include('meigestao_app.relatorios.urls', namespace='relatorios')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
