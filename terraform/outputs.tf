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
  value       = google_compute_subnet.gke_subnet.name
}

output "cloudsql_subnet_name" {
  description = "Name of the Cloud SQL subnet"
  value       = google_compute_subnet.cloudsql_subnet.name
}

# Cloud SQL outputs
output "cloudsql_instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.name
}

output "cloudsql_connection_name" {
  description = "Connection name for Cloud SQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "cloudsql_private_ip" {
  description = "Private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "database_name" {
  description = "Name of the created database"
  value       = google_sql_database.app_database.name
}

output "database_user" {
  description = "Database user name"
  value       = google_sql_user.app_user.name
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
  description = "Database connection information for applications"
  value = {
    host     = google_sql_database_instance.postgres.private_ip_address
    port     = 5432
    database = google_sql_database.app_database.name
    user     = google_sql_user.app_user.name
    ssl_mode = "require"
  }
  sensitive = true
}

# Kubernetes configuration
output "k8s_service_account_annotation" {
  description = "Annotation to add to Kubernetes service account for Workload Identity"
  value       = "iam.gke.io/gcp-service-account=${google_service_account.app_sa.email}"
}
