#!/bin/bash
set -e

echo "🚀 Setting up Argo Workflows development environment..."

echo "📦 Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

echo "📦 Installing Argo CLI..."
curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.7.0/argo-linux-amd64.gz
gunzip argo-linux-amd64.gz
chmod +x argo-linux-amd64
sudo mv argo-linux-amd64 /usr/local/bin/argo

echo "🧹 Cleaning up any existing k3s-server container..."
docker rm -f k3s-server 2>/dev/null || true

echo "🔧 Starting k3s Kubernetes cluster..."
docker run -d --name k3s-server --privileged -p 6443:6443 rancher/k3s:latest server --disable=traefik

echo "⏳ Waiting for k3s to start..."
sleep 10

echo "🔧 Configuring kubectl..."
mkdir -p ~/.kube
docker exec k3s-server cat /etc/rancher/k3s/k3s.yaml | sed 's/127.0.0.1/172.17.0.2/g' > ~/.kube/config
CONTAINER_IP=$(docker inspect k3s-server | grep '"IPAddress"' | head -1 | cut -d'"' -f4)
docker exec k3s-server cat /etc/rancher/k3s/k3s.yaml | sed "s/127.0.0.1/$CONTAINER_IP/g" > ~/.kube/config
sed -i '/certificate-authority-data:/d' ~/.kube/config
sed -i '/server:/a\    insecure-skip-tls-verify: true' ~/.kube/config

echo "📦 Installing Argo Workflows..."
kubectl create namespace argo || true
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.7.0/install.yaml

echo "⏳ Waiting for Argo Workflows to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argo-server -n argo || echo "⚠️  Argo server may still be starting..."
kubectl wait --for=condition=available --timeout=300s deployment/workflow-controller -n argo || echo "⚠️  Workflow controller may still be starting..."

echo "🔐 Setting up RBAC for workflows..."
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default

echo "✅ Setup complete!"
