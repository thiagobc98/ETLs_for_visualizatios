import time
import datetime
import sistema_curva_abc
import analises
import superlogica
import sistema
import recebidos_enviados_assinados
import concatenando
import assinados_desocupados
import analise_pretendentes
import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def time_start_pipeline():
    start_time = datetime.datetime.now()
    print("\n\nInício do pipeline:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    return start_time


def time_end_pipeline(start_time):
    end_time = datetime.datetime.now()
    print("Fim do pipeline:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    elapsed_time = end_time - start_time
    print("Tempo decorrido:", str(elapsed_time).split(".")[0])


def main_comercial():

    time_start_time = time_start_pipeline()
    print("\nPARTE 01\n")
    # superlogica.main()
    sistema.main()
    print("\nPARTE 02\n")
    # concatenando.main()
    print("\nPARTE 03\n")
    analise_pretendentes.main()
    print("\nPARTE 04\n")
    recebidos_enviados_assinados.main()
    print("\nPARTE 05\n")
    assinados_desocupados.main()
    print("\nPARTE 06\n")
    analises.main()
    print("\nPARTE 07\n")

    sistema_curva_abc.main()

    time_end_pipeline(time_start_time)


if __name__ == "__main__":
    main_comercial()
