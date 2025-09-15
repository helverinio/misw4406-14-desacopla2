# Create multiple Cloud SQL PostgreSQL instances
resource "google_sql_database_instance" "postgres_instances" {
  for_each = var.postgres_instances

  name             = each.value.instance_name != null ? each.value.instance_name : "${var.project_name}-${each.key}-postgres"
  database_version = "POSTGRES_16"
  region           = var.region


  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    edition = "ENTERPRISE"
    tier    = var.cloudsql_tier

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }

    # Backup configuration disabled for cost optimization
    backup_configuration {
      enabled = false
    }

    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }

    # Optimized database flags for free tier
    database_flags {
      name  = "log_statement"
      value = "none" # Reduced logging for free tier
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "5000" # Increased threshold for free tier
    }
  }

  deletion_protection = var.deletion_protection
}

# Create databases for each instance
resource "google_sql_database" "databases" {
  for_each = var.postgres_instances

  name     = each.value.database_name
  instance = google_sql_database_instance.postgres_instances[each.key].name
}

# Create users for each instance
resource "google_sql_user" "users" {
  for_each = var.postgres_instances

  name     = each.value.database_user
  instance = google_sql_database_instance.postgres_instances[each.key].name
  password = each.value.database_password

  lifecycle {
    ignore_changes = [password]
  }
}

