#!/bin/bash

# Terraform deployment script for GCP infrastructure
set -e

echo "🚀 Starting Terraform deployment for GCP infrastructure..."

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found!"
    echo "Please copy terraform.tfvars.example to terraform.tfvars and fill in your values:"
    echo "cp terraform.tfvars.example terraform.tfvars"
    exit 1
fi

# Check if backend.conf exists
if [ ! -f "backend.conf" ]; then
    echo "❌ backend.conf not found!"
    echo "Please copy backend.conf.example to backend.conf and update with your GCS bucket:"
    echo "cp backend.conf.example backend.conf"
    echo "Then edit backend.conf with your bucket name"
    exit 1
fi

# Check if required variables are set
if ! grep -q "project_id.*=" terraform.tfvars || ! grep -q "database_password.*=" terraform.tfvars; then
    echo "❌ Required variables not set in terraform.tfvars!"
    echo "Please set project_id and database_password in terraform.tfvars"
    exit 1
fi

echo "✅ Configuration files found"

# Create GCS bucket for state if it doesn't exist
BUCKET_NAME=$(grep "bucket" backend.conf | cut -d'"' -f2)
echo "🔧 Checking GCS bucket: $BUCKET_NAME"

if ! gsutil ls gs://$BUCKET_NAME >/dev/null 2>&1; then
    echo "📦 Creating GCS bucket for Terraform state..."
    gsutil mb gs://$BUCKET_NAME
    echo "✅ Bucket created successfully"
else
    echo "✅ Bucket already exists"
fi

# Initialize Terraform with backend configuration
echo "🔧 Initializing Terraform with remote state..."
terraform init -backend-config=backend.conf

# Plan the deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo "⚠️  This will create the following resources:"
echo "   - VPC network with subnets"
echo "   - Cloud SQL PostgreSQL instance"
echo "   - GKE Autopilot cluster"
echo "   - Service accounts with proper permissions"
echo "   - IAM bindings for Workload Identity"
echo ""
read -p "Do you want to proceed? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Applying Terraform configuration..."
    terraform apply tfplan
    
    echo ""
    echo "✅ Infrastructure deployed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure kubectl:"
    echo "   gcloud container clusters get-credentials \$(terraform output -raw gke_cluster_name) --region \$(terraform output -raw region) --project \$(terraform output -raw project_id)"
    echo ""
    echo "2. Update Kubernetes manifests with your values:"
    echo "   # Get service account email"
    echo "   terraform output app_service_account_email"
    echo "   # Get database private IP"
    echo "   terraform output cloudsql_private_ip"
    echo ""
    echo "3. Deploy your application:"
    echo "   kubectl apply -f k8s-manifests/"
    echo ""
    echo "🔍 Useful commands:"
    echo "   terraform output                    # View all outputs"
    echo "   terraform destroy                   # Clean up resources"
    echo "   kubectl get nodes                   # Check cluster status"
    
else
    echo "❌ Deployment cancelled"
    rm -f tfplan
    exit 1
fi
