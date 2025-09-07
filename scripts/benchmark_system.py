#!/usr/bin/env python3
"""
Performance benchmark script for LLMStack deployment
"""
import time
import asyncio
import httpx
import statistics
import json

async def benchmark_endpoint(endpoint: str, model: str, num_requests: int = 10):
    """Benchmark a model endpoint"""
    client = httpx.AsyncClient(timeout=30.0)
    latencies = []
    
    print(f"Benchmarking {model} at {endpoint}...")
    
    for i in range(num_requests):
        start = time.time()
        
        try:
            response = await client.post(
                f"{endpoint}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "Count to 5"}],
                    "max_tokens": 50,
                    "temperature": 0
                }
            )
            
            latency = time.time() - start
            latencies.append(latency)
            
            if response.status_code == 200:
                print(f"  Request {i+1}: {latency:.2f}s")
            else:
                print(f"  Request {i+1}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
    
    await client.aclose()
    
    if latencies:
        stats = {
            "model": model,
            "endpoint": endpoint,
            "requests": len(latencies),
            "average": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "std_dev": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
        
        print(f"\n📊 Statistics for {model}:")
        print(f"  Average: {stats['average']:.2f}s")
        print(f"  Median: {stats['median']:.2f}s")
        print(f"  Min: {stats['min']:.2f}s")
        print(f"  Max: {stats['max']:.2f}s")
        print(f"  Std Dev: {stats['std_dev']:.2f}s")
        
        return stats
    
    return None

async def system_health_check():
    """Check system health before benchmarking"""
    client = httpx.AsyncClient(timeout=5.0)
    
    services = {
        "Ollama": "http://localhost:11434/api/tags",
        "LM Studio": "http://localhost:1234/v1/models",
        "vLLM": "http://localhost:8000/v1/models",
        "LLMStack": "http://localhost:3000/api/health",
        "Flowise": "http://localhost:3001",
        "OpenHands": "http://localhost:3002/health"
    }
    
    print("🔍 System Health Check:")
    health = {}
    
    for service, url in services.items():
        try:
            response = await client.get(url)
            is_healthy = response.status_code in [200, 404]  # 404 can be OK for some endpoints
            health[service] = is_healthy
            status = "✓ Online" if is_healthy else "✗ Offline"
            print(f"  {service}: {status}")
        except:
            health[service] = False
            print(f"  {service}: ✗ Offline")
    
    await client.aclose()
    return health

async def main():
    """Main benchmark function"""
    print("=" * 60)
    print("  LLMSTACK PERFORMANCE BENCHMARK")
    print("=" * 60)
    print()
    
    # Health check first
    health = await system_health_check()
    print()
    
    # Benchmark available services
    results = []
    
    # Test Ollama models
    if health.get("Ollama", False):
        models = ["llama3.2:3b", "mistral:7b", "codellama:7b"]
        for model in models:
            try:
                result = await benchmark_endpoint("http://localhost:11434/v1", model, 5)
                if result:
                    results.append(result)
                print()
            except Exception as e:
                print(f"Error benchmarking {model}: {e}")
    
    # Test LM Studio
    if health.get("LM Studio", False):
        try:
            result = await benchmark_endpoint("http://localhost:1234/v1", "auto", 3)
            if result:
                results.append(result)
            print()
        except Exception as e:
            print(f"Error benchmarking LM Studio: {e}")
    
    # Test vLLM
    if health.get("vLLM", False):
        try:
            result = await benchmark_endpoint("http://localhost:8000/v1", "microsoft/Phi-3-mini-4k-instruct", 3)
            if result:
                results.append(result)
            print()
        except Exception as e:
            print(f"Error benchmarking vLLM: {e}")
    
    # Summary
    print("=" * 60)
    print("  BENCHMARK SUMMARY")
    print("=" * 60)
    
    if results:
        # Sort by average response time
        results.sort(key=lambda x: x['average'])
        
        print(f"{'Model':<30} {'Avg Time':<10} {'Min/Max':<12} {'Requests':<10}")
        print("-" * 60)
        
        for result in results:
            model_name = result['model'][:28]
            avg_time = f"{result['average']:.2f}s"
            min_max = f"{result['min']:.1f}/{result['max']:.1f}s"
            requests = str(result['requests'])
            
            print(f"{model_name:<30} {avg_time:<10} {min_max:<12} {requests:<10}")
        
        # Save results
        with open('benchmark_results.json', 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "health": health,
                "results": results
            }, f, indent=2)
        
        print()
        print("📁 Results saved to benchmark_results.json")
    else:
        print("No successful benchmarks completed.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())