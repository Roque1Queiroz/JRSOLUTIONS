from django import forms
from .models import Produto, Categoria, Estoque, MovimentacaoEstoque

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['categoria', 'nome', 'sku', 'descricao', 'preco_custo', 'preco_venda', 'ativo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU único'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco_custo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'preco_venda': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = (
            Categoria.objects.filter(empresa=empresa)
            if empresa
            else Categoria.objects.none()
        )
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class EstoqueForm(forms.ModelForm):
    class Meta:
        model = Estoque
        fields = ['quantidade_minima', 'localizacao']
        widgets = {
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Prateleira A1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['tipo_movimento', 'quantidade', 'motivo']
        widgets = {
            'tipo_movimento': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"
