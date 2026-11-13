from django import forms

from .models import ConfiguracaoIA, CotaUsuario


class ConfiguracaoIAForm(forms.ModelForm):
    nova_api_key = forms.CharField(
        label='Chave da API',
        required=False,
        widget=forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password'}),
        help_text='Deixe em branco para manter a chave atual.',
    )

    class Meta:
        model = ConfiguracaoIA
        fields = ['provedor', 'modelo', 'base_url', 'max_tokens', 'temperatura', 'cota_mensal_padrao', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome, campo in self.fields.items():
            if nome == 'ativo':
                campo.widget.attrs['class'] = 'form-check-input'
            elif nome == 'provedor':
                campo.widget.attrs['class'] = 'form-select'
            else:
                campo.widget.attrs['class'] = 'form-control'

    def clean_temperatura(self):
        valor = self.cleaned_data['temperatura']
        if not 0 <= valor <= 1:
            raise forms.ValidationError('Informe um valor entre 0 e 1.')
        return valor


class CotaUsuarioForm(forms.ModelForm):
    class Meta:
        model = CotaUsuario
        fields = ['cota_mensal', 'permitido']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cota_mensal'].widget.attrs['class'] = 'form-control'
        self.fields['permitido'].widget.attrs['class'] = 'form-check-input'
