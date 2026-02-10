output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "location" {
  value = azurerm_resource_group.rg.location
}

output "function_app_name" {
  value = var.enable_function_app && length(azurerm_linux_function_app.api) > 0 ? azurerm_linux_function_app.api[0].name : null
}

output "function_app_base_url" {
  value = var.enable_function_app && length(azurerm_linux_function_app.api) > 0 ? "https://${azurerm_linux_function_app.api[0].default_hostname}" : null
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
