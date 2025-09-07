# 🎯 Flowise Quick Start - Agent Flow Setup

## ✅ Flowise is Running!

**🌐 Access Now: http://localhost:3001**

## 🔐 Login Credentials
- **Username**: `admin`
- **Password**: `flowise123`

## 🚀 5-Minute Agent Setup

### Step 1: Open Flowise
Go to: **http://localhost:3001**

### Step 2: Login
Use the credentials above

### Step 3: Import Agent Flow
1. Click **"Chatflows"** in sidebar
2. Click **"Add New"** button
3. Click **"Load Chatflow"** (top menu)
4. Select file: `C:\Users\scarm\llmstack\flowise_agent_flow.json`
5. Click **"Save"**

### Step 4: Configure LLM Provider

#### Option A: Use LocalAI (Free, Local)
In the ChatOpenAI node:
- Base URL: `http://host.docker.internal:8080/v1`
- API Key: `sk-localai`
- Model: `gpt-3.5-turbo`

#### Option B: Use OpenAI
In the ChatOpenAI node:
- Leave Base URL empty
- API Key: Your OpenAI API key
- Model: `gpt-4` or `gpt-3.5-turbo`

### Step 5: Test Your Agent
1. Click the **Chat button** (💬) in top-right corner
2. Try these prompts:
   - "Write a Python function to sort a list"
   - "Explain how REST APIs work"
   - "Debug this code: [paste any code]"
   - "Create a React component for a todo list"

## 🎨 Visual Agent Builder

### Creating Custom Flows

**Basic Conversational Agent:**
```
[LLM] → [Memory] → [Agent] → [Output]
```

**Advanced Tool-Using Agent:**
```
[LLM] → [Agent] ← [Tools: Web Search, Code Executor, Calculator]
           ↓
        [Memory]
```

**Multi-Stage Processing:**
```
[Input] → [Agent 1: Research] → [Agent 2: Analyze] → [Agent 3: Generate] → [Output]
```

## 🛠️ Available Tools

### Built-in Tools
- **🔍 Web Search** - Search Google/Serper
- **🧮 Calculator** - Math operations
- **📝 Custom Tool** - Create any function
- **🌐 API Request** - Call external APIs
- **📊 Code Executor** - Run Python/JS code

### Document Processing
- **📄 PDF Loader** - Extract from PDFs
- **📑 Text Splitter** - Chunk documents
- **🗂️ Vector Store** - Semantic search

### Integrations
- **OpenAI** - GPT models
- **Anthropic** - Claude models
- **LocalAI** - Local models
- **Ollama** - Local LLMs
- **HuggingFace** - Open models

## 💡 Example Agent Flows

### 1. Code Assistant
**Purpose**: Help with programming
```javascript
Tools: [Code Executor, Web Search, Documentation Loader]
System: "Expert programmer assistant"
```

### 2. Research Agent
**Purpose**: Gather and analyze information
```javascript
Tools: [Web Search, PDF Reader, Summarizer]
System: "Research analyst"
```

### 3. API Builder
**Purpose**: Create and test APIs
```javascript
Tools: [Code Executor, API Tester, Schema Validator]
System: "API development specialist"
```

## 🔗 API Access

### Get Your API Key
1. Go to **"API Keys"** in Flowise
2. Click **"Add New"**
3. Copy the key

### Call Your Agent via API

**Bash/cURL:**
```bash
curl -X POST http://localhost:3001/api/v1/prediction/<chatflow-id> \
  -H "Content-Type: application/json" \
  -d '{"question": "Your prompt here"}'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:3001/api/v1/prediction/<chatflow-id>",
    json={"question": "Write a hello world function"}
)
print(response.json())
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:3001/api/v1/prediction/<id>', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: 'Your prompt'})
});
const result = await response.json();
```

## 🎯 Your AI Stack Status

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Flowise** | http://localhost:3001 | ✅ Running | Visual Agent Builder |
| **OpenHands** | http://localhost:3000 | ✅ Running | AI Coding Assistant |
| **LocalAI** | http://localhost:8080 | ⚠️ Start with `setup_localai.bat` | Local LLM Server |
| **Orchestrator** | http://localhost:5000 | ⚠️ Run `python unified_orchestrator.py` | Unified Control |

## 📚 Resources

### Files Created
- `flowise_agent_flow.json` - Pre-built agent template
- `FLOWISE_AGENT_SETUP.md` - Detailed setup guide
- `setup_flowise.bat` - Flowise installer
- `test_flowise.py` - Connection tester

### Docker Commands
```bash
# View logs
docker logs -f flowise

# Restart
docker restart flowise

# Stop
docker stop flowise

# Remove
docker rm flowise
```

## 🏁 Next Steps

1. **Login to Flowise**: http://localhost:3001
2. **Import the agent flow** (flowise_agent_flow.json)
3. **Configure your LLM** (LocalAI or OpenAI)
4. **Test with sample prompts**
5. **Customize** for your needs
6. **Share via API** or embed

---

## 🎉 Ready to Build!

**Flowise is running at http://localhost:3001**

You now have:
- ✅ Visual agent builder (Flowise)
- ✅ AI coding assistant (OpenHands)
- ✅ Multiple AI frameworks integrated
- ✅ Ready-to-use agent templates

**Start building intelligent agents visually - no code required!**