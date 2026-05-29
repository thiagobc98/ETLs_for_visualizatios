import dotenv
import pandas as pd
from utils.sheets import Sheets
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


dotenv.load_dotenv()

CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
PAGINA_SHEETS_TODOS = 'SISTEMA_SUPERLOGICA'
PAGINA_SHEETS_ATIVOS = 'SISTEMA e SUPERLOGICA - ATIVOS'

COLUNAS_DESEJADAS = ['codigo_contrato', 'codigo_parceiro',
                     'nome_parceiro', 'valor_aluguel_contrato',
                     'name_status', 'data_inicio_contrato',
                     'data_desocupacao', 'tipo_parceiro', 'tipo_sistema',
                     'migracao', 'nome_produto', 'pontualizado']


superlogica_todos = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'superlogica_todos.csv')
sistema_todos = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_todos.csv')
concatenado_todos = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'concatenado_todos.csv')


def concatenar_todos() -> pd.DataFrame:
    print('\n\nCONCETENANDO TODOS SUPERLOGICA E SISTEMA')
    df_superlogica = pd.read_csv(superlogica_todos)
    df_sistema = pd.read_csv(sistema_todos)

    df_concatenado = pd.concat([df_sistema, df_superlogica])
    df_concatenado = df_concatenado[COLUNAS_DESEJADAS]

    df_concatenado.to_csv(concatenado_todos, index=False)
    print('CONCATENADOS TODOS COM SUCESSO!!!')
    return df_concatenado


def concatenar_ativos() -> pd.DataFrame:
    print('\n\nCONCETENANDO ATIVOS SUPERLOGICA E SISTEMA')
    df_superlogica = pd.read_csv(superlogica_todos)
    df_sistema = pd.read_csv(sistema_todos)

    df_concatenado = pd.concat([df_sistema, df_superlogica])
    df_concatenado = df_concatenado[COLUNAS_DESEJADAS]

    df_concatenado.to_csv(concatenado_todos, index=False)
    print('CONCATENADOS ATIVOS COM SUCESSO!!!')
    return df_concatenado


def main():
    print('\n\t------>CONCATENANDO<------\n')

    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)

    df_concatenado_todos = concatenar_todos()
    sheet.clear_sheets(PAGINA_SHEETS_TODOS)
    sheet.upload_to_sheets(df_concatenado_todos, PAGINA_SHEETS_TODOS)

    df_concatenado_ativos = concatenar_ativos()
    sheet.clear_sheets(PAGINA_SHEETS_ATIVOS)
    sheet.upload_to_sheets(df_concatenado_ativos, PAGINA_SHEETS_ATIVOS)


if __name__ == "__main__":
    main()
