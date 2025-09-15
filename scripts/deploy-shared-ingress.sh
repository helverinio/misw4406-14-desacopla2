#!/bin/bash

# Deploy shared ingress for all AlpesPartners services using Helm
# Usage: ./scripts/deploy-shared-ingress.sh [release-name] [namespace]

set -e

RELEASE_NAME=${1:-shared-ingress}
NAMESPACE=${2:-alpespartners}
CHART_PATH="terraform/charts/shared-ingress"
VALUES_FILE="terraform/charts/shared-ingress/values.yaml"

echo "🚀 Deploying shared ingress for AlpesPartners services with Helm..."
echo "Release: ${RELEASE_NAME}"
echo "Namespace: ${NAMESPACE}"
echo "Chart: ${CHART_PATH}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not configured or cluster is not accessible."
    echo "Please run: gcloud container clusters get-credentials --region us-central1 misw4406-2025-14-desacopla2"
    exit 1
fi

# Check if chart directory exists
if [ ! -d "${CHART_PATH}" ]; then
    echo "❌ Chart directory not found: ${CHART_PATH}"
    exit 1
fi

# Check if values file exists
if [ ! -f "${VALUES_FILE}" ]; then
    echo "❌ Values file not found: ${VALUES_FILE}"
    exit 1
fi

# Deploy or upgrade the Helm chart
echo "🔨 Deploying Helm chart..."
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo "📈 Upgrading existing release..."
    helm upgrade ${RELEASE_NAME} ${CHART_PATH} \
        --values ${VALUES_FILE} \
        --namespace ${NAMESPACE}
else
    echo "🆕 Installing new release..."
    helm install ${RELEASE_NAME} ${CHART_PATH} \
        --values ${VALUES_FILE} \
        --namespace ${NAMESPACE} \
        --create-namespace
fi

echo "✅ Successfully deployed shared ingress!"
echo ""
echo "🌐 Ingress status:"
kubectl get ingress -n ${NAMESPACE}
echo ""
echo "🔗 Your services will be accessible at:"
echo "   http://<STATIC_IP>/campaigns"
echo "   http://<STATIC_IP>/alliances"
echo "   http://<STATIC_IP>/integrations"
echo ""
echo "📋 To get the static IP address, run:"
echo "   kubectl get ingress alpespartners-api-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
