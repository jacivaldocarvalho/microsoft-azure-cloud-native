
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.33.0"
    }
  }
}

# Limites para gerar o nome único para storage account.
resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}


# Define o provedor da Azure necessário para o Terraform.
provider "azurerm" {
  features {}
}

# Cria um Resource Group, que é um agrupamento lógico de recursos na Azure.
resource "azurerm_resource_group" "rg" {
  name     = "rg-ecommerce"
  location = var.location
}

# Cria uma Storage Account para armazenar arquivos.
resource "azurerm_storage_account" "storage" {
  name                     = "${var.prefix}storage${random_integer.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  #allow_blob_public_access = false

  tags = {
    environment = "dev"
  }
}

# Cria um servidor SQL (Azure SQL Server)
resource "azurerm_mssql_server" "sql_server" {
  name                         = var.sql_server_name
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_password

  minimum_tls_version = "1.2"

  tags = {
    environment = "dev"
  }
}

# Cria o banco de dados SQL dentro do servidor criado anteriormente.
resource "azurerm_mssql_database" "sql_db" {
  name               = var.sql_db_name
  server_id          = azurerm_mssql_server.sql_server.id
  collation          = "SQL_Latin1_General_CP1_CI_AS"
  sku_name           = "Basic"
  zone_redundant     = false
  storage_account_type = "Local"
}

# Cria uma regra de firewall que permite acesso de serviços da Azure ao SQL Server. 
# OBS: esta regra permite acesso de qualquer serviço da Azure, o que deve ser evitado em produção.
resource "azurerm_mssql_firewall_rule" "allow_azure" {
  name             = "AllowAzure"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
