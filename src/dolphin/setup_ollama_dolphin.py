#!/usr/bin/env python3
"""
Ollama + Dolphin-Mistral Setup Script
Sets up local uncensored AI model for security research
"""

import os
import sys
import subprocess
import platform
import json
import requests
import time
from pathlib import Path


class OllamaSetup:
    """Setup and configure Ollama with Dolphin model"""
    
    def __init__(self):
        self.system = platform.system()
        self.ollama_installed = False
        self.models = []
        
    def check_ollama_installed(self):
        """Check if Ollama is already installed"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[+] Ollama is already installed")
                version = result.stdout.strip()
                print(f"    Version: {version}")
                self.ollama_installed = True
                return True
        except FileNotFoundError:
            print("[-] Ollama not found")
            return False
        except Exception as e:
            print(f"[-] Error checking Ollama: {e}")
            return False
    
    def install_ollama_windows(self):
        """Install Ollama on Windows"""
        print("\n[*] Installing Ollama for Windows...")
        
        # Download URL for Windows
        download_url = "https://ollama.ai/download/OllamaSetup.exe"
        installer_path = Path.home() / "Downloads" / "OllamaSetup.exe"
        
        print(f"[*] Downloading from: {download_url}")
        print(f"[*] Saving to: {installer_path}")
        
        # Create PowerShell script for installation
        ps_script = """
# Download Ollama installer
$url = "https://ollama.ai/download/OllamaSetup.exe"
$output = "$env:USERPROFILE\\Downloads\\OllamaSetup.exe"

Write-Host "[*] Downloading Ollama installer..."
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "[*] Installer downloaded to: $output"
Write-Host "[!] Please run the installer manually:"
Write-Host "    1. Go to your Downloads folder"
Write-Host "    2. Run OllamaSetup.exe"
Write-Host "    3. Follow the installation wizard"
Write-Host "    4. After installation, run this script again"

# Check if we should auto-start installer
$response = Read-Host "Do you want to start the installer now? (y/n)"
if ($response -eq 'y') {
    Start-Process $output
}
"""
        
        ps_file = Path("install_ollama.ps1")
        ps_file.write_text(ps_script)
        
        print("\n[!] Windows installation requires manual steps:")
        print("    1. Run PowerShell as Administrator")
        print(f"    2. Execute: .\\{ps_file}")
        print("    3. Follow the installer")
        print("    4. Run this script again after installation")
        
        return False
    
    def install_ollama_linux(self):
        """Install Ollama on Linux/WSL"""
        print("\n[*] Installing Ollama for Linux/WSL...")
        
        install_script = """
curl -fsSL https://ollama.ai/install.sh | sh
"""
        
        print("[*] Running installation command...")
        result = subprocess.run(install_script, shell=True, 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Ollama installed successfully")
            return True
        else:
            print(f"[-] Installation failed: {result.stderr}")
            return False
    
    def start_ollama_service(self):
        """Start Ollama service"""
        print("\n[*] Starting Ollama service...")
        
        if self.system == "Windows":
            # Windows - Ollama runs as service automatically
            print("[*] On Windows, Ollama starts automatically")
            return True
        else:
            # Linux/Mac - Start service
            try:
                subprocess.Popen(['ollama', 'serve'], 
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                time.sleep(3)  # Wait for service to start
                print("[+] Ollama service started")
                return True
            except Exception as e:
                print(f"[-] Failed to start service: {e}")
                return False
    
    def list_available_models(self):
        """List available models"""
        print("\n[*] Available Models:")
        
        models = [
            {"name": "dolphin-mistral", "size": "7B", "description": "Uncensored Mistral fine-tune"},
            {"name": "dolphin-llama2", "size": "7B", "description": "Uncensored Llama2 fine-tune"},
            {"name": "wizard-uncensored", "size": "13B", "description": "Uncensored WizardLM"},
            {"name": "mistral", "size": "7B", "description": "Base Mistral model"},
            {"name": "llama2-uncensored", "size": "7B", "description": "Uncensored Llama2"},
            {"name": "codellama", "size": "7B", "description": "Code-focused model"},
        ]
        
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['name']} ({model['size']}) - {model['description']}")
        
        return models
    
    def pull_model(self, model_name):
        """Pull/download a model"""
        print(f"\n[*] Downloading model: {model_name}")
        print("[!] This may take several minutes (4-7GB download)...")
        
        try:
            result = subprocess.run(['ollama', 'pull', model_name],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Model {model_name} downloaded successfully")
                return True
            else:
                print(f"[-] Failed to download: {result.stderr}")
                return False
        except Exception as e:
            print(f"[-] Error pulling model: {e}")
            return False
    
    def test_model(self, model_name):
        """Test the model with a simple prompt"""
        print(f"\n[*] Testing model: {model_name}")
        
        test_prompt = "What is cybersecurity?"
        
        try:
            result = subprocess.run(
                ['ollama', 'run', model_name, test_prompt],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                print("[+] Model test successful!")
                print("\nSample output:")
                print("-" * 50)
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
                print("-" * 50)
                return True
            else:
                print(f"[-] Model test failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("[-] Model test timed out")
            return False
        except Exception as e:
            print(f"[-] Error testing model: {e}")
            return False
    
    def create_security_research_script(self):
        """Create a script for security research with Dolphin"""
        script_content = '''#!/usr/bin/env python3
"""
Security Research Assistant using Dolphin-Mistral
For authorized testing and research only
"""

import subprocess
import json

class DolphinSecurityResearch:
    def __init__(self, model="dolphin-mistral"):
        self.model = model
        
    def query(self, prompt):
        """Send a query to the model"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True, text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_code(self, code):
        """Analyze code for security issues"""
        prompt = f"""Analyze this code for security vulnerabilities:

{code}

Identify any security issues, explain the risk, and suggest fixes."""
        return self.query(prompt)
    
    def explain_vulnerability(self, vuln_type):
        """Explain a vulnerability type"""
        prompt = f"""Explain the {vuln_type} vulnerability:
1. How it works
2. How to identify it
3. How to prevent it
4. Example vulnerable code
5. Example secure code"""
        return self.query(prompt)
    
    def penetration_test_checklist(self, target_type):
        """Generate a penetration testing checklist"""
        prompt = f"""Create a penetration testing checklist for {target_type}.
Include:
- Information gathering steps
- Common vulnerabilities to check
- Tools to use
- Reporting requirements
Note: For authorized testing only."""
        return self.query(prompt)

def main():
    print("=" * 60)
    print("DOLPHIN SECURITY RESEARCH ASSISTANT")
    print("For authorized testing and educational purposes only")
    print("=" * 60)
    
    assistant = DolphinSecurityResearch()
    
    while True:
        print("\\nOptions:")
        print("1. Analyze code for vulnerabilities")
        print("2. Explain a vulnerability type")
        print("3. Generate pentest checklist")
        print("4. Custom security question")
        print("5. Exit")
        
        choice = input("\\nSelect option (1-5): ")
        
        if choice == "1":
            print("Paste your code (end with 'END' on a new line):")
            code_lines = []
            while True:
                line = input()
                if line == "END":
                    break
                code_lines.append(line)
            code = "\\n".join(code_lines)
            print("\\nAnalyzing...")
            result = assistant.analyze_code(code)
            print(result)
            
        elif choice == "2":
            vuln = input("Enter vulnerability type (e.g., SQL Injection, XSS): ")
            print("\\nExplaining...")
            result = assistant.explain_vulnerability(vuln)
            print(result)
            
        elif choice == "3":
            target = input("Enter target type (e.g., web app, API, network): ")
            print("\\nGenerating checklist...")
            result = assistant.penetration_test_checklist(target)
            print(result)
            
        elif choice == "4":
            question = input("Enter your security question: ")
            print("\\nProcessing...")
            result = assistant.query(question)
            print(result)
            
        elif choice == "5":
            print("Exiting...")
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
'''
        
        script_path = Path("dolphin_security_research.py")
        script_path.write_text(script_content)
        print(f"\n[+] Created security research script: {script_path}")
        return script_path
    
    def setup_complete(self):
        """Complete setup process"""
        print("\n" + "=" * 60)
        print("OLLAMA + DOLPHIN SETUP COMPLETE")
        print("=" * 60)
        
        print("\n[*] Quick Start Commands:")
        print("-" * 40)
        print("1. Chat with Dolphin:")
        print("   ollama run dolphin-mistral")
        print("\n2. Use in Python:")
        print("   python dolphin_security_research.py")
        print("\n3. API Usage:")
        print("   curl http://localhost:11434/api/generate -d '{")
        print('     "model": "dolphin-mistral",')
        print('     "prompt": "your question here"')
        print("   }'")
        
        print("\n[!] IMPORTANT REMINDERS:")
        print("-" * 40)
        print("• This is for authorized security testing only")
        print("• You are responsible for how you use this tool")
        print("• Always get written permission before testing")
        print("• Follow responsible disclosure practices")
        print("• Uncensored ≠ Unlimited knowledge")
        

def main():
    """Main setup process"""
    print("=" * 60)
    print("OLLAMA + DOLPHIN-MISTRAL SETUP")
    print("Uncensored AI for Security Research")
    print("=" * 60)
    
    setup = OllamaSetup()
    
    # Step 1: Check/Install Ollama
    if not setup.check_ollama_installed():
        print("\n[!] Ollama needs to be installed")
        
        if setup.system == "Windows":
            setup.install_ollama_windows()
            print("\n[!] Please install Ollama manually and run this script again")
            sys.exit(1)
        else:
            if not setup.install_ollama_linux():
                print("[-] Installation failed. Please install manually:")
                print("    curl -fsSL https://ollama.ai/install.sh | sh")
                sys.exit(1)
    
    # Step 2: Start service
    setup.start_ollama_service()
    
    # Step 3: List and select models
    models = setup.list_available_models()
    
    print("\n[?] Which model to install? (recommended: 1 for dolphin-mistral)")
    choice = input("Enter number (1-6) or model name: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(models):
        model_name = models[int(choice)-1]["name"]
    else:
        model_name = choice if choice else "dolphin-mistral"
    
    # Step 4: Download model
    if not setup.pull_model(model_name):
        print("[-] Failed to download model")
        print("[!] Try manually: ollama pull dolphin-mistral")
        sys.exit(1)
    
    # Step 5: Test model
    setup.test_model(model_name)
    
    # Step 6: Create helper script
    setup.create_security_research_script()
    
    # Step 7: Complete
    setup.setup_complete()
    
    print("\n[+] Setup successful! You can now use Dolphin for research.")
    print(f"[*] Try: ollama run {model_name} 'What is a buffer overflow?'")


if __name__ == "__main__":
    main()