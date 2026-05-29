# Documentação Dash Contratos
- **Autor da Documentação:** Thiago Berberich Cabral
- **Data de Criação:** 12/02/2024
- **Última Atualização:** 04/03/2024
- **Status Projeto:** Concluído
- **Criadores:** Thiago Berberich Cabral, Paulo Ricardo Lima

## Dependencies
Para executar o Dash Contratos, você precisará das seguintes dependências:
- **Variáveis de Ambiente:**
  - `PATH_TOKEN_SHEETS_JSON` e `PATH_CREDENCIAL_SHEETS_JSON` da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br).
  - `PATH_TOKEN_MASTER_LANE_SHEETS` tutorial para obter esse token pode ser encontrado em [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), e [YouTube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato).
  - `PATH_DOWNLOAD_CHROME`: O caminho para download de arquivos no Google.
  - `CODE_SHEETS_DASH_ANALISE_DE_CREDITO`: O código das planilhas.

## Links
- **Dashboard:** [Looker Studio  Análise de Crédito](https://lookerstudio.google.com/reporting/2faec92c-c8f9-4ce6-a7e1-1b7e8fbdaabd).
- **Dados:** [Planilha de dados para o Dashboard  Análise de crédito](https://docs.google.com/spreadsheets/d/1VFyXXD2TM4f_3OIfkQxZNQXJkcVJ0DiSWiGI4GfuP0c/edit#gid=2112053216).

## Atualização
- **Frequência:** Atualização todas às segundas-feiras na parte da manhã
- **Modo:** Script Python `dash_analise_credito\main.py`

## Acessos
- **Proprietário:** Thiago Berberich Cabral
- **Editores:** Paulo Ricardo Lima, Daniel Vianna
- **Leitores:** Matheus Penna, Alberto Teixeira
- **Gerente de Acessos:** Matheus Penna

## Fontes de Dados
1. **Banco de dados Sistema UP**


## Extração de Dados
### Sistema UP
- Via SQL 
- Database: appupest_app
- Scripts
  - SQL: `dash_analise_credito\sql\analise_de_credito.sql`, `dash_analise_credito\sql\parceiros.sql`
  - Python: `dash_analise_credito\main.py`
    
=======
### Regras
- **Resultado de análises de crédito**
   - 1 - Aprovado
   - 2, 3, 7 - Pré aprovado
   - 4 - Elegível para manual
   - 5 - Recusa contornável
   - 6 - Recusada
 
- **Vinculo empregaticio**
   - "1">Aposentado/Pensionista
   - "2">Autônomo
   - "3">Empresário
   - "4">Estudante
   - "5">Funcionário CLT
   - "6">Funcionário Público
   - "7">Profissional Liberal
   - "8">Renda proveniente de aluguéis 
