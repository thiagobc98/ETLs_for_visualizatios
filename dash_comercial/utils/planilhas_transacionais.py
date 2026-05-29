from .utils import create_cod_to_merge 
from .sheets import Sheets
import pandas as pd 
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")

def get_desocupado():
    print('\n\nLENDO DADOS_TRANSACIONAIS - DEVOLUCAO_CHAVES...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('DEVOLUCAO_CHAVES')
    df_desocupado = pd.DataFrame(data[1:], columns=data[0])

    print('Cortando dataframe na linhda 217...')
    df_desocupado = df_desocupado[217:] # Só usar depois da linhas 219 planilha (aqui fica 217)
    df_desocupado.reset_index(drop=True, inplace=True)

    print('Tirando vazios...')
    df_desocupado = df_desocupado[df_desocupado['Código do contrato'].str.len() > 1]

    print('Adicionando coluna cod_to_merge no  df_desocupado...')
    df_desocupado['cod_to_merge'] = df_desocupado['Código do contrato'].apply(create_cod_to_merge)

    return df_desocupado

def get_recebidos_enviados_assinados():
    print('\n\nLENDO DADOS_TRANSACIONAIS - RECEBIDOS_ENV_ASS...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('CONTRATOS')
    n_cols = max((len(row) for row in data[1:]), default=len(data[0]))
    df_recb_env_ass = pd.DataFrame(data[1:], columns=data[0][:n_cols])

    return df_recb_env_ass

def get_parceiros(name_coluna_parceiro: str):
    print('\n\nLENDO DADOS_TRANSACIONAIS - DIM_COD_PARCEIROS...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('DIM_COD_PARCEIROS')
    df_parceiros = pd.DataFrame(data[1:], columns=data[0])

    print(f'Deletando as linhas que tem - na coluna {name_coluna_parceiro}...')
    df_parceiros = df_parceiros.loc[(df_parceiros[[name_coluna_parceiro]] != "-").all(axis=1)]
    return df_parceiros

def get_parceiros_to_super_logica():
    df_parceiros = get_parceiros('Superlogica')

    print('Alterando o nome da Matriz para bater com o do superlogica...')
    df_parceiros['Superlogica'] = df_parceiros['Superlogica'].replace('Matriz (Up Gestao de Pagamentos Ltda)', 'Matriz')
    df_parceiros.drop_duplicates('Superlogica', inplace=True)# deletando as linhas que tem - na coluna Superlogica
    df_parceiros = df_parceiros.loc[(df_parceiros[['Superlogica']] != "-").all(axis=1)]

    print('Alterando o nome da Matriz para bater com o do superlogica...')
    df_parceiros['Superlogica'] = df_parceiros['Superlogica'].replace('Matriz (Up Gestao de Pagamentos Ltda)', 'Matriz')
    df_parceiros.drop_duplicates('Superlogica', inplace=True)

    print('Adicionando coluna cod_to_merge no  df_parceiros...')
    df_parceiros['cod_to_merge'] = df_parceiros['Superlogica'].apply(create_cod_to_merge)

    return df_parceiros

def get_parceiros_to_sistema():
    df_parceiros = get_parceiros('Parceiro no sistema UP')

    print('Pegando apenas as colunas que me interresa...')
    df_parceiros = df_parceiros[['Cod Parceiro', 'Parceiro no sistema UP', 'Tipo de parceiro']]

    print('Criando o cod_to_merge com base no nome do parceiro')
    df_parceiros['cod_to_merge'] = df_parceiros['Parceiro no sistema UP'].apply(create_cod_to_merge)

    print('Tirando os códigos duplicados')
    df_parceiros.drop_duplicates(subset='cod_to_merge', inplace=True)

    return df_parceiros

