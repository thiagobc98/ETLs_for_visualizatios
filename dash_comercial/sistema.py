import pandas as pd
from utils.utils import create_cod_to_merge
from utils import planilhas_transacionais
from utils.sheets import Sheets
import dotenv
import utils.mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


dotenv.load_dotenv()
sistema_todos = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_todos.sql')
sistema_ativos = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'sql', 'sistema_ativos.sql')
sistema_todos_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_todos.csv')
sistema_ativos_csv = os.path.join(os.path.dirname(
    __file__), '..', 'dash_comercial', 'data', 'sistema_ativos.csv')


COLUMNS_SISTEMA = ['codigo_contrato',
                   'nome_parceiro',
                   'date_inicio_contrato',
                   'meses_duracao_contrato',
                   'valor_aluguel_contrato',
                   'taxa_contrato',
                   'taxa_admin_contrato',
                   'name_status',
                   'nome_produto',
                   'migracao',
                   'pontualizado']


def add_coluns_from_sheets(df: pd.DataFrame,  name_df: str) -> pd.DataFrame:
    df_parceiros = planilhas_transacionais.get_parceiros_to_sistema()
    df_desocupado = planilhas_transacionais.get_desocupado()

    print(f'Criando cod_to_merge  {name_df}')
    df['cod_to_merge_parceiros'] = df['nome_parceiro'].apply(
        create_cod_to_merge)
    df['cod_to_merge_desocupado'] = df['codigo_contrato'].apply(
        create_cod_to_merge)

    print(
        f'Passando o codigo_parceiro com base no cod_to_merge de parceiros...  {name_df}')
    df['codigo_parceiro'] = df['cod_to_merge_parceiros'].map(
        df_parceiros.set_index('cod_to_merge')['Cod Parceiro'])

    print(
        f'Passando Tipo_parceiro com base no cod_to_merge de parceiros...  {name_df}')
    df['tipo_parceiro'] = df['cod_to_merge_parceiros'].map(
        df_parceiros.set_index('cod_to_merge')['Tipo de parceiro'])

    print(
        f'Passando data_desocupacaocom base no cod_to_merge de desocupado...  {name_df}')
    df['data_desocupacao'] = df['cod_to_merge_desocupado'].map(
        df_desocupado.set_index('cod_to_merge')['Data de desocupação'])

    print(f'deletando colunas cod_to_merge...  {name_df}')
    del df['cod_to_merge_parceiros']
    del df['cod_to_merge_desocupado']

    return df


def processar_sistema(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    df = add_coluns_from_sheets(df, name_df)

    print(f'Renomeando colunas e passando apenas as que precisso... {name_df}')
    df.rename(columns={'date_inicio_contrato': 'data_inicio_contrato',
                       'nome_parceiro': 'nome_parceiro',
                       'taxa_admin_contrato': 'porcentagem_taxa_administracao',
                       'valor_aluguel_contrato': 'valor_aluguel_contrato',
                       'codigo_contrato': 'codigo_contrato',
                       'codigo_parceiro': 'codigo_parceiro',
                       'data_desocupacao': 'data_desocupacao',
                       'name_status': 'name_status',
                       'meses_duracao_contrato': 'meses_duracao_contrato',
                       'taxa_contrato': 'taxa_contrato',
                       'tipo_parceiro': 'tipo_parceiro'}, inplace=True)

    df['tipo_sistema'] = 'sistema'

    df = df[['codigo_contrato', 'codigo_parceiro', 'nome_parceiro', 'valor_aluguel_contrato', 'taxa_contrato',
             'porcentagem_taxa_administracao', 'name_status', 'data_inicio_contrato',
             'meses_duracao_contrato', 'data_desocupacao', 'tipo_parceiro', 'tipo_sistema', 'nome_produto',
             'migracao', 'pontualizado']]
    df['meses_duracao_contrato'] = df['meses_duracao_contrato'].fillna(0)
    df['meses_duracao_contrato'] = df['meses_duracao_contrato'].astype(int)

    # df = df[~df['codigo_contrato'].str.startswith('S-')]
    df['migracao'] = df['migracao'].replace('NÃ£o', 'Nao')

    print(
        f'Formatando data_inicio_contrato para o formato desejado... {name_df}')
    df['data_inicio_contrato'] = pd.to_datetime(
        df['data_inicio_contrato']).dt.strftime('%d/%m/%Y')

    return df


def main():
    con = db.connect_to_db()
    cursor = con.cursor()
    CODE_SHEETS_DASH_COMERCIAL = os.getenv("CODE_SHEETS_DASH_COMERCIAL")
    SISTEMA_SUPERLOGICA = 'SISTEMA_SUPERLOGICA'
    SISTEMA_SUPERLOGICA_ATIVOS = 'SISTEMA e SUPERLOGICA - ATIVOS'
    sheet = Sheets(CODE_SHEETS_DASH_COMERCIAL)

    print('\n\t------>SISTEMA-TODOS<------')
    results = db.execute_select_in_db(cursor, sistema_todos)
    df_sistema = pd.DataFrame(results, columns=COLUMNS_SISTEMA)
    df_sistema = processar_sistema(df_sistema, 'Todos')
    df_sistema.to_csv(sistema_todos_csv, index=False)
    sheet.clear_sheets(SISTEMA_SUPERLOGICA)
    sheet.upload_to_sheets(df_sistema, SISTEMA_SUPERLOGICA)

    print('\n\t------>SISTEMA-ATIVOS<------')
    results = db.execute_select_in_db(cursor, sistema_ativos)
    df_sistema_ativos = pd.DataFrame(results, columns=COLUMNS_SISTEMA)
    df_sistema_ativos = processar_sistema(df_sistema_ativos, 'ATIVOS')
    df_sistema_ativos.to_csv(sistema_ativos_csv, index=False)
    sheet.clear_sheets(SISTEMA_SUPERLOGICA_ATIVOS)
    sheet.upload_to_sheets(df_sistema_ativos, SISTEMA_SUPERLOGICA_ATIVOS)

    cursor.close()
    con.close()


if __name__ == "__main__":
    main()
