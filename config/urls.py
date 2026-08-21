# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from meigestao_app.core.views import DashboardView, cadastro

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    # Alias limpo da raiz para o cadastro self-service (mesma view do core; a landing
    # aponta o botão "Começar teste grátis" para esta URL).
    path('cadastro/', cadastro, name='cadastro'),
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
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# /media/ (logo da empresa p/ white label, anexos, etc.) também é servido em PRODUÇÃO.
# ATENÇÃO: o helper django.conf.urls.static.static() retorna [] quando DEBUG=False (Django 4.2),
# então registramos a rota via re_path direto para o upload aparecer mesmo com DJANGO_DEBUG=False.
# Fix: white label (marca/logo do cliente) não aparecia em produção (URL /media/ dava 404).
from django.urls import re_path as _re_path
from django.views.static import serve as _serve_media
urlpatterns += [
    _re_path(r"^media/(?P<path>.*)$", _serve_media,
             {"document_root": settings.MEDIA_ROOT}),
]
