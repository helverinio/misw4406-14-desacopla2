#!/bin/bash

# Docker build and push script for AlpesPartners application
set -e

echo "🐳 Building and pushing AlpesPartners Docker image..."

# Get project ID from terraform
if [ ! -f "../terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found. Please run this script from the charts directory."
    exit 1
fi

PROJECT_ID=$(grep "project_id" ../terraform.tfvars | cut -d'"' -f2)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Could not find project_id in terraform.tfvars"
    exit 1
fi

echo "✅ Project ID: $PROJECT_ID"

# Configure Docker to use gcloud as a credential helper
echo "🔧 Configuring Docker for GCR..."
gcloud auth configure-docker

# Build the image
IMAGE_NAME="gcr.io/$PROJECT_ID/alpespartners"
TAG="latest"

echo "🏗️  Building Docker image: $IMAGE_NAME:$TAG"
cd ..
docker build -t $IMAGE_NAME:$TAG .

# Push the image
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME:$TAG

echo ""
echo "✅ Image built and pushed successfully!"
echo "   Image: $IMAGE_NAME:$TAG"
echo ""
echo "📋 Next steps:"
echo "1. Deploy the application:"
echo "   cd terraform/charts"
echo "   ./deploy-campaigns-service.sh"
echo ""
echo "2. Or update the Helm chart values:"
echo "   helm upgrade campaigns-service ./campaigns-service --set image.tag=$TAG"
