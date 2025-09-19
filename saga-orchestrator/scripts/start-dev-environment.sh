#!/bin/bash

# Start development environment for Saga Orchestrator
set -e

echo "🚀 Starting Saga Orchestrator Development Environment"
echo "=" * 50

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to saga orchestrator directory
cd "$(dirname "$0")/.."

# Start infrastructure services
echo "📦 Starting infrastructure services (PostgreSQL, Pulsar)..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check PostgreSQL
echo "🔍 Checking PostgreSQL connection..."
until docker exec saga-postgres-dev pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check Pulsar
echo "🔍 Checking Pulsar connection..."
until docker exec saga-pulsar-dev bin/pulsar-admin brokers healthcheck > /dev/null 2>&1; do
    echo "   Waiting for Pulsar..."
    sleep 5
done
echo "✅ Pulsar is ready"

# Create Pulsar topics
echo "📡 Creating Pulsar topics..."
docker exec saga-pulsar-dev bin/pulsar-admin topics create persistent://public/default/saga-events || true
docker exec saga-pulsar-dev bin/pulsar-admin topics create persistent://public/default/eventos-partners || true
docker exec saga-pulsar-dev bin/pulsar-admin topics create persistent://public/default/gestion-de-integraciones || true
docker exec saga-pulsar-dev bin/pulsar-admin topics create persistent://public/default/administracion-financiera-compliance || true

echo "✅ Pulsar topics created"

# Show connection info
echo ""
echo "🎉 Development environment is ready!"
echo "=" * 50
echo "📊 Service URLs:"
echo "   PostgreSQL: localhost:5432"
echo "   Pulsar Broker: pulsar://localhost:6650"
echo "   Pulsar Admin: http://localhost:8080"
echo "   Pulsar Manager: http://localhost:9527"
echo ""
echo "🔧 Environment Variables for local development:"
echo "   export BROKER_URL=pulsar://localhost:6650"
echo "   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saga_db"
echo "   export INTEGRACIONES_API_URL=http://localhost:5001"
echo "   export ALIANZAS_API_URL=http://localhost:5002"
echo ""
echo "🚀 To start the Saga Orchestrator locally:"
echo "   uv run python app.py"
echo ""
echo "📊 To monitor events:"
echo "   python scripts/monitor_saga_events.py"
echo ""
echo "🧪 To run tests:"
echo "   python scripts/test_saga_integration.py"
echo ""
echo "🛑 To stop the environment:"
echo "   docker-compose -f docker-compose.dev.yml down"
