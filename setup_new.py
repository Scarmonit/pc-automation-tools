#!/usr/bin/env python3
"""
Setup script for AI Platform
Handles installation and configuration
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_requirements():
    """Install required packages"""
    print("\nInstalling requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("[OK] Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install requirements: {e}")
        print("\nTry installing manually with: pip install -r requirements.txt")
        return False
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if not env_path.exists():
        print("\nCreating .env file...")
        env_template = """# AI Platform Environment Configuration

# API Keys (Optional - for cloud services)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=
MISTRAL_API_KEY=
OPENROUTER_API_KEY=
AZURE_OPENAI_API_KEY=

# Local Model Endpoints (Ollama)
OLLAMA_HOST=http://localhost:11434
LM_STUDIO_HOST=http://localhost:1234

# Database Configuration
DATABASE_URL=postgresql://localhost/ai_platform
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Features
DEBUG=False
LOG_LEVEL=INFO
ENABLE_GPU=False
"""
        env_path.write_text(env_template)
        print("[OK] .env file created - Please update with your API keys")
    else:
        print("[OK] .env file already exists")


def setup_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "cache",
        "configs",
        "notebooks"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created directory: {dir_name}")


def check_docker():
    """Check if Docker is installed"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Docker detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("[WARNING] Docker not found - Required for LLMStack deployment")
    print("  Install from: https://docs.docker.com/get-docker/")
    return False


def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Ollama detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("[WARNING] Ollama not found - Required for local AI models")
    print("  Install from: https://ollama.com")
    return False


def setup_llmstack():
    """Setup LLMStack deployment"""
    llmstack_path = Path("llmstack")
    if llmstack_path.exists():
        print("\n[OK] LLMStack deployment directory found")
        print("\nTo deploy LLMStack:")
        print("  cd llmstack")
        print("  ./deploy.sh check    # Check requirements")
        print("  ./deploy.sh all      # Complete installation")
        return True
    else:
        print("\n[ERROR] LLMStack directory not found")
        return False


def main():
    """Main setup process"""
    print("=" * 60)
    print("AI Platform Setup")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\nSetting up directories...")
    setup_directories()
    
    # Create .env file
    create_env_file()
    
    # Install requirements
    if "--skip-deps" not in sys.argv:
        install_requirements()
    else:
        print("\nSkipping dependency installation (--skip-deps flag)")
    
    # Check optional components
    print("\nChecking optional components...")
    docker_installed = check_docker()
    ollama_installed = check_ollama()
    llmstack_ready = setup_llmstack()
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    print("\n[OK] Core setup complete!")
    
    print("\nNext steps:")
    print("1. Update .env file with your API keys (optional)")
    
    if not docker_installed:
        print("2. Install Docker for full functionality")
    
    if not ollama_installed:
        print("3. Install Ollama for local AI models")
    
    if llmstack_ready and docker_installed:
        print("4. Deploy LLMStack: cd llmstack && ./deploy.sh all")
    
    print("\nTo run the platform:")
    print("  python main.py list          # List all modules")
    print("  python main.py core          # Run core AI platform")
    print("  python main.py security      # Run security tools")
    print("  python main.py dolphin       # Run Dolphin models")
    
    print("\nFor help:")
    print("  python main.py --help")
    
    print("\n[OK] Setup complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during setup: {e}")
        sys.exit(1)