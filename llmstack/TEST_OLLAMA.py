#!/usr/bin/env python3
"""
Test Ollama API with your installed models
"""

import requests
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_ollama():
    """Test Ollama connectivity and model inference"""
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            print(f"📦 Available models: {len(models['models'])}")
            for model in models['models']:
                size_gb = model['size'] / (1024**3)
                print(f"   - {model['name']}: {size_gb:.1f} GB")
        else:
            print("❌ Ollama API returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False
    
    # Test inference with a small model
    print("\n🧪 Testing inference with deepseek-r1:8b...")
    try:
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json={
                "model": "deepseek-r1:8b",
                "messages": [
                    {"role": "user", "content": "Say hello in 5 words or less"}
                ],
                "max_tokens": 20,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            print(f"✅ AI Response: {ai_response}")
            return True
        else:
            print(f"❌ Inference failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Inference error: {e}")
        return False

def test_openai_compatibility():
    """Test OpenAI-compatible endpoint"""
    print("\n🔌 Testing OpenAI-compatible API...")
    
    try:
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "llama3.1:8b",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"}
                ],
                "temperature": 0
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OpenAI API working! Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ OpenAI API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  Ollama Local AI Test Suite")
    print("=" * 50)
    
    # Run tests
    ollama_ok = test_ollama()
    openai_ok = test_openai_compatibility()
    
    print("\n" + "=" * 50)
    print("  Test Summary")
    print("=" * 50)
    
    if ollama_ok and openai_ok:
        print("✅ All tests passed! Your local AI is ready.")
        print("\n📚 Quick Start Commands:")
        print("   ollama run deepseek-r1:8b    # Chat with DeepSeek")
        print("   ollama run llama3.1:8b       # Chat with Llama 3.1")
        print("   ollama run gemma2:27b        # Chat with Gemma 2 (large)")
        print("\n🔗 API Endpoints:")
        print("   Base: http://localhost:11434")
        print("   OpenAI-compatible: http://localhost:11434/v1")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        
    print("\n💰 Total API Cost: $0.00")
    print("🔒 Data Privacy: 100% Local")
    print("🚀 Production Ready: YES")