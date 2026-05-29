import os
import sys
import traceback
from datetime import datetime
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from utils import sheets


hora_atual = datetime.now().strftime("%H:%M:%S")


project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# from dash_cobrancas.main import main_cobrancas
# from dash_comercial.main import main_comercial
# from dash_contratos.main import main_contratos
# from dash_financeiro.main import main_financeiro
# from dash_gerencial.main import main_gerencial
# from dash_rescisao.main import main_recisao
from googleapiclient.discovery import build
# from dash_analise_credito.main import main_analise_credito


marcador = os.getenv("Relatorio_Marcacao")
sheet_json = os.getenv("PATH_TOKEN_MASTER_LANE_SHEETS")
ATULIZACAO_DA_DATA = os.getenv("ATULIZACAO_DA_DATA")
sheet_json = os.getenv("PATH_TOKEN_MASTER_LANE_SHEETS")
sheet = sheets.Sheets(ATULIZACAO_DA_DATA)

def authenticate_google_services(credentials_file):
    """Autentica e retorna os clientes do Google Sheets e Google Drive"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
    
    client_sheets = gspread.authorize(credentials)  # Cliente para Google Sheets
    client_drive = build("drive", "v3", credentials=credentials)  # Cliente para Google Drive

    return client_sheets, client_drive

client_sheets, client_drive = authenticate_google_services(sheet_json)


print(f"ID da planilha de data (ATULIZACAO_DA_DATA): {ATULIZACAO_DA_DATA}")
print(f"Valor retornado por sheets.Sheets: {sheet}")


SHEET_ID_DATA = ATULIZACAO_DA_DATA  # já é algo como "17f_00pWYt9alb64_…"

def registrar_marcacao_DASH(client, spreadsheet_id):
    try:
        planilha_marcacao = client.open_by_key(spreadsheet_id)
        aba_marcacao = planilha_marcacao.sheet1
        data_atual = datetime.now().strftime("%d/%m/%Y")
        aba_marcacao.append_row([data_atual], value_input_option="USER_ENTERED")
        print('Deu bom')
    except Exception as e:
        print(f"Erro ao registrar a marcação do relatório: {e}")


def authenticate_google_sheets(credentials_file):
    """Autentica e retorna o cliente do Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
    client = gspread.authorize(credentials)
    return client



def registrar_marcacao_relatorio(client, nome_relatorio, solicitante,hora_atual,observacao):
    
    try:
        # Abre a planilha usando o ID armazenado na variável de ambiente
        planilha_marcacao = client.open_by_key(marcador)
        
        # Seleciona a primeira aba da planilha
        aba_marcacao = planilha_marcacao.sheet1
        
        # Obtém a data e hora atual
       
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        # Prepara os dados para inserção
        nova_linha = [
            nome_relatorio,         # Tipo do Relatório
            solicitante,            # Solicitante
            data_atual,             # Data
            hora_atual,             # Hora
            " " ,
            observacao                        # Entrega
        ]
        
        # Adiciona a nova linha à planilha
        aba_marcacao.append_row(nova_linha, value_input_option="USER_ENTERED")
        print(f"Registro de geração do relatório '{nome_relatorio}' adicionado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao registrar a marcação do relatório: {e}")


# funcoes =[main_recisao,main_cobrancas,main_contratos,main_comercial,main_financeiro,main_gerencial,main_analise_credito]

funcoes_com_erro =[]

registrar_marcacao_DASH(client_sheets, SHEET_ID_DATA)

# for func in funcoes:
#     try:
#         print(f"---------- ATUALIZANDO {func.__name__} ----------")
#         func()
#     except Exception as e:
#         print(f"Erro ao execultar {func.__name__}:{e}")
#         print(traceback.format_exc())
#         funcoes_com_erro.append(func.__name__)


# Prepare a observacao string
if funcoes_com_erro:
    observacao = f"ATUALIZAÇÕES QUE DERAM ERRADO NO AUTOMATICO: {', '.join(funcoes_com_erro)}"
    print("\nATUALIZAÇOES QUE DERAM ERRADO")
    for nome_func in funcoes_com_erro:
        print(f"\n{nome_func}")
else:
    observacao = "Sem observações - todos os dashboards atualizados com sucesso"
    print("\nTODOS OS DSH ATUALIZADOS COM SUCESSO")

client = authenticate_google_sheets(sheet_json)
registrar_marcacao_relatorio(client, 'Atualizacao de Dash', 'Geral', hora_atual, observacao)
