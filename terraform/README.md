# Terraform GCP Infrastructure

This Terraform configuration provisions a complete infrastructure setup on Google Cloud Platform (GCP) including:

- **Cloud SQL PostgreSQL Database** with private IP
- **GKE Autopilot Cluster** for containerized applications
- **VPC Network** with proper subnets and security
- **Service Accounts** with Workload Identity for secure pod-to-database communication

## File Structure

The Terraform configuration is organized into logical modules for better maintainability:

```
terraform/
├── main.tf                    # Main entry point and documentation
├── backend.tf                 # Terraform backend and provider configuration
├── apis.tf                    # GCP API enablement
├── networking.tf              # VPC, subnets, and networking resources
├── cloudsql.tf               # Cloud SQL PostgreSQL database resources
├── gke.tf                    # Google Kubernetes Engine cluster
├── iam.tf                    # Service accounts and IAM permissions
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── terraform.tfvars.example  # Example variables file
├── backend.conf.example      # Example backend configuration
├── setup.sh                  # Automated setup script
├── deploy.sh                 # Deployment script
├── cleanup.sh                # Cleanup script
├── charts/                   # Helm charts for application deployment
│   ├── campaigns-service/    # AlpesPartners campaigns service chart
│   ├── build-and-push.sh    # Docker build and push script
│   ├── deploy-campaigns-service.sh  # Helm deployment script
│   └── README.md            # Charts documentation
└── README.md                 # This documentation
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        VPC Network                         │
│  ┌─────────────────┐              ┌─────────────────────┐  │
│  │   GKE Subnet    │              │  Cloud SQL Subnet   │  │
│  │                 │              │                     │  │
│  │  ┌───────────┐  │              │  ┌───────────────┐  │  │
│  │  │   Pods    │  │              │  │  PostgreSQL   │  │  │
│  │  │           │  │              │  │   Database    │  │  │
│  │  │ ┌───────┐ │  │              │  │               │  │  │
│  │  │ │  App  │ │  │              │  │               │  │  │
│  │  │ │  Pod  │ │  │              │  │               │  │  │
│  │  │ └───────┘ │  │              │  │               │  │  │
│  │  └───────────┘  │              │  └───────────────┘  │  │
│  └─────────────────┘              └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **GCP Project**: You need a GCP project with billing enabled
2. **Terraform**: Install Terraform >= 1.0
3. **Google Cloud SDK**: Install and authenticate with `gcloud auth application-default login`
4. **Required APIs**: The Terraform configuration will enable the necessary APIs automatically

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Navigate to the terraform directory**:
   ```bash
   cd terraform
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```
   This will automatically:
   - Detect your current GCP project
   - Create `terraform.tfvars` with your project ID
   - Generate a secure database password
   - Create `backend.conf` for state management
   - Set up the GCS bucket name

3. **Deploy the infrastructure**:
   ```bash
   ./deploy.sh
   ```

### Option 2: Manual Setup

1. **Copy configuration files**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   cp backend.conf.example backend.conf
   ```

2. **Edit `terraform.tfvars`** with your values:
   ```hcl
   project_id = "your-gcp-project-id"
   database_password = "your-secure-password"
   state_bucket = "your-project-terraform-state"
   ```

3. **Edit `backend.conf`** with your bucket name:
   ```hcl
   bucket = "your-project-terraform-state"
   prefix = "terraform/state"
   ```

4. **Initialize and deploy**:
   ```bash
   ./deploy.sh
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
- `database_password`: Password for the database user

### Optional Variables

- `project_name`: Prefix for resource names (default: "misw4406-14")
- `region`: GCP region (default: "us-central1")
- `cloudsql_tier`: Database instance size (default: "db-f1-micro")
- `deletion_protection`: Enable deletion protection (default: true)

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
- **Backups**: Automated daily backups with point-in-time recovery
- **Deletion Protection**: Prevents accidental deletion

## Helm Charts

The `charts/` directory contains Helm charts for deploying applications:

### campaigns-service

A production-ready Helm chart for the AlpesPartners Flask application with:

- **Flask Application**: Deploys the AlpesPartners API
- **Database Integration**: Connects to Cloud SQL PostgreSQL
- **Workload Identity**: Secure authentication with GCP service accounts
- **Health Checks**: Built-in health and readiness probes
- **Auto-scaling**: Configurable horizontal pod autoscaling
- **Security**: Non-root containers with proper security contexts

For detailed information, see [charts/README.md](charts/README.md).

## Deploying Applications

### 1. Configure kubectl

After Terraform completes, configure kubectl:

```bash
gcloud container clusters get-credentials $(terraform output -raw gke_cluster_name) \
  --region $(terraform output -raw region) \
  --project $(terraform output -raw project_id)
```

### 2. Build and Deploy the Application

```bash
# Build and push the Docker image
cd charts
./build-and-push.sh

# Deploy the application with Helm
./deploy-campaigns-service.sh
```

The deployment script will:
- Get configuration from Terraform outputs
- Build and push the Docker image to GCR
- Deploy the application using Helm
- Configure Workload Identity automatically

### 3. Verify Deployment

Check the deployment status:

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/name=campaigns-service

# Check service
kubectl get svc campaigns-service

# Check logs
kubectl logs -l app.kubernetes.io/name=campaigns-service

# Test health endpoint
kubectl port-forward svc/campaigns-service 8080:80
curl http://localhost:8080/health
```

The application connects to the database using:
- **Host**: Private IP (from Terraform output)
- **Port**: 5432
- **SSL**: Required
- **Authentication**: Using Workload Identity

## Connecting to the Database

### From GKE Pods

The recommended approach is to use the Cloud SQL Proxy:

```yaml
# Add to your deployment
- name: cloud-sql-proxy
  image: gcr.io/cloudsql-docker/gce-proxy:1.33.2
  command:
    - "/cloud_sql_proxy"
    - "-instances=CONNECTION_NAME=tcp:5432"
    - "-credential_file=/var/secrets/google/key.json"
```

### From External Applications

For external access, you can:

1. **Use Cloud SQL Proxy** on your local machine
2. **Create a bastion host** in the VPC
3. **Use Cloud Shell** with authorized networks

## Monitoring and Logging

- **Cloud Logging**: All resources send logs to Cloud Logging
- **Cloud Monitoring**: Metrics are automatically collected
- **Database Logs**: SQL statements and performance metrics logged

## Cost Optimization

- **Autopilot**: GKE Autopilot optimizes resource usage
- **Preemptible Nodes**: Can be configured for non-production workloads
- **Database Tiers**: Start with `db-f1-micro` for development

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

**Warning**: This will delete all data in the database. Ensure you have backups if needed.

## Support

For issues or questions:
1. Check the [Terraform Google Provider documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
2. Review [GKE Autopilot documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
3. Check [Cloud SQL documentation](https://cloud.google.com/sql/docs)
