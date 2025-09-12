output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

# Network outputs
output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.main.name
}

output "vpc_network_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.main.id
}

output "gke_subnet_name" {
  description = "Name of the GKE subnet"
  value       = google_compute_subnetwork.gke_subnet.name
}

output "cloudsql_subnet_name" {
  description = "Name of the Cloud SQL subnet"
  value       = google_compute_subnetwork.cloudsql_subnet.name
}

# Multiple PostgreSQL instances outputs
output "postgres_instances" {
  description = "Information about all created PostgreSQL instances"
  value = {
    for key, instance in google_sql_database_instance.postgres_instances : key => {
      instance_name = instance.name
      connection_name = instance.connection_name
      private_ip = instance.private_ip_address
      database_name = google_sql_database.databases[key].name
      database_user = google_sql_user.users[key].name
    }
  }
}


# GKE outputs
output "gke_cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.main.name
}

output "gke_cluster_location" {
  description = "Location of the GKE cluster"
  value       = google_container_cluster.main.location
}

output "gke_cluster_endpoint" {
  description = "Endpoint of the GKE cluster"
  value       = google_container_cluster.main.endpoint
}

output "gke_cluster_ca_certificate" {
  description = "CA certificate of the GKE cluster"
  value       = google_container_cluster.main.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

# Service Account outputs
output "gke_node_service_account_email" {
  description = "Email of the GKE node service account"
  value       = google_service_account.gke_node_sa.email
}

output "app_service_account_email" {
  description = "Email of the application service account"
  value       = google_service_account.app_sa.email
}

output "workload_identity_pool" {
  description = "Workload Identity pool for the project"
  value       = "${var.project_id}.svc.id.goog"
}

# Connection information for applications
output "database_connection_info" {
  description = "Database connection information for all PostgreSQL instances"
  value = {
    for key, instance in google_sql_database_instance.postgres_instances : key => {
      host     = instance.private_ip_address
      port     = 5432
      database = google_sql_database.databases[key].name
      user     = google_sql_user.users[key].name
      ssl_mode = "require"
      instance_name = instance.name
      connection_name = instance.connection_name
    }
  }
  sensitive = true
}


# Artifact Registry outputs
output "artifact_registry_repositories" {
  description = "Information about all Artifact Registry repositories"
  value = {
    for key, repo in google_artifact_registry_repository.repositories : key => {
      name     = repo.name
      location = repo.location
      url      = "${var.region}-docker.pkg.dev/${var.project_id}/${repo.name}"
      repository_id = repo.repository_id
    }
  }
}

output "docker_registry_urls" {
  description = "Docker registry URLs for all repositories"
  value = {
    for key, repo in google_artifact_registry_repository.repositories : key => 
      "${var.region}-docker.pkg.dev/${var.project_id}/${repo.name}"
  }
}

# Kubernetes configuration
output "k8s_service_account_annotation" {
  description = "Annotation to add to Kubernetes service account for Workload Identity"
  value       = "iam.gke.io/gcp-service-account=${google_service_account.app_sa.email}"
}
