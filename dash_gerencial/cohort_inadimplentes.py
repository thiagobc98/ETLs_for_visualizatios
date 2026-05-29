import sys
from utils.sheets import Sheets
import dotenv
import os
from utils import mysql_db as db
import pandas as pd
from datetime import date, datetime
dotenv.load_dotenv()

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

cohort_inadimplentes = os.path.join(os.path.dirname(__file__), '..', 'dash_gerencial', 'sql', 'cohort_inadimplentes.sql')


def count_months_passed(start_date, end_date):
    difference_in_year = (end_date.year - start_date.year) * 12
    
    difference_in_months = (end_date.month - start_date.month)
    difference = difference_in_year +  difference_in_months
    return difference

# Função para verificar se a data_transacao é menor ou igual ao vencimento_fatura
def verificar_inadimplencia(row):
    if row['data_transacao'] <= row['vencimento_fatura']:
        return 0
    else:
        return 1

con = db.connect_to_db()
cursor = con.cursor()
colunas = ['codigo_contrato', 'data_inicio_contrato', 'data_de_rescisao','nome_parceiro', 'id_fatura', 
           'vencimento_fatura', 'pagamento_fatura','status_fatura', 'Inadimplentes' ]
results = db.execute_select_in_db(cursor,cohort_inadimplentes)
df_inadimplentes = pd.DataFrame(results, columns=colunas)
print(f'Dataframe criado com sucesso!')

df_inadimplentes = df_inadimplentes[['codigo_contrato', 'data_inicio_contrato', 'data_de_rescisao', 'vencimento_fatura', 'nome_parceiro', 'id_fatura', 'Inadimplentes']]
df_inadimplentes['data_inicio_contrato'] = pd.to_datetime(df_inadimplentes['data_inicio_contrato'])
df_inadimplentes['data_de_rescisao'] = pd.to_datetime(df_inadimplentes['data_de_rescisao'])
df_inadimplentes['vencimento_fatura'] = pd.to_datetime(df_inadimplentes['vencimento_fatura'])

# Aplicar a função às colunas do DataFrame e criar uma nova coluna
df_inadimplentes['transacao'] = df_inadimplentes.apply(lambda row: count_months_passed(row['data_inicio_contrato'], row['vencimento_fatura'] if pd.Timestamp(date.today()) > row['vencimento_fatura'] else date.today() ), axis=1) + 1
print("Aplicar a função às colunas do DataFrame e criar uma nova coluna")

# Filtrando os dados para manter apenas os registros do ano de 2023
df_inadimplentes = df_inadimplentes[df_inadimplentes['data_inicio_contrato'].dt.year == 2023]
print("Filtrando os dados para manter apenas os registros do ano de 2023")

df_inadimplentes['data_transacao'] = df_inadimplentes.apply(lambda row: row['data_inicio_contrato'] + pd.DateOffset(months=row['transacao']) - pd.DateOffset(months= 1), axis=1)

# duplicando as linhas de acordo com a quantidade de transacao
df_inadimplentes = df_inadimplentes.loc[df_inadimplentes.index.repeat(df_inadimplentes['transacao'])].reset_index(drop=True)
print("Duplicando as linhas de acordo com a quantidade de transacao")

# colocando transacao no formato de contagem e repetições
df_inadimplentes['transacao'] = df_inadimplentes.groupby('id_fatura').cumcount() 
print("Colocando transacao no formato de contagem e repetições")

# Criar a nova coluna 'data_de_inicio_mais_transacao_meses'
df_inadimplentes['data_transacao'] = df_inadimplentes.apply(lambda row: row['data_inicio_contrato'] + pd.DateOffset(months=row['transacao']), axis=1)
print("Criar a nova coluna 'data_de_inicio_mais_transacao_meses'")

# Obtém o dia do vencimento_fatura e soma 1
df_inadimplentes['novo_dia_transacao'] = df_inadimplentes['vencimento_fatura'].dt.day + 1
print("Obtém o dia do vencimento_fatura e soma 1")

# Corrige casos onde o novo dia ultrapassa o limite do mês
df_inadimplentes['novo_dia_transacao'] = df_inadimplentes.apply(
    lambda row: min(row['novo_dia_transacao'], pd.Timestamp(row['data_transacao']).days_in_month),
    axis=1
)
print("Corrige casos onde o novo dia ultrapassa o limite do mês")

# Substitui o dia na coluna 'data_transacao' pelo novo_dia_transacao
df_inadimplentes['data_transacao'] = df_inadimplentes.apply(
    lambda row: row['data_transacao'].replace(day=row['novo_dia_transacao']),
    axis=1
)
print("Substituindo o dia na coluna 'data_transacao' pelo novo_dia_transacao")

# Drop da coluna temporária
df_inadimplentes = df_inadimplentes.drop(columns=['novo_dia_transacao'])
print("Deletando a coluna temporária!")

# Aplicar a função à nova coluna
df_inadimplentes['Inadimplentes_Inadim'] = df_inadimplentes.apply(verificar_inadimplencia, axis=1)
print("Função aplicada na nova coluna de Inadimplentes!")

df_inadimplentes = df_inadimplentes[['codigo_contrato', 'id_fatura', 'data_inicio_contrato', 'vencimento_fatura', 'nome_parceiro', 'transacao', 'data_transacao', 'Inadimplentes_Inadim']]

# Calculando o número de meses entre as datas
df_inadimplentes['cohort_mes'] = df_inadimplentes.apply(lambda row: (row['data_transacao'].year - row['data_inicio_contrato'].year) * 12 +
                                       (row['data_transacao'].month - row['data_inicio_contrato'].month) + 1, axis=1)
print("Coluna de cohort gerada!")




CODE_SHEETS_DASH_GERENCIAL_COHORT = os.getenv("CODE_SHEETS_DASH_GERENCIAL_COHORT")
PAGINA_SHEETS = 'df_inadimplentes'

sheet = Sheets(CODE_SHEETS_DASH_GERENCIAL_COHORT)
sheet.clear_and_upload(df_inadimplentes, PAGINA_SHEETS)


