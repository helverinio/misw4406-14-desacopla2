# Create GKE cluster
resource "google_container_cluster" "main" {
  name     = "${var.project_name}-gke"
  location = var.region

  # Use Autopilot mode
  enable_autopilot = true

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnet.gke_subnet.name

  # Configure private cluster
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  # Configure IP allocation for pods and services
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Configure master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = var.gke_subnet_cidr
      display_name = "GKE Subnet"
    }
  }

  # Configure workload identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  depends_on = [
    google_project_service.required_apis,
    google_compute_subnet.gke_subnet
  ]
}
