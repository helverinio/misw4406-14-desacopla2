#!/bin/bash

# Clean up and restart Docker Compose environment
set -e

echo "🧹 Cleaning up existing containers and volumes..."

# Navigate to saga orchestrator directory
cd "$(dirname "$0")/.."

# Stop and remove all containers, networks, and volumes
echo "Stopping all compose services..."
docker-compose down -v 2>/dev/null || true
docker-compose -f docker-compose.dev.yml down -v 2>/dev/null || true
docker-compose -f docker-compose.simple.yml down -v 2>/dev/null || true

# Remove any orphaned containers
echo "Removing orphaned containers..."
docker container prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Remove unused volumes (optional - uncomment if you want to clean data)
# echo "Removing unused volumes..."
# docker volume prune -f

echo "✅ Cleanup complete!"
echo ""
echo "🚀 Ready to start fresh. Use one of:"
echo "   make dev-up       # Development environment"
echo "   make simple-up    # Simple environment"
echo "   make full-up      # Full environment"
