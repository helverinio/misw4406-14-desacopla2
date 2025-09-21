#!/bin/bash

# Deploy Individual Service
# Usage: ./deploy-service.sh <service-name>
# Example: ./deploy-service.sh alliances-service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if service name is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <service-name>"
    echo "Available services:"
    echo "  - campaigns-service"
    echo "  - alliances-service"
    echo "  - integrations-service"
    echo "  - compliance-service"
    exit 1
fi

SERVICE_NAME=$1
CHART_PATH="../helm/$SERVICE_NAME"

# Validate service name
case $SERVICE_NAME in
    campaigns-service|alliances-service|integrations-service|compliance-service)
        ;;
    *)
        print_error "Invalid service name: $SERVICE_NAME"
        echo "Available services:"
        echo "  - campaigns-service"
        echo "  - alliances-service"
        echo "  - integrations-service"
        echo "  - compliance-service"
        exit 1
        ;;
esac

# Check if chart directory exists
if [ ! -d "$CHART_PATH" ]; then
    print_error "Chart directory not found: $CHART_PATH"
    exit 1
fi

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

# Create namespace if it doesn't exist
print_status "Creating namespace 'alpespartners'..."
kubectl create namespace alpespartners --dry-run=client -o yaml | kubectl apply -f -

# Deploy the service
print_status "Deploying $SERVICE_NAME..."
helm upgrade --install $SERVICE_NAME $CHART_PATH \
  --namespace alpespartners \
  --wait \
  --timeout=5m

if [ $? -eq 0 ]; then
    print_success "$SERVICE_NAME deployed successfully"
    
    # Show service status
    echo ""
    print_status "Service status:"
    kubectl get svc $SERVICE_NAME -n alpespartners
    kubectl get pods -l app.kubernetes.io/name=$SERVICE_NAME -n alpespartners
    
    # Get external IP if available
    EXTERNAL_IP=$(kubectl get ingress alpespartners-api-ingress -n alpespartners -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [ -n "$EXTERNAL_IP" ]; then
        echo ""
        print_success "Service accessible at:"
        case $SERVICE_NAME in
            campaigns-service)
                echo "  http://$EXTERNAL_IP/campaigns/*"
                ;;
            alliances-service)
                echo "  http://$EXTERNAL_IP/alliances/*"
                ;;
            integrations-service)
                echo "  http://$EXTERNAL_IP/integrations/*"
                ;;
            compliance-service)
                echo "  http://$EXTERNAL_IP/compliance/*"
                ;;
        esac
    fi
else
    print_error "Failed to deploy $SERVICE_NAME"
    exit 1
fi
