from django import forms
from .models import FichaTecnica, OrdemProducao

class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = FichaTecnica
        fields = ['produto_final', 'descricao', 'tempo_estimado_minutos', 'ativo']
        widgets = {
            'produto_final': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tempo_estimado_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} is-invalid"

class OrdemProducaoForm(forms.ModelForm):
    class Meta:
        model = OrdemProducao
        fields = ['ficha_tecnica', 'quantidade_planejada', 'custo_mao_obra_estimado']
        widgets = {
            'ficha_tecnica': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_planejada': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00',
                'onfocus': "if(this.value=='0.00' || this.value=='0') this.value='';"
            }),
            'custo_mao_obra_estimado': forms.NumberInput(attrs={
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
