#!/usr/bin/env python3
"""
Interactive Ollama Chat Demo
"""

import requests
import json

def chat_with_ollama(model="deepseek-r1:8b"):
    """Interactive chat with Ollama models"""
    
    print(f"\n🤖 Chatting with {model}")
    print("Type 'exit' to quit, 'switch' to change model\n")
    
    messages = []
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'switch':
            print("\nAvailable models:")
            print("1. deepseek-r1:8b (reasoning)")
            print("2. llama3.1:8b (general)")
            print("3. dolphin-mistral:latest (coding)")
            choice = input("Select (1-3): ")
            models = {
                "1": "deepseek-r1:8b",
                "2": "llama3.1:8b", 
                "3": "dolphin-mistral:latest"
            }
            model = models.get(choice, model)
            print(f"Switched to {model}\n")
            messages = []  # Clear context
            continue
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Get AI response
        print("AI: ", end="", flush=True)
        
        try:
            response = requests.post(
                "http://localhost:11434/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "stream": True
                },
                stream=True
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse streaming response
                        json_str = line.decode('utf-8').replace('data: ', '')
                        if json_str == '[DONE]':
                            break
                        data = json.loads(json_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            print(content, end="", flush=True)
                            full_response += content
                    except:
                        pass
            
            print("\n")  # New line after response
            
            # Add assistant response to history
            messages.append({"role": "assistant", "content": full_response})
            
            # Keep conversation manageable (last 10 exchanges)
            if len(messages) > 20:
                messages = messages[-20:]
                
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("   Ollama Interactive Chat Demo")
    print("=" * 50)
    
    # Show available models
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()["models"]
            print("\nAvailable models:")
            for i, model in enumerate(models, 1):
                size_gb = model['size'] / (1024**3)
                print(f"{i}. {model['name']} ({size_gb:.1f} GB)")
    except:
        print("Could not fetch models")
    
    chat_with_ollama()