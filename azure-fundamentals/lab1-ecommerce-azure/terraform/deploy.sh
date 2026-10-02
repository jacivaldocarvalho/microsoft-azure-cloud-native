#!/bin/bash

# Carregar variáveis de ambiente do arquivo .env
if [ -f .env ]; then
  echo "Carregando variáveis do .env..."
  export $(grep -v '^#' .env | xargs)
else
  echo "Arquivo .env não encontrado."
  exit 1
fi

# Inicializa Terraform se necessário
if [ ! -d ".terraform" ]; then
  echo "Executando terraform init..."
  terraform init
fi

# Executa o plano e salva em tfplan
echo "Gerando plano Terraform..."
terraform plan -out=tfplan

# Pergunta se deseja aplicar o plano
read -p "Deseja aplicar este plano? (s/n): " CONFIRMAR

if [[ "$CONFIRMAR" == "s" || "$CONFIRMAR" == "S" ]]; then
  echo "Aplicando plano..."
  terraform apply tfplan
else
  echo "Plano não aplicado."
fi

#debug em caso de erro
#terraform destroy -auto-approve
#rm -rf .terraform terraform.tfstate*
#terraform init
#terraform plan -out plan.tfout
#terraform apply plan.tfout