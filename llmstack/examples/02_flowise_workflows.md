# Flowise Visual Workflow Guide

## Access Flowise
1. Open browser: http://localhost:3001
2. Click "Chatflows" → "Add New"

## Example Workflows

### Workflow 1: Simple Chatbot with Ollama
1. **Add Components** (drag from left panel):
   - Chat Models → ChatOllama
   - Chains → Conversation Chain
   - Memory → Buffer Memory

2. **Configure ChatOllama**:
   - Base URL: `http://host.docker.internal:11434`
   - Model Name: `deepseek-r1:8b`
   - Temperature: 0.7

3. **Connect Components**:
   - Drag from ChatOllama output to Conversation Chain "Model" input
   - Drag from Buffer Memory to Conversation Chain "Memory" input

4. **Save & Test**:
   - Click "Save Chatflow"
   - Click chat icon to test

### Workflow 2: Document Q&A System
1. **Add Components**:
   - Document Loaders → PDF File
   - Text Splitters → Recursive Character Text Splitter
   - Vector Stores → In-Memory Vector Store
   - Embeddings → Ollama Embeddings
   - Chains → Retrieval QA Chain
   - Chat Models → ChatOllama

2. **Configuration**:
   - PDF File: Upload your document
   - Text Splitter: Chunk Size: 1000, Overlap: 200
   - Ollama Embeddings: Model: `llama3.1:8b`
   - ChatOllama: Model: `deepseek-r1:8b`

3. **Connections**:
   - PDF → Text Splitter → Vector Store (Document input)
   - Embeddings → Vector Store (Embedding input)
   - Vector Store → Retrieval QA (Vector Store input)
   - ChatOllama → Retrieval QA (Model input)

### Workflow 3: Code Assistant
1. **Components**:
   - Tools → Custom Tool (for code execution)
   - Agents → Tool Agent
   - Chat Models → ChatOllama (use dolphin-mistral)
   - Memory → Buffer Window Memory

2. **Custom Tool Code**:
```javascript
const { exec } = require('child_process');

const run = async (input) => {
    return new Promise((resolve) => {
        exec(input, (error, stdout, stderr) => {
            if (error) {
                resolve(`Error: ${stderr}`);
            } else {
                resolve(stdout);
            }
        });
    });
};

module.exports = { run };
```

3. **Test Prompts**:
   - "Write and test a Python fibonacci function"
   - "Create a bash script to monitor CPU usage"
   - "Debug this code: [paste code]"

## API Integration
Once saved, each workflow gets an API endpoint:

```python
import requests

# Use your workflow API
response = requests.post(
    "http://localhost:3001/api/v1/prediction/<chatflow-id>",
    json={"question": "What is machine learning?"}
)
print(response.json())
```

## Tips
- Use Buffer Memory for conversations
- Window Memory (k=10) for limited context
- Add Tools for web search, calculations, code execution
- Chain multiple models for complex tasks
- Export/Import workflows as JSON