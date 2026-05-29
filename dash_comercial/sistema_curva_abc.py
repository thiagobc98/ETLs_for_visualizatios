from numpy import int64
import pandas as pd
from utils import planilhas_transacionais
from utils.utils import create_cod_to_merge
import dotenv
from utils.sheets import Sheets
import utils.mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


sistema_ativos_curva_abc_monetario = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_ativos_curva_abc_monetario.sql')
sistema_ativos_curva_abc_numerico = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_ativos_curva_abc_numerico.sql')
sistema_todos_curva_abc_num = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_todos_curva_abc_num.sql')
sistema_todos_curva_abc_mon = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_todos_curva_abc_mon.sql')
sistema_ativos_curva_abc_monetario_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_ativos_curva_abc_monetario.csv')
sistema_todos_curva_abc_mon_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_todos_curva_abc_mon.csv')
sistema_ativos_curva_abc_numerico_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_ativos_curva_abc_numerico.csv')
sistema_todos_curva_abc_num_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_todos_curva_abc_num.csv')


dotenv.load_dotenv()


CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
PAGINA_SHEETS_MON = 'CURVA ABC MONETÁRIO - ATIVOS'
PAGINA_SHEETS_NUM = 'CURVA ABC NUMÉRICOS - ATIVOS'
PAGINA_SHEETS_TODOS_MON = 'CURVA ABC MONETÁRIO - TODOS'
PAGINA_SHEETS_TODOS_NUM = 'CURVA ABC NUMÉRICOS - TODOS'


COLUMNS_SISTEMA_MON = [
    'nome_parceiro',
    'nome_produto',
    'count_contratos',
    'valor_aluguel',
    'valor_aluguel_acumulado',
    'date_inicio_contrato_mais_rescente',
    'porcentagem',
    'porcentagem_acumulada',
    'classe',
    'pontualizado']

COLUMNS_SISTEMA_NUM = [
    'nome_parceiro',
    'nome_produto',
    'count_contratos',
    'qtd_acumulado',
    'porcentagem',
    'porcentagem_acumulada',
    'classe',
    'date_inicio_contrato_mais_rescente',
    'pontualizado']


def processar_sistema_mon(df: pd.DataFrame, name_df: str) -> pd.DataFrame:

    df = df[['nome_parceiro', 'nome_produto', 'count_contratos', 'valor_aluguel',
             'valor_aluguel_acumulado',  'date_inicio_contrato_mais_rescente', 'porcentagem_acumulada', 'classe', 'pontualizado']]

    df['porcentagem_acumulada'] = pd.to_numeric(
        df['porcentagem_acumulada'])

    df['pontualizado'] = df['pontualizado'].astype(str)

    pd.options.display.float_format = '{:.2f}'.format

    return df


def processar_sistema_num(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    df = df[['nome_parceiro', 'nome_produto', 'count_contratos',
             'qtd_acumulado', 'porcentagem', 'porcentagem_acumulada', 'classe', 'date_inicio_contrato_mais_rescente',  'pontualizado']]
    df['porcentagem'] = df['porcentagem'].astype(float)
    df['porcentagem_acumulada'] = df['porcentagem_acumulada'].astype(float)
    df['pontualizado'] = df['pontualizado'].astype(str)
    pd.options.display.float_format = '{:.2f}'.format

    return df


def main():
    con = db.connect_to_db()
    cursor = con.cursor()

    print('\n\t------>CURVA-ABC ATIVOS MONETÁRIOS<------')
    results = db.execute_select_in_db(
        cursor, sistema_ativos_curva_abc_monetario)
    df_sistema_ativos_mon = pd.DataFrame(results, columns=COLUMNS_SISTEMA_MON)
    df_sistema_ativos_mon = processar_sistema_mon(df_sistema_ativos_mon, 'MON')
    df_sistema_ativos_mon.to_csv(
        sistema_ativos_curva_abc_monetario_csv, index=False)

    print('\n\t------>SISTEMA-ATIVOS-NUMERICOS<------')
    results = db.execute_select_in_db(
        cursor, sistema_ativos_curva_abc_numerico)
    df_sistema_ativos_num = pd.DataFrame(results, columns=COLUMNS_SISTEMA_NUM)
    df_sistema_ativos_num = processar_sistema_num(df_sistema_ativos_num, 'NUM')
    df_sistema_ativos_num.to_csv(
        sistema_ativos_curva_abc_numerico_csv, index=False)

    print('\n\t------>CURVA-ABC TODOS MONETÁRIOS<------')
    results = db.execute_select_in_db(cursor, sistema_todos_curva_abc_mon)
    df_sistema_mon = pd.DataFrame(results, columns=COLUMNS_SISTEMA_MON)
    df_sistema_mon = processar_sistema_mon(df_sistema_mon, 'MON')
    df_sistema_mon.to_csv(sistema_todos_curva_abc_mon_csv, index=False)

    print('\n\t------>SISTEMA-TODOS-NUMERICOS<------')
    results = db.execute_select_in_db(cursor, sistema_todos_curva_abc_num)
    df_sistema_num = pd.DataFrame(results, columns=COLUMNS_SISTEMA_NUM)
    df_sistema_num = processar_sistema_num(df_sistema_num, 'NUM')
    df_sistema_num.to_csv(sistema_todos_curva_abc_num_csv, index=False)

    cursor.close()
    con.close()

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)

    sheet.clear_sheets(PAGINA_SHEETS_MON)
    sheet.upload_to_sheets(df_sistema_ativos_mon, PAGINA_SHEETS_MON)

    sheet.clear_sheets(PAGINA_SHEETS_NUM)
    sheet.upload_to_sheets(df_sistema_ativos_num, PAGINA_SHEETS_NUM)

    sheet.clear_sheets(PAGINA_SHEETS_TODOS_MON)
    sheet.upload_to_sheets(df_sistema_mon, PAGINA_SHEETS_TODOS_MON)

    sheet.clear_sheets(PAGINA_SHEETS_TODOS_NUM)
    sheet.upload_to_sheets(df_sistema_num, PAGINA_SHEETS_TODOS_NUM)


if __name__ == "__main__":
    main()
