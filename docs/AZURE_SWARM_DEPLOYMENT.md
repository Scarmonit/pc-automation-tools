# Azure Swarm Intelligence Deployment Guide

## 🚀 Overview

This guide walks you through deploying your AI Swarm Intelligence system to Microsoft Azure, transforming your local swarm into a globally scalable, cloud-native multi-agent system.

## 📋 Prerequisites

1. **Azure Account**: Active Azure subscription ([Free trial available](https://azure.microsoft.com/free/))
2. **Azure CLI**: Installed locally ([Installation guide](https://docs.microsoft.com/cli/azure/install-azure-cli))
3. **Docker**: Installed for building container images
4. **kubectl**: For Kubernetes management
5. **API Keys**: Your existing Anthropic, OpenAI, and Perplexity keys

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Cloud                           │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     AKS      │  │  Cosmos DB   │  │ Service Bus  │ │
│  │   Cluster    │  │   (Memory)   │  │  (Messaging) │ │
│  │              │  │              │  │              │ │
│  │ ┌──────────┐ │  └──────────────┘  └──────────────┘ │
│  │ │  Queen   │ │                                      │
│  │ │  Agent   │ │  ┌──────────────┐  ┌──────────────┐ │
│  │ └──────────┘ │  │  Key Vault   │  │   Storage    │ │
│  │              │  │  (Secrets)   │  │   Account    │ │
│  │ ┌──────────┐ │  └──────────────┘  └──────────────┘ │
│  │ │ Workers  │ │                                      │
│  │ │ (7 types)│ │  ┌──────────────┐                   │
│  │ └──────────┘ │  │   Functions   │                   │
│  └──────────────┘  │   (Triggers)  │                   │
│                    └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## 📦 Created Resources

### Infrastructure Files
- `azure-deploy/` - Deployment configurations
  - `Dockerfile.queen` - Queen agent container
  - `Dockerfile.worker` - Worker agents template
  - `docker-compose.yml` - Local testing setup
  - `build-and-push.sh` - Container build script
  - `kubernetes/` - K8s manifests
    - `namespace.yaml` - Swarm namespace
    - `queen-deployment.yaml` - Queen agent deployment
    - `worker-deployments.yaml` - All worker agents
    - `hpa.yaml` - Auto-scaling configurations

### Configuration Files
- `azure-config/` - Azure setup scripts
  - `azure-setup.sh` - Resource creation script
  - `azure-config.json` - Generated configuration

### Serverless Functions
- `azure-functions/` - Function apps
  - `agent-trigger/` - HTTP trigger for tasks

## 🛠️ Deployment Steps

### Step 1: Set Up Azure Resources

```bash
# Make scripts executable
chmod +x azure-config/azure-setup.sh
chmod +x azure-deploy/build-and-push.sh

# Run Azure setup
cd azure-config
./azure-setup.sh
```

This creates:
- Resource Group
- Container Registry (ACR)
- Kubernetes Service (AKS)
- Cosmos DB (distributed memory)
- Service Bus (messaging)
- Key Vault (secrets)
- Storage Account

### Step 2: Add Your API Keys to Key Vault

```bash
# Use the Key Vault name from azure-config.json
KV_NAME=$(grep -o '"name": "[^"]*"' azure-config.json | grep -A1 keyVault | tail -1 | cut -d'"' -f4)

# Add your API keys
az keyvault secret set --vault-name $KV_NAME --name anthropic-api-key --value "your_anthropic_api_key_here"
az keyvault secret set --vault-name $KV_NAME --name openai-api-key --value "sk-proj-YOUR-KEY"
az keyvault secret set --vault-name $KV_NAME --name perplexity-api-key --value "your_perplexity_api_key_here"
```

### Step 3: Build and Push Docker Images

```bash
# Update ACR login server in Kubernetes manifests
ACR_SERVER=$(grep -o '"loginServer": "[^"]*"' azure-config/azure-config.json | cut -d'"' -f4)
find azure-deploy/kubernetes -name "*.yaml" -exec sed -i "s/<ACR_LOGIN_SERVER>/$ACR_SERVER/g" {} \;

# Build and push images
cd ..  # Return to root directory
./azure-deploy/build-and-push.sh
```

### Step 4: Deploy to Kubernetes

```bash
# Get AKS credentials
RESOURCE_GROUP=$(grep -o '"resourceGroup": "[^"]*"' azure-config/azure-config.json | cut -d'"' -f4)
AKS_CLUSTER=$(grep -o '"aksCluster": "[^"]*"' azure-config/azure-config.json | cut -d'"' -f4)
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER

# Create secrets in Kubernetes
kubectl create namespace swarm-intelligence
kubectl create secret generic swarm-secrets \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=perplexity-api-key=$PERPLEXITY_API_KEY \
  --from-literal=cosmos-endpoint=$COSMOS_ENDPOINT \
  --from-literal=cosmos-key=$COSMOS_KEY \
  --from-literal=servicebus-connection=$SERVICE_BUS_CONNECTION \
  -n swarm-intelligence

# Deploy the swarm
kubectl apply -f azure-deploy/kubernetes/
```

### Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods -n swarm-intelligence

# Check services
kubectl get svc -n swarm-intelligence

# View Queen agent logs
kubectl logs -l app=swarm-queen -n swarm-intelligence

# Check autoscaling status
kubectl get hpa -n swarm-intelligence
```

## 🧪 Local Testing

Before deploying to Azure, test locally with Docker Compose:

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export PERPLEXITY_API_KEY="your-key"

# Start local swarm
cd azure-deploy
docker-compose up -d

# View logs
docker-compose logs -f swarm-queen

# Stop swarm
docker-compose down
```

## 📊 Monitoring & Management

### Azure Portal Dashboard
1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to your resource group: `swarm-intelligence-rg`
3. Monitor:
   - AKS cluster health
   - Cosmos DB metrics
   - Service Bus message flow
   - Function app invocations

### Kubernetes Dashboard
```bash
# Port forward to Queen service
kubectl port-forward svc/swarm-queen-service 8080:80 -n swarm-intelligence

# Access at http://localhost:8080
```

### Scaling Operations
```bash
# Manual scaling
kubectl scale deployment swarm-coder --replicas=5 -n swarm-intelligence

# Update autoscaling
kubectl edit hpa swarm-coder-hpa -n swarm-intelligence
```

## 💰 Cost Optimization

### Estimated Monthly Costs
- AKS Cluster (3 B2s nodes): ~$90
- Cosmos DB (400 RU/s): ~$24
- Service Bus (Standard): ~$10
- Storage Account: ~$5
- Functions (Consumption plan): ~$0-5
- **Total**: ~$130-135/month

### Cost Saving Tips
1. Use spot instances for worker agents
2. Scale down during off-hours
3. Use Azure Free Tier services where applicable
4. Enable auto-shutdown for dev/test environments

## 🔒 Security Best Practices

1. **Secrets Management**: All API keys stored in Key Vault
2. **Network Isolation**: Use VNet integration
3. **RBAC**: Configure role-based access control
4. **Monitoring**: Enable Azure Security Center
5. **Updates**: Regular security patches

## 🔧 Troubleshooting

### Common Issues

#### Pods not starting
```bash
kubectl describe pod <pod-name> -n swarm-intelligence
kubectl logs <pod-name> -n swarm-intelligence
```

#### Connection issues
```bash
# Test Service Bus connection
az servicebus namespace show --resource-group $RESOURCE_GROUP --name $SERVICE_BUS_NAMESPACE

# Test Cosmos DB connection
az cosmosdb show --resource-group $RESOURCE_GROUP --name $COSMOS_ACCOUNT
```

#### Image pull errors
```bash
# Re-authenticate with ACR
az acr login --name $ACR_NAME

# Check image availability
az acr repository list --name $ACR_NAME
```

## 🚀 Advanced Features

### Multi-Region Deployment
1. Create AKS clusters in multiple regions
2. Configure Cosmos DB global replication
3. Use Azure Traffic Manager for routing

### CI/CD Pipeline
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Azure
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: |
          ./azure-deploy/build-and-push.sh
          kubectl apply -f azure-deploy/kubernetes/
```

## 📝 Next Steps

1. **Configure Monitoring**: Set up Application Insights
2. **Add Custom Domain**: Configure ingress with SSL
3. **Implement Backup**: Automated Cosmos DB backups
4. **Set up Alerts**: Configure alerts for critical metrics
5. **Performance Tuning**: Optimize based on usage patterns

## 🆘 Support

- [Azure Documentation](https://docs.microsoft.com/azure/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Azure Support](https://azure.microsoft.com/support/)

---

Your Swarm Intelligence is now ready for cloud deployment! The system will automatically scale based on demand, providing enterprise-grade reliability and global reach for your AI agents.