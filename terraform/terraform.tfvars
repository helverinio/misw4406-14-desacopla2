# Copy this file to terraform.tfvars and fill in your values

# Required variables
project_id = "misw4406-2025-14-desacopla2"

# Optional variables (uncomment and modify as needed)
project_name = "misw4406-2025-14-desacopla2"
region = "us-east1"
zone = "us-east1-a"

# Network configuration (optional - defaults are provided)
gke_subnet_cidr = "10.0.1.0/24"
cloudsql_subnet_cidr = "10.0.2.0/24"
pods_cidr = "10.1.0.0/16"
services_cidr = "10.2.0.0/16"
master_ipv4_cidr_block = "172.16.0.0/28"

# Cloud SQL configuration (optional)
cloudsql_tier = "db-f1-micro"  # Free tier - for production, consider db-standard-1 or higher
deletion_protection = true

# Multiple PostgreSQL instances configuration
postgres_instances = {
  campaigns_instance = {
    database_name = "campaigns_database"
    database_user = "campaigns_user"
    database_password = "pA*Eo6@4@kuP3f"
    instance_name = "campaigns-postgres"
  }
#   analytics_instance = {
#     database_name = "analytics_database"
#     database_user = "analytics_user"
#     database_password = "An@lyt1cs#2024!"
#     instance_name = "analytics-postgres"
#   }
#   reporting_instance = {
#     database_name = "reporting_database"
#     database_user = "reporting_user"
#     database_password = "R3p0rt!ng$ecure"
#     instance_name = "reporting-postgres"
#   }
#   audit_instance = {
#     database_name = "audit_database"
#     database_user = "audit_user"
#     database_password = "Aud1t@Tr@il2024"
#     instance_name = "audit-postgres"
#   }
}


# Artifact Registry repositories configuration
artifact_registry_repositories = {
  campaigns_service = {
    repository_id = "campaigns-service"
    description   = "Docker repository for campaigns-service application"
    keep_count    = 5
  }
#   analytics_service = {
#     repository_id = "analytics-service"
#     description   = "Docker repository for analytics-service application"
#     keep_count    = 5
#   }
#   reporting_service = {
#     repository_id = "reporting-service"
#     description   = "Docker repository for reporting-service application"
#     keep_count    = 5
#   }
#   audit_service = {
#     repository_id = "audit-service"
#     description   = "Docker repository for audit-service application"
#     keep_count    = 5
#   }
}

# Kubernetes configuration (optional)
k8s_namespace = "default"
k8s_service_account = "app-sa"
