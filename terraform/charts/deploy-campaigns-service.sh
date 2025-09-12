#!/bin/bash

# Helm deployment script for campaigns-service
set -e

echo "🚀 Deploying campaigns-service with Helm..."

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Please install Helm first."
    echo "Visit: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl not configured or cluster not accessible."
    echo "Please configure kubectl first:"
    echo "gcloud container clusters get-credentials \$(terraform output -raw gke_cluster_name) --region \$(terraform output -raw region) --project \$(terraform output -raw project_id)"
    exit 1
fi

echo "✅ Helm and kubectl are ready"

# Get values from Terraform outputs
echo "📋 Getting configuration from Terraform outputs..."

# Check if we're in the terraform directory
if [ ! -f "../terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found. Please run this script from the charts directory."
    exit 1
fi

# Get Terraform outputs
cd ..
APP_SA_EMAIL=$(terraform output -raw app_service_account_email 2>/dev/null || echo "")
DB_PRIVATE_IP=$(terraform output -raw cloudsql_private_ip 2>/dev/null || echo "")
DB_NAME=$(terraform output -raw database_name 2>/dev/null || echo "")
DB_USER=$(terraform output -raw database_user 2>/dev/null || echo "")
PROJECT_ID=$(terraform output -raw project_id 2>/dev/null || echo "")

if [ -z "$APP_SA_EMAIL" ] || [ -z "$DB_PRIVATE_IP" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$PROJECT_ID" ]; then
    echo "❌ Could not get all required values from Terraform outputs."
    echo "Please ensure Terraform has been applied successfully."
    exit 1
fi

echo "✅ Configuration retrieved:"
echo "   Project ID: $PROJECT_ID"
echo "   Database IP: $DB_PRIVATE_IP"
echo "   Database Name: $DB_NAME"
echo "   Database User: $DB_USER"
echo "   Service Account: $APP_SA_EMAIL"

# Get database password
echo ""
echo "🔐 Please enter the database password:"
read -s DB_PASSWORD

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Database password is required"
    exit 1
fi

# Encode password to base64
DB_PASSWORD_B64=$(echo -n "$DB_PASSWORD" | base64)

# Go back to charts directory
cd charts

# Create values file for this deployment
VALUES_FILE="campaigns-service-values.yaml"
cat > $VALUES_FILE << EOF
# Generated values for campaigns-service deployment
image:
  repository: gcr.io/$PROJECT_ID/alpespartners
  tag: "latest"

serviceAccount:
  annotations:
    iam.gke.io/gcp-service-account: "$APP_SA_EMAIL"

database:
  host: "$DB_PRIVATE_IP"
  name: "$DB_NAME"
  user: "$DB_USER"

# Override the secret with the actual password
secrets:
  postgresPassword: "$DB_PASSWORD_B64"
EOF

echo "📝 Created values file: $VALUES_FILE"

# Deploy with Helm
echo "🚀 Deploying campaigns-service..."
helm upgrade --install campaigns-service ./campaigns-service \
  --values $VALUES_FILE \
  --namespace default \
  --create-namespace \
  --wait \
  --timeout 10m

echo ""
echo "✅ campaigns-service deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Check deployment status:"
echo "   kubectl get pods -l app.kubernetes.io/name=campaigns-service"
echo ""
echo "2. Check service:"
echo "   kubectl get svc campaigns-service"
echo ""
echo "3. Check logs:"
echo "   kubectl logs -l app.kubernetes.io/name=campaigns-service"
echo ""
echo "4. Test health endpoint:"
echo "   kubectl port-forward svc/campaigns-service 8080:80"
echo "   curl http://localhost:8080/health"
echo ""
echo "5. View API documentation:"
echo "   curl http://localhost:8080/spec"
echo ""

# Clean up values file
rm -f $VALUES_FILE
echo "🧹 Cleaned up temporary values file"
