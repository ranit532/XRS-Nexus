resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_storage_account" "stg" {
  name                     = replace("${var.prefix}${var.env}stg${random_string.suffix.result}", "-", "")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true # Essential for ADLS Gen2
}

resource "azurerm_data_factory" "adf" {
  name                = "${var.prefix}-${var.env}-adf-${random_string.suffix.result}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_databricks_workspace" "dbw" {
  name                = "${var.prefix}-${var.env}-dbw-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "standard"
}

resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.stg.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.stg.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.stg.id
}

# Synapse workspace creation disabled due to regional capacity limits
# resource "azurerm_synapse_workspace" "synapse" {
#   name                                 = "${var.prefix}-${var.env}-synapse-${random_string.suffix.result}"
#   resource_group_name                  = azurerm_resource_group.rg.name
#   location                             = var.location
#   storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.bronze.id
#   sql_administrator_login              = "sqladminuser"
#   sql_administrator_login_password     = "P@ssw0rd1234!" # In real env, use Key Vault
#
#   identity {
#     type = "SystemAssigned"
#   }
# }
#
# # Allow Synapse to access Storage
# resource "azurerm_role_assignment" "synapse_storage" {
#   scope                = azurerm_storage_account.stg.id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = azurerm_synapse_workspace.synapse.identity[0].principal_id
# }
