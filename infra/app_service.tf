resource "random_id" "global_suffix" {
  byte_length = 4
}

locals {
  # Storage account names must be 3-24 chars, lowercase letters + numbers only.
  storage_name_base = lower(replace("${var.prefix}${var.env}${random_id.global_suffix.hex}", "-", ""))
  function_sa_name  = substr(local.storage_name_base, 0, 24)
}

resource "azurerm_storage_account" "function_sa" {
  name                     = local.function_sa_name
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  allow_nested_items_to_be_public = false
  min_tls_version                 = "TLS1_2"
}

resource "azurerm_service_plan" "func_plan" {
  name                = "${var.prefix}-${var.env}-func-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  os_type  = "Linux"
  sku_name = "Y1" # Azure Functions Consumption (low cost, pay-per-execution)
}

resource "azurerm_linux_function_app" "api" {
  name                = "${var.prefix}-${var.env}-api-${random_id.global_suffix.hex}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.function_sa.name
  storage_account_access_key = azurerm_storage_account.function_sa.primary_access_key

  https_only                = true
  functions_extension_version = "~4"

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    # Functions runtime
    FUNCTIONS_WORKER_RUNTIME    = "python"
    WEBSITE_RUN_FROM_PACKAGE    = "1"
    RAG_MODE                    = var.rag_mode

    # Telemetry
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.app_insights.connection_string

    # Optional AI services (blank when disabled)
    AZURE_SEARCH_ENDPOINT = var.enable_ai_search ? "https://${azurerm_search_service.search[0].name}.search.windows.net" : ""
    AZURE_SEARCH_KEY      = var.enable_ai_search ? azurerm_search_service.search[0].primary_key : ""

    AZURE_OPENAI_ENDPOINT = var.enable_openai ? azurerm_cognitive_account.openai[0].endpoint : ""
    AZURE_OPENAI_KEY      = var.enable_openai ? azurerm_cognitive_account.openai[0].primary_access_key : ""
  }

  site_config {
    application_stack {
      python_version = var.function_app_python_version
    }
  }
}
