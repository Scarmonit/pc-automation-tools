# Setup Free AI Agents for Windows
# Configure AutoGen, Aider, and other free AI tools

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Setting up Free AI Agents" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Create agents directory
$agentsPath = "$PSScriptRoot\..\..\agents"
if (!(Test-Path $agentsPath)) {
    New-Item -Path $agentsPath -ItemType Directory -Force | Out-Null
}

# Configure AutoGen
Write-Host "Configuring AutoGen..." -ForegroundColor Yellow
$autogenConfig = @{
    model_list = @(
        @{
            model = "llama3.2:3b"
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
            api_type = "openai"
        },
        @{
            model = "mistral:7b-instruct"
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
            api_type = "openai"
        },
        @{
            model = "codellama:7b"
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
            api_type = "openai"
        }
    )
    code_execution_config = @{
        work_dir = "$agentsPath\autogen_workspace"
        use_docker = $false
    }
} | ConvertTo-Json -Depth 10

$autogenPath = "$env:USERPROFILE\.autogen"
if (!(Test-Path $autogenPath)) {
    New-Item -Path $autogenPath -ItemType Directory -Force | Out-Null
}
Set-Content -Path "$autogenPath\config.json" -Value $autogenConfig
Write-Host "  AutoGen configured" -ForegroundColor Green

# Configure Aider
Write-Host "Configuring Aider..." -ForegroundColor Yellow
$aiderConfig = @"
model: ollama/codellama:7b
openai-api-base: http://localhost:11434/v1
openai-api-key: ollama
auto-commits: false
stream: true
edit-format: diff
"@

$aiderPath = "$env:USERPROFILE\.aider"
Set-Content -Path "$aiderPath.conf.yml" -Value $aiderConfig
Write-Host "  Aider configured" -ForegroundColor Green

# Create agent orchestrator
Write-Host "Creating Agent Orchestrator..." -ForegroundColor Yellow
$orchestrator = @'
import asyncio
import httpx
from typing import Dict, Any, List
import json
from pathlib import Path

class FreeAgentOrchestrator:
    """Orchestrates multiple free AI agents for complex tasks"""
    
    def __init__(self):
        self.endpoints = {
            "ollama": "http://localhost:11434/v1",
            "flowise": "http://localhost:3001/api/v1",
            "chroma": "http://localhost:8001"
        }
        self.client = httpx.AsyncClient(timeout=60.0)
        self.workspace = Path(__file__).parent / "workspace"
        self.workspace.mkdir(exist_ok=True)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check which services are available"""
        health = {}
        for name, endpoint in self.endpoints.items():
            try:
                if name == "ollama":
                    response = await self.client.get(f"{endpoint}/models")
                else:
                    response = await self.client.get(endpoint)
                health[name] = response.status_code == 200
            except:
                health[name] = False
        return health
    
    async def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code using CodeLlama"""
        response = await self.client.post(
            f"{self.endpoints['ollama']}/chat/completions",
            json={
                "model": "codellama:7b",
                "messages": [
                    {"role": "system", "content": f"You are an expert {language} programmer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    
    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for quality and security issues"""
        prompt = f"""Analyze this code for:
        1. Security vulnerabilities
        2. Performance issues
        3. Code quality
        4. Suggested improvements
        
        Code:
        {code}
        """
        
        response = await self.client.post(
            f"{self.endpoints['ollama']}/chat/completions",
            json={
                "model": "mistral:7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
        )
        
        return {
            "analysis": response.json()["choices"][0]["message"]["content"],
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def create_rag_pipeline(self, documents: List[str]) -> str:
        """Create a RAG pipeline for document Q&A"""
        # This would integrate with Chroma for vector storage
        # and Flowise for workflow management
        return "RAG pipeline created"
    
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()

# Example usage
async def main():
    orchestrator = FreeAgentOrchestrator()
    
    # Check health
    health = await orchestrator.check_health()
    print("Service Health:", json.dumps(health, indent=2))
    
    # Generate code
    code = await orchestrator.generate_code(
        "Create a FastAPI endpoint for user authentication with JWT"
    )
    print("\nGenerated Code:")
    print(code[:500] + "..." if len(code) > 500 else code)
    
    # Analyze code
    analysis = await orchestrator.analyze_code(code)
    print("\nCode Analysis:")
    print(analysis["analysis"][:500] + "...")
    
    await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())
'@

Set-Content -Path "$agentsPath\orchestrator.py" -Value $orchestrator
Write-Host "  Agent Orchestrator created" -ForegroundColor Green

# Create AutoGen example
Write-Host "Creating AutoGen Examples..." -ForegroundColor Yellow
$autogenExample = @'
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import autogen

# Load configuration
config_list = config_list_from_json(env_or_file="~/.autogen/config.json")

# Create assistant agent
assistant = AssistantAgent(
    name="coding_assistant",
    llm_config={
        "config_list": config_list,
        "temperature": 0.3,
    },
    system_message="You are a helpful AI assistant that writes high-quality code."
)

# Create user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": False,
    }
)

# Example task
def solve_task(task: str):
    user_proxy.initiate_chat(
        assistant,
        message=task
    )

if __name__ == "__main__":
    task = """
    Create a Python function that:
    1. Fetches data from a REST API
    2. Processes the JSON response
    3. Saves results to a SQLite database
    Include error handling and logging.
    """
    solve_task(task)
'@

Set-Content -Path "$agentsPath\autogen_example.py" -Value $autogenExample
Write-Host "  AutoGen examples created" -ForegroundColor Green

# Create Aider helper script
Write-Host "Creating Aider Helper Scripts..." -ForegroundColor Yellow
$aiderHelper = @"
#!/usr/bin/env python3
'''Aider Helper - Automated code improvement with Ollama'''

import subprocess
import sys
from pathlib import Path

def run_aider(project_path: str, instruction: str):
    '''Run Aider with specific instructions'''
    
    cmd = [
        'aider',
        '--model', 'ollama/codellama:7b',
        '--openai-api-base', 'http://localhost:11434/v1',
        '--openai-api-key', 'ollama',
        '--message', instruction,
        '--yes',  # Auto-accept suggestions
        project_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running Aider: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: aider_helper.py <project_path> <instruction>")
        sys.exit(1)
    
    project = sys.argv[1]
    instruction = ' '.join(sys.argv[2:])
    
    success = run_aider(project, instruction)
    sys.exit(0 if success else 1)
"@

Set-Content -Path "$agentsPath\aider_helper.py" -Value $aiderHelper
Write-Host "  Aider helper created" -ForegroundColor Green

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "AI Agents Setup Complete!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configured Agents:" -ForegroundColor Yellow
Write-Host "  - AutoGen (Multi-agent conversations)" -ForegroundColor Cyan
Write-Host "  - Aider (Code improvement)" -ForegroundColor Cyan
Write-Host "  - Agent Orchestrator (Task coordination)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example Usage:" -ForegroundColor Yellow
Write-Host "  python agents\orchestrator.py" -ForegroundColor Green
Write-Host "  python agents\autogen_example.py" -ForegroundColor Green
Write-Host "  aider --message 'Add tests' src\" -ForegroundColor Green