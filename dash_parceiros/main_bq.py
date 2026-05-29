from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import BadRequest
import utils.mysql_db as db
import dotenv
import os
import pandas as pd
from utils.sheets import Sheets
dotenv.load_dotenv()
COLUMNS_CONTRATOS = ['id_contrato',
                     'codigo_contrato',
                     'nome_parceiro',
                     'date_inicio_contrato',
                     'data_pausa_contrato',
                     'meses_duracao_contrato',
                     'valor_aluguel_contrato',
                     'name_status',
                     'migracao',
                     'email_parceiro',
                     'rua_end',
                     'numero_end',
                     'complemento_end',
                     'bairro_end',
                     'cidade_end',
                     'estado_end',
                     'cep_end']

COLUMNS_FATURAS = ['fk_id_contrato',
                   'id_fatura',
                   'vencimento_fatura',
                   'pagamento_fatura',
                   'status_fatura']


con = db.connect_to_db()
cursor = con.cursor()

print('\n\t------>SISTEMA-CONTRATOS<------')
results = db.execute_select_in_db(
    cursor, r'C:\Users/thico\Desktop\Dev-Data\Git-Hub\dash_parceiros\sql\sistema_contratos.sql')
df_contratos = pd.DataFrame(results, columns=COLUMNS_CONTRATOS)

print('\n\t------>SISTEMA-FATURAS<------')
results = db.execute_select_in_db(
    cursor, r'C:\Users\thico\Desktop\Dev-Data\Git-Hub\dash_parceiros\sql\sistema_faturas.sql')
df_faturas = pd.DataFrame(results, columns=COLUMNS_FATURAS)

df_merge = df_contratos.merge(
    df_faturas, left_on='id_contrato', right_on='fk_id_contrato', how='left')


emails_parceiros = {
    'ABRYLAR NEGOCIOS IMOBILIARIOS LTDA': 'taliagnes@gmail.com',
    'ABRYLAR - STACK IMOVEIS - SOLUCOES IMOBILIARIAS LTDA': 'taliagnes@gmail.com',
    'IMOVEIS BRUNO LARA LTDA': 'stella.ppa24@gmail.com',
    'GOLDEN IMÓVEIS LTDA': 'alexmilke75@gmail.com'
}


def tratar_email_parceiro(df):
    df_copy = df.copy()
    df_copy['email_parceiro'] = df_copy.apply(
        lambda row: emails_parceiros.get(
            row['nome_parceiro'], row['email_parceiro']),
        axis=1
    )
    return df_copy


df_merge = tratar_email_parceiro(df_merge)

df_merge['valor_aluguel_contrato'] = pd.to_numeric(df_merge['valor_aluguel_contrato'].astype(
    str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

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
    file_path = fr'C:\Users\thico\Desktop\Dev-Data\Git-Hub\dash_parceiros\{SALVA}'
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


def sistema():
    df = df_merge.copy()
    tabela_id = "sistema"
    schema = [
        bigquery.SchemaField("id_contrato", "INTEGER"),
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("date_inicio_contrato", "STRING"),
        bigquery.SchemaField("data_pausa_contrato", "STRING"),
        bigquery.SchemaField("meses_duracao_contrato", "INTEGER"),
        bigquery.SchemaField("valor_aluguel_contrato", "FLOAT"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("migracao", "STRING"),
        bigquery.SchemaField("email_parceiro", "STRING"),
        bigquery.SchemaField("rua_end", "STRING"),
        bigquery.SchemaField("numero_end", "STRING"),
        bigquery.SchemaField("complemento_end", "STRING"),
        bigquery.SchemaField("bairro_end", "STRING"),
        bigquery.SchemaField("cidade_end", "STRING"),
        bigquery.SchemaField("estado_end", "STRING"),
        bigquery.SchemaField("cep_end", "STRING"),
        bigquery.SchemaField("fk_id_contrato", "INTEGER"),
        bigquery.SchemaField("id_fatura", "INTEGER"),
        bigquery.SchemaField("vencimento_fatura", "STRING"),
        bigquery.SchemaField("pagamento_fatura", "STRING"),
        bigquery.SchemaField("status_fatura", "STRING")

    ]

    upload_bigquery(schema, tabela_id, df, "dash_parceiros", 'sistema')


def upload_todos_sistemas():
    sistema()


upload_todos_sistemas()
