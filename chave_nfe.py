import qrcode
import os

def gerar_qrcode_chave_nfe(chave_nfe):
    # Define o caminho onde o QR Code será salvo
    caminho = f'static/qrcodes/{chave_nfe}.png'

    # Gera o QR Code apenas se ainda não existir
    if not os.path.exists(caminho):
        qr = qrcode.make(chave_nfe)
        qr.save(caminho)

    return caminho