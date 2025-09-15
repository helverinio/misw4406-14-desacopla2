# Shared Ingress Deployment Guide

This guide explains how to deploy AlpesPartners microservices using a single static IP with path-based routing.

## 🎯 **Architecture Overview**

Instead of having separate static IPs for each service, we now use:
- **Single Static IP**: `alpespartners-api-ip`
- **Path-Based Routing**: Different paths route to different services
- **Single Domain**: `api.alpespartners.com`

## 🔗 **Service URLs**

| Service | URL | Path |
|---------|-----|------|
| Campaigns | `http://<STATIC_IP>/campaigns` | `/campaigns` |
| Alliances | `http://<STATIC_IP>/alliances` | `/alliances` |
| Integrations | `http://<STATIC_IP>/integrations` | `/integrations` |

**Note**: Replace `<STATIC_IP>` with the actual static IP address assigned to your ingress.

## 📋 **Deployment Steps**

### **Step 1: Deploy All Services (without individual ingress)**

Deploy each service with ingress disabled:

```bash
# Deploy campaigns service
./scripts/deploy-campaigns.sh

# Deploy alliances service  
./scripts/deploy-alliances.sh

# Deploy integrations service
./scripts/deploy-integrations.sh
```

### **Step 2: Deploy Shared Ingress**

Deploy the shared ingress using the Helm chart:

```bash
./scripts/deploy-shared-ingress.sh
```

Or manually with Helm:

```bash
helm install shared-ingress ./terraform/charts/shared-ingress -n alpespartners --create-namespace
```

### **Step 3: Get Static IP Address**

Get the static IP address assigned to your ingress:

```bash
# Get the static IP address
kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test your services using the IP
curl http://<STATIC_IP>/campaigns/health
curl http://<STATIC_IP>/alliances/health
curl http://<STATIC_IP>/integrations/health
```

## 🔧 **Configuration Details**

### **Static IP Configuration**

The shared ingress uses:
- **Static IP Name**: `alpespartners-api-ip`
- **Ingress Class**: `gce` (Google Cloud Engine)
- **Namespace**: `alpespartners`

### **Path Routing Rules**

```yaml
paths:
- path: /campaigns    → campaigns-service:80
- path: /alliances    → alliances-service:80  
- path: /integrations → integrations-service:80
```

### **SSL/TLS Configuration**

- **TLS**: Disabled (HTTP only for IP-based access)
- **Protocol**: HTTP
- **Note**: For production use, consider setting up SSL termination at the load balancer level

## 🚀 **Benefits**

1. **Cost Effective**: Single static IP instead of multiple
2. **Simplified Management**: One ingress to manage
3. **Consistent URLs**: All services under same domain
4. **Easy SSL**: Single certificate for all services
5. **Better Monitoring**: Centralized traffic monitoring

## 🔍 **Verification**

After deployment, verify everything is working:

```bash
# Check ingress status
kubectl get ingress -n alpespartners

# Check services are running
kubectl get pods -n alpespartners

# Test endpoints (replace with actual IP)
curl -k https://<STATIC_IP>/campaigns/health
curl -k https://<STATIC_IP>/alliances/health
curl -k https://<STATIC_IP>/integrations/health
```

## 🛠 **Troubleshooting**

### **Common Issues**

1. **Services not accessible**:
   - Check if services are running: `kubectl get pods -n alpespartners`
   - Verify ingress configuration: `kubectl describe ingress alpespartners-api-ingress -n alpespartners`

2. **DNS not resolving**:
   - Verify DNS A record points to the static IP
   - Check if static IP is assigned: `kubectl get ingress -n alpespartners`

3. **SSL certificate issues**:
   - Verify certificate is created: `kubectl get secret alpespartners-api-tls -n alpespartners`
   - Check certificate status in Google Cloud Console

### **Useful Commands**

```bash
# Get static IP address
kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Check ingress events
kubectl describe ingress alpespartners-api-ingress -n alpespartners

# View ingress logs
kubectl logs -n alpespartners -l app.kubernetes.io/name=nginx-ingress-controller
```

## 📝 **Migration from Individual IPs**

If you're migrating from individual static IPs:

1. **Backup current configuration**:
   ```bash
   kubectl get ingress -n alpespartners -o yaml > backup-ingress.yaml
   ```

2. **Deploy new configuration**:
   - Deploy services with `enabled: false` for ingress
   - Deploy shared ingress
   - Update DNS

3. **Clean up old resources**:
   ```bash
   # Remove old individual ingress resources
   kubectl delete ingress campaigns-service-ingress -n alpespartners
   kubectl delete ingress alliances-service-ingress -n alpespartners  
   kubectl delete ingress integrations-service-ingress -n alpespartners
   ```

## 🔄 **Adding New Services**

To add a new service to the shared ingress:

1. **Add path to shared-ingress.yaml**:
   ```yaml
   - path: /new-service
     pathType: Prefix
     backend:
       service:
         name: new-service
         port:
           number: 80
   ```

2. **Redeploy shared ingress**:
   ```bash
   ./scripts/deploy-shared-ingress.sh
   ```

3. **Update DNS if needed** (usually not required)

## 📞 **Support**

For issues or questions:
- Check the troubleshooting section above
- Review Kubernetes ingress documentation
- Check Google Cloud Load Balancer logs
