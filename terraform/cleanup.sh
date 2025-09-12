#!/bin/bash

# Terraform cleanup script for GCP infrastructure
set -e

echo "🧹 Starting Terraform cleanup..."

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found!"
    echo "Cannot proceed with cleanup without knowing which resources to destroy"
    exit 1
fi

echo "⚠️  This will destroy ALL resources created by Terraform:"
echo "   - VPC network and subnets"
echo "   - Cloud SQL PostgreSQL instance (ALL DATA WILL BE LOST)"
echo "   - GKE Autopilot cluster"
echo "   - Service accounts and IAM bindings"
echo ""
echo "🔴 WARNING: This action cannot be undone!"
echo ""

read -p "Are you sure you want to destroy all resources? Type 'yes' to confirm: " confirmation

if [ "$confirmation" = "yes" ]; then
    echo "🗑️  Destroying infrastructure..."
    terraform destroy -auto-approve
    
    echo ""
    echo "✅ Infrastructure destroyed successfully!"
    echo ""
    echo "🧹 Cleanup completed. All resources have been removed."
    
else
    echo "❌ Cleanup cancelled"
    exit 1
fi
