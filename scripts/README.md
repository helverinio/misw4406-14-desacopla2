# Deployment Scripts

This directory contains deployment scripts for all application Helm charts.

## Scripts

### `deploy-all.sh`
Deploys all services and the shared ingress with BackendConfig for path rewriting.

**Usage:**
```bash
cd scripts
./deploy-all.sh
```

**What it does:**
1. Creates the `alpespartners` namespace
2. Deploys shared-ingress with BackendConfigs
3. Deploys all services (campaigns, alliances, integrations, compliance)
4. Waits for external IP assignment
5. Shows deployment summary and test endpoints

### `deploy-service.sh`
Deploys a single service.

**Usage:**
```bash
cd scripts
./deploy-service.sh <service-name>
```

**Examples:**
```bash
./deploy-service.sh alliances-service
./deploy-service.sh campaigns-service
./deploy-service.sh integrations-service
./deploy-service.sh compliance-service
```

### `cleanup.sh`
Removes all deployed services and ingress.

**Usage:**
```bash
cd scripts
./cleanup.sh
```

## Prerequisites

- `kubectl` installed and configured
- `helm` installed
- Access to a Kubernetes cluster
- GKE cluster with BackendConfig support (for path rewriting)

## Path Rewriting

All services are configured with BackendConfig to strip their service prefixes:

- `http://<external-ip>/campaigns/*` → `/*`
- `http://<external-ip>/alliances/*` → `/*`
- `http://<external-ip>/integrations/*` → `/*`
- `http://<external-ip>/compliance/*` → `/*`

## Testing

After deployment, test the endpoints:

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl http://$EXTERNAL_IP/alliances/posts/ping
curl http://$EXTERNAL_IP/campaigns/health
curl http://$EXTERNAL_IP/integrations/health
curl http://$EXTERNAL_IP/compliance/health
```

## Troubleshooting

- **External IP not assigned**: Wait a few minutes for GKE to assign the static IP
- **Services not accessible**: Check pod status with `kubectl get pods -n alpespartners`
- **Path rewriting not working**: Verify BackendConfigs with `kubectl get backendconfig -n alpespartners`
