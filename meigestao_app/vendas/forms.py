from django import forms
from django.forms import inlineformset_factory
from .models import Venda, ItemVenda

class VendaForm(forms.ModelForm):
    """Formulário para o modelo Venda."""
    class Meta:
        model = Venda
        fields = ['cliente', 'data_venda', 'descricao', 'desconto', 'status', 'observacoes']
        widgets = {
            'data_venda': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'desconto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class ItemVendaForm(forms.ModelForm):
    """Formulário para o modelo ItemVenda."""
    class Meta:
        model = ItemVenda
        fields = ['produto_vinculado', 'produto_nome', 'quantidade', 'preco_unitario']
        widgets = {
            'produto_vinculado': forms.Select(attrs={'class': 'form-select'}),
            'produto_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'preco_unitario': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

ItemVendaFormSet = inlineformset_factory(
    Venda, 
    ItemVenda, 
    form=ItemVendaForm,
    extra=1, 
    can_delete=True
)
