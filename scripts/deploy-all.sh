#!/bin/bash

# Deploy All Application Helm Charts
# This script deploys all services with BackendConfig for path rewriting

set -e

echo "🚀 Deploying All Application Helm Charts..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
print_status "Checking cluster connectivity..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi
print_success "Cluster connectivity verified"

# Create namespace if it doesn't exist
print_status "Creating namespace 'alpespartners'..."
kubectl create namespace alpespartners --dry-run=client -o yaml | kubectl apply -f -
print_success "Namespace ready"

# Deploy shared-ingress first (includes BackendConfigs)
# print_status "Deploying shared-ingress with BackendConfigs..."
# helm upgrade --install shared-ingress ./terraform/charts/shared-ingress \
#   --namespace alpespartners \
#   --wait \
#   --timeout=5m

# if [ $? -eq 0 ]; then
#     print_success "Shared ingress deployed successfully"
# else
#     print_error "Failed to deploy shared ingress"
#     exit 1
# fi

# Deploy campaigns service
print_status "Deploying campaigns service..."
helm upgrade --install campaigns-service ./terraform/charts/campaigns-service \
  --namespace alpespartners \
  --wait \
  --timeout=5m

if [ $? -eq 0 ]; then
    print_success "Campaigns service deployed successfully"
else
    print_error "Failed to deploy campaigns service"
    exit 1
fi

# Deploy alliances service
print_status "Deploying alliances service..."
helm upgrade --install alliances-service ./terraform/charts/alliances-service \
  --namespace alpespartners \
  --wait \
  --timeout=5m

if [ $? -eq 0 ]; then
    print_success "Alliances service deployed successfully"
else
    print_error "Failed to deploy alliances service"
    exit 1
fi

# Deploy integrations service
print_status "Deploying integrations service..."
helm upgrade --install integrations-service ./terraform/charts/integrations-service \
  --namespace alpespartners \
  --wait \
  --timeout=5m

if [ $? -eq 0 ]; then
    print_success "Integrations service deployed successfully"
else
    print_error "Failed to deploy integrations service"
    exit 1
fi

# Deploy compliance service
print_status "Deploying compliance service..."
helm upgrade --install compliance-service ./terraform/charts/compliance-service \
  --namespace alpespartners \
  --wait \
  --timeout=5m

if [ $? -eq 0 ]; then
    print_success "Compliance service deployed successfully"
else
    print_error "Failed to deploy compliance service"
    exit 1
fi

# Wait for ingress to get external IP
print_status "Waiting for ingress to get external IP..."
EXTERNAL_IP=""
for i in {1..30}; do
    EXTERNAL_IP=$(kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$EXTERNAL_IP" ]; then
        break
    fi
    print_status "Waiting for external IP... (attempt $i/30)"
    sleep 10
done

# Verify deployment
print_status "Verifying deployment..."
echo ""
echo "📋 Deployment Summary:"
echo "======================"

# Check BackendConfigs
print_status "BackendConfigs:"
kubectl get backendconfig -n alpespartners

echo ""
print_status "Services:"
kubectl get svc -n alpespartners

echo ""
print_status "Ingress:"
kubectl get ingress -n alpespartners

echo ""
print_status "Pods:"
kubectl get pods -n alpespartners

echo ""

if [ -n "$EXTERNAL_IP" ]; then
    print_success "🎉 All services deployed successfully!"
    echo ""
    echo "🌐 External IP: $EXTERNAL_IP"
    echo ""
    echo "🎯 Available endpoints with path rewriting:"
    echo "   Campaigns:    http://$EXTERNAL_IP/campaigns/* → /*"
    echo "   Alliances:    http://$EXTERNAL_IP/alliances/* → /*"
    echo "   Integrations: http://$EXTERNAL_IP/integrations/* → /*"
    echo "   Compliance:   http://$EXTERNAL_IP/compliance/* → /*"
    echo ""
    echo "🔍 Test endpoints:"
    echo "   curl http://$EXTERNAL_IP/alliances/posts/ping"
    echo "   curl http://$EXTERNAL_IP/campaigns/health"
    echo "   curl http://$EXTERNAL_IP/integrations/health"
    echo "   curl http://$EXTERNAL_IP/compliance/health"
else
    print_warning "External IP not yet assigned. This may take a few minutes."
    echo "Run 'kubectl get ingress alpespartners-api-ingress -n alpespartners' to check status"
fi

echo ""
print_success "Deployment complete! 🚀"
