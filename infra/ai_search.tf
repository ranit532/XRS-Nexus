resource "azurerm_search_service" "search" {
  name                = "${var.prefix}-${var.env}-search"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = "standard" # Required for Semantic Search
  semantic_search_sku = "standard"
}
