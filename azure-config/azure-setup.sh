#!/bin/bash

# Azure Swarm Intelligence Setup Script
# Creates all necessary Azure resources for the swarm deployment

set -e

# Configuration
RESOURCE_GROUP="swarm-intelligence-rg"
LOCATION="eastus"
ACR_NAME="swarmacr$(date +%s)"
AKS_CLUSTER="swarm-aks-cluster"
COSMOS_ACCOUNT="swarm-cosmos-$(date +%s)"
COSMOS_DATABASE="swarm-memory"
SERVICE_BUS_NAMESPACE="swarm-bus-$(date +%s)"
KEY_VAULT_NAME="swarm-kv-$(date +%s)"
STORAGE_ACCOUNT="swarmstore$(date +%s)"

echo "================================================"
echo "Azure Swarm Intelligence Infrastructure Setup"
echo "================================================"
echo ""

# Check if logged in to Azure
echo "Checking Azure login status..."
if ! az account show &>/dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using subscription: $SUBSCRIPTION_ID"
echo ""

# Create Resource Group
echo "Creating Resource Group: $RESOURCE_GROUP"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Create Azure Container Registry
echo "Creating Container Registry: $ACR_NAME"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Standard \
    --admin-enabled true

# Create Azure Kubernetes Service
echo "Creating AKS Cluster: $AKS_CLUSTER"
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER \
    --node-count 3 \
    --node-vm-size Standard_B2s \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 10 \
    --generate-ssh-keys \
    --attach-acr $ACR_NAME

# Create Cosmos DB Account
echo "Creating Cosmos DB Account: $COSMOS_ACCOUNT"
az cosmosdb create \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --kind GlobalDocumentDB \
    --default-consistency-level Session \
    --locations regionName=$LOCATION failoverPriority=0 isZoneRedundant=False

# Create Cosmos DB Database
echo "Creating Cosmos DB Database: $COSMOS_DATABASE"
az cosmosdb sql database create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --name $COSMOS_DATABASE

# Create Cosmos DB Container for swarm memory
echo "Creating Cosmos DB Container: swarm-memory"
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --database-name $COSMOS_DATABASE \
    --resource-group $RESOURCE_GROUP \
    --name swarm-memory \
    --partition-key-path /namespace \
    --throughput 400

# Create Service Bus Namespace
echo "Creating Service Bus Namespace: $SERVICE_BUS_NAMESPACE"
az servicebus namespace create \
    --resource-group $RESOURCE_GROUP \
    --name $SERVICE_BUS_NAMESPACE \
    --location $LOCATION \
    --sku Standard

# Create Service Bus Queues
echo "Creating Service Bus Queues..."
for queue in queen-tasks worker-tasks agent-collaboration memory-sync; do
    az servicebus queue create \
        --resource-group $RESOURCE_GROUP \
        --namespace-name $SERVICE_BUS_NAMESPACE \
        --name $queue
done

# Create Azure Key Vault
echo "Creating Key Vault: $KEY_VAULT_NAME"
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Create Storage Account
echo "Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

# Create Storage Containers
echo "Creating Storage Containers..."
STORAGE_KEY=$(az storage account keys list \
    --resource-group $RESOURCE_GROUP \
    --account-name $STORAGE_ACCOUNT \
    --query '[0].value' -o tsv)

az storage container create \
    --name agent-outputs \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

az storage container create \
    --name swarm-backups \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY

# Get connection strings and keys
echo ""
echo "Retrieving connection strings..."
COSMOS_KEY=$(az cosmosdb keys list \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query primaryMasterKey -o tsv)

COSMOS_ENDPOINT=$(az cosmosdb show \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query documentEndpoint -o tsv)

SERVICE_BUS_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --resource-group $RESOURCE_GROUP \
    --namespace-name $SERVICE_BUS_NAMESPACE \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString -o tsv)

ACR_LOGIN_SERVER=$(az acr show \
    --name $ACR_NAME \
    --query loginServer -o tsv)

# Store secrets in Key Vault
echo "Storing secrets in Key Vault..."
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "cosmos-key" \
    --value "$COSMOS_KEY"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "cosmos-endpoint" \
    --value "$COSMOS_ENDPOINT"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "servicebus-connection" \
    --value "$SERVICE_BUS_CONNECTION"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "storage-key" \
    --value "$STORAGE_KEY"

# Create output file with configuration
cat > azure-config.json <<EOF
{
  "subscriptionId": "$SUBSCRIPTION_ID",
  "resourceGroup": "$RESOURCE_GROUP",
  "location": "$LOCATION",
  "containerRegistry": {
    "name": "$ACR_NAME",
    "loginServer": "$ACR_LOGIN_SERVER"
  },
  "aksCluster": "$AKS_CLUSTER",
  "cosmosDb": {
    "account": "$COSMOS_ACCOUNT",
    "database": "$COSMOS_DATABASE",
    "endpoint": "$COSMOS_ENDPOINT"
  },
  "serviceBus": {
    "namespace": "$SERVICE_BUS_NAMESPACE"
  },
  "keyVault": {
    "name": "$KEY_VAULT_NAME",
    "url": "https://$KEY_VAULT_NAME.vault.azure.net/"
  },
  "storageAccount": {
    "name": "$STORAGE_ACCOUNT"
  }
}
EOF

echo ""
echo "================================================"
echo "Azure Setup Complete!"
echo "================================================"
echo ""
echo "Configuration saved to: azure-config.json"
echo ""
echo "Next steps:"
echo "1. Add your API keys to Key Vault:"
echo "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name anthropic-api-key --value YOUR_KEY"
echo "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name openai-api-key --value YOUR_KEY"
echo "   az keyvault secret set --vault-name $KEY_VAULT_NAME --name perplexity-api-key --value YOUR_KEY"
echo ""
echo "2. Get AKS credentials:"
echo "   az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER"
echo ""
echo "3. Build and push Docker images:"
echo "   ./build-and-push.sh"
echo ""
echo "4. Deploy to Kubernetes:"
echo "   kubectl apply -f kubernetes/"