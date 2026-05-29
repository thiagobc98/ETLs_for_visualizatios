import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def main_gerencial():
    import contratos
    import contratos_2
    import cohort_inadimplentes
    import cohort_rescisao

if __name__ == "__main__":
    main_gerencial()