from datetime import datetime, timedelta, date
from utils import mysql_db as db
from utils.planilhas_transacionais import get_contratos
from google.api_core.exceptions import BadRequest
from google.oauth2 import service_account
from google.cloud import bigquery
from workalendar.america import Brazil
from unidecode import unidecode
import numpy as np
import pandas as pd
import dotenv
import uuid
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

dotenv.load_dotenv()
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
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
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


def tranto_contratos():
    df_contratos = get_contratos()

    print('Excluindo as 57 primeiras linhas...')
    df_contratos = df_contratos.iloc[1437:]  # partir daqui tem horas

    print('Pegando apenas colunas a se utilizar...')
    df_contratos = df_contratos[['Código do Contrato', 'Receb.',
                                'Envio', 'Assin.', 'Sistema',
                                 'Gr. Boleto', 'Captadora', 'Valor',
                                 'Preencher com "SIM"']]

    print('Renomeando colunas...')
    df_contratos.rename(columns={'Código do Contrato': 'codigo_contrato',
                                 'Receb.': 'data_recebido',
                                 'Envio': 'data_envio',
                                 'Assin.': 'data_assinado',
                                 'Sistema': 'data_sistema',
                                 'Gr. Boleto': 'data_primeiro_boleto',
                                 'Captadora': 'captadora',
                                 'Valor': 'valor_aluguel',
                                 'Preencher com "SIM"': 'contrato_cancelado'}, inplace=True)

    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_contratos['data_envio'] = df_contratos.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Trativas de preenchimento errado das menians de contratos em data_primeiro_boleto...')
    df_contratos['data_primeiro_boleto'] = df_contratos['data_primeiro_boleto'].replace(
        ['-', 'Pendente', 'Bruna', 'Pendente ', 'pendente ', 'penente', 'pendente iptu', 'pendete'], '')

    print('Converter todos os Sim em maiúsculas...')
    df_contratos['contrato_cancelado'] = df_contratos['contrato_cancelado'].str.upper()

    print('Trativa se alguma coluna tiver vazia e ter data em alguma coluna seguite...')
    df_contratos['data_sistema'] = df_contratos.apply(
        lambda row: row['data_primeiro_boleto'] if row['data_sistema'] == '' else row['data_sistema'], axis=1)
    df_contratos['data_assinado'] = df_contratos.apply(
        lambda row: row['data_sistema'] if row['data_assinado'] == '' else row['data_assinado'], axis=1)
    df_contratos['data_envio'] = df_contratos.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

    print('Excluindo linhas que não tem nehuma data_preenchida...')
    df_contratos = df_contratos[df_contratos['data_recebido'] != '']

    print('Tratando valor_aluguel para o padrão sheets...')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        '', None)
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].str.replace(
        'R$', '').str.replace(' ', '')

    print('ERROS das meninas de contratos!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        'R$3,900,00', '3.900,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        'R$ 2,500,00', '2.500,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        '1.000.00', '1.000,00')

    df_contratos.drop(['valor_aluguel', 'contrato_cancelado'],
                      axis=1, inplace=True)

    print('Tratando erros das meninas de contratos (colocaram - e Pendente em coluna de Data)')
    colunas_para_tratar = ['data_primeiro_boleto', 'data_sistema']
    df_contratos[colunas_para_tratar] = df_contratos[colunas_para_tratar].replace(
        ['pendente', '-', 'pendnete '], '')

    print('Passando colunas data_recebido, data_envio para datetime...')
    df_contratos['data_recebido'] = pd.to_datetime(
        df_contratos['data_recebido'], format='%d/%m/%Y %H:%M:%S')
    df_contratos['data_envio'] = pd.to_datetime(
        df_contratos['data_envio'], format='%d/%m/%Y %H:%M:%S')

    print('Passando colunas data_assinado, data_sistema, data_boleto para datetime...')
    df_contratos['data_assinado'].replace(" ", None, inplace=True)
    df_contratos['data_assinado'].replace("-", pd.NaT, inplace=True)
    df_contratos['data_sistema'].replace(" ", None, inplace=True)
    df_contratos['data_primeiro_boleto'].replace(" ", None, inplace=True)

    df_contratos['data_assinado'] = pd.to_datetime(
        df_contratos['data_assinado'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_contratos['data_sistema'] = pd.to_datetime(
        df_contratos['data_sistema'], format='%d/%m/%Y %H:%M:%S')
    df_contratos['data_primeiro_boleto'] = pd.to_datetime(
        df_contratos['data_primeiro_boleto'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

    return df_contratos


def is_after_1800(datetime_value):
    time_1800 = datetime(datetime_value.year,
                         datetime_value.month, datetime_value.day, 18, 0, 0)
    time_800 = datetime(datetime_value.year,
                        datetime_value.month, datetime_value.day, 8, 0, 0)
    if (time_1800 < datetime_value) or (datetime_value < time_800):
        return "Fora do horário comercial"

    return "Horário comercial"


df_contratos = tranto_contratos()

df_contratos.dropna(subset=['data_envio'], inplace=True)

df_contratos['horario_comercial'] = df_contratos.apply(
    lambda row: is_after_1800(row['data_recebido']), axis=1)


def corrigir_colunas_datetime(df):
    min_bq = pd.Timestamp("1677-09-21")
    max_bq = pd.Timestamp("2262-04-11")

    for col in df.columns:
        if "data" in col:  # ou uma lista com nomes específicos
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df[col] = df[col].where(
                    df[col].between(min_bq, max_bq), pd.NaT)
                df[col] = df[col].dt.round("us")
            except Exception as e:
                print(f"⚠️ Erro ao converter coluna {col}: {e}")
    return df


CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")


def tranto_contratos():
    df_contratos2 = get_contratos()

    print('Excluindo as 57 primeiras linhas...')
    df_contratos2 = df_contratos2.iloc[57:]  # Não são mais utilizadas

    print('Pegando apenas colunas a se utilizar...')
    df_contratos2 = df_contratos2[['Código do Contrato', 'Receb.',
                                   'Envio', 'Assin.', 'Sistema',
                                   'Gr. Boleto', 'Captadora', 'Valor',
                                   'Preencher com "SIM"']]

    print('Renomeando colunas...')
    df_contratos2.rename(columns={'Código do Contrato': 'codigo_contrato',
                                  'Receb.': 'data_recebido',
                                  'Envio': 'data_envio',
                                  'Assin.': 'data_assinado',
                                  'Sistema': 'data_sistema',
                                  'Gr. Boleto': 'data_primeiro_boleto',
                                  'Captadora': 'captadora',
                                  'Valor': 'valor_aluguel',
                                  'Preencher com "SIM"': 'contrato_cancelado'}, inplace=True)

    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_contratos2['data_envio'] = df_contratos2.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_contratos2['data_recebido'] = df_contratos2.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Trativas de preenchimento errado das menians de contratos em data_primeiro_boleto...')
    df_contratos2['data_primeiro_boleto'] = df_contratos2['data_primeiro_boleto'].replace([
                                                                                          '-', 'Pendente'], '')

    print('Converter todos os Sim em maiúsculas...')
    df_contratos2['contrato_cancelado'] = df_contratos2['contrato_cancelado'].str.upper()

    print('Trativa se alguma coluna tiver vazia e ter data em alguma coluna seguite...')
    df_contratos2['data_sistema'] = df_contratos2.apply(
        lambda row: row['data_primeiro_boleto'] if row['data_sistema'] == '' else row['data_sistema'], axis=1)
    df_contratos2['data_assinado'] = df_contratos2.apply(
        lambda row: row['data_sistema'] if row['data_assinado'] == '' else row['data_assinado'], axis=1)
    df_contratos2['data_envio'] = df_contratos2.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '' else row['data_envio'], axis=1)
    df_contratos2['data_recebido'] = df_contratos2.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

    print('Excluindo linhas que não tem nehuma data_preenchida...')
    df_contratos2 = df_contratos2[df_contratos2['data_recebido'] != '']

    print('Tratando valor_aluguel para o padrão sheets...')
    df_contratos2['valor_aluguel'] = df_contratos2['valor_aluguel'].replace(
        '', None)
    df_contratos2['valor_aluguel'] = df_contratos2['valor_aluguel'].str.replace(
        'R$', '').str.replace(' ', '')

    print('ERROS das meninas de contratos!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    df_contratos2['valor_aluguel'] = df_contratos2['valor_aluguel'].replace(
        'R$3,900,00', '3.900,00')
    df_contratos2['valor_aluguel'] = df_contratos2['valor_aluguel'].replace(
        'R$ 2,500,00', '2.500,00')
    df_contratos2['valor_aluguel'] = df_contratos2['valor_aluguel'].replace(
        '1.000.00', '1.000,00')  # Não passei para as meninas de contratos, fiquei com vergonha

    print('Tratando erros das meninas de contratos (colocaram - e Pendente em coluna de Data)')
    colunas_para_tratar = ['data_primeiro_boleto', 'data_sistema']
    df_contratos2[colunas_para_tratar] = df_contratos2[colunas_para_tratar].replace([
                                                                                    'pendente', '-'], '')

    return df_contratos2


df_contratos2 = tranto_contratos()


PRIVIOUS_YEAR_HOLIDAYS = [(datetime(date.year, date.month, date.day), holiday)
                          for date, holiday in Brazil().holidays(datetime.now().year - 1)]
CURRENT_YEAR_HOLIDAYS = [(datetime(date.year, date.month, date.day), holiday)
                         for date, holiday in Brazil().holidays(datetime.now().year)]
HOLIDAYS = PRIVIOUS_YEAR_HOLIDAYS + CURRENT_YEAR_HOLIDAYS


def is_holiday(date):
    return date.date() in HOLIDAYS


def count_weekends_date(start_date, end_date):
    counted_days = 0
    day = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in [5, 6]:  # 5 é sábado e 6 é domingo
            counted_days += 1
        current_date += day
    return counted_days


def count_holidays(start_date, end_date):
    worked_on_holiday = 0
    for holiday_date, holiday_name in HOLIDAYS:
        # Verifique se alguma data de feriado cai entre a data de início e a data de término do trabalho
        if start_date <= holiday_date <= end_date:
            worked_on_holiday += 1
    return worked_on_holiday

# Qtd de contratos que foram recebidos em dia de feriado


df_contratos2['data_recebido'] = pd.to_datetime(
    df_contratos2['data_recebido'], dayfirst=True, errors='coerce')
# Obter a lista de datas de feriado em formato string 'YYYY-MM-DD'
holidays_dates = [date.strftime('%Y-%m-%d') for date, _ in HOLIDAYS]
# Verificar se cada data na coluna 'data_recebido' está na lista de feriados
df_contratos2['feriado'] = df_contratos2['data_recebido'].dt.strftime(
    '%Y-%m-%d').isin(holidays_dates)
df_contratos2['feriado'] = df_contratos2['feriado'].apply(
    lambda x: 'Sim' if x else 'Não')  # Converter os valores True/False para 'Sim'/'Não'

# Qtd de contratos que foram recebidos em finais de semana


def is_weekend(date):
    return date.weekday() in [5, 6]


df_contratos2['data_recebido'] = pd.to_datetime(df_contratos2['data_recebido'])
df_contratos2['final_de_semana'] = df_contratos2['data_recebido'].apply(
    is_weekend)
df_contratos2['final_de_semana'] = df_contratos2['final_de_semana'].apply(
    lambda x: 'Sim' if x else 'Não')  # Converter os valores True/False para 'Sim'/'Não'

# Tratando NaT e garantindo o tipo de dado correto para cada coluna de data
df_contratos['data_recebido'] = pd.to_datetime(
    df_contratos['data_recebido'], errors='coerce')
df_contratos['data_envio'] = pd.to_datetime(
    df_contratos['data_envio'], errors='coerce')
df_contratos['data_assinado'] = pd.to_datetime(
    df_contratos['data_assinado'], errors='coerce')
df_contratos['data_sistema'] = pd.to_datetime(
    df_contratos['data_sistema'], errors='coerce')
df_contratos['data_primeiro_boleto'] = pd.to_datetime(
    df_contratos['data_primeiro_boleto'], errors='coerce')

# Tratando NaT e garantindo o tipo de dado correto para cada coluna de data em contratos2
df_contratos2['data_recebido'] = pd.to_datetime(
    df_contratos2['data_recebido'], errors='coerce')
df_contratos2['data_envio'] = pd.to_datetime(
    df_contratos2['data_envio'], errors='coerce')
df_contratos2['data_assinado'] = pd.to_datetime(
    df_contratos2['data_assinado'], errors='coerce')
df_contratos2['data_sistema'] = pd.to_datetime(
    df_contratos2['data_sistema'], errors='coerce')
df_contratos2['data_primeiro_boleto'] = pd.to_datetime(
    df_contratos2['data_primeiro_boleto'], errors='coerce')

# Substituindo valores NaT por None (NULL no BigQuery) explicitamente para df_contratos2

# Certificando-se de que as colunas de data estão corretamente convertidas para o formato DATE em df_contratos2
df_contratos2['data_recebido'] = df_contratos2['data_recebido'].dt.date
df_contratos2['data_envio'] = df_contratos2['data_envio'].dt.date
df_contratos2['data_assinado'] = df_contratos2['data_assinado'].dt.date
df_contratos2['data_sistema'] = df_contratos2['data_sistema'].dt.date
df_contratos2['data_primeiro_boleto'] = df_contratos2['data_primeiro_boleto'].dt.date

# Verifique os dados após a transformação
print(df_contratos2[['data_envio', 'data_assinado', 'data_recebido']].head())

# Substituindo valores NaT por None (NULL no BigQuery) para df_contratos

# Certificando-se de que todos os valores estão no formato correto (DATE) e ajustando as colunas para DATE em df_contratos
df_contratos['data_recebido'] = df_contratos['data_recebido'].dt.date
df_contratos['data_envio'] = df_contratos['data_envio'].dt.date
df_contratos['data_assinado'] = df_contratos['data_assinado'].dt.date
df_contratos['data_sistema'] = df_contratos['data_sistema'].dt.date
df_contratos['data_primeiro_boleto'] = df_contratos['data_primeiro_boleto'].dt.date


def contratos2():
    df = df_contratos2.copy()
    tabela_id = "contratos2"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("data_envio", "DATE"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("data_sistema", "DATE"),
        bigquery.SchemaField("data_primeiro_boleto", "DATE"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("valor_aluguel", "STRING"),
        bigquery.SchemaField("contrato_cancelado", "STRING"),
        bigquery.SchemaField("feriado", "STRING"),
        bigquery.SchemaField("final_de_semana", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_gerencial", 'contratos2')


def contratos():
    df = df_contratos.copy()
    # df = corrigir_colunas_datetime(df)
    # df["data_assinado"] = df["data_assinado"].where(df["data_assinado"].notna(), None)
    print(df["data_assinado"].head(10))
    tabela_id = "contratos"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_recebido", "DATE"),
        bigquery.SchemaField("data_envio", "DATE"),
        bigquery.SchemaField("data_assinado", "DATE"),
        bigquery.SchemaField("data_sistema", "DATE"),
        bigquery.SchemaField("data_primeiro_boleto", "DATE"),
        bigquery.SchemaField("captadora", "STRING"),
        bigquery.SchemaField("horario_comercial", "STRING"),
    ]

    upload_bigquery(schema, tabela_id, df, "dash_gerencial", 'contratos1')


rescisao_cohort = r"C:\Users\Julio Lage\Documents\GitHub\cloud-and-data-team\dash_gerencial\sql\rescisao_cohort.sql"


def count_months_passed(start_date, end_date):
    difference_in_year = (end_date.year - start_date.year) * 12

    difference_in_months = (end_date.month - start_date.month)
    difference = difference_in_year + difference_in_months
    return difference


con = db.connect_to_db()
cursor = con.cursor()
colunas = ['codigo_contrato', 'data_de_inicio', 'data_de_rescisao', 'parceiro']
results = db.execute_select_in_db(cursor, rescisao_cohort)
df = pd.DataFrame(results, columns=colunas)
print("Dataframe gerado com sucesso!!!")

df['data_de_inicio'] = pd.to_datetime(df['data_de_inicio'])
df['data_de_rescisao'] = pd.to_datetime(
    df['data_de_rescisao'], errors='coerce')

# Removendo linhas com datas inválidas (NaT)
# TEM APENAS 1 LINHA
df = df.dropna(subset=['data_de_inicio', 'data_de_rescisao'])
print("Removendo linhas com datas inválidas (NaT)")

# Aplicar a função às colunas do DataFrame e criar uma nova coluna
df['transacao'] = df.apply(lambda row: count_months_passed(row['data_de_inicio'], row['data_de_rescisao'] if pd.Timestamp(
    date.today()) > row['data_de_rescisao'] else date.today()), axis=1) + 1
print("Aplicando a função às colunas do DataFrame e criar uma nova coluna")

# Filtrando os dados para manter apenas os registros do ano de 2023
df = df[df['data_de_inicio'].dt.year == 2023]
print("Filtrando os dados para manter apenas os registros do ano de 2023")

df['data_transacao'] = df.apply(lambda row: row['data_de_inicio'] + pd.DateOffset(
    months=row['transacao']) - pd.DateOffset(months=1), axis=1)

# duplicando as linhas de acordo com a quantidade de transacao
df = df.loc[df.index.repeat(df['transacao'])].reset_index(drop=True)
print("Duplicando as linhas de acordo com a quantidade de transacao")

# colocando transacao no fromato de contagem e repetições
df['transacao'] = df.groupby('codigo_contrato').cumcount()
print("colocando transacao no fromato de contagem e repetições")

# Criar a nova coluna 'data_de_inicio_mais_transacao_meses'
df['data_transacao'] = df.apply(
    lambda row: row['data_de_inicio'] + pd.DateOffset(months=row['transacao']), axis=1)
print("Criar a nova coluna 'data_de_inicio_mais_transacao_meses'")

df_rescisao = df[['codigo_contrato', 'data_de_inicio',
                  'parceiro', 'transacao', 'data_transacao']]

# Convertendo para o formato datetime, se ainda não estiver no formato correto
df_rescisao['data_de_inicio'] = pd.to_datetime(df_rescisao['data_de_inicio'])
df_rescisao['data_transacao'] = pd.to_datetime(df_rescisao['data_transacao'])

# Calculando o número de meses entre as datas
df_rescisao['cohort_mes'] = df_rescisao.apply(lambda row: (row['data_transacao'].year - row['data_de_inicio'].year) * 12 +
                                              (row['data_transacao'].month - row['data_de_inicio'].month) + 1, axis=1)
print("Criando a coluna de cohort ")


df_rescisao['data_de_inicio'] = pd.to_datetime(
    df_rescisao['data_de_inicio'], errors='coerce')
df_rescisao['data_transacao'] = pd.to_datetime(
    df_rescisao['data_transacao'], errors='coerce')

df_rescisao['data_de_inicio'] = df_rescisao['data_de_inicio'].dt.date
df_rescisao['data_transacao'] = df_rescisao['data_transacao'].dt.date


def recisao():

    df = df_rescisao.copy()
    tabela_id = "recisao"
    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("data_de_inicio", "DATE"),
        bigquery.SchemaField("parceiro", "STRING"),
        bigquery.SchemaField("transacao", "INTEGER"),
        bigquery.SchemaField("data_transacao", "DATE"),
        bigquery.SchemaField("cohort_mes", "INTEGER"),
    ]

    # Realiza o upload para o BigQuery
    upload_bigquery(schema, tabela_id, df, 'dash_gerencial', 'recisao')


cohort_inadimplentes = r'C:\Users\Julio Lage\Documents\GitHub\cloud-and-data-team\dash_gerencial\sql\cohort_inadimplentes.sql'


def count_months_passed(start_date, end_date):
    difference_in_year = (end_date.year - start_date.year) * 12

    difference_in_months = (end_date.month - start_date.month)
    difference = difference_in_year + difference_in_months
    return difference

# Função para verificar se a data_transacao é menor ou igual ao vencimento_fatura


def verificar_inadimplencia(row):
    if row['data_transacao'] <= row['vencimento_fatura']:
        return 0
    else:
        return 1


con = db.connect_to_db()
cursor = con.cursor()
colunas = ['codigo_contrato', 'data_inicio_contrato', 'data_de_rescisao', 'nome_parceiro', 'id_fatura',
           'vencimento_fatura', 'pagamento_fatura', 'status_fatura', 'Inadimplentes']
results = db.execute_select_in_db(cursor, cohort_inadimplentes)
df_inadimplentes = pd.DataFrame(results, columns=colunas)
print(f'Dataframe criado com sucesso!')

df_inadimplentes = df_inadimplentes[['codigo_contrato', 'data_inicio_contrato',
                                     'data_de_rescisao', 'vencimento_fatura', 'nome_parceiro', 'id_fatura', 'Inadimplentes']]
df_inadimplentes['data_inicio_contrato'] = pd.to_datetime(
    df_inadimplentes['data_inicio_contrato'])
df_inadimplentes['data_de_rescisao'] = pd.to_datetime(
    df_inadimplentes['data_de_rescisao'])
df_inadimplentes['vencimento_fatura'] = pd.to_datetime(
    df_inadimplentes['vencimento_fatura'])

# Aplicar a função às colunas do DataFrame e criar uma nova coluna
df_inadimplentes['transacao'] = df_inadimplentes.apply(lambda row: count_months_passed(
    row['data_inicio_contrato'], row['vencimento_fatura'] if pd.Timestamp(date.today()) > row['vencimento_fatura'] else date.today()), axis=1) + 1
print("Aplicar a função às colunas do DataFrame e criar uma nova coluna")

# Filtrando os dados para manter apenas os registros do ano de 2023
df_inadimplentes = df_inadimplentes[df_inadimplentes['data_inicio_contrato'].dt.year == 2023]
print("Filtrando os dados para manter apenas os registros do ano de 2023")

df_inadimplentes['data_transacao'] = df_inadimplentes.apply(
    lambda row: row['data_inicio_contrato'] + pd.DateOffset(months=row['transacao']) - pd.DateOffset(months=1), axis=1)

# duplicando as linhas de acordo com a quantidade de transacao
df_inadimplentes = df_inadimplentes.loc[df_inadimplentes.index.repeat(
    df_inadimplentes['transacao'])].reset_index(drop=True)
print("Duplicando as linhas de acordo com a quantidade de transacao")

# colocando transacao no formato de contagem e repetições
df_inadimplentes['transacao'] = df_inadimplentes.groupby(
    'id_fatura').cumcount()
print("Colocando transacao no formato de contagem e repetições")

# Criar a nova coluna 'data_de_inicio_mais_transacao_meses'
df_inadimplentes['data_transacao'] = df_inadimplentes.apply(
    lambda row: row['data_inicio_contrato'] + pd.DateOffset(months=row['transacao']), axis=1)
print("Criar a nova coluna 'data_de_inicio_mais_transacao_meses'")

# Obtém o dia do vencimento_fatura e soma 1
df_inadimplentes['novo_dia_transacao'] = df_inadimplentes['vencimento_fatura'].dt.day + 1
print("Obtém o dia do vencimento_fatura e soma 1")

# Corrige casos onde o novo dia ultrapassa o limite do mês
df_inadimplentes['novo_dia_transacao'] = df_inadimplentes.apply(
    lambda row: min(row['novo_dia_transacao'], pd.Timestamp(
        row['data_transacao']).days_in_month),
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
df_inadimplentes['Inadimplentes_Inadim'] = df_inadimplentes.apply(
    verificar_inadimplencia, axis=1)
print("Função aplicada na nova coluna de Inadimplentes!")

df_inadimplentes = df_inadimplentes[['codigo_contrato', 'id_fatura', 'data_inicio_contrato',
                                     'vencimento_fatura', 'nome_parceiro', 'transacao', 'data_transacao', 'Inadimplentes_Inadim']]

# Calculando o número de meses entre as datas
df_inadimplentes['cohort_mes'] = df_inadimplentes.apply(lambda row: (row['data_transacao'].year - row['data_inicio_contrato'].year) * 12 +
                                                        (row['data_transacao'].month - row['data_inicio_contrato'].month) + 1, axis=1)
print("Coluna de cohort gerada!")


df_inadimplentes['data_inicio_contrato'] = pd.to_datetime(
    df_inadimplentes['data_inicio_contrato'], errors='coerce')
df_inadimplentes['vencimento_fatura'] = pd.to_datetime(
    df_inadimplentes['vencimento_fatura'], errors='coerce')
df_inadimplentes['data_transacao'] = pd.to_datetime(
    df_inadimplentes['data_transacao'], errors='coerce')

df_inadimplentes['data_inicio_contrato'] = df_inadimplentes['data_inicio_contrato'].dt.date
df_inadimplentes['vencimento_fatura'] = df_inadimplentes['vencimento_fatura'].dt.date
df_inadimplentes['data_transacao'] = df_inadimplentes['data_transacao'].dt.date


def inadimplentes():

    df = df_inadimplentes.copy()
    tabela_id = "inadimplentes"

    schema = [
        bigquery.SchemaField("codigo_contrato", "STRING"),
        bigquery.SchemaField("id_fatura", "INTEGER"),
        bigquery.SchemaField("data_inicio_contrato", "DATE"),
        bigquery.SchemaField("vencimento_fatura", "DATE"),
        bigquery.SchemaField("nome_parceiro", "STRING"),
        bigquery.SchemaField("transacao", "INTEGER"),
        bigquery.SchemaField("data_transacao", "DATE"),
        bigquery.SchemaField("Inadimplentes_Inadim", "INTEGER"),
        bigquery.SchemaField("cohort_mes", "INTEGER"),
    ]

    # Realiza o upload para o BigQuery
    upload_bigquery(schema, tabela_id, df, 'dash_gerencial', 'inadimplentes')


def main_gerencial():
    inadimplentes()
    recisao()
    contratos2()
    contratos()


if __name__ == "__main__":
    main_gerencial()
