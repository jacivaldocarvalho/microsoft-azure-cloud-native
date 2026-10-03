variable "prefix" {
  description = "Prefixo do projeto"
  type        = string
  default     = "ecommerce"

  validation {
    condition     = can(regex("^[a-z0-9]{1,13}$", var.prefix))
    error_message = "prefix must contain 1 to 13 lowercase letters or digits."
  }
}

variable "location" {
  type        = string
  description = "Single Azure region used by every lab resource"
  default     = "brazilsouth"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name"
  default     = "rg-ecommerce-lab"

  validation {
    condition     = can(regex("^rg-[a-z0-9-]{1,87}$", var.resource_group_name))
    error_message = "resource_group_name must start with rg- and contain lowercase letters, digits, or hyphens."
  }
}

variable "sql_server_name" {
  type        = string
  description = "Nome do servidor SQL"
}

variable "sql_db_name" {
  type        = string
  description = "Nome do banco de dados"
}

variable "sql_admin" {
  type        = string
  description = "Usuário administrador do SQL"
}

variable "sql_password" {
  type        = string
  description = "Senha do SQL Admin"
  sensitive   = true
  ephemeral   = true
  nullable    = false

  validation {
    condition     = length(trimspace(var.sql_password)) > 0
    error_message = "sql_password must not be empty. Supply TF_VAR_sql_password before generating the plan."
  }
}

variable "sql_password_version" {
  type        = number
  description = "Increment to rotate the write-only SQL administrator password"
  default     = 1
}

variable "storage_account_name" {
  type        = string
  description = "Optional globally unique storage account name; null uses a generated name"
  default     = null

  validation {
    condition     = var.storage_account_name == null ? true : can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "storage_account_name must contain 3 to 24 lowercase letters or digits."
  }
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription ID selected for this lab"
}

variable "client_ip_address" {
  type        = string
  description = "Public IPv4 address of the machine connecting to Azure SQL"

  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$", var.client_ip_address)) && can(cidrhost("${var.client_ip_address}/32", 0)) && var.client_ip_address != "0.0.0.0"
    error_message = "client_ip_address must be one valid IPv4 address other than 0.0.0.0."
  }
}

variable "storage_container_name" {
  type        = string
  description = "Private container for product images"
  default     = "products"

  validation {
    condition     = length(var.storage_container_name) >= 3 && length(var.storage_container_name) <= 63 && can(regex("^[a-z0-9]+(-[a-z0-9]+)*$", var.storage_container_name))
    error_message = "Container names must have 3 to 63 lowercase letters, digits, or single interior hyphens."
  }
}
