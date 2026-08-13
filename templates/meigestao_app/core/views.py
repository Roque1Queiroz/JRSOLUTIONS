from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Empresa

class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'meigestao_app/core/empresa_list.html'
    context_object_name = 'object_list'
    paginate_by = 20

class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'meigestao_app/core/empresa_detail.html'

class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    template_name = 'meigestao_app/core/empresa_form.html'
    fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco']
    success_url = reverse_lazy('core:empresa_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)

class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    template_name = 'meigestao_app/core/empresa_form.html'
    fields = ['nome', 'cnpj', 'email', 'telefone', 'endereco']
    success_url = reverse_lazy('core:empresa_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        return super().form_valid(form)

class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    template_name = 'meigestao_app/core/empresa_confirm_delete.html'
    success_url = reverse_lazy('core:empresa_list')