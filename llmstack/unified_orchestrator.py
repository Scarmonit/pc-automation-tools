#!/usr/bin/env python3
"""
Unified AI Orchestrator - Complete Integration System
Combines LocalAI, MemGPT, AutoGen, CAMEL-AI, and existing services
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from flask import Flask, jsonify, request, render_template_string
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the AI frameworks integration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_frameworks_integration import UnifiedAIOrchestrator, AIConfig

# Flask app for web interface
app = Flask(__name__)

@dataclass
class SystemStatus:
    """System-wide status tracking"""
    localai: bool = False
    memgpt: bool = False
    autogen: bool = False
    camel: bool = False
    ollama: bool = False
    flowise: bool = False
    llmstack: bool = False
    last_check: Optional[datetime] = None

class UnifiedSystemOrchestrator:
    """Main orchestrator combining all AI systems"""
    
    def __init__(self):
        # Initialize AI frameworks orchestrator
        config = AIConfig(
            use_local=True,
            localai_endpoint="http://localhost:8080/v1",
            model_name="gpt-3.5-turbo"
        )
        self.ai_orchestrator = UnifiedAIOrchestrator(config)
        
        # Service endpoints
        self.endpoints = {
            "localai": "http://localhost:8080",
            "ollama": "http://localhost:11434",
            "flowise": "http://localhost:3001",
            "llmstack": "http://localhost:3000",
            "grafana": "http://localhost:3003",
            "prometheus": "http://localhost:9090"
        }
        
        # System status
        self.status = SystemStatus()
        self.update_status()
    
    def update_status(self):
        """Update system status"""
        import requests
        
        # Check each service
        services_status = {}
        
        # Check LocalAI
        try:
            r = requests.get(f"{self.endpoints['localai']}/models", timeout=2)
            services_status['localai'] = r.status_code == 200
        except:
            services_status['localai'] = False
        
        # Check Ollama
        try:
            r = requests.get(f"{self.endpoints['ollama']}/api/tags", timeout=2)
            services_status['ollama'] = r.status_code == 200
        except:
            services_status['ollama'] = False
        
        # Check Flowise
        try:
            r = requests.get(self.endpoints['flowise'], timeout=2)
            services_status['flowise'] = r.status_code == 200
        except:
            services_status['flowise'] = False
        
        # Check LLMStack
        try:
            r = requests.get(self.endpoints['llmstack'], timeout=2)
            services_status['llmstack'] = r.status_code == 200
        except:
            services_status['llmstack'] = False
        
        # Update framework status
        framework_status = self.ai_orchestrator.check_status()
        
        # Update system status
        self.status.localai = services_status.get('localai', False)
        self.status.ollama = services_status.get('ollama', False)
        self.status.flowise = services_status.get('flowise', False)
        self.status.llmstack = services_status.get('llmstack', False)
        self.status.memgpt = framework_status.get('memgpt', False)
        self.status.autogen = framework_status.get('autogen', False)
        self.status.camel = framework_status.get('camel', False)
        self.status.last_check = datetime.now()
        
        return self.get_status_dict()
    
    def get_status_dict(self) -> Dict[str, Any]:
        """Get status as dictionary"""
        return {
            "services": {
                "localai": self.status.localai,
                "ollama": self.status.ollama,
                "flowise": self.status.flowise,
                "llmstack": self.status.llmstack
            },
            "frameworks": {
                "memgpt": self.status.memgpt,
                "autogen": self.status.autogen,
                "camel": self.status.camel
            },
            "last_check": self.status.last_check.isoformat() if self.status.last_check else None
        }
    
    def route_task(self, task: str, routing_strategy: str = "auto") -> Dict[str, Any]:
        """Route task to appropriate framework or service"""
        
        # Analyze task to determine best framework
        task_lower = task.lower()
        
        # Routing logic
        if routing_strategy == "auto":
            if "remember" in task_lower or "memory" in task_lower:
                framework = "memgpt"
            elif "collaborate" in task_lower or "team" in task_lower:
                framework = "autogen"
            elif "role" in task_lower or "play" in task_lower:
                framework = "camel"
            elif "code" in task_lower or "program" in task_lower:
                framework = "autogen"
            else:
                framework = "localai"
        else:
            framework = routing_strategy
        
        # Execute task
        try:
            result = self.ai_orchestrator.chat(task, framework=framework)
            return {
                "success": True,
                "framework": framework,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error routing task: {e}")
            return {
                "success": False,
                "error": str(e),
                "framework": framework,
                "timestamp": datetime.now().isoformat()
            }
    
    def multi_agent_collaboration(self, task: str, agents: List[str] = None):
        """Execute task with multiple agents collaborating"""
        agents = agents or ["autogen", "camel", "localai"]
        
        results = {}
        for agent in agents:
            logger.info(f"Processing with {agent}...")
            result = self.route_task(task, routing_strategy=agent)
            results[agent] = result
        
        # Synthesize results
        synthesis_prompt = f"Synthesize these responses to '{task}':\n"
        for agent, result in results.items():
            if result.get('success'):
                synthesis_prompt += f"\n{agent}: {result.get('result', 'No result')[:200]}..."
        
        # Use LocalAI to synthesize
        final_result = self.ai_orchestrator.chat(synthesis_prompt, framework="localai")
        
        return {
            "individual_results": results,
            "synthesis": final_result,
            "timestamp": datetime.now().isoformat()
        }

# Global orchestrator instance
orchestrator = UnifiedSystemOrchestrator()

# Flask routes
@app.route('/')
def index():
    """Web interface"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified AI Orchestrator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
            .status { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }
            .status-item { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .online { background: #d4edda; border-color: #28a745; }
            .offline { background: #f8d7da; border-color: #dc3545; }
            .task-form { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            input, select, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #45a049; }
            .result { margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px; }
            pre { white-space: pre-wrap; word-wrap: break-word; }
        </style>
        <script>
            async function checkStatus() {
                const response = await fetch('/status');
                const data = await response.json();
                updateStatus(data);
            }
            
            function updateStatus(data) {
                const statusDiv = document.getElementById('status');
                let html = '';
                
                // Services
                html += '<h3>Services</h3><div class="status">';
                for (const [service, status] of Object.entries(data.services)) {
                    const cssClass = status ? 'online' : 'offline';
                    const statusText = status ? 'Online' : 'Offline';
                    html += `<div class="status-item ${cssClass}">${service}: ${statusText}</div>`;
                }
                html += '</div>';
                
                // Frameworks
                html += '<h3>AI Frameworks</h3><div class="status">';
                for (const [framework, status] of Object.entries(data.frameworks)) {
                    const cssClass = status ? 'online' : 'offline';
                    const statusText = status ? 'Available' : 'Not Available';
                    html += `<div class="status-item ${cssClass}">${framework}: ${statusText}</div>`;
                }
                html += '</div>';
                
                statusDiv.innerHTML = html;
            }
            
            async function executeTask() {
                const task = document.getElementById('task').value;
                const framework = document.getElementById('framework').value;
                
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task, framework})
                });
                
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            }
            
            // Auto-refresh status every 5 seconds
            setInterval(checkStatus, 5000);
            window.onload = checkStatus;
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Unified AI Orchestrator</h1>
            
            <div id="status">
                <p>Loading status...</p>
            </div>
            
            <div class="task-form">
                <h2>Execute Task</h2>
                <textarea id="task" rows="4" placeholder="Enter your task or question..."></textarea>
                <select id="framework">
                    <option value="auto">Auto-select Framework</option>
                    <option value="localai">LocalAI</option>
                    <option value="memgpt">MemGPT (Memory)</option>
                    <option value="autogen">AutoGen (Multi-agent)</option>
                    <option value="camel">CAMEL (Role-play)</option>
                </select>
                <button onclick="executeTask()">Execute</button>
            </div>
            
            <div id="result" class="result">
                <p>Results will appear here...</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/status')
def get_status():
    """Get system status"""
    return jsonify(orchestrator.update_status())

@app.route('/execute', methods=['POST'])
def execute_task():
    """Execute a task"""
    data = request.json
    task = data.get('task', '')
    framework = data.get('framework', 'auto')
    
    result = orchestrator.route_task(task, routing_strategy=framework)
    return jsonify(result)

@app.route('/collaborate', methods=['POST'])
def collaborate():
    """Multi-agent collaboration"""
    data = request.json
    task = data.get('task', '')
    agents = data.get('agents', None)
    
    result = orchestrator.multi_agent_collaboration(task, agents)
    return jsonify(result)

def run_flask():
    """Run Flask in a separate thread"""
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    """Main entry point"""
    print("=" * 60)
    print("  UNIFIED AI ORCHESTRATOR")
    print("=" * 60)
    print()
    print("Integrating:")
    print("  • LocalAI - Local model serving")
    print("  • MemGPT - Memory-enhanced conversations")
    print("  • AutoGen - Multi-agent collaboration")
    print("  • CAMEL-AI - Role-playing agents")
    print("  • Ollama - Local LLMs")
    print("  • Flowise - Visual workflows")
    print("  • LLMStack - LLM platform")
    print()
    print("=" * 60)
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("\n✓ Web interface started at: http://localhost:5000")
    
    # Check initial status
    print("\nChecking system status...")
    status = orchestrator.update_status()
    
    print("\nServices:")
    for service, online in status['services'].items():
        status_str = "[OK]" if online else "[X]"
        print(f"  {status_str} {service}")
    
    print("\nFrameworks:")
    for framework, available in status['frameworks'].items():
        status_str = "[OK]" if available else "[X]"
        print(f"  {status_str} {framework}")
    
    print("\n" + "=" * 60)
    print("System ready! Access the web interface at:")
    print("  http://localhost:5000")
    print("\nPress Ctrl+C to exit")
    print("=" * 60)
    
    # Keep running
    try:
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()