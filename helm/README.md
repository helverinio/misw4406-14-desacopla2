# Helm Charts

This directory contains Helm charts for deploying applications to the GKE cluster.

## Charts

### campaigns-service

A Helm chart for deploying the AlpesPartners campaigns service (Flask application).

#### Features

- **Flask Application**: Deploys the AlpesPartners Flask API
- **Database Integration**: Connects to Cloud SQL PostgreSQL
- **Workload Identity**: Uses GCP service accounts for secure authentication
- **Health Checks**: Built-in health and readiness probes
- **Auto-scaling**: Configurable horizontal pod autoscaling
- **Ingress Support**: Optional ingress configuration
- **Security**: Non-root containers with security contexts

#### Quick Start

1. **Build and push the Docker image**:
   ```bash
   ./build-and-push.sh
   ```

2. **Deploy the application**:
   ```bash
   ./deploy-campaigns-service.sh
   ```

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
