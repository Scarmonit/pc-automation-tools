#!/usr/bin/env python3
import time
import asyncio
import httpx
import statistics

async def benchmark_endpoint(endpoint: str, model: str, num_requests: int = 10):
    """Benchmark a model endpoint"""
    client = httpx.AsyncClient(timeout=30.0)
    latencies = []

    for i in range(num_requests):
        start = time.time()

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
            print(f"  Request {i+1}: Failed")

    if latencies:
        print(f"\nStatistics for {model}:")
        print(f"  Average: {statistics.mean(latencies):.2f}s")
        print(f"  Median: {statistics.median(latencies):.2f}s")
        print(f"  Min: {min(latencies):.2f}s")
        print(f"  Max: {max(latencies):.2f}s")

async def main():
    print("=== Performance Benchmark ===\n")

    # Test Ollama
    print("Testing Ollama (llama3.2:3b)...")
    await benchmark_endpoint("http://localhost:11434/v1", "llama3.2:3b", 5)

    print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
