# Makefile for Saga Orchestrator

.PHONY: help install dev-up dev-down full-up full-down test clean build

# Default target
help:
	@echo "Saga Orchestrator - Available Commands:"
	@echo "======================================"
	@echo "  install     - Install dependencies with uv"
	@echo "  dev-up      - Start development environment (PostgreSQL + Pulsar)"
	@echo "  dev-down    - Stop development environment"
	@echo "  simple-up   - Start simple environment (orchestrator + infrastructure)"
	@echo "  simple-down - Stop simple environment"
	@echo "  shared-up   - Start with shared Pulsar broker (from root directory)"
	@echo "  shared-down - Stop shared Pulsar environment"
	@echo "  full-up     - Start full environment (all services)"
	@echo "  full-down   - Stop full environment"
	@echo "  run         - Run saga orchestrator locally"
	@echo "  test        - Run integration tests"
	@echo "  monitor     - Monitor saga events"
	@echo "  build       - Build Docker image"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  logs        - Show logs from development environment"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync

# Start development environment (infrastructure only)
dev-up:
	@echo "🚀 Starting development environment..."
	chmod +x scripts/start-dev-environment.sh
	./scripts/start-dev-environment.sh

# Stop development environment
dev-down:
	@echo "🛑 Stopping development environment..."
	chmod +x scripts/stop-dev-environment.sh
	./scripts/stop-dev-environment.sh

# Start simple environment (orchestrator + infrastructure)
simple-up:
	@echo "🚀 Starting simple environment..."
	docker-compose -f docker-compose.simple.yml up -d

# Stop simple environment
simple-down:
	@echo "🛑 Stopping simple environment..."
	docker-compose -f docker-compose.simple.yml down

# Start with shared Pulsar broker
shared-up:
	@echo "🚀 Starting saga orchestrator with shared Pulsar..."
	@echo "⚠️  Make sure shared Pulsar is running first:"
	@echo "   cd .. && docker-compose -f docker-compose.pulsar.yml up -d"
	docker-compose -f docker-compose.shared-pulsar.yml up -d

# Stop shared environment
shared-down:
	@echo "🛑 Stopping shared environment..."
	docker-compose -f docker-compose.shared-pulsar.yml down

# Start full environment (all services)
full-up:
	@echo "🚀 Starting full environment..."
	docker-compose up -d

# Stop full environment
full-down:
	@echo "🛑 Stopping full environment..."
	docker-compose down

# Run saga orchestrator locally
run:
	@echo "🚀 Starting Saga Orchestrator..."
	@echo "Make sure development environment is running (make dev-up)"
	uv run python app.py

# Run integration tests
test:
	@echo "🧪 Running integration tests..."
	uv run python scripts/test_saga_integration.py

# Monitor saga events
monitor:
	@echo "📊 Monitoring saga events..."
	uv run python scripts/monitor_saga_events.py

# Build Docker image
build:
	@echo "🐳 Building Docker image..."
	docker build -t saga-orchestrator:latest .

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	docker system prune -f

# Show logs
logs:
	@echo "📋 Showing development environment logs..."
	docker-compose -f docker-compose.dev.yml logs -f

# Show status
status:
	@echo "📊 Development environment status:"
	docker-compose -f docker-compose.dev.yml ps
