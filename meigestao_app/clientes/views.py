from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import redirect
from .models import Cliente
from meigestao_app.core.utils.csv_importer import CSVImportService
from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.core.mixins import (
    ExigeModuloPermissaoMixin,
    ExigeEscritaModuloMixin,
    ExigeExclusaoModuloMixin,
)

MODULO = 'clientes'


class ClienteListView(LoginRequiredMixin, ExigeModuloPermissaoMixin, ListView):
    modulo = MODULO

    model = Cliente
    template_name = 'meigestao_app/clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Cliente.objects.filter(empresa=empresa)

    def get_create_url(self):
        return reverse_lazy('clientes:cliente_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['total_clientes'] = qs.count()
        context['clientes_ativos'] = qs.filter(ativo=True).count()
        context['clientes_inativos'] = qs.filter(ativo=False).count()
        return context

class ClienteCreateView(LoginRequiredMixin, ExigeEscritaModuloMixin, CreateView):
    modulo = MODULO
    model = Cliente
    template_name = 'meigestao_app/clientes/cliente_form.html'
    fields = ['nome', 'tipo', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'cidade', 'estado', 'cep', 'ativo']
    success_url = reverse_lazy('clientes:cliente_list')

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, 'Cliente criado com sucesso!')
        return super().form_valid(form)

class ClienteDetailView(LoginRequiredMixin, ExigeModuloPermissaoMixin, DetailView):
    modulo = MODULO
    model = Cliente
    template_name = 'meigestao_app/clientes/cliente_detail.html'
    context_object_name = 'cliente'

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Cliente.objects.filter(empresa=empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscamos as vendas explicitamente para garantir que o contexto as receba
        context['vendas_cliente'] = self.object.vendas.all().order_by('-data_venda')
        return context

class ClienteUpdateView(LoginRequiredMixin, ExigeEscritaModuloMixin, UpdateView):
    modulo = MODULO
    model = Cliente
    template_name = 'meigestao_app/clientes/cliente_form.html'
    fields = ['nome', 'tipo', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'cidade', 'estado', 'cep', 'ativo']
    success_url = reverse_lazy('clientes:cliente_list')

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Cliente.objects.filter(empresa=empresa)

    def form_valid(self, form):
        form.instance.empresa = get_empresa_do_usuario(self.request.user)
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)

class ClienteDeleteView(LoginRequiredMixin, ExigeExclusaoModuloMixin, DeleteView):
    modulo = MODULO
    model = Cliente
    template_name = 'meigestao_app/clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Cliente.objects.filter(empresa=empresa)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cliente excluido com sucesso!')
        return super().delete(request, *args, **kwargs)

class ClienteImportView(LoginRequiredMixin, ExigeEscritaModuloMixin, View):
    """
    View para processar a importação de clientes via CSV.
    """
    modulo = MODULO
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Nenhum arquivo enviado.')
            return redirect('clientes:cliente_list')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'O arquivo deve ser um CSV.')
            return redirect('clientes:cliente_list')

        # Define os campos obrigatórios
        required = ['nome', 'cpf_cnpj']
        
        # Função para salvar cada linha do CSV
        def save_cliente(row):
            cpf_cnpj = row.get('cpf_cnpj')
            nome = row.get('nome')
            
            if not cpf_cnpj or not nome:
                return False, "Nome ou CPF/CNPJ ausente na linha."

            # Busca empresa do perfil do usuário
            empresa = get_empresa_do_usuario(request.user)
            
            if Cliente.objects.filter(empresa=empresa, cpf_cnpj=cpf_cnpj).exists():
                return False, f"Cliente com CPF/CNPJ {cpf_cnpj} já cadastrado."

            try:
                Cliente.objects.create(
                    empresa=empresa,
                    nome=nome,
                    cpf_cnpj=cpf_cnpj,
                    email=row.get('email', ''),
                    telefone=row.get('telefone', ''),
                    endereco=row.get('endereco', ''),
                    cidade=row.get('cidade', ''),
                    estado=row.get('estado', ''),
                    cep=row.get('cep', ''),
                    tipo='pf' if len(cpf_cnpj) <= 14 else 'pj'
                )
                return True, ""
            except Exception as e:
                return False, str(e)

        importer = CSVImportService(csv_file.read(), required)
        importer.process(save_cliente)
        
        summary = importer.get_summary()
        
        if summary['success'] > 0:
            messages.success(request, f"{summary['success']} clientes importados com sucesso!")
        
        if summary['has_errors']:
            err_msg = f"Ocorreram {summary['total_errors']} erros durante a importação."
            if summary['errors']:
                err_details = "; ".join([f"Linha {e['line']}: {e['error']}" for e in summary['errors']])
                err_msg += f" Detalhes: {err_details}"
            messages.warning(request, err_msg)

        return redirect('clientes:cliente_list')
