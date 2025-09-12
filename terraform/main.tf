# This file serves as the main entry point for the Terraform configuration.
# The actual resources are defined in separate files organized by GCP service:
#
# - backend.tf     : Terraform backend configuration and provider setup
# - apis.tf        : GCP API enablement
# - networking.tf  : VPC, subnets, and networking resources
# - cloudsql.tf    : Cloud SQL PostgreSQL database resources
# - gke.tf         : Google Kubernetes Engine cluster
# - iam.tf         : Service accounts and IAM permissions
# - variables.tf   : Input variables
# - outputs.tf     : Output values
#
# This modular approach makes the configuration more maintainable and easier to understand.
