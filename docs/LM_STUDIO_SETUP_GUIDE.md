# 🖥️ LM Studio Setup Guide

LM Studio is a user-friendly desktop application for running local AI models with a beautiful interface. This guide shows you how to set up LM Studio for seamless local AI model management and integration with your automation tools.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install LM Studio (manual download required)
bash scripts/install_lm_studio.sh

# Configure with automation tools
python3 scripts/configure_providers.py --lmstudio
```

### Manual Installation

#### Windows
1. Download LM Studio from [lmstudio.ai](https://lmstudio.ai)
2. Run the installer (`LM-Studio-Setup.exe`)
3. Follow installation wizard
4. Launch LM Studio

#### macOS
1. Download LM Studio for macOS
2. Open the `.dmg` file
3. Drag LM Studio to Applications
4. Launch from Applications folder

#### Linux
```bash
# Download AppImage
wget https://releases.lmstudio.ai/linux/x86/0.2.22/LM_Studio-0.2.22.AppImage

# Make executable
chmod +x LM_Studio-0.2.22.AppImage

# Run LM Studio
./LM_Studio-0.2.22.AppImage
```

## 📋 Prerequisites

- **8GB+ RAM** (16GB recommended for larger models)
- **20GB+ Storage** for models and application
- **Modern CPU** (Apple Silicon, Intel, or AMD)
- **Optional GPU** (NVIDIA with CUDA support)
- **Internet connection** for model downloads

## 🔧 Configuration

### 1. Initial Setup

When you first launch LM Studio:

1. **Welcome Screen**: Complete the setup wizard
2. **Model Discovery**: Browse and download models
3. **Performance Settings**: Configure GPU/CPU usage
4. **Server Settings**: Enable local server for API access

### 2. Model Management

#### Downloading Models

1. **Browse Models**: Use the "Discover" tab to find models
2. **Search**: Look for specific models (llama, mistral, codellama)
3. **Download**: Click download button for desired models
4. **Monitor Progress**: Watch download progress in bottom panel

**Recommended Models for AI Automation:**
```
Essential Models:
- Llama-3.2-3B-Instruct-Q4_K_M.gguf (general purpose)
- CodeLlama-7B-Instruct-Q4_K_M.gguf (coding)
- Mistral-7B-Instruct-v0.2-Q4_K_M.gguf (balanced)

Performance Models:
- Llama-3.2-1B-Instruct-Q4_K_M.gguf (fast responses)
- TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf (ultra-fast)

Quality Models:
- Llama-3.1-8B-Instruct-Q4_K_M.gguf (high quality)
- WizardCoder-15B-V1.0-Q4_K_M.gguf (advanced coding)
```

#### Model Organization

Create folders in LM Studio:
- **Development**: Coding and technical models
- **General**: General purpose conversation models
- **Specialized**: Domain-specific models
- **Fast**: Lightweight models for quick responses

### 3. Server Configuration

Enable LM Studio's local server for API integration:

1. **Server Tab**: Click on "Local Server" tab
2. **Load Model**: Select a model to serve
3. **Start Server**: Click "Start Server"
4. **Configure Port**: Default is 1234, change if needed

#### Server Settings
```json
{
  "server": {
    "port": 1234,
    "cors": true,
    "verbose_logging": false,
    "max_parallel_requests": 4
  },
  "model": {
    "context_length": 4096,
    "gpu_layers": -1,
    "cpu_threads": 0,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1
  }
}
```

### 4. Advanced Configuration

#### GPU Acceleration
```json
{
  "gpu": {
    "enabled": true,
    "layers": -1,
    "memory_usage": 0.8,
    "vulkan": false
  }
}
```

#### Performance Tuning
```json
{
  "performance": {
    "batch_size": 512,
    "context_length": 4096,
    "rope_freq_base": 10000,
    "rope_freq_scale": 1.0,
    "cache_type": "f16"
  }
}
```

## 💻 Using LM Studio

### Chat Interface

#### 1. Basic Chat
1. **Load Model**: Select and load a model
2. **Start Conversation**: Type your message
3. **Adjust Settings**: Modify temperature, max tokens, etc.
4. **System Prompt**: Set custom system instructions

#### 2. System Prompts for AI Tools

**Developer Assistant:**
```
You are an expert software developer specializing in AI automation tools. 
You have deep knowledge of Python, Docker, AutoGen, Flowise, OpenHands, and other AI frameworks.
Provide practical, working code solutions with proper error handling and documentation.
Always consider integration with the existing AI automation infrastructure.
```

**DevOps Engineer:**
```
You are a DevOps engineer expert in containerization, monitoring, and deployment.
You understand Docker, Prometheus, Grafana, and CI/CD pipelines.
Provide secure, scalable solutions with proper monitoring and logging.
Focus on reliability and operational excellence.
```

**Documentation Writer:**
```
You are a technical writer specializing in AI tools documentation.
Create clear, comprehensive guides with emoji headers, troubleshooting sections, and practical examples.
Follow the repository's documentation standards and include code snippets.
```

#### 3. Model Comparison

Use LM Studio's split view to compare different models:

1. **Split Chat**: Enable split view in settings
2. **Load Two Models**: Load different models in each pane
3. **Same Prompt**: Send identical prompts to both
4. **Compare Responses**: Evaluate quality and performance

### Playground Features

#### 1. Template System
Create reusable templates for common tasks:

```json
{
  "templates": {
    "code_review": {
      "system": "You are a senior software engineer conducting code reviews.",
      "prompt": "Review this code for bugs, security issues, and improvements:\n\n{code}",
      "temperature": 0.3
    },
    "documentation": {
      "system": "You are a technical writer creating clear documentation.",
      "prompt": "Create comprehensive documentation for:\n\n{topic}",
      "temperature": 0.5
    },
    "debugging": {
      "system": "You are a debugging expert helping solve technical issues.",
      "prompt": "Help debug this issue:\n\n{problem}",
      "temperature": 0.2
    }
  }
}
```

#### 2. Batch Processing
Process multiple prompts with the same model:

1. **Prepare Prompts**: Create list of prompts
2. **Configure Model**: Set consistent parameters
3. **Run Batch**: Process all prompts sequentially
4. **Export Results**: Save responses for analysis

## 🔄 Integration with Repository

### API Integration

LM Studio provides an OpenAI-compatible API:

```python
# lm_studio_integration.py
import openai
import requests
from typing import Dict, Any, List, Optional

class LMStudioAPI:
    """LM Studio API client for automation tools integration"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key="lm-studio"  # LM Studio doesn't require real API key
        )
    
    def chat_completion(self, messages: List[Dict], model: str = "local-model",
                       temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Send chat completion request"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LM Studio API error: {e}")
    
    def stream_chat(self, messages: List[Dict], model: str = "local-model"):
        """Stream chat completion"""
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"LM Studio stream error: {e}")
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/models")
            models = response.json()
            return [model["id"] for model in models.get("data", [])]
        except Exception as e:
            raise Exception(f"Failed to list models: {e}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get LM Studio server status"""
        try:
            response = requests.get(f"{self.base_url}/models")
            return {
                "status": "running" if response.status_code == 200 else "error",
                "models_available": len(response.json().get("data", [])),
                "endpoint": self.base_url
            }
        except Exception:
            return {"status": "not_running", "endpoint": self.base_url}

# Integration with repository patterns
class LMStudioAgent:
    """LM Studio agent wrapper for unified orchestrator"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.lm_studio = LMStudioAPI()
        self.current_model = None
        
    def initialize(self):
        """Initialize LM Studio connection"""
        try:
            status = self.lm_studio.get_server_status()
            if status["status"] == "running":
                models = self.lm_studio.list_models()
                if models:
                    self.current_model = models[0]
                    logger.info(f"LM Studio initialized with model: {self.current_model}")
                else:
                    logger.warning("LM Studio running but no models loaded")
            else:
                logger.error("LM Studio server not running")
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio: {e}")
    
    def chat(self, message: str, context: str = None) -> str:
        """Chat with LM Studio model"""
        if not self.current_model:
            return "LM Studio not initialized or no model loaded"
        
        messages = []
        
        # Add system context for AI tools
        system_message = """You are an AI assistant specialized in PC automation tools and AI frameworks.
        You understand AutoGen, Flowise, OpenHands, Aider, MemGPT, CAMEL-AI, and other AI tools.
        Provide practical, working solutions with proper integration patterns."""
        
        if context:
            system_message += f"\n\nAdditional context: {context}"
        
        messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.lm_studio.chat_completion(messages, model=self.current_model)
            return response
        except Exception as e:
            logger.error(f"LM Studio chat error: {e}")
            return f"Error: {e}"
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code using LM Studio"""
        prompt = f"Generate {language} code for: {description}\n\nProvide working code with proper error handling and documentation."
        
        messages = [
            {
                "role": "system", 
                "content": f"You are an expert {language} developer. Generate clean, working code with explanations."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self.lm_studio.chat_completion(messages, model=self.current_model, temperature=0.3)
        except Exception as e:
            return f"Code generation error: {e}"

# Example usage
def demo_lm_studio_integration():
    """Demonstrate LM Studio integration"""
    
    # Initialize LM Studio API
    lm_studio = LMStudioAPI()
    
    # Check server status
    status = lm_studio.get_server_status()
    print(f"LM Studio Status: {status}")
    
    if status["status"] == "running":
        # List available models
        models = lm_studio.list_models()
        print(f"Available models: {models}")
        
        # Chat example
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain Docker containers in simple terms"}
        ]
        
        response = lm_studio.chat_completion(messages)
        print(f"Response: {response}")
        
        # Streaming example
        print("Streaming response:")
        for chunk in lm_studio.stream_chat(messages):
            print(chunk, end="", flush=True)
        print()

if __name__ == "__main__":
    demo_lm_studio_integration()
```

### Workflow Integration

```python
# lm_studio_workflows.py
class LMStudioWorkflowManager:
    """Manage complex workflows using LM Studio"""
    
    def __init__(self):
        self.lm_studio = LMStudioAPI()
        self.workflow_templates = self.load_workflow_templates()
    
    def load_workflow_templates(self) -> Dict[str, Dict]:
        """Load predefined workflow templates"""
        return {
            "code_review": {
                "steps": [
                    {"role": "analyzer", "prompt": "Analyze this code for structure and purpose: {code}"},
                    {"role": "security", "prompt": "Review for security vulnerabilities: {code}"},
                    {"role": "performance", "prompt": "Suggest performance improvements: {code}"},
                    {"role": "documentation", "prompt": "Create documentation for: {code}"}
                ],
                "temperature": 0.3
            },
            "project_planning": {
                "steps": [
                    {"role": "analyst", "prompt": "Analyze project requirements: {requirements}"},
                    {"role": "architect", "prompt": "Design system architecture for: {requirements}"},
                    {"role": "estimator", "prompt": "Estimate timeline and resources for: {requirements}"},
                    {"role": "risk_assessor", "prompt": "Identify risks and mitigation strategies: {requirements}"}
                ],
                "temperature": 0.5
            },
            "documentation_creation": {
                "steps": [
                    {"role": "analyzer", "prompt": "Analyze the purpose and functionality: {topic}"},
                    {"role": "writer", "prompt": "Create comprehensive documentation: {topic}"},
                    {"role": "reviewer", "prompt": "Review and improve documentation: {topic}"},
                    {"role": "example_creator", "prompt": "Create practical examples for: {topic}"}
                ],
                "temperature": 0.6
            }
        }
    
    def execute_workflow(self, workflow_name: str, input_data: str) -> Dict[str, str]:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name]
        results = {}
        
        for step in workflow["steps"]:
            role = step["role"]
            prompt_template = step["prompt"]
            
            # Format prompt with input data
            if "{code}" in prompt_template:
                prompt = prompt_template.format(code=input_data)
            elif "{requirements}" in prompt_template:
                prompt = prompt_template.format(requirements=input_data)
            elif "{topic}" in prompt_template:
                prompt = prompt_template.format(topic=input_data)
            else:
                prompt = prompt_template
            
            # Create messages for this step
            messages = [
                {"role": "system", "content": f"You are a {role} expert providing professional analysis."},
                {"role": "user", "content": prompt}
            ]
            
            try:
                response = self.lm_studio.chat_completion(
                    messages, 
                    temperature=workflow.get("temperature", 0.5)
                )
                results[role] = response
                print(f"✓ {role.replace('_', ' ').title()} step completed")
                
            except Exception as e:
                results[role] = f"Error: {e}"
                print(f"✗ {role.replace('_', ' ').title()} step failed: {e}")
        
        return results
    
    def create_comprehensive_analysis(self, code: str) -> str:
        """Create comprehensive code analysis using multiple perspectives"""
        results = self.execute_workflow("code_review", code)
        
        # Combine results into comprehensive report
        report = "# Comprehensive Code Analysis\n\n"
        
        for role, analysis in results.items():
            role_title = role.replace('_', ' ').title()
            report += f"## {role_title}\n\n{analysis}\n\n"
        
        return report

# Example usage
def demo_workflow():
    """Demonstrate LM Studio workflow execution"""
    
    manager = LMStudioWorkflowManager()
    
    # Example code for analysis
    code_sample = """
    def authenticate_user(username, password):
        import sqlite3
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = cursor.execute(query).fetchone()
        
        conn.close()
        return result is not None
    """
    
    # Execute code review workflow
    print("Executing code review workflow...")
    analysis = manager.create_comprehensive_analysis(code_sample)
    print(analysis)

if __name__ == "__main__":
    demo_workflow()
```

## 🧪 Testing LM Studio Setup

### 1. Basic Functionality Test

```python
# test_lm_studio_basic.py
def test_lm_studio_basic():
    """Test basic LM Studio functionality"""
    
    lm_studio = LMStudioAPI()
    
    # Test server status
    status = lm_studio.get_server_status()
    print(f"Server Status: {status['status']}")
    
    if status["status"] != "running":
        print("✗ LM Studio server not running")
        print("Please start LM Studio and load a model")
        return False
    
    # Test model listing
    try:
        models = lm_studio.list_models()
        if not models:
            print("✗ No models loaded in LM Studio")
            return False
        
        print(f"✓ {len(models)} models available: {models}")
        
        # Test simple chat
        messages = [
            {"role": "user", "content": "Say hello and introduce yourself"}
        ]
        
        response = lm_studio.chat_completion(messages)
        
        if len(response) > 0:
            print("✓ Chat test passed")
            print(f"Response: {response[:100]}...")
            return True
        else:
            print("✗ Empty response from LM Studio")
            return False
            
    except Exception as e:
        print(f"✗ LM Studio test failed: {e}")
        return False

if __name__ == "__main__":
    test_lm_studio_basic()
```

### 2. Performance Benchmark

```python
# test_lm_studio_performance.py
import time
from typing import Dict, List

def benchmark_lm_studio_models() -> Dict[str, Dict]:
    """Benchmark different models in LM Studio"""
    
    lm_studio = LMStudioAPI()
    models = lm_studio.list_models()
    
    if not models:
        print("No models available for benchmarking")
        return {}
    
    test_prompts = [
        "Explain what Docker is in one sentence.",
        "Write a Python function to calculate fibonacci numbers.",
        "List the benefits of microservices architecture."
    ]
    
    results = {}
    
    for model in models:
        print(f"\nBenchmarking model: {model}")
        model_results = {
            "response_times": [],
            "token_rates": [],
            "responses": []
        }
        
        for prompt in test_prompts:
            messages = [{"role": "user", "content": prompt}]
            
            try:
                start_time = time.time()
                response = lm_studio.chat_completion(messages, model=model)
                end_time = time.time()
                
                duration = end_time - start_time
                token_count = len(response.split())
                token_rate = token_count / duration
                
                model_results["response_times"].append(duration)
                model_results["token_rates"].append(token_rate)
                model_results["responses"].append(len(response))
                
                print(f"  {duration:.2f}s, {token_rate:.1f} tokens/sec")
                
            except Exception as e:
                print(f"  Error: {e}")
        
        # Calculate averages
        if model_results["response_times"]:
            model_results["avg_response_time"] = sum(model_results["response_times"]) / len(model_results["response_times"])
            model_results["avg_token_rate"] = sum(model_results["token_rates"]) / len(model_results["token_rates"])
        
        results[model] = model_results
    
    return results

def print_benchmark_summary(results: Dict[str, Dict]):
    """Print benchmark summary"""
    print("\n" + "="*50)
    print("BENCHMARK SUMMARY")
    print("="*50)
    
    for model, data in results.items():
        if "avg_response_time" in data:
            print(f"\n{model}:")
            print(f"  Average Response Time: {data['avg_response_time']:.2f}s")
            print(f"  Average Token Rate: {data['avg_token_rate']:.1f} tokens/sec")

if __name__ == "__main__":
    results = benchmark_lm_studio_models()
    print_benchmark_summary(results)
```

### 3. Integration Test

```python
# test_lm_studio_integration.py
from llmstack.ai_frameworks_integration import LMStudioAgent, AIConfig

def test_lm_studio_integration():
    """Test LM Studio integration with repository"""
    
    config = AIConfig(
        model_name="local-model",
        use_local=True
    )
    
    agent = LMStudioAgent(config)
    agent.initialize()
    
    if not agent.current_model:
        print("✗ LM Studio agent initialization failed")
        return False
    
    # Test repository knowledge
    response = agent.chat("What AI frameworks are available in this repository?")
    
    frameworks = ["autogen", "flowise", "openhands", "aider"]
    mentioned_count = sum(1 for fw in frameworks if fw.lower() in response.lower())
    
    if mentioned_count >= 2:
        print(f"✓ Agent mentioned {mentioned_count} repository frameworks")
        
        # Test code generation
        code = agent.generate_code("Create a function to validate email addresses", "python")
        
        if "def " in code and "email" in code.lower():
            print("✓ Code generation test passed")
            return True
        else:
            print("✗ Code generation test failed")
            return False
    else:
        print(f"✗ Agent only mentioned {mentioned_count} frameworks")
        return False

if __name__ == "__main__":
    test_lm_studio_integration()
```

## 🛟 Troubleshooting

### Common Issues

#### 1. LM Studio Won't Start
```bash
# Check system requirements
# Windows: Windows 10/11 64-bit
# macOS: macOS 10.15+
# Linux: glibc 2.27+

# Clear application cache
# Windows: %APPDATA%\LM Studio
# macOS: ~/Library/Application Support/LM Studio
# Linux: ~/.config/LM Studio

# Restart with admin privileges if needed
```

#### 2. Models Won't Download
```bash
# Check available disk space
df -h  # Linux/macOS
dir C:\  # Windows

# Check internet connection
ping huggingface.co

# Try manual download from Hugging Face
# Then import into LM Studio via File > Import Model
```

#### 3. Server Won't Start
```bash
# Check if port 1234 is available
netstat -an | grep 1234  # Linux/macOS
netstat -an | findstr 1234  # Windows

# Try different port in LM Studio settings
# Kill processes using the port if needed
```

#### 4. Poor Performance
```json
// Adjust model settings in LM Studio
{
  "context_length": 2048,  // Reduce from 4096
  "gpu_layers": 20,        // Reduce if memory issues
  "cpu_threads": 4,        // Match CPU cores
  "batch_size": 256        // Reduce from 512
}
```

#### 5. API Connection Issues
```python
# Test API directly
import requests

try:
    response = requests.get("http://localhost:1234/v1/models", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Models: {response.json()}")
except Exception as e:
    print(f"Connection error: {e}")
```

### Performance Optimization

#### 1. Model Selection Guide
```
For different use cases:
- Quick responses: 1B-3B parameter models
- Balanced performance: 7B parameter models
- High quality: 13B+ parameter models
- Coding: CodeLlama, WizardCoder models
- Chat: Llama, Mistral chat variants
```

#### 2. Hardware Optimization
```json
{
  "gpu_acceleration": {
    "enabled": true,
    "layers_to_offload": -1,  // All layers to GPU
    "memory_fraction": 0.8    // Use 80% of GPU memory
  },
  "cpu_settings": {
    "threads": 8,             // Match CPU cores
    "batch_size": 512
  }
}
```

#### 3. Memory Management
```json
{
  "memory_optimization": {
    "context_length": 4096,   // Adjust based on needs
    "cache_size": 2048,       // KV cache size
    "quantization": "Q4_K_M", // Good balance of quality/speed
    "mlock": true             // Lock model in memory
  }
}
```

## 🚀 Advanced Features

### 1. Custom Model Import

Import your own fine-tuned models:

1. **Prepare Model**: Convert to GGUF format if needed
2. **Import**: File > Import Model in LM Studio
3. **Configure**: Set model parameters and metadata
4. **Test**: Verify model loads and responds correctly

### 2. Model Comparison

Compare multiple models side-by-side:

1. **Split View**: Enable in LM Studio settings
2. **Load Models**: Load different models in each pane
3. **Same Prompts**: Send identical prompts
4. **Evaluate**: Compare response quality and speed

### 3. Batch Processing

Process multiple prompts efficiently:

```python
# batch_processor.py
class LMStudioBatchProcessor:
    """Process multiple prompts in batch"""
    
    def __init__(self):
        self.lm_studio = LMStudioAPI()
    
    def process_batch(self, prompts: List[str], model: str = "local-model") -> List[str]:
        """Process list of prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"Processing {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            messages = [{"role": "user", "content": prompt}]
            
            try:
                response = self.lm_studio.chat_completion(messages, model=model)
                results.append(response)
            except Exception as e:
                results.append(f"Error: {e}")
        
        return results
    
    def process_with_template(self, data_items: List[str], template: str) -> List[str]:
        """Process data items with a template"""
        prompts = [template.format(item=item) for item in data_items]
        return self.process_batch(prompts)

# Example usage
processor = LMStudioBatchProcessor()

# Batch code review
code_files = ["file1.py", "file2.py", "file3.py"]
template = "Review this code for bugs and improvements:\n\n{item}"
reviews = processor.process_with_template(code_files, template)
```

## 📈 Next Steps

1. **Explore Model Hub**: Try different models for various tasks
2. **Optimize Performance**: Fine-tune settings for your hardware
3. **Create Workflows**: Build automated processing workflows
4. **API Integration**: Integrate with your development tools
5. **Custom Models**: Import and test specialized models

## 🎓 Learning Resources

### Official Documentation
- [LM Studio Website](https://lmstudio.ai)
- [LM Studio Documentation](https://lmstudio.ai/docs)

### Model Resources
- [Hugging Face Model Hub](https://huggingface.co/models)
- [GGUF Models](https://huggingface.co/models?library=gguf)

### Repository Examples
- [LM Studio Integration](scripts/install_lm_studio.sh)
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)

---

**🖥️ LM Studio is now configured for local AI model management!**

Enjoy a beautiful, user-friendly interface for running and managing local AI models with seamless API integration.