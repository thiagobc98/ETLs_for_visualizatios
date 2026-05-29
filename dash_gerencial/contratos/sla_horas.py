import pandas as pd
from datetime import datetime, timedelta
from workalendar.america import Brazil 

from utils.sheets import Sheets
import fluxo_contratos 

import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DASH_COTRATOS = os.getenv("CODE_SHEETS_DASH_CONTRATOS")
PAGINA_SHEETS = 'base_sla_horas'

PRIVIOUS_YEAR_HOLIDAYS  = [(datetime(date.year, date.month, date.day), holiday) for date, holiday in Brazil().holidays(datetime.now().year -1)]
CURRENT_YEAR_HOLIDAYS = [(datetime(date.year, date.month, date.day), holiday) for date, holiday in Brazil().holidays(datetime.now().year)]
HOLIDAYS = PRIVIOUS_YEAR_HOLIDAYS + CURRENT_YEAR_HOLIDAYS

TIME_START_OF_DAY = 8
TIME_END_OF_DAY = 18
WORK_SECONDS = 9 * 3600

def is_holiday(date):
    return date.date() in HOLIDAYS

def validate_time(date_time):
    end_of_day = datetime(date_time.year, date_time.month, date_time.day, 18, 0, 0)
    if date_time.time() > end_of_day.time():
        date_time += timedelta(days=1)
        while date_time.weekday() in [5, 6] or is_holiday(date_time):
            date_time += timedelta(days=1)
        date_time = date_time.replace(hour=8, minute=0, second=0)
    return date_time

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

def count_seconds_passed_in_day_step01(start_date):
    start_time = datetime(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, start_date.second)
    end_time = datetime(start_date.year, start_date.month, start_date.day, TIME_END_OF_DAY, 0, 0)
    seconds_passed_in_day = (end_time - start_time).total_seconds()
    return seconds_passed_in_day

def count_seconds_passed_in_day_step02(finished_date):
    finished_time = datetime(finished_date.year, finished_date.month, finished_date.day, finished_date.hour, finished_date.minute, finished_date.second)
    start_time = datetime(finished_date.year, finished_date.month, finished_date.day, TIME_START_OF_DAY, 0, 0)
    seconds_passed_in_day = (finished_time - start_time).total_seconds() 
    return seconds_passed_in_day

def calculate_sla(index, row, step01, step02):
    sla_seconds = None
    step1_date = row[step01]
    step2_date = row[step02]

    if not pd.isna(step1_date) and not pd.isna(step2_date):
        step1_date = validate_time(row[step01])
        step2_date = validate_time(row[step02])

        days_difference = (step2_date.replace(hour=0, minute=0, second=0) - step1_date.replace(hour=0, minute=0, second=0)).days -1

        if days_difference == -1:  # Se aconteceu no mesmo dia
            sla_seconds = (step2_date - step1_date).total_seconds() 
        elif days_difference == 0:  # Se aconteceu de um dia para o outro
            seconds_worked_in_day_step01 = count_seconds_passed_in_day_step01(step1_date)
            seconds_worked_in_day_step02 = count_seconds_passed_in_day_step02(step2_date)

            sla_seconds = seconds_worked_in_day_step01 + seconds_worked_in_day_step02
        else:
            seconds_worked_in_day_step01 = count_seconds_passed_in_day_step01(step1_date)
            seconds_worked_in_day_step02 = count_seconds_passed_in_day_step02(step2_date)

            # Conte os sábados e domingos e feriados entre as datas de início e término do trabalho
            counted_weekend_days = count_weekends_date(step1_date, step2_date)
            counted_holidays = count_holidays(step1_date, step2_date)

            working_days = days_difference - (counted_weekend_days + counted_holidays)
            working_seconds = working_days * WORK_SECONDS

            sla_seconds = seconds_worked_in_day_step01 + seconds_worked_in_day_step02 + working_seconds
    return sla_seconds


def get_contratos_tratados():
    df = fluxo_contratos.tranto_contratos()
    return df

def gerando_sla_horas(df):
    print('Pegando contratos apenas da linha 1380 para frente...')
    df = df[1380:].copy()
    df.drop(['valor_aluguel', 'contrato_cancelado'], axis=1, inplace=True)

    print('Passando colunas data_recebido, data_envio para datetime...')
    df['data_recebido'] = pd.to_datetime(df['data_recebido'], format='%d/%m/%Y %H:%M:%S')
    df['data_envio'] = pd.to_datetime(df['data_envio'], format='%d/%m/%Y %H:%M:%S')

    print('Passando colunas data_assinado, data_sistema, data_boleto para datetime...')
    df['data_assinado'].replace(" ", None, inplace=True)
    df['data_sistema'].replace(" ", None, inplace=True)
    df['data_primeiro_boleto'].replace(" ", None, inplace=True)

    df['data_assinado'] = pd.to_datetime(df['data_assinado'], format='%d/%m/%Y %H:%M:%S')
    df['data_sistema'] = pd.to_datetime(df['data_sistema'], format='%d/%m/%Y %H:%M:%S')
    df['data_primeiro_boleto'] = pd.to_datetime(df['data_primeiro_boleto'], format='%d/%m/%Y %H:%M:%S')

    print('Calculando o sla em segundos!!!...')
    df['sla_recebido_enviado'] = df.apply(lambda row: calculate_sla(row.name, row, 'data_recebido', 'data_envio'), axis=1)
    df['sla_enviado_assinado'] = df.apply(lambda row: calculate_sla(row.name, row, 'data_envio', 'data_assinado'), axis=1)
    df['sla_assinado_sistema'] = df.apply(lambda row: calculate_sla(row.name, row, 'data_assinado', 'data_sistema'), axis=1)
    df['sla_sistema_boleto'] = df.apply(lambda row: calculate_sla(row.name, row, 'data_sistema', 'data_primeiro_boleto'), axis=1)

    print('Limpando linhas NaN e resetando index...')
    df.dropna(subset=['sla_recebido_enviado'], inplace= True)
    df.reset_index(inplace=True, drop=True)

    print('Dropando colunas que não vou usar no dash...')
    df.drop(['data_envio', 'data_assinado', 'data_sistema', 'data_primeiro_boleto'], axis=1, inplace=True)
    return df

def upload_sheets(df_contratos):
    sheet = Sheets(CODE_SHEETS_DASH_COTRATOS)
    sheet.clear_and_upload(df_contratos, PAGINA_SHEETS)

def main():
    df = get_contratos_tratados()
    df = gerando_sla_horas(df)
    upload_sheets(df)
    return df

if __name__ == "__main__":
    df_contratos = main()