import dotenv
import pandas as pd
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Agora deve funcionar a importação do módulo utils
dotenv.load_dotenv()


def main_analise_credito():
    CODE_SHEETS_DASH_ANALISE_DE_CREDITO = os.getenv(
        "CODE_SHEETS_DASH_ANALISE_DE_CREDITO")
    PAGINA1_SHEETS = 'pretendendes'
    PAGINA2_SHEETS = 'parceiros'

    con = db.connect_to_db()
    cursor = con.cursor()
    sheet = Sheets(CODE_SHEETS_DASH_ANALISE_DE_CREDITO)

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

    sheet.clear_sheets(PAGINA1_SHEETS)
    sheet.upload_to_sheets(df_pretendentes, PAGINA1_SHEETS)

    sheet.clear_sheets(PAGINA2_SHEETS)
    sheet.upload_to_sheets(df_parceiros, PAGINA2_SHEETS)
    print("------------------- ATUALIZADO ----------------")


if __name__ == "__main__":
    main_analise_credito()
