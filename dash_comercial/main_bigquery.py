import sys
import os
import pandas as pd
from decimal import Decimal
from unidecode import unidecode
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import BadRequest
import dotenv
from utils import mysql_db as db
from utils import planilhas_transacionais
from utils.utils import create_cod_to_merge
from utils.sheets import Sheets

dotenv.load_dotenv()


class GerenciadorBigQuery:
    """Classe para gerenciar operações com o BigQuery"""

    def __init__(self):
        """Inicializa a conexão com o BigQuery"""
        path_token = os.getenv('PATH_TOKEN_JSON_BIGQUERY')
        self.credenciais = service_account.Credentials.from_service_account_file(
            path_token)
        self.cliente = bigquery.Client(
            credentials=self.credenciais,
            project=self.credenciais.project_id
        )

    def criar_dataset(self, dataset_id):
        """Cria um dataset no BigQuery se não existir"""
        dataset_ref = self.cliente.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"

        dataset = self.cliente.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {dataset_id} criado ou já existente.")
        return self.cliente, dataset_id

    def criar_tabela(self, dataset_id, schema, tabela_id):
        """Cria uma tabela no BigQuery se não existir"""
        tabela_ref = self.cliente.dataset(dataset_id).table(tabela_id)

        try:
            self.cliente.get_table(tabela_ref)
            print(f"Tabela '{tabela_id}' já existe.")
        except Exception:
            tabela = bigquery.Table(tabela_ref, schema=schema)
            self.cliente.create_table(tabela)
            print(f"Tabela '{tabela_id}' criada com sucesso.")

        return tabela_id

    def fazer_upload(self, schema, tabela_id, df, dataset_id, nome_arquivo):
        """Faz upload de um DataFrame para uma tabela no BigQuery"""
        # Salvar como Parquet
        caminho_arquivo = f'dash_comercial/data/{nome_arquivo}'
        df.to_parquet(caminho_arquivo, index=False)

        # Criar dataset e tabela
        _, dataset_id = self.criar_dataset(dataset_id)
        tabela_id = self.criar_tabela(dataset_id, schema, tabela_id)
        tabela_ref = self.cliente.dataset(dataset_id).table(tabela_id)

        # Configurar job de upload
        config_job = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        # Enviar dados
        try:
            with open(caminho_arquivo, "rb") as arquivo:
                job = self.cliente.load_table_from_file(
                    arquivo, tabela_ref, job_config=config_job)
            job.result()
            print("Upload do Parquet concluído com sucesso!")
        except BadRequest as e:
            print("❌ Erro ao enviar para o BigQuery:")
            print(e)
        except Exception as e:
            print("❌ Erro inesperado:")
            print(e)


class ProcessadorSistema:
    """Classe para processar dados do sistema"""

    def __init__(self, sql_path, nome, colunas_sistema):
        """Inicializa o processador do sistema"""
        self.sql_path = sql_path
        self.nome = nome
        self.colunas = colunas_sistema
        self.df = None
        self.caminho_csv = f"dash_comercial/data/sistema_{self.nome.lower()}.csv"
        self.gerenciador_bq = GerenciadorBigQuery()

    def adicionar_colunas_planilhas(self):
        """Adiciona colunas de planilhas externas ao DataFrame"""
        df_parceiros = planilhas_transacionais.get_parceiros_to_sistema()
        df_desocupado = planilhas_transacionais.get_desocupado()

        print(f'Criando cod_to_merge para {self.nome}')
        self.df['cod_to_merge_parceiros'] = self.df['nome_parceiro'].apply(
            create_cod_to_merge)
        self.df['cod_to_merge_desocupado'] = self.df['codigo_contrato'].apply(
            create_cod_to_merge)

        print(f'Mapeando dados das planilhas para {self.nome}...')
        self.df['codigo_parceiro'] = self.df['cod_to_merge_parceiros'].map(
            df_parceiros.set_index('cod_to_merge')['Cod Parceiro'])

        self.df['tipo_parceiro'] = self.df['cod_to_merge_parceiros'].map(
            df_parceiros.set_index('cod_to_merge')['Tipo de parceiro'])

        self.df['data_desocupacao'] = self.df['cod_to_merge_desocupado'].map(
            df_desocupado.set_index('cod_to_merge')['Data de desocupação'])

        print(f'Deletando colunas temporárias para {self.nome}...')
        del self.df['cod_to_merge_parceiros']
        del self.df['cod_to_merge_desocupado']

    def executar_sql(self):
        """Executa a consulta SQL e cria o DataFrame"""
        print(f'\n\t------>SISTEMA-{self.nome}<------')
        con = db.connect_to_db()
        cursor = con.cursor()

        resultados = db.execute_select_in_db(cursor, self.sql_path)
        self.df = pd.DataFrame(resultados, columns=self.colunas)

        cursor.close()
        con.close()

    def processar(self):
        """Processa os dados do sistema"""
        self.executar_sql()
        self.adicionar_colunas_planilhas()

        # Renomear colunas
        print(f'Renomeando colunas para {self.nome}...')
        self.df.rename(columns={
            'date_inicio_contrato': 'data_inicio_contrato',
            'nome_parceiro': 'nome_parceiro',
            'taxa_admin_contrato': 'porcentagem_taxa_administracao',
            'valor_aluguel_contrato': 'valor_aluguel_contrato',
            'codigo_contrato': 'codigo_contrato',
            'codigo_parceiro': 'codigo_parceiro',
            'data_desocupacao': 'data_desocupacao',
            'name_status': 'name_status',
            'meses_duracao_contrato': 'meses_duracao_contrato',
            'taxa_contrato': 'taxa_contrato',
            'tipo_parceiro': 'tipo_parceiro'},
            inplace=True
        )

        # Adicionar tipo sistema
        self.df['tipo_sistema'] = 'sistema'

        # Selecionar e ordenar colunas
        self.df = self.df[[
            'codigo_contrato', 'codigo_parceiro', 'nome_parceiro',
            'valor_aluguel_contrato', 'taxa_contrato', 'porcentagem_taxa_administracao',
            'name_status', 'data_inicio_contrato', 'meses_duracao_contrato',
            'data_desocupacao', 'tipo_parceiro', 'tipo_sistema', 'nome_produto', 'migracao'
        ]]

        # Tratar valores
        self.df['meses_duracao_contrato'] = self.df['meses_duracao_contrato'].fillna(
            0)
        self.df['meses_duracao_contrato'] = self.df['meses_duracao_contrato'].astype(
            int)
        self.df['migracao'] = self.df['migracao'].replace('NÃ£o', 'Nao')

        # Formatar datas
        print(f'Formatando datas para {self.nome}...')
        self.df['data_inicio_contrato'] = pd.to_datetime(
            self.df['data_inicio_contrato']).dt.strftime('%d/%m/%Y')

        # Salvar CSV
        self.df.to_csv(self.caminho_csv, index=False)

    def formatar_datas(self):
        """Formatar as datas (método a ser sobrescrito pelas subclasses)"""
        pass

    def enviar_para_bigquery(self):
        """Enviar dados para BigQuery (método a ser sobrescrito pelas subclasses)"""
        pass


class ProcessadorSistemaTodos(ProcessadorSistema):
    """Classe para processar dados do sistema (todos)"""

    def __init__(self, sql_path, colunas_sistema):
        """Inicializa o processador do sistema (todos)"""
        super().__init__(sql_path, "Todos", colunas_sistema)

    def formatar_datas(self):
        """Formata as datas para sistema todos"""
        data_cols = ["data_inicio_contrato", "data_desocupacao"]

        for col in data_cols:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        self.df['data_inicio_contrato'] = self.df['data_inicio_contrato'].dt.date
        self.df['data_desocupacao'] = self.df['data_desocupacao'].dt.date

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("codigo_contrato", "STRING"),
            bigquery.SchemaField("codigo_parceiro", "STRING"),
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("valor_aluguel_contrato", "STRING"),
            bigquery.SchemaField("taxa_contrato", "STRING"),
            bigquery.SchemaField("porcentagem_taxa_administracao", "STRING"),
            bigquery.SchemaField("name_status", "STRING"),
            bigquery.SchemaField("data_inicio_contrato", "DATE"),
            bigquery.SchemaField("meses_duracao_contrato", "INTEGER"),
            bigquery.SchemaField("data_desocupacao", "DATE"),
            bigquery.SchemaField("tipo_parceiro", "STRING"),
            bigquery.SchemaField("tipo_sistema", "STRING"),
            bigquery.SchemaField("nome_produto", "STRING"),
            bigquery.SchemaField("migracao", "STRING"),
        ]

        # Formatar datas antes de enviar
        self.formatar_datas()

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="sistema",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="sistema"
        )


class ProcessadorSistemaAtivos(ProcessadorSistema):
    """Classe para processar dados do sistema (ativos)"""

    def __init__(self, sql_path, colunas_sistema):
        """Inicializa o processador do sistema (ativos)"""
        super().__init__(sql_path, "ATIVOS", colunas_sistema)

    def formatar_datas(self):
        """Formata as datas para sistema ativos"""
        data_cols = ["data_inicio_contrato", "data_desocupacao"]

        for col in data_cols:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        self.df['data_desocupacao'] = pd.to_datetime(
            self.df['data_desocupacao'], errors='coerce')
        self.df['data_desocupacao'] = self.df['data_desocupacao'].dt.strftime(
            '%Y%m%d')
        self.df['data_desocupacao'] = self.df['data_desocupacao'].fillna(
            0).astype(int)
        self.df['data_inicio_contrato'] = self.df['data_inicio_contrato'].dt.strftime(
            '%Y-%m-%d')

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("codigo_contrato", "STRING"),
            bigquery.SchemaField("codigo_parceiro", "STRING"),
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("valor_aluguel_contrato", "STRING"),
            bigquery.SchemaField("taxa_contrato", "STRING"),
            bigquery.SchemaField("porcentagem_taxa_administracao", "STRING"),
            bigquery.SchemaField("name_status", "STRING"),
            bigquery.SchemaField("data_inicio_contrato", "STRING"),
            bigquery.SchemaField("meses_duracao_contrato", "INTEGER"),
            bigquery.SchemaField("data_desocupacao", "INTEGER"),
            bigquery.SchemaField("tipo_parceiro", "STRING"),
            bigquery.SchemaField("tipo_sistema", "STRING"),
            bigquery.SchemaField("nome_produto", "STRING"),
            bigquery.SchemaField("migracao", "STRING"),
        ]

        # Formatar datas antes de enviar
        self.formatar_datas()

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="sistema_ativos",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="sistema_ativos"
        )


class ProcessadorPretendentes:
    """Classe para processar dados de pretendentes"""

    def __init__(self, sql_path):
        """Inicializa o processador de pretendentes"""
        self.sql_path = sql_path
        self.df = None
        self.colunas = [
            'id_parceiro',
            'parceiro',
            'data_analise',
            'valor_aluguel_analisado',
            'resultado_analise_pretendente'
        ]
        self.gerenciador_bq = GerenciadorBigQuery()

    def processar(self):
        """Processa os dados de pretendentes"""
        print('\n\t------>PRETENDENTES SEM SOLIDÁRIOS<------')

        # Executar SQL
        con = db.connect_to_db()
        cursor = con.cursor()

        resultados = db.execute_select_in_db(cursor, self.sql_path)
        self.df = pd.DataFrame(resultados, columns=self.colunas)

        cursor.close()
        con.close()

        # Formatar datas
        self.df['data_analise'] = pd.to_datetime(
            self.df['data_analise'], errors='coerce')
        self.df['data_analise'] = self.df['data_analise'].dt.date

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("id_parceiro", "INTEGER"),
            bigquery.SchemaField("parceiro", "STRING"),
            bigquery.SchemaField("data_analise", "DATE"),
            bigquery.SchemaField("valor_aluguel_analisado", "STRING"),
            bigquery.SchemaField("resultado_analise_pretendente", "INTEGER"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="pretendentes_sem_solidarios",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="pretendentes_sem_solidarios"
        )


class ProcessadorRecebidosEnviadosAssinados:
    """Classe para processar dados de recebidos, enviados e assinados"""

    def __init__(self):
        """Inicializa o processador"""
        self.df = None
        self.colunas = {
            'Código do Contrato': 'codigo_contrato',
            'Receb.': 'data_recebido',
            'Envio': 'data_enviado',
            'Assin.': 'data_assinado',
            'Captadora': 'captadora',
            'Valor': 'valor'
        }
        self.gerenciador_bq = GerenciadorBigQuery()

    def processar(self):
        """Processa os dados de recebidos, enviados e assinados"""
        print('\n\t------>RECEBIDOS ENVIADOS ASSINADOS<------\n')

        # Obter dados da planilha
        self.df = planilhas_transacionais.get_recebidos_enviados_assinados()

        # Renomear e selecionar colunas
        print('Renomeando colunas...')
        self.df.rename(columns=self.colunas, inplace=True)
        self.df = self.df[self.colunas.values()]

        # Tratar dados vazios
        print('Tratando dados vazios...')
        self.df['data_recebido'] = self.df.apply(
            lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'],
            axis=1
        )

        self.df['data_enviado'] = self.df.apply(
            lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'],
            axis=1
        )

        self.df['data_recebido'] = self.df.apply(
            lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'],
            axis=1
        )

        # Filtrar valores inválidos
        self.df = self.df[self.df['data_recebido'] != 'X']

        # Converter para datetime
        print('Convertendo para datetime...')
        self.df['data_recebido'] = pd.to_datetime(
            self.df['data_recebido'], format='%d/%m/%Y %H:%M:%S'
        )

        # Filtrar por data
        print('Filtrando dados a partir de 2023...')
        self.df = self.df[self.df['data_recebido'] >= '2023-01-01']

        # Criar coluna ano_mes
        print('Criando coluna ano_mes...')
        self.df['ano_mes'] = self.df['data_recebido'].dt.strftime('%Y-%m')

        # Formatar data
        self.df['data_recebido'] = self.df['data_recebido'].dt.strftime(
            '%d/%m/%Y')

        # Tratar captadora
        print('Ajustando coluna captadora...')
        self.df['captadora'] = self.df['captadora'].fillna('VAZIO')
        self.df['captadora'] = self.df['captadora'].str.upper()

        # Separar em DataFrames específicos
        print('Separando em DataFrames distintos...')
        recebidos = self.df[['codigo_contrato',
                             'captadora', 'ano_mes', 'data_recebido', 'valor']]
        recebidos = recebidos.copy()
        recebidos.rename(columns={'valor': 'valor_recebidos'}, inplace=True)

        enviados = self.df[['codigo_contrato', 'captadora',
                            'ano_mes', 'data_enviado', 'valor']]
        enviados = enviados.copy()
        enviados = enviados[enviados['data_enviado'].str.len() > 1]
        enviados.rename(columns={'valor': 'valor_enviado'}, inplace=True)

        assinados = self.df[['codigo_contrato',
                             'captadora', 'ano_mes', 'data_assinado', 'valor']]
        assinados = assinados.copy()
        assinados = assinados[assinados['data_assinado'].str.len() > 1]
        assinados.rename(columns={'valor': 'valor_assinados'}, inplace=True)

        # Juntar os DataFrames
        print('Juntando os DataFrames...')
        self.df = pd.merge(
            recebidos, enviados,
            on=['ano_mes', 'captadora', 'codigo_contrato'],
            how='outer'
        )

        self.df = pd.merge(
            self.df, assinados,
            on=['ano_mes', 'captadora', 'codigo_contrato'],
            how='outer'
        )

        # Formatar datas
        for col in ["data_recebido", "data_enviado", "data_assinado"]:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        self.df['data_recebido'] = self.df['data_recebido'].dt.date
        self.df['data_enviado'] = self.df['data_enviado'].dt.date
        self.df['data_assinado'] = self.df['data_assinado'].dt.date

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("codigo_contrato", "STRING"),
            bigquery.SchemaField("captadora", "STRING"),
            bigquery.SchemaField("ano_mes", "STRING"),
            bigquery.SchemaField("data_recebido", "DATE"),
            bigquery.SchemaField("valor_recebidos", "STRING"),
            bigquery.SchemaField("data_enviado", "DATE"),
            bigquery.SchemaField("valor_enviado", "STRING"),
            bigquery.SchemaField("data_assinado", "DATE"),
            bigquery.SchemaField("valor_assinados", "STRING"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="recebidos_enviados_assinados",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="recebidos_enviados_assinados"
        )


class ProcessadorAssinadosDesocupados:
    """Classe para processar dados de assinados e desocupados"""

    def __init__(self):
        """Inicializa o processador"""
        self.df = None
        self.gerenciador_bq = GerenciadorBigQuery()

    def processar_desocupado(self):
        """Processa os dados de desocupados"""
        print('\n\t------>TRATANDO DADOS DESOCUPADO<------')
        df_desocupado = planilhas_transacionais.get_desocupado()

        # Renomear e selecionar colunas
        print('Renomeando colunas...')
        df_desocupado.rename(columns={
            'Código do contrato': 'codigo_contrato',
            'Data de desocupação': 'data_desocupacao'
        }, inplace=True)

        df_desocupado = df_desocupado[['codigo_contrato', 'data_desocupacao']]

        # Converter para datetime
        print('Convertendo para datetime...')
        df_desocupado['data_desocupacao'] = pd.to_datetime(
            df_desocupado['data_desocupacao'], format='%d/%m/%Y'
        )

        # Filtrar por data
        print('Filtrando dados a partir de 2023...')
        df_desocupado = df_desocupado[df_desocupado['data_desocupacao']
                                      >= '2023-01-01']

        # Criar coluna ano_mes
        df_desocupado['ano_mes'] = df_desocupado['data_desocupacao'].dt.to_period(
            'M')

        # Formatar data
        df_desocupado['data_desocupacao'] = df_desocupado['data_desocupacao'].dt.strftime(
            '%d/%m/%Y')

        df_desocupado.reset_index(drop=True, inplace=True)
        return df_desocupado

    def processar_assinado(self):
        """Processa os dados de assinados"""
        print('\n\t------>TRATANDO DADOS ASSINADO<------')
        df_assinado = planilhas_transacionais.get_recebidos_enviados_assinados()

        # Renomear colunas
        df_assinado.rename(columns={
            'Código do Contrato': 'codigo_contrato',
            'Receb.': 'data_recebido',
            'Envio': 'data_envio',
            'Assin.': 'data_assinado',
            'Sistema': 'data_sistema',
            'Valor': 'valor'
        }, inplace=True)

        # Tratar dados vazios
        print('Tratando dados vazios...')
        df_assinado['data_envio'] = df_assinado.apply(
            lambda row: row['data_assinado'] if row['data_envio'] == '-' else row['data_envio'],
            axis=1
        )

        df_assinado['data_recebido'] = df_assinado.apply(
            lambda row: row['data_envio'] if row['data_recebido'] == '-' else row['data_recebido'],
            axis=1
        )

        # Converter para datetime
        print('Convertendo para datetime...')
        df_assinado['data_recebido'] = pd.to_datetime(
            df_assinado['data_recebido'], format='%d/%m/%Y %H:%M:%S'
        )

        # Filtrar por data
        print('Filtrando dados a partir de 2023...')
        df_assinado = df_assinado[df_assinado['data_recebido'] >= '2023-01-01']

        # Criar coluna ano_mes
        df_assinado['ano_mes'] = df_assinado['data_recebido'].dt.to_period('M')

        # Selecionar colunas
        df_assinado = df_assinado[['codigo_contrato',
                                   'data_assinado', 'ano_mes', 'valor']]

        return df_assinado

    def processar(self):
        """Processa os dados de assinados e desocupados"""
        print('\n\t------>ASSINADOS DESOCUPADOS<------\n')
        df_desocupado = self.processar_desocupado()
        df_assinado = self.processar_assinado()

        # Juntar os DataFrames
        print('Juntando os DataFrames...')
        self.df = pd.merge(
            df_assinado, df_desocupado,
            on=['ano_mes', 'codigo_contrato'],
            how='outer'
        )

        # Converter ano_mes para string
        self.df["ano_mes"] = self.df["ano_mes"].astype(str)

        # Formatar datas
        for col in ["data_assinado", "data_desocupacao"]:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        self.df['data_assinado'] = self.df['data_assinado'].dt.date
        self.df['data_desocupacao'] = self.df['data_desocupacao'].dt.date

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("codigo_contrato", "STRING"),
            bigquery.SchemaField("data_assinado", "DATE"),
            bigquery.SchemaField("ano_mes", "STRING"),
            bigquery.SchemaField("valor", "STRING"),
            bigquery.SchemaField("data_desocupacao", "DATE"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="assinados_desocupados",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="assinados_desocupados"
        )


class ProcessadorCurvaABC:
    """Classe base para processar dados de Curva ABC"""

    def __init__(self, sql_path, colunas, nome, tipo):
        """Inicializa o processador de Curva ABC"""
        self.sql_path = sql_path
        self.colunas = colunas
        self.nome = nome
        self.tipo = tipo  # 'MON' para monetária, 'NUM' para numérica
        self.df = None
        self.gerenciador_bq = GerenciadorBigQuery()

    def executar_sql(self):
        """Executa a consulta SQL e cria o DataFrame"""
        con = db.connect_to_db()
        cursor = con.cursor()

        resultados = db.execute_select_in_db(cursor, self.sql_path)
        self.df = pd.DataFrame(resultados, columns=self.colunas)

        cursor.close()
        con.close()

    def processar(self):
        """Método a ser implementado pelas subclasses"""
        pass

    def enviar_para_bigquery(self):
        """Método a ser implementado pelas subclasses"""
        pass


class ProcessadorCurvaABCMonetaria(ProcessadorCurvaABC):
    """Classe para processar dados de Curva ABC Monetária"""

    def __init__(self, sql_path, nome):
        """Inicializa o processador de Curva ABC Monetária"""
        colunas = [
            'nome_parceiro',
            'count_contratos',
            'valor_aluguel',
            'valor_aluguel_acumulado',
            'porcentagem_valor_acumulada',
            'classe'
        ]
        super().__init__(sql_path, colunas, nome, 'MON')

    def processar(self):
        """Processa os dados de Curva ABC Monetária"""
        print(f'\n\t------>CURVA-ABC {self.nome} MONETÁRIOS<------')
        self.executar_sql()

        # Selecionar colunas
        self.df = self.df[[
            'nome_parceiro',
            'count_contratos',
            'valor_aluguel',
            'valor_aluguel_acumulado',
            'porcentagem_valor_acumulada',
            'classe'
        ]]

        # Converter para numérico
        self.df['porcentagem_valor_acumulada'] = pd.to_numeric(
            self.df['porcentagem_valor_acumulada'])

        # Configurar formato de exibição
        pd.options.display.float_format = '{:.2f}'.format


class ProcessadorCurvaABCMonetariaAtivos(ProcessadorCurvaABCMonetaria):
    """Classe para processar dados de Curva ABC Monetária (Ativos)"""

    def __init__(self, sql_path):
        """Inicializa o processador de Curva ABC Monetária (Ativos)"""
        super().__init__(sql_path, "ATIVOS")

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        # Converter para Decimal para maior precisão
        self.df['valor_aluguel'] = self.df['valor_aluguel'].apply(
            lambda x: Decimal(x))
        self.df['valor_aluguel_acumulado'] = self.df['valor_aluguel_acumulado'].apply(
            lambda x: Decimal(x))

        schema = [
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("count_contratos", "INTEGER"),
            bigquery.SchemaField("valor_aluguel", "NUMERIC"),
            bigquery.SchemaField("valor_aluguel_acumulado", "NUMERIC"),
            bigquery.SchemaField("porcentagem_valor_acumulada", "FLOAT"),
            bigquery.SchemaField("classe", "STRING"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="sistema_ativos_mon",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="Curva_ABC_Monetario_Ativos"
        )


class ProcessadorCurvaABCMonetariaTodos(ProcessadorCurvaABCMonetaria):
    """Classe para processar dados de Curva ABC Monetária (Todos)"""

    def __init__(self, sql_path):
        """Inicializa o processador de Curva ABC Monetária (Todos)"""
        super().__init__(sql_path, "TODOS")

    def processar(self):
        """Processa os dados de Curva ABC Monetária (Todos)"""
        super().processar()

        # Converter para float
        self.df['valor_aluguel'] = pd.to_numeric(
            self.df['valor_aluguel'], errors='coerce').astype('float')
        self.df['valor_aluguel_acumulado'] = pd.to_numeric(
            self.df['valor_aluguel_acumulado'], errors='coerce'
        ).astype('float')

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("count_contratos", "INTEGER"),
            bigquery.SchemaField("valor_aluguel", "FLOAT"),
            bigquery.SchemaField("valor_aluguel_acumulado", "FLOAT"),
            bigquery.SchemaField("porcentagem_valor_acumulada", "FLOAT"),
            bigquery.SchemaField("classe", "STRING"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="sistema_todos_mon",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="Curva_ABC_Monetario_Todos"
        )


class ProcessadorCurvaABCNumerica(ProcessadorCurvaABC):
    """Classe para processar dados de Curva ABC Numérica"""

    def __init__(self, sql_path, nome):
        """Inicializa o processador de Curva ABC Numérica"""
        colunas = [
            'nome_parceiro',
            'count_contratos',
            'qtd_acumulado',
            'porcentagem',
            'porcentagem_acumulada',
            'classe'
        ]
        super().__init__(sql_path, colunas, nome, 'NUM')

    def processar(self):
        """Processa os dados de Curva ABC Numérica"""
        print(f'\n\t------>SISTEMA-{self.nome}-NUMERICOS<------')
        self.executar_sql()

        # Selecionar colunas
        self.df = self.df[[
            'nome_parceiro',
            'count_contratos',
            'qtd_acumulado',
            'porcentagem',
            'porcentagem_acumulada',
            'classe'
        ]]

        # Converter para float
        self.df['porcentagem'] = self.df['porcentagem'].astype(float)
        self.df['porcentagem_acumulada'] = self.df['porcentagem_acumulada'].astype(
            float)

        # Configurar formato de exibição
        pd.options.display.float_format = '{:.2f}'.format


class ProcessadorCurvaABCNumericaAtivos(ProcessadorCurvaABCNumerica):
    """Classe para processar dados de Curva ABC Numérica (Ativos)"""

    def __init__(self, sql_path):
        """Inicializa o processador de Curva ABC Numérica (Ativos)"""
        super().__init__(sql_path, "ATIVOS")

    def processar(self):
        """Processa os dados de Curva ABC Numérica (Ativos)"""
        super().processar()

        # Converter para Int64
        self.df['qtd_acumulado'] = pd.to_numeric(
            self.df['qtd_acumulado'], errors='coerce').astype('Int64')

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("count_contratos", "INTEGER"),
            bigquery.SchemaField("qtd_acumulado", "INTEGER"),
            bigquery.SchemaField("porcentagem", "FLOAT"),
            bigquery.SchemaField("porcentagem_acumulada", "FLOAT"),
            bigquery.SchemaField("classe", "STRING"),
        ]

        self.gerenciador_bq.fazer_upload(
            schema=schema,
            tabela_id="sistema_ativos_num",
            df=self.df,
            dataset_id="dash_comercial",
            nome_arquivo="Curva_ABC_Numericos_Ativos"
        )


class ProcessadorCurvaABCNumericaTodos(ProcessadorCurvaABCNumerica):
    """Classe para processar dados de Curva ABC Numérica (Todos)"""

    def __init__(self, sql_path):
        """Inicializa o processador de Curva ABC Numérica (Todos)"""
        super().__init__(sql_path, "TODOS")

    def processar(self):
        """Processa os dados de Curva ABC Numérica (Todos)"""
        super().processar()

        # Converter para Int64
        self.df['qtd_acumulado'] = pd.to_numeric(
            self.df['qtd_acumulado'], errors='coerce').astype('Int64')

    def enviar_para_bigquery(self):
        """Envia dados para BigQuery"""
        schema = [
            bigquery.SchemaField("nome_parceiro", "STRING"),
            bigquery.SchemaField("count_contratos", "INTEGER"),
            bigquery.SchemaField("qtd_acumulado", "INTEGER"),
            bigquery.SchemaField("porcentagem", "FLOAT"),
            bigquery.SchemaField("porcentagem_acumulada", "FLOAT"),
            bigquery.SchemaField("classe", "STRING"),
        ]

        self.gerenciador


class ProcessadorAnalises:
    """Classe para processar dados de análises"""

    def __init__(self, sql_path):
        """Inicializa o processador"""
        self.sql_path = sql_path
        self.df_analises = None
        self.df_contratos = None
        self.df = None
        self.colunas_analises = [
            'nome_pretendente', 'doc_pretendente', 'id_parceiro',
            'nome_parceiro', 'data_analise', 'valor_aluguel_analisado',
            'resultado_analise_pretendente', 'origem_analise'
        ]
        self.colunas_contratos = {
            'Código do Contrato': 'codigo_contrato',
            'Locatário': 'Locatario',
            'Receb.': 'data_recebido',
            'Envio': 'data_enviado',
            'Assin.': 'data_assinado',
            'Sistema': 'data_sistema',
            'Captadora': 'captadora',
            'Valor': 'valor'
        }
        self.gerenciador_bq = GerenciadorBigQuery()

    def processar(self):
        """Processa os dados de análises"""
        print('\n\t------>ANALISES<------\n')

        # Obter dados do sistema
        print('Obtendo dados do sistema...')
        con = db.connect_to_db()
        cursor = con.cursor()

        resultados = db.execute_select_in_db(cursor, self.sql_path)
        self.df_analises = pd.DataFrame(
            resultados, columns=self.colunas_analises)

        # Remover duplicados
        self.df_analises = self.df_analises.drop_duplicates(
            subset=['nome_pretendente', 'resultado_analise_pretendente',
                    'valor_aluguel_analisado'],
            keep='first'
        )

        # Obter dados da planilha de contratos
        print('Obtendo dados da planilha de contratos...')
        self.df_contratos = planilhas_transacionais.get_recebidos_enviados_assinados()

        # Renomear e selecionar colunas
        print('Tratando dados da planilha...')
        self.df_contratos.rename(columns=self.colunas_contratos, inplace=True)
        self.df_contratos = self.df_contratos[self.colunas_contratos.values()]

        # Remover duplicados
        self.df_contratos = self.df_contratos.drop_duplicates(
            subset=['codigo_contrato', 'Locatario', 'valor'],
            keep='first'
        )

        # Remover última linha (geralmente totais ou rodapé)
        self.df_contratos = self.df_contratos.iloc[:-1]

        # Tratar dados vazios
        print('Tratando dados vazios...')
        self.df_contratos['data_recebido'] = self.df_contratos.apply(
            lambda row: row['data_enviado'] if row['data_recebido'] == '' else row['data_recebido'],
            axis=1
        )

        self.df_contratos['data_enviado'] = self.df_contratos.apply(
            lambda row: row['data_assinado'] if row['data_enviado'] == '-' else row['data_enviado'],
            axis=1
        )

        self.df_contratos['data_recebido'] = self.df_contratos.apply(
            lambda row: row['data_enviado'] if row['data_recebido'] == '-' else row['data_recebido'],
            axis=1
        )

        # Filtrar valores inválidos
        print('Filtrando valores inválidos...')
        self.df_contratos = self.df_contratos[self.df_contratos['data_recebido'] != 'X']

        # Converter para datetime
        print('Convertendo para datetime...')
        self.df_contratos['data_recebido'] = pd.to_datetime(
            self.df_contratos['data_recebido'], format='%d/%m/%Y %H:%M:%S'
        )

        # Filtrar por data
        print('Filtrando dados a partir de 2023...')
        self.df_contratos = self.df_contratos[self.df_contratos['data_recebido'] >= '2023-01-01']

        # Juntar os DataFrames
        print('Juntando os DataFrames...')
        self.df = pd.merge(
            self.df_analises, self.df_contratos,
            how='left',
            left_on=['nome_pretendente'],
            right_on=['Locatario']
        )

        # Formatar datas
        for col in ["data_enviado", "data_assinado", "data_analise", "data_recebido", "data_sistema"]:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            self.df[col] = self.df[col].dt.date

        cursor.close()
        con.close()
