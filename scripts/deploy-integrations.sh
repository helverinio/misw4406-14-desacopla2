#!/bin/bash

# Deploy integrations-service using Helm
# Usage: ./scripts/deploy-integrations.sh [release-name] [namespace]

set -e

# Configuration
RELEASE_NAME=${1:-integrations-service}
NAMESPACE=${2:-alpespartners}
CHART_PATH="terraform/charts/integrations-service"
VALUES_FILE="terraform/charts/integrations-service/values.yaml"

echo "🚀 Deploying integrations-service with Helm..."
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

echo "✅ Successfully deployed integrations-service!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=integrations-service
echo ""
echo "🌐 Ingress status:"
kubectl get ingress -n ${NAMESPACE}
echo ""
echo "🔗 Your application should be accessible at:"
echo "   http://integrations-service-587248656384-uc.a.run.app"
