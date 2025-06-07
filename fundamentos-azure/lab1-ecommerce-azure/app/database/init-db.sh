#!/bin/bash

# Carrega variáveis do arquivo .env
if [[ -f ".env" ]]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Arquivo .env não encontrado!"
  exit 1
fi

# Verificações
if [[ -z "$SQL_PASSWORD" || -z "$SQL_SERVER_NAME" || -z "$SQL_USER" || -z "$SQL_DB_NAME" ]]; then
  echo "Variáveis de ambiente faltando. Verifique o .env"
  exit 1
fi

INIT_SQL_PATH="init.sql"

if [[ ! -f "$INIT_SQL_PATH" ]]; then
  echo "Arquivo SQL '$INIT_SQL_PATH' não encontrado."
  exit 1
fi

# Execução do comando
echo "Executando script SQL em $SQL_SERVER_NAME.database.windows.net..."

sqlcmd -S "${SQL_SERVER_NAME}.database.windows.net" \
       -U "$SQL_USER" \
       -P "$SQL_PASSWORD" \
       -d "$SQL_DB_NAME" \
       -i "$INIT_SQL_PATH"

if [[ $? -eq 0 ]]; then
  echo "Script executado com sucesso!"
else
  echo "Erro ao executar script SQL."
fi
