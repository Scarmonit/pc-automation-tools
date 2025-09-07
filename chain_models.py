#!/usr/bin/env python3
"""
Chain multiple models for enhanced reasoning
"""
import subprocess
import json

def query_model(prompt, model):
    """Query a specific model"""
    result = subprocess.run(
        ['ollama', 'run', model, prompt],
        capture_output=True,
        text=True
    )
    return result.stdout

def enhanced_query(question):
    """Use multiple models to enhance answer"""
    
    # Step 1: Get initial analysis from Dolphin
    print("[1/3] Initial analysis...")
    initial = query_model(
        f"Analyze this security question and identify key concepts: {question}",
        "dolphin-mistral"
    )
    
    # Step 2: Get detailed technical answer
    print("[2/3] Detailed response...")
    detailed = query_model(
        f"Given this context: {initial[:500]}\n\nProvide detailed answer to: {question}",
        "dolphin-mistral"
    )
    
    # Step 3: Get code examples if available from codellama
    print("[3/3] Code examples...")
    code = query_model(
        f"Provide code examples for: {question}",
        "codellama" if "codellama" in get_models() else "dolphin-mistral"
    )
    
    # Combine responses
    return f"""
ENHANCED RESPONSE:
{'='*60}

ANALYSIS:
{initial}

DETAILED EXPLANATION:
{detailed}

CODE EXAMPLES:
{code}
"""

def get_models():
    """Get list of available models"""
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    return result.stdout

# Usage
if __name__ == "__main__":
    question = input("Enter security question: ")
    print(enhanced_query(question))
