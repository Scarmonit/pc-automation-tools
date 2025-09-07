#!/usr/bin/env python3
"""
Simple Orchestrator - Routes requests to appropriate AI services
"""

import asyncio
import httpx
from typing import Dict, Any, List
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class FreeAgentOrchestrator:
    def __init__(self):
        self.endpoints = {
            "ollama": "http://localhost:11434/v1",
            "flowise": "http://localhost:3001/api/v1",
            "openhands": "http://localhost:3002/api",
            "grafana": "http://localhost:3003",
            "prometheus": "http://localhost:9090"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check which services are available"""
        health = {}
        
        # Check Ollama
        try:
            response = await self.client.get(f"{self.endpoints['ollama']}/models")
            health["ollama"] = response.status_code == 200
        except:
            health["ollama"] = False
        
        # Check Flowise
        try:
            response = await self.client.get("http://localhost:3001")
            health["flowise"] = response.status_code == 200
        except:
            health["flowise"] = False
        
        # Check OpenHands
        try:
            response = await self.client.get("http://localhost:3002/health")
            health["openhands"] = response.status_code == 200
        except:
            health["openhands"] = False
        
        # Check Grafana
        try:
            response = await self.client.get("http://localhost:3003/api/health")
            health["grafana"] = response.status_code == 200
        except:
            health["grafana"] = False
        
        # Check Prometheus
        try:
            response = await self.client.get("http://localhost:9090/-/ready")
            health["prometheus"] = response.status_code == 200
        except:
            health["prometheus"] = False
        
        return health
    
    async def route_request(self, prompt: str, task_type: str = "general") -> str:
        """Route to appropriate service based on task"""
        routing = {
            "code": "ollama",  # Use dolphin-mistral for code
            "reasoning": "ollama",  # Use deepseek-r1 for reasoning
            "general": "ollama",  # Use llama3.1 for general
            "workflow": "flowise",  # Use visual workflow
            "development": "openhands"  # Use coding agent
        }
        
        endpoint = self.endpoints.get(routing.get(task_type, "ollama"))
        
        # Select model based on task type
        model_map = {
            "code": "dolphin-mistral:latest",
            "reasoning": "deepseek-r1:8b",
            "general": "llama3.1:8b"
        }
        
        model = model_map.get(task_type, "llama3.1:8b")
        
        try:
            response = await self.client.post(
                f"{endpoint}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def list_models(self) -> List[str]:
        """List available models from Ollama"""
        try:
            response = await self.client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json()["models"]
                return [m["name"] for m in models]
        except:
            pass
        return []
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()

# Test orchestrator
async def test():
    orchestrator = FreeAgentOrchestrator()
    
    print("=" * 50)
    print("  Free Agent Orchestrator Test")
    print("=" * 50)
    
    # Check health
    print("\nChecking service health...")
    health = await orchestrator.check_health()
    for service, status in health.items():
        status_emoji = "[OK]" if status else "[X]"
        print(f"  {status_emoji} {service}: {'Online' if status else 'Offline'}")
    
    # List models
    print("\nAvailable models:")
    models = await orchestrator.list_models()
    for model in models:
        print(f"  - {model}")
    
    # Test routing
    if health.get("ollama"):
        print("\nTesting inference routing...")
        
        # Test general query
        print("\n1. General query:")
        response = await orchestrator.route_request(
            "What is 2+2?",
            task_type="general"
        )
        print(f"   Response: {response[:100]}...")
        
        # Test code query
        print("\n2. Code query:")
        response = await orchestrator.route_request(
            "Write a Python hello world function",
            task_type="code"
        )
        print(f"   Response: {response[:100]}...")
    
    await orchestrator.close()
    
    print("\n" + "=" * 50)
    print("  Orchestrator test complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())