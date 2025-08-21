from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

# 🔐 Formulário de login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# 👤 Formulário de registro
class RegisterForm(FlaskForm):
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=8, max=20)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(),
        EqualTo('senha', message='As senhas não coincidem.')
    ])
    submit = SubmitField('Registrar')

# 🔑 Formulário para alterar senha
class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField('Senha atual', validators=[DataRequired()])
    nova_senha = PasswordField('Nova senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar nova senha', validators=[
        DataRequired(),
        EqualTo('nova_senha', message='As senhas não coincidem.')
    ])
    submit = SubmitField('Alterar senha')

# 🧠 Formulário para recuperar senha
class RecuperarSenhaForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar link de recuperação')

# 🔄 Formulário para redefinir senha
class RedefinirSenhaForm(FlaskForm):
    nova_senha = PasswordField('Nova senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar nova senha', validators=[
        DataRequired(),
        EqualTo('nova_senha', message='As senhas não coincidem.')
    ])
    submit = SubmitField('Redefinir senha')

# 📋 Formulário de filtro para o dashboard
class FiltroNotasForm(FlaskForm):
    nome_cliente = StringField('Nome do Cliente', validators=[Optional()])
    controle = StringField('Número da Nota Fiscal', validators=[Optional()])
    emissao = DateField('Data de Emissão', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Filtrar')