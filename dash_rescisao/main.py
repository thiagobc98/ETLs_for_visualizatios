import sys
import os
# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.sheets import Sheets
import pandas as pd 
from unidecode import unidecode
import dotenv
import os
dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")
CODE_SHEETS_DASH_RESCISAO = os.getenv("CODE_SHEETS_DASH_RESCISAO")
PAGINA_SHEETS = 'DEVOLUCAO_CHAVES'


def verifica_envio_juridico(valor):
    if valor == 'Jurídico':
        return 1
    else:
        return 0

def verifica_envio_unidade(valor):
    if valor == 'Unidade':
        return 1
    else:
        return 0

def verifica_envio_juridico_unidade(valor):
    if valor == 'Jurídico/Unidade':
        return 1
    else:
        return 0
    
def verifica_envio_para_rescisao(valor):
    if pd.notna(valor):  # Verifica se o valor não é NaN
        try:
            pd.to_datetime(valor, format='%d/%m/%Y')
            return 1
        except ValueError:
            pass
    return 0


def main_recisao():
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('DEVOLUCAO_CHAVES')
    df_desocupado = pd.DataFrame(data[1:], columns=data[0])

    print('Cortando dataframe na linhda 217...')
    df_desocupado = df_desocupado[217:] # Só usar depois da linhas 219 planilha (aqui fica 217)
    # df_desocupado.reset_index(drop=True, inplace=True)

    df_desocupado = df_desocupado.rename(columns={'Motivo/Tipo de Rescisão':'Motivo_da_devolucao'})

    print('Tirando linhas vazios...')
    df_desocupado = df_desocupado[df_desocupado['Código do contrato'].str.len() > 1]

    def format_column_name(column_name):
        column_name = unidecode(column_name)  # Remove acentos
        column_name = column_name.lower()  # Converte para minúsculas
        column_name = column_name.replace(' ', '_')  # Substitui espaços por _
        column_name = column_name.replace('-', '_') # substitui - por _
        return column_name

    print('Renomeando as colunas...')
    df_desocupado.columns = [format_column_name(col) for col in df_desocupado.columns]

    print('Pegando apenas as colunas que vou usar...')
    df_desocupado = df_desocupado[['codigo_do_contrato', 
                                'data_de_desocupacao', 
                                'tipo_de_seguro', 
                                'documento_de_rescisao_enviado', 
                                'motivo_da_devolucao', 
                                'unidade_captadora', 
                                'valor_da_multa',
                                'valor_da_administradora',
                                'status_financeira_na_devolucao_da_posse',
                                'ultimo_boleto_de_aluguel_quitado',
                                'data_que_o_contrato_foi_pausado',
                                'data_de_envio_do_link_pela_imobiliaria', 
                                'data_do_envio_da_rescisao']]

    print("Tratando Valores na coluna 'valor_multa' e 'valor_da_administradora'...")
    df_desocupado['valor_da_multa'] = df_desocupado['valor_da_multa'].replace('-', None).str.replace('R$', '').str.replace(' ', '')
    df_desocupado['valor_da_administradora'] = df_desocupado['valor_da_administradora'].replace('-', None).str.replace('R$', '').str.replace(' ', '')


    # Crie a nova coluna usando a função apply
    df_desocupado['enviado_para_rescisao'] = df_desocupado['data_do_envio_da_rescisao'].apply(lambda x: verifica_envio_para_rescisao(x))
    df_desocupado['enviado_para_juridico'] = df_desocupado['data_do_envio_da_rescisao'].apply(lambda x: verifica_envio_juridico(x))
    df_desocupado['enviado_para_unidade'] = df_desocupado['data_do_envio_da_rescisao'].apply(lambda x: verifica_envio_unidade(x))
    df_desocupado['enviado_para_juridico_unidade'] = df_desocupado['data_do_envio_da_rescisao'].apply(lambda x: verifica_envio_juridico_unidade(x))



    sheet.set_code_sheets(CODE_SHEETS_DASH_RESCISAO)
    sheet.clear_and_upload(df_desocupado, 'RESCISAO')

if __name__ == "__main__":
    main_recisao()