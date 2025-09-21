#!/bin/bash

# Deploy Apache Pulsar using Helm charts
# Usage: ./scripts/deploy-pulsar.sh [release-name] [namespace]

set -e

# Configuration
RELEASE_NAME=${1:-pulsar}
NAMESPACE=${2:-pulsar}
CHART_REPO="https://pulsar.apache.org/charts"
CHART_NAME="pulsar"
VALUES_FILE="helm/pulsar/values.yaml"

echo "🚀 Deploying Apache Pulsar with Helm..."
echo "Release: ${RELEASE_NAME}"
echo "Namespace: ${NAMESPACE}"
echo "Chart: ${CHART_NAME}"

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

# Add Pulsar Helm repository
echo "📋 Adding Pulsar Helm repository..."
helm repo add apache ${CHART_REPO}
helm repo update

# Create namespace if it doesn't exist
echo "📋 Ensuring namespace exists..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Check if values file exists
if [ ! -f "${VALUES_FILE}" ]; then
    echo "❌ Values file not found: ${VALUES_FILE}"
    exit 1
fi

echo "📝 Using Pulsar values from: ${VALUES_FILE}"

# Deploy or upgrade the Pulsar Helm chart
echo "🔨 Deploying Pulsar Helm chart..."
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo "📈 Upgrading existing Pulsar release..."
    helm upgrade ${RELEASE_NAME} apache/${CHART_NAME} \
        --install \
        --values ${VALUES_FILE} \
        --namespace ${NAMESPACE} 
        # --wait \
        # --timeout=10m
else
    echo "🆕 Installing new Pulsar release..."
    helm install ${RELEASE_NAME} apache/${CHART_NAME} \
        --values ${VALUES_FILE} \
        --namespace ${NAMESPACE} \
        --create-namespace 
        # --wait \
        # --timeout=10m
fi

echo "✅ Successfully deployed Apache Pulsar!"
echo ""
echo "📊 Deployment status:"
kubectl get pods -n ${NAMESPACE}
echo ""
echo "🌐 Services:"
kubectl get services -n ${NAMESPACE}
echo ""
echo "🔗 Access Pulsar:"
echo "  - Pulsar Admin: kubectl port-forward -n ${NAMESPACE} svc/${RELEASE_NAME}-pulsar-proxy 8080:8080"
echo "  - Pulsar Client: kubectl port-forward -n ${NAMESPACE} svc/${RELEASE_NAME}-pulsar-proxy 6650:6650"
echo "  - Pulsar Manager (Web UI): kubectl port-forward -n ${NAMESPACE} svc/${RELEASE_NAME}-pulsar-manager 9527:9527"
echo ""
echo "📚 Useful commands:"
echo "  - Check logs: kubectl logs -n ${NAMESPACE} -l app=pulsar"
echo "  - Scale broker: kubectl scale -n ${NAMESPACE} deployment ${RELEASE_NAME}-pulsar-broker --replicas=3"
echo "  - Access Pulsar shell: kubectl exec -n ${NAMESPACE} -it ${RELEASE_NAME}-pulsar-toolset-0 -- /pulsar/bin/pulsar-admin"
