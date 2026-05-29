from google.api_core.exceptions import BadRequest
from google.oauth2 import service_account
from google.cloud import bigquery
from unidecode import unidecode
from workalendar.america import Brazil
from utils.sheets import Sheets
import sla_horas
import fluxo_contratos
import pandas as pd
import datetime
import dotenv
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
    file_path = rf'dash_contratos\data\{SALVA}'
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


def time_start_pipeline():
    start_time = datetime.datetime.now()
    print("\n\nInício do pipeline:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return start_time


def time_end_pipeline(start_time):
    end_time = datetime.datetime.now()
    print("Fim do pipeline:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    elapsed_time = end_time - start_time
    print("Tempo decorrido:", str(elapsed_time).split(".")[0])


# time_start_time = time_start_pipeline()
df_contratos = fluxo_contratos.main()
print('\n')
df_sla_horas = sla_horas.gerando_sla_horas(df_contratos)

df_filtrado = df_sla_horas[df_sla_horas['data_recebido'] >= '2023-01-01']
print(df_contratos)

# Corrigindo valor_aluguel
df_contratos['valor_aluguel'] = (
    df_contratos['valor_aluguel']
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
df_contratos['valor_aluguel'] = pd.to_numeric(
    df_contratos['valor_aluguel'], errors='coerce')

# Substitui NaN por 0
df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].fillna(0.0)

data_cols = [
    "data_recebido",
    "data_envio",
    "data_assinado",
    "data_sistema",
    "data_primeiro_boleto"
]

for col in data_cols:
    df_contratos[col] = pd.to_datetime(
        df_contratos[col], dayfirst=True, errors='coerce').dt.date


def contrato():
    df = df_contratos.copy()
    tabela_id = "contrato"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("data_envio", "DATE"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("data_sistema", "DATE"),
        bigquery.SchemaField("data_primeiro_boleto", "DATE"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("valor_aluguel", "FLOAT"),
        bigquery.SchemaField("contrato_cancelado", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_contrato", 'contrato')


df_filtrado["data_recebido"] = pd.to_datetime(
    df_filtrado["data_recebido"], dayfirst=True, errors='coerce').dt.date


def contrato_filtrados():
    df = df_filtrado.copy()
    tabela_id = "contrato_filtrado"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("sla_recebido_enviado", "FLOAT"),
        bigquery.SchemaField("sla_enviado_assinado", "FLOAT"),
        bigquery.SchemaField("sla_assinado_sistema", "FLOAT"),
        bigquery.SchemaField("sla_sistema_boleto", "FLOAT"),
        bigquery.SchemaField("sla_recebido_enviado_corridas", "FLOAT"),
        bigquery.SchemaField("sla_enviado_assinado_corridas", "FLOAT"),
        bigquery.SchemaField("sla_assinado_sistema_corridas", "FLOAT"),
        bigquery.SchemaField("sla_sistema_boleto_corridas", "FLOAT"),
    ]

    upload_bigquery(schema, tabela_id, df,
                    "dash_contrato", "contrato_filtrado")


def main_contratos():
    contrato_filtrados()
    contrato()


if __name__ == "__main__":
    main_contratos()
