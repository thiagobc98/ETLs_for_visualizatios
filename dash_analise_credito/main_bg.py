import dotenv
import pandas as pd
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os
from google.api_core.exceptions import BadRequest
from google.oauth2 import service_account
from google.cloud import bigquery

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Agora deve funcionar a importação do módulo utils
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
    file_path = rf'dash_analise_credito\data\{SALVA}'
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


def main_analise_credito():

    con = db.connect_to_db()
    cursor = con.cursor()

    print("------------- INÍCIO DA ATUALIZAÇÃO --------------")
    results = db.execute_select_in_db(
        cursor, 'dash_analise_credito/sql/analise_de_credito.sql')
    print("Executando o sql de analise_de_credito")
    columns = ['nome_pretendente',
               'documento_pretendente',
               'profissao_pretendente',
               'renda_pretendente',
               'renda_presumida_pretendente',
               'score_assertiva_pretendente',
               'faixa_de_score',
               'vinculo_empregaticio',
               'Resultado_Analise_Pretendente',
               'id_parceiro',
               'nome_parceiro',
               'data_analise',
               'valor_aluguel_analisado'
               ]

    df_pretendentes = pd.DataFrame(results, columns=columns)
    print("Gravando os dados e gerando um dataframe df_pretendentes que foram retornados pelo sql de analise_de_credito")

    results = db.execute_select_in_db(
        cursor, 'dash_analise_credito/sql/parceiros.sql')
    print("Executando o sql de parceiros")

    columns = ['codigo_contrato', 'id_parceiro',
               'nome_parceiro', 'date_inicio_contrato', 'name_status']
    df_parceiros = pd.DataFrame(results, columns=columns)
    print("Gravando os dados e gerando um dataframe df_parceiros que foram retornados pelo sql de parceiros")

    df_pretendentes['renda_pretendente'] = df_pretendentes['renda_pretendente'].astype(
        float)

    df_pretendentes['renda_presumida_pretendente'] = df_pretendentes['renda_presumida_pretendente'].astype(
        float)

    df_pretendentes['valor_aluguel_analisado'] = df_pretendentes['valor_aluguel_analisado'].str.replace(
        '.', '', regex=False)  # remove pontos de milhar
    df_pretendentes['valor_aluguel_analisado'] = df_pretendentes['valor_aluguel_analisado'].str.replace(
        ',', '.', regex=False)  # troca vírgula por ponto
    df_pretendentes['valor_aluguel_analisado'] = df_pretendentes['valor_aluguel_analisado'].astype(
        float)

    df_pretendentes['data_analise'] = pd.to_datetime(
        df_pretendentes['data_analise'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

    tabela_id = "Parceiros"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("id_parceiro", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("date_inicio_contrato", "DATE"),
        bigquery.SchemaField("name_status", "STRING")
    ]

    upload_bigquery(schema, tabela_id, df_parceiros,
                    "dash_analise_credito", 'Parceiros')

    tabela_id = "Pretendentes"
    schema = [
        bigquery.SchemaField("nome_pretendente", "STRING"),
        bigquery.SchemaField("documento_pretendente", "STRING"),
        bigquery.SchemaField("profissao_pretendente", "STRING"),
        bigquery.SchemaField("renda_pretendente", "FLOAT"),
        bigquery.SchemaField("renda_presumida_pretendente", "FLOAT"),
        bigquery.SchemaField("faixa_de_score", "STRING"),
        bigquery.SchemaField("vinculo_empregaticio", "STRING"),
        bigquery.SchemaField("Resultado_Analise_Pretendente", "STRING"),
        bigquery.SchemaField("id_parceiro", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("data_analise", "DATE"),
        bigquery.SchemaField("valor_aluguel_analisado", "FLOAT")
    ]

    upload_bigquery(schema, tabela_id, df_pretendentes,
                    "dash_analise_credito", 'Pretendentes')

    print("------------------- ATUALIZADO ----------------")


if __name__ == "__main__":
    main_analise_credito()
