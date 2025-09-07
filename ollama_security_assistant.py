#!/usr/bin/env python3
"""
Ollama Security Research Assistant
Uses locally installed models for security analysis
"""

import subprocess
import json
import sys
from pathlib import Path


class OllamaSecurityAssistant:
    """Security research using local Ollama models"""
    
    def __init__(self):
        self.models = self.get_available_models()
        self.current_model = None
        
    def get_available_models(self):
        """Get list of installed models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                return models
            return []
        except:
            return []
    
    def query_model(self, prompt, model=None):
        """Send query to Ollama model"""
        if not model:
            model = self.current_model or self.models[0] if self.models else "llama3.1:8b"
        
        try:
            result = subprocess.run(
                ['ollama', 'run', model, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Query timed out. Try a simpler question."
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_security_code(self, code):
        """Analyze code for security vulnerabilities"""
        prompt = f"""Analyze this code for security vulnerabilities:

{code}

Identify:
1. Security vulnerabilities
2. Risk level (Critical/High/Medium/Low)
3. How to exploit (for defensive understanding)
4. How to fix the vulnerability
5. Best practices to prevent this issue"""
        
        return self.query_model(prompt)
    
    def explain_vulnerability(self, vuln_type):
        """Explain a vulnerability in detail"""
        prompt = f"""Explain {vuln_type} vulnerability:

1. What is it?
2. How does it work?
3. Common attack vectors
4. Real-world impact
5. Detection methods
6. Prevention techniques
7. Example vulnerable code
8. Example secure code

Provide practical, actionable information for security testing."""
        
        return self.query_model(prompt)
    
    def generate_security_test(self, target_type):
        """Generate security testing checklist"""
        prompt = f"""Create a comprehensive security testing checklist for {target_type}:

Include:
- Reconnaissance phase
- Vulnerability scanning
- Common vulnerabilities to test
- Authentication/Authorization tests
- Input validation tests
- Business logic tests
- Tools to use
- Reporting guidelines

Format as a practical checklist for authorized penetration testing."""
        
        return self.query_model(prompt)
    
    def exploit_development_help(self, vulnerability):
        """Help understand exploit development (educational)"""
        prompt = f"""For educational/defensive purposes, explain how to develop an exploit for {vulnerability}:

1. Technical requirements
2. Step-by-step process
3. Common pitfalls
4. Detection evasion techniques
5. Mitigation strategies

This is for understanding attack methods to build better defenses."""
        
        return self.query_model(prompt)


def interactive_mode():
    """Interactive security research mode"""
    print("=" * 60)
    print("OLLAMA SECURITY RESEARCH ASSISTANT")
    print("=" * 60)
    
    assistant = OllamaSecurityAssistant()
    
    if not assistant.models:
        print("[-] No Ollama models found. Install with:")
        print("    ollama pull llama3.1")
        return
    
    print(f"\n[+] Available models: {', '.join(assistant.models)}")
    assistant.current_model = assistant.models[0]
    print(f"[*] Using model: {assistant.current_model}\n")
    
    while True:
        print("\n" + "=" * 60)
        print("OPTIONS:")
        print("1. Analyze code for vulnerabilities")
        print("2. Explain vulnerability type")
        print("3. Generate security test checklist")
        print("4. Understand exploit development")
        print("5. Custom security question")
        print("6. Change model")
        print("7. Exit")
        print("=" * 60)
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            print("\nPaste code to analyze (end with 'END' on new line):")
            code_lines = []
            while True:
                line = input()
                if line == "END":
                    break
                code_lines.append(line)
            
            code = "\n".join(code_lines)
            print("\n[*] Analyzing code for vulnerabilities...")
            result = assistant.analyze_security_code(code)
            print("\n" + "=" * 40)
            print(result)
            
        elif choice == "2":
            vuln = input("\nEnter vulnerability type (e.g., XSS, SQLi, RCE): ")
            print(f"\n[*] Explaining {vuln}...")
            result = assistant.explain_vulnerability(vuln)
            print("\n" + "=" * 40)
            print(result)
            
        elif choice == "3":
            target = input("\nEnter target type (e.g., web app, API, network): ")
            print(f"\n[*] Generating security checklist for {target}...")
            result = assistant.generate_security_test(target)
            print("\n" + "=" * 40)
            print(result)
            
        elif choice == "4":
            vuln = input("\nEnter vulnerability to understand (e.g., buffer overflow): ")
            print(f"\n[*] Explaining exploit development for {vuln}...")
            result = assistant.exploit_development_help(vuln)
            print("\n" + "=" * 40)
            print(result)
            
        elif choice == "5":
            question = input("\nEnter your security question: ")
            print("\n[*] Processing question...")
            result = assistant.query_model(question)
            print("\n" + "=" * 40)
            print(result)
            
        elif choice == "6":
            print(f"\nAvailable models: {', '.join(assistant.models)}")
            model = input("Enter model name: ").strip()
            if model in assistant.models:
                assistant.current_model = model
                print(f"[+] Switched to {model}")
            else:
                print("[-] Model not found")
                
        elif choice == "7":
            print("\n[*] Exiting...")
            break
        
        else:
            print("[-] Invalid option")


def batch_mode(queries):
    """Batch processing mode"""
    assistant = OllamaSecurityAssistant()
    
    if not assistant.models:
        print("[-] No models available")
        return
    
    results = []
    for query in queries:
        print(f"[*] Processing: {query[:50]}...")
        result = assistant.query_model(query)
        results.append({
            "query": query,
            "response": result
        })
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama Security Research Assistant")
    parser.add_argument("-q", "--query", help="Single query to run")
    parser.add_argument("-f", "--file", help="File with queries (one per line)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.query:
        assistant = OllamaSecurityAssistant()
        result = assistant.query_model(args.query)
        print(result)
        
    elif args.file:
        queries = Path(args.file).read_text().strip().split('\n')
        results = batch_mode(queries)
        for r in results:
            print(f"\nQ: {r['query']}")
            print(f"A: {r['response'][:500]}...")
            
    else:
        interactive_mode()


if __name__ == "__main__":
    main()