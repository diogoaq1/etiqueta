from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 👤 Modelo de Usuário
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    token_recuperacao = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    # 🔐 Métodos de segurança
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<User {self.email}>'

# 📄 Modelo de Nota Fiscal
class NotaFiscal(db.Model):
    __bind_key__ = 'notas_fiscais'
    __tablename__ = 'notas_fiscais'
    id = db.Column(db.Integer, primary_key=True)
    controle = db.Column(db.String(50), nullable=False)
    nome_cliente = db.Column(db.String(100), nullable=False)
    emissao = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(150))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    transp = db.Column(db.String(100))
    vol = db.Column(db.Integer)
    obs = db.Column(db.Text)
    inf = db.Column(db.Text)
    chave_nfe = db.Column(db.Text)


    
    def __repr__(self):
        return f'<NotaFiscal {self.controle}>'
