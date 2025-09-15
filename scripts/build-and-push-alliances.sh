#!/bin/bash

# Build and push Docker image for alliances-service
# Usage: ./scripts/build-and-push-alliances.sh [tag]

set -e

# Configuration
PROJECT_ID="misw4406-2025-14-desacopla2"
REGION="us-east1"
REPOSITORY="alliances-service"
IMAGE_NAME="alliances-service"

# Get tag from argument or use 'latest'
TAG=${1:-latest}

# Full image name
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"

echo "🚀 Building and pushing Docker image..."
echo "Image: ${FULL_IMAGE_NAME}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Configure Docker to use gcloud as a credential helper
echo "📋 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and push the Docker image for multiple platforms
echo "🔨 Building and pushing Docker image for multiple platforms (amd64, arm64)..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${FULL_IMAGE_NAME} \
    --push \
    --file gestion-de-alianzas/Dockerfile \
    gestion-de-alianzas/

echo "✅ Successfully built and pushed: ${FULL_IMAGE_NAME}"
echo "🎯 You can now deploy with: ./scripts/deploy-alliances.sh"
