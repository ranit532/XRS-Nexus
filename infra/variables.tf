variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "xrs-nexus-dev-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "prefix" {
  description = "Prefix for all resources"
  default     = "xrs-nexus"
}

variable "env" {
  description = "Environment (dev, prod)"
  default     = "dev"
}

variable "enable_ai_search" {
  description = "Provision Azure AI Search. Note: Free SKU is limited and may not support vector/semantic."
  type        = bool
  default     = false
}

variable "enable_openai" {
  description = "Provision Azure OpenAI account (model deployments are manual in Azure AI Studio)."
  type        = bool
  default     = false
}

variable "enable_language" {
  description = "Provision Azure AI Language (Text Analytics)."
  type        = bool
  default     = false
}

variable "enable_speech" {
  description = "Provision Azure AI Speech."
  type        = bool
  default     = false
}

variable "function_app_python_version" {
  description = "Python version for Azure Functions runtime."
  type        = string
  default     = "3.11"
}

variable "rag_mode" {
  description = "RAG mode for demo: 'text' (free-tier friendly) or 'vector' (requires Search SKU that supports vectors + OpenAI embeddings)."
  type        = string
  default     = "text"
}
