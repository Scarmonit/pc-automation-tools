# ⚡ vLLM High-Performance Deployment Guide

vLLM is a high-performance, memory-efficient serving engine for large language models. This guide shows you how to deploy vLLM for maximum throughput and efficiency in your AI automation infrastructure.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install and configure vLLM
bash scripts/setup_vllm.sh

# Start vLLM server with default model
python3 -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --port 8000

# Configure with automation tools
python3 scripts/configure_providers.py --vllm
```

### Manual Installation
```bash
# Install vLLM
pip install vllm

# For CUDA support (GPU acceleration)
pip install vllm[cuda]

# For specific CUDA version
pip install vllm[cuda-12.1]
```

## 📋 Prerequisites

### Hardware Requirements
- **CPU**: 16+ cores recommended for CPU-only deployment
- **RAM**: 32GB+ (depends on model size)
- **GPU**: NVIDIA GPU with 16GB+ VRAM (optional but recommended)
- **Storage**: SSD with 50GB+ free space for models

### Software Requirements
- **Python 3.8+**
- **CUDA 11.8+ or 12.1+** (for GPU acceleration)
- **Docker** (for containerized deployment)
- **Linux/WSL2** (recommended, Windows support limited)

### CUDA Setup (GPU)
```bash
# Check NVIDIA driver
nvidia-smi

# Install CUDA toolkit if needed
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt -y install cuda

# Verify CUDA installation
nvcc --version
```

## 🔧 Configuration

### 1. Basic vLLM Server

#### CPU-Only Deployment
```bash
# Start vLLM server with CPU
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --port 8000 \
  --host 0.0.0.0 \
  --disable-log-requests \
  --enforce-eager
```

#### GPU Deployment
```bash
# Start vLLM server with GPU
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.8 \
  --max-model-len 4096 \
  --dtype float16
```

### 2. Advanced Configuration

#### High-Performance Setup
```bash
# Maximum performance configuration
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-13b-chat-hf \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.95 \
  --max-model-len 4096 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 256 \
  --dtype float16 \
  --enable-prefix-caching \
  --disable-log-requests \
  --tensor-parallel-size 2
```

#### Multi-GPU Configuration
```bash
# Multi-GPU deployment (2 GPUs)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-70b-chat-hf \
  --port 8000 \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --dtype float16
```

### 3. Docker Deployment

#### Single GPU Container
```dockerfile
# Dockerfile.vllm
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Install vLLM
RUN pip install vllm torch torchvision torchaudio

# Set working directory
WORKDIR /app

# Copy configuration files
COPY vllm_config.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "meta-llama/Llama-2-7b-chat-hf", \
     "--port", "8000", \
     "--host", "0.0.0.0"]
```

#### Docker Compose Configuration
```yaml
# docker-compose.vllm.yml
version: '3.8'

services:
  vllm-server:
    build:
      context: .
      dockerfile: Dockerfile.vllm
    container_name: vllm-server
    ports:
      - "8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    runtime: nvidia
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      python -m vllm.entrypoints.openai.api_server
      --model meta-llama/Llama-2-7b-chat-hf
      --port 8000
      --host 0.0.0.0
      --gpu-memory-utilization 0.8
      --max-model-len 4096
      --dtype float16

  vllm-metrics:
    image: prom/prometheus:latest
    container_name: vllm-metrics
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus-vllm.yml:/etc/prometheus/prometheus.yml
    depends_on:
      - vllm-server
    restart: unless-stopped

volumes:
  models:
  logs:
```

### 4. Configuration File

Create `vllm_config.py` for programmatic configuration:

```python
# vllm_config.py
from dataclasses import dataclass
from typing import Optional, List
import os

@dataclass
class VLLMConfig:
    """vLLM server configuration"""
    
    # Model settings
    model: str = "meta-llama/Llama-2-7b-chat-hf"
    revision: Optional[str] = None
    tokenizer: Optional[str] = None
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Performance settings
    gpu_memory_utilization: float = 0.8
    max_model_len: int = 4096
    max_num_batched_tokens: int = 8192
    max_num_seqs: int = 256
    dtype: str = "float16"
    
    # Parallel processing
    tensor_parallel_size: int = 1
    pipeline_parallel_size: int = 1
    
    # Memory optimization
    enable_prefix_caching: bool = True
    block_size: int = 16
    swap_space: int = 4
    
    # Logging and monitoring
    disable_log_requests: bool = True
    log_level: str = "info"
    
    # Safety and limits
    enforce_eager: bool = False
    max_logprobs: int = 5
    
    @classmethod
    def from_env(cls) -> 'VLLMConfig':
        """Create config from environment variables"""
        return cls(
            model=os.getenv("VLLM_MODEL", cls.model),
            host=os.getenv("VLLM_HOST", cls.host),
            port=int(os.getenv("VLLM_PORT", cls.port)),
            gpu_memory_utilization=float(os.getenv("VLLM_GPU_MEMORY", cls.gpu_memory_utilization)),
            max_model_len=int(os.getenv("VLLM_MAX_MODEL_LEN", cls.max_model_len)),
            tensor_parallel_size=int(os.getenv("VLLM_TENSOR_PARALLEL", cls.tensor_parallel_size)),
            dtype=os.getenv("VLLM_DTYPE", cls.dtype)
        )
    
    def to_args(self) -> List[str]:
        """Convert config to command line arguments"""
        args = [
            "--model", self.model,
            "--host", self.host,
            "--port", str(self.port),
            "--gpu-memory-utilization", str(self.gpu_memory_utilization),
            "--max-model-len", str(self.max_model_len),
            "--max-num-batched-tokens", str(self.max_num_batched_tokens),
            "--max-num-seqs", str(self.max_num_seqs),
            "--dtype", self.dtype,
            "--tensor-parallel-size", str(self.tensor_parallel_size),
            "--block-size", str(self.block_size),
            "--swap-space", str(self.swap_space),
            "--log-level", self.log_level
        ]
        
        if self.revision:
            args.extend(["--revision", self.revision])
        
        if self.tokenizer:
            args.extend(["--tokenizer", self.tokenizer])
        
        if self.enable_prefix_caching:
            args.append("--enable-prefix-caching")
        
        if self.disable_log_requests:
            args.append("--disable-log-requests")
        
        if self.enforce_eager:
            args.append("--enforce-eager")
        
        return args

def start_vllm_server(config: VLLMConfig):
    """Start vLLM server with given configuration"""
    import subprocess
    
    cmd = ["python", "-m", "vllm.entrypoints.openai.api_server"] + config.to_args()
    
    print(f"Starting vLLM server with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("vLLM server stopped by user")
    except Exception as e:
        print(f"vLLM server error: {e}")

if __name__ == "__main__":
    config = VLLMConfig.from_env()
    start_vllm_server(config)
```

## 🔄 Integration with Repository

### vLLM API Client

```python
# vllm_client.py
import requests
import json
from typing import Dict, Any, List, Optional, Iterator
import asyncio
import aiohttp

class VLLMClient:
    """High-performance vLLM API client"""
    
    def __init__(self, base_url: str = "http://localhost:8000/v1"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if vLLM server is healthy"""
        try:
            response = self.session.get(f"{self.base_url.replace('/v1', '')}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            return [model["id"] for model in response.json()["data"]]
        except Exception as e:
            raise Exception(f"Failed to list models: {e}")
    
    def chat_completion(self, messages: List[Dict], model: str = None,
                       temperature: float = 0.7, max_tokens: int = 2048,
                       top_p: float = 0.9, stop: List[str] = None) -> str:
        """Send chat completion request"""
        
        payload = {
            "model": model or "default",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": False
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            raise Exception(f"vLLM API error: {e}")
    
    def stream_chat_completion(self, messages: List[Dict], model: str = None,
                              temperature: float = 0.7, max_tokens: int = 2048) -> Iterator[str]:
        """Stream chat completion response"""
        
        payload = {
            "model": model or "default",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                delta = data.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            raise Exception(f"vLLM stream error: {e}")
    
    def completion(self, prompt: str, model: str = None,
                  temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Send completion request"""
        
        payload = {
            "model": model or "default",
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["text"]
            
        except Exception as e:
            raise Exception(f"vLLM completion error: {e}")

class AsyncVLLMClient:
    """Asynchronous vLLM client for high-throughput applications"""
    
    def __init__(self, base_url: str = "http://localhost:8000/v1"):
        self.base_url = base_url
    
    async def batch_chat_completion(self, requests: List[Dict]) -> List[str]:
        """Process multiple chat requests in parallel"""
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._single_chat_request(session, req)
                for req in requests
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions and return results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(f"Error: {result}")
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def _single_chat_request(self, session: aiohttp.ClientSession, 
                                  request: Dict) -> str:
        """Send single chat request"""
        
        payload = {
            "model": request.get("model", "default"),
            "messages": request["messages"],
            "temperature": request.get("temperature", 0.7),
            "max_tokens": request.get("max_tokens", 2048),
            "stream": False
        }
        
        try:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=60
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            raise Exception(f"Async chat error: {e}")

# Integration with repository patterns
class VLLMAgent:
    """vLLM agent wrapper for unified orchestrator"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = VLLMClient(base_url=f"http://localhost:8000/v1")
        self.async_client = AsyncVLLMClient(base_url=f"http://localhost:8000/v1")
        
    def initialize(self):
        """Initialize vLLM connection"""
        try:
            if self.client.health_check():
                models = self.client.list_models()
                logger.info(f"vLLM initialized with {len(models)} models")
            else:
                logger.error("vLLM server not responding")
        except Exception as e:
            logger.error(f"Failed to initialize vLLM: {e}")
    
    def chat(self, message: str, context: str = None) -> str:
        """Chat with vLLM model"""
        messages = []
        
        # Add system context
        system_message = """You are an AI assistant specialized in PC automation tools and AI frameworks.
        You understand AutoGen, Flowise, OpenHands, Aider, MemGPT, CAMEL-AI, and other AI tools.
        Provide practical, working solutions with proper integration patterns."""
        
        if context:
            system_message += f"\n\nAdditional context: {context}"
        
        messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": message})
        
        try:
            return self.client.chat_completion(
                messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        except Exception as e:
            logger.error(f"vLLM chat error: {e}")
            return f"Error: {e}"
    
    async def batch_process(self, requests: List[str]) -> List[str]:
        """Process multiple requests in parallel"""
        
        batch_requests = []
        for request in requests:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": request}
            ]
            batch_requests.append({"messages": messages})
        
        try:
            return await self.async_client.batch_chat_completion(batch_requests)
        except Exception as e:
            logger.error(f"vLLM batch processing error: {e}")
            return [f"Error: {e}"] * len(requests)

# Example usage
def demo_vllm_integration():
    """Demonstrate vLLM integration"""
    
    client = VLLMClient()
    
    # Check health
    if not client.health_check():
        print("vLLM server is not running")
        return
    
    # List models
    models = client.list_models()
    print(f"Available models: {models}")
    
    # Chat completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the benefits of high-performance AI inference"}
    ]
    
    response = client.chat_completion(messages)
    print(f"Response: {response}")
    
    # Streaming completion
    print("Streaming response:")
    for chunk in client.stream_chat_completion(messages):
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    demo_vllm_integration()
```

### Performance Monitoring

```python
# vllm_monitoring.py
import time
import psutil
import GPUtil
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Prometheus metrics for vLLM
VLLM_REQUESTS = Counter('vllm_requests_total', 'Total vLLM requests', ['model', 'status'])
VLLM_REQUEST_DURATION = Histogram('vllm_request_duration_seconds', 'vLLM request duration', ['model'])
VLLM_ACTIVE_REQUESTS = Gauge('vllm_active_requests', 'Active vLLM requests')
VLLM_GPU_MEMORY = Gauge('vllm_gpu_memory_used_bytes', 'vLLM GPU memory usage', ['gpu_id'])
VLLM_THROUGHPUT = Gauge('vllm_throughput_tokens_per_second', 'vLLM throughput in tokens/sec')

class VLLMMonitor:
    """Monitor vLLM performance and resources"""
    
    def __init__(self, vllm_client: VLLMClient):
        self.client = vllm_client
        self.metrics_port = 9091
        self.start_time = time.time()
        self.total_tokens = 0
    
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        start_http_server(self.metrics_port)
        print(f"vLLM metrics server started on port {self.metrics_port}")
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system resource metrics"""
        metrics = {}
        
        # CPU and memory
        metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        metrics["memory_percent"] = memory.percent
        metrics["memory_used_gb"] = memory.used / (1024**3)
        
        # GPU metrics
        try:
            gpus = GPUtil.getGPUs()
            gpu_metrics = []
            
            for i, gpu in enumerate(gpus):
                gpu_data = {
                    "id": i,
                    "utilization": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                    "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    "temperature": gpu.temperature
                }
                gpu_metrics.append(gpu_data)
                
                # Update Prometheus metrics
                VLLM_GPU_MEMORY.labels(gpu_id=i).set(gpu.memoryUsed * 1024 * 1024)  # Convert to bytes
            
            metrics["gpus"] = gpu_metrics
            
        except Exception as e:
            print(f"Failed to collect GPU metrics: {e}")
            metrics["gpus"] = []
        
        return metrics
    
    def benchmark_performance(self, num_requests: int = 10) -> Dict[str, float]:
        """Benchmark vLLM performance"""
        
        if not self.client.health_check():
            return {"error": "vLLM server not available"}
        
        test_messages = [
            {"role": "user", "content": "Write a short Python function to calculate factorial."}
        ]
        
        response_times = []
        token_counts = []
        
        print(f"Running performance benchmark with {num_requests} requests...")
        
        for i in range(num_requests):
            start_time = time.time()
            
            try:
                response = self.client.chat_completion(test_messages)
                end_time = time.time()
                
                duration = end_time - start_time
                tokens = len(response.split())
                
                response_times.append(duration)
                token_counts.append(tokens)
                
                # Update Prometheus metrics
                VLLM_REQUESTS.labels(model="default", status="success").inc()
                VLLM_REQUEST_DURATION.labels(model="default").observe(duration)
                
                print(f"Request {i+1}: {duration:.2f}s, {tokens} tokens")
                
            except Exception as e:
                VLLM_REQUESTS.labels(model="default", status="error").inc()
                print(f"Request {i+1} failed: {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            avg_tokens = sum(token_counts) / len(token_counts)
            throughput = avg_tokens / avg_response_time
            
            # Update throughput metric
            VLLM_THROUGHPUT.set(throughput)
            
            return {
                "avg_response_time": avg_response_time,
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "avg_tokens_per_request": avg_tokens,
                "throughput_tokens_per_second": throughput,
                "total_requests": len(response_times),
                "failed_requests": num_requests - len(response_times)
            }
        else:
            return {"error": "All requests failed"}
    
    def monitor_continuous(self, interval: int = 30):
        """Monitor vLLM continuously"""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                # Collect system metrics
                system_metrics = self.collect_system_metrics()
                
                print(f"\n--- vLLM Monitor ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
                print(f"CPU: {system_metrics['cpu_percent']:.1f}%")
                print(f"Memory: {system_metrics['memory_percent']:.1f}% ({system_metrics['memory_used_gb']:.1f}GB)")
                
                for gpu in system_metrics.get("gpus", []):
                    print(f"GPU {gpu['id']}: {gpu['utilization']:.1f}% utilization, "
                          f"{gpu['memory_percent']:.1f}% memory ({gpu['memory_used']}MB/{gpu['memory_total']}MB)")
                
                # Check vLLM health
                if self.client.health_check():
                    print("vLLM Status: ✓ Healthy")
                else:
                    print("vLLM Status: ✗ Unhealthy")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)

def main():
    """Main monitoring function"""
    client = VLLMClient()
    monitor = VLLMMonitor(client)
    
    # Start metrics server
    monitor.start_metrics_server()
    
    # Run benchmark
    benchmark_results = monitor.benchmark_performance()
    print("\nBenchmark Results:")
    for key, value in benchmark_results.items():
        print(f"  {key}: {value}")
    
    # Start continuous monitoring
    monitor.monitor_continuous()

if __name__ == "__main__":
    main()
```

## 🧪 Testing vLLM Setup

### 1. Basic Functionality Test

```python
# test_vllm_basic.py
def test_vllm_basic():
    """Test basic vLLM functionality"""
    
    client = VLLMClient()
    
    # Test health check
    if not client.health_check():
        print("✗ vLLM server not responding")
        print("Please start vLLM server:")
        print("python -m vllm.entrypoints.openai.api_server --model microsoft/DialoGPT-medium")
        return False
    
    print("✓ vLLM server is healthy")
    
    # Test model listing
    try:
        models = client.list_models()
        if models:
            print(f"✓ {len(models)} models available: {models}")
        else:
            print("⚠ No models loaded")
        
        # Test chat completion
        messages = [
            {"role": "user", "content": "Say hello and explain what you are in one sentence."}
        ]
        
        response = client.chat_completion(messages)
        
        if response and len(response) > 0:
            print("✓ Chat completion test passed")
            print(f"Response: {response[:100]}...")
            return True
        else:
            print("✗ Empty response from vLLM")
            return False
            
    except Exception as e:
        print(f"✗ vLLM test failed: {e}")
        return False

if __name__ == "__main__":
    test_vllm_basic()
```

### 2. Performance Stress Test

```python
# test_vllm_stress.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def test_vllm_concurrent_load():
    """Test vLLM under concurrent load"""
    
    client = VLLMClient()
    
    if not client.health_check():
        print("vLLM server not available")
        return
    
    def single_request(request_id: int) -> Dict[str, Any]:
        """Single request for load testing"""
        start_time = time.time()
        
        messages = [
            {"role": "user", "content": f"Request {request_id}: Explain machine learning briefly."}
        ]
        
        try:
            response = client.chat_completion(messages, max_tokens=100)
            duration = time.time() - start_time
            
            return {
                "request_id": request_id,
                "success": True,
                "duration": duration,
                "response_length": len(response)
            }
        except Exception as e:
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    # Concurrent load test
    num_requests = 20
    max_workers = 5
    
    print(f"Starting concurrent load test: {num_requests} requests, {max_workers} workers")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(single_request, i) for i in range(num_requests)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Analyze results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        min_duration = min(r["duration"] for r in successful)
        max_duration = max(r["duration"] for r in successful)
        
        print(f"\nLoad Test Results:")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Successful Requests: {len(successful)}/{num_requests}")
        print(f"Failed Requests: {len(failed)}")
        print(f"Average Response Time: {avg_duration:.2f}s")
        print(f"Min Response Time: {min_duration:.2f}s")
        print(f"Max Response Time: {max_duration:.2f}s")
        print(f"Requests per Second: {len(successful) / total_duration:.2f}")
        
        if failed:
            print(f"\nFailed Requests:")
            for f in failed[:5]:  # Show first 5 failures
                print(f"  Request {f['request_id']}: {f['error']}")
    
    return results

async def test_vllm_async_batch():
    """Test async batch processing"""
    
    async_client = AsyncVLLMClient()
    
    requests = []
    for i in range(10):
        messages = [{"role": "user", "content": f"Batch request {i}: What is AI?"}]
        requests.append({"messages": messages, "max_tokens": 50})
    
    print("Testing async batch processing...")
    start_time = time.time()
    
    try:
        results = await async_client.batch_chat_completion(requests)
        duration = time.time() - start_time
        
        successful = [r for r in results if not r.startswith("Error:")]
        
        print(f"Batch Processing Results:")
        print(f"Duration: {duration:.2f}s")
        print(f"Successful: {len(successful)}/{len(requests)}")
        print(f"Throughput: {len(successful) / duration:.2f} requests/sec")
        
        return results
        
    except Exception as e:
        print(f"Async batch test failed: {e}")
        return []

if __name__ == "__main__":
    # Run concurrent load test
    test_vllm_concurrent_load()
    
    # Run async batch test
    asyncio.run(test_vllm_async_batch())
```

### 3. Integration Test

```python
# test_vllm_integration.py
from llmstack.ai_frameworks_integration import VLLMAgent, AIConfig

def test_vllm_integration():
    """Test vLLM integration with repository"""
    
    config = AIConfig(
        model_name="default",
        temperature=0.7,
        max_tokens=2048,
        use_local=True
    )
    
    agent = VLLMAgent(config)
    agent.initialize()
    
    # Test repository knowledge
    response = agent.chat("What AI frameworks are included in this automation tools repository?")
    
    frameworks = ["autogen", "flowise", "openhands", "aider", "memgpt"]
    mentioned_count = sum(1 for fw in frameworks if fw.lower() in response.lower())
    
    if mentioned_count >= 2:
        print(f"✓ vLLM agent mentioned {mentioned_count} repository frameworks")
        
        # Test batch processing
        requests = [
            "Explain AutoGen multi-agent systems",
            "How does Flowise work?",
            "What is the purpose of OpenHands?"
        ]
        
        import asyncio
        batch_results = asyncio.run(agent.batch_process(requests))
        
        successful_batch = [r for r in batch_results if not r.startswith("Error:")]
        
        if len(successful_batch) >= 2:
            print(f"✓ Batch processing successful: {len(successful_batch)}/{len(requests)}")
            return True
        else:
            print(f"✗ Batch processing failed: {len(successful_batch)}/{len(requests)}")
            return False
    else:
        print(f"✗ vLLM agent only mentioned {mentioned_count} frameworks")
        return False

if __name__ == "__main__":
    test_vllm_integration()
```

## 🛟 Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory
```bash
# Reduce GPU memory utilization
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --gpu-memory-utilization 0.6 \  # Reduce from 0.8
  --max-model-len 2048 \           # Reduce context length
  --max-num-seqs 128               # Reduce batch size
```

#### 2. Model Loading Errors
```bash
# Check model compatibility
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'microsoft/DialoGPT-medium'
tokenizer = AutoTokenizer.from_pretrained(model_name)
print('Model is compatible with Transformers')
"

# Try CPU-only mode first
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --enforce-eager
```

#### 3. Performance Issues
```bash
# Check GPU utilization
nvidia-smi

# Monitor vLLM process
htop -p $(pgrep -f vllm)

# Optimize for your hardware
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --tensor-parallel-size 1 \      # Adjust for multi-GPU
  --pipeline-parallel-size 1 \
  --enable-prefix-caching \
  --dtype float16
```

#### 4. Server Not Starting
```bash
# Check port availability
netstat -an | grep 8000

# Try different port
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --port 8001

# Check logs
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --log-level debug
```

#### 5. Docker Issues
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8-runtime-ubuntu20.04 nvidia-smi

# Build with specific CUDA version
docker build --build-arg CUDA_VERSION=12.1 -t vllm-server .

# Debug container
docker run -it --gpus all vllm-server bash
```

### Performance Optimization

#### 1. Model Selection
```bash
# Choose appropriate model size for your hardware
# 8GB VRAM: 7B parameter models
# 16GB VRAM: 13B parameter models  
# 24GB VRAM: 30B parameter models
# 40GB+ VRAM: 70B parameter models

# Use quantized models for better efficiency
# GPTQ models: Lower memory, faster inference
# AWQ models: Balanced quality and speed
```

#### 2. Memory Optimization
```bash
# Optimize memory usage
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --gpu-memory-utilization 0.95 \
  --swap-space 4 \
  --enable-prefix-caching \
  --block-size 16
```

#### 3. Throughput Optimization
```bash
# Maximize throughput
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/DialoGPT-medium \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 256 \
  --enable-chunked-prefill \
  --max-num-batched-tokens 8192
```

## 📈 Next Steps

1. **Optimize for Your Hardware**: Fine-tune settings for your specific GPU/CPU setup
2. **Experiment with Models**: Try different model sizes and types
3. **Scale Deployment**: Use multiple GPUs or model parallelism
4. **Monitor Performance**: Set up comprehensive monitoring
5. **Production Deployment**: Implement load balancing and auto-scaling

## 🎓 Learning Resources

### Official Documentation
- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub Repository](https://github.com/vllm-project/vllm)

### Performance Guides
- [vLLM Performance Tuning](https://docs.vllm.ai/en/latest/performance/performance_guide.html)
- [Model Parallelism Guide](https://docs.vllm.ai/en/latest/distributed/distributed_serving.html)

### Repository Examples
- [vLLM Setup Script](scripts/setup_vllm.sh)
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)

---

**⚡ vLLM is now configured for high-performance AI inference!**

Experience blazing-fast AI model serving with maximum throughput and efficiency for your automation tools.