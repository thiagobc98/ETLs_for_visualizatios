from utils import planilhas_transacionais
import codecs
import dotenv
import pandas as pd
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


dotenv.load_dotenv()

CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
PAGINA_SHEETS = 'ANALISES'

COLUMNS_ANALISES = ['nome_pretendente', 'documento_pretendente',  'profissao_pretendente', 'renda_pretendente', 'renda_presumida_pretendente', 'score_assertiva_pretendente',
                    'faixa_de_score', 'vinculo_empregaticio', 'resultado_analise_pretendente', 'id_parceiro', 'nome_parceiro', 'data_analise',  'valor_aluguel_analisado']

COLUMNS_CONTRATOS = {'Código do Contrato': 'codigo_contrato',
                     'Locatário': 'Locatário',
                     'Receb.': 'data_recebido',
                     'Envio': 'data_enviado',
                     'Assin.': 'data_assinado',
                     'Sistema': 'data_sistema',
                     'Captadora': 'captadora',
                     'Valor': 'valor'

                     }

sql_file_path = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'analises.sql')


def main():
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
        subset=['codigo_contrato', 'Locatário', 'valor'], keep='first')

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
                        'nome_pretendente'], right_on=['Locatário'])

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)
    sheet.clear_sheets(PAGINA_SHEETS)
    sheet.upload_to_sheets(df_merge, PAGINA_SHEETS)

    cursor.close()
    con.close()


if __name__ == "__main__":
    main()
