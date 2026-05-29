import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.sheets import Sheets
import pandas as pd
from unidecode import unidecode

import numpy as np
import dotenv
import os
dotenv.load_dotenv()


def main_cobrancas():
    CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")
    CODE_SHEETS_DASH_COBRANCAS = os.getenv("CODE_SHEETS_DASH_COBRANCAS")

    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('COBRANCA_AMIGAVEL')
    df_co_amigavel = pd.DataFrame(data[1:], columns=data[0])

    print('Removendo linhas sem contratos...')
    df_co_amigavel = df_co_amigavel[df_co_amigavel['Contrato'] != '']


    print('Removendo linhas sem 1o_lemb...')
    df_co_amigavel = df_co_amigavel[df_co_amigavel['1º Lemb'].str.strip() != '']


    print('Padronizando colunas...')
    def format_column_name(column_name):
        column_name = unidecode(column_name)  # Remove acentos
        column_name = column_name.lower()  # Converte para minúsculas
        column_name = column_name.replace(' ', '_')  # Substitui espaços por _
        return column_name

    df_co_amigavel.columns = [format_column_name(col) for col in df_co_amigavel.columns]

    print('Rename nas colunas...')
    rename_columns = {'contrato': 'codigo_contrato', 
                    'locatario': 'nome_locatario',
                    'x': 'reincidencia',
                    '1o_boleto?': '1o_boleto',
                    'situacao_da_cobranca': 'observacao_de_cobranca',
                    '5o_lembr': '5o_lemb',
                    'valor_total_do(s)_boleto(s)_em_aberto': 'valor_total_boleto_em_aberto', 
                    'data_de_vencimento_do_boleto': 'data_de_vencimento',
                    'data_de_previsao_de_pagamento_(acordo)': 'data_de_previsao_de_pagamento_acordo'}

    df_co_amigavel.rename(columns=rename_columns, inplace=True)


    print(' Padronizando o formato das datas na coluna data_de_vencimento...')
    def padronizar_data(data):
        # Tenta analisar a data no formato 'd/m/yyyy'
        try:
            data_formatada = pd.to_datetime(data, format='%d/%m/%Y')
        # Se não conseguir, tenta analisar no formato 'dd/mm/yyyy'
        except ValueError:
            data_formatada = pd.to_datetime(data, format='%d/%m/%Y')

        # Formata a data no formato 'dd/mm/yyyy'
        return data_formatada.strftime('%d/%m/%Y')

    # Aplicar a função de padronização à coluna 'data'
    # df_co_amigavel['data_de_vencimento'] = df_co_amigavel['data_de_vencimento'].apply(padronizar_data)
    df_co_amigavel['data_de_vencimento'] = pd.to_datetime(df_co_amigavel['data_de_vencimento'], format='%d/%m/%Y', errors='coerce')

    print('Rename canal...')
    df_co_amigavel.columns.values[11] = '1o_canal'
    df_co_amigavel.columns.values[13] = '2o_canal'
    df_co_amigavel.columns.values[15] = '3o_canal'
    df_co_amigavel.columns.values[17] = '4o_canal'
    df_co_amigavel.columns.values[19] = '5o_canal'
    df_co_amigavel.columns.values[21] = '6o_canal'

    # Substituir 'Preencher' na coluna '1o_canal' pelo valor correspondente na coluna '2o_canal'
    df_co_amigavel['1o_canal'] = np.where(df_co_amigavel['1o_canal'].str.strip() == 'Preencher', df_co_amigavel['2o_canal'], df_co_amigavel['1o_canal'])

    df_co_amigavel['sistema'] = df_co_amigavel['sistema'].str.strip().replace('', 'UP')

    print('Drop nas coluans...')
    df_co_amigavel.drop(['link_consulta_cadastral', 'observacao_de_cobranca', 'observacoes_de_acordo'], axis=1, inplace=True)

    print('Tratando reincidencia...')
    df_co_amigavel['reincidencia'] = df_co_amigavel['reincidencia'].str.extract('(\d+)')

    print('Tratando valor_total_boleto_em_aberto...')
    df_co_amigavel['valor_total_boleto_em_aberto'] = df_co_amigavel['valor_total_boleto_em_aberto'].str.replace('R$', '').str.strip()

    # Substituir valores vazios ('') por 'Não'
    df_co_amigavel['fraude'] = df_co_amigavel['fraude'].str.strip().replace('', 'Não')

    # Substituir valores '-' por 'Não'
    df_co_amigavel['fraude'] = df_co_amigavel['fraude'].str.strip().replace('-', 'Não')


    def processar_coluna_lemb(df, coluna_lemb):
        df[coluna_lemb] = df[coluna_lemb].str.strip().replace('', '01/01/2000')
        df[coluna_lemb] = df[coluna_lemb].str.strip().replace('pago', '01/01/2000')

    colunas_lemb = ['2o_lemb', '3o_lemb', '4o_lemb', '5o_lemb', '6o_lemb']

    for coluna in colunas_lemb:
        processar_coluna_lemb(df_co_amigavel, coluna)

    df_co_amigavel['data_de_pagamento'] = df_co_amigavel['data_de_pagamento'].str.strip().replace('', 'em aberto')
    df_co_amigavel['data_de_pagamento'] = df_co_amigavel['data_de_pagamento'].str.strip().replace('em aberto', '')


    df_co_amigavel['data_repasse_extrajudicial'] = df_co_amigavel['data_repasse_extrajudicial'].str.strip().replace('', '01/01/2000')

    sheet.set_code_sheets(CODE_SHEETS_DASH_COBRANCAS)
    sheet.clear_and_upload(df_co_amigavel, 'COBRANCA_AMIGAVEL')


    columns_extrajudicial = ['sistema', 'seguro', 'contrato', 'locatario ', 'Locatário 2', 'fraude', 'telefone', 'contato', 'data_ligacao', 'retornou_ligacao', 'data_whatsapp', 'retornou_whatsapp', 'data_carta', 'retornou_carta', 'negativacao_do_locatario', 'boletos_em_aberto', 'valor_boleto', 'observacoes', 'acordo_foi_firmado', 'data_acordo', 'valor_recuperado','chaves', 'inadimplentes']

    CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")

    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('COBRANCA_JUDICIAIS')
    df_co_judiciais = pd.DataFrame(data[1:], columns=columns_extrajudicial)

    df_co_judiciais.drop(columns='Locatário 2', inplace=True)

    # Substituir espaços em branco e strings vazias por NaN
    df_co_judiciais['contrato'].replace({'': pd.NA, ' ': pd.NA}, inplace=True)
    df_co_judiciais.dropna(subset=['contrato'], inplace=True)


    df_co_judiciais['fraude'] = df_co_judiciais['fraude'].apply(lambda x: 'Não' if pd.isnull(x) or x.strip() == '' else x)

    df_co_judiciais['data_ligacao'] = df_co_judiciais['data_ligacao'].replace('-', '')
    df_co_judiciais['retornou_ligacao'] = df_co_judiciais['retornou_ligacao'].replace('-', '')
    df_co_judiciais['data_whatsapp'] = df_co_judiciais['data_whatsapp'].replace('-', '')
    df_co_judiciais['retorno_whatsapp'] = df_co_judiciais['retornou_whatsapp'].replace('-', '')
    df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace('-', '')
    df_co_judiciais['retornou_carta'] = df_co_judiciais['retornou_carta'].replace('-', '')
    df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace('Não enviada', '')
    df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace('Nâo enviada ', '')
    df_co_judiciais['data_carta'] = df_co_judiciais['data_carta'].replace('Não enviada ', '')


    df_co_judiciais['boletos_em_aberto'] = df_co_judiciais['boletos_em_aberto'].replace('-', '')


    # df_co_judiciais['data_carta'] = pd.to_datetime(df_co_judiciais['data_carta'])
    # df_co_judiciais['data_whatsapp'] = pd.to_datetime(df_co_judiciais['data_whatsapp'])
    # df_co_judiciais['data_ligacao'] = pd.to_datetime(df_co_judiciais['data_ligacao'])
    # df_co_judiciais['data_acordo'] = pd.to_datetime(df_co_judiciais['data_acordo'])

    CODE_SHEETS_DASH_COBRANCAS = os.getenv("CODE_SHEETS_DASH_COBRANCAS")

    sheet.set_code_sheets(CODE_SHEETS_DASH_COBRANCAS)
    sheet.clear_and_upload(df_co_judiciais, 'COBRANCA_JUDICIAIS')

if __name__ == "__main__":
    main_cobrancas()