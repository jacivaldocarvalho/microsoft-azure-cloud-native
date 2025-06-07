"""
Script: init-db.py
Description: Realiza query em um banco de dados no Azure.
Author: Jacivaldo Carvalho
Date Created: 2025-06-07
Version: 1.0.0
"""
import os
import pyodbc
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

server_name = os.getenv("SQL_SERVER_NAME")
database_name = os.getenv("SQL_DB_NAME")
user = os.getenv("SQL_USER")
password = os.getenv("SQL_PASSWORD")

if not all([server_name, database_name, user, password]):
    print("Variáveis de ambiente faltando no .env")
    exit(1)

server = f"{server_name}.database.windows.net"

# Caminho do arquivo SQL
sql_file = "init.sql"

if not os.path.isfile(sql_file):
    print(f"Arquivo SQL '{sql_file}' não encontrado.")
    exit(1)

# String de conexão ODBC para Azure SQL
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database_name};"
    f"UID={user};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

try:
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_script = f.read()

    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_script)
            conn.commit()

    print("Script SQL executado com sucesso!")

except Exception as e:
    print(f"Erro ao executar o script SQL: {e}")
