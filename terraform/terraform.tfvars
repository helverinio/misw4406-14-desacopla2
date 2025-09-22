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
  integrations_instance = {
    database_name = "integrations_database"
    database_user = "integrations_user"
    database_password = "integrations_password"
    instance_name = "integrations-postgres"
  }
  alliances_instance = {
    database_name = "alliances_database"
    database_user = "alliances_user"
    database_password = "alliances_password"
    instance_name = "alliances-postgres"
  }
  compliance_instance = {
    database_name = "compliance_database"
    database_user = "compliance_user"
    database_password = "compliance_password"
    instance_name = "compliance-postgres"
  }
}


# Artifact Registry repositories configuration
artifact_registry_repositories = {
  campaigns_service = {
    repository_id = "campaigns-service"
    description   = "Docker repository for campaigns-service application"
    keep_count    = 5
  }
  integrations_service = {
    repository_id = "integrations-service"
    description   = "Docker repository for integrations-service application"
    keep_count    = 5
  }
  alliances_service = {
    repository_id = "alliances-service"
    description   = "Docker repository for alliances-service application"
    keep_count    = 5
  }
  compliance_service = {
    repository_id = "compliance-service"
    description   = "Docker repository for compliance-service application"
    keep_count    = 5
  }
  partners_bff = {
    repository_id = "partners-bff"
    description   = "Docker repository for partners-bff application"
    keep_count    = 5
  }
}

# Kubernetes configuration (optional)
k8s_namespace = "default"
k8s_service_account = "app-sa"
