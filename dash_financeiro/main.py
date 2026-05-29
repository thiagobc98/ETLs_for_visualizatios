import dotenv
import pandas as pd
import datetime
from utils.sheets import Sheets
from utils import mysql_db as db
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


dotenv.load_dotenv()

CODE_SHEETS_DASH_FINANCEIRO_1 = os.getenv("CODE_SHEETS_DASH_FINANCEIRO_1")
CODE_SHEETS_DASH_FINANCEIRO_2 = os.getenv("CODE_SHEETS_DASH_FINANCEIRO_2")
CODE_SHEETS_DASH_FINANCEIRO_3 = os.getenv("CODE_SHEETS_DASH_FINANCEIRO_3")
CODE_SHEETS_DASH_FINANCEIRO_4 = os.getenv("CODE_SHEETS_DASH_FINANCEIRO_4")
CODE_SHEETS_DASH_FINANCEIRO_5 = os.getenv("CODE_SHEETS_DASH_FINANCEIRO_5")

SHEET_1 = Sheets(CODE_SHEETS_DASH_FINANCEIRO_1)
SHEET_2 = Sheets(CODE_SHEETS_DASH_FINANCEIRO_2)
SHEET_3 = Sheets(CODE_SHEETS_DASH_FINANCEIRO_3)
SHEET_4 = Sheets(CODE_SHEETS_DASH_FINANCEIRO_4)
SHEET_5 = Sheets(CODE_SHEETS_DASH_FINANCEIRO_5)


def time_start_pipeline():
    start_time = datetime.datetime.now()
    print("\n\nInício do pipeline:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return start_time


def time_end_pipeline(start_time):
    end_time = datetime.datetime.now()
    print("Fim do pipeline:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    elapsed_time = end_time - start_time
    print("Tempo decorrido:", str(elapsed_time).split(".")[0])


def get_data_financeiro(cursor, bloco: str, colunas: list):
    print(f'Lendo SQL {bloco}...')
    results = db.execute_select_in_db(
        cursor, f'dash_financeiro/sql/{bloco}.sql')
    df = pd.DataFrame(results, columns=colunas)
    print(f'Dataframe {bloco} criado com sucesso!')
    return df


def pipe(cursor, bloco: str, pagina_sheet: str, colunas: list):
    df = get_data_financeiro(cursor, bloco, colunas)
    SHEET_1.clear_and_upload(df, pagina_sheet)
    print(f'Pipe {bloco} feita com sucesso!!!\n')


def pipe2(cursor, bloco: str, pagina_sheet: str, colunas: list):
    df = get_data_financeiro(cursor, bloco, colunas)
    SHEET_2.clear_and_upload(df, pagina_sheet)
    print(f'Pipe {bloco} feita com sucesso!!!\n')


def pipe3(cursor, bloco: str, pagina_sheet: str, colunas: list):
    df = get_data_financeiro(cursor, bloco, colunas)
    SHEET_3.clear_and_upload(df, pagina_sheet)
    print(f'Pipe {bloco} feita com sucesso!!!\n')


def pipe4(cursor, bloco: str, pagina_sheet: str, colunas: list):
    df = get_data_financeiro(cursor, bloco, colunas)
    SHEET_4.clear_and_upload(df, pagina_sheet)
    print(f'Pipe {bloco} feita com sucesso!!!\n')


def triplicar_linhas_e_manipular_valores_b4g1(df):
    df_triplicado = df.loc[df.index.repeat(3)].reset_index(drop=True)

    count = 0
    data = []
    valor_fatura = []
    valor_proprietario = []
    valor_parceiro = []

    for index, row in df_triplicado.iterrows():
        count += 1
        if count == 1:
            data.append(row['data_pagamento_fatura'])
            valor_fatura.append(row['valor_fatura'])
            valor_proprietario.append(0)
            valor_parceiro.append(0)
        elif count == 2:
            data.append(row['data_repasse_fatura'])
            valor_fatura.append(0)
            valor_proprietario.append(row['valor_repasse_proprietario'])
            valor_parceiro.append(0)
        else:
            data.append(row['data_repasse_parceiro'])
            valor_fatura.append(0)
            valor_proprietario.append(0)
            valor_parceiro.append(row['valor_repasse_parceiro'])
            count = 0

    df_triplicado['data'] = data
    df_triplicado['valor_fatura'] = valor_fatura
    df_triplicado['valor_repasse_proprietario'] = valor_proprietario
    df_triplicado['valor_repasse_parceiro'] = valor_parceiro

    return df_triplicado


def main_financeiro():

    time_start_time = time_start_pipeline()

    con = db.connect_to_db()
    cursor = con.cursor()

    print('BLOCO 01')
    pipe2(cursor=cursor, bloco='bloco01', pagina_sheet='Bloco01',
          colunas=['id_fatura', 'data_pagamento_fatura',
                   'pago_atraso_2_ou_mais', 'pago_atraso_1_mes',
                   'pago_no_mes', 'pago_antecipado_1_mes',
                   'valor_pago_fatura', 'codigo_contrato', 'nome_produto'])

    print('BLOCO 02')
    pipe3(cursor=cursor, bloco='bloco02', pagina_sheet='Bloco02',
          colunas=['codigo_contrato', 'id_contrato',
                   'id_fatura', 'nome_parceiro',
                   'name_status', 'adicional_fatura',
                   'status_repasse_fatura', 'data_pagamento_fatura',
                   'data_vencimento_fatura', 'valor_fatura',
                   'pagamento_em_aberto', 'pagamento_em_dia',
                   'pagamento_em_atraso', 'nome_produto'])

    print('BLOCO 03')
    df_bloco03 = get_data_financeiro(cursor, 'bloco03', ['nome_parceiro', 'status_fatura',
                                                         'valor_fatura', 'contratos_com_1_boleto_em_aberto',
                                                         'contratos_com_2_boletos_em_aberto',
                                                         'contratos_com_3_boletos_em_aberto',
                                                         'contratos_com_4_ou_mais_boletos_em_aberto',
                                                         'quantidade_de_boletos', 'status_contrato', 'nome_produto'])
    # df_bloco03['status_contrato'] = df_bloco03['status_contrato'].str.encode('latin-1').str.decode('utf-8')
    df_bloco03['status_contrato'] = df_bloco03['status_contrato'].str.encode(
        'latin-1', errors='replace').str.decode('utf-8', errors='replace')

    SHEET_3.clear_and_upload(df_bloco03, 'Bloco03')

    print('BLOCO 03 Monetário')
    df_bloco03_monetario = get_data_financeiro(cursor, 'bloco03_monetario', ['id_contrato', 'id_parceiro', 'nome_parceiro',
                                                                             'valor_fatura', 'status_fatura',
                                                                             'quantidade_de_boletos', 'valor_por_fatura_de_contrato', 'status_contrato', 'nome_produto'])
    # df_bloco03_monetario['status_contrato'] = df_bloco03_monetario['status_contrato'].str.encode('latin-1').str.decode('utf-8')
    df_bloco03['status_contrato'] = df_bloco03['status_contrato'].str.encode(
        'latin-1', errors='replace').str.decode('utf-8', errors='replace')
    SHEET_3.clear_and_upload(df_bloco03_monetario, 'Bloco03_monetario')

    print('BLOCO 04 Grafico 01')
    df_b4g1 = get_data_financeiro(cursor, 'bloco04_grafico01', ['nome_parceiro', 'name_status',
                                                                'adicional_fatura', 'status_repasse_fatura',
                                                                'valor_fatura', 'valor_repasse_proprietario',
                                                                'valor_repasse_parceiro', 'data_repasse_fatura',
                                                                'data_pagamento_fatura', 'data_repasse_parceiro'])

    df_bloco04_grafico01 = triplicar_linhas_e_manipular_valores_b4g1(df_b4g1)
    SHEET_5.clear_and_upload(df_bloco04_grafico01, 'Bloco04_grafico01')

    print('BLOCO 04 Grafico 02')
    pipe4(cursor=cursor, bloco='bloco04_grafico02', pagina_sheet='Bloco04_grafico02',
          colunas=['id_fatura', 'select', 'dt_fluxo', 'valor'])

    print('BLOCO 05 tablea 01')
    pipe(cursor=cursor, bloco='bloco05_tabela01', pagina_sheet='Bloco05_tabela01',
         colunas=['nome_parceiro', 'quantidade_total_de_contratos',
                  'boleto_em_aberto_em_atraso', 'quantidade_contratos_com_boletos_em_atraso',
                  'porcentagem_contratos_por_boletos_em_atraso'])

    print('BLOCO 05 tablea 02')
    pipe(cursor=cursor, bloco='bloco05_tabela02', pagina_sheet='Bloco05_tabela02',
         colunas=['nome_parceiro', 'quantidade_total_de_contratos',
                  'boleto_em_aberto_em_atraso', 'quantidade_contratos_com_boletos_em_atraso',
                  'porcentagem_contratos_por_boletos_em_atraso'])

    print('BLOCO 06 Grafico 1 e 2')
    pipe3(cursor=cursor, bloco='bloco06_grafico1e2', pagina_sheet='Bloco06_grafico1e2',
          colunas=['nome_parceiro', 'name_status',
                   'status_fatura', 'adicional_fatura',
                   'status_repasse_fatura', 'valor_fatura',
                   'valor_aluguel_contrato', 'data_repasse_fatura',
                   'data_vencimento_fatura', 'data_pagamento_fatura'])

    print('BLOCO 06 Grafico 03')
    pipe3(cursor=cursor, bloco='bloco06_grafico03', pagina_sheet='Bloco06_grafico03',
          colunas=['vencimento_fatura', 'taxa_boleto',
                   'taxa_ted_doc_pix', 'taxa_servico',
                   'taxa_administracao_parcela_up',
                   'taxa_contrato_parcela_up'])

    time_end_pipeline(time_start_time)


if __name__ == "__main__":
    main_financeiro()
