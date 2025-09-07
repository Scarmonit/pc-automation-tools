# LLMStack Open Source Deployment - Windows Edition

## 🚀 Quick Start

Open PowerShell as Administrator and run:

```powershell
cd C:\Users\scarm\llmstack
PowerShell -ExecutionPolicy Bypass -File .\DEPLOY_ALL.ps1
```

Select option 1 for full installation.

## 📋 System Requirements

Your system status:
- ✅ CPU: 32 cores (Excellent!)
- ✅ RAM: 64GB (Perfect for large models)
- ✅ Disk: 787GB free (Plenty of space)
- ✅ Docker: Installed
- ✅ Python: 3.12.10

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
├─────────────────────────────────────────────────────────┤
│  LLMStack UI │ Flowise │ OpenHands │ Grafana Dashboard  │
├─────────────────────────────────────────────────────────┤
│                    AI Agent Layer                        │
├─────────────────────────────────────────────────────────┤
│   AutoGen │ Aider │ Continue │ Custom Orchestrator      │
├─────────────────────────────────────────────────────────┤
│                  Local Model Servers                     │
├─────────────────────────────────────────────────────────┤
│     Ollama │ LM Studio │ vLLM (GPU) │ Jan API          │
├─────────────────────────────────────────────────────────┤
│                    Infrastructure                        │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL │ Redis │ ChromaDB │ Prometheus │ Docker    │
└─────────────────────────────────────────────────────────┘
```

## 📦 Included Components

### Model Servers
- **Ollama**: Primary local model server with multiple models
- **LM Studio**: GUI-based model management
- **vLLM**: High-performance GPU inference (if NVIDIA GPU available)

### Pre-installed Models
- `llama3.2:3b` - Fast general purpose (2GB)
- `mistral:7b-instruct` - Excellent reasoning (4GB)
- `codellama:7b` - Code generation (4GB)
- `qwen2.5:3b` - Multilingual support (2GB)

### AI Agents
- **AutoGen**: Multi-agent conversations
- **Flowise**: Visual workflow builder
- **OpenHands**: Autonomous coding agent
- **Aider**: CLI coding assistant
- **Continue**: VS Code AI extension

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards

## 🌐 Access Points

After deployment, access your services at:

| Service | URL | Credentials |
|---------|-----|-------------|
| LLMStack | http://localhost:3000 | Create on first login |
| Flowise | http://localhost:3001 | None required |
| OpenHands | http://localhost:3002 | None required |
| Grafana | http://localhost:3003 | admin/admin |
| Prometheus | http://localhost:9090 | None required |

## 🔌 API Endpoints

Use these endpoints in your applications:

| Service | Endpoint | API Key |
|---------|----------|---------|
| Ollama | http://localhost:11434/v1 | `ollama` |
| LM Studio | http://localhost:1234/v1 | `lm-studio` |
| Jan | http://localhost:1337/v1 | `jan` |

## 🛠️ Common Commands

### Model Management
```powershell
# List installed models
ollama list

# Pull a new model
ollama pull llama3.2:latest

# Remove a model
ollama rm model_name
```

### Docker Management
```powershell
# View running containers
docker ps

# View logs
docker logs flowise
docker logs openhands

# Restart a service
docker restart flowise

# Stop all services
docker compose down

# Start all services
docker compose up -d
```

### Testing Inference
```powershell
# Test Ollama
curl -X POST http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"Hello"}]}'
```

## 🔧 Troubleshooting

### Issue: Service won't start
```powershell
# Check logs
docker logs container_name

# Check port conflicts
netstat -an | findstr :3000
```

### Issue: Out of memory
```powershell
# Clean Docker
docker system prune -a

# Remove unused models
ollama rm unused_model
```

### Issue: Slow inference
- Reduce context size in model settings
- Use smaller models (3B instead of 7B)
- Enable GPU acceleration if available

## 📊 Performance Tips

1. **GPU Acceleration**: If you have an NVIDIA GPU, models will automatically use it
2. **Memory Management**: Close unused applications to free RAM for models
3. **Model Selection**: Start with smaller models (3B) and upgrade as needed
4. **Batch Processing**: Use the orchestrator for efficient multi-model workflows

## 🔐 Security Notes

- All data stays on your local machine
- No external API calls (except model downloads)
- Secure random keys generated during setup
- Services bound to localhost only

## 📈 Monitoring Your Deployment

1. Open Grafana at http://localhost:3003
2. Login with admin/admin
3. Import the LLMStack dashboard
4. Monitor:
   - Model inference latency
   - Memory usage
   - Request throughput
   - Container health

## 🚀 Next Steps

1. **Create Your First App**:
   - Open LLMStack at http://localhost:3000
   - Click "Create New App"
   - Choose a template (RAG, Chatbot, etc.)
   - Connect to Ollama models

2. **Build a Workflow**:
   - Open Flowise at http://localhost:3001
   - Drag and drop components
   - Connect to local models
   - Test your workflow

3. **Code with AI**:
   - Use `aider` in terminal for coding help
   - Open VS Code with Continue extension
   - Let OpenHands build entire features

## 💰 Cost Breakdown

| Component | Cost | Note |
|-----------|------|------|
| Models | $0 | All open source |
| API Calls | $0 | Everything local |
| Infrastructure | $0 | Your hardware |
| **Total** | **$0** | **100% Free** |

## 📞 Support

- Check logs: `docker logs container_name`
- Validate deployment: Run script #6 from DEPLOY_ALL.ps1
- GitHub Issues: Report to respective project repositories

## 🎉 Congratulations!

You now have a complete, production-ready AI agent stack running locally with:
- Zero API costs
- Complete data privacy
- Multiple AI models
- Professional monitoring
- Scalable architecture

Happy building! 🚀