# -*- coding: utf-8 -*-
from django.urls import path
from .views import (
    VendaListView,
    VendaCreateView,
    VendaDetailView,
    VendaUpdateView,
    VendaDeleteView,
)

app_name = 'vendas'

urlpatterns = [
    path('', VendaListView.as_view(), name='venda_list'),
    path('criar/', VendaCreateView.as_view(), name='venda_create'),
    path('<int:pk>/', VendaDetailView.as_view(), name='venda_detail'),
    path('<int:pk>/editar/', VendaUpdateView.as_view(), name='venda_update'),
    path('<int:pk>/excluir/', VendaDeleteView.as_view(), name='venda_delete'),
]
