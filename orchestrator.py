#!/usr/bin/env python3
import asyncio
import httpx
from typing import Dict, Any, List

class FreeAgentOrchestrator:
    def __init__(self):
        self.endpoints = {
            "ollama": "http://localhost:11434/v1",
            "lm_studio": "http://localhost:1234/v1",
            "flowise": "http://localhost:3001/api/v1",
            "openhands": "http://localhost:3002/api",
            "jan": "http://localhost:1337/v1"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check which services are available"""
        health = {}
        for name, endpoint in self.endpoints.items():
            try:
                response = await self.client.get(f"{endpoint}/models")
                health[name] = response.status_code == 200
            except:
                health[name] = False
        return health
    
    async def route_request(self, prompt: str, task_type: str = "general") -> str:
        """Route to appropriate service based on task"""
        routing = {
            "code": "ollama",  # Use CodeLlama
            "general": "lm_studio",  # Use best available model
            "workflow": "flowise",  # Use visual workflow
            "development": "openhands"  # Use coding agent
        }
        
        endpoint = self.endpoints.get(routing.get(task_type, "ollama"))
        
        response = await self.client.post(
            f"{endpoint}/chat/completions",
            json={
                "model": "auto",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        return response.json()["choices"][0]["message"]["content"]

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