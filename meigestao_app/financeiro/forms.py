from django import forms
from .models import Transacao, ContaBancaria, ReciboReembolso
from meigestao_app.usuarios.models import Perfil

class TransacaoForm(forms.ModelForm):
    """Formulário para transações financeiras (Receitas/Despesas)."""
    class Meta:
        model = Transacao
        fields = [
            'conta', 'tipo', 'categoria', 'descricao', 
            'valor', 'data_transacao', 'data_vencimento', 'paga', 'empresa'
        ]
        widgets = {
            'data_transacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Aluguel, Vendas, etc.'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalhes da transação...'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'conta': forms.Select(attrs={'class': 'form-select'}),
            'paga': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class ReciboReembolsoForm(forms.ModelForm):
    """Formulário para registro de recibos de reembolso."""
    class Meta:
        model = ReciboReembolso
        fields = ['colaborador', 'nome_solicitante', 'prioridade', 'item', 'valor', 'data_compra', 'foto_recibo', 'observacoes']
        widgets = {
            'colaborador': forms.Select(attrs={'class': 'form-select'}),
            'nome_solicitante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preencha se o solicitante não estiver na lista'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'item': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Uber, Almoço com Cliente, etc.'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'data_compra': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'DD/MM/AAAA'}),
            'foto_recibo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,application/pdf'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informações adicionais...'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['prioridade'].required = False
        
        if empresa:
            self.fields['colaborador'].queryset = Perfil.objects.filter(empresa=empresa, ativo=True)
        
        # Se não for staff, removemos a restrição de ver apenas a si mesmo se o usuário quiser permitir 
        # selecionar outros colaboradores da mesma empresa (conforme pedido: "não tem como altera")
        # Mas vamos manter o valor inicial como o perfil do usuário se estiver criando.
        if user and not user.is_staff and not self.instance.pk:
            try:
                self.fields['colaborador'].initial = user.perfil
            except AttributeError:
                pass

        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['prioridade'] = cleaned_data.get('prioridade') or 'media'
        colaborador = cleaned_data.get('colaborador')
        nome_solicitante = cleaned_data.get('nome_solicitante')

        if not colaborador and not nome_solicitante:
            raise forms.ValidationError("Selecione um colaborador da lista ou informe um nome manualmente.")
        
        return cleaned_data
