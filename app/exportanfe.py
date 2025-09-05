import sqlite3
import pandas as pd
import os
import cx_Oracle

# 🔧 Inicializa o Oracle Client
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_11_2")

# 🔌 Conexão com o banco Oracle
conn_origem = cx_Oracle.connect(
    user='nbsat',
    password='nbsa',
    dsn='192.168.0.7/nbsimpar.world'
)

# 📄 Consulta SQL
sql = """
SELECT
  ROW_NUMBER() OVER (ORDER BY v.emissao, v.controle) AS id,
  v.controle,
  TRUNC(v.emissao) AS emissao,
  v.local_entrega_nome_cliente AS nome_cliente,
  v.local_entrega_logradouro AS endereco,
  v.local_entrega_fachada AS numero,
  v.local_entrega_bairro AS bairro,
  v.local_entrega_cidade AS cidade,
  v.local_entrega_uf AS uf,
  cd.cep AS cep,
  t.descricao AS transp,
  v.observacoes AS obs,
  v.inf_complementar AS inf,
  v.volume_quantidade AS vol,
  nfe.chave_nfe
FROM VENDAS v
INNER JOIN transportadoras t ON v.cod_transportadora = t.cod_transportadora
INNER JOIN nfe_movimento nfe ON v.controle = nfe.numr_controle AND v.cod_empresa = nfe.id_empresa
INNER JOIN clientes c ON v.cod_cliente = c.cod_cliente
INNER JOIN cliente_diverso cd ON v.local_entrega_cod_cliente=cd.cod_cliente
INNER JOIN cidades cid ON cd.cod_cidades = cid.cod_cidades
WHERE v.cod_empresa = 12 AND v.local_entrega_nome_cliente IS NOT NULL
  AND v.emissao > TO_DATE('18/08/2025','DD/MM/YYYY')

UNION ALL

SELECT
  ROW_NUMBER() OVER (ORDER BY v.emissao, v.controle) + (
    SELECT COUNT(*) FROM VENDAS v2
    WHERE v2.cod_empresa = 12 AND v2.local_entrega_nome_cliente IS NOT NULL
      AND v2.emissao > TO_DATE('18/08/2025','DD/MM/YYYY')
  ) AS id,
  v.controle,
  TRUNC(v.emissao) AS emissao,
  c.nome AS nome_cliente,
  cd.endereco AS endereco,
  cd.fachada AS numero,
  cd.bairro AS bairro,
  cid.descricao AS cidade,
  cd.uf AS uf,
  cd.cep AS cep,
  t.descricao AS transp,
  v.observacoes AS obs,
  v.inf_complementar AS inf,
  v.volume_quantidade AS vol,
  nfe.chave_nfe
FROM VENDAS v
INNER JOIN transportadoras t ON v.cod_transportadora = t.cod_transportadora
INNER JOIN nfe_movimento nfe ON v.controle = nfe.numr_controle AND v.cod_empresa = nfe.id_empresa
INNER JOIN clientes c ON v.cod_cliente = c.cod_cliente
INNER JOIN cliente_diverso cd ON v.cod_cliente = cd.cod_cliente
INNER JOIN cidades cid ON cd.cod_cidades = cid.cod_cidades
WHERE v.cod_empresa = 12 AND v.local_entrega_nome_cliente IS NULL
  AND v.emissao > TO_DATE('18/08/2025','DD/MM/YYYY')
"""

# 📥 Executa a consulta e carrega em DataFrame
df = pd.read_sql(sql, conn_origem)
print(df.columns.tolist())


df['EMISSAO'] = pd.to_datetime(df['EMISSAO'], format='%d/%m/%Y').dt.date


# 📁 Garante que a pasta existe
os.makedirs(r'C:\xml', exist_ok=True)

# 🗃️ Conecta ao banco SQLite
sqlite_path = r'C:\xml\notas_fiscais.db'
conn_sqlite = sqlite3.connect(sqlite_path)

# 🧾 Salva os dados na tabela 'notas_fiscais'
df.to_sql('notas_fiscais', conn_sqlite, if_exists='replace', index=False)

# ✅ Finaliza
conn_origem.close()
conn_sqlite.close()
print("Consulta salva com sucesso em C:\\xml\\notas_fiscais.db")