import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from utils import planilhas_transacionais 
from datetime import datetime
from utils.planilhas_transacionais import get_contratos
import pandas as pd

def tranto_contratos():
    df_contratos =  get_contratos()

    print('Excluindo as 57 primeiras linhas...') 
    df_contratos = df_contratos.iloc[1437:] # partir daqui tem horas 

    print('Pegando apenas colunas a se utilizar...')
    df_contratos = df_contratos[['Código do Contrato', 'Receb.', 
                                'Envio', 'Assin.', 'Sistema', 
                                'Gr. Boleto', 'Captadora', 'Valor',
                                'Preencher com "SIM"']]

    print('Renomeando colunas...')
    df_contratos.rename(columns={'Código do Contrato': 'codigo_contrato',
                                'Receb.': 'data_recebido', 
                                'Envio': 'data_envio', 
                                'Assin.': 'data_assinado', 
                                'Sistema': 'data_sistema', 
                                'Gr. Boleto': 'data_primeiro_boleto', 
                                'Captadora': 'captadora', 
                                'Valor': 'valor_aluguel', 
                                'Preencher com "SIM"': 'contrato_cancelado'}, inplace=True)
    
    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_contratos['data_envio'] = df_contratos.apply(lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Trativas de preenchimento errado das menians de contratos em data_primeiro_boleto...')
    df_contratos['data_primeiro_boleto'] = df_contratos['data_primeiro_boleto'].replace(['-', 'Pendente', 'Bruna', 'Pendente ', 'pendente ', 'penente', 'pendente iptu','pendete'], '')

    print('Converter todos os Sim em maiúsculas...')
    df_contratos['contrato_cancelado'] = df_contratos['contrato_cancelado'].str.upper()

    print('Trativa se alguma coluna tiver vazia e ter data em alguma coluna seguite...')
    df_contratos['data_sistema'] = df_contratos.apply(lambda row: row['data_primeiro_boleto'] if row['data_sistema'] == '' else row['data_sistema'], axis=1)
    df_contratos['data_assinado'] = df_contratos.apply(lambda row: row['data_sistema'] if row['data_assinado'] == '' else row['data_assinado'], axis=1)
    df_contratos['data_envio'] = df_contratos.apply(lambda row: row['data_assinado'] if row['data_envio'] == '' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(lambda row: row['data_envio'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

    print('Excluindo linhas que não tem nehuma data_preenchida...')
    df_contratos = df_contratos[df_contratos['data_recebido'] != '']

    print('Tratando valor_aluguel para o padrão sheets...')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace('', None)
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].str.replace('R$', '').str.replace(' ', '')

    print('ERROS das meninas de contratos!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace('R$3,900,00', '3.900,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace('R$ 2,500,00', '2.500,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace('1.000.00', '1.000,00') 


    df_contratos.drop(['valor_aluguel', 'contrato_cancelado'], axis=1, inplace=True)

    print('Tratando erros das meninas de contratos (colocaram - e Pendente em coluna de Data)')
    colunas_para_tratar = ['data_primeiro_boleto', 'data_sistema']
    df_contratos[colunas_para_tratar] = df_contratos[colunas_para_tratar].replace(['pendente', '-', 'pendnete '], '')

    print('Passando colunas data_recebido, data_envio para datetime...')
    df_contratos['data_recebido'] = pd.to_datetime(df_contratos['data_recebido'], format='%d/%m/%Y %H:%M:%S')
    df_contratos['data_envio'] = pd.to_datetime(df_contratos['data_envio'], format='%d/%m/%Y %H:%M:%S')

    print('Passando colunas data_assinado, data_sistema, data_boleto para datetime...')
    df_contratos['data_assinado'].replace(" ", None, inplace=True)
    df_contratos['data_assinado'].replace("-", pd.NaT, inplace=True)
    df_contratos['data_sistema'].replace(" ", None, inplace=True)
    df_contratos['data_primeiro_boleto'].replace(" ", None, inplace=True)

    df_contratos['data_assinado'] = pd.to_datetime(df_contratos['data_assinado'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df_contratos['data_sistema'] = pd.to_datetime(df_contratos['data_sistema'], format='%d/%m/%Y %H:%M:%S')
    df_contratos['data_primeiro_boleto'] = pd.to_datetime(df_contratos['data_primeiro_boleto'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

    return df_contratos


def is_after_1800(datetime_value):
  time_1800 = datetime(datetime_value.year, datetime_value.month, datetime_value.day, 18, 0, 0)
  time_800 = datetime(datetime_value.year, datetime_value.month, datetime_value.day, 8, 0, 0)
  if (time_1800 < datetime_value) or (datetime_value < time_800): 
     return "Fora do horário comercial"

  return "Horário comercial"

df_contratos = tranto_contratos()

df_contratos.dropna(subset=['data_envio'], inplace= True)
df_contratos['horario_comercial'] = df_contratos.apply(lambda row: is_after_1800(row['data_recebido']), axis=1)

from utils.sheets import Sheets
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DASH_GERENCIAL = os.getenv("CODE_SHEETS_DASH_GERENCIAL")
PAGINA_SHEETS = 'CONTRATOS'

sheet = Sheets(CODE_SHEETS_DASH_GERENCIAL)
sheet.clear_and_upload(df_contratos, PAGINA_SHEETS)