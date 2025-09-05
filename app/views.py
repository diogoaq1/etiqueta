from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import (
    LoginForm, RegisterForm, FiltroNotasForm,
    AlterarSenhaForm, RecuperarSenhaForm, RedefinirSenhaForm
)
from django.contrib.auth.models import User
from .models import NotaFiscal
from .email_utils import enviar_email
from datetime import datetime
from pathlib import Path
import secrets
import qrcode
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render


def gerar_qrcode_chave_nfe(chave_nfe: str) -> str:
    """
    Gera o QR code em static/qrcodes/<chave>.png (se não existir)
    Retorna o caminho relativo para uso no template com {% static %}
    """
    static_base = Path(settings.BASE_DIR) / 'static'
    qrcodes_dir = static_base / 'qrcodes'
    qrcodes_dir.mkdir(parents=True, exist_ok=True)

    rel_path = Path('qrcodes') / f'{chave_nfe}.png'
    abs_path = qrcodes_dir / f'{chave_nfe}.png'

    if not abs_path.exists():
        img = qrcode.make(chave_nfe)
        img.save(abs_path)

    return str(rel_path).replace('\\', '/')

def index_view(request):
    ano = datetime.now().year
    return render(request, 'index.html', {'ano': ano})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        senha = form.cleaned_data['senha']
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            form.add_error(None, 'Usuário ou senha inválidos.')
    return render(request, 'login.html', {'form': form})

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['senha'])
        user.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard_view(request):
    form = FiltroNotasForm(request.POST or None)
    notas = NotaFiscal.objects.using('notas').all()

    if request.method == 'POST' and form.is_valid():
        nome_cliente = form.cleaned_data.get('nome_cliente')
        controle = form.cleaned_data.get('controle')
        emissao = form.cleaned_data.get('emissao')

        if nome_cliente:
            notas = notas.filter(nome_cliente__icontains=nome_cliente)
        if controle:
            notas = notas.filter(controle__icontains=controle)
        if emissao:
            notas = notas.filter(emissao=emissao)

    return render(request, 'dashboard.html', {
        'form': form,
        'notas_fiscais': notas
    })

@login_required
def alterar_senha_view(request):
    form = AlterarSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = request.user
        if user.check_password(form.cleaned_data['senha_atual']):
            user.set_password(form.cleaned_data['nova_senha'])
            user.save()
            return redirect('dashboard')
        form.add_error('senha_atual', 'Senha atual incorreta.')
    return render(request, 'alterar_senha.html', {'form': form})

def recuperar_senha_view(request):
    form = RecuperarSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.filter(email=form.cleaned_data['email']).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.token_recuperacao = token
            user.save()
            link = request.build_absolute_uri(f'/redefinir_senha/{token}/')
            enviar_email(user.email, 'Recuperação de senha', f'Clique no link para redefinir sua senha: {link}')
        return redirect('login')
    return render(request, 'recuperar_senha.html', {'form': form})

def redefinir_senha_view(request, token):
    user = User.objects.filter(token_recuperacao=token).first()
    if not user:
        return redirect('login')
    form = RedefinirSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['nova_senha'])
        user.token_recuperacao = None
        user.save()
        return redirect('login')
    return render(request, 'redefinir_senha.html', {'form': form})

@login_required
def visualizar_nota(request, controle):
    nota = get_object_or_404(
        NotaFiscal.objects.using('notas'),
        controle=controle
    )
    qr_rel_url = gerar_qrcode_chave_nfe(nota.chave_nfe)
    return render(request, 'nota.html', {
        'nota': nota,
        'qr_rel_url': qr_rel_url
    })


User = get_user_model()

@login_required
def admin_dashboard_view(request):
    usuarios = User.objects.all().order_by('id')
    return render(request, 'admin_dashboard.html', {'usuarios': usuarios})

@login_required
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        usuario.username = request.POST.get('username', usuario.username)
        usuario.email = request.POST.get('email', usuario.email)
        # Se tiver campo telefone no seu modelo personalizado:
        if hasattr(usuario, 'telefone'):
            usuario.telefone = request.POST.get('telefone', usuario.telefone)
        usuario.save()
        return redirect('admin_dashboard')

    return render(request, 'editar_usuario.html', {'usuario': usuario})

@login_required
def excluir_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    usuario.delete()
    return redirect('admin_dashboard')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')