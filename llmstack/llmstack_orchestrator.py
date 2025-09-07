#!/usr/bin/env python3
"""
LLMStack Orchestrator - Integrates all local AI services
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMStackOrchestrator:
    """Main orchestrator for LLMStack services"""
    
    def __init__(self):
        self.services = {
            "ollama": "http://localhost:11434",
            "ollama_openai": "http://localhost:11434/v1",
            "flowise": "http://localhost:3001",
            "chroma": "http://localhost:8001",
            "grafana": "http://localhost:3003",
            "postgres": "postgresql://llmstack:llmstack_secure_password_2024@localhost:5432/llmstack",
            "redis": "redis://localhost:6379"
        }
        
        self.models = {
            "deepseek": "deepseek-r1:8b",
            "dolphin": "dolphin-mistral:latest",
            "llama": "llama3.1:8b",
            "gemma": "gemma2:27b"
        }
        
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        health_status = {}
        
        # Check Ollama
        try:
            response = await self.client.get(f"{self.services['ollama']}/api/tags")
            health_status['ollama'] = response.status_code == 200
            if health_status['ollama']:
                models = response.json().get('models', [])
                health_status['ollama_models'] = len(models)
        except:
            health_status['ollama'] = False
        
        # Check Flowise
        try:
            response = await self.client.get(self.services['flowise'])
            health_status['flowise'] = response.status_code == 200
        except:
            health_status['flowise'] = False
        
        # Check Chroma
        try:
            response = await self.client.get(f"{self.services['chroma']}/api/v2/heartbeat")
            health_status['chroma'] = response.status_code == 200
        except:
            health_status['chroma'] = False
        
        # Check Grafana
        try:
            response = await self.client.get(f"{self.services['grafana']}/api/health")
            health_status['grafana'] = response.status_code == 200
        except:
            health_status['grafana'] = False
        
        return health_status
    
    async def chat_completion(self, 
                             prompt: str, 
                             model: str = None, 
                             temperature: float = 0.7,
                             max_tokens: int = 1000) -> str:
        """Send chat completion request to Ollama"""
        
        if model is None:
            model = self.models['dolphin']  # Default to Dolphin
        elif model in self.models:
            model = self.models[model]
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = await self.client.post(
                f"{self.services['ollama_openai']}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def store_embedding(self, text: str, metadata: Dict = None) -> bool:
        """Store text embedding in Chroma"""
        try:
            # Generate embedding using Ollama
            embedding_response = await self.client.post(
                f"{self.services['ollama']}/api/embeddings",
                json={
                    "model": "llama3.1:8b",
                    "prompt": text
                }
            )
            
            if embedding_response.status_code == 200:
                embedding = embedding_response.json()['embedding']
                
                # Store in Chroma (v2 API)
                chroma_response = await self.client.post(
                    f"{self.services['chroma']}/api/v2/collections/default/add",
                    json={
                        "embeddings": [embedding],
                        "documents": [text],
                        "metadatas": [metadata or {}],
                        "ids": [str(hash(text))]
                    }
                )
                
                return chroma_response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False
    
    async def search_similar(self, query: str, n_results: int = 5) -> List[str]:
        """Search for similar documents in Chroma"""
        try:
            # Generate query embedding
            embedding_response = await self.client.post(
                f"{self.services['ollama']}/api/embeddings",
                json={
                    "model": "llama3.1:8b",
                    "prompt": query
                }
            )
            
            if embedding_response.status_code == 200:
                query_embedding = embedding_response.json()['embedding']
                
                # Search in Chroma (v2 API)
                search_response = await self.client.post(
                    f"{self.services['chroma']}/api/v2/collections/default/query",
                    json={
                        "query_embeddings": [query_embedding],
                        "n_results": n_results
                    }
                )
                
                if search_response.status_code == 200:
                    results = search_response.json()
                    return results.get('documents', [[]])[0]
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return []
    
    async def rag_query(self, question: str) -> str:
        """Perform RAG (Retrieval Augmented Generation) query"""
        # Search for relevant context
        context_docs = await self.search_similar(question, n_results=3)
        
        if context_docs:
            context = "\n".join(context_docs)
            prompt = f"""Based on the following context, answer the question.
            
Context:
{context}

Question: {question}

Answer:"""
        else:
            prompt = question
        
        # Generate response with context
        return await self.chat_completion(prompt, model='dolphin')
    
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()


async def main():
    """Test the orchestrator"""
    orchestrator = LLMStackOrchestrator()
    
    # Check health
    print("\n[*] Checking Service Health...")
    health = await orchestrator.check_health()
    for service, status in health.items():
        icon = "[OK]" if status else "[FAIL]"
        if service == 'ollama_models' and status:
            print(f"  {icon} Ollama Models: {status} available")
        else:
            print(f"  {icon} {service.capitalize()}: {'Online' if status else 'Offline'}")
    
    # Test chat completion
    print("\n[*] Testing Chat Completion...")
    response = await orchestrator.chat_completion(
        "Explain in 2 sentences what LLMStack is and why it's useful.",
        model='dolphin'
    )
    print(f"Response: {response[:200]}...")
    
    # Test embedding storage
    print("\n[*] Testing Vector Storage...")
    stored = await orchestrator.store_embedding(
        "LLMStack is a powerful platform for building AI applications",
        {"source": "test", "timestamp": "2024-01-01"}
    )
    print(f"  Storage: {'Success' if stored else 'Failed'}")
    
    # Test RAG
    print("\n[*] Testing RAG Query...")
    rag_response = await orchestrator.rag_query("What is LLMStack?")
    print(f"RAG Response: {rag_response[:200]}...")
    
    await orchestrator.close()
    
    print("\n[+] All tests complete!")


if __name__ == "__main__":
    asyncio.run(main())