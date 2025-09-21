# Partners BFF Service Helm Chart

This Helm chart deploys the Partners BFF Service FastAPI application on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Apache Pulsar broker

## Installing the Chart

To install the chart with the release name `partners-bff`:

```bash
helm install partners-bff ./helm/partners-bff
```

The command deploys the Partners BFF Service on the Kubernetes cluster with the default configuration.

## Uninstalling the Chart

To uninstall/delete the `partners-bff` deployment:

```bash
helm uninstall partners-bff
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `us-east1-docker.pkg.dev/misw4406-2025-14-desacopla2/partners-bff/partners-bff` |
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
| `broker.url` | Pulsar broker URL | `pulsar://pulsar-broker.pulsar.svc.cluster.local:6650` |

## Examples

### Install with custom values

```bash
helm install partners-bff ./helm/partners-bff \
  --set replicaCount=3 \
  --set image.tag=v1.0.0 \
  --set service.type=LoadBalancer
```


### Install with custom Pulsar configuration

```bash
helm install partners-bff ./helm/partners-bff \
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
kubectl get pods -l app.kubernetes.io/name=partners-bff
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=partners-bff
```

### Port forward for local access
```bash
kubectl port-forward svc/partners-bff 8000:8000
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