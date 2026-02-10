resource "azurerm_cognitive_account" "speech" {
  count               = var.enable_speech ? 1 : 0
  name                = "${var.prefix}-${var.env}-speech"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "SpeechServices"
  sku_name            = "F0" # Free Tier if available, else S0
}

resource "azurerm_cognitive_account" "language" {
  count               = var.enable_language ? 1 : 0
  name                = "${var.prefix}-${var.env}-language"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "TextAnalytics"
  sku_name            = "F0" # Free Tier
}

resource "azurerm_cognitive_account" "openai" {
  count               = var.enable_openai ? 1 : 0
  name                = "${var.prefix}-${var.env}-openai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0" # Standard (Free trial has 0 quota usually, but this creates the account)
}

resource "azurerm_search_service" "search" {
  count               = var.enable_ai_search ? 1 : 0
  name                = "${var.prefix}-${var.env}-search"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "free" # Free Tier
  # Semantic search not supported in free tier
}
