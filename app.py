import os
import secrets
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from models import db, User, NotaFiscal
from forms import (
    RegisterForm, LoginForm, AlterarSenhaForm,
    RecuperarSenhaForm, RedefinirSenhaForm, FiltroNotasForm
)
from email_utils import enviar_email
import qrcode

# 🔧 Função para gerar QR Code
def gerar_qrcode_chave_nfe(chave_nfe):
    caminho = f'static/qrcodes/{chave_nfe}.png'
    if not os.path.exists(caminho):
        img = qrcode.make(chave_nfe)
        img.save(caminho)
    return caminho

# 🚀 Inicialização do Flask
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {
    'notas_fiscais': 'sqlite:///notas_fiscais.db'
}
db.init_app(app)
csrf = CSRFProtect(app)

# 🏠 Página inicial com botão de login
@app.route('/')
def index():
    ano_atual = datetime.now().year
    return render_template('index.html', ano_atual=ano_atual)

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verificar_senha(form.senha.data):
            session['user'] = user.nome
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('admin_dashboard' if user.is_admin else 'dashboard'))
        else:
            form.senha.errors.append('Email ou senha inválidos.')
    return render_template('login.html', form=form)

# 👤 Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data
        )
        user.set_senha(form.senha.data)
        db.session.add(user)
        db.session.commit()
        enviar_email(user.email, 'Bem-vindo!', f'Olá {user.nome}, seja bem-vindo ao nosso sistema!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# 📋 Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    form = FiltroNotasForm()
    query = NotaFiscal.query

    if form.validate_on_submit():
        if form.nome_cliente.data:
            query = query.filter(NotaFiscal.nome_cliente.ilike(f"%{form.nome_cliente.data}%"))
        if form.controle.data:
            query = query.filter(NotaFiscal.controle.ilike(f"%{form.controle.data}%"))
        if form.emissao.data:
            query = query.filter(NotaFiscal.emissao == form.emissao.data)

    notas_fiscais = query.all()

    for nota in notas_fiscais:
        try:
            nota.data_formatada = datetime.strptime(nota.data, "%d/%m/%Y")
        except Exception:
            nota.data_formatada = None

    return render_template('dashboard.html', nome=session['user'], notas_fiscais=notas_fiscais, form=form)

# 🔑 Alterar senha
@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(nome=session['user']).first()
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if user.verificar_senha(form.senha_atual.data):
            user.set_senha(form.nova_senha.data)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            form.senha_atual.errors.append('Senha atual incorreta.')
    return render_template('alterar_senha.html', form=form)

# 🧠 Recuperar senha
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    form = RecuperarSenhaForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.token_recuperacao = token
            db.session.commit()
            link = f'http://localhost:5000/redefinir_senha/{token}'
            enviar_email(user.email, 'Recuperação de senha', f'Clique no link para redefinir sua senha: {link}')
        return redirect(url_for('login'))
    return render_template('recuperar_senha.html', form=form)

# 🔄 Redefinir senha
@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    user = User.query.filter_by(token_recuperacao=token).first()
    if not user:
        return redirect(url_for('login'))
    form = RedefinirSenhaForm()
    if form.validate_on_submit():
        user.set_senha(form.nova_senha.data)
        user.token_recuperacao = None
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('redefinir_senha.html', form=form)

# 🛠️ Painel administrativo
@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    usuarios = User.query.all()
    return render_template('admin_dashboard.html', usuarios=usuarios)

# ✏️ Editar usuário
@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.nome = request.form['nome']
        user.email = request.form['email']
        user.telefone = request.form['telefone']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('editar_usuario.html', user=user)

# ❌ Excluir usuário
@app.route('/excluir_usuario/<int:id>')
def excluir_usuario(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# 📄 Visualizar nota fiscal
@app.route('/nota/<int:controle>')
def visualizar_nota(controle):
    if 'user' not in session:
        return redirect(url_for('login'))
    nota = NotaFiscal.query.filter_by(controle=str(controle)).first_or_404()
    gerar_qrcode_chave_nfe(nota.chave_nfe)
    return render_template('nota.html', nota=nota)

# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 🧪 Execução local
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)