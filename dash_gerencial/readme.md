# Documentação Dash Gerencial
- **Autor da Documentação:** Thiago Berberich Cabral
- **Data de Criação:** 06/10/2024
- **Última Atualização:** 04/03/2024
- **Status Projeto:** Concluído
- **Criadores:** Thiago Berberich Cabral

## Dependencies
Para executar o Dash Gerencial, você precisará das seguintes dependências:
- **Variáveis de Ambiente:**
  - `PATH_TOKEN_SHEETS_JSON` e `PATH_CREDENCIAL_SHEETS_JSON` da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br).
  - `PATH_TOKEN_MASTER_LANE_SHEETS` tutorial para obter esse token pode ser encontrado em [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), e [YouTube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato).
  - `PATH_DOWNLOAD_CHROME`: O caminho para download de arquivos no Google.
  - `CODE_SHEETS_DASH_GERENCIAL`: O código das planilhas.
  - `CODE_SHEETS_DASH_GERENCIAL_COHORT`: O código das planilhas.


## Links
- **Dashboard:** [Looker Studio Gerencial].
- **Dados:** [Planilha de dados para Dashboard Gerencial].
- **Dados:** [Planilha de dados para Dashboard Gerencial - Cohort].



## Atualização
- **Frequência:** Atualização todas às segundas-feiras na parte da manhã
- **Modo:** Script Python `dash_gerencial\main.py`


## Fontes de Dados
1. **Banco de Dados Sistema**
2. **Planilha de dados transacionais**

## Extração de Dados
### Sistema UP
- Via SQL 
- Database
- Scripts
  - **SQL:** `dash_gerencial\sql\rescisao_cohort.sql`, `dash_gerencial\sql\cohort_inadimplentes.sql`
    - **Python:** 
    1. `dash_gerencial\cohort_inadimplentes.py`
    2. `dash_gerencial\cohort_rescisao.py`
    3. `dash_gerencial\main.py`
### Planilha de Contratos 
- Link da planilha de contratos: [Planilha de Contratos - Contratos Locador PF].
    - Pedir acesso para Bianca Ferreira
    - Dados são levados para a [planilha dados transacionais]

- **Script:**
    - **Python:** 
    1. `dash_gerencial\contratos.py`
    2. `dash_gerencial\contratos_2.py`
    3. `dash_gerencial\main.py`
