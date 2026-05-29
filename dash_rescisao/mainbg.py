import pandas as pd
import dotenv
from unidecode import unidecode
from utils.sheets import Sheets
import os
from google.cloud import bigquery
from google.oauth2 import service_account


dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")
CODE_SHEETS_DASH_RESCISAO = os.getenv("CODE_SHEETS_DASH_RESCISAO")
PAGINA_SHEETS = 'DEVOLUCAO_CHAVES'


def verifica_envio_juridico(valor):
    if valor == 'Jurídico':
        return 1
    else:
        return 0


def verifica_envio_unidade(valor):
    if valor == 'Unidade':
        return 1
    else:
        return 0


def verifica_envio_juridico_unidade(valor):
    if valor == 'Jurídico/Unidade':
        return 1
    else:
        return 0


def verifica_envio_para_rescisao(valor):
    if pd.notna(valor):  # Verifica se o valor não é NaN
        try:
            pd.to_datetime(valor, format='%d/%m/%Y')
            return 1
        except ValueError:
            pass
    return 0


def main_recisao():
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('DEVOLUCAO_CHAVES')
    df_desocupado = pd.DataFrame(data[1:], columns=data[0])

    print('Cortando dataframe na linhda 217...')
    # Só usar depois da linhas 219 planilha (aqui fica 217)
    df_desocupado = df_desocupado[217:]
    # df_desocupado.reset_index(drop=True, inplace=True)

    df_desocupado = df_desocupado.rename(
        columns={'Motivo/Tipo de Rescisão': 'Motivo_da_devolucao'})

    print('Tirando linhas vazios...')
    df_desocupado = df_desocupado[df_desocupado['Código do contrato'].str.len(
    ) > 1]

    def format_column_name(column_name):
        column_name = unidecode(column_name)  # Remove acentos
        column_name = column_name.lower()  # Converte para minúsculas
        column_name = column_name.replace(' ', '_')  # Substitui espaços por _
        column_name = column_name.replace('-', '_')  # substitui - por _
        return column_name

    print('Renomeando as colunas...')
    df_desocupado.columns = [format_column_name(
        col) for col in df_desocupado.columns]

    print('Pegando apenas as colunas que vou usar...')
    df_desocupado = df_desocupado[['codigo_do_contrato',
                                   'data_de_desocupacao',
                                   'tipo_de_seguro',
                                   'documento_de_rescisao_enviado',
                                   'motivo_da_devolucao',
                                   'unidade_captadora',
                                   'valor_da_multa',
                                   'valor_da_administradora',
                                   'status_financeira_na_devolucao_da_posse',
                                   'ultimo_boleto_de_aluguel_quitado',
                                   'data_que_o_contrato_foi_pausado',
                                   'data_de_envio_do_link_pela_imobiliaria',
                                   'data_do_envio_da_rescisao']]

    print("Tratando Valores na coluna 'valor_multa' e 'valor_da_administradora'...")
    df_desocupado['valor_da_multa'] = df_desocupado['valor_da_multa'].replace(
        '-', None).str.replace('R$', '').str.replace(' ', '')
    df_desocupado['valor_da_administradora'] = df_desocupado['valor_da_administradora'].replace(
        '-', None).str.replace('R$', '').str.replace(' ', '')

    # Crie a nova coluna usando a função apply
    df_desocupado['enviado_para_rescisao'] = df_desocupado['data_do_envio_da_rescisao'].apply(
        lambda x: verifica_envio_para_rescisao(x))
    df_desocupado['enviado_para_juridico'] = df_desocupado['data_do_envio_da_rescisao'].apply(
        lambda x: verifica_envio_juridico(x))
    df_desocupado['enviado_para_unidade'] = df_desocupado['data_do_envio_da_rescisao'].apply(
        lambda x: verifica_envio_unidade(x))
    df_desocupado['enviado_para_juridico_unidade'] = df_desocupado['data_do_envio_da_rescisao'].apply(
        lambda x: verifica_envio_juridico_unidade(x))

    return df_desocupado


df_desocupado = main_recisao()

df_desocupado['codigo_do_contrato'] = df_desocupado['codigo_do_contrato'].replace(
    "17/10/2024 11:39:27", None)

df_desocupado['data_de_desocupacao'] = pd.to_datetime(
    df_desocupado['data_de_desocupacao'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
df_desocupado['data_de_envio_do_link_pela_imobiliaria'] = pd.to_datetime(
    df_desocupado['data_de_envio_do_link_pela_imobiliaria'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
df_desocupado['data_do_envio_da_rescisao'] = pd.to_datetime(
    df_desocupado['data_do_envio_da_rescisao'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
df_desocupado['data_que_o_contrato_foi_pausado'] = pd.to_datetime(
    df_desocupado['data_que_o_contrato_foi_pausado'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

df_desocupado['valor_da_multa'] = pd.to_numeric(df_desocupado['valor_da_multa'].str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
df_desocupado['valor_da_administradora'] = pd.to_numeric(df_desocupado['valor_da_administradora'].str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

PATH_TOKEN_JSON_BIGQUERY = os.getenv('PATH_TOKEN_JSON_BIGQUERY')

credentials = service_account.Credentials.from_service_account_file(
    PATH_TOKEN_JSON_BIGQUERY)
client = bigquery.Client(credentials=credentials,
                         project=credentials.project_id)


def criando_df_bigquery():
    # Definir cliente do BigQuery
    global client
    # Nome do dataset
    dataset_id = "dash_rescisao"

    # Referência ao dataset
    dataset_ref = client.dataset(dataset_id)

    # Criar o dataset se não existir
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"  # Escolha a região onde deseja armazenar os dados

    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} criado ou já existente.")
    return client, dataset_id


def criando_tabela_bigquery(client, dataset_id):

    # Definir o esquema da tabela (Exemplo com 2 colunas)
    schema = [
        bigquery.SchemaField("codigo_do_contrato", "STRING"),
        bigquery.SchemaField("data_de_desocupacao", "STRING"),
        bigquery.SchemaField("tipo_de_seguro", "STRING"),
        bigquery.SchemaField("documento_de_rescisao_enviado", "STRING"),
        bigquery.SchemaField("motivo_da_devolucao", "STRING"),
        bigquery.SchemaField("unidade_captadora", "STRING"),
        bigquery.SchemaField("valor_da_multa", "FLOAT"),
        bigquery.SchemaField("valor_da_administradora", "FLOAT"),
        bigquery.SchemaField(
            "status_financeira_na_devolucao_da_posse", "STRING"),
        bigquery.SchemaField("ultimo_boleto_de_aluguel_quitado", "STRING"),
        bigquery.SchemaField("data_que_o_contrato_foi_pausado", "STRING"),
        bigquery.SchemaField(
            "data_de_envio_do_link_pela_imobiliaria", "STRING"),
        bigquery.SchemaField("data_do_envio_da_rescisao", "STRING"),
        bigquery.SchemaField("enviado_para_rescisao", "INTEGER"),
        bigquery.SchemaField("enviado_para_juridico", "INTEGER"),
        bigquery.SchemaField("enviado_para_unidade", "INTEGER"),
        bigquery.SchemaField("enviado_para_juridico_unidade", "INTEGER")


    ]

    tabela_id = "rescisao"
    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id}' criada com sucesso.")

    return tabela_id


def upload_bigquery():
    df = df_desocupado

    df.to_parquet(r'dash_rescisao/data/dados.parquet',
                  engine='pyarrow', index=False)

    print(df.dtypes)

    file_path = r'dash_rescisao/data/dados.parquet'
    client, dataset_id = criando_df_bigquery()
    tabela_id = criando_tabela_bigquery(client, dataset_id)
    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    with open(file_path, "rb") as file:
        job = client.load_table_from_file(
            file, tabela_ref, job_config=job_config)

    job.result()
    print("Upload do Parquet concluído com sucesso!")


if __name__ == "__main__":
    upload_bigquery()
