#!/usr/bin/env python3
"""
LLMStack - Complete Local AI Platform
Zero API Costs | 100% Local | Production Ready
"""

import asyncio
import sys
import argparse
from pathlib import Path
import logging

# Import our orchestrator
from llmstack_orchestrator import LLMStackOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LLMStackCLI:
    """Command-line interface for LLMStack"""
    
    def __init__(self):
        self.orchestrator = LLMStackOrchestrator()
    
    async def health_check(self):
        """Check health of all services"""
        print("\n[*] LLMStack Health Check")
        print("=" * 40)
        
        health = await self.orchestrator.check_health()
        all_healthy = True
        
        for service, status in health.items():
            icon = "[OK]" if status else "[FAIL]"
            if service == 'ollama_models' and status:
                print(f"  {icon} Ollama Models: {status} available")
            else:
                print(f"  {icon} {service.capitalize()}: {'Online' if status else 'Offline'}")
            
            if not status and service != 'ollama_models':
                all_healthy = False
        
        print()
        if all_healthy:
            print("[SUCCESS] All services are healthy!")
        else:
            print("[WARNING] Some services are offline. Check Docker containers.")
        
        return all_healthy
    
    async def interactive_chat(self, model_name="dolphin"):
        """Start interactive chat session"""
        print(f"\n[*] Starting interactive chat with {model_name}")
        print("Type 'exit' to quit, 'help' for commands")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("""
Available commands:
  help - Show this help
  exit - Exit chat
  /model <name> - Switch model (e.g., /model llama)
  /rag <query> - RAG query with context
                    """)
                    continue
                
                if user_input.startswith('/model '):
                    model_name = user_input[7:].strip()
                    print(f"Switched to model: {model_name}")
                    continue
                
                if user_input.startswith('/rag '):
                    query = user_input[5:].strip()
                    print("AI (RAG): ", end="")
                    response = await self.orchestrator.rag_query(query)
                    print(response)
                    continue
                
                if not user_input:
                    continue
                
                print("AI: ", end="")
                response = await self.orchestrator.chat_completion(
                    user_input, model=model_name, temperature=0.7
                )
                print(response)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def benchmark_models(self):
        """Benchmark available models"""
        print("\n[*] Model Benchmark")
        print("=" * 40)
        
        test_prompt = "Explain quantum computing in exactly 2 sentences."
        models = ['dolphin', 'deepseek', 'llama', 'gemma']
        
        for model in models:
            try:
                print(f"\nTesting {model}...")
                import time
                start_time = time.time()
                
                response = await self.orchestrator.chat_completion(
                    test_prompt, model=model, max_tokens=100
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  Response time: {duration:.2f}s")
                print(f"  Response: {response[:100]}...")
                
            except Exception as e:
                print(f"  Error with {model}: {e}")
    
    async def setup_rag_demo(self):
        """Set up RAG demo with sample documents"""
        print("\n[*] Setting up RAG Demo")
        print("=" * 40)
        
        documents = [
            "LLMStack is a comprehensive local AI platform that runs entirely on your machine without requiring external API calls.",
            "The platform includes Ollama for local language models, Chroma for vector storage, and Flowise for visual workflow building.",
            "All components are dockerized for easy deployment and can run on both CPU and GPU systems.",
            "The orchestrator manages communication between all services including health checks and API routing.",
            "Vector storage enables semantic search and retrieval-augmented generation for enhanced AI responses."
        ]
        
        print(f"Storing {len(documents)} documents in vector database...")
        
        success_count = 0
        for i, doc in enumerate(documents):
            stored = await self.orchestrator.store_embedding(
                doc, {"source": "demo", "doc_id": i}
            )
            if stored:
                success_count += 1
                print(f"  [OK] Document {i+1} stored")
            else:
                print(f"  [FAIL] Document {i+1} failed")
        
        print(f"\nStored {success_count}/{len(documents)} documents successfully")
        
        if success_count > 0:
            print("\nTesting RAG query...")
            response = await self.orchestrator.rag_query("What is LLMStack?")
            print(f"RAG Response: {response[:200]}...")
    
    async def run_demo(self):
        """Run a complete demonstration"""
        print("\n[*] LLMStack Complete Demo")
        print("=" * 50)
        
        # Health check
        healthy = await self.health_check()
        if not healthy:
            print("Some services are offline. Demo may not work fully.")
            return
        
        # Chat test
        print("\n[*] Testing Chat Completion...")
        response = await self.orchestrator.chat_completion(
            "Introduce yourself as LLMStack AI Assistant in 2 sentences.",
            model='dolphin'
        )
        print(f"Response: {response}")
        
        # RAG setup and test
        await self.setup_rag_demo()
        
        print("\n[SUCCESS] Demo completed! Try the interactive chat with:")
        print("  python main.py chat")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.orchestrator.close()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LLMStack - Complete Local AI Platform")
    parser.add_argument('command', nargs='?', default='demo', 
                       choices=['demo', 'health', 'chat', 'benchmark', 'rag-setup'],
                       help='Command to run')
    parser.add_argument('--model', default='dolphin', help='Model to use for chat')
    
    args = parser.parse_args()
    
    cli = LLMStackCLI()
    
    try:
        if args.command == 'health':
            await cli.health_check()
        elif args.command == 'chat':
            await cli.interactive_chat(args.model)
        elif args.command == 'benchmark':
            await cli.benchmark_models()
        elif args.command == 'rag-setup':
            await cli.setup_rag_demo()
        elif args.command == 'demo':
            await cli.run_demo()
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        await cli.cleanup()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)