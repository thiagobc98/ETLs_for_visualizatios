import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from utils import planilhas_transacionais 
from utils.sheets import Sheets
from utils.planilhas_transacionais import get_contratos
from datetime import datetime
import pandas as pd

import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")


def tranto_contratos():
    df_contratos = get_contratos()

    print('Excluindo as 57 primeiras linhas...') 
    df_contratos = df_contratos.iloc[57:] # Não são mais utilizadas

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
    df_contratos['data_primeiro_boleto'] = df_contratos['data_primeiro_boleto'].replace(['-', 'Pendente'], '')

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
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace('1.000.00', '1.000,00') # Não passei para as meninas de contratos, fiquei com vergonha

    print('Tratando erros das meninas de contratos (colocaram - e Pendente em coluna de Data)')
    colunas_para_tratar = ['data_primeiro_boleto', 'data_sistema']
    df_contratos[colunas_para_tratar] = df_contratos[colunas_para_tratar].replace(['pendente', '-'], '')

    return df_contratos

df_contratos = tranto_contratos()

from datetime import datetime, timedelta
from workalendar.america import Brazil 

PRIVIOUS_YEAR_HOLIDAYS  = [(datetime(date.year, date.month, date.day), holiday) for date, holiday in Brazil().holidays(datetime.now().year -1)]
CURRENT_YEAR_HOLIDAYS = [(datetime(date.year, date.month, date.day), holiday) for date, holiday in Brazil().holidays(datetime.now().year)]
HOLIDAYS = PRIVIOUS_YEAR_HOLIDAYS + CURRENT_YEAR_HOLIDAYS



def is_holiday(date):
    return date.date() in HOLIDAYS


def count_weekends_date(start_date, end_date):
    counted_days = 0
    day = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in [5, 6]:  # 5 é sábado e 6 é domingo
            counted_days += 1
        current_date += day
    return counted_days

def count_holidays(start_date, end_date):
    worked_on_holiday = 0
    for holiday_date, holiday_name in HOLIDAYS:
        # Verifique se alguma data de feriado cai entre a data de início e a data de término do trabalho
        if start_date <= holiday_date <= end_date:
            worked_on_holiday += 1
    return worked_on_holiday

# Qtd de contratos que foram recebidos em dia de feriado

df_contratos['data_recebido'] = pd.to_datetime(
    df_contratos['data_recebido'],
    dayfirst=True,
    errors='coerce'
)
# Converter a coluna 'data_recebido' para datetime, se ainda não for
holidays_dates = [date.strftime('%Y-%m-%d') for date, _ in HOLIDAYS] # Obter a lista de datas de feriado em formato string 'YYYY-MM-DD'
df_contratos['feriado'] = df_contratos['data_recebido'].dt.strftime('%Y-%m-%d').isin(holidays_dates) # Verificar se cada data na coluna 'data_recebido' está na lista de feriados
df_contratos['feriado'] = df_contratos['feriado'].apply(lambda x: 'Sim' if x else 'Não') # Converter os valores True/False para 'Sim'/'Não'

# Qtd de contratos que foram recebidos em finais de semana

def is_weekend(date):
    return date.weekday() in [5, 6]

df_contratos['data_recebido'] = pd.to_datetime(df_contratos['data_recebido'])
df_contratos['final_de_semana'] = df_contratos['data_recebido'].apply(is_weekend) 
df_contratos['final_de_semana'] = df_contratos['final_de_semana'].apply(lambda x: 'Sim' if x else 'Não') # Converter os valores True/False para 'Sim'/'Não'

CODE_SHEETS_DASH_GERENCIAL = os.getenv("CODE_SHEETS_DASH_GERENCIAL")
PAGINA_SHEETS = 'CONTRATOS_2'

sheet = Sheets(CODE_SHEETS_DASH_GERENCIAL)
sheet.clear_and_upload(df_contratos, PAGINA_SHEETS)