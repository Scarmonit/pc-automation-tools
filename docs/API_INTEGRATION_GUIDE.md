# 🔗 API Integration Guide

This guide shows you how to integrate with the various APIs provided by the AI automation tools. Learn to build applications that leverage the full power of your AI stack.

## 🚀 Quick Start

### API Endpoints Overview
```bash
# AI Model APIs
Ollama API:     http://localhost:11434/v1
LocalAI API:    http://localhost:8080/v1
LM Studio API:  http://localhost:1234/v1

# AI Agent APIs  
Flowise API:    http://localhost:3001/api/v1
OpenHands API:  http://localhost:3002/api
Custom Orchestrator: http://localhost:8080/api

# Monitoring APIs
Prometheus:     http://localhost:9090/api/v1
Grafana:        http://localhost:3003/api
```

### Authentication
Most local APIs use simple authentication:
```bash
# Ollama (no auth required for local)
curl http://localhost:11434/api/version

# OpenAI-compatible endpoints
export OPENAI_API_KEY="ollama"  # or "sk-localai"
export OPENAI_API_BASE="http://localhost:11434/v1"
```

## 🧠 AI Model APIs

### Ollama API

#### Basic Chat Completion
```python
import requests
import json

def ollama_chat(prompt: str, model: str = "llama3.2") -> str:
    """Send chat request to Ollama"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama API error: {response.status_code}")

# Example usage
response = ollama_chat("Explain machine learning in simple terms")
print(response)
```

#### Streaming Response
```python
import requests
import json

def ollama_stream_chat(prompt: str, model: str = "llama3.2"):
    """Stream chat response from Ollama"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    response = requests.post(url, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if not data.get("done", False):
                yield data.get("response", "")
            else:
                break

# Example usage
print("AI: ", end="", flush=True)
for chunk in ollama_stream_chat("Write a short story about AI"):
    print(chunk, end="", flush=True)
print()
```

#### OpenAI-Compatible API
```python
import openai

# Configure for Ollama
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "ollama"

def openai_compatible_chat(messages: list, model: str = "llama3.2") -> str:
    """Use OpenAI client with Ollama"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    
    return response.choices[0].message.content

# Example usage
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

response = openai_compatible_chat(messages)
print(response)
```

### Advanced Model Management
```python
import requests
from typing import List, Dict, Any

class OllamaManager:
    """Advanced Ollama API management"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        response = requests.get(f"{self.base_url}/api/tags")
        return response.json().get("models", [])
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model"""
        url = f"{self.base_url}/api/pull"
        payload = {"name": model_name}
        
        response = requests.post(url, json=payload)
        return response.status_code == 200
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        url = f"{self.base_url}/api/delete"
        payload = {"name": model_name}
        
        response = requests.delete(url, json=payload)
        return response.status_code == 200
    
    def show_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model information"""
        url = f"{self.base_url}/api/show"
        payload = {"name": model_name}
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def generate_embeddings(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate embeddings for text"""
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": model,
            "prompt": text
        }
        
        response = requests.post(url, json=payload)
        return response.json().get("embedding", [])

# Example usage
ollama = OllamaManager()

# List available models
models = ollama.list_models()
print("Available models:", [m["name"] for m in models])

# Get embeddings
embeddings = ollama.generate_embeddings("Hello, world!")
print(f"Embedding dimensions: {len(embeddings)}")
```

## 🌊 Flowise API Integration

### Basic Flow Execution
```python
import requests
from typing import Dict, Any, Optional

class FlowiseAPI:
    """Flowise API client"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
    
    def execute_flow(self, flow_id: str, question: str, **kwargs) -> Dict[str, Any]:
        """Execute a Flowise flow"""
        url = f"{self.base_url}/api/v1/prediction/{flow_id}"
        
        payload = {
            "question": question,
            **kwargs
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Flowise API error: {response.status_code} - {response.text}")
    
    def stream_flow(self, flow_id: str, question: str, **kwargs):
        """Stream flow execution"""
        url = f"{self.base_url}/api/v1/prediction/{flow_id}"
        
        payload = {
            "question": question,
            "streaming": True,
            **kwargs
        }
        
        response = requests.post(url, json=payload, stream=True)
        
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8')
    
    def get_flow_config(self, flow_id: str) -> Dict[str, Any]:
        """Get flow configuration"""
        url = f"{self.base_url}/api/v1/chatflows/{flow_id}"
        response = requests.get(url)
        return response.json()
    
    def list_flows(self) -> List[Dict[str, Any]]:
        """List available flows"""
        url = f"{self.base_url}/api/v1/chatflows"
        response = requests.get(url)
        return response.json()

# Example usage
flowise = FlowiseAPI()

# Execute a flow
response = flowise.execute_flow(
    flow_id="your-flow-id",
    question="Generate a Python function for sorting",
    temperature=0.7
)
print(response)

# Stream execution
for chunk in flowise.stream_flow("your-flow-id", "Tell me a story"):
    print(chunk, end="")
```

### Advanced Flowise Integration
```python
import asyncio
import aiohttp
from typing import AsyncGenerator

class AsyncFlowiseAPI:
    """Async Flowise API client for high-performance applications"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
    
    async def execute_flow_async(self, session: aiohttp.ClientSession, 
                                flow_id: str, question: str) -> Dict[str, Any]:
        """Execute flow asynchronously"""
        url = f"{self.base_url}/api/v1/prediction/{flow_id}"
        payload = {"question": question}
        
        async with session.post(url, json=payload) as response:
            return await response.json()
    
    async def batch_execute(self, flow_id: str, questions: List[str]) -> List[Dict[str, Any]]:
        """Execute multiple flows in parallel"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.execute_flow_async(session, flow_id, question)
                for question in questions
            ]
            return await asyncio.gather(*tasks)

# Example usage
async def main():
    flowise = AsyncFlowiseAPI()
    
    questions = [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?"
    ]
    
    results = await flowise.batch_execute("your-flow-id", questions)
    
    for question, result in zip(questions, results):
        print(f"Q: {question}")
        print(f"A: {result.get('response', 'No response')}\n")

# Run async example
# asyncio.run(main())
```

## 🤖 Unified Orchestrator API

### Custom Orchestrator Client
```python
import requests
from typing import Dict, Any, List, Optional
from enum import Enum

class TaskType(Enum):
    """Task types for routing"""
    CODE = "code"
    RESEARCH = "research" 
    ANALYSIS = "analysis"
    CHAT = "chat"
    MEMORY = "memory"

class UnifiedOrchestratorAPI:
    """Client for the unified orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    def route_task(self, task: str, task_type: Optional[TaskType] = None, 
                  routing_strategy: str = "auto") -> Dict[str, Any]:
        """Route task to appropriate AI service"""
        url = f"{self.base_url}/api/route"
        
        payload = {
            "task": task,
            "task_type": task_type.value if task_type else None,
            "routing_strategy": routing_strategy
        }
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def multi_agent_collaboration(self, task: str, 
                                 agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute task with multiple agents"""
        url = f"{self.base_url}/api/collaborate"
        
        payload = {
            "task": task,
            "agents": agents or ["autogen", "flowise", "localai"]
        }
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        url = f"{self.base_url}/api/status"
        response = requests.get(url)
        return response.json()
    
    def health_check(self) -> bool:
        """Check if orchestrator is healthy"""
        try:
            url = f"{self.base_url}/api/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

# Example usage
orchestrator = UnifiedOrchestratorAPI()

# Check health
if orchestrator.health_check():
    print("Orchestrator is healthy")
    
    # Route a coding task
    result = orchestrator.route_task(
        "Create a REST API for user management",
        task_type=TaskType.CODE
    )
    print("Routing result:", result)
    
    # Multi-agent collaboration
    collab_result = orchestrator.multi_agent_collaboration(
        "Design and implement a chatbot with memory"
    )
    print("Collaboration result:", collab_result)
```

## 📊 Monitoring API Integration

### Prometheus Metrics API
```python
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

class PrometheusAPI:
    """Prometheus metrics API client"""
    
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
    
    def query(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        """Execute Prometheus query"""
        url = f"{self.base_url}/api/v1/query"
        
        params = {"query": query}
        if time:
            params["time"] = time.timestamp()
        
        response = requests.get(url, params=params)
        return response.json()
    
    def query_range(self, query: str, start: datetime, end: datetime, 
                   step: str = "15s") -> Dict[str, Any]:
        """Execute Prometheus range query"""
        url = f"{self.base_url}/api/v1/query_range"
        
        params = {
            "query": query,
            "start": start.timestamp(),
            "end": end.timestamp(),
            "step": step
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    def get_targets(self) -> Dict[str, Any]:
        """Get scrape targets"""
        url = f"{self.base_url}/api/v1/targets"
        response = requests.get(url)
        return response.json()
    
    def get_service_metrics(self, service: str) -> Dict[str, float]:
        """Get key metrics for a service"""
        metrics = {}
        
        # Request rate
        query = f'rate(ai_requests_total{{service="{service}"}}[5m])'
        result = self.query(query)
        if result["data"]["result"]:
            metrics["request_rate"] = float(result["data"]["result"][0]["value"][1])
        
        # Error rate
        query = f'rate(ai_requests_total{{service="{service}",status="error"}}[5m]) / rate(ai_requests_total{{service="{service}"}}[5m])'
        result = self.query(query)
        if result["data"]["result"]:
            metrics["error_rate"] = float(result["data"]["result"][0]["value"][1])
        
        # Response time (95th percentile)
        query = f'histogram_quantile(0.95, rate(ai_request_duration_seconds_bucket{{service="{service}"}}[5m]))'
        result = self.query(query)
        if result["data"]["result"]:
            metrics["p95_response_time"] = float(result["data"]["result"][0]["value"][1])
        
        return metrics

# Example usage
prometheus = PrometheusAPI()

# Get Ollama metrics
ollama_metrics = prometheus.get_service_metrics("ollama")
print("Ollama metrics:", ollama_metrics)

# Query system CPU usage
cpu_query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
cpu_result = prometheus.query(cpu_query)
print("CPU usage:", cpu_result)
```

### Grafana API Integration
```python
import requests
from typing import Dict, Any, List

class GrafanaAPI:
    """Grafana API client"""
    
    def __init__(self, base_url: str = "http://localhost:3003", 
                 username: str = "admin", password: str = "admin"):
        self.base_url = base_url
        self.auth = (username, password)
    
    def get_dashboards(self) -> List[Dict[str, Any]]:
        """Get all dashboards"""
        url = f"{self.base_url}/api/search"
        response = requests.get(url, auth=self.auth)
        return response.json()
    
    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Get specific dashboard"""
        url = f"{self.base_url}/api/dashboards/uid/{dashboard_id}"
        response = requests.get(url, auth=self.auth)
        return response.json()
    
    def create_alert(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create alert rule"""
        url = f"{self.base_url}/api/v1/provisioning/alert-rules"
        response = requests.post(url, json=alert_config, auth=self.auth)
        return response.json()
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts"""
        url = f"{self.base_url}/api/v1/provisioning/alert-rules"
        response = requests.get(url, auth=self.auth)
        return response.json()

# Example usage
grafana = GrafanaAPI()

# List dashboards
dashboards = grafana.get_dashboards()
for dashboard in dashboards:
    print(f"Dashboard: {dashboard['title']} (ID: {dashboard['uid']})")
```

## 🔄 Workflow Automation Examples

### Complete AI Pipeline
```python
import asyncio
from typing import Dict, Any

class AIWorkflowPipeline:
    """Complete AI workflow using multiple APIs"""
    
    def __init__(self):
        self.ollama = OllamaManager()
        self.flowise = FlowiseAPI()
        self.orchestrator = UnifiedOrchestratorAPI()
        self.prometheus = PrometheusAPI()
    
    async def execute_research_pipeline(self, topic: str) -> Dict[str, Any]:
        """Execute complete research pipeline"""
        pipeline_results = {}
        
        # Step 1: Initial research with Ollama
        research_prompt = f"Research the topic: {topic}. Provide a comprehensive overview."
        initial_research = self.ollama.generate_response(research_prompt)
        pipeline_results["initial_research"] = initial_research
        
        # Step 2: Deep analysis with Flowise
        analysis_result = self.flowise.execute_flow(
            flow_id="analysis-flow-id",
            question=f"Analyze this research: {initial_research}"
        )
        pipeline_results["deep_analysis"] = analysis_result
        
        # Step 3: Multi-agent collaboration for insights
        collaboration_result = self.orchestrator.multi_agent_collaboration(
            f"Generate insights and recommendations for: {topic}"
        )
        pipeline_results["insights"] = collaboration_result
        
        # Step 4: Collect pipeline metrics
        metrics = self.prometheus.get_service_metrics("pipeline")
        pipeline_results["metrics"] = metrics
        
        return pipeline_results
    
    def create_content_generation_workflow(self, content_type: str, topic: str) -> Dict[str, Any]:
        """Create content using multiple AI services"""
        workflow_results = {}
        
        # Route to appropriate service based on content type
        if content_type == "code":
            result = self.orchestrator.route_task(
                f"Generate {content_type} for {topic}",
                task_type=TaskType.CODE
            )
        elif content_type == "documentation":
            result = self.flowise.execute_flow(
                "documentation-flow-id",
                f"Create documentation for {topic}"
            )
        else:
            result = self.ollama.generate_response(
                f"Create {content_type} content about {topic}"
            )
        
        workflow_results["content"] = result
        workflow_results["type"] = content_type
        workflow_results["topic"] = topic
        
        return workflow_results

# Example usage
async def main():
    pipeline = AIWorkflowPipeline()
    
    # Execute research pipeline
    research_results = await pipeline.execute_research_pipeline("quantum computing")
    print("Research pipeline completed:", research_results.keys())
    
    # Generate different types of content
    code_content = pipeline.create_content_generation_workflow("code", "REST API")
    doc_content = pipeline.create_content_generation_workflow("documentation", "API usage")
    
    print("Content generation completed")

# asyncio.run(main())
```

### Real-time Monitoring Dashboard
```python
import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

class RealTimeMonitoringApp:
    """Real-time monitoring dashboard using APIs"""
    
    def __init__(self):
        self.prometheus = PrometheusAPI()
        self.grafana = GrafanaAPI()
    
    def create_dashboard(self):
        """Create Streamlit dashboard"""
        st.title("AI Tools Real-Time Monitoring")
        
        # Service status
        st.header("Service Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ollama_status = self.check_service_health("ollama")
            st.metric("Ollama", "🟢 Online" if ollama_status else "🔴 Offline")
        
        with col2:
            flowise_status = self.check_service_health("flowise")
            st.metric("Flowise", "🟢 Online" if flowise_status else "🔴 Offline")
        
        with col3:
            openhands_status = self.check_service_health("openhands")
            st.metric("OpenHands", "🟢 Online" if openhands_status else "🔴 Offline")
        
        # Performance metrics
        st.header("Performance Metrics")
        
        # Request rate chart
        request_data = self.get_request_rate_data()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=request_data["timestamps"],
            y=request_data["rates"],
            mode='lines+markers',
            name='Requests/sec'
        ))
        fig.update_layout(title="Request Rate Over Time")
        st.plotly_chart(fig)
        
        # Response time chart
        response_data = self.get_response_time_data()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=response_data["timestamps"],
            y=response_data["times"],
            mode='lines+markers',
            name='Response Time (ms)'
        ))
        fig2.update_layout(title="Response Time Over Time")
        st.plotly_chart(fig2)
    
    def check_service_health(self, service: str) -> bool:
        """Check if service is healthy"""
        try:
            query = f'up{{job="{service}"}}'
            result = self.prometheus.query(query)
            return bool(result["data"]["result"])
        except:
            return False
    
    def get_request_rate_data(self) -> Dict[str, List]:
        """Get request rate data for charting"""
        end = datetime.now()
        start = end - timedelta(hours=1)
        
        query = 'sum(rate(ai_requests_total[5m]))'
        result = self.prometheus.query_range(query, start, end, "1m")
        
        timestamps = []
        rates = []
        
        if result["data"]["result"]:
            for value in result["data"]["result"][0]["values"]:
                timestamps.append(datetime.fromtimestamp(value[0]))
                rates.append(float(value[1]))
        
        return {"timestamps": timestamps, "rates": rates}
    
    def get_response_time_data(self) -> Dict[str, List]:
        """Get response time data for charting"""
        end = datetime.now()
        start = end - timedelta(hours=1)
        
        query = 'histogram_quantile(0.95, rate(ai_request_duration_seconds_bucket[5m])) * 1000'
        result = self.prometheus.query_range(query, start, end, "1m")
        
        timestamps = []
        times = []
        
        if result["data"]["result"]:
            for value in result["data"]["result"][0]["values"]:
                timestamps.append(datetime.fromtimestamp(value[0]))
                times.append(float(value[1]))
        
        return {"timestamps": timestamps, "times": times}

# Run dashboard (uncomment to use)
# if __name__ == "__main__":
#     app = RealTimeMonitoringApp()
#     app.create_dashboard()
```

## 🧪 Testing API Integrations

### API Test Suite
```python
import pytest
import requests
from unittest.mock import Mock, patch

class TestAPIIntegrations:
    """Test suite for API integrations"""
    
    def test_ollama_health(self):
        """Test Ollama API health"""
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        assert response.status_code == 200
        assert "version" in response.json()
    
    def test_ollama_generate(self):
        """Test Ollama generation"""
        payload = {
            "model": "llama3.2",
            "prompt": "Say hello",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        assert response.status_code == 200
        assert "response" in response.json()
    
    @pytest.mark.integration
    def test_flowise_flow(self):
        """Test Flowise flow execution"""
        # This would require a valid flow ID
        pytest.skip("Integration test - requires flow setup")
    
    def test_prometheus_query(self):
        """Test Prometheus query"""
        query = "up"
        response = requests.get(
            "http://localhost:9090/api/v1/query",
            params={"query": query}
        )
        assert response.status_code == 200
        assert "data" in response.json()
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling"""
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"error": "Internal server error"}
        
        with pytest.raises(Exception):
            ollama = OllamaManager()
            ollama.list_models()

# Run tests
# pytest test_api_integrations.py -v
```

## 📚 SDK Development

### Python SDK Example
```python
# ai_tools_sdk.py
from typing import Dict, Any, Optional, List
import requests
from dataclasses import dataclass

@dataclass
class AIToolsConfig:
    """Configuration for AI Tools SDK"""
    ollama_url: str = "http://localhost:11434"
    flowise_url: str = "http://localhost:3001"
    orchestrator_url: str = "http://localhost:8080"
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3003"
    grafana_auth: tuple = ("admin", "admin")

class AIToolsSDK:
    """Unified SDK for AI Tools"""
    
    def __init__(self, config: Optional[AIToolsConfig] = None):
        self.config = config or AIToolsConfig()
        self.ollama = OllamaManager(self.config.ollama_url)
        self.flowise = FlowiseAPI(self.config.flowise_url)
        self.orchestrator = UnifiedOrchestratorAPI(self.config.orchestrator_url)
        self.prometheus = PrometheusAPI(self.config.prometheus_url)
    
    def chat(self, message: str, service: str = "auto") -> str:
        """Simple chat interface"""
        if service == "auto":
            return self.orchestrator.route_task(message)["response"]
        elif service == "ollama":
            return self.ollama.generate_response(message)
        elif service == "flowise":
            return self.flowise.execute_flow("default-flow-id", message)["response"]
        else:
            raise ValueError(f"Unknown service: {service}")
    
    def generate_code(self, description: str) -> str:
        """Generate code using best available service"""
        return self.orchestrator.route_task(
            description, 
            task_type="code"
        )["response"]
    
    def analyze_data(self, data: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze data using AI services"""
        prompt = f"Analyze this data ({analysis_type}): {data}"
        return self.orchestrator.route_task(prompt, task_type="analysis")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        return {
            "orchestrator": self.orchestrator.health_check(),
            "services": self.orchestrator.get_system_status(),
            "metrics": self.prometheus.get_service_metrics("system")
        }

# Example usage
if __name__ == "__main__":
    # Initialize SDK
    sdk = AIToolsSDK()
    
    # Simple chat
    response = sdk.chat("Hello, how are you?")
    print(f"AI: {response}")
    
    # Generate code
    code = sdk.generate_code("Create a Python function to calculate factorial")
    print(f"Generated code:\n{code}")
    
    # Check system health
    health = sdk.get_system_health()
    print(f"System health: {health}")
```

## 📈 Next Steps

1. **Explore Advanced APIs**: Dive deeper into specific service APIs
2. **Build Custom Integrations**: Create applications using the SDK
3. **Implement Webhooks**: Set up real-time notifications
4. **Create Monitoring Dashboards**: Build custom monitoring solutions
5. **Develop Workflow Automation**: Automate complex AI workflows

## 🎓 Learning Resources

### API Documentation
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Prometheus API Documentation](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Grafana API Documentation](https://grafana.com/docs/grafana/latest/http_api/)

### Repository Examples
- [API Integration Examples](llmstack/examples/)
- [SDK Development](llmstack/src/)
- [Monitoring Scripts](scripts/monitoring/)

---

**🔗 Your AI automation tools are now API-ready for integration into any application!**

Build powerful applications that leverage the full capabilities of your AI infrastructure.