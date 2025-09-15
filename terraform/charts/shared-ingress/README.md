# Shared Ingress Helm Chart

This Helm chart deploys a shared ingress configuration for all AlpesPartners microservices, providing a single entry point with path-based routing.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Google Cloud Load Balancer (GCE ingress class)
- All microservices deployed and running

## Installing the Chart

To install the chart with the release name `shared-ingress`:

```bash
helm install shared-ingress ./terraform/charts/shared-ingress
```

## Uninstalling the Chart

To uninstall/delete the `shared-ingress` deployment:

```bash
helm uninstall shared-ingress
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.name` | Ingress name | `alpespartners-api-ingress` |
| `ingress.className` | Ingress class | `gce` |
| `ingress.host` | Host name (empty for IP-based access) | `""` |
| `ingress.tls.enabled` | Enable TLS | `false` |
| `ingress.tls.secretName` | TLS secret name | `alpespartners-api-tls` |
| `global.namespace` | Target namespace | `alpespartners` |

### Service Routing Configuration

The chart automatically configures routing for the following services:

| Service | Path | Backend |
|---------|------|---------|
| Campaigns | `/campaigns` | `campaigns-service:80` |
| Alliances | `/alliances` | `alliances-service:80` |
| Integrations | `/integrations` | `integrations-service:80` |

## Examples

### Install with custom host (for hostname-based access)

```bash
helm install shared-ingress ./terraform/charts/shared-ingress \
  --set ingress.host=api.example.com \
  --set ingress.tls.enabled=true
```

### Install with custom namespace

```bash
helm install shared-ingress ./terraform/charts/shared-ingress \
  --set global.namespace=production
```

### Install with custom static IP

```bash
helm install shared-ingress ./terraform/charts/shared-ingress \
  --set ingress.annotations."kubernetes\.io/ingress\.global-static-ip-name"="my-custom-ip"
```

## Adding New Services

To add a new service to the shared ingress, update the `values.yaml` file:

```yaml
ingress:
  services:
    - name: "new-service"
      path: "/new-service"
      pathType: "Prefix"
      port: 80
```

Then upgrade the chart:

```bash
helm upgrade shared-ingress ./terraform/charts/shared-ingress
```

## Troubleshooting

### Check ingress status
```bash
kubectl get ingress -n alpespartners
```

### View ingress details
```bash
kubectl describe ingress alpespartners-api-ingress -n alpespartners
```

### Check ingress events
```bash
kubectl get events -n alpespartners --field-selector involvedObject.name=alpespartners-api-ingress
```

## Service URLs

After successful deployment, your services will be accessible at:

- **Campaigns**: `http://<STATIC_IP>/campaigns`
- **Alliances**: `http://<STATIC_IP>/alliances`
- **Integrations**: `http://<STATIC_IP>/integrations`

**Note**: Replace `<STATIC_IP>` with the actual static IP address. Get it with:
```bash
kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the chart
5. Submit a pull request

## License

This chart is licensed under the same license as the main project.
