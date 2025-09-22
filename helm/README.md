# Helm Charts

This directory contains Helm charts for deploying applications to the GKE cluster provisioned by Terraform.

## Prerequisites

Before deploying applications, ensure you have:

1. **GKE Cluster**: Deployed via Terraform (see [../terraform/README.md](../terraform/README.md))
2. **kubectl configured**: Connected to your GKE cluster
3. **Docker images**: Built and pushed to Artifact Registry
4. **Service accounts**: Configured with Workload Identity

## Quick Start

### 1. Configure kubectl

After Terraform completes, configure kubectl:

```bash
gcloud container clusters get-credentials $(terraform output -raw gke_cluster_name) \
  --region $(terraform output -raw region) \
  --project $(terraform output -raw project_id)
```

### 2. Build and Deploy Applications

```bash
# Build and push Docker images
./build-and-push.sh

# Deploy applications with Helm
./deploy-campaigns-service.sh
```

## Charts

### campaigns-service

A production-ready Helm chart for the AlpesPartners Flask application with:

- **Flask Application**: Deploys the AlpesPartners API
- **Database Integration**: Connects to Cloud SQL PostgreSQL
- **Workload Identity**: Secure authentication with GCP service accounts
- **Health Checks**: Built-in health and readiness probes
- **Auto-scaling**: Configurable horizontal pod autoscaling
- **Security**: Non-root containers with proper security contexts

### partners-bff

A Backend for Frontend (BFF) service for the AlpesPartners platform with:

- **FastAPI Application**: Deploys the Partners BFF API
- **Message Broker Integration**: Connects to Apache Pulsar for event-driven communication
- **Integrations API Integration**: Communicates with the integrations service
- **Health Checks**: Built-in health and readiness probes with `/ping` endpoint
- **Auto-scaling**: Configurable horizontal pod autoscaling
- **Security**: Non-root containers with proper security contexts
- **Configuration Management**: Environment variables for broker URL and integrations API URL

### alliances-service

A Helm chart for the AlpesPartners alliances service.

### compliance-service

A Helm chart for the AlpesPartners compliance service.

### integrations-service

A Helm chart for the AlpesPartners integrations service.

### pulsar

A Helm chart for deploying Apache Pulsar message broker.

### shared-gateway

A shared API gateway configuration.

### shared-ingress

Shared ingress configuration for all services.

## Deployment

### Build and Deploy Applications

The deployment script will:
- Get configuration from Terraform outputs
- Build and push the Docker image to GCR
- Deploy the application using Helm
- Configure Workload Identity automatically

```bash
# Build and push the Docker image
./build-and-push.sh

# Deploy the application with Helm
./deploy-campaigns-service.sh
```

### Verify Deployment

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

## Service Endpoints

The following services are deployed and accessible via their external IP addresses:

| Service | URL |
|---------|-----|
| alliances-service | http://34.144.243.152/ |
| campaigns-service | http://35.244.216.199/ |
| compliance-service | http://34.111.90.7/ |
| integrations-service | http://34.111.239.116/ |
| partners-bff | http://35.227.227.186/ |

## Database Connection

Applications can connect to any of the PostgreSQL instances using:
- **Host**: Private IP (from Terraform output for each instance)
- **Port**: 5432
- **SSL**: Required
- **Authentication**: Using Workload Identity or instance-specific credentials

Get connection details:
```bash
# View all instance connection info
terraform output database_connection_info

# View specific instance info
terraform output postgres_instances

# View all repository URLs
terraform output docker_registry_urls

# View repository details
terraform output artifact_registry_repositories
```

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

#### Manual Deployment

1. **Update values.yaml** with your configuration:
   ```yaml
   image:
     repository: gcr.io/YOUR_PROJECT_ID/alpespartners
     tag: "latest"
   
   serviceAccount:
     annotations:
       iam.gke.io/gcp-service-account: "YOUR_SERVICE_ACCOUNT_EMAIL"
   
   database:
     host: "YOUR_DATABASE_PRIVATE_IP"
     name: "YOUR_DATABASE_NAME"
     user: "YOUR_DATABASE_USER"
   
   secrets:
     postgresPassword: "BASE64_ENCODED_PASSWORD"
   ```

2. **Deploy with Helm**:
   ```bash
   helm upgrade --install campaigns-service ./campaigns-service \
     --values campaigns-service/values.yaml \
     --namespace default \
     --create-namespace
   ```

#### Configuration

The chart supports the following main configuration sections:

- **Image**: Docker image configuration
- **Service Account**: Kubernetes service account with Workload Identity
- **Database**: PostgreSQL connection settings
- **Resources**: CPU and memory limits/requests
- **Autoscaling**: HPA configuration
- **Ingress**: Optional ingress configuration
- **Health Checks**: Liveness and readiness probes

#### Environment Variables

The application uses the following environment variables:

- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port (default: 5432)
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password (from secret)

#### Health Endpoints

- `/health`: Health check endpoint
- `/spec`: API specification (Swagger)

#### Monitoring

Check the deployment status:

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/name=campaigns-service

# Check service
kubectl get svc campaigns-service

# Check logs
kubectl logs -l app.kubernetes.io/name=campaigns-service

# Port forward for testing
kubectl port-forward svc/campaigns-service 8080:80
curl http://localhost:8080/health
```

#### Scaling

Enable autoscaling in values.yaml:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

#### Security

The chart implements several security best practices:

- **Non-root containers**: Runs as user 1000
- **Read-only root filesystem**: Optional configuration
- **Security contexts**: Proper capabilities and permissions
- **Workload Identity**: No service account keys needed
- **Network policies**: Can be extended with network policies

#### Troubleshooting

Common issues and solutions:

1. **Image pull errors**: Ensure the image exists in GCR and you have proper permissions
2. **Database connection errors**: Check database configuration and network connectivity
3. **Service account issues**: Verify Workload Identity binding
4. **Health check failures**: Check application logs and database connectivity

#### Development

To modify the chart:

1. Edit the templates in `campaigns-service/templates/`
2. Update values in `campaigns-service/values.yaml`
3. Test with `helm template campaigns-service ./campaigns-service`
4. Deploy with `helm upgrade --install campaigns-service ./campaigns-service`
