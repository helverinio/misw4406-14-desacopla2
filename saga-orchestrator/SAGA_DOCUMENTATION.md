# Saga Pattern Implementation Documentation

## Overview

This document describes the implementation of the Saga pattern for coordinating distributed transactions. 
The Saga Orchestrator manages the partner creation workflow between `gestion-de-integraciones` and `gestion-de-alianzas` services.

## Architecture

### Components

1. **Saga Orchestrator** (`saga-orchestrator/`)
   - Central coordinator for distributed transactions
   - Manages saga state and workflow execution
   - Handles compensation logic for rollbacks
   - Provides REST API for saga management

2. **Gestion de Integraciones** (Modified)
   - Creates partners and manages integrations
   - Integrated with saga orchestrator for coordinated workflows
   - Publishes partner events to Pulsar

3. **Gestion de Alianzas** (Modified)
   - Creates alliances/contracts based on partner events
   - Enhanced to include saga metadata in events
   - Publishes alliance creation events

### Saga Flow

```mermaid
sequenceDiagram
    participant Client
    participant SagaOrchestrator
    participant Integraciones
    participant Alianzas
    participant Pulsar

    Client->>SagaOrchestrator: POST /api/v1/saga/partner-creation
    SagaOrchestrator->>SagaOrchestrator: Create saga state
    SagaOrchestrator->>Integraciones: POST /api/v1/partners
    Integraciones->>Pulsar: Publish partner_created event
    SagaOrchestrator->>Pulsar: Send alliance creation command
    Alianzas->>Pulsar: Consume alliance command
    Alianzas->>Alianzas: Create alliance/contract
    Alianzas->>Pulsar: Publish alliance_created event
    SagaOrchestrator->>SagaOrchestrator: Complete saga
    SagaOrchestrator->>Client: Saga completed
```

## API Endpoints

### Saga Orchestrator

- `POST /api/v1/saga/partner-creation` - Start partner creation saga
- `GET /api/v1/saga/status/{saga_id}` - Get saga status
- `GET /api/v1/saga/active` - List active sagas
- `GET /health` - Health check

### Gestion de Integraciones (New Endpoints)

- `POST /api/v1/saga/partners` - Create partner via saga
- `GET /api/v1/saga/partners/saga-status/{saga_id}` - Get saga status

## Usage Examples

### Starting a Partner Creation Saga

```bash
curl -X POST http://localhost:5003/api/v1/saga/partner-creation \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Example Partner",
    "email": "partner@example.com",
    "telefono": "+1234567890",
    "direccion": "123 Main Street",
    "correlation_id": "unique-correlation-id"
  }'
```

Response:
```json
{
  "mensaje": "Partner creation saga started successfully",
  "saga_id": "550e8400-e29b-41d4-a716-446655440000",
  "correlation_id": "unique-correlation-id",
  "status": "started"
}
```

### Checking Saga Status

```bash
curl http://localhost:5003/api/v1/saga/status/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "saga": {
    "saga_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "partner_id": "partner-123",
    "alliance_id": "alliance-456",
    "created_at": "2025-09-19T16:58:19Z",
    "completed_at": "2025-09-19T16:58:45Z"
  }
}
```

## Saga States

| State | Description |
|-------|-------------|
| `started` | Saga has been initiated |
| `partner_creation_in_progress` | Partner creation is in progress |
| `partner_created` | Partner has been created successfully |
| `alliance_creation_in_progress` | Alliance creation is in progress |
| `alliance_created` | Alliance has been created successfully |
| `completed` | Saga completed successfully |
| `failed` | Saga failed at some step |
| `compensating` | Compensation actions are being executed |
| `compensated` | Compensation completed |

## Compensation Logic

When a saga fails, the orchestrator executes compensation actions to rollback completed steps:

1. **Partner Creation Compensation**: Delete the created partner
2. **Alliance Creation Compensation**: Mark alliance as cancelled (if applicable)

## Event Topics

| Topic | Purpose | Producer | Consumer |
|-------|---------|----------|----------|
| `saga-events` | Saga orchestration events | Saga Orchestrator | Monitoring tools |
| `eventos-partners` | Partner lifecycle events | Gestion de Integraciones | Saga Orchestrator |
| `gestion-de-integraciones` | Alliance creation commands | Saga Orchestrator | Gestion de Alianzas |
| `administracion-financiera-compliance` | Alliance events | Gestion de Alianzas | Saga Orchestrator |

## Configuration

### Environment Variables

#### Saga Orchestrator
```bash
BROKER_URL=pulsar://localhost:6650
DATABASE_URL=postgresql://user:password@localhost:5432/saga_db
INTEGRACIONES_API_URL=http://localhost:5001
ALIANZAS_API_URL=http://localhost:5002
HOST=0.0.0.0
PORT=5003
DEBUG=false
```

#### Gestion de Integraciones
```bash
SAGA_ORCHESTRATOR_URL=http://localhost:5003
```

## Deployment

### Docker

Build and run the saga orchestrator:

```bash
cd saga-orchestrator
docker build -t saga-orchestrator .
docker run -p 5003:5003 \
  -e BROKER_URL=pulsar://pulsar:6650 \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/saga_db \
  saga-orchestrator
```

### Kubernetes

Deploy using Helm:

```bash
helm install saga-orchestrator ./terraform/charts/saga-orchestrator-service
```

## Monitoring and Testing

### Event Monitoring

Monitor saga events in real-time:

```bash
cd saga-orchestrator
python scripts/monitor_saga_events.py --type all
```

### Integration Testing

Run comprehensive saga tests:

```bash
cd saga-orchestrator
python scripts/test_saga_integration.py
```

### Unit Testing

Run unit tests:

```bash
cd saga-orchestrator
python tests/test_saga_flow.py
```

## Error Handling

### Common Error Scenarios

1. **Partner Creation Failure**
   - Saga status: `failed`
   - No compensation needed (no resources created)

2. **Alliance Creation Failure**
   - Saga status: `compensating` → `compensated`
   - Partner is deleted as compensation

3. **Service Unavailability**
   - Saga orchestrator retries with exponential backoff
   - Timeout after configured duration

### Error Response Format

```json
{
  "error": "Error description",
  "codigo": "ERROR_CODE",
  "saga_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-09-19T16:58:19Z"
}
```

## Performance Considerations

- **Database**: PostgreSQL for saga state persistence
- **Message Broker**: Apache Pulsar for event-driven communication
- **Scaling**: Saga orchestrator can be horizontally scaled
- **Timeouts**: Configurable timeouts for each saga step
- **Retries**: Automatic retry with exponential backoff

## Security

- **Authentication**: Service-to-service authentication via API keys
- **Authorization**: Role-based access control for saga operations
- **Encryption**: TLS encryption for all communications
- **Audit**: All saga operations are logged for audit purposes

## Troubleshooting

### Common Issues

1. **Saga Stuck in Progress**
   - Check service availability
   - Verify Pulsar connectivity
   - Review service logs

2. **Compensation Not Working**
   - Verify service endpoints are accessible
   - Check database connectivity
   - Review compensation logic

3. **Event Processing Delays**
   - Monitor Pulsar topic lag
   - Check consumer group status
   - Scale consumer instances if needed

### Debugging Commands

```bash
# Check saga orchestrator health
curl http://localhost:5003/health

# List active sagas
curl http://localhost:5003/api/v1/saga/active

# Monitor Pulsar topics
python scripts/monitor_saga_events.py

# Run integration tests
python scripts/test_saga_integration.py
```

## Best Practices

1. **Idempotency**: All saga operations should be idempotent
2. **Timeouts**: Set appropriate timeouts for each step
3. **Monitoring**: Monitor saga completion rates and failure patterns
4. **Testing**: Regularly test compensation logic
5. **Documentation**: Keep saga documentation up to date
6. **Versioning**: Version saga definitions for backward compatibility

## Future Enhancements

1. **Saga Choreography**: Implement choreography-based sagas
2. **Advanced Compensation**: More sophisticated compensation strategies
3. **Saga Visualization**: Web UI for saga monitoring and management
4. **Performance Optimization**: Caching and optimization improvements
5. **Multi-tenant Support**: Support for multiple tenants/organizations
