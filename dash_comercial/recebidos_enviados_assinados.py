import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from utils.sheets import Sheets
from utils import planilhas_transacionais 

import pandas as pd
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
PAGINA_SHEETS = 'RECEBIDOS_ENV_ASSIN'
COLUMNS={'Código do Contrato': 'codigo_contrato',
        'Receb.': 'data_recebido',
        'Envio': 'data_enviado',
        'Assin.': 'data_assinado',
        'Captadora': 'captadora',
        'Valor': 'valor'}

def main():
    print('\n\t------>RECEBIDOS ENVIADOS ASSINADOS<------\n')
    df_recb_env_ass =  planilhas_transacionais.get_recebidos_enviados_assinados()

    print('Renomeando e pegando apenas colunas que vou utilizar...')
    df_recb_env_ass.rename(columns=COLUMNS, inplace=True)
    df_recb_env_ass = df_recb_env_ass[COLUMNS.values()]

    print('Trativa para a coluna data_recebido, vazio e data_enviado preenchida')
    df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)
    
    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_recb_env_ass['data_enviado'] = df_recb_env_ass.apply(lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'], axis=1)
    df_recb_env_ass['data_recebido'] = df_recb_env_ass.apply(lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)


    # AS VEZES ELAS COLOCAM UM X NA COLUNCA DATA_RECEBIDO
    df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido'] != 'X']


    print('Converter a coluna "data_inicio_contrato" para o formato de data...')
    df_recb_env_ass['data_recebido'] = pd.to_datetime(df_recb_env_ass['data_recebido'], format='%d/%m/%Y %H:%M:%S')
    df_recb_env_ass['data_assinado'] = (
    pd.to_datetime(df_recb_env_ass['data_assinado'], dayfirst=True, errors='coerce')
    .dt.strftime('%Y-%m-%d')
    )

    df_recb_env_ass['data_enviado'] = (
        pd.to_datetime(df_recb_env_ass['data_enviado'], dayfirst=True, errors='coerce')
        .dt.strftime('%Y-%m-%d')
    )
    df_recb_env_ass = df_recb_env_ass[df_recb_env_ass['data_recebido'] >= '2023-01-01']

    print('Criando a coluna ano_mes...')
    df_recb_env_ass['ano_mes'] = df_recb_env_ass['data_recebido'].dt.strftime('%Y-%m')

    print('Convertendo a coluna "datahora" para o formato data desejado...')
    df_recb_env_ass['data_recebido'] = df_recb_env_ass['data_recebido'].dt.strftime('%d/%m/%Y')

    print('Ajustando a coluna captadora...')
    df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].fillna('VAZIO')
    df_recb_env_ass['captadora'] = df_recb_env_ass['captadora'].str.upper()

    print('Separando dataframe em 3...')
    recebidos = df_recb_env_ass[['codigo_contrato', 'captadora', 'ano_mes', 'data_recebido', 'valor']]
    enviados = df_recb_env_ass[['codigo_contrato', 'captadora', 'ano_mes', 'data_enviado', 'valor']]
    assinados = df_recb_env_ass[['codigo_contrato', 'captadora', 'ano_mes', 'data_assinado', 'valor']]

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
    relacionamento = pd.merge(recebidos, enviados, on=['ano_mes','captadora', 'codigo_contrato'], how='outer')
    relacionamento = pd.merge(relacionamento, assinados, on=['ano_mes','captadora', 'codigo_contrato'], how='outer')

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)
    sheet.clear_sheets(PAGINA_SHEETS)
    sheet.upload_to_sheets(relacionamento, PAGINA_SHEETS)

if __name__ == "__main__":
    main()