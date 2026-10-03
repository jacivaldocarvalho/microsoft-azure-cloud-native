mock_provider "azurerm" {}
mock_provider "random" {}

variables {
  subscription_id   = "00000000-0000-0000-0000-000000000000"
  sql_server_name   = "lab-test-server"
  sql_db_name       = "ecommerce"
  sql_admin         = "labadmin"
  sql_password      = "Offline-Test-Only-42!"
  client_ip_address = "203.0.113.10"
}

run "private_storage_and_client_firewall" {
  command = plan

  assert {
    condition     = azurerm_storage_container.products.container_access_type == "private" && !azurerm_storage_account.storage.allow_nested_items_to_be_public
    error_message = "Product images must not allow anonymous access."
  }
  assert {
    condition     = azurerm_mssql_firewall_rule.client.start_ip_address == var.client_ip_address && azurerm_mssql_firewall_rule.client.end_ip_address == var.client_ip_address
    error_message = "SQL access must be limited to the supplied client IPv4 address."
  }
  assert {
    condition     = output.sql_database_name == var.sql_db_name && output.storage_container_name == "products"
    error_message = "Connection outputs must match provisioned resources."
  }
}

run "explicit_storage_name" {
  command = plan
  variables {
    storage_account_name = "labteststorage123"
  }
  assert {
    condition     = azurerm_storage_account.storage.name == "labteststorage123"
    error_message = "Explicit storage account names must be honored."
  }
  assert {
    condition     = length(random_string.storage_suffix) == 0
    error_message = "An explicit storage account name must not create an unused random suffix."
  }
}

run "reject_azure_wide_firewall_address" {
  command = plan
  variables {
    client_ip_address = "0.0.0.0"
  }
  expect_failures = [var.client_ip_address]
}

run "reject_invalid_storage_name" {
  command = plan
  variables {
    storage_account_name = "Invalid-Storage"
  }
  expect_failures = [var.storage_account_name]
}

run "reject_empty_sql_password" {
  command = plan
  variables {
    sql_password = ""
  }
  expect_failures = [var.sql_password]
}

run "single_region_for_all_resources" {
  command = plan
  variables {
    location = "brazilsouth"
  }
  assert {
    condition     = azurerm_resource_group.rg.location == var.location && azurerm_mssql_server.sql_server.location == var.location && azurerm_storage_account.storage.location == var.location
    error_message = "The resource group, SQL server, and storage account must use the selected lab region."
  }
}
