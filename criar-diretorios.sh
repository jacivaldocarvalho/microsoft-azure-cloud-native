#!/bin/bash

# Lista de diretórios a serem criados
pastas=(
  "fundamentos-azure"
  "conteinerizacao-aks"
  "azure-container-apps"
  "api-management"
  "serverless-functions"
  "ia-e-copilot"
  "aplicacao-cloud-native"
)

# Criar os diretórios
echo "Criando diretórios..."
for pasta in "${pastas[@]}"; do
  mkdir -p "$pasta"
  echo "Diretório criado: $pasta"
done

echo "Todos os diretórios foram criados com sucesso!"
