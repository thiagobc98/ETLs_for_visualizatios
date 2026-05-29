import dotenv
import pandas as pd
import datetime
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os
from google.cloud import bigquery
from google.oauth2 import service_account

PATH_TOKEN_JSON_BIGQUERY = os.getenv('PATH_TOKEN_JSON_BIGQUERY')

credentials = service_account.Credentials.from_service_account_file(
    PATH_TOKEN_JSON_BIGQUERY)
client = bigquery.Client(credentials=credentials,
                         project=credentials.project_id)


def criando_df_bigquery():
    # Definir cliente do BigQuery
    global client
    # Nome do dataset
    dataset_id = "dash_financeiro"

    # Referência ao dataset
    dataset_ref = client.dataset(dataset_id)

    # Criar o dataset se não existir
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"  # Escolha a região onde deseja armazenar os dados

    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} criado ou já existente.")
    return client, dataset_id


def get_data_financeiro(cursor, bloco: str, colunas: list):
    print(f'Lendo SQL {bloco}...')
    results = db.execute_select_in_db(
        cursor, fr'dash_financeiro\sql/{bloco}.sql')
    df = pd.DataFrame(results, columns=colunas)
    print(f'Dataframe {bloco} criado com sucesso!')
    return df


def tratar_bloco01(df):
    df['pago_atraso_2_ou_mais'] = df['pago_atraso_2_ou_mais'].astype(int)
    df['pago_atraso_1_mes'] = df['pago_atraso_1_mes'].astype(int)
    df['pago_no_mes'] = df['pago_no_mes'].astype(int)
    df['pago_antecipado_1_mes'] = df['pago_antecipado_1_mes'].astype(int)
    df['data_pagamento_fatura'] = pd.to_datetime(
        df['data_pagamento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['valor_pago_fatura'] = pd.to_numeric(df['valor_pago_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    return df


def tratar_bloco02(df):
    df['pagamento_em_atraso'] = df['pagamento_em_atraso'].astype(int)
    df['pagamento_em_dia'] = df['pagamento_em_dia'].astype(int)
    df['pagamento_em_aberto'] = df['pagamento_em_aberto'].astype(int)
    df['data_pagamento_fatura'] = pd.to_datetime(
        df['data_pagamento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_vencimento_fatura'] = pd.to_datetime(
        df['data_vencimento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['valor_fatura'] = pd.to_numeric(df['valor_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    return df


def tratar_bloco03(df):
    df['contratos_com_1_boleto_em_aberto'] = df['contratos_com_1_boleto_em_aberto'].astype(
        int)
    df['contratos_com_2_boletos_em_aberto'] = df['contratos_com_2_boletos_em_aberto'].astype(
        int)
    df['contratos_com_3_boletos_em_aberto'] = df['contratos_com_3_boletos_em_aberto'].astype(
        int)
    df['contratos_com_4_boletos_em_aberto'] = df['contratos_com_4_boletos_em_aberto'].astype(
        int)
    df['quantidade_de_boletos'] = df['quantidade_de_boletos'].astype(int)
    df['valor_fatura'] = pd.to_numeric(df['valor_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    return df


def tratar_bloco03monetario(df):
    df['quantidade_de_boletos'] = df['quantidade_de_boletos'].astype(int)
    df['valor_fatura'] = pd.to_numeric(df['valor_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['valor_por_fatura_de_contrato'] = pd.to_numeric(df['valor_por_fatura_de_contrato'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    return df


def triplicar_linhas_e_manipular_valores_b4g1(df):
    df_triplicado = df.loc[df.index.repeat(3)].reset_index(drop=True)

    count = 0
    data = []
    valor_fatura = []
    valor_proprietario = []
    valor_parceiro = []

    for index, row in df_triplicado.iterrows():
        count += 1
        if count == 1:
            data.append(row['data_pagamento_fatura'])
            valor_fatura.append(row['valor_fatura'])
            valor_proprietario.append(0)
            valor_parceiro.append(0)
        elif count == 2:
            data.append(row['data_repasse_fatura'])
            valor_fatura.append(0)
            valor_proprietario.append(row['valor_repasse_proprietario'])
            valor_parceiro.append(0)
        else:
            data.append(row['data_repasse_parceiro'])
            valor_fatura.append(0)
            valor_proprietario.append(0)
            valor_parceiro.append(row['valor_repasse_parceiro'])
            count = 0

    df_triplicado['data'] = data
    df_triplicado['valor_fatura'] = valor_fatura
    df_triplicado['valor_repasse_proprietario'] = valor_proprietario
    df_triplicado['valor_repasse_parceiro'] = valor_parceiro

    return df_triplicado


def tratar_bloco04_grafico01(df):
    df = triplicar_linhas_e_manipular_valores_b4g1(df)
    df['data_repasse_fatura'] = pd.to_datetime(
        df['data_repasse_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_repasse_parceiro'] = pd.to_datetime(
        df['data_repasse_parceiro'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_pagamento_fatura'] = pd.to_datetime(
        df['data_pagamento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data'] = pd.to_datetime(
        df['data'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['valor_fatura'] = pd.to_numeric(df['valor_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['valor_repasse_proprietario'] = pd.to_numeric(df['valor_repasse_proprietario'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['valor_repasse_parceiro'] = pd.to_numeric(df['valor_repasse_parceiro'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

    return df


def tratar_bloco04_grafico02(df):
    df['dt_fluxo'] = pd.to_datetime(
        df['dt_fluxo'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

    return df


def tratar_bloco05(df):
    df['quantidade_total_de_contratos'] = df['quantidade_total_de_contratos'].astype(
        int)
    df['boleto_em_aberto_em_atraso'] = df['boleto_em_aberto_em_atraso'].astype(
        int)
    df['quantidade_contratos_com_boletos_em_atraso'] = df['quantidade_contratos_com_boletos_em_atraso'].astype(
        int)
    df['porcentagem_contratos_por_boletos_em_atraso'] = pd.to_numeric(df['porcentagem_contratos_por_boletos_em_atraso'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

    return df


def tratar_bloco06_grafico1e2(df):
    df['data_repasse_fatura'] = pd.to_datetime(
        df['data_repasse_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_vencimento_fatura'] = pd.to_datetime(
        df['data_vencimento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_pagamento_fatura'] = pd.to_datetime(
        df['data_pagamento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['valor_fatura'] = pd.to_numeric(df['valor_fatura'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['valor_aluguel_contrato'] = pd.to_numeric(df['valor_aluguel_contrato'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

    return df


def tratar_bloco06_grafico03(df):
    df['vencimento_fatura'] = pd.to_datetime(
        df['vencimento_fatura'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    df['taxa_boleto'] = pd.to_numeric(df['taxa_boleto'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['taxa_ted_doc_pix'] = pd.to_numeric(df['taxa_ted_doc_pix'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['taxa_servico'] = pd.to_numeric(df['taxa_servico'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['taxa_administracao_parcela_up'] = pd.to_numeric(df['taxa_administracao_parcela_up'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
    df['taxa_contrato_parcela_up'] = pd.to_numeric(df['taxa_contrato_parcela_up'].str.replace(
        '.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')

    return df


def criando_tabela_bloco01_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    # Definir o esquema da tabela
    schema = [
        bigquery.SchemaField("id_fatura", "INTEGER"),
        bigquery.SchemaField("data_pagamento_fatura", "STRING"),
        bigquery.SchemaField("pago_atraso_2_ou_mais", "INTEGER"),
        bigquery.SchemaField("pago_atraso_1_mes", "INTEGER"),
        bigquery.SchemaField("pago_no_mes", "INTEGER"),
        bigquery.SchemaField("pago_antecipado_1_mes", "INTEGER"),
        bigquery.SchemaField("valor_pago_fatura", "FLOAT"),
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING")
    ]

    tabela_id_bloco01 = "Bloco01"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco01)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco01}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco01}' criada com sucesso.")

    return tabela_id_bloco01


def criando_tabela_bloco02_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    # Definir o esquema da tabela (Exemplo com 2 colunas)
    schema = [
        bigquery.SchemaField("codigo_do_contrato", "STRING"),
        bigquery.SchemaField("id_contrato", "INTEGER"),
        bigquery.SchemaField("id_fatura", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("adicional_fatura", "STRING"),
        bigquery.SchemaField("status_repasse_fatura", "STRING"),
        bigquery.SchemaField("data_pagamento_fatura", "STRING"),
        bigquery.SchemaField("data_vencimento_fatura", "STRING"),
        bigquery.SchemaField("valor_fatura", "FLOAT"),
        bigquery.SchemaField("pagamento_em_aberto", "INTEGER"),
        bigquery.SchemaField("pagamento_em_dia", "INTEGER"),
        bigquery.SchemaField("pagamento_em_atraso", "INTEGER"),
        bigquery.SchemaField("nome_produto", "STRING")
    ]

    tabela_id_bloco02 = "Bloco02"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco02)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco02}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco02}' criada com sucesso.")

    return tabela_id_bloco02


def criando_tabela_bloco03_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("status_fatura", "STRING"),
        bigquery.SchemaField("valor_fatura", "FLOAT"),
        bigquery.SchemaField("contratos_com_1_boleto_em_aberto", "INTEGER"),
        bigquery.SchemaField("contratos_com_2_boletos_em_aberto", "INTEGER"),
        bigquery.SchemaField("contratos_com_3_boletos_em_aberto", "INTEGER"),
        bigquery.SchemaField(
            "contratos_com_4_ou_mais_boletos_em_aberto", "INTEGER"),
        bigquery.SchemaField("quantidade_de_boletos", "INTEGER"),
        bigquery.SchemaField("status_contrato", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING")
    ]

    tabela_id_bloco03 = "Bloco03"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco03)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco03}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco03}' criada com sucesso.")

    return tabela_id_bloco03


def criando_tabela_bloco03_monetario_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("id_contrato", "INTEGER"),
        bigquery.SchemaField("id_parceiro", "INTEGER"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("valor_fatura", "FLOAT"),
        bigquery.SchemaField("status_fatura", "STRING"),
        bigquery.SchemaField("quantidade_de_boletos", "INTEGER"),
        bigquery.SchemaField("valor_por_fatura_de_contrato", "FLOAT"),
        bigquery.SchemaField("status_contrato", "STRING"),
        bigquery.SchemaField("nome_produto", "STRING")
    ]

    tabela_id_bloco03_monetario = "Bloco03_monetario"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco03_monetario)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco03_monetario}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco03_monetario}' criada com sucesso.")

    return tabela_id_bloco03_monetario


def criando_tabela_Bloco04_grafico01_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("adicional_fatura", "STRING"),
        bigquery.SchemaField("valor_fatura", "FLOAT"),
        bigquery.SchemaField("valor_repasse_proprietario", "FLOAT"),
        bigquery.SchemaField("valor_repasse_parceiro", "FLOAT"),
        bigquery.SchemaField("data_repasse_fatura", "STRING"),
        bigquery.SchemaField("data_pagamento_fatura", "STRING"),
        bigquery.SchemaField("data_repasse_parceiro", "STRING"),
        bigquery.SchemaField("data", "DATE")
    ]

    tabela_id_bloco04_grafico01 = "Bloco04_grafico01"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco04_grafico01)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco04_grafico01}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco04_grafico01}' criada com sucesso.")

    return tabela_id_bloco04_grafico01


def criando_tabela_Bloco04_grafico02_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("id_fatura", "INTEGER"),
        bigquery.SchemaField("select", "STRING"),
        bigquery.SchemaField("dt_fluxo", "STRING"),
        bigquery.SchemaField("valor", "FLOAT")
    ]

    tabela_id_bloco04_grafico02 = "Bloco04_grafico02"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco04_grafico02)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco04_grafico02}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco04_grafico02}' criada com sucesso.")

    return tabela_id_bloco04_grafico02


def criando_tabela_Bloco05_tabela01_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("quantidade_total_de_contratos", "INTEGER"),
        bigquery.SchemaField("boleto_em_aberto_em_atraso", "INTEGER"),
        bigquery.SchemaField(
            "quantidade_contratos_com_boletos_em_atraso", "INTEGER"),
        bigquery.SchemaField(
            "porcentagem_contratos_por_boletos_em_atraso", "FLOAT"),
    ]

    tabela_id_bloco05_tabela01 = "Bloco05_tabela01"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco05_tabela01)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco05_tabela01}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco05_tabela01}' criada com sucesso.")

    return tabela_id_bloco05_tabela01


def criando_tabela_Bloco05_tabela02_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("quantidade_total_de_contratos", "INTEGER"),
        bigquery.SchemaField("boleto_em_aberto_em_atraso", "INTEGER"),
        bigquery.SchemaField(
            "quantidade_contratos_com_boletos_em_atraso", "INTEGER"),
        bigquery.SchemaField(
            "porcentagem_contratos_por_boletos_em_atraso", "FLOAT"),
    ]

    tabela_id_bloco05_tabela02 = "Bloco05_tabela02"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco05_tabela02)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco05_tabela02}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco05_tabela02}' criada com sucesso.")

    return tabela_id_bloco05_tabela02


def criando_tabela_Bloco06_grafico1e2_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("name_status", "STRING"),
        bigquery.SchemaField("status_fatura", "STRING"),
        bigquery.SchemaField("adicional_fatura", "STRING"),
        bigquery.SchemaField("status_repasse_fatura", "STRING"),
        bigquery.SchemaField("valor_fatura", "FLOAT"),
        bigquery.SchemaField("valor_aluguel_contrato", "FLOAT"),
        bigquery.SchemaField("data_repasse_fatura", "STRING"),
        bigquery.SchemaField("data_vencimento_fatura", "STRING"),
        bigquery.SchemaField("data_pagamento_fatura", "STRING")
    ]

    tabela_id_bloco06_grafico1e2 = "Bloco06_grafico1e2"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco06_grafico1e2)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco06_grafico1e2}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco06_grafico1e2}' criada com sucesso.")

    return tabela_id_bloco06_grafico1e2


def criando_tabela_Bloco06_grafico03_bigquery(client, dataset_id, cursor, bloco: str, colunas: list):

    schema = [
        bigquery.SchemaField("vencimento_fatura", "STRING"),
        bigquery.SchemaField("taxa_boleto", "FLOAT"),
        bigquery.SchemaField("taxa_ted_doc_pix", "FLOAT"),
        bigquery.SchemaField("taxa_servico", "FLOAT"),
        bigquery.SchemaField("taxa_administracao_parcela_up", "FLOAT"),
        bigquery.SchemaField("taxa_contrato_parcela_up", "FLOAT")
    ]

    tabela_id_bloco06_grafico03 = "Bloco06_grafico03"
    tabela_ref = client.dataset(dataset_id).table(tabela_id_bloco06_grafico03)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id_bloco06_grafico03}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
    print(f"Tabela '{tabela_id_bloco06_grafico03}' criada com sucesso.")

    return tabela_id_bloco06_grafico03


dotenv.load_dotenv()


def time_start_pipeline():
    start_time = datetime.datetime.now()
    print("\n\nInício do pipeline:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return start_time


def time_end_pipeline(start_time):
    end_time = datetime.datetime.now()
    print("Fim do pipeline:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    elapsed_time = end_time - start_time
    print("Tempo decorrido:", str(elapsed_time).split(".")[0])


def criando_tabela_bigquery(client, dataset_id, bloco, cursor):
    if bloco == 'bloco01':
        return criando_tabela_bloco01_bigquery(
            client, dataset_id, cursor, bloco,
            ['id_fatura', 'data_pagamento_fatura',
             'pago_atraso_2_ou_mais', 'pago_atraso_1_mes',
             'pago_no_mes', 'pago_antecipado_1_mes',
             'valor_pago_fatura', 'codigo_contrato', 'nome_produto']
        )
    elif bloco == 'bloco02':
        return criando_tabela_bloco02_bigquery(
            client, dataset_id, cursor, bloco,
            ['codigo_do_contrato', 'id_contrato', 'id_fatura',
             'nome_parceiro', 'name_status', 'adicional_fatura',
             'status_repasse_fatura', 'data_pagamento_fatura',
             'data_vencimento_fatura', 'valor_fatura',
             'pagamento_em_aberto', 'pagamento_em_dia',
             'pagamento_em_atraso', 'nome_produto']
        )
    elif bloco == 'bloco03':
        return criando_tabela_bloco03_bigquery(
            client, dataset_id, cursor, bloco,
            ['nome_parceiro', 'status_fatura', 'valor_fatura',
             'contratos_com_1_boleto_em_aberto',
             'contratos_com_2_boletos_em_aberto',
             'contratos_com_3_boletos_em_aberto',
             'contratos_com_4_ou_mais_boletos_em_aberto',
             'quantidade_de_boletos', 'status_contrato', 'nome_produto']
        )
    elif bloco == 'bloco03_monetario':
        return criando_tabela_bloco03_monetario_bigquery(
            client, dataset_id, cursor, bloco,
            ['id_contrato', 'id_parceiro', 'nome_parceiro',
             'valor_fatura', 'status_fatura',
             'quantidade_de_boletos', 'valor_por_fatura_de_contrato',
             'status_contrato', 'nome_produto']
        )
    elif bloco == 'bloco04_grafico01':
        return criando_tabela_Bloco04_grafico01_bigquery(
            client, dataset_id, cursor, bloco,
            ['nome_parceiro', 'name_status', 'adicional_fatura',
             'valor_fatura', 'valor_repasse_proprietario',
             'valor_repasse_parceiro', 'data_repasse_fatura',
             'data_pagamento_fatura', 'data_repasse_parceiro',
             'data']
        )
    elif bloco == 'bloco04_grafico02':
        return criando_tabela_Bloco04_grafico02_bigquery(
            client, dataset_id, cursor, bloco,
            ['id_fatura', 'select', 'dt_fluxo', 'valor']
        )
    elif bloco == 'bloco05_tabela01':
        return criando_tabela_Bloco05_tabela01_bigquery(
            client, dataset_id, cursor, bloco,
            ['nome_parceiro', 'quantidade_total_de_contratos',
             'boleto_em_aberto_em_atraso',
             'quantidade_contratos_com_boletos_em_atraso',
             'porcentagem_contratos_por_boletos_em_atraso']
        )
    elif bloco == 'bloco05_tabela02':
        return criando_tabela_Bloco05_tabela02_bigquery(
            client, dataset_id, cursor, bloco,
            ['nome_parceiro', 'quantidade_total_de_contratos',
             'boleto_em_aberto_em_atraso',
             'quantidade_contratos_com_boletos_em_atraso',
             'porcentagem_contratos_por_boletos_em_atraso']
        )
    elif bloco == 'bloco06_grafico1e2':
        return criando_tabela_Bloco06_grafico1e2_bigquery(
            client, dataset_id, cursor, bloco,
            ['nome_parceiro', 'name_status', 'status_fatura',
             'adicional_fatura', 'status_repasse_fatura',
             'valor_fatura', 'valor_aluguel_contrato',
             'data_repasse_fatura', 'data_vencimento_fatura',
             'data_pagamento_fatura']
        )
    elif bloco == 'bloco06_grafico03':
        return criando_tabela_Bloco06_grafico03_bigquery(
            client, dataset_id, cursor, bloco,
            ['vencimento_fatura', 'taxa_boleto',
             'taxa_ted_doc_pix', 'taxa_servico',
             'taxa_administracao_parcela_up',
             'taxa_contrato_parcela_up']
        )
    else:
        raise ValueError(
            f"Bloco '{bloco}' não tem função de criação de tabela implementada.")


def pipe_bigquery(cursor, bloco: str, tabela_id: str, colunas: list):
    client, dataset_id = criando_df_bigquery()
    tabela_id = criando_tabela_bigquery(client, dataset_id, bloco, cursor)
    df = get_data_financeiro(cursor, bloco, colunas)
    # Aplica o tratamento específico para o bloco
    if bloco == 'bloco01':
        df = tratar_bloco01(df)
        print("Fazendo tratamento do bloco 01...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco02':
        df = tratar_bloco02(df)
        print("Fazendo tratamento do bloco 02...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco03':
        df = tratar_bloco03(df)
        print("Fazendo tratamento do bloco 03...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco03_monetario':
        df = tratar_bloco03monetario(df)
        print("Fazendo tratamento do bloco 03 monetário...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco04_grafico01':
        df = tratar_bloco04_grafico01(df)
        print("Fazendo tratamento do bloco 04 gráfico 01...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco04_grafico02':
        df = tratar_bloco04_grafico02(df)
        print("Fazendo tratamento do bloco 04 gráfico 02...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco05_tabela01':
        df = tratar_bloco05(df)
        print("Fazendo tratamento do bloco 05 tabela 01...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco05_tabela02':
        df = tratar_bloco05(df)
        print("Fazendo tratamento do bloco 05 tabela 02...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco06_grafico1e2':
        df = tratar_bloco06_grafico1e2(df)
        print("Fazendo tratamento do bloco 06 gráfico 1 e 2...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    elif bloco == 'bloco06_grafico03':
        df = tratar_bloco06_grafico03(df)
        print("Fazendo tratamento do bloco 06 gráfico 03...")
        df.to_parquet(
            f'dash_financeiro/data/{bloco}.parquet', engine='pyarrow', index=False)
        file_path = f'dash_financeiro/data/{bloco}.parquet'
    else:
        raise ValueError(f"Tratamento não definido para o bloco: {bloco}")

    tabela_ref = client.dataset(dataset_id).table(tabela_id)
    print(f'Limpando a tabela do bigquery e fazendo upload do parquet para o BigQuery...')
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        # Substitui os dados existentes
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    with open(file_path, "rb") as file:
        job = client.load_table_from_file(
            file, tabela_ref, job_config=job_config)

    job.result()
    print("Upload do Parquet concluído com sucesso!")

    print(f'Pipe {bloco} feita com sucesso!!!\n')


def main_financeiro():

    time_start_time = time_start_pipeline()

    con = db.connect_to_db()
    cursor = con.cursor()

    print('BLOCO 01')
    pipe_bigquery(cursor=cursor, bloco='bloco01', tabela_id='Bloco01',
                  colunas=['id_fatura', 'data_pagamento_fatura',
                           'pago_atraso_2_ou_mais', 'pago_atraso_1_mes',
                           'pago_no_mes', 'pago_antecipado_1_mes',
                           'valor_pago_fatura', 'codigo_contrato', 'nome_produto'])
    print('BLOCO 02')
    pipe_bigquery(cursor=cursor, bloco='bloco02', tabela_id='Bloco02',
                  colunas=['codigo_do_contrato', 'id_contrato', 'id_fatura',
                           'nome_parceiro', 'name_status', 'adicional_fatura',
                           'status_repasse_fatura', 'data_pagamento_fatura',
                           'data_vencimento_fatura', 'valor_fatura',
                           'pagamento_em_aberto', 'pagamento_em_dia',
                           'pagamento_em_atraso', 'nome_produto'])
    print('BLOCO 03')
    pipe_bigquery(cursor=cursor, bloco='bloco03', tabela_id='Bloco03',
                  colunas=['nome_parceiro', 'status_fatura', 'valor_fatura',
                           'contratos_com_1_boleto_em_aberto',
                           'contratos_com_2_boletos_em_aberto',
                           'contratos_com_3_boletos_em_aberto',
                           'contratos_com_4_boletos_em_aberto',
                           'quantidade_de_boletos', 'status_contrato', 'nome_produto'])
    print('BLOCO 03 MONETARIO')
    pipe_bigquery(cursor=cursor, bloco='bloco03_monetario', tabela_id='Bloco03_monetario',
                  colunas=['id_contrato', 'id_parceiro', 'nome_parceiro',
                           'valor_fatura', 'status_fatura',
                           'quantidade_de_boletos', 'valor_por_fatura_de_contrato',
                           'status_contrato', 'nome_produto'])
    print('BLOCO 04 GRAFICO 01')
    pipe_bigquery(cursor=cursor, bloco='bloco04_grafico01', tabela_id='Bloco04_grafico01',
                  colunas=['nome_parceiro', 'name_status', 'adicional_fatura',
                           'valor_fatura', 'valor_repasse_proprietario',
                           'valor_repasse_parceiro', 'data_repasse_fatura',
                           'data_pagamento_fatura', 'data_repasse_parceiro',
                           'data'])
    print('BLOCO 04 GRAFICO 02')
    pipe_bigquery(cursor=cursor, bloco='bloco04_grafico02', tabela_id='Bloco04_grafico02',
                  colunas=['id_fatura', 'select', 'dt_fluxo', 'valor'])
    print('BLOCO 05 TABELA 01')
    pipe_bigquery(cursor=cursor, bloco='bloco05_tabela01', tabela_id='Bloco05_tabela01',
                  colunas=['nome_parceiro', 'quantidade_total_de_contratos',
                           'boleto_em_aberto_em_atraso',
                           'quantidade_contratos_com_boletos_em_atraso',
                           'porcentagem_contratos_por_boletos_em_atraso'])
    print('BLOCO 05 TABELA 02')
    pipe_bigquery(cursor=cursor, bloco='bloco05_tabela02', tabela_id='Bloco05_tabela02',
                  colunas=['nome_parceiro', 'quantidade_total_de_contratos',
                           'boleto_em_aberto_em_atraso',
                           'quantidade_contratos_com_boletos_em_atraso',
                           'porcentagem_contratos_por_boletos_em_atraso'])
    print('BLOCO 06 GRAFICO 1 E 2')
    pipe_bigquery(cursor=cursor, bloco='bloco06_grafico1e2', tabela_id='Bloco06_grafico1e2',
                  colunas=['nome_parceiro', 'name_status', 'status_fatura',
                           'adicional_fatura', 'status_repasse_fatura',
                           'valor_fatura', 'valor_aluguel_contrato',
                           'data_repasse_fatura', 'data_vencimento_fatura',
                           'data_pagamento_fatura'])
    print('BLOCO 06 GRAFICO 3')
    pipe_bigquery(cursor=cursor, bloco='bloco06_grafico03', tabela_id='Bloco06_grafico03',
                  colunas=['vencimento_fatura', 'taxa_boleto',
                           'taxa_ted_doc_pix', 'taxa_servico',
                           'taxa_administracao_parcela_up',
                           'taxa_contrato_parcela_up'])

    time_end_pipeline(time_start_time)


main_financeiro()
