import mysql.connector
from mysql.connector.cursor import MySQLCursor
from mysql.connector import MySQLConnection
import dotenv
import os

dotenv.load_dotenv()
HOST_DB = os.getenv("HOST_DB_APP")
DATABSE = os.getenv("DATABASE")
USER_DB = os.getenv("USER_DB_APP")
PASS_DB = os.getenv("PASS_DB_APP")


def connect_to_db() -> MySQLConnection:
    con = mysql.connector.connect(
        host=HOST_DB, database=DATABSE, user=USER_DB, password=PASS_DB)

    if con.is_connected():
        db_info = con.get_server_info()
        print(f"Conectado ao servidor MySQL versão {db_info}\n")
    else:
        print('ERROR AO CONECTAR NO BANCO DE DADOS!!!!')
        print('FAVOR VERIFICAR IP!!!!')
    return con


def read_sql(path_sql_file: str) -> str:
    with open(path_sql_file, 'r') as arquivo_sql:
        query = arquivo_sql.read()
    return query


def execute_select_in_db(cursor: MySQLCursor, path_sql_file: str) -> list:
    print('Fazendo select no db...')
    query = read_sql(path_sql_file)
    cursor.execute(query)

    # Obtenha os resultados da consulta
    results = cursor.fetchall()
    return results
