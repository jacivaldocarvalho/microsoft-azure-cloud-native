/**
 * Terraform Configuration
 * 
 * Description: Creates the Azure resources used by the e-commerce lab.
 * Created By: Jacivaldo Carvalho
 * Created Date: 2025-06-07
 * Last Modified: 2026-10-02

 */

terraform {
  required_version = ">= 1.10, < 2.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.32"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}

# Generate a suffix only when no explicit storage account name is supplied.
resource "random_string" "storage_suffix" {
  count   = var.storage_account_name == null ? 1 : 0
  length  = 6
  upper   = false
  special = false
}


provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name != null ? var.storage_account_name : "${var.prefix}st${random_string.storage_suffix[0].result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  allow_nested_items_to_be_public = false
  min_tls_version                 = "TLS1_2"

  tags = local.common_tags
}

resource "azurerm_mssql_server" "sql_server" {
  name                                    = var.sql_server_name
  resource_group_name                     = azurerm_resource_group.rg.name
  location                                = var.location
  version                                 = "12.0"
  administrator_login                     = var.sql_admin
  administrator_login_password_wo         = var.sql_password
  administrator_login_password_wo_version = var.sql_password_version

  minimum_tls_version = "1.2"

  tags = local.common_tags
}

# Cria o banco de dados SQL dentro do servidor criado anteriormente.
resource "azurerm_mssql_database" "sql_db" {
  name                 = var.sql_db_name
  server_id            = azurerm_mssql_server.sql_server.id
  collation            = "SQL_Latin1_General_CP1_CI_AS"
  sku_name             = "Basic"
  zone_redundant       = false
  storage_account_type = "Local"
}

# Allow only the IPv4 address of the machine running the local application.
resource "azurerm_mssql_firewall_rule" "client" {
  name             = "AllowLabClient"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = var.client_ip_address
  end_ip_address   = var.client_ip_address
}

resource "azurerm_storage_container" "products" {
  name                  = var.storage_container_name
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

locals {
  common_tags = {
    environment = "dev"
    project     = "ecommerce-lab"
    managed_by  = "terraform"
  }
}
