#!/usr/bin/env python3
"""
LLMStack Performance Benchmark Script
Tests inference speed, throughput, and resource usage
"""

import time
import asyncio
import httpx
import statistics
import json
import argparse
from typing import Dict, List, Any
from datetime import datetime
import psutil
import concurrent.futures

class LLMStackBenchmark:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.endpoints = {
            "ollama": "http://localhost:11434/v1",
            "lm_studio": "http://localhost:1234/v1",
            "vllm": "http://localhost:8000/v1",
            "jan": "http://localhost:1337/v1"
        }
        self.results = {}
        
    async def check_endpoint_health(self, name: str, endpoint: str) -> bool:
        """Check if an endpoint is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{endpoint}/models")
                return response.status_code == 200
        except:
            return False
    
    async def benchmark_latency(
        self, 
        endpoint: str, 
        model: str, 
        prompt: str,
        num_requests: int = 10
    ) -> Dict[str, float]:
        """Benchmark latency for a single endpoint"""
        latencies = []
        errors = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                try:
                    start = time.time()
                    
                    response = await client.post(
                        f"{endpoint}/chat/completions",
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 50,
                            "temperature": 0,
                            "stream": False
                        }
                    )
                    
                    latency = time.time() - start
                    
                    if response.status_code == 200:
                        latencies.append(latency)
                        if self.verbose:
                            print(f"  Request {i+1}/{num_requests}: {latency:.2f}s")
                    else:
                        errors += 1
                        if self.verbose:
                            print(f"  Request {i+1}/{num_requests}: Failed (HTTP {response.status_code})")
                            
                except Exception as e:
                    errors += 1
                    if self.verbose:
                        print(f"  Request {i+1}/{num_requests}: Error - {str(e)}")
        
        if latencies:
            return {
                "avg_latency": statistics.mean(latencies),
                "median_latency": statistics.median(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0],
                "success_rate": (len(latencies) / num_requests) * 100,
                "errors": errors
            }
        else:
            return {"errors": errors, "success_rate": 0}
    
    async def benchmark_throughput(
        self,
        endpoint: str,
        model: str,
        concurrent_requests: int = 5
    ) -> Dict[str, float]:
        """Benchmark throughput with concurrent requests"""
        prompts = [
            "Write a haiku about programming",
            "Explain quantum computing in simple terms",
            "What is the meaning of life?",
            "Generate a Python function to sort a list",
            "Describe the water cycle"
        ] * (concurrent_requests // 5 + 1)
        
        prompts = prompts[:concurrent_requests]
        
        start_time = time.time()
        tasks = []
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for prompt in prompts:
                task = client.post(
                    f"{endpoint}/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 50,
                        "temperature": 0.7
                    }
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        
        return {
            "total_time": total_time,
            "requests_per_second": successful / total_time if total_time > 0 else 0,
            "successful_requests": successful,
            "failed_requests": concurrent_requests - successful,
            "avg_time_per_request": total_time / successful if successful > 0 else 0
        }
    
    def benchmark_resources(self) -> Dict[str, Any]:
        """Benchmark system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get Docker container stats if possible
        docker_stats = {}
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        stat = json.loads(line)
                        docker_stats[stat['Name']] = {
                            'cpu': stat['CPUPerc'],
                            'memory': stat['MemUsage']
                        }
        except:
            pass
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "docker_stats": docker_stats
        }
    
    async def run_comprehensive_benchmark(self):
        """Run complete benchmark suite"""
        print("=" * 60)
        print("LLMStack Comprehensive Performance Benchmark")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check available endpoints
        print("Checking available endpoints...")
        available_endpoints = {}
        
        for name, endpoint in self.endpoints.items():
            if await self.check_endpoint_health(name, endpoint):
                available_endpoints[name] = endpoint
                print(f"  ✓ {name}: Available")
            else:
                print(f"  ✗ {name}: Not available")
        
        if not available_endpoints:
            print("\nNo endpoints available for benchmarking!")
            return
        
        print("\n" + "=" * 60)
        
        # Benchmark configurations
        test_configs = [
            {
                "name": "Simple Query",
                "prompt": "Hello, how are you?",
                "requests": 5
            },
            {
                "name": "Code Generation",
                "prompt": "Write a Python function to calculate fibonacci numbers",
                "requests": 3
            },
            {
                "name": "Complex Reasoning",
                "prompt": "Explain the implications of artificial general intelligence on society, economy, and human purpose",
                "requests": 3
            }
        ]
        
        # Run benchmarks for each endpoint
        for endpoint_name, endpoint_url in available_endpoints.items():
            print(f"\nBenchmarking: {endpoint_name}")
            print("-" * 40)
            
            # Determine model to use
            if endpoint_name == "ollama":
                model = "llama3.2:3b"
            elif endpoint_name == "lm_studio":
                model = "auto"
            else:
                model = "default"
            
            endpoint_results = {}
            
            # Latency benchmarks
            for config in test_configs:
                print(f"\nTest: {config['name']}")
                latency_results = await self.benchmark_latency(
                    endpoint_url,
                    model,
                    config['prompt'],
                    config['requests']
                )
                
                if latency_results.get('success_rate', 0) > 0:
                    print(f"  Average latency: {latency_results.get('avg_latency', 0):.2f}s")
                    print(f"  Median latency:  {latency_results.get('median_latency', 0):.2f}s")
                    print(f"  Min/Max:         {latency_results.get('min_latency', 0):.2f}s / {latency_results.get('max_latency', 0):.2f}s")
                    print(f"  Success rate:    {latency_results.get('success_rate', 0):.1f}%")
                else:
                    print(f"  All requests failed")
                
                endpoint_results[config['name']] = latency_results
            
            # Throughput benchmark
            print(f"\nThroughput Test (5 concurrent requests)")
            throughput_results = await self.benchmark_throughput(endpoint_url, model, 5)
            print(f"  Requests/second: {throughput_results['requests_per_second']:.2f}")
            print(f"  Total time:      {throughput_results['total_time']:.2f}s")
            print(f"  Success/Failed:  {throughput_results['successful_requests']}/{throughput_results['failed_requests']}")
            
            endpoint_results['throughput'] = throughput_results
            self.results[endpoint_name] = endpoint_results
        
        # System resources
        print("\n" + "=" * 60)
        print("System Resource Usage")
        print("-" * 40)
        resources = self.benchmark_resources()
        print(f"CPU Usage:        {resources['cpu_percent']:.1f}%")
        print(f"Memory Usage:     {resources['memory_percent']:.1f}%")
        print(f"Memory Available: {resources['memory_available_gb']:.2f} GB")
        print(f"Disk Free:        {resources['disk_free_gb']:.2f} GB")
        
        if resources['docker_stats']:
            print("\nDocker Container Stats:")
            for container, stats in resources['docker_stats'].items():
                if 'llmstack' in container.lower():
                    print(f"  {container}: CPU {stats['cpu']}, Memory {stats['memory']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("Benchmark Summary")
        print("=" * 60)
        
        best_latency = float('inf')
        best_endpoint = None
        
        for endpoint, results in self.results.items():
            avg_latencies = []
            for test_name, test_results in results.items():
                if test_name != 'throughput' and 'avg_latency' in test_results:
                    avg_latencies.append(test_results['avg_latency'])
            
            if avg_latencies:
                overall_avg = statistics.mean(avg_latencies)
                print(f"{endpoint}: Average latency {overall_avg:.2f}s")
                
                if overall_avg < best_latency:
                    best_latency = overall_avg
                    best_endpoint = endpoint
        
        if best_endpoint:
            print(f"\nBest performing endpoint: {best_endpoint} ({best_latency:.2f}s avg latency)")
        
        print(f"\nBenchmark completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results to file
        output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
                "resources": resources
            }, f, indent=2)
        print(f"\nResults saved to: {output_file}")

async def main():
    parser = argparse.ArgumentParser(description='LLMStack Performance Benchmark')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark only')
    
    args = parser.parse_args()
    
    benchmark = LLMStackBenchmark(verbose=args.verbose)
    
    if args.quick:
        # Quick test
        print("Running quick benchmark...")
        result = await benchmark.benchmark_latency(
            "http://localhost:11434/v1",
            "llama3.2:3b",
            "Hello, how are you?",
            3
        )
        print(f"Average latency: {result.get('avg_latency', 0):.2f}s")
    else:
        await benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    asyncio.run(main())