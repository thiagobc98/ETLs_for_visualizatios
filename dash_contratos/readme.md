# Documentação Dash Contratos
- **Autor da Documentação:** Thiago Berberich Cabral
- **Data de Criação Dash:** 30/10/2023
- **Última Atualização Documentação:** 06/03/2023
- **Status Projeto:** Concluído
- **Criadores:** Thiago Berberich Cabral, Paulo Ricardo Lima

## Dependencies
Para executar o Dash Contratos, você precisará das seguintes dependências:
- **Variáveis de Ambiente:**
  - `PATH_TOKEN_SHEETS_JSON` e `PATH_CREDENCIAL_SHEETS_JSON` da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br).
  - `PATH_TOKEN_MASTER_LANE_SHEETS` tutorial para obter esse token pode ser encontrado em [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), e [YouTube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato).
  - `PATH_DOWNLOAD_CHROME`: O caminho para download de arquivos no Google.
  - `CODE_SHEETS_DASH_CONTRATOS`: O código das planilhas.

## Links
- **Dashboard:** [Looker Studio  Contratos](https://lookerstudio.google.com/reporting/cd8d4139-3b77-45fb-a266-86c4b861817c).
- **Dados:** [Planilha de dados para o Dashboard  Contratos](https://docs.google.com/spreadsheets/d/1b_9i0Lr8iQlZC-vQk3rpv4aRF1CXB3E4wsLBKDv-dzY/edit?usp=sharing).

## Atualização
- **Frequência:** Atualização todas às quartas-feiras na parte da manhã
- **Modo:** Script Python `dash_contratos\main.py`

## Acessos
- **Proprietário:** Thiago Berberich Cabral
- **Editores:** Paulo Ricardo Lima, Daniel Vianna
- **Leitores:** Matheus Penna, Alberto Teixeira, Bianca Ferreira
- **Gerente de Acessos:** Matheus Penna, Alberto Teixeira

## Fontes de Dados
1. **Planilhas Google:** [Informações para Confecção do Contrato (Aba: Contratos Locador PF)](https://docs.google.com/spreadsheets/d/1mp3g33H62_32ZMfp5wXYCorcprNBAQcSojG9vJniJys/edit#gid=968692995)
	- Pedir acesso para Bianca Ferreira
> Dados são levados para [DADOS_TRANSACIONAIS](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=0)

## Extração de Dados
### Planilha de contratos
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=1090219161) através da função IMPORTRANGE na aba CONTRATOS A:2
- **Script Python:** `dash_contratos\fluxo_contratos.py`

### Gerar o SLA Horas
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=1090219161) através da função IMPORTRANGE na aba CONTRATOS A:2
- **Script Python:** `dash_contratos\sla_horas.py`
