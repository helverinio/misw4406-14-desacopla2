# Alliances Service Helm Chart

This Helm chart deploys the Alliances Service FastAPI application on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PostgreSQL database
- Apache Pulsar broker

## Installing the Chart

To install the chart with the release name `alliances-service`:

```bash
helm install alliances-service ./terraform/charts/alliances-service
```

The command deploys the Alliances Service on the Kubernetes cluster with the default configuration.

## Uninstalling the Chart

To uninstall/delete the `alliances-service` deployment:

```bash
helm uninstall alliances-service
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `us-east1-docker.pkg.dev/misw4406-2025-14-desacopla2/alliances-service/alliances-service` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `NodePort` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Service target port | `8000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `gce` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `database.host` | PostgreSQL host | `10.179.0.3` |
| `database.port` | PostgreSQL port | `5432` |
| `database.name` | PostgreSQL database name | `alpespartners` |
| `database.user` | PostgreSQL username | `postgres_user` |
| `broker.url` | Pulsar broker URL | `pulsar://pulsar-broker.pulsar.svc.cluster.local:6650` |

## Examples

### Install with custom values

```bash
helm install alliances-service ./terraform/charts/alliances-service \
  --set replicaCount=3 \
  --set image.tag=v1.0.0 \
  --set service.type=LoadBalancer
```

### Install with custom database configuration

```bash
helm install alliances-service ./terraform/charts/alliances-service \
  --set database.host=my-postgres.example.com \
  --set database.name=my_database \
  --set database.user=my_user
```

### Install with custom Pulsar configuration

```bash
helm install alliances-service ./terraform/charts/alliances-service \
  --set broker.url=pulsar://my-pulsar.example.com:6650
```

## Health Checks

The chart includes configurable health checks:

- **Liveness Probe**: Ensures the container is running
- **Readiness Probe**: Ensures the container is ready to receive traffic
- **Health Check Endpoint**: `/health` (configurable)

## Security

The chart includes security best practices:

- Non-root user execution
- Security context configuration
- Service account with GCP IAM integration
- Secrets management for sensitive data

## Monitoring

The service exposes metrics and health endpoints that can be used for monitoring:

- Health endpoint: `/health`
- FastAPI docs: `/docs`
- OpenAPI spec: `/openapi.json`

## Troubleshooting

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/name=alliances-service
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=alliances-service
```

### Port forward for local access
```bash
kubectl port-forward svc/alliances-service 8000:8000
```

Then visit: http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the chart
5. Submit a pull request

## License

This chart is licensed under the same license as the main project.