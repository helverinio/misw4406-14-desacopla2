#!/bin/bash

# Cleanup All Application Helm Charts
# This script removes all deployed services and ingress

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

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This will remove all deployed services and ingress!${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled"
    exit 0
fi

print_status "Starting cleanup..."

# Remove services in reverse order
print_status "Removing compliance service..."
helm uninstall compliance-service -n alpespartners 2>/dev/null || print_warning "Compliance service not found"

print_status "Removing integrations service..."
helm uninstall integrations-service -n alpespartners 2>/dev/null || print_warning "Integrations service not found"

print_status "Removing alliances service..."
helm uninstall alliances-service -n alpespartners 2>/dev/null || print_warning "Alliances service not found"

print_status "Removing campaigns service..."
helm uninstall campaigns-service -n alpespartners 2>/dev/null || print_warning "Campaigns service not found"

print_status "Removing shared ingress..."
helm uninstall shared-ingress -n alpespartners 2>/dev/null || print_warning "Shared ingress not found"

# Wait for resources to be cleaned up
print_status "Waiting for resources to be cleaned up..."
sleep 10

# Check remaining resources
print_status "Checking remaining resources in alpespartners namespace..."
kubectl get all -n alpespartners 2>/dev/null || print_warning "No resources found in alpespartners namespace"

# Check BackendConfigs
print_status "Checking remaining BackendConfigs..."
kubectl get backendconfig -n alpespartners 2>/dev/null || print_warning "No BackendConfigs found"

# Check Ingress
print_status "Checking remaining Ingress resources..."
kubectl get ingress -n alpespartners 2>/dev/null || print_warning "No Ingress resources found"

print_success "Cleanup completed! 🧹"

# Optional: Remove namespace (uncomment if you want to remove the entire namespace)
# print_status "Removing alpespartners namespace..."
# kubectl delete namespace alpespartners 2>/dev/null || print_warning "Namespace alpespartners not found"
# print_success "Namespace removed"
