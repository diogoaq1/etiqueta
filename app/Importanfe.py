import os
import sqlite3
import xmltodict
from datetime import datetime

# 📂 Caminho da pasta com os arquivos XML
PASTA_XML = 'c:/xml'

# 📂 Pasta onde o banco será salvo
PASTA_BANCO = 'c:/xml/banco'
NOME_BANCO = 'notas_fiscais.db'

# 🔧 Garante que a pasta do banco existe
os.makedirs(PASTA_BANCO, exist_ok=True)
CAMINHO_BANCO = os.path.join(PASTA_BANCO, NOME_BANCO)

# 🗃️ Conexão com banco SQLite
conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()

# 🏗️ Criação da tabela com campo data como TEXTO no formato dd/mm/aaaa
cursor.execute('''
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    endereco TEXT,
    numero TEXT,
    bairro TEXT,
    cidade TEXT,
    uf TEXT,
    cep TEXT,
    nNF TEXT,
    vol TEXT,
    data TEXT,  -- formato dd/mm/aaaa
    xNome TEXT,
    infCpl TEXT
)
''')

# 🔄 Função para extrair dados do XML
def extrair_dados(xml_path):
    try:
        with open(xml_path, encoding='utf-8') as f:
            doc = xmltodict.parse(f.read())

        nota = doc.get('nfeProc', {}).get('NFe', {}).get('infNFe', {})

        nome = nota.get('entrega', {}).get('xNome')
        endereco = nota.get('entrega', {}).get('xLgr')
        numero = nota.get('entrega', {}).get('nro')
        bairro = nota.get('entrega', {}).get('xBairro')
        cidade = nota.get('entrega', {}).get('xMun')
        uf = nota.get('entrega', {}).get('UF')
        cep = nota.get('entrega', {}).get('CEP')
        nNF = nota.get('ide', {}).get('nNF')
        vol = nota.get('transp', {}).get('vol', {}).get('qVol')
        dhEmi = nota.get('ide', {}).get('dhEmi', '')[:10]  # Ex: '2025-08-19'
        xNome = nota.get('transp', {}).get('transporta', {}).get('xNome')
        infCpl = nota.get('infAdic', {}).get('infCpl')

        # 🧠 Converte data para formato dd/mm/aaaa
        try:
            data_formatada = datetime.strptime(dhEmi, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            data_formatada = ''

        print(f'✔️ {os.path.basename(xml_path)}: nNF={nNF}, data={data_formatada}, nome={nome}')
        return nome, endereco, numero, bairro, cidade, uf, cep, nNF, vol, data_formatada, xNome, infCpl
    except Exception as e:
        print(f'❌ Erro ao processar {xml_path}: {e}')
        return None

# 📦 Processar todos os arquivos XML da pasta
if os.path.isdir(PASTA_XML):
    arquivos_xml = [f for f in os.listdir(PASTA_XML) if f.endswith('.xml')]
    if not arquivos_xml:
        print('⚠️ Nenhum arquivo XML encontrado na pasta.')
    else:
        total = 0
        for arquivo in arquivos_xml:
            caminho_arquivo = os.path.join(PASTA_XML, arquivo)
            dados = extrair_dados(caminho_arquivo)
            if dados and any(dados):
                cursor.execute('''
                INSERT INTO notas (
                    nome, endereco, numero, bairro, cidade, uf,cep, nNF, vol, data, xNome, infCpl
                ) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', dados)
                total += 1
        conn.commit()
        print(f'✅ Importação concluída! {total} registros salvos. Banco: {CAMINHO_BANCO}')
else:
    print('❌ Caminho inválido. Verifique se a pasta existe.')

conn.close()