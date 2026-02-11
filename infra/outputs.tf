output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  value = azurerm_storage_account.ai_sa.name
}

output "function_app_name" {
  value = length(azurerm_linux_function_app.api) > 0 ? azurerm_linux_function_app.api[0].name : ""
}

output "function_app_default_hostname" {
  value = length(azurerm_linux_function_app.api) > 0 ? azurerm_linux_function_app.api[0].default_hostname : ""
}

output "key_vault_name" {
  value = azurerm_key_vault.kv.name
}

output "key_vault_id" {
  value = azurerm_key_vault.kv.id
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  value     = azurerm_container_registry.acr.admin_username
  sensitive = true
}

output "acr_admin_password" {
  value     = azurerm_container_registry.acr.admin_password
  sensitive = true
}

output "search_service_name" {
  value = length(azurerm_search_service.search) > 0 ? azurerm_search_service.search[0].name : ""
}

output "ai_search_endpoint" {
  value = length(azurerm_search_service.search) > 0 ? "https://${azurerm_search_service.search[0].name}.search.windows.net" : ""
}

output "ai_search_admin_key" {
  value     = length(azurerm_search_service.search) > 0 ? azurerm_search_service.search[0].primary_key : ""
  sensitive = true
}

output "application_insights_connection_string" {
  value     = azurerm_application_insights.app_insights.connection_string
  sensitive = true
}

output "ai_hub_name" {
  value = azapi_resource.hub.name
}

output "ai_hub_id" {
  value = azapi_resource.hub.id
}

output "ai_project_name" {
  value = azapi_resource.project.name
}

output "ai_project_id" {
  value = azapi_resource.project.id
}
