import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import fluxo_contratos
from workalendar.america import Brazil
from datetime import datetime, timedelta
import sla_horas



def time_start_pipeline():
    start_time = datetime.now()
    print("\n\nInício do pipeline:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return start_time


def time_end_pipeline(start_time):
    end_time = datetime.now()
    print("Fim do pipeline:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    elapsed_time = end_time - start_time
    print("Tempo decorrido:", str(elapsed_time).split(".")[0])


def main_contratos():

    time_start_time = time_start_pipeline()

    df_contratos = fluxo_contratos.main()
    print('\n')
    df_sla_horas = sla_horas.gerando_sla_horas(df_contratos)

    # Correção rápida, isso é gambirrar entender depois o porque esta vindo com dados do ano de 2022
    df_filtrado = df_sla_horas[df_sla_horas['data_recebido'] >= '2023-01-01']

    sla_horas.upload_sheets(df_filtrado)

    time_end_pipeline(time_start_time)


if __name__ == "__main__":
    main_contratos()
