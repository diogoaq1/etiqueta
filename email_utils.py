import smtplib
from email.mime.text import MIMEText
import os

def enviar_email(destinatario, assunto, corpo):
    remetente = os.getenv('EMAIL_USER')
    senha = os.getenv('EMAIL_PASS')

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.markachevrolet.com.br', 465) as smtp:
            smtp.login(remetente, senha)
            smtp.send_message(msg)
        print('Email enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar email: {e}')