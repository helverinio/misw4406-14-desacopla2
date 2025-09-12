# Create VPC network
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.required_apis]
}

# Create subnet for GKE
resource "google_compute_subnet" "gke_subnet" {
  name          = "${var.project_name}-gke-subnet"
  ip_cidr_range = var.gke_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }
}

# Create subnet for Cloud SQL
resource "google_compute_subnet" "cloudsql_subnet" {
  name          = "${var.project_name}-cloudsql-subnet"
  ip_cidr_range = var.cloudsql_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id
}

# Create private IP range for Cloud SQL
resource "google_compute_global_address" "private_ip_range" {
  name          = "${var.project_name}-private-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

# Create private connection for Cloud SQL
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}
