resource "azurerm_service_plan" "asp" {
  name                = "${var.prefix}-${var.env}-asp"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption
}

resource "azurerm_linux_function_app" "function" {
  name                       = "${var.prefix}-${var.env}-func"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = var.location
  service_plan_id            = azurerm_service_plan.asp.id
  storage_account_name       = azurerm_storage_account.st.name
  storage_account_access_key = azurerm_storage_account.st.primary_access_key

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }
}
