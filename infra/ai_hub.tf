# Storage for AI Hub
resource "azurerm_storage_account" "ai_sa" {
  name                     = lower(replace("${var.prefix}${var.env}ais${substr(random_id.global_suffix.hex, 0, 4)}", "-", ""))
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# AI Hub
resource "azapi_resource" "hub" {
  type                      = "Microsoft.MachineLearningServices/workspaces@2024-07-01-preview"
  name                      = "${var.prefix}-${var.env}-ai-hub"
  location                  = azurerm_resource_group.rg.location
  parent_id                 = azurerm_resource_group.rg.id
  tags                      = {}
  schema_validation_enabled = false

  body = jsonencode({
    kind = "Hub"
    identity = {
      type = "SystemAssigned"
    }
    properties = {
      friendlyName        = "AI Hub"
      storageAccount      = azurerm_storage_account.ai_sa.id
      keyVault            = azurerm_key_vault.kv.id
      applicationInsights = azurerm_application_insights.app_insights.id
      containerRegistry   = azurerm_container_registry.acr.id
    }
  })

  response_export_values = ["properties.workspaceId", "properties.discoveryUrl"]
}

# AI Project
resource "azapi_resource" "project" {
  type                      = "Microsoft.MachineLearningServices/workspaces@2024-07-01-preview"
  name                      = "${var.prefix}-${var.env}-ai-project"
  location                  = azurerm_resource_group.rg.location
  parent_id                 = azurerm_resource_group.rg.id
  tags                      = {}
  schema_validation_enabled = false

  body = jsonencode({
    kind = "Project"
    identity = {
      type = "SystemAssigned"
    }
    properties = {
      friendlyName  = "AI Project"
      hubResourceId = azapi_resource.hub.id
    }
  })
}
