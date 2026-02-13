# Synapse Workspace and Spark Pool Configuration

resource "azurerm_synapse_workspace" "synapse" {
  name                                 = "${var.prefix}-${var.env}-synapse-${random_string.suffix.result}"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = "westus2" # Using West US 2 for better capacity
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.bronze.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "P@ssw0rd1234!" # In real env, use Key Vault

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.env
    Project     = "XRS-Nexus"
  }
}

# Synapse Spark Pool
resource "azurerm_synapse_spark_pool" "spark_pool" {
  name                 = "sparkpool01"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  node_size_family     = "MemoryOptimized"
  node_size            = "Small" # 8 vCores per node (minimum allowed by Azure)

  auto_scale {
    max_node_count = 3 # Min allowed by Azure (24 vCores max)
    min_node_count = 3 # Min allowed by Azure (24 vCores baseline)
  }

  auto_pause {
    delay_in_minutes = 5 # Faster shutdown to save trial credits
  }

  spark_version = "3.3"

  tags = {
    Environment = var.env
    Project     = "XRS-Nexus"
  }
}

# Allow Synapse to access Storage
resource "azurerm_role_assignment" "synapse_storage" {
  scope                = azurerm_storage_account.stg.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_synapse_workspace.synapse.identity[0].principal_id
}

# Firewall rule to allow Azure services
resource "azurerm_synapse_firewall_rule" "allow_azure" {
  name                 = "AllowAllWindowsAzureIps"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"
}

# Firewall rule to allow all IPs (for development - restrict in production)
resource "azurerm_synapse_firewall_rule" "allow_all" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}
