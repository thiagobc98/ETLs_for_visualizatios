import unicodedata
import re

def create_cod_to_merge(texto):
    # Converter o texto para minúsculas
    texto = str(texto).lower()

    # Remover acentos
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

    # Remover espaços em branco
    texto = re.sub(r'\s', '', texto)

    # Remover caracteres especiais, mantendo apenas letras e números
    texto = re.sub(r'[^a-zA-Z0-9]', '', texto)

    return texto

