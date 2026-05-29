import pandas as pd
import numpy as np
from google.api_core.exceptions import BadRequest
from google.oauth2 import service_account
from google.cloud import bigquery
from unidecode import unidecode
from decimal import Decimal
from utils.sheets import Sheets
import dotenv
from utils.utils import create_cod_to_merge
from utils import planilhas_transacionais
import utils.mysql_db as db
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
dotenv.load_dotenv()

PATH_TOKEN_JSON_BIGQUERY = os.getenv('PATH_TOKEN_JSON_BIGQUERY')

credentials = service_account.Credentials.from_service_account_file(
    PATH_TOKEN_JSON_BIGQUERY)
client = bigquery.Client(credentials=credentials,
                         project=credentials.project_id)


def criando_df_bigquery(dataset_id):
    # Definir cliente do BigQuery
    global client

    # Referência ao dataset
    dataset_ref = client.dataset(dataset_id)

    # Criar o dataset se não existir
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"  # Escolha a região onde deseja armazenar os dados

    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} criado ou já existente.")
    return client, dataset_id


def criando_tabela_bigquery(client, dataset_id, schema, tabela_id):

    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id}' criada com sucesso.")

    return tabela_id


def upload_bigquery(schema, tabela_id, df, dataset_id, SALVA):

    # Exportar Parquet
    file_path = rf'dash_comercial\data\{SALVA}'
    df.to_parquet(file_path, index=False)

    # df_contratos.to_parquet(file_path, engine='pyarrow', index=False)

    client, dataset_id = criando_df_bigquery(dataset_id)
    tabela_id = criando_tabela_bigquery(client, dataset_id, schema, tabela_id)
    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    try:
        with open(file_path, "rb") as file:
            job = client.load_table_from_file(
                file, tabela_ref, job_config=job_config)
        job.result()
        print("Upload do Parquet concluído com sucesso!")
    except BadRequest as e:
        print("❌ Erro ao enviar para o BigQuery:")
        print(e)
        # Opcional: salvar erro em log ou reformatar dados
    except Exception as e:
        print("❌ Erro inesperado:")
        print(e)


sistema_todos = r"dash_comercial\sql\sistema_todos.sql"
sistema_ativos = r"dash_comercial\sql\sistema_ativos.sql"
sistema_todos_csv = r"dash_comercial\data\sistema_todos.csv"
sistema_ativos_csv = r"dash_comercial\data\sistema_ativos.csv"


COLUMNS_SISTEMA = ['codigo_contrato',
                   'nome_parceiro',
                   'date_inicio_contrato',
                   'meses_duracao_contrato',
                   'valor_aluguel_contrato',
                   'taxa_contrato',
                   'taxa_admin_contrato',
                   'name_status',
                   'nome_produto',
                   'migracao']


def add_coluns_from_sheets(df: pd.DataFrame,  name_df: str) -> pd.DataFrame:
    df_parceiros = planilhas_transacionais.get_parceiros_to_sistema()
    df_desocupado = planilhas_transacionais.get_desocupado()

    print(f'Criando cod_to_merge  {name_df}')
    df['cod_to_merge_parceiros'] = df['nome_parceiro'].apply(
        create_cod_to_merge)
    df['cod_to_merge_desocupado'] = df['codigo_contrato'].apply(
        create_cod_to_merge)

    print(
        f'Passando o codigo_parceiro com base no cod_to_merge de parceiros...  {name_df}')
    df['codigo_parceiro'] = df['cod_to_merge_parceiros'].map(
        df_parceiros.set_index('cod_to_merge')['Cod Parceiro'])

    print(
        f'Passando Tipo_parceiro com base no cod_to_merge de parceiros...  {name_df}')
    df['tipo_parceiro'] = df['cod_to_merge_parceiros'].map(
        df_parceiros.set_index('cod_to_merge')['Tipo de parceiro'])

    print(
        f'Passando data_desocupacaocom base no cod_to_merge de desocupado...  {name_df}')
    df['data_desocupacao'] = df['cod_to_merge_desocupado'].map(
        df_desocupado.set_index('cod_to_merge')['Data de desocupação'])

    print(f'deletando colunas cod_to_merge...  {name_df}')
    del df['cod_to_merge_parceiros']
    del df['cod_to_merge_desocupado']

    return df


def processar_sistema(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    df = add_coluns_from_sheets(df, name_df)

    print(f'Renomeando colunas e passando apenas as que precisso... {name_df}')
    df.rename(columns={'date_inicio_contrato': 'data_inicio_contrato',
                       'nome_parceiro': 'nome_parceiro',
                       'taxa_admin_contrato': 'porcentagem_taxa_administracao',
                       'valor_aluguel_contrato': 'valor_aluguel_contrato',
                       'codigo_contrato': 'codigo_contrato',
                       'codigo_parceiro': 'codigo_parceiro',
                       'data_desocupacao': 'data_desocupacao',
                       'name_status': 'name_status',
                       'meses_duracao_contrato': 'meses_duracao_contrato',
                       'taxa_contrato': 'taxa_contrato',
                       'tipo_parceiro': 'tipo_parceiro'}, inplace=True)

    df['tipo_sistema'] = 'sistema'

    df = df[['codigo_contrato', 'codigo_parceiro', 'nome_parceiro', 'valor_aluguel_contrato', 'taxa_contrato',
             'porcentagem_taxa_administracao', 'name_status', 'data_inicio_contrato',
             'meses_duracao_contrato', 'data_desocupacao', 'tipo_parceiro', 'tipo_sistema', 'nome_produto',
             'migracao']]
    df['meses_duracao_contrato'] = df['meses_duracao_contrato'].fillna(0)
    df['meses_duracao_contrato'] = df['meses_duracao_contrato'].astype(int)

    # df = df[~df['codigo_contrato'].str.startswith('S-')]
    df['migracao'] = df['migracao'].replace('NÃ£o', 'Nao')

    print(
        f'Formatando data_inicio_contrato para o formato desejado... {name_df}')
    df['data_inicio_contrato'] = pd.to_datetime(
        df['data_inicio_contrato']).dt.strftime('%d/%m/%Y')

    return df


con = db.connect_to_db()
cursor = con.cursor()

print('\n\t------>SISTEMA-TODOS<------')
results = db.execute_select_in_db(cursor, sistema_todos)
df_sistema = pd.DataFrame(results, columns=COLUMNS_SISTEMA)
df_sistema = processar_sistema(df_sistema, 'Todos')
df_sistema.to_csv(sistema_todos_csv, index=False)

print('\n\t------>SISTEMA-ATIVOS<------')
results = db.execute_select_in_db(cursor, sistema_ativos)
df_sistema_ativos = pd.DataFrame(results, columns=COLUMNS_SISTEMA)
df_sistema_ativos = processar_sistema(df_sistema_ativos, 'ATIVOS')
df_sistema_ativos.to_csv(sistema_ativos_csv, index=False)


cursor.close()
con.close()


data_cols = [
    "data_inicio_contrato",
    "data_desocupacao"
]

for col in data_cols:
    df_sistema[col] = pd.to_datetime(
        df_sistema[col], format='%d/%m/%Y', errors='coerce')

df_sistema['data_inicio_contrato'] = df_sistema['data_inicio_contrato'].dt.date
df_sistema['data_desocupacao'] = df_sistema['data_desocupacao'].dt.date

# data_cols = ["data_inicio_contrato", "data_desocupacao"]
# df_sistema['data_inicio_contrato'] = pd.to_datetime(
#     df_sistema['data_inicio_contrato'], errors='coerce')
# df_sistema['data_desocupacao'] = pd.to_datetime(
#     df_sistema['data_desocupacao'], errors='coerce')
# df_sistema['data_inicio_contrato'] = df_sistema['data_inicio_contrato'].dt.date
# df_sistema['data_desocupacao'] = df_sistema['data_desocupacao'].dt.date
data_cols = [
    "data_inicio_contrato",
    "data_desocupacao"
]

# for col in data_cols:
#     df_sistema_ativos[col] = pd.to_datetime(
#         df_sistema_ativos[col], errors='coerce')

# df_sistema_ativos['data_desocupacao'] = pd.to_datetime(
#     df_sistema_ativos['data_desocupacao'], errors='coerce')
# df_sistema_ativos['data_desocupacao'] = df_sistema_ativos['data_desocupacao'].dt.strftime(
#     '%Y%m%d')
# df_sistema_ativos['data_desocupacao'] = df_sistema_ativos['data_desocupacao'].fillna(
#     0).astype(int)
# df_sistema_ativos['data_inicio_contrato'] = df_sistema_ativos['data_inicio_contrato'].dt.strftime(
#     '%Y-%m-%d')

data_cols = [
    "data_inicio_contrato",
    "data_desocupacao"
]

for col in data_cols:
    df_sistema_ativos[col] = pd.to_datetime(
        df_sistema_ativos[col],  format='%d/%m/%Y', errors='coerce')

df_sistema_ativos['data_desocupacao'] = pd.to_datetime(
    df_sistema_ativos['data_desocupacao'], errors='coerce')
df_sistema_ativos['data_desocupacao'] = df_sistema_ativos['data_desocupacao'].dt.strftime(
    '%Y%m%d')
df_sistema_ativos['data_desocupacao'] = df_sistema_ativos['data_desocupacao'].fillna(
    0).astype(int)
df_sistema_ativos['data_inicio_contrato'] = df_sistema_ativos['data_inicio_contrato'].dt.strftime(
    '%Y-%m-%d')


df_sistema['valor_aluguel_contrato'] = (df_sistema['valor_aluguel_contrato'].str.replace(
    '.', '', regex=False)   .str.replace(',', '.', regex=False) .astype(float))
df_sistema_ativos['valor_aluguel_contrato'] = (df_sistema_ativos['valor_aluguel_contrato'].str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False).astype(float))


def sistema():
    df = df_sistema.copy()
    tabela_id = "sistema"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("codigo_parceiro", "STRING"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("valor_aluguel_contrato", "FLOAT"),
        bigquery.SchemaField("taxa_contrato", "STRING"),
        bigquery.SchemaField("porcentagem_taxa_administracao", "STRING"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("data_inicio_contrato", "DATE"),
        bigquery.SchemaField("meses_duracao_contrato", "INTEGER"),
        bigquery.SchemaField("data_desocupacao", "DATE"),
        bigquery.SchemaField("tipo_parceiro", "STRING"),
        bigquery.SchemaField("tipo_sistema", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("migracao", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial", 'sistema')


def sistemaAtivos():
    df = df_sistema_ativos.copy()
    tabela_id = "sistema_ativos"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("codigo_parceiro", "STRING"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("valor_aluguel_contrato", "FLOAT"),
        bigquery.SchemaField("taxa_contrato", "STRING"),
        bigquery.SchemaField("porcentagem_taxa_administracao", "STRING"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("data_inicio_contrato", "STRING"),
        bigquery.SchemaField("meses_duracao_contrato", "INTEGER"),
        bigquery.SchemaField("data_desocupacao", "INTEGER"),
        bigquery.SchemaField("tipo_parceiro", "STRING"),
        bigquery.SchemaField("tipo_sistema", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("migracao", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial", 'sistema_ativos')


COLUMNS = ['id_parceiro',
           'nome_parceiro',
           'data_analise',
           'valor_aluguel_analisado',
           'Resultado_Analise_Pretendente',
           'nome_produto']

pretendentes_sem_solidarios = r"dash_comercial/sql/pretendentes_sem_solidarios.sql"

con = db.connect_to_db()
cursor = con.cursor()

results = db.execute_select_in_db(cursor, pretendentes_sem_solidarios)
df_analise = pd.DataFrame(results, columns=COLUMNS)

df_analise['Resultado_Analise_Pretendente'] = df_analise['Resultado_Analise_Pretendente'].apply(
    lambda x: x.encode('latin1').decode('utf8') if isinstance(x, str) else x)

data_cols = [
    "data_analise",

]

for col in data_cols:
    df_analise[col] = pd.to_datetime(
        df_analise[col],  format='%d/%m/%Y', errors='coerce')

df_analise['data_analise'] = df_analise['data_analise'].dt.date

df_analise['valor_aluguel_analisado'] = pd.to_numeric(
    df_analise['valor_aluguel_analisado']
    .astype(str)
    .str.strip()
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False),
    errors='coerce'
)


def pretendentes_sem_solidarios():
    df = df_analise.copy()
    tabela_id = "pretendentes_sem_solidarios"
    schema = [
        bigquery.SchemaField("id_parceiro", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("data_analise", "DATE"),
        bigquery.SchemaField("valor_aluguel_analisado", "FLOAT"),
        bigquery.SchemaField("Resultado_Analise_Pretendente", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'pretendentes_sem_solidarios')


# COLUMNS = {'Código do Contrato': 'codigo_contrato',
#            'Receb.': 'data_recebido',
#            'Envio': 'data_enviado',
#            'Assin.': 'data_assinado',
#            'Captadora': 'captadora',
#            'Valor': 'valor'}

# print('\n\t------>RECEBIDOS ENVIADOS ASSINADOS<------\n')
# df_recb_env_ass = planilhas_transacionais.get_recebidos_enviados_assinados()

# print('Renomeando e pegando apenas colunas que vou utilizar...')
# df_recb_env_ass.rename(columns=COLUMNS, inplace=True)
# df_recb_env_ass = df_recb_env_ass[COLUMNS.values()]

# print('Trativa para a coluna data_recebido, vazio e data_enviado preenchida')
# df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(
#     lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

# print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
# df_recb_env_ass['data_enviado'] = df_recb_env_ass.apply(
#     lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'], axis=1)
# df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(
#     lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)


# # AS VEZES ELAS COLOCAM UM X NA COLUNCA DATA_RECEBIDO
# df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido'] != 'X']


# print('Converter a coluna "data_inicio_contrato" para o formato de data...')
# df_recb_env_ass['data_recebido'] = pd.to_datetime(
#     df_recb_env_ass['data_recebido'], format='%d/%m/%Y %H:%M:%S')

# print('Pegando datas só depois de 2023...')
# df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido']
#                                   >= '2023-01-01']

# print('Criando a coluna ano_mes...')
# df_recb_env_ass['ano_mes'] = df_recb_env_ass['data_recebido'].dt.strftime(
#     '%Y-%m')

# print('Convertendo a coluna "datahora" para o formato data desejado...')
# df_recb_env_ass['data_recebido'] = df_recb_env_ass['data_recebido'].dt.strftime(
#     '%d/%m/%Y')

# print('Ajustando a coluna captadora...')
# df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].fillna('VAZIO')
# df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].str.upper()

# print('Separando dataframe em 3...')
# recebidos = df_recb_env_ass[['codigo_contrato',
#                              'captadora', 'ano_mes', 'data_recebido', 'valor']]
# enviados = df_recb_env_ass[['codigo_contrato',
#                             'captadora', 'ano_mes', 'data_enviado', 'valor']]
# assinados = df_recb_env_ass[['codigo_contrato',
#                              'captadora', 'ano_mes', 'data_assinado', 'valor']]

# print('Mudando o nome da coluna valor...')
# recebidos = recebidos.copy()
# recebidos.rename(columns={'valor': 'valor_recebidos'}, inplace=True)

# enviados = enviados.copy()
# print('Tirando vazios...')
# enviados = enviados[enviados['data_enviado'].str.len() > 1]
# enviados.rename(columns={'valor': 'valor_enviado'}, inplace=True)

# assinados = assinados.copy()
# assinados = assinados[assinados['data_assinado'].str.len() > 1]
# assinados.rename(columns={'valor': 'valor_assinados'}, inplace=True)

# print('Juntando os dados novamente...')
# relacionamento = pd.merge(recebidos, enviados, on=[
#                           'ano_mes', 'captadora', 'codigo_contrato'], how='outer')
# relacionamento = pd.merge(relacionamento, assinados, on=[
#                           'ano_mes', 'captadora', 'codigo_contrato'], how='outer')

COLUMNS = {'Código do Contrato': 'codigo_contrato',
           'Receb.': 'data_recebido',
           'Envio': 'data_enviado',
           'Assin.': 'data_assinado',
           'Captadora': 'captadora',
           'Valor': 'valor'}

print('\n\t------>RECEBIDOS ENVIADOS ASSINADOS<------\n')
df_recb_env_ass = planilhas_transacionais.get_recebidos_enviados_assinados()

print('Renomeando e pegando apenas colunas que vou utilizar...')
df_recb_env_ass.rename(columns=COLUMNS, inplace=True)
df_recb_env_ass = df_recb_env_ass[COLUMNS.values()]

print('Trativa para a coluna data_recebido, vazio e data_enviado preenchida')
df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(
    lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
df_recb_env_ass['data_enviado'] = df_recb_env_ass.apply(
    lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'], axis=1)
df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(
    lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)


# AS VEZES ELAS COLOCAM UM X NA COLUNCA DATA_RECEBIDO
df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido'] != 'X']


print('Converter a coluna "data_inicio_contrato" para o formato de data...')
df_recb_env_ass['data_recebido'] = pd.to_datetime(
    df_recb_env_ass['data_recebido'], format='%d/%m/%Y %H:%M:%S')

print('Pegando datas só depois de 2023...')
df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido']
                                  >= '2023-01-01']

print('Criando a coluna ano_mes...')
df_recb_env_ass['ano_mes'] = df_recb_env_ass['data_recebido'].dt.strftime(
    '%Y-%m')

print('Convertendo a coluna "datahora" para o formato data desejado...')
df_recb_env_ass['data_recebido'] = df_recb_env_ass['data_recebido'].dt.strftime(
    '%d/%m/%Y')

print('Ajustando a coluna captadora...')
df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].fillna('VAZIO')
df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].str.upper()

print('Separando dataframe em 3...')
recebidos = df_recb_env_ass[['codigo_contrato',
                             'captadora', 'ano_mes', 'data_recebido', 'valor']]
enviados = df_recb_env_ass[['codigo_contrato',
                            'captadora', 'ano_mes', 'data_enviado', 'valor']]
assinados = df_recb_env_ass[['codigo_contrato',
                             'captadora', 'ano_mes', 'data_assinado', 'valor']]

print('Mudando o nome da coluna valor...')
recebidos = recebidos.copy()
recebidos.rename(columns={'valor': 'valor_recebidos'}, inplace=True)

enviados = enviados.copy()
print('Tirando vazios...')
enviados = enviados[enviados['data_enviado'].str.len() > 1]
enviados.rename(columns={'valor': 'valor_enviado'}, inplace=True)

assinados = assinados.copy()
assinados = assinados[assinados['data_assinado'].str.len() > 1]
assinados.rename(columns={'valor': 'valor_assinados'}, inplace=True)

print('Juntando os dados novamente...')
rel = pd.merge(recebidos, enviados, on=[
    'ano_mes', 'captadora', 'codigo_contrato'], how='outer')
rel = pd.merge(rel, assinados, on=[
    'ano_mes', 'captadora', 'codigo_contrato'], how='outer')


data_cols = [
    "data_recebido"

]

for col in data_cols:
    rel[col] = pd.to_datetime(
        rel[col],  format='%d/%m/%Y', errors='coerce')

rel['data_recebido'] = rel['data_recebido'].dt.date

rel['data_enviado'] = pd.to_datetime(
    rel['data_enviado'],
    format='%d/%m/%Y %H:%M:%S',
    errors='coerce'
).dt.strftime('%Y-%m-%d')

rel['data_assinado'] = pd.to_datetime(
    rel['data_assinado'],
    format='%d/%m/%Y %H:%M:%S',
    errors='coerce'
).dt.strftime('%Y-%m-%d')


rel['valor_assinados'] = pd.to_numeric(rel['valor_assinados'].astype(str).str.strip().str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False).str.replace('R$', '', regex=False), errors='coerce')
rel['valor_enviado'] = pd.to_numeric(rel['valor_enviado'].astype(str).str.strip().str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False).str.replace('R$', '', regex=False), errors='coerce')
rel['valor_recebidos'] = pd.to_numeric(rel['valor_recebidos'].astype(str).str.strip().str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False).str.replace('R$', '', regex=False), errors='coerce')


def relacionamento_com():
    df = rel.copy()
    tabela_id = "recebidos_enviados_assinados"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("ano_mes", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("valor_recebidos", "FLOAT"),
        bigquery.SchemaField("data_enviado", "DATE"),
        bigquery.SchemaField("valor_enviado", "FLOAT"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("valor_assinados", "FLOAT"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'recebidos_enviados_assinados')


def processar_desocupado():
    print('\n\t------>TRATANDO DADOS DESOCUPADO<------')
    df_desocupado = planilhas_transacionais.get_desocupado()
    print('Renomeando e pegando apenas as colunas do meu interresse...')
    df_desocupado.rename(columns={'Código do contrato': 'codigo_contrato',
                                  'Data de desocupação': 'data_desocupacao'}, inplace=True)
    df_desocupado = df_desocupado[['codigo_contrato', 'data_desocupacao']]

    print('Converter a coluna "data_inicio_contrato" para o formato de data...')
    df_desocupado['data_desocupacao'] = pd.to_datetime(
        df_desocupado['data_desocupacao'], format='%d/%m/%Y')

    print('Pegando datas só depois de 2023...')
    df_desocupado = df_desocupado[df_desocupado['data_desocupacao']
                                  >= '2023-01-01']
    df_desocupado['ano_mes'] = df_desocupado['data_desocupacao'].dt.to_period(
        'M')

    print('Convertendo a coluna "datahora" para o tipo data desejado...')
    df_desocupado['data_desocupacao'] = df_desocupado['data_desocupacao'].dt.strftime(
        '%d/%m/%Y')

    df_desocupado.reset_index(drop=True, inplace=True)
    return df_desocupado


def processar_assinado():
    print('\n\t------>TRATANDO DADOS ASSINADO<------')
    df_assinado = planilhas_transacionais.get_recebidos_enviados_assinados()

    df_assinado.rename(columns={'Código do Contrato': 'codigo_contrato',
                                'Receb.': 'data_recebido',
                                'Envio': 'data_envio',
                                'Assin.': 'data_assinado',
                                'Sistema': 'data_sistema',
                                'Valor': 'valor'}, inplace=True)

    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_assinado['data_envio'] = df_assinado.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_assinado['data_recebido'] = df_assinado.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Converter a coluna "data_inicio_contrato" para o formato de data...')
    df_assinado['data_recebido'] = pd.to_datetime(
        df_assinado['data_recebido'], format='%d/%m/%Y %H:%M:%S')

    print('Pegando datas só depois de 2023...')
    # THIAGO ESSA PARTE NO OUTRO ESTAMOS FAZENDO COM A COLUNA DATA_DESOCUPAÇAO PQ AQUI FAZEMOS COM DATA_RECEBIDOS
    df_assinado = df_assinado[df_assinado['data_recebido'] >= '2023-01-01']
    df_assinado['ano_mes'] = df_assinado['data_recebido'].dt.to_period('M')

    df_assinado = df_assinado[['codigo_contrato',
                               'data_assinado', 'ano_mes', 'valor']]
    return df_assinado


print('\n\t------>ASSINADOS DESOCUPADOS<------\n')
df_desocupado = processar_desocupado()
df_assinado = processar_assinado()

print('\n\nFazendo merge dos dois df...')
relacionamento = pd.merge(df_assinado, df_desocupado,
                          on=['ano_mes', 'codigo_contrato'],
                          how='outer')

relacionamento['ano_mes'] = relacionamento['ano_mes'].astype(str)


def assinados_desocupados_com():
    df = relacionamento.copy()
    tabela_id = "assinados_desocupados"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("ano_mes", "STRING"),
        bigquery.SchemaField("valor", "STRING"),
        bigquery.SchemaField("data_desocupacao", "DATE"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'assinados_desocupados')


# data_cols = [
#     "data_assinado", "data_desocupacao"
# ]

# for col in data_cols:
#     rel[col] = pd.to_datetime(rel[col], errors='coerce')

# rel['data_assinado'] = rel['data_assinado'].dt.date
# rel['data_desocupacao'] = rel['data_desocupacao'].dt.date

# # Transforma ano_mes para formato YYYY-MM-01
# rel["ano_mes"] = rel["ano_mes"].astype(str)
# rel["ano_mes"] = pd.to_datetime(rel["ano_mes"]).dt.strftime("%Y-%m-01")


# def assinados_desocupados_com():
#     df = rel.copy()
#     tabela_id = "assinados_desocupados"
#     schema = [
#         bigquery.SchemaField("codigo_contrato", "STRING"),
#         bigquery.SchemaField("data_assinado", "DATE"),
#         # period[M] será convertido para string 'YYYY-MM'
#         bigquery.SchemaField("ano_mes", "STRING"),
#         bigquery.SchemaField("valor", "STRING"),
#         bigquery.SchemaField("data_desocupacao", "DATE"),
#     ]

#     upload_bigquery(schema, tabela_id, df, "dash_comercial",
#                     'assinados_desocupados')


COLUMNS_ANALISES = ['nome_pretendente', 'documento_pretendente',  'profissao_pretendente', 'renda_pretendente', 'renda_presumida_pretendente', 'score_assertiva_pretendente',
                    'faixa_de_score', 'vinculo_empregaticio', 'resultado_analise_pretendente', 'id_parceiro', 'nome_parceiro', 'data_analise',  'valor_aluguel_analisado']

COLUMNS_CONTRATOS = {'Código do Contrato': 'codigo_contrato',
                     'Locatário': 'Locatario',
                     'Receb.': 'data_recebido',
                     'Envio': 'data_enviado',
                     'Assin.': 'data_assinado',
                     'Sistema': 'data_sistema',
                     'Captadora': 'captadora',
                     'Valor': 'valor'

                     }

sql_file_path = r"dash_comercial/sql/analises.sql"

print('\n\t------>ANALISES<------\n')
con = db.connect_to_db()
cursor = con.cursor()

print('Consumindo os dados do sistema...')
results = db.execute_select_in_db(cursor, sql_file_path)
df_analises = pd.DataFrame(results, columns=COLUMNS_ANALISES)
df_analises = df_analises.drop_duplicates(
    subset=['nome_pretendente', 'resultado_analise_pretendente', 'valor_aluguel_analisado'], keep='first')
df_analises['resultado_analise_pretendente'] = df_analises['resultado_analise_pretendente'].apply(
    lambda x: x.encode('latin1').decode('utf8') if isinstance(x, str) else x)
df_analises['vinculo_empregaticio'] = df_analises['vinculo_empregaticio'].apply(
    lambda x: x.encode('latin1').decode('utf8') if isinstance(x, str) else x)

print('Consumindo os dados da planilha de contratos...')
df_contratos = planilhas_transacionais.get_recebidos_enviados_assinados()

print('Fazendo tratamento dos dados da planilha...')
print('Renomeando e pegando apenas colunas que vou utilizar...')
df_contratos.rename(columns=COLUMNS_CONTRATOS, inplace=True)

df_contratos = df_contratos[COLUMNS_CONTRATOS.values()]

df_contratos = df_contratos.drop_duplicates(
    subset=['codigo_contrato', 'Locatario', 'valor'], keep='first')

df_contratos = df_contratos.iloc[:-1]

print('Trativa para a coluna data_recebido, vazio e data_enviado preenchida')
df_contratos['data_recebido'] = df_contratos.apply(
    lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
df_contratos['data_enviado'] = df_contratos.apply(
    lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'], axis=1)
df_contratos['data_recebido'] = df_contratos.apply(
    lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)


print('Tratativa para tirar da coluna data_recebido, onde tem X NA COLUNCA DATA_RECEBIDO')
df_contratos = df_contratos[df_contratos['data_recebido'] != 'X']

print('Converter a coluna "data_inicio_contrato" para o formato de data...')
df_contratos['data_recebido'] = pd.to_datetime(
    df_contratos['data_recebido'], format='%d/%m/%Y %H:%M:%S')

print('Pegando datas só depois de 2023...')
df_contratos = df_contratos[df_contratos['data_recebido'] >= '2023-01-01']

print('Fazendo um merge entre os df_analises e df_contratos, ligando pelo nome_pretendente e Locatário')
df_merge = pd.merge(df_analises, df_contratos, how='left', left_on=[
                    'nome_pretendente'], right_on=['Locatario'])


cursor.close()
con.close()

df_merge['data_analise'] = pd.to_datetime(
    df_merge['data_analise'],
    format='%d/%m/%Y',
    errors='coerce'
).dt.strftime('%Y-%m-%d')

df_merge['data_recebido'] = pd.to_datetime(
    df_merge['data_recebido'],
    format='%d/%m/%Y %H:%M:%S',
    errors='coerce'
).dt.date

data_cols = [
    "data_enviado", "data_assinado", "data_recebido", "data_sistema"

]

for col in data_cols:
    df_merge[col] = pd.to_datetime(df_merge[col], errors='coerce')
    df_merge[col] = df_merge[col].dt.date

df_merge['renda_pretendente'] = pd.to_numeric(df_merge['renda_pretendente'].astype(
    str).str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
df_merge['renda_presumida_pretendente'] = pd.to_numeric(df_merge['renda_presumida_pretendente'].astype(
    str).str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
df_merge['score_assertiva_pretendente'] = pd.to_numeric(df_merge['score_assertiva_pretendente'].astype(
    str).str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
df_merge['valor_aluguel_analisado'] = pd.to_numeric(df_merge['valor_aluguel_analisado'].astype(
    str).str.strip().str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
df_merge['valor'] = pd.to_numeric(df_merge['valor'].astype(str).str.strip().str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')


def analises_com():
    df = df_merge.copy()
    tabela_id = "analises"
    schema = [
        bigquery.SchemaField("nome_pretendente", "STRING"),
        bigquery.SchemaField("documento_pretendente", "STRING"),
        bigquery.SchemaField("profissao_pretendente", "STRING"),
        bigquery.SchemaField("renda_pretendente", "FLOAT"),
        bigquery.SchemaField("renda_presumida_pretendente", "FLOAT"),
        bigquery.SchemaField("score_assertiva_pretendente", "FLOAT"),
        bigquery.SchemaField("faixa_de_score", "STRING"),
        bigquery.SchemaField("vinculo_empregaticio", "STRING"),
        bigquery.SchemaField("resultado_analise_pretendente", "STRING"),
        bigquery.SchemaField("id_parceiro", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("data_analise", "DATE"),
        bigquery.SchemaField("valor_aluguel_analisado", "FLOAT"),
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("Locatário", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("data_enviado", "DATE"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("data_sistema", "DATE"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("valor", "FLOAT"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial", 'analises')


sistema_ativos_curva_abc_monetario = fr"dash_comercial\sql\sistema_ativos_curva_abc_monetario.sql"
sistema_ativos_curva_abc_numerico = fr"dash_comercial/sql/sistema_ativos_curva_abc_numerico.sql"
sistema_todos_curva_abc_num = fr"dash_comercial/sql/sistema_todos_curva_abc_num.sql"
sistema_todos_curva_abc_mon = fr"dash_comercial/sql/sistema_todos_curva_abc_mon.sql"


COLUMNS_SISTEMA_MON = [
    'nome_parceiro',
    'nome_produto',
    'count_contratos',
    'valor_aluguel',
    'valor_aluguel_acumulado',
    'porcentagem',
    'porcentagem_acumulada',
    'classe']

COLUMNS_SISTEMA_NUM = [
    'nome_parceiro',
    'nome_produto',
    'count_contratos',
    'qtd_acumulado',
    'porcentagem',
    'porcentagem_acumulada',
    'classe']


def processar_sistema_mon(df: pd.DataFrame, name_df: str) -> pd.DataFrame:

    df = df[['nome_parceiro', 'nome_produto', 'count_contratos', 'valor_aluguel',
             'valor_aluguel_acumulado', 'porcentagem', 'porcentagem_acumulada', 'classe']]

    df['porcentagem_vacumulada'] = pd.to_numeric(df['porcentagem_acumulada'])

    pd.options.display.float_format = '{:.2f}'.format

    return df


def processar_sistema_num(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    df = df[['nome_parceiro', 'nome_produto', 'count_contratos', 'qtd_acumulado',
             'porcentagem', 'porcentagem_acumulada', 'classe']]
    df['porcentagem'] = df['porcentagem'].astype(float)
    df['porcentagem_acumulada'] = df['porcentagem_acumulada'].astype(float)
    pd.options.display.float_format = '{:.2f}'.format

    return df


con = db.connect_to_db()
cursor = con.cursor()

print('\n\t------>CURVA-ABC ATIVOS MONETÁRIOS<------')
results = db.execute_select_in_db(cursor, sistema_ativos_curva_abc_monetario)
df_sistema_ativos_mon = pd.DataFrame(results, columns=COLUMNS_SISTEMA_MON)
df_sistema_ativos_mon = processar_sistema_mon(df_sistema_ativos_mon, 'MON')


print('\n\t------>SISTEMA-ATIVOS-NUMERICOS<------')
results = db.execute_select_in_db(cursor, sistema_ativos_curva_abc_numerico)
df_sistema_ativos_num = pd.DataFrame(results, columns=COLUMNS_SISTEMA_NUM)
df_sistema_ativos_num = processar_sistema_num(df_sistema_ativos_num, 'NUM')

print('\n\t------>CURVA-ABC TODOS MONETÁRIOS<------')
results = db.execute_select_in_db(cursor, sistema_todos_curva_abc_mon)
df_sistema_mon = pd.DataFrame(results, columns=COLUMNS_SISTEMA_MON)
df_sistema_mon = processar_sistema_mon(df_sistema_mon, 'MON')


print('\n\t------>SISTEMA-TODOS-NUMERICOS<------')
results = db.execute_select_in_db(cursor, sistema_todos_curva_abc_num)
df_sistema_num = pd.DataFrame(results, columns=COLUMNS_SISTEMA_NUM)
df_sistema_num = processar_sistema_num(df_sistema_num, 'NUM')


cursor.close()
con.close()


def sistema_ativos_mon():
    df = df_sistema_ativos_mon.copy()

    # Converter colunas para Decimal
    df['valor_aluguel'] = df['valor_aluguel'].apply(lambda x: Decimal(x))
    df['valor_aluguel_acumulado'] = df['valor_aluguel_acumulado'].apply(
        lambda x: Decimal(x))

    tabela_id = "sistema_ativos_mon"
    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("count_contratos", "INTEGER"),
        bigquery.SchemaField("valor_aluguel", "NUMERIC"),
        bigquery.SchemaField("valor_aluguel_acumulado", "NUMERIC"),
        bigquery.SchemaField("porcentagem", "STRING"),
        bigquery.SchemaField("porcentagem_acumulada", "STRING"),
        bigquery.SchemaField("classe", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    "Curva_ABC_Monetario_Ativos")


df_sistema_ativos_num['qtd_acumulado'] = pd.to_numeric(
    df_sistema_ativos_num['qtd_acumulado'], errors='coerce').astype('Int64')
df_sistema_mon['valor_aluguel'] = pd.to_numeric(
    df_sistema_mon['valor_aluguel'], errors='coerce').astype('float')
df_sistema_mon['valor_aluguel_acumulado'] = pd.to_numeric(
    df_sistema_mon['valor_aluguel_acumulado'], errors='coerce').astype('float')


def sistema_mon_todos():
    df = df_sistema_mon.copy()
    tabela_id = "sistema_todos_mon"
    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("count_contratos", "INTEGER"),
        bigquery.SchemaField("valor_aluguel", "NUMERIC"),
        bigquery.SchemaField("valor_aluguel_acumulado", "NUMERIC"),
        bigquery.SchemaField("porcentagem", "STRING"),
        bigquery.SchemaField("porcentagem_acumulada", "STRING"),
        bigquery.SchemaField("classe", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'Curva_ABC_Monetario_Todos')


df_sistema_num['qtd_acumulado'] = pd.to_numeric(
    df_sistema_num['qtd_acumulado'], errors='coerce').astype('Int64')


def sistema_num_todos():
    df = df_sistema_num.copy()
    tabela_id = "sistema_todos_num"
    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("count_contratos", "INTEGER"),
        bigquery.SchemaField("qtd_acumulado", "INTEGER"),
        bigquery.SchemaField("porcentagem", "FLOAT"),
        bigquery.SchemaField("porcentagem_acumulada", "FLOAT"),
        bigquery.SchemaField("classe", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'Curva_ABC_Numericos_Todos')


def sistema_ativos_num():
    df = df_sistema_ativos_num.copy()
    tabela_id = "sistema_ativos_num"
    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING"),
        bigquery.SchemaField("count_contratos", "INTEGER"),
        bigquery.SchemaField("qtd_acumulado", "INTEGER"),
        bigquery.SchemaField("porcentagem", "FLOAT"),
        bigquery.SchemaField("porcentagem_acumulada", "FLOAT"),
        bigquery.SchemaField("classe", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_comercial",
                    'Curva_ABC_Numericos_Ativos')


def main_comercial():
    sistema_ativos_mon()
    sistema_ativos_num()
    sistema_mon_todos()
    sistema_num_todos()
    sistema()
    sistemaAtivos()
    analises_com()
    relacionamento_com()
    assinados_desocupados_com()
    pretendentes_sem_solidarios()


if __name__ == "__main__":
    main_comercial()
