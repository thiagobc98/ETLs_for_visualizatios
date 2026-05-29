# Documentação Dash Cobrança
Author Documentation: Thiago Berberich   
Creation Date Dash: 20/12/2024  
Author Update: Thiago Berberich 
Last Update Documentation: 06/03/2024 <br>
Status: Finished  
Creators: Thiago Berberich

## Dependencies
- Python libraries run: `pip install requirements.txt`
- Environment variables
  - Precisa ter PATH_TOKEN_SHEETS_JSON e PATH_CREDENCIAL_SHEETS_JSON da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br)
  - PATH_TOKEN_MASTER_LANE_SHEETS tutorial para pegar o token [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), [Yotube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato)
  - CODE_SHEETS_DASH_COBRANCAS
  - CODE_SHEETS_DADOS_TRANSACIONAIS


.  

## Atualização
Frequência: Atualização todas às segundas-feiras na parte da manhã  
Modo: Script Python `dash_cobrancas\main.py`


## Fontes de dados
[Imóveis Ocupados] (Aba: Cobrança amigável)  
[Cobranças Extrajudiciais e Pré-Judiciais] 

> Dados são levados para [DADOS_TRANSACIONAIS]

## Extração de Dados

### Planilha Imóveis Ocupados
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google]
- Script: `dash_cobrancas\main.py` 

### Planilha Cobranças Extrajudiciais e Pré-Judiciais
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google]através da função IMPORTRANGE na aba COBRANCA_JUDICIAIS
- Script: `dash_cobrancas\main.py`
