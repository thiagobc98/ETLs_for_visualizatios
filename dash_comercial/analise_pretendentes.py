import dotenv
import pandas as pd
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


dotenv.load_dotenv()

pretendentes_sem_solidarios = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'pretendentes_sem_solidarios.sql')

CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
PAGINA_SHEETS = 'ANALISE DE PRETENDENTES'
COLUMNS = ['id_parceiro',
           'nome_parceiro',
           'data_analise',
           'valor_aluguel_analisado',
           'Resultado_Analise_Pretendente',
           'nome_produto']


def main():
    print('\n\t------>ANALISE PRETENDENTES<------\n')
    con = db.connect_to_db()
    cursor = con.cursor()

    results = db.execute_select_in_db(cursor, pretendentes_sem_solidarios)
    df_analise = pd.DataFrame(results, columns=COLUMNS)

    df_analise['Resultado_Analise_Pretendente'] = df_analise['Resultado_Analise_Pretendente'].apply(
        lambda x: x.encode('latin1').decode('utf8') if isinstance(x, str) else x)

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)
    sheet.clear_sheets(PAGINA_SHEETS)
    sheet.upload_to_sheets(df_analise, PAGINA_SHEETS)

    cursor.close()
    con.close()


if __name__ == "__main__":
    main()
