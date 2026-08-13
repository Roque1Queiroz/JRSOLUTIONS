# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from gestor.core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('core/', include('gestor.core.urls')),
    path('vendas/', include('gestor.vendas.urls')),
    path('clientes/', include('gestor.clientes.urls')),
    path('estoque/', include('gestor.estoque.urls')),
    path('financeiro/', include('gestor.financeiro.urls')),
    path('fiscal/', include('gestor.fiscal.urls')),
    path('usuarios/', include('gestor.usuarios.urls')),
    path('relatorios/', include('gestor.relatorios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

