#!/bin/bash

# Build and push Docker image for campaigns-service
# Usage: ./scripts/build-and-push.sh [tag]

set -e

# Configuration
PROJECT_ID="misw4406-2025-14-desacopla2"
REGION="us-east1"
REPOSITORY="campaigns-service"
IMAGE_NAME="campaigns-service"

# Get tag from argument or use 'latest'
TAG=${1:-latest}

# Full image name
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"

echo "🚀 Building and pushing Docker image..."
echo "Image: ${FULL_IMAGE_NAME}"

# Navigate to project root
cd "$(dirname "$0")/../gestion-de-programas"

# Configure Docker to use gcloud as a credential helper
echo "📋 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and push the Docker image for multiple platforms
echo "🔨 Building and pushing Docker image for multiple platforms (amd64, arm64)..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${FULL_IMAGE_NAME} \
    --push .

echo "✅ Successfully built and pushed: ${FULL_IMAGE_NAME}"
echo "🎯 You can now deploy with: ./scripts/deploy-helm.sh"
