#!/bin/bash

# Stop development environment for Saga Orchestrator
set -e

echo "🛑 Stopping Saga Orchestrator Development Environment"
echo "=" * 50

# Navigate to saga orchestrator directory
cd "$(dirname "$0")/.."

# Stop and remove containers
echo "📦 Stopping infrastructure services..."
docker-compose -f docker-compose.dev.yml down

# Optional: Remove volumes (uncomment if you want to clean up data)
# echo "🗑️  Removing volumes..."
# docker-compose -f docker-compose.dev.yml down -v

echo "✅ Development environment stopped"
echo ""
echo "💡 To clean up volumes and data, run:"
echo "   docker-compose -f docker-compose.dev.yml down -v"
