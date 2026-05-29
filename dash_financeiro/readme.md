# Documentação Dash Financeiro
- **Autor da Documentação:** Thiago Berberich Cabral
- **Data de Criação:** 30/10/2023
- **Última Atualização:** 30/10/2023
- **Status Projeto:** Concluído
- **Criadores:** Thiago Berberich Cabral

## Dependencies
Para executar o Dash Financeiro, você precisará das seguintes dependências:
- **Variáveis de Ambiente:**
  - `PATH_TOKEN_SHEETS_JSON` e `PATH_CREDENCIAL_SHEETS_JSON` da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br).
  - `PATH_TOKEN_MASTER_LANE_SHEETS` tutorial para obter esse token pode ser encontrado em [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), e [YouTube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato).
  - `PATH_DOWNLOAD_CHROME`: O caminho para download de arquivos no Google.
  - `CODE_SHEETS_DASH_FINANCEIRO`: O código das planilhas.

## Links
- **Dashboard:** [Looker Studio Financeiro](https://lookerstudio.google.com/reporting/3d7eec0b-b360-4a3d-b4ee-e7c1308318e6).
- **Dados:** [Planilha de dados para Dashboard Financeiro](https://docs.google.com/spreadsheets/d/1uma35KXtzXViZyHri3ij_Yswq-z38OKPd8-oPRAouKA/edit?usp=sharing).

## Atualização
- **Frequência:** Atualização todas às segundas-feiras na parte da manhã
- **Modo:** Script Python `dash_financeiro\main.py`

## Acessos
- **Proprietário:** Thiago Berberich Cabral

## Fontes de Dados
1. **Banco de Dados Sistema

## Extração de Dados
### Sistema UP
- Database
- **Script:**
  - **SQL:**
    1. `dash_financeiro\sql\bloco01.sql`
    2. `dash_financeiro\sql\bloco02.sql`
    3. `dash_financeiro\sql\bloco03.sql`
    4. `dash_financeiro\sql\bloco04_grafico01.sql`
    5. `dash_financeiro\sql\bloco04_grafico02.sql`
    6. `dash_financeiro\sql\bloco05_tabela01.sql`
    7. `dash_financeiro\sql\bloco05_tabela02.sql`
    8. `dash_financeiro\sql\bloco06_grafico1e2.sql`
    9. `dash_financeiro\sql\bloco06_grafico03.sql`
  - **Python:** 
    1. `dash_financeiro\main.py`
