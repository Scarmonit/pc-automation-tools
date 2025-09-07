# 🚀 Flowise Agent Setup Guide

## ✅ Flowise is Running!

**Access Flowise at: http://localhost:3001**

## Quick Login
- **Username**: admin
- **Password**: flowise123

## Setting Up Your First Agent Flow

### Method 1: Import Pre-configured Agent (Recommended)

1. **Open Flowise**: http://localhost:3001
2. **Login** with credentials above
3. **Click "Chatflows"** in the sidebar
4. **Click "Add New"** → **"Load Chatflow"**
5. **Upload** the file: `C:\Users\scarm\llmstack\flowise_agent_flow.json`
6. **Save** the flow
7. **Test** using the chat button in the top-right

### Method 2: Create Agent Flow Manually

#### Step 1: Create New Chatflow
1. Click **"Chatflows"** → **"Add New"**
2. Name it: "AI Development Assistant"

#### Step 2: Add Chat Model
1. Drag **"Chat Models"** → **"ChatOpenAI"** to canvas
2. Configure:
   - Model Name: `gpt-3.5-turbo`
   - Temperature: `0.7`
   - Max Tokens: `2000`
   - For LocalAI:
     - Base URL: `http://host.docker.internal:8080/v1`
     - API Key: `sk-localai`
   - For OpenAI:
     - API Key: Your OpenAI key

#### Step 3: Add Agent
1. Drag **"Agents"** → **"OpenAI Function Agent"** to canvas
2. Connect the ChatOpenAI node to Agent's "Model" input

#### Step 4: Add Memory
1. Drag **"Memory"** → **"Buffer Memory"** to canvas
2. Configure:
   - Memory Key: `chat_history`
   - Return Messages: `true`
3. Connect to Agent's "Memory" input

#### Step 5: Add Tools
Drag and connect these tools to the Agent:

**A. Web Search Tool**
- **"Tools"** → **"Serper API"** or **"Google Custom Search"**
- For web searching capabilities

**B. Calculator Tool**
- **"Tools"** → **"Calculator"**
- For mathematical operations

**C. Code Execution Tool**
- **"Tools"** → **"Custom Tool"**
- Name: `code_executor`
- Description: `Execute Python code`

**D. API Request Tool**
- **"Tools"** → **"API Request"**
- For making HTTP requests

#### Step 6: Configure System Message
In the Agent node, set system message:
```
You are an AI Development Assistant with access to multiple tools.
You can:
- Search the web for information
- Execute code
- Perform calculations
- Make API requests
- Help with programming tasks

Be helpful, accurate, and provide working solutions.
```

#### Step 7: Save and Test
1. Click **"Save Chatflow"**
2. Click the **Chat icon** (top-right)
3. Test with: "Write a Python function to calculate fibonacci numbers"

## Pre-built Agent Templates

### 1. Code Assistant Agent
```json
{
  "name": "Code Assistant",
  "tools": ["code_executor", "web_search", "calculator"],
  "systemMessage": "Expert programmer helping with code"
}
```

### 2. Research Agent
```json
{
  "name": "Research Agent",
  "tools": ["web_search", "pdf_loader", "summarization"],
  "systemMessage": "Research assistant for gathering information"
}
```

### 3. API Integration Agent
```json
{
  "name": "API Agent",
  "tools": ["api_request", "json_parser", "webhook"],
  "systemMessage": "API integration specialist"
}
```

## Connecting to Your AI Stack

### Use with LocalAI
1. In ChatOpenAI node:
   - Base URL: `http://host.docker.internal:8080/v1`
   - API Key: `sk-localai`
   - Model: `gpt-3.5-turbo`

### Use with Ollama
1. Add **"Ollama"** node instead of ChatOpenAI
2. Configure:
   - Base URL: `http://host.docker.internal:11434`
   - Model: `llama3.1` or `deepseek-r1`

### Use with OpenHands
Create a Custom Tool that calls OpenHands API:
```javascript
const response = await fetch('http://host.docker.internal:3000/api/execute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({task: $input})
});
return await response.text();
```

## Advanced Features

### 1. Document Processing
Add these nodes for document handling:
- **Document Loaders** → PDF, Word, CSV
- **Text Splitters** → For chunking
- **Vector Stores** → For semantic search

### 2. Custom Functions
Create custom JavaScript functions:
```javascript
// Example: Data transformer
const data = JSON.parse($input);
const transformed = data.map(item => ({
  ...item,
  processed: true,
  timestamp: new Date().toISOString()
}));
return JSON.stringify(transformed);
```

### 3. Webhooks & APIs
- Add **Webhook** node for external triggers
- Use **API Endpoint** to expose your flow as API

### 4. Chains & Sequences
Connect multiple agents for complex workflows:
1. Research Agent → gathers information
2. Analysis Agent → processes data
3. Output Agent → formats results

## Testing Your Agent

### Test Prompts
Try these to test your agent:

1. **Code Generation**:
   "Create a Python REST API using FastAPI with CRUD operations for a todo list"

2. **Problem Solving**:
   "Debug this code: [paste code with error]"

3. **Research**:
   "Find the latest best practices for React performance optimization"

4. **Data Analysis**:
   "Analyze this CSV data and create visualizations: [paste data]"

## API Access

Your Flowise agents are accessible via API:

### Get API Key
1. Go to **"API Keys"** in Flowise
2. Click **"Add New API Key"**
3. Copy the generated key

### Make API Calls
```bash
curl -X POST http://localhost:3001/api/v1/prediction/<chatflow-id> \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"question": "Your prompt here"}'
```

### Python Example
```python
import requests

response = requests.post(
    "http://localhost:3001/api/v1/prediction/<chatflow-id>",
    headers={"Authorization": "Bearer <api-key>"},
    json={"question": "Write a hello world function"}
)
print(response.json())
```

## Integration with Unified Orchestrator

Add Flowise to your `unified_orchestrator.py`:
```python
# Flowise endpoint
flowise_url = "http://localhost:3001/api/v1/prediction/<chatflow-id>"
response = requests.post(flowise_url, json={"question": task})
```

## Troubleshooting

### Can't Connect to LocalAI
- Ensure LocalAI is running: `setup_localai.bat`
- Use `http://host.docker.internal:8080/v1` as base URL

### Agent Not Responding
- Check node connections (all must be green)
- Verify API keys are set correctly
- Check Docker logs: `docker logs flowise`

### Memory Not Working
- Ensure Buffer Memory is connected
- Set a unique Session ID if needed
- Clear chat history and retry

## Next Steps

1. **Open Flowise**: http://localhost:3001
2. **Import the agent flow** or create your own
3. **Configure LocalAI** or your preferred LLM
4. **Test the agent** with various prompts
5. **Customize** tools and behaviors
6. **Share** via API or embed in applications

---

**🎯 Flowise is ready at http://localhost:3001 - Start building visual AI agents now!**