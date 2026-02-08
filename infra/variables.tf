variable "location" {
  description = "Region for all resources"
  default     = "uksouth"
}

variable "prefix" {
  description = "Prefix for all resources"
  default     = "xrs-nexus"
}

variable "env" {
  description = "Environment (dev, prod)"
  default     = "dev"
}
