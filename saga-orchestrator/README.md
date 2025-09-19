# Saga Orchestrator

Central orchestrator service implementing the Saga pattern for coordinating distributed transactions across microservices.

## Overview

This service orchestrates the partner creation workflow between:
- **gestion-de-integraciones**: Creates partners and manages integrations
- **gestion-de-alianzas**: Creates alliances/contracts based on partner events

## Saga Flow

1. Partner creation initiated in gestion-de-integraciones
2. Saga orchestrator receives partner creation event
3. Orchestrator coordinates alliance creation in gestion-de-alianzas
4. Handles success/failure scenarios with compensation logic

## Architecture

- **Saga State Machine**: Manages workflow states and transitions
- **Event Handlers**: Process events from participating services
- **Compensation Logic**: Handles rollback scenarios
- **Pulsar Integration**: Event-driven communication

## Running the Service

### Option 1: Using Docker Compose (Recommended for Development)

```bash
# Start infrastructure services (PostgreSQL + Pulsar)
make dev-up
# or
docker-compose -f docker-compose.dev.yml up -d

# Run the orchestrator locally
make run
# or
uv run python app.py

# Stop infrastructure when done
make dev-down
```

### Option 2: Using Shared Pulsar Broker (Recommended for Integration)

```bash
# Start shared Pulsar broker first (from root directory)
cd .. && docker-compose -f docker-compose.pulsar.yml up -d

# Start saga orchestrator with shared broker
make shared-up
# or
docker-compose -f docker-compose.shared-pulsar.yml up -d

# Stop saga orchestrator
make shared-down

# Stop shared Pulsar (from root directory)
cd .. && docker-compose -f docker-compose.pulsar.yml down
```

### Option 3: Full Docker Compose (All Services)

```bash
# Start all services including orchestrator
make full-up
# or
docker-compose up -d

# Stop all services
make full-down
```

### Option 4: Manual Setup

```bash
# Install dependencies
uv sync

# Set environment variables
export BROKER_URL=pulsar://localhost:6650
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saga_db

# Run the orchestrator
uv run python app.py
```

## Environment Variables

- `BROKER_URL`: Pulsar broker URL (default: pulsar://localhost:6650)
- `DATABASE_URL`: PostgreSQL connection string
- `INTEGRACIONES_API_URL`: gestion-de-integraciones service URL
- `ALIANZAS_API_URL`: gestion-de-alianzas service URL

## Testing

```bash
# Run integration tests
make test
# or
python scripts/test_saga_integration.py

# Monitor events
make monitor
# or
python scripts/monitor_saga_events.py

# Test Docker build and deployment
python scripts/test_docker_build.py
```

## Quick Start Commands

```bash
# Development (recommended)
make dev-up          # Start infrastructure
make run             # Run orchestrator locally
make monitor         # Monitor events (in another terminal)
make dev-down        # Stop when done

# Shared Pulsar integration (recommended for multi-service setup)
make shared-up       # Start with shared Pulsar broker
make shared-down     # Stop saga orchestrator only

# Full Docker deployment
make simple-up       # Start orchestrator + infrastructure
make simple-down     # Stop everything

# Testing and debugging
make test            # Run integration tests
make logs            # View logs
make status          # Check service status
make clean           # Clean up everything
```

## Troubleshooting

If you encounter issues, check the [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) guide for common problems and solutions.
