import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils import mysql_db as db
import pandas as pd
from datetime import date 

rescisao_cohort = os.path.join(os.path.dirname(__file__), '..', 'dash_gerencial', 'sql', 'rescisao_cohort.sql')


def count_months_passed(start_date, end_date):
    difference_in_year = (end_date.year - start_date.year) * 12
    
    difference_in_months = (end_date.month - start_date.month)
    difference = difference_in_year +  difference_in_months
    return difference

con = db.connect_to_db()
cursor = con.cursor()
colunas = ['codigo_contrato', 'data_de_inicio', 'data_de_rescisao', 'parceiro']
results = db.execute_select_in_db(cursor, rescisao_cohort)
df = pd.DataFrame(results, columns=colunas)
print("Dataframe gerado com sucesso!!!")

df['data_de_inicio'] = pd.to_datetime(df['data_de_inicio'])
df['data_de_rescisao'] = pd.to_datetime(df['data_de_rescisao'], errors='coerce')

# Removendo linhas com datas inválidas (NaT)
df = df.dropna(subset=['data_de_inicio', 'data_de_rescisao']) # TEM APENAS 1 LINHA
print("Removendo linhas com datas inválidas (NaT)")

# Aplicar a função às colunas do DataFrame e criar uma nova coluna
df['transacao'] = df.apply(lambda row: count_months_passed(row['data_de_inicio'], row['data_de_rescisao'] if pd.Timestamp(date.today()) > row['data_de_rescisao'] else date.today() ), axis=1) + 1
print("Aplicando a função às colunas do DataFrame e criar uma nova coluna")

# Filtrando os dados para manter apenas os registros do ano de 2023
df = df[df['data_de_inicio'].dt.year == 2023]
print("Filtrando os dados para manter apenas os registros do ano de 2023")

df['data_transacao'] = df.apply(lambda row: row['data_de_inicio'] + pd.DateOffset(months=row['transacao']) - pd.DateOffset(months= 1), axis=1)

# duplicando as linhas de acordo com a quantidade de transacao
df = df.loc[df.index.repeat(df['transacao'])].reset_index(drop=True)
print("Duplicando as linhas de acordo com a quantidade de transacao")

# colocando transacao no fromato de contagem e repetições
df['transacao'] = df.groupby('codigo_contrato').cumcount() 
print("colocando transacao no fromato de contagem e repetições")

# Criar a nova coluna 'data_de_inicio_mais_transacao_meses'
df['data_transacao'] = df.apply(lambda row: row['data_de_inicio'] + pd.DateOffset(months=row['transacao']), axis=1)
print("Criar a nova coluna 'data_de_inicio_mais_transacao_meses'")

df_rescisao = df[['codigo_contrato', 'data_de_inicio', 'parceiro', 'transacao', 'data_transacao']]

# Convertendo para o formato datetime, se ainda não estiver no formato correto
df_rescisao['data_de_inicio'] = pd.to_datetime(df_rescisao['data_de_inicio'])
df_rescisao['data_transacao'] = pd.to_datetime(df_rescisao['data_transacao'])

# Calculando o número de meses entre as datas
df_rescisao['cohort_mes'] = df_rescisao.apply(lambda row: (row['data_transacao'].year - row['data_de_inicio'].year) * 12 +
                                       (row['data_transacao'].month - row['data_de_inicio'].month) + 1, axis=1)
print("Criando a coluna de cohort ")

from utils.sheets import Sheets
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DASH_GERENCIAL_COHORT = os.getenv("CODE_SHEETS_DASH_GERENCIAL_COHORT")
PAGINA_SHEETS = 'df_rescisao'

sheet = Sheets(CODE_SHEETS_DASH_GERENCIAL_COHORT)
sheet.clear_and_upload(df_rescisao, PAGINA_SHEETS)

