# Multiple Artifact Registry repositories for Docker images
resource "google_artifact_registry_repository" "repositories" {
  for_each = var.artifact_registry_repositories
  
  location      = var.region
  repository_id = each.value.repository_id
  description   = each.value.description
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-latest-tag"
    action = "KEEP"
    condition {
      tag_state = "TAGGED"
      tag_prefixes = ["latest"]
    }
  }

  cleanup_policies {
    id     = "keep-recent-untagged"
    action = "KEEP"
    most_recent_versions {
      keep_count = 3
    }
  }
}

# IAM binding to allow GKE service accounts to pull images from all repositories
resource "google_artifact_registry_repository_iam_binding" "repositories_reader" {
  for_each = var.artifact_registry_repositories
  
  location   = google_artifact_registry_repository.repositories[each.key].location
  repository = google_artifact_registry_repository.repositories[each.key].name
  role       = "roles/artifactregistry.reader"

  members = [
    "serviceAccount:${google_service_account.gke_node_sa.email}",
    "serviceAccount:${google_service_account.app_sa.email}",
  ]
}

