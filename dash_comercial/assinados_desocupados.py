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
PAGINA_SHEETS = 'ASSINADOS_DESOCUPADOS'

def processar_desocupado():
    print('\n\t------>TRATANDO DADOS DESOCUPADO<------')
    df_desocupado = planilhas_transacionais.get_desocupado()
    print('Renomeando e pegando apenas as colunas do meu interresse...') 
    df_desocupado.rename(columns={'Código do contrato': 'codigo_contrato',
                                    'Data de desocupação': 'data_desocupacao'}, inplace=True)
    df_desocupado = df_desocupado[['codigo_contrato', 'data_desocupacao']]

    print('Converter a coluna "data_inicio_contrato" para o formato de data...') 
    df_desocupado['data_desocupacao'] = pd.to_datetime(df_desocupado['data_desocupacao'], format='%d/%m/%Y')

    print('Pegando datas só depois de 2023...') 
    df_desocupado = df_desocupado[df_desocupado['data_desocupacao'] >= '2023-01-01']
    df_desocupado['ano_mes'] = df_desocupado['data_desocupacao'].dt.to_period('M')


    print('Convertendo a coluna "datahora" para o tipo data desejado...')
    df_desocupado['data_desocupacao'] = df_desocupado['data_desocupacao'].dt.strftime('%d/%m/%Y')

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
    df_assinado['data_envio'] = df_assinado.apply(lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_assinado['data_recebido'] = df_assinado.apply(lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Converter a coluna "data_inicio_contrato" para o formato de data...') 
    df_assinado['data_recebido'] = pd.to_datetime(df_assinado['data_recebido'], format='%d/%m/%Y %H:%M:%S')


    print('Pegando datas só depois de 2023...') 
    # THIAGO ESSA PARTE NO OUTRO ESTAMOS FAZENDO COM A COLUNA DATA_DESOCUPAÇAO PQ AQUI FAZEMOS COM DATA_RECEBIDOS 
    df_assinado = df_assinado[df_assinado['data_recebido'] >= '2023-01-01']
    df_assinado['ano_mes'] = df_assinado['data_recebido'].dt.to_period('M')

    df_assinado = df_assinado[['codigo_contrato', 'data_assinado', 'ano_mes', 'valor']]
    return df_assinado


def main():
    print('\n\t------>ASSINADOS DESOCUPADOS<------\n')
    df_desocupado = processar_desocupado()
    df_assinado = processar_assinado()

    print('\n\nFazendo merge dos dois df...')
    relacionamento = pd.merge(df_assinado, df_desocupado, 
                              on=['ano_mes','codigo_contrato'], 
                              how='outer')

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)
    sheet.clear_sheets(PAGINA_SHEETS)
    sheet.upload_to_sheets(relacionamento, PAGINA_SHEETS)

if __name__ == "__main__":
    main()