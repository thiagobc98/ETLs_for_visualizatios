from google.api_core.exceptions import BadRequest
from google.oauth2 import service_account
from google.cloud import bigquery
from workalendar.america import Brazil
import dotenv
import numpy as np
from unidecode import unidecode
import pandas as pd
from utils.sheets import Sheets
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
    file_path = rf'C:\Users\Julio Lage\Documents\GitHub\cloud-and-data-team\dash_gerencial\data\{SALVA}'
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


CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")
sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
data = sheet.get_planilha('COBRANCA_AMIGAVEL')
df_co_amigavel = pd.DataFrame(data[1:], columns=data[0])

print('Removendo linhas sem contratos...')
df_co_amigavel = df_co_amigavel[df_co_amigavel['Contrato'] != '']


print('Removendo linhas sem 1o_lemb...')
df_co_amigavel = df_co_amigavel[df_co_amigavel['1º Lemb'].str.strip() != '']


print('Padronizando colunas...')


def format_column_name(column_name):
    column_name = unidecode(column_name)  # Remove acentos
    column_name = column_name.lower()  # Converte para minúsculas
    column_name = column_name.replace(' ', '_')  # Substitui espaços por _
    return column_name


df_co_amigavel.columns = [format_column_name(
    col) for col in df_co_amigavel.columns]

print('Rename nas colunas...')
rename_columns = {'contrato': 'codigo_contrato',
                  'locatario': 'nome_locatario',
                  'x': 'reincidencia',
                  '1o_boleto?': '1o_boleto',
                  'situacao_da_cobranca': 'observacao_de_cobranca',
                  '5o_lembr': '5o_lemb',
                  'valor_total_do(s)_boleto(s)_em_aberto': 'valor_total_boleto_em_aberto',
                  'data_de_vencimento_do_boleto': 'data_de_vencimento',
                  'data_de_previsao_de_pagamento_(acordo)': 'data_de_previsao_de_pagamento_acordo'}

df_co_amigavel.rename(columns=rename_columns, inplace=True)


print(' Padronizando o formato das datas na coluna data_de_vencimento...')


def padronizar_data(data):
    # Tenta analisar a data no formato 'd/m/yyyy'
    try:
        data_formatada = pd.to_datetime(data, format='%d/%m/%Y')
    # Se não conseguir, tenta analisar no formato 'dd/mm/yyyy'
    except ValueError:
        data_formatada = pd.to_datetime(data, format='%d/%m/%Y')

    # Formata a data no formato 'dd/mm/yyyy'
    return data_formatada.strftime('%d/%m/%Y')


# Aplicar a função de padronização à coluna 'data'
# df_co_amigavel['data_de_vencimento'] = df_co_amigavel['data_de_vencimento'].apply(padronizar_data)
df_co_amigavel['data_de_vencimento'] = pd.to_datetime(
    df_co_amigavel['data_de_vencimento'], format='%d/%m/%Y', errors='coerce')

print('Rename canal...')
df_co_amigavel.columns.values[11] = '1o_canal'
df_co_amigavel.columns.values[13] = '2o_canal'
df_co_amigavel.columns.values[15] = '3o_canal'
df_co_amigavel.columns.values[17] = '4o_canal'
df_co_amigavel.columns.values[19] = '5o_canal'
df_co_amigavel.columns.values[21] = '6o_canal'

# Substituir 'Preencher' na coluna '1o_canal' pelo valor correspondente na coluna '2o_canal'
df_co_amigavel['1o_canal'] = np.where(df_co_amigavel['1o_canal'].str.strip(
) == 'Preencher', df_co_amigavel['2o_canal'], df_co_amigavel['1o_canal'])

df_co_amigavel['sistema'] = df_co_amigavel['sistema'].str.strip().replace(
    '', 'UP')

print('Drop nas coluans...')
df_co_amigavel.drop(['link_consulta_cadastral', 'observacao_de_cobranca',
                    'observacoes_de_acordo'], axis=1, inplace=True)

print('Tratando reincidencia...')
df_co_amigavel['reincidencia'] = df_co_amigavel['reincidencia'].str.extract(
    '(\d+)')

print('Tratando valor_total_boleto_em_aberto...')
df_co_amigavel['valor_total_boleto_em_aberto'] = df_co_amigavel['valor_total_boleto_em_aberto'].str.replace(
    'R$', '').str.strip()

# Substituir valores vazios ('') por 'Não'
df_co_amigavel['fraude'] = df_co_amigavel['fraude'].str.strip().replace(
    '', 'Não')

# Substituir valores '-' por 'Não'
df_co_amigavel['fraude'] = df_co_amigavel['fraude'].str.strip().replace(
    '-', 'Não')


def processar_coluna_lemb(df, coluna_lemb):
    df[coluna_lemb] = df[coluna_lemb].str.strip().replace('', '01/01/2000')
    df[coluna_lemb] = df[coluna_lemb].str.strip().replace('pago', '01/01/2000')


colunas_lemb = ['2o_lemb', '3o_lemb', '4o_lemb', '5o_lemb', '6o_lemb']

for coluna in colunas_lemb:
    processar_coluna_lemb(df_co_amigavel, coluna)

df_co_amigavel['data_de_pagamento'] = df_co_amigavel['data_de_pagamento'].str.strip(
).replace('', 'em aberto')
df_co_amigavel['data_de_pagamento'] = df_co_amigavel['data_de_pagamento'].str.strip(
).replace('em aberto', '')


df_co_amigavel['data_repasse_extrajudicial'] = df_co_amigavel['data_repasse_extrajudicial'].str.strip(
).replace('', '01/01/2000')

columns_extrajudicial = ['sistema', 'seguro', 'contrato', 'locatario ', 'Locatário 2', 'fraude', 'telefone', 'contato', 'data_ligacao', 'retornou_ligacao', 'data_whatsapp', 'retornou_whatsapp',
                         'data_carta', 'retornou_carta', 'negativacao_do_locatario', 'boletos_em_aberto', 'valor_boleto', 'observacoes', 'acordo_foi_firmado', 'data_acordo', 'valor_recuperado', 'chaves', 'inadimplentes']

data = sheet.get_planilha('COBRANCA_JUDICIAIS')
df_co_judiciais = pd.DataFrame(data[1:], columns=columns_extrajudicial)

df_co_judiciais.drop(columns='Locatário 2', inplace=True)

# Substituir espaços em branco e strings vazias por NaN
df_co_judiciais['contrato'].replace({'': pd.NA, ' ': pd.NA}, inplace=True)
df_co_judiciais.dropna(subset=['contrato'], inplace=True)


df_co_judiciais['fraude'] = df_co_judiciais['fraude'].apply(
    lambda x: 'Não' if pd.isnull(x) or x.strip() == '' else x)

df_co_judiciais['data_ligacao'] = df_co_judiciais['data_ligacao'].replace(
    '-', '')
df_co_judiciais['retornou_ligacao'] = df_co_judiciais['retornou_ligacao'].replace(
    '-', '')
df_co_judiciais['data_whatsapp'] = df_co_judiciais['data_whatsapp'].replace(
    '-', '')
df_co_judiciais['retorno_whatsapp'] = df_co_judiciais['retornou_whatsapp'].replace(
    '-', '')
df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace('-', '')
df_co_judiciais['retornou_carta'] = df_co_judiciais['retornou_carta'].replace(
    '-', '')
df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace(
    'Não enviada', '')
df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace(
    'Nâo enviada ', '')
df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace(
    'Não enviada ', '')


df_co_judiciais['boletos_em_aberto'] = df_co_judiciais['boletos_em_aberto'].replace(
    '-', '')

df_co_judiciais.columns = df_co_judiciais.columns.str.strip()

datas = {"data_ligacao", "data_whatsapp", "data_carta", "data_acordo"}

for date in datas:
    df_co_judiciais[date] = pd.to_datetime(
        df_co_judiciais[date], format='%d/%m/%Y',  errors='coerce')
    df_co_judiciais[date] = df_co_judiciais[date].dt.strftime('%Y-%m-%d')

# Corrigindo valor_boleto
df_co_judiciais['valor_boleto'] = (
    df_co_judiciais['valor_boleto']
    .fillna('0')
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .str.replace(' ', '', regex=False)  # remove espaços indesejados
    .replace('', '0')
    .str.replace('..', '.', regex=False)  # substitui dois pontos por um
    .str.replace('R$', '', regex=False)  # remove 'R$'
)

# Converte para float, substituindo valores inválidos por NaN
df_co_judiciais['valor_boleto'] = pd.to_numeric(
    df_co_judiciais['valor_boleto'], errors='coerce')

# Substitui NaN por 0
df_co_judiciais['valor_boleto'] = df_co_judiciais['valor_boleto'].fillna(0.0)


# Corrigindo valor_recuperado
df_co_judiciais['valor_recuperado'] = (
    df_co_judiciais['valor_recuperado']
    .fillna('0')
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .str.replace(' ', '', regex=False)  # remove espaços indesejados
    .replace('', '0')
    .str.replace('..', '.', regex=False)  # substitui dois pontos por um
    .str.replace('R$', '', regex=False)  # remove 'R$'
    .astype(float)
)


def judiciais():
    df = df_co_judiciais.copy()
    tabela_id = "judiciais"

    schema = [
        bigquery.SchemaField("sistema", "STRING"),
        bigquery.SchemaField("seguro", "STRING"),
        bigquery.SchemaField("contrato", "STRING"),
        bigquery.SchemaField("locatario", "STRING"),
        bigquery.SchemaField("fraude", "STRING"),
        bigquery.SchemaField("telefone", "STRING"),
        bigquery.SchemaField("contato", "STRING"),
        bigquery.SchemaField("data_ligacao", "DATE"),
        bigquery.SchemaField("retornou_ligacao", "STRING"),
        bigquery.SchemaField("data_whatsapp", "DATE"),
        bigquery.SchemaField("retornou_whatsapp", "STRING"),
        bigquery.SchemaField("data_carta", "DATE"),
        bigquery.SchemaField("retornou_carta", "STRING"),
        bigquery.SchemaField("negativacao_do_locatario", "STRING"),
        bigquery.SchemaField("boletos_em_aberto", "STRING"),
        bigquery.SchemaField("valor_boleto", "INTEGER"),
        bigquery.SchemaField("observacoes", "STRING"),
        bigquery.SchemaField("acordo_foi_firmado", "STRING"),
        bigquery.SchemaField("data_acordo", "DATE"),
        bigquery.SchemaField("valor_recuperado", "INTEGER"),
        bigquery.SchemaField("chaves", "STRING"),
        bigquery.SchemaField("inadimplentes", "STRING"),
        bigquery.SchemaField("retorno_whatsapp", "STRING"),
    ]

    # Aqui você deve verificar a tabela e garantir que o esquema corresponda ou recriar a tabela
    upload_bigquery(schema, tabela_id, df, "dash_cobrancas", 'judiciais')


datas = {"1o_lemb", "2o_lemb", "4o_lemb", "5o_lemb", "6o_lemb", "data_de_previsao_de_pagamento_acordo",
         "data_de_pagamento", "data_repasse_extrajudicial", "data_de_vencimento"}

for date in datas:
    df_co_amigavel[date] = pd.to_datetime(
        df_co_amigavel[date], format='%d/%m/%Y',  errors='coerce')
    df_co_amigavel[date] = df_co_amigavel[date].dt.strftime('%Y-%m-%d')

# Corrigindo valor_total_boleto_em_aberto
df_co_amigavel['valor_total_boleto_em_aberto'] = (
    df_co_amigavel['valor_total_boleto_em_aberto']
    .fillna('0')
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .str.replace(' ', '', regex=False)  # remove espaços indesejados
    .replace('', '0')
    .str.replace('..', '.', regex=False)  # substitui dois pontos por um
    .str.replace('R$', '', regex=False)  # remove 'R$'
    .astype(float)
)

# Corrigindo valor_recuperado
df_co_amigavel['valor_recuperado'] = (
    df_co_amigavel['valor_recuperado']
    .fillna('0')
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .str.replace(' ', '', regex=False)  # remove espaços indesejados
    .replace('', '0')
    .str.replace('..', '.', regex=False)  # substitui dois pontos por um
    .str.replace('R$', '', regex=False)  # remove 'R$'
    .astype(float)
)


def amigavel():
    df = df_co_amigavel.copy()
    tabela_id = "amigavel"

    schema = [
        bigquery.SchemaField("sistema", "STRING"),
        bigquery.SchemaField("fraude", "STRING"),
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("nome_locatario", "STRING"),
        bigquery.SchemaField("reincidencia", "STRING"),
        bigquery.SchemaField("1o_boleto", "STRING"),
        bigquery.SchemaField("valor_total_boleto_em_aberto", "STRING"),
        bigquery.SchemaField("data_de_vencimento", "DATE"),
        bigquery.SchemaField("1o_lemb", "STRING"),
        bigquery.SchemaField("1o_canal", "STRING"),
        bigquery.SchemaField("2o_lemb", "STRING"),
        bigquery.SchemaField("2o_canal", "STRING"),
        bigquery.SchemaField("3o_lemb", "STRING"),
        bigquery.SchemaField("3o_canal", "STRING"),
        bigquery.SchemaField("4o_lemb", "STRING"),
        bigquery.SchemaField("4o_canal", "STRING"),
        bigquery.SchemaField("5o_lemb", "STRING"),
        bigquery.SchemaField("5o_canal", "STRING"),
        bigquery.SchemaField("6o_lemb", "STRING"),
        bigquery.SchemaField("6o_canal", "STRING"),
        bigquery.SchemaField("data_de_previsao_de_pagamento_acordo", "STRING"),
        bigquery.SchemaField("data_de_pagamento", "STRING"),
        bigquery.SchemaField("valor_recuperado", "STRING"),
        bigquery.SchemaField("devolucao_de_chaves", "STRING"),
        bigquery.SchemaField("data_repasse_extrajudicial", "STRING"),
        bigquery.SchemaField("passar_para_extrajudicial", "STRING"),
    ]

    # Aqui você deve verificar a tabela e garantir que o esquema corresponda ou recriar a tabela
    upload_bigquery(schema, tabela_id, df, "dash_cobrancas", 'amigavel')


def main_cobrancas():
    amigavel()
    judiciais()


if __name__ == "__main__":
    main_cobrancas()
