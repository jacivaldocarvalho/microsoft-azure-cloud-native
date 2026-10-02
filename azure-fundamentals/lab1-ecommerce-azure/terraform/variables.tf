variable "prefix" {
  description = "Prefixo do projeto"
  type        = string
  default     = "ecommerce"
}

variable "suffix" {
  description = "Sufixo para tornar os nomes únicos"
  type        = string
  default     = "dev"
}

variable "location" {
  default = "eastus2"
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
}

variable "storage_account_name" {
  type        = string
  description = "Nome da storage account"
}