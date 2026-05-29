import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
import re
import os
import dotenv
dotenv.load_dotenv()

from utils.utils import create_cod_to_merge 
from utils import planilhas_transacionais 

superlogica_todos_csv = os.path.join(os.path.dirname(__file__), '..', 'dash_comercial', 'data', 'superlogica_todos.csv')
superlogica_ativos_csv = os.path.join(os.path.dirname(__file__), '..', 'dash_comercial', 'data', 'superlogica_ativos.csv')




PATH_DOWNLOAD_CHROME = os.getenv("PATH_DOWNLOAD_CHROME")
SUPERLOGICA_USER = os.getenv("SUPERLOGICA_USER")
SUPERLOGICA_PASS = os.getenv("SUPERLOGICA_PASS")

def create_chrome_driver() -> webdriver:
    chromeOptions = webdriver.ChromeOptions()
    # Configurar o caminho da pasta de download
    chromeOptions.add_experimental_option('prefs', {
        'download.default_directory': PATH_DOWNLOAD_CHROME,
        'download.prompt_for_download': False,  # Evita que o Chrome pergunte onde salvar os downloads
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True  # Ativa a verificação de segurança para downloads
    })
    chromeOptions.add_argument("--disable-save-password-bubble")
    chromeOptions.add_argument("start-maximized")
    # chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chromeOptions)
    return driver

def quit_chrome(driver: webdriver)->None:
    print('Fechando Navegador...')
    driver.close()
    driver.quit()

def insert_key(driver: webdriver, xpath: str, key: str) -> None: 
    driver.find_element(By.XPATH, xpath).send_keys(key)
    sleep(1)

def click(driver: webdriver, xpath: str) -> None: 
    driver.find_element(By.XPATH, xpath).click()
    sleep(1)


def login_super(driver: webdriver) -> None:
    print('Abrindo navegador...')
    driver.get("https://superlogica.net/clients/")

    print('Fazendo login...')
    insert_key(driver,'//*[@id="username"]', SUPERLOGICA_USER)
    insert_key(driver, '//*[@id="password"]', SUPERLOGICA_PASS)
    click(driver,'//*[@id="entrar"]')

    print('Click contratos...')
    click(driver,'//*[@id="bootstrapmenu-tabContratosImob"]')

    print('Click impressora...')
    click(driver,'//*[@id="botoesTopo"]/div/div')

    print('Click contratos...')
    click(driver,'//*[@id="botoesTopo"]/div/div/ul/li[2]/a')

def export_data_super(driver: webdriver) -> None:
    print('Click visualizar...')
    click(driver, '//*[@id="container_btn_imprimir"]/a')
    sleep(5)

    print('Click Mais opções...')
    click(driver,'//*[@id="conteudo"]/div[2]/div[1]/div/div[1]/div')

    print('Exportando contratos como csv..')
    click(driver,'//*[@id="conteudo"]/div[2]/div[1]/div/div[1]/div/div/ul/li[2]/a')
    sleep(25)

def export_ativos_super(driver: webdriver) -> None:
    print('\n\nEXPORTANDO ATIVOS')
    print('Click Campos Adicionais...')
    click(driver, '//*[@id="fieldset-CAMPOS_ADICIONAIS"]/legend/button')

    print('Click filtro Com início do contrato...')
    click(driver, '//*[@id="fieldset-CAMPOS_ADICIONAIS"]/div[1]/label/span/button')

    print('Click filtro Com filíais...')
    click(driver, '//*[@id="fieldset-CAMPOS_ADICIONAIS"]/div[4]/label/span/button')

    export_data_super(driver)
    sleep(10)

def export_todos_super(driver: webdriver) -> None:
    print('\n\nEXPORTANDO TODOS')
    print('Click mais opções')
    click(driver, '//*[@id="fieldset-OPCOES"]/legend/button')

    print('Click filtro status')
    click(driver, '//*[@id="comStatus"]')

    print('Click TODOS')
    click(driver,'//*[@id="comStatus"]/option[6]')

    export_data_super(driver)
    sleep(30)

def get_ordenados_arquivos_csv()  -> list:
    print('\n\nOrdenando os arquivos por data de modificação em ordem decrescente...')
    arquivos_csv_com_data = []
    for arquivo_csv in os.listdir(PATH_DOWNLOAD_CHROME):
        if arquivo_csv.endswith('.csv'):
            caminho_arquivo = os.path.join(PATH_DOWNLOAD_CHROME, arquivo_csv)
            data_modificacao = os.path.getmtime(caminho_arquivo)
            arquivos_csv_com_data.append((caminho_arquivo, data_modificacao))

    arquivos_csv_com_data.sort(key=lambda x: x[1], reverse=True)
    return arquivos_csv_com_data

def read_csv_super_todos(name: str) -> pd.DataFrame:
    arquivos_csv_com_data = get_ordenados_arquivos_csv()
    print(f'Lendo últimos .csv baixados do superlogica {name}...')
    print(arquivos_csv_com_data[0][0])
    df_todos_super = pd.read_csv(arquivos_csv_com_data[0][0], encoding='latin-1') 
    return df_todos_super

def read_csv_super_ativos(name: str) -> pd.DataFrame:
    arquivos_csv_com_data = get_ordenados_arquivos_csv()
    print(f'Lendo últimos .csv baixados do superlogica {name}...')
    print(arquivos_csv_com_data[1][0])
    df_ativos_super = pd.read_csv(arquivos_csv_com_data[1][0], encoding='latin-1') 
    return df_ativos_super


def add_coluns_from_sheets(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    df_parceiros = planilhas_transacionais.get_parceiros_to_super_logica()
    df_desocupado = planilhas_transacionais.get_desocupado()

    print('Criando cod_contrato com base na conluna contrato...') 
    df['codigo_contrato'] = df['Contrato'].apply(lambda x: re.split(r'- [A-Z][a-z]', x)[0].strip())

    print(f'Adicionando coluna cod_to_merge no {name_df}...')
    df['cod_to_merge_parceiros'] = df['Filial'].apply(create_cod_to_merge)
    df['cod_to_merge_desocupado'] = df['codigo_contrato'].apply(create_cod_to_merge)

    print(f'Fazendo merge para adicionar as colunas codigo_parceiro e data_desocupacao em {name_df}...')
    df['codigo_parceiro'] = df['cod_to_merge_parceiros'].map(df_parceiros.set_index('cod_to_merge')['Cod Parceiro'])
    df['data_desocupacao'] = df['cod_to_merge_desocupado'].map(df_desocupado.set_index('cod_to_merge')['Data de desocupação'])

    return df

def processar_super_logica(df: pd.DataFrame, name_df: str) -> pd.DataFrame:
    print(f'Alterando e organizando colunas do {name_df}...')
    df = df.reset_index()

    df.rename(columns = {
        'index': 'Contrato',
        'Contrato': 'Início',
        'Início': 'Término',
        'Término': 'Filial',
        'Filial': 'Taxa de administração',
        'Taxa de administração': 'Aluguel',
        'Aluguel': 'valor_aluguel_contrato'}, inplace=True)
    print('Criando cod_contrato com base na conluna contrato...') 
    df['codigo_contrato'] = df['Contrato'].apply(lambda x: re.split(r'- [A-Z][a-z]', x)[0].strip())

    df = add_coluns_from_sheets(df, name_df)

    print(f'Criando coluna name_status {name_df}...')
    df['name_status'] =  df['data_desocupacao'].apply(lambda x: 'Ativo' if pd.isna(x) else 'Encerrado')

    print(f'Criando as colunas que também tem no sistema em {name_df}...')
    df['meses_duracao_contrato'] = None
    df['taxa_contrato'] = None
    df['taxa_admin_contrato'] = None

    print(f'Adicionando coluans sistema para saber que esses dados são do superlogica em {name_df}...')
    df['tipo_sistema'] = 'super_logica'

    print(f'Deletando colunas cod_to_merge de {name_df}...')
    del df['cod_to_merge_parceiros']
    del df['cod_to_merge_desocupado']

    print(f'Excluindo a última linha que sempre vem bugada...')
    df.drop(df.index[-1], inplace=True) 

    print(f'Selecionando apenas colunas que vão para o sheets em {name_df}...')
    # **** quer dizer que não vai seguir porque não tem no sistema
    df.rename(columns={'Contrato': 'contrato_completo****',
                            'Início': 'data_inicio_contrato',
                            'Término': 'termino****',
                            'Filial': 'nome_parceiro',
                            'Tipo': 'tipo****',
                            'Taxa de administração': 'porcentagem_taxa_administracao',
                            'Aluguel': 'valor_taxa_administracao******',
                            'Valor_aluguel_contrato': 'valor_aluguel_contrato',
                            'codigo_contrato': 'codigo_contrato',
                            'codigo_parceiro': 'codigo_parceiro',
                            'data_desocupacao': 'data_desocupacao',
                            'name_status': 'name_status',
                            'meses_duracao_contrato': 'meses_duracao_contrato',
                            'taxa_contrato': 'taxa_contrato',
                            'tipo_sistema': 'tipo_sistema',
                            }, inplace=True)

    df = df[['codigo_contrato', 'codigo_parceiro', 
            'nome_parceiro', 'valor_aluguel_contrato', 
            'taxa_contrato', 'porcentagem_taxa_administracao', 
            'name_status', 'data_inicio_contrato', 
            'meses_duracao_contrato', 'data_desocupacao', 'tipo_sistema']]

    return df

def main():
    print('\n\t------>SUPERLOGICA<------\n')
    driver = create_chrome_driver()

    login_super(driver)
    export_ativos_super(driver)
    export_todos_super(driver)

    df_todos_super = read_csv_super_todos('df_todos_super')
    df_ativos_super = read_csv_super_ativos('df_ativos_super')
    
    df_todos_super = processar_super_logica(df_todos_super, 'TODOS')
    df_ativos_super = processar_super_logica(df_ativos_super, 'ATIVOS')

    df_todos_super['nome_produto'] = 'Smart'
    df_todos_super['migracao'] = 'Nao'
    df_ativos_super['nome_produto'] = 'Smart'
    df_ativos_super['migracao'] = 'Nao'
    
    df_todos_super.to_csv(superlogica_todos_csv, index=False)
    df_ativos_super.to_csv(superlogica_ativos_csv, index=False)

    quit_chrome(driver)

if __name__ == "__main__":
    main()