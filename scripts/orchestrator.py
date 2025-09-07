#!/usr/bin/env python3
import asyncio
import httpx
from typing import Dict, Any, List

class FreeAgentOrchestrator:
    def __init__(self):
        self.endpoints = {
            "ollama": "http://localhost:11434/v1",
            "flowise": "http://localhost:3001/api/v1",
            "openhands": "http://localhost:3002/api",
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check which services are available"""
        health = {}
        for name, endpoint in self.endpoints.items():
            try:
                if name == "ollama":
                    response = await self.client.get(f"http://localhost:11434/api/tags")
                else:
                    response = await self.client.get(f"{endpoint}/models")
                health[name] = response.status_code == 200
            except:
                health[name] = False
        return health
    
    async def route_request(self, prompt: str, task_type: str = "general") -> str:
        """Route to appropriate service based on task"""
        routing = {
            "code": "ollama",  # Use CodeLlama
            "general": "ollama",  # Use best available model
            "workflow": "flowise",  # Use visual workflow
            "development": "openhands"  # Use coding agent
        }
        
        service = routing.get(task_type, "ollama")
        
        if service == "ollama":
            response = await self.client.post(
                "http://localhost:11434/v1/chat/completions",
                json={
                    "model": "llama3.2:3b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code}"
        
        return f"Service {service} not yet implemented in orchestrator"

# Test orchestrator
async def test():
    orchestrator = FreeAgentOrchestrator()
    health = await orchestrator.check_health()
    print("Service Health:", health)
    
    # Test routing
    response = await orchestrator.route_request(
        "Write a Python function to calculate fibonacci",
        task_type="code"
    )
    print("Response:", response[:200])

if __name__ == "__main__":
    asyncio.run(test())