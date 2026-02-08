resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-${var.env}-rg"
  location = var.location
}

resource "azapi_resource" "ai_hub" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
  name      = "${var.prefix}-${var.env}-ai-hub"
  location  = var.location
  parent_id = azurerm_resource_group.rg.id

  body = jsonencode({
    kind = "Hub"
    sku = {
      name = "Basic"
      tier = "Basic"
    }
    properties = {
      friendlyName        = "XRS Nexus AI Hub"
      storageAccount      = azurerm_storage_account.st.id
      keyVault            = azurerm_key_vault.kv.id
      applicationInsights = azurerm_application_insights.app_insights.id
      containerRegistry   = azurerm_container_registry.acr.id
    }
  })
}

resource "azapi_resource" "ai_project" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
  name      = "${var.prefix}-${var.env}-ai-project"
  location  = var.location
  parent_id = azurerm_resource_group.rg.id

  body = jsonencode({
    kind = "Project"
    properties = {
      friendlyName  = "XRS Nexus Integration Project"
      hubResourceId = azapi_resource.ai_hub.id
    }
  })
}
