from django import forms
from .models import NotaFiscal

class NotaFiscalForm(forms.ModelForm):
    """Formulário para emissão e edição de Notas Fiscais."""
    class Meta:
        model = NotaFiscal
        fields = [
            'cliente', 'venda', 'numero', 'serie', 'data_emissao', 
            'valor_subtotal', 'valor_desconto', 'valor_icms', 'valor_ipi', 
            'status', 'observacoes', 'empresa'
        ]
        widgets = {
            'data_emissao': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'venda': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número da NF'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Série'}),
            'valor_subtotal': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'valor_desconto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'valor_icms': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'valor_ipi': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
        }