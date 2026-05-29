import utils.mysql_db as db
import dotenv
import os
import pandas as pd
from utils.sheets import Sheets
dotenv.load_dotenv()

COLUMNS_CONTRATOS = ['id_contrato',
                     'codigo_contrato',
                     'nome_parceiro',
                     'date_inicio_contrato',
                     'data_pausa_contrato',
                     'meses_duracao_contrato',
                     'valor_aluguel_contrato',
                     'name_status',
                     'migracao',
                     'email_parceiro',
                     'rua_end',
                     'numero_end',
                     'complemento_end',
                     'bairro_end',
                     'cidade_end',
                     'estado_end',
                     'cep_end',
                     'Status motivo pausa']

COLUMNS_FATURAS = ['fk_id_contrato',
                   'id_fatura',
                   'vencimento_fatura',
                   'pagamento_fatura',
                   'status_fatura']


con = db.connect_to_db()
cursor = con.cursor()

print('\n\t------>SISTEMA-CONTRATOS<------')
results = db.execute_select_in_db(
    cursor, fr'dash_parceiros\sql\sistema_contratos.sql')
df_contratos = pd.DataFrame(results, columns=COLUMNS_CONTRATOS)

print('\n\t------>SISTEMA-FATURAS<------')
results = db.execute_select_in_db(
    cursor, fr'dash_parceiros\sql\sistema_faturas.sql')
df_faturas = pd.DataFrame(results, columns=COLUMNS_FATURAS)

df_merge = df_contratos.merge(
    df_faturas, left_on='id_contrato', right_on='fk_id_contrato', how='left')

emails_parceiros = {
    'ABRYLAR NEGOCIOS IMOBILIARIOS LTDA': 'taliagnes@gmail.com',
    'ABRYLAR - STACK IMOVEIS - SOLUCOES IMOBILIARIAS LTDA': 'taliagnes@gmail.com',
    'IMOVEIS BRUNO LARA LTDA': 'stella.ppa24@gmail.com',
    'GOLDEN IMÓVEIS LTDA': 'alexmilke75@gmail.com',
    'MAVINC MARAJOARA CONSULTORIA IMOBILIÁRIA LTDA': 'wnogueira@remax.com.br',
    'FIVE-MAVINC MARAJOARA CONSULTORIA IMOBILIÁRIA LTDA ': 'wnogueira@remax.com.br',
    'ANDREA DUTRA NEGOCIOS IMOBILIARIOS LTDA': 'fmullerf2902@gmail.com'

}

# emails_parceiros = {
#     'IMOVEIS BRUNO LARA LTDA': 'thiago.berberich@upestate.com.br'
# }


def tratar_email_parceiro(df):
    df_copy = df.copy()
    df_copy['email_parceiro'] = df_copy.apply(
        lambda row: emails_parceiros.get(
            row['nome_parceiro'], row['email_parceiro']),
        axis=1
    )
    return df_copy


df_merge = tratar_email_parceiro(df_merge)

CODE_SHEETS_DASH_PARCEIROS = os.getenv("CODE_SHEETS_DASH_PARCEIROS")
SISTEMA = 'dados_sistemas'
sheet = Sheets(CODE_SHEETS_DASH_PARCEIROS)
sheet.clear_sheets(SISTEMA)
sheet.upload_to_sheets(df_merge, SISTEMA)

CODE_SHEETS_DASH_PARCEIROS = os.getenv("CODE_SHEETS_DASH_PARCEIROS")
SISTEMA_2 = 'dados_contratos'
sheet = Sheets(CODE_SHEETS_DASH_PARCEIROS)
sheet.clear_sheets(SISTEMA_2)
sheet.upload_to_sheets(df_contratos, SISTEMA_2)
