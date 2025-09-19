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

```bash
# Install dependencies
uv sync

# Run the orchestrator
uv run python app.py
```

## Environment Variables

- `BROKER_URL`: Pulsar broker URL (default: pulsar://localhost:6650)
- `DATABASE_URL`: PostgreSQL connection string
- `INTEGRACIONES_API_URL`: gestion-de-integraciones service URL
- `ALIANZAS_API_URL`: gestion-de-alianzas service URL
