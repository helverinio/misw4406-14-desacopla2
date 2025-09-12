variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "misw4406-14"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-a"
}

# Network configuration
variable "gke_subnet_cidr" {
  description = "CIDR block for GKE subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "cloudsql_subnet_cidr" {
  description = "CIDR block for Cloud SQL subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "pods_cidr" {
  description = "CIDR block for GKE pods"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr" {
  description = "CIDR block for GKE services"
  type        = string
  default     = "10.2.0.0/16"
}

variable "master_ipv4_cidr_block" {
  description = "CIDR block for GKE master"
  type        = string
  default     = "172.16.0.0/28"
}

# Cloud SQL configuration
variable "cloudsql_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "postgres_instances" {
  description = "Map of PostgreSQL instances to create with their databases, users and passwords"
  type = map(object({
    database_name = string
    database_user = string
    database_password = string
    instance_name = optional(string)
  }))
  default = {
    app_instance = {
      database_name = "app_database"
      database_user = "app_user"
      database_password = "default_password"
      instance_name = "app-postgres"
    }
  }
  # Removed sensitive = true to allow for_each usage
}


variable "deletion_protection" {
  description = "Enable deletion protection for Cloud SQL"
  type        = bool
  default     = true
}

# Kubernetes configuration
variable "k8s_namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "default"
}

variable "k8s_service_account" {
  description = "Kubernetes service account name"
  type        = string
  default     = "app-sa"
}

# Artifact Registry configuration
variable "artifact_registry_repositories" {
  description = "Map of Artifact Registry repositories to create"
  type = map(object({
    repository_id = string
    description   = string
    keep_count    = optional(number, 5)
  }))
  default = {
    campaigns_service = {
      repository_id = "campaigns-service"
      description   = "Docker repository for campaigns-service application"
      keep_count    = 5
    }
  }
  # No sensitive values, so no sensitive = true needed
}
