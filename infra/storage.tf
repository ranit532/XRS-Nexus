resource "azurerm_storage_account" "st" {
  name                     = replace("${var.prefix}${var.env}st", "-", "")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_key_vault" "kv" {
  name                = "${var.prefix}-${var.env}-kv"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

resource "azurerm_container_registry" "acr" {
  name                = replace("${var.prefix}${var.env}acr", "-", "")
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_application_insights" "app_insights" {
  name                = "${var.prefix}-${var.env}-appinsights"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
}

data "azurerm_client_config" "current" {}
