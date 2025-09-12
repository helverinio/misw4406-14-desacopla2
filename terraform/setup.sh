#!/bin/bash

# Setup script for Terraform GCP infrastructure
set -e

echo "🔧 Setting up Terraform configuration for GCP infrastructure..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ No active gcloud authentication found."
    echo "Please run: gcloud auth login"
    exit 1
fi

echo "✅ gcloud CLI is installed and authenticated"

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No default project set in gcloud."
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Current project: $CURRENT_PROJECT"

# Create terraform.tfvars if it doesn't exist
if [ ! -f "terraform.tfvars" ]; then
    echo "📝 Creating terraform.tfvars from template..."
    cp terraform.tfvars.example terraform.tfvars
    
    # Replace project_id with current project
    sed -i "s/your-gcp-project-id/$CURRENT_PROJECT/g" terraform.tfvars
    
    # Generate a random password
    RANDOM_PASSWORD=$(openssl rand -base64 32)
    sed -i "s/your-secure-database-password/$RANDOM_PASSWORD/g" terraform.tfvars
    
    # Set state bucket name
    STATE_BUCKET="${CURRENT_PROJECT}-terraform-state"
    sed -i "s/your-project-terraform-state/$STATE_BUCKET/g" terraform.tfvars
    
    echo "✅ terraform.tfvars created with your project ID and generated password"
    echo "📋 Generated database password: $RANDOM_PASSWORD"
    echo "💾 Please save this password securely!"
else
    echo "✅ terraform.tfvars already exists"
fi

# Create backend.conf if it doesn't exist
if [ ! -f "backend.conf" ]; then
    echo "📝 Creating backend.conf from template..."
    cp backend.conf.example backend.conf
    
    # Replace bucket name with current project
    STATE_BUCKET="${CURRENT_PROJECT}-terraform-state"
    sed -i "s/your-project-terraform-state/$STATE_BUCKET/g" backend.conf
    
    echo "✅ backend.conf created with your project's state bucket"
else
    echo "✅ backend.conf already exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review terraform.tfvars and backend.conf files"
echo "2. Run ./deploy.sh to deploy the infrastructure"
echo ""
echo "📁 Files created/updated:"
echo "   - terraform.tfvars (with your project ID and generated password)"
echo "   - backend.conf (with your state bucket name)"
echo ""
echo "🔐 Database password: $RANDOM_PASSWORD"
echo "💾 Please save this password securely!"
