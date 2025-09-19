#!/bin/bash

# Start Saga Orchestrator with shared Pulsar broker
set -e

echo "🚀 Starting Saga Orchestrator with Shared Pulsar Broker"
echo "=" * 60

# Navigate to saga orchestrator directory
cd "$(dirname "$0")/.."

# Check if we're in the right directory structure
if [ ! -f "../docker-compose.pulsar.yml" ]; then
    echo "❌ Error: Cannot find shared Pulsar configuration"
    echo "   Expected: ../docker-compose.pulsar.yml"
    echo "   Make sure you're running this from the saga-orchestrator directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📋 Step 1: Starting shared Pulsar broker..."
cd ..
echo "   Running: docker-compose -f docker-compose.pulsar.yml up -d"
docker-compose -f docker-compose.pulsar.yml up -d

echo "⏳ Waiting for Pulsar broker to be ready..."
sleep 20

# Check if broker is healthy
echo "🔍 Checking Pulsar broker health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker exec broker curl -f http://localhost:8080/admin/v2/brokers/health > /dev/null 2>&1; then
        echo "✅ Pulsar broker is healthy"
        break
    else
        echo "   Attempt $attempt/$max_attempts: Waiting for Pulsar broker..."
        sleep 5
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Pulsar broker failed to become healthy"
    echo "   Check logs: docker logs broker"
    exit 1
fi

echo "📋 Step 2: Starting Saga Orchestrator..."
cd saga-orchestrator
docker-compose -f docker-compose.shared-pulsar.yml up -d

echo "⏳ Waiting for Saga Orchestrator to be ready..."
sleep 15

# Check if saga orchestrator is healthy
echo "🔍 Checking Saga Orchestrator health..."
max_attempts=20
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:5003/health > /dev/null 2>&1; then
        echo "✅ Saga Orchestrator is healthy"
        break
    else
        echo "   Attempt $attempt/$max_attempts: Waiting for Saga Orchestrator..."
        sleep 3
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "⚠️  Saga Orchestrator may not be fully ready yet"
    echo "   Check logs: docker logs saga-orchestrator-shared"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=" * 60
echo "📊 Service URLs:"
echo "   Saga Orchestrator: http://localhost:5003"
echo "   Saga Health Check: http://localhost:5003/health"
echo "   PostgreSQL: localhost:5433"
echo "   Pulsar Broker: pulsar://localhost:6650"
echo "   Pulsar Admin: http://localhost:8081"
echo ""
echo "🔧 Environment Variables for local development:"
echo "   export BROKER_URL=pulsar://localhost:6650"
echo "   export DATABASE_URL=postgresql://postgres:postgres@localhost:5433/saga_db"
echo ""
echo "📊 To monitor:"
echo "   docker logs -f saga-orchestrator-shared"
echo "   docker logs -f broker"
echo ""
echo "🛑 To stop everything:"
echo "   make shared-down"
echo "   cd .. && docker-compose -f docker-compose.pulsar.yml down"
