output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "location" {
  value = azurerm_resource_group.rg.location
}

output "function_app_name" {
  value = azurerm_linux_function_app.api.name
}

output "function_app_base_url" {
  value = "https://${azurerm_linux_function_app.api.default_hostname}"
}

output "application_insights_connection_string" {
  value     = azurerm_application_insights.app_insights.connection_string
  sensitive = true
}

output "ai_search_endpoint" {
  value = var.enable_ai_search ? "https://${azurerm_search_service.search[0].name}.search.windows.net" : null
}

output "ai_search_admin_key" {
  value     = var.enable_ai_search ? azurerm_search_service.search[0].primary_key : null
  sensitive = true
}

output "openai_endpoint" {
  value = var.enable_openai ? azurerm_cognitive_account.openai[0].endpoint : null
}

output "openai_key" {
  value     = var.enable_openai ? azurerm_cognitive_account.openai[0].primary_access_key : null
  sensitive = true
}
