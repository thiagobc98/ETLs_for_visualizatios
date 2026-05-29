import dotenv
import pandas as pd
from utils.sheets import Sheets
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

dotenv.load_dotenv()

CODE_SHEETS_DADOS_TRANSACIONAIS = os.getenv("CODE_SHEETS_DADOS_TRANSACIONAIS")
CODE_SHEETS_DASH_COTRATOS = os.getenv("CODE_SHEETS_DASH_CONTRATOS")
PAGINA_SHEETS = 'fluxo_contrato'


def tranto_contratos():

    print('\n\nLENDO DADOS_TRANSACIONAIS - CONTRATOS...')
    sheet = Sheets(CODE_SHEETS_DADOS_TRANSACIONAIS)
    data = sheet.get_planilha('CONTRATOS')

    headers = data[0]
    rows = [row + [''] * (len(headers) - len(row)) for row in data[1:]]
    df_contratos = pd.DataFrame(rows, columns=headers)
    print('Tirando linhas vazias...')
    df_contratos = df_contratos[df_contratos['Código do Contrato'] != '']
    df_contratos = df_contratos.dropna(subset=['Código do Contrato'])

    print('Excluindo as 57 primeiras linhas...')
    df_contratos = df_contratos.iloc[57:]  # Não são mais utilizadas

    print('Pegando apenas colunas a se utilizar...')
    df_contratos = df_contratos[['Código do Contrato', 'Receb.',
                                'Envio', 'Assin.', 'Sistema',
                                 'Boleto', 'Captadora', 'Valor',
                                 'Preencher com "SIM"']]

    print('Renomeando colunas...')
    df_contratos.rename(columns={'Código do Contrato': 'codigo_contrato',
                                 'Receb.': 'data_recebido',
                                 'Envio': 'data_envio',
                                 'Assin.': 'data_assinado',
                                 'Sistema': 'data_sistema',
                                 'Boleto': 'data_primeiro_boleto',
                                 'Captadora': 'captadora',
                                 'Valor': 'valor_aluguel',
                                 'Preencher com "SIM"': 'contrato_cancelado'}, inplace=True)

    print('Trativa para a coluna data_recebido e enviado, com - e data_Assinado preenchida')
    df_contratos['data_envio'] = df_contratos.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'], axis=1)

    print('Trativas de preenchimento errado das menians de contratos em data_primeiro_boleto...')
    df_contratos['data_primeiro_boleto'] = df_contratos['data_primeiro_boleto'].replace(
        ['-', 'Pendente', 'Pendente ', 'pendnete ', 'pendente iptu', 'pendente ', 'pendete'], '')

    print('Converter todos os Sim em maiúsculas...')
    df_contratos['contrato_cancelado'] = df_contratos['contrato_cancelado'].str.upper()

    print('Trativa se alguma coluna tiver vazia e ter data em alguma coluna seguite...')
    df_contratos['data_sistema'] = df_contratos.apply(
        lambda row: row['data_primeiro_boleto'] if row['data_sistema'] == '' else row['data_sistema'], axis=1)
    df_contratos['data_assinado'] = df_contratos.apply(
        lambda row: row['data_sistema'] if row['data_assinado'] == '' else row['data_assinado'], axis=1)
    df_contratos['data_envio'] = df_contratos.apply(
        lambda row: row['data_assinado'] if row['data_envio'] == '' else row['data_envio'], axis=1)
    df_contratos['data_recebido'] = df_contratos.apply(
        lambda row: row['data_envio'] if row['data_recebido'] == '' else row['data_recebido'], axis=1)

    print('Excluindo linhas que não tem nehuma data_preenchida...')
    df_contratos = df_contratos[df_contratos['data_recebido'] != '']

    print('Tratando erros das meninas de contratos (colocaram - e Pendente em coluna de Data)')
    colunas_para_tratar = ['data_primeiro_boleto', 'data_sistema']
    df_contratos[colunas_para_tratar] = df_contratos[colunas_para_tratar].replace([
                                                                                  'pendente', '-'], '')

    print('Tratando valor_aluguel para o padrão sheets...')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        '', None)
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].str.replace(
        'R$', '').str.replace(' ', '')

    print('ERROS das meninas de contratos!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        'R$3,900,00', '3.900,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        'R$ 2,500,00', '2.500,00')
    df_contratos['valor_aluguel'] = df_contratos['valor_aluguel'].replace(
        '1.000.00', '1.000,00')  # Não passei para as meninas de contratos, fiquei com vergonha
    return df_contratos


def upload_sheets(df_contratos):
    sheet = Sheets(CODE_SHEETS_DASH_COTRATOS)
    sheet.clear_and_upload(df_contratos, PAGINA_SHEETS)


def main():
    df_contratos = tranto_contratos()
    upload_sheets(df_contratos)
    return df_contratos


if __name__ == "__main__":
    df_contratos = main()
