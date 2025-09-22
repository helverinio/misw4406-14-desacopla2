# Terraform GCP Infrastructure

This Terraform configuration provisions a complete infrastructure setup on Google Cloud Platform (GCP) including:

- **Multiple Cloud SQL PostgreSQL Instances** with private IPs (up to 4 instances)
- **Multiple Artifact Registry Repositories** for Docker images (up to 4 repositories)
- **GKE Autopilot Cluster** for containerized applications
- **VPC Network** with proper subnets and security
- **Service Accounts** with Workload Identity for secure pod-to-database communication

## File Structure

The project is organized with Terraform infrastructure in this directory and Helm charts in a separate `../helm/` directory:

```
misw4406-14-desacopla2/
├── terraform/                # Infrastructure as Code
│   ├── main.tf              # Main entry point and documentation
│   ├── backend.tf           # Terraform backend and provider configuration
│   ├── apis.tf              # GCP API enablement
│   ├── networking.tf        # VPC, subnets, and networking resources
│   ├── cloudsql.tf          # Multiple Cloud SQL PostgreSQL instances
│   ├── artifact-registry.tf # Multiple Artifact Registry repositories
│   ├── gke.tf               # Google Kubernetes Engine cluster
│   ├── iam.tf               # Service accounts and IAM permissions
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── terraform.tfvars     # Variables configuration
│   └── README.md            # This documentation
├── scripts/                  # Deployment and utility scripts
├── helm/                     # Helm charts for application deployment (see ../helm/README.md)
└── README.md                # Project overview documentation
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                VPC Network                                     │
│                                                                                 │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │         GKE Subnet              │    │        Cloud SQL Subnet            │ │
│  │                                 │    │                                     │ │
│  │  ┌─────────────────────────────┐ │    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │ │
│  │  │         Pods                │ │    │  │All. │ │Camp.│ │Comp.│ │Int. │   │ │
│  │  │                             │ │    │  │ DB  │ │ DB  │ │ DB  │ │ DB  │   │ │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐    │ │    │  └─────┘ └─────┘ └─────┘ └─────┘   │ │
│  │  │  │All. │ │Camp.│ │Comp.│    │ │    │                                     │ │
│  │  │  │Svc  │ │Svc  │ │Svc  │    │ │    │                                     │ │
│  │  │  └─────┘ └─────┘ └─────┘    │ │    │                                     │ │
│  │  │  ┌─────┐ ┌─────┐            │ │    │                                     │ │
│  │  │  │Int. │ │Part.│            │ │    │                                     │ │
│  │  │  │Svc  │ │BFF  │            │ │    │                                     │ │
│  │  │  └─────┘ └─────┘            │ │    │                                     │ │
│  │  └─────────────────────────────┘ │    │                                     │ │
│  └─────────────────────────────────┘    └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Artifact Registry (Global)                            │
│                                                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │Alliances│ │Campaigns│ │Compliance│ │Integrations│ │Partners │                   │
│  │Service  │ │Service  │ │Service  │ │Service  │ │BFF Repo │                   │
│  │  Repo   │ │  Repo   │ │  Repo   │ │  Repo   │ │         │                   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **GCP Project**: You need a GCP project with billing enabled
2. **Terraform**: Install Terraform >= 1.0
3. **Google Cloud SDK**: Install and authenticate with `gcloud auth application-default login`
4. **Required APIs**: The Terraform configuration will enable the necessary APIs automatically

## Quick Start

### 1. Prerequisites Setup

1. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Set your project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs**:
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable container.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable servicenetworking.googleapis.com
   ```

### 2. Configure Terraform

1. **Navigate to the terraform directory**:
   ```bash
   cd terraform
   ```

2. **Configure backend (optional)**:
   ```bash
   # Create backend.conf if you want to use remote state
   # Edit backend.conf with your GCS bucket name
   ```

3. **Update terraform.tfvars** with your project details:
   ```hcl
   project_id = "your-gcp-project-id"
   # Update postgres_instances passwords as needed
   # Update artifact_registry_repositories as needed
   ```

### 3. Deploy Infrastructure

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Plan the deployment**:
   ```bash
   terraform plan
   ```

3. **Apply the configuration**:
   ```bash
   terraform apply
   ```

4. **Configure kubectl** (after deployment):
   ```bash
   gcloud container clusters get-credentials $(terraform output -raw gke_cluster_name) \
     --region $(terraform output -raw region) \
     --project $(terraform output -raw project_id)
   ```

## Remote State Management

This configuration uses Google Cloud Storage (GCS) for remote state management, which provides:

- **Team Collaboration**: Multiple team members can work on the same infrastructure
- **State Locking**: Prevents concurrent modifications
- **State History**: Version history of your infrastructure state
- **Security**: Encrypted state storage in GCS

### State Bucket Configuration

The state bucket is automatically created during deployment. The bucket name follows the pattern:
```
{project-id}-terraform-state
```

For example, if your project ID is `my-gcp-project`, the state bucket will be:
```
my-gcp-project-terraform-state
```

## Configuration

### Required Variables

- `project_id`: Your GCP project ID

### Optional Variables

- `project_name`: Prefix for resource names (default: "misw4406-14")
- `region`: GCP region (default: "us-central1")
- `cloudsql_tier`: Database instance size (default: "db-f1-micro" - free tier)
- `deletion_protection`: Enable deletion protection (default: true)

### PostgreSQL Instances Configuration

The `postgres_instances` variable allows you to configure up to 4 separate PostgreSQL instances:

```hcl
postgres_instances = {
  app_instance = {
    database_name = "app_database"
    database_user = "app_user"
    database_password = "secure_password"
    instance_name = "app-postgres"
  }
  analytics_instance = {
    database_name = "analytics_database"
    database_user = "analytics_user"
    database_password = "another_secure_password"
    instance_name = "analytics-postgres"
  }
  # Add more instances as needed...
}
```

Each instance gets:
- Its own PostgreSQL server
- A dedicated database
- A dedicated user with unique password
- Free tier optimization (no backups, minimal logging)

### Artifact Registry Repositories Configuration

The `artifact_registry_repositories` variable allows you to configure multiple Docker repositories:

```hcl
artifact_registry_repositories = {
  campaigns_service = {
    repository_id = "campaigns-service"
    description   = "Docker repository for campaigns-service application"
    keep_count    = 3
  }
  analytics_service = {
    repository_id = "analytics-service"
    description   = "Docker repository for analytics-service application"
    keep_count    = 3
  }
  # Add more repositories as needed...
}
```

Each repository gets:
- Its own Docker repository
- Configurable image retention (latest tag + N most recent untagged)
- Automatic cleanup policies
- IAM permissions for GKE and CI/CD

## Security Features

### Network Security
- **Private VPC**: All resources are in a private VPC
- **Private IPs**: Cloud SQL uses private IP only
- **Subnet Isolation**: Separate subnets for GKE and Cloud SQL
- **SSL Required**: Database connections require SSL

### Access Control
- **Workload Identity**: Pods authenticate using GCP service accounts
- **Least Privilege**: Service accounts have minimal required permissions
- **IAM Integration**: Proper IAM roles and bindings

### Data Protection
- **Encryption**: Data encrypted at rest and in transit
- **No Backups**: Backups disabled for cost optimization (suitable for development/testing)
- **Deletion Protection**: Prevents accidental deletion

## Next Steps

After successfully deploying the infrastructure with Terraform:

1. **Configure kubectl** to connect to your GKE cluster
2. **Deploy applications** using the Helm charts in the `../helm/` directory
3. **Monitor and manage** your applications

For detailed application deployment instructions, see [../helm/README.md](../helm/README.md).

## Monitoring and Logging

- **Cloud Logging**: All resources send logs to Cloud Logging
- **Cloud Monitoring**: Metrics are automatically collected
- **Database Logs**: SQL statements and performance metrics logged

## Cost Optimization

- **Autopilot**: GKE Autopilot optimizes resource usage
- **Free Tier Databases**: All PostgreSQL instances use `db-f1-micro` (free tier)
- **No Backups**: Backups disabled to minimize costs
- **Minimal Logging**: Reduced logging to save storage costs
- **Image Cleanup**: Automatic cleanup of old Docker images (keeps latest + 3 recent)
- **Preemptible Nodes**: Can be configured for non-production workloads

## Troubleshooting

### Common Issues

1. **API Not Enabled**: Ensure all required APIs are enabled
2. **Quota Exceeded**: Check your GCP quotas
3. **Network Issues**: Verify VPC and subnet configuration
4. **Authentication**: Ensure proper service account permissions

### Useful Commands

```bash
# Check cluster status
kubectl get nodes

# View pod logs
kubectl logs -l app=app-deployment

# Test database connectivity
kubectl exec -it <pod-name> -- psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# View Terraform outputs
terraform output
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all data in all PostgreSQL instances. Since backups are disabled, all data will be permanently lost.

## Support

For issues or questions:
1. Check the [Terraform Google Provider documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
2. Review [GKE Autopilot documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
3. Check [Cloud SQL documentation](https://cloud.google.com/sql/docs)
