#!/bin/bash

# Build and Push Docker Images to Azure Container Registry

set -e

# Load Azure configuration
if [ ! -f "azure-config/azure-config.json" ]; then
    echo "Error: azure-config.json not found. Run azure-setup.sh first."
    exit 1
fi

# Extract ACR details from config
ACR_NAME=$(grep -o '"name": "[^"]*"' azure-config/azure-config.json | grep -A1 containerRegistry | tail -1 | cut -d'"' -f4)
ACR_LOGIN_SERVER=$(grep -o '"loginServer": "[^"]*"' azure-config/azure-config.json | cut -d'"' -f4)

echo "================================================"
echo "Building and Pushing Swarm Agent Images"
echo "================================================"
echo "Registry: $ACR_LOGIN_SERVER"
echo ""

# Login to ACR
echo "Logging in to Azure Container Registry..."
az acr login --name $ACR_NAME

# Build and push Queen agent
echo "Building Queen Agent image..."
docker build -f azure-deploy/Dockerfile.queen -t $ACR_LOGIN_SERVER/swarm-queen:latest .
echo "Pushing Queen Agent image..."
docker push $ACR_LOGIN_SERVER/swarm-queen:latest

# Build and push Worker agents
AGENT_TYPES=("architect" "coder" "tester" "researcher" "analyst" "security" "optimizer")
PRIORITIES=(8 7 6 5 5 9 4)
MAX_INSTANCES=(2 3 2 2 2 1 1)

for i in "${!AGENT_TYPES[@]}"; do
    AGENT=${AGENT_TYPES[$i]}
    PRIORITY=${PRIORITIES[$i]}
    MAX_INST=${MAX_INSTANCES[$i]}
    
    echo ""
    echo "Building $AGENT Agent image..."
    docker build -f azure-deploy/Dockerfile.worker \
        --build-arg AGENT_TYPE=$AGENT \
        --build-arg AGENT_PRIORITY=$PRIORITY \
        --build-arg MAX_INSTANCES=$MAX_INST \
        -t $ACR_LOGIN_SERVER/swarm-$AGENT:latest .
    
    echo "Pushing $AGENT Agent image..."
    docker push $ACR_LOGIN_SERVER/swarm-$AGENT:latest
done

echo ""
echo "================================================"
echo "All Images Built and Pushed Successfully!"
echo "================================================"
echo ""
echo "Images available in registry:"
docker images | grep $ACR_LOGIN_SERVER

echo ""
echo "Next step: Deploy to Kubernetes"
echo "Run: kubectl apply -f azure-deploy/kubernetes/"