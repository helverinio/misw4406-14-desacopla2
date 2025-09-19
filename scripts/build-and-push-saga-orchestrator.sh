#!/bin/bash

# Build and push Saga Orchestrator service
set -e

# Configuration
SERVICE_NAME="saga-orchestrator"
IMAGE_NAME="saga-orchestrator"
TAG=${1:-latest}
REGISTRY=${REGISTRY:-"gcr.io/your-project-id"}

echo "🚀 Building and pushing $SERVICE_NAME..."

# Navigate to service directory
cd "$(dirname "$0")/../$SERVICE_NAME"

# Build Docker image
echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

# Tag for registry
FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME:$TAG"
docker tag $IMAGE_NAME:$TAG $FULL_IMAGE_NAME

# Push to registry
echo "⬆️  Pushing to registry..."
docker push $FULL_IMAGE_NAME

echo "✅ Successfully built and pushed $FULL_IMAGE_NAME"

# Update Kubernetes deployment if exists
if [ -f "../terraform/charts/saga-orchestrator-service/values.yaml" ]; then
    echo "🔄 Updating Kubernetes deployment..."
    sed -i "s|image:.*|image: $FULL_IMAGE_NAME|g" ../terraform/charts/saga-orchestrator-service/values.yaml
    echo "✅ Updated Kubernetes deployment configuration"
fi

echo "🎉 $SERVICE_NAME deployment ready!"
