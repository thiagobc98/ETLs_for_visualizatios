# Documentação Dash Comercial 
Author Documentation: Paulo Ricardo Lima   
Creation Date: 31/08/2023  
Author Update: Paulo Ricardo Lima  
Last Update: 30/10/2023  
Status: Finished  
Creators: Paulo Ricardo Lima, Thiago Berberich

## Dependencies
- Python libraries run: `pip install requirements.txt`
- Environment variables
  - Precisa ter PATH_TOKEN_SHEETS_JSON e PATH_CREDENCIAL_SHEETS_JSON da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br)
  - PATH_TOKEN_MASTER_LANE_SHEETS tutorial para pegar o token [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), [Yotube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato)
  - PATH_DOWNLOAD_CHROME Caminho para download dos arquivos no google
  - SUPERLOGICA_USER, SUPERLOGICA_PASS usuário de acesso ao [Superlógica](https://superlogica.net/)
  - CODE_SHEETS_DADOS_TRANSACIONAIS, CODE_SHEETS_DASH_COMERCIAL código das planilhas 


## Links
Dashboard: [Looker Studio Comercial](https://lookerstudio.google.com/u/0/reporting/a77f6b97-779b-4b15-89d5-1d1ff0c8405d/page/p_z52zlzpg6c?pli=1).  
Data: [Sheet de dados para o Dashboard Comercial](https://docs.google.com/spreadsheets/d/1vDxPi0inVGIuok_pG5hVJocqo90qqEFm6dlYYIYkClw/edit?pli=1#gid=1348169899).  

## Atualização
Frequency: Atualização todas às segundas-feiras na parte da manhã  
Mode: Script Python `dash_comercial\main.py`

## Acessos
Owner: Thiago Berberich Cabral  
Editor: Paulo Ricardo Lima, Daniel Vianna   
Reader: Matheus Penna, Alberto Teixeira, Débora Oliveira   
Access Manager: Matheus Penna

## Fontes de dados
Base completa Super Lógica  
Banco de dados Sistema UP   
[Planilhas Google - Parceiros Sistemas](https://docs.google.com/spreadsheets/d/1EF7nNenBI5f8PSVJL7H1F5fz65H61H4-ubN9nwuVrXw/edit#gid=593386082)(Aba: Planilha)  
[Planilhas Google - Imóveis Desocupados 💨 ](https://docs.google.com/spreadsheets/d/1EF7nNenBI5f8PSVJL7H1F5fz65H61H4-ubN9nwuVrXw/edit#gid=593386082)(Aba: Devol. de chaves)  
[Planilhas Google - Informações para confecção do contrato](https://docs.google.com/spreadsheets/d/1EF7nNenBI5f8PSVJL7H1F5fz65H61H4-ubN9nwuVrXw/edit#gid=593386082)(Aba: Contratos Locador PF)

## Extração de Dados

### Super Lógica
- Pelo próprio sistema do Superlógica
- Logar no site [Superlógica](https://superlogica.net/)
  - Clique em "Contratos"
  - Clique em "Impressora" (Canto superior direito)
  - Clique em "Contratos"
  - Filtrar as seguintes opções:
    - Mais opções: status para ativos ou todos
    - Campos adicionais: selecionar com início do contrato, com filiais
  - Clique em "Visualizar"
  - Clique em "Exportar como CSV ou Excel"
- Script: `dash_comercial\superlogica.py`

### Sistema UP
- Via SQL 
- Database: appupest_app
- Scripts
  - SQL: `dash_comercial\sql\sistema_ativos.sql`, `dash_comercial\sql\sistema_todos.sql`
  - Python: `dash_comercial\sistema.py`

### Planilha Parceiros
- Cada novo parceiro deve ser inserido nessa planilha, atualmente é responsabilidade do Eduardo Faria    
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=336447999) através da função IMPORTRANGE na aba DIM_COD_PARCEIROS, célula A:4
- Script: `dash_comercial\utils\planilhas_transacionais.py` 

### Planilha Imóveis Desocupados
- É importada para [DADOS_TRANSACIONAIS - Planilhas Google](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=336447999) através da função IMPORTRANGE na aba DEVOLUCAO_CHAVES, célula A:1
- Script: `dash_comercial\utils\planilhas_transacionais.py` 

### Planilha confecção do contrato
- É importada para DADOS_TRANSACIONAIS - Planilhas Google através da função IMPORTRANGE na aba RECEBIDOS_ENV_ASS, célula A:2
- Script: `dash_comercial\utils\planilhas_transacionais.py` 

=======
# Documentação Dash Comercial
- **Autor da Documentação:** Paulo Ricardo Lima
- **Data de Criação:** 31/08/2023
- **Última Atualização:** 30/10/2023
- **Status Projeto:** Concluído
- **Criadores:** Paulo Ricardo Lima, Thiago Berberich Cabral

## Dependencies
Para executar o Dash Comercial, você precisará das seguintes dependências:
- **Python libraries run:** `pip install requirements.txt`
- **Variáveis de Ambiente:**
  - `PATH_TOKEN_SHEETS_JSON` e `PATH_CREDENCIAL_SHEETS_JSON` da [API do Google Sheets](https://developers.google.com/sheets/api/quickstart/python?hl=pt-br).
  - `PATH_TOKEN_MASTER_LANE_SHEETS`. tutorial para obter esse token pode ser encontrado em [Medium](https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0), [Python Enginer](https://www.python-engineer.com/posts/google-sheets-api/), e [YouTube](https://www.youtube.com/watch?v=FDkknYBBbwQ&ab_channel=FelipeLobato).
  - `PATH_DOWNLOAD_CHROME`: O caminho para download de arquivos no Google.
  - `CODE_SHEETS_DASH_COMERCIAL`: O código das planilhas.

## Links
- **Dashboard:** [Looker Studio Comercial](https://lookerstudio.google.com/u/0/reporting/a77f6b97-779b-4b15-89d5-1d1ff0c8405d/page/p_z52zlzpg6c?pli=1).  
- **Dados:** [Planilha de dados para o Dashboard Comercial](https://docs.google.com/spreadsheets/d/1vDxPi0inVGIuok_pG5hVJocqo90qqEFm6dlYYIYkClw/edit?pli=1#gid=1348169899).  

## Atualização
- **Frequência:** Atualização todas às segundas-feiras na parte da manhã  
- **Modo:** Script Python `dash_comercial\main.py`

## Acessos
- **Proprietário:** Thiago Berberich Cabral
- **Editores:** Paulo Ricardo Lima, Daniel Vianna
- **Leitores:** Matheus Penna, Alberto Teixeira, Débora Oliveira
- **Gerente de Acessos:** Matheus Penna

## Fontes de Dados
1. **Base Completa Super Lógica:** [Superlógica](https://superlogica.net/)
2. **Banco de Dados Sistema UP:** `appupest_app`
3. **Planilhas Google:** [Parceiros Sistemas (Aba: Planilha)](https://docs.google.com/spreadsheets/d/1EF7nNenBI5f8PSVJL7H1F5fz65H61H4-ubN9nwuVrXw/edit#gid=593386082)
4. **Planilhas Google:** [Imóveis Desocupados 💨(Aba: Devol. de chaves)](https://docs.google.com/spreadsheets/d/1i6hZaA3LS5PIpqp-6RM1M_iM_H7njipBnfpvUJsgAnE/edit#gid=1522951899)
5. **Planilhas Google:** [Informações para Confecção do Contrato (Aba: Contratos Locador PF)](https://docs.google.com/spreadsheets/d/1mp3g33H62_32ZMfp5wXYCorcprNBAQcSojG9vJniJys/edit#gid=968692995)

## Extração de Dados
### Super Lógica
1. Logar no site [Superlógica](https://superlogica.net/)
2. Click em "Contratos"
3. Click em "Impressora" (Canto superior direito)
4. Click em "Contratos"
5. Filtrar as seguintes opções:
	- Mais opções: status para ativos ou todos
	- Campos adicionais: selecionar com início do contrato, com filiais
6. Click em "Visualizar"
7. Click em "Exportar como CSV ou Excel"
- **Script:** `dash_comercial\superlogica.py`

### Sistema UP
- **Scripts**
  - **SQL:** 
    1. `dash_comercial\sql\sistema_ativos.sql`
    2. `dash_comercial\sql\sistema_todos.sql`
  - **Python:** `dash_comercial\sistema.py`

### Planilha Parceiros
- Cada novo parceiro deve ser inserido nessa planilha, atualmente é responsabilidade do Eduardo Faria
- É importada para [Planilhas Google - DADOS_TRANSACIONAIS](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=336447999) através da função IMPORTRANGE na aba DIM_COD_PARCEIROS, célula A:4
- **Script:** `dash_comercial\utils\planilhas_transacionais.py` 

### Planilha Imóveis Desocupados
- É importada para [Planilhas Google - DADOS_TRANSACIONAIS](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=1902143247) através da função IMPORTRANGE na aba DEVOLUCAO_CHAVES, célula A:1
- **Script:** `dash_comercial\utils\planilhas_transacionais.py`

### Planilha confecção do contrato
- É importada para [Planilhas Google - DADOS_TRANSACIONAIS](https://docs.google.com/spreadsheets/d/1qgIDPZbKhHluuc75i0Ls0mSxPiULKFVSeG5cP505p-E/edit#gid=0) através da função IMPORTRANGE na aba RECEBIDOS_ENV_ASS, célula A:2
- **Script:** `dash_comercial\utils\planilhas_transacionais.py` 
>>>>>>> 6c0d86a77549070f6fe39509bbc3101cc3731fa4
