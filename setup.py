#!/usr/bin/env python3
"""
AI Platform Setup Script
Comprehensive setup for all AI platform components
"""

import os
import sys
import subprocess
from pathlib import Path
import platform
import json

class AIPlatformSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.python_cmd = sys.executable
        self.os_type = platform.system()
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {text}")
        print("="*60)
        
    def run_command(self, cmd, description=""):
        """Run shell command with error handling"""
        if description:
            print(f"\n-> {description}")
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[ERROR] {result.stderr}")
                return False
            print("[SUCCESS]")
            return True
        except Exception as e:
            print(f"[FAILED] {str(e)}")
            return False
    
    def check_python_version(self):
        """Check Python version"""
        self.print_header("Checking Python Version")
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print("✅ Python version OK")
        return True
    
    def install_requirements(self):
        """Install Python requirements"""
        self.print_header("Installing Python Requirements")
        
        # Upgrade pip first
        self.run_command(
            f"{self.python_cmd} -m pip install --upgrade pip",
            "Upgrading pip"
        )
        
        # Install main requirements
        req_file = self.root_dir / "requirements.txt"
        if req_file.exists():
            self.run_command(
                f"{self.python_cmd} -m pip install -r {req_file}",
                "Installing main requirements"
            )
        
        return True
    
    def setup_ollama(self):
        """Setup Ollama for Dolphin models"""
        self.print_header("Setting up Ollama")
        
        if self.os_type == "Windows":
            # Check if Ollama is installed
            result = subprocess.run("ollama version", shell=True, capture_output=True)
            if result.returncode != 0:
                print("⚠️  Ollama not installed. Please install from: https://ollama.ai/download")
                return False
        
        # Pull required models
        models = ["dolphin-mistral", "codellama", "llama2"]
        for model in models:
            self.run_command(
                f"ollama pull {model}",
                f"Pulling {model} model"
            )
        
        return True
    
    def setup_docker(self):
        """Setup Docker containers"""
        self.print_header("Setting up Docker Services")
        
        # Check if Docker is running
        result = subprocess.run("docker version", shell=True, capture_output=True)
        if result.returncode != 0:
            print("⚠️  Docker not running. Please start Docker Desktop")
            return False
        
        # Navigate to infrastructure directory
        docker_dir = self.root_dir / "src" / "infrastructure"
        if docker_dir.exists():
            os.chdir(docker_dir)
            
            # Build and start containers
            self.run_command(
                "docker-compose build",
                "Building Docker containers"
            )
            
            self.run_command(
                "docker-compose up -d",
                "Starting Docker services"
            )
            
            os.chdir(self.root_dir)
        
        return True
    
    def setup_environment(self):
        """Setup environment variables"""
        self.print_header("Setting up Environment")
        
        env_example = self.root_dir / ".env.example"
        env_file = self.root_dir / ".env"
        
        if not env_file.exists() and env_example.exists():
            print("Creating .env file from example...")
            env_example.rename(env_file)
            print("✅ Created .env file - Please update with your API keys")
        elif env_file.exists():
            print("✅ .env file already exists")
        
        return True
    
    def setup_mcp(self):
        """Setup MCP services"""
        self.print_header("Setting up MCP Services")
        
        # Install Node.js dependencies for MCP
        mcp_dirs = [
            self.root_dir / "Desktop-MCP-Integration",
            self.root_dir / "claude-memory-mcp",
            self.root_dir / "mcp-memory-service"
        ]
        
        for mcp_dir in mcp_dirs:
            if mcp_dir.exists():
                package_json = mcp_dir / "package.json"
                if package_json.exists():
                    os.chdir(mcp_dir)
                    self.run_command(
                        "npm install",
                        f"Installing dependencies for {mcp_dir.name}"
                    )
                    os.chdir(self.root_dir)
        
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        self.print_header("Creating Directory Structure")
        
        dirs = [
            "data",
            "logs",
            "models",
            "cache",
            "outputs"
        ]
        
        for dir_name in dirs:
            dir_path = self.root_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created {dir_name}/")
        
        return True
    
    def test_installation(self):
        """Test the installation"""
        self.print_header("Testing Installation")
        
        # Test main module
        result = subprocess.run(
            f"{self.python_cmd} main.py list",
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.root_dir
        )
        
        if result.returncode == 0:
            print("✅ Main module working")
        else:
            print(f"❌ Main module error: {result.stderr}")
        
        return result.returncode == 0
    
    def run(self):
        """Run complete setup"""
        self.print_header("AI PLATFORM SETUP")
        print("Starting comprehensive setup...")
        
        steps = [
            ("Python Version", self.check_python_version),
            ("Environment", self.setup_environment),
            ("Directories", self.create_directories),
            ("Requirements", self.install_requirements),
            ("Ollama", self.setup_ollama),
            ("MCP Services", self.setup_mcp),
            ("Docker", self.setup_docker),
            ("Testing", self.test_installation)
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n⚠️  {step_name} setup incomplete (continuing...)")
            except Exception as e:
                print(f"\n❌ {step_name} failed: {str(e)}")
                continue
        
        self.print_header("SETUP COMPLETE")
        print("\n🚀 AI Platform is ready to use!")
        print("\nQuick Start:")
        print("  python main.py list           - List all modules")
        print("  python main.py core           - Run core platform")
        print("  python main.py dolphin --action=gui - Launch Dolphin GUI")
        print("  python main.py security --action=webscan - Run security scanner")
        print("\nDocumentation: docs/README.md")
        

if __name__ == "__main__":
    setup = AIPlatformSetup()
    setup.run()