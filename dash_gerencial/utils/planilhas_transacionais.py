#from .utils import create_cod_to_merge 
from .sheets import Sheets
import pandas as pd 
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")

def get_contratos():
    print('\n\nLENDO DADOS_TRANSACIONAIS - CONTRATOS...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('CONTRATOS')
    df_contratos = pd.DataFrame(data[1:], columns=data[0])
    print('Tirando linhas vazias...')
    df_contratos = df_contratos[df_contratos['Código do Contrato'] != '']
    df_contratos = df_contratos.dropna(subset=['Código do Contrato'])
    return df_contratos

def get_rescisao():
    print('\n\nLENDO DADOS_TRANSACIONAIS - DEVOLUCAO_CHAVES...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('DEVOLUCAO_CHAVES')
    df_desocupado = pd.DataFrame(data[1:], columns=data[0])
    print('Cortando dataframe na linhda 217...')
    df_desocupado = df_desocupado[217:] 

    print('Tirando linhas vazios...')
    df_desocupado = df_desocupado[df_desocupado['Código do contrato'].str.len() > 1]
    return df_desocupado
