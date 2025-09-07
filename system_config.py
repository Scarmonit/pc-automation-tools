"""
System Performance Optimization Configuration
Optimizes CPU, GPU, and memory usage for AI research and web scraping
"""

import os
import psutil
import json
from pathlib import Path

class SystemOptimizer:
    """Optimize system resources for AI workloads"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.logical_cpu_count = psutil.cpu_count(logical=True)
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
    def get_system_info(self):
        """Get comprehensive system information"""
        info = {
            "cpu_physical_cores": self.cpu_count,
            "cpu_logical_cores": self.logical_cpu_count,
            "total_memory_gb": round(self.memory_gb, 2),
            "available_memory_gb": round(self.available_memory_gb, 2),
            "memory_usage_percent": psutil.virtual_memory().percent
        }
        
        # Check GPU availability
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(', ')
                info['gpu_name'] = gpu_info[0] if len(gpu_info) > 0 else 'Unknown'
                info['gpu_memory_mb'] = int(gpu_info[1]) if len(gpu_info) > 1 else 0
                info['gpu_available'] = True
            else:
                info['gpu_available'] = False
        except:
            info['gpu_available'] = False
            
        return info
    
    def get_optimal_worker_counts(self):
        """Calculate optimal worker/thread counts for different tasks"""
        
        # Conservative approach to leave resources for system
        cpu_reserve = 4  # Reserve 4 cores for system
        memory_reserve_gb = 8  # Reserve 8GB for system
        
        available_cores = max(1, self.logical_cpu_count - cpu_reserve)
        available_memory = max(4, self.available_memory_gb - memory_reserve_gb)
        
        return {
            # Web scraping - I/O bound, can use more workers
            "web_scraping_workers": min(available_cores * 2, 32),
            
            # AI processing - CPU/GPU bound, more conservative
            "ai_processing_workers": min(available_cores // 2, 16),
            
            # General async tasks
            "async_workers": min(available_cores, 24),
            
            # Memory-intensive tasks (per GB of available RAM)
            "memory_intensive_concurrent": max(1, int(available_memory // 4)),
            
            # Database connections
            "db_connections": min(available_cores, 20)
        }
    
    def get_ollama_optimization_config(self):
        """Generate optimal Ollama configuration"""
        
        # Calculate optimal settings based on hardware
        config = {
            # CPU optimization
            "num_thread": min(self.logical_cpu_count - 2, 30),  # Leave 2 threads for system
            "num_gpu": 1 if self.get_system_info()['gpu_available'] else 0,
            
            # Memory optimization (in MB)
            "num_ctx": min(8192, int(self.available_memory_gb * 1024 * 0.1)),  # 10% of available RAM for context
            
            # GPU memory optimization
            "num_gqa": 8,  # Grouped query attention for efficiency
            "num_batch": min(512, int(self.available_memory_gb * 32)),  # Batch size based on RAM
            
            # Performance settings
            "low_vram": False if self.get_system_info().get('gpu_memory_mb', 0) > 12000 else True,
            "numa": True,  # Enable NUMA optimization
            "mmap": True,  # Enable memory mapping
            
            # Environment variables for optimization
            "env": {
                "OMP_NUM_THREADS": str(min(self.logical_cpu_count - 2, 16)),
                "CUDA_VISIBLE_DEVICES": "0",  # Use first GPU
                "OLLAMA_NUM_PARALLEL": "4",  # Parallel requests
                "OLLAMA_MAX_LOADED_MODELS": "2",  # Models in memory
                "OLLAMA_FLASH_ATTENTION": "1",  # Enable flash attention if available
                "OLLAMA_GPU_OVERHEAD": "0.1"  # Reserve 10% GPU memory
            }
        }
        
        return config

def set_environment_optimizations():
    """Set system environment variables for optimal performance"""
    
    optimizer = SystemOptimizer()
    workers = optimizer.get_optimal_worker_counts()
    
    # Set environment variables
    env_vars = {
        # Python optimizations
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        
        # Threading optimizations
        "OMP_NUM_THREADS": str(min(psutil.cpu_count(logical=True) - 2, 16)),
        "MKL_NUM_THREADS": str(min(psutil.cpu_count(logical=True) - 2, 16)),
        "NUMBA_NUM_THREADS": str(min(psutil.cpu_count(logical=True) - 2, 16)),
        
        # Memory optimizations
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:128",
        "CUDA_LAUNCH_BLOCKING": "0",
        
        # Async optimizations
        "ASYNC_WORKER_COUNT": str(workers["async_workers"]),
        "WEB_SCRAPING_WORKERS": str(workers["web_scraping_workers"]),
        
        # ChromaDB optimizations
        "CHROMA_SERVER_HTTP_PORT": "8000",
        "CHROMA_SERVER_GRPC_PORT": "50051"
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        
    return env_vars

def create_optimized_configs():
    """Create configuration files for all tools"""
    
    optimizer = SystemOptimizer()
    system_info = optimizer.get_system_info()
    workers = optimizer.get_optimal_worker_counts()
    ollama_config = optimizer.get_ollama_optimization_config()
    
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)
    
    # Ollama configuration
    ollama_config_path = config_dir / "ollama_config.json"
    with open(ollama_config_path, 'w') as f:
        json.dump(ollama_config, f, indent=2)
    
    # ScrapeGraphAI configuration
    scrapegraph_config = {
        "llm": {
            "model": "ollama/gemma2:27b",
            "base_url": "http://localhost:11434",
            "temperature": 0.1,
            "timeout": 120,
            "max_tokens": 4096
        },
        "browser": {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu" if not system_info['gpu_available'] else "",
                "--memory-pressure-off",
                f"--max_old_space_size={int(optimizer.available_memory_gb * 1024 * 0.3)}"
            ]
        },
        "performance": {
            "concurrent_requests": workers["web_scraping_workers"],
            "request_delay": 1.0,
            "timeout": 60
        }
    }
    
    scrapegraph_config_path = config_dir / "scrapegraph_config.json"
    with open(scrapegraph_config_path, 'w') as f:
        json.dump(scrapegraph_config, f, indent=2)
    
    # Crawl4AI configuration
    crawl4ai_config = {
        "browser_config": {
            "headless": True,
            "verbose": False,
            "java_script_enabled": True,
            "browser_type": "chromium",
            "chrome_args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu" if not system_info['gpu_available'] else "",
                "--memory-pressure-off",
                f"--max_old_space_size={int(optimizer.available_memory_gb * 1024 * 0.2)}"
            ]
        },
        "crawler_config": {
            "concurrent_crawls": min(workers["web_scraping_workers"], 8),
            "wait_for": 2000,
            "page_timeout": 30000,
            "word_count_threshold": 50,
            "screenshot": False,
            "pdf_extraction": True
        },
        "performance": {
            "semaphore_limit": min(workers["async_workers"], 12),
            "chunk_size": 1000,
            "max_retries": 3
        }
    }
    
    crawl4ai_config_path = config_dir / "crawl4ai_config.json"
    with open(crawl4ai_config_path, 'w') as f:
        json.dump(crawl4ai_config, f, indent=2)
    
    # ChromaDB configuration
    chromadb_config = {
        "settings": {
            "persist_directory": "./chroma_db",
            "anonymized_telemetry": False
        },
        "performance": {
            "batch_size": min(1000, workers["db_connections"] * 50),
            "max_connections": workers["db_connections"],
            "query_threads": min(workers["ai_processing_workers"], 8)
        }
    }
    
    chromadb_config_path = config_dir / "chromadb_config.json"
    with open(chromadb_config_path, 'w') as f:
        json.dump(chromadb_config, f, indent=2)
    
    # System summary
    summary = {
        "system_info": system_info,
        "worker_counts": workers,
        "ollama_optimization": ollama_config,
        "config_files_created": [
            str(ollama_config_path),
            str(scrapegraph_config_path), 
            str(crawl4ai_config_path),
            str(chromadb_config_path)
        ]
    }
    
    summary_path = config_dir / "system_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def main():
    """Generate optimized system configuration"""
    
    print("=== System Performance Optimization ===")
    print()
    
    # Set environment optimizations
    env_vars = set_environment_optimizations()
    print("Environment variables optimized:")
    for key, value in list(env_vars.items())[:10]:  # Show first 10
        print(f"  {key} = {value}")
    print(f"  ... and {len(env_vars) - 10} more")
    print()
    
    # Create configuration files
    summary = create_optimized_configs()
    
    print("System Analysis:")
    print(f"  CPU: {summary['system_info']['cpu_logical_cores']} logical cores")
    print(f"  RAM: {summary['system_info']['total_memory_gb']:.1f}GB total, {summary['system_info']['available_memory_gb']:.1f}GB available")
    print(f"  GPU: {'Available' if summary['system_info']['gpu_available'] else 'Not detected'}")
    if summary['system_info']['gpu_available']:
        print(f"       {summary['system_info']['gpu_name']} ({summary['system_info']['gpu_memory_mb']}MB)")
    print()
    
    print("Optimal Worker Counts:")
    for task, count in summary['worker_counts'].items():
        print(f"  {task.replace('_', ' ').title()}: {count}")
    print()
    
    print("Configuration files created:")
    for config_file in summary['config_files_created']:
        print(f"  {config_file}")
    print()
    
    print("Ollama Optimization Settings:")
    ollama = summary['ollama_optimization']
    print(f"  Threads: {ollama['num_thread']}")
    print(f"  GPU: {ollama['num_gpu']}")
    print(f"  Context: {ollama['num_ctx']}")
    print(f"  Batch Size: {ollama['num_batch']}")
    print(f"  Low VRAM Mode: {ollama['low_vram']}")
    print()
    
    print("Next Steps:")
    print("1. Restart Ollama with optimized settings")
    print("2. Use the generated config files in your scripts")
    print("3. Run performance tests to validate improvements")
    
    return summary

if __name__ == "__main__":
    main()