from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={'class': 'form-control'}))
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(forms.ModelForm):
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']  # campos válidos no modelo padrão

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AlterarSenhaForm(forms.Form):
    senha_atual = forms.CharField(label='Senha Atual', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nova_senha = forms.CharField(label='Nova Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RecuperarSenhaForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

class RedefinirSenhaForm(forms.Form):
    nova_senha = forms.CharField(label='Nova Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_senha = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        senha1 = cleaned_data.get('nova_senha')
        senha2 = cleaned_data.get('confirmar_senha')
        if senha1 and senha2 and senha1 != senha2:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')

class FiltroNotasForm(forms.Form):
    nome_cliente = forms.CharField(required=False, label='Cliente', widget=forms.TextInput(attrs={'class': 'form-control'}))
    controle = forms.CharField(required=False, label='Número NF', widget=forms.TextInput(attrs={'class': 'form-control'}))
    emissao = forms.DateField(required=False, label='Data de Emissão', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))