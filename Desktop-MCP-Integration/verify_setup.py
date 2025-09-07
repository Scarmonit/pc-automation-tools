#!/usr/bin/env python3
"""
MCP Integration Verification Script
Checks if all components are properly configured and accessible
"""

import json
import os
import subprocess
import sys
import asyncio
import aiohttp
from pathlib import Path

class MCPVerifier:
    def __init__(self):
        self.results = []
        self.ai_platform_url = "http://localhost:8000"
        self.tidy_assistant_url = "http://localhost:8001"
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        status = "[PASS]" if success else "[FAIL]"
        self.results.append((test_name, success, details))
        print(f"{status} {test_name}: {details}")
    
    def check_claude_config(self):
        """Check if Claude Desktop configuration exists"""
        config_path = Path.home() / ".claude" / "claude_desktop_config.json"
        
        if not config_path.exists():
            self.log_result("Claude Config", False, "Configuration file not found")
            return False
            
        try:
            with open(config_path) as f:
                config = json.load(f)
                
            mcp_servers = config.get("mcpServers", {})
            expected_servers = ["perplexity-search", "ai-platform", "filesystem"]
            
            found_servers = []
            for server in expected_servers:
                if server in mcp_servers:
                    found_servers.append(server)
            
            if len(found_servers) == len(expected_servers):
                self.log_result("Claude Config", True, f"All {len(found_servers)} MCP servers configured")
                return True
            else:
                self.log_result("Claude Config", False, f"Only {len(found_servers)}/{len(expected_servers)} servers configured")
                return False
                
        except Exception as e:
            self.log_result("Claude Config", False, f"Error reading config: {e}")
            return False
    
    def check_node_dependencies(self):
        """Check if Node.js dependencies are installed"""
        package_json_path = Path("package.json")
        node_modules_path = Path("node_modules")
        
        if not package_json_path.exists():
            self.log_result("Node.js Setup", False, "package.json not found")
            return False
            
        if not node_modules_path.exists():
            self.log_result("Node.js Setup", False, "node_modules not found - run 'npm install'")
            return False
            
        # Check if MCP SDK is installed
        mcp_path = node_modules_path / "@modelcontextprotocol" / "sdk"
        if mcp_path.exists():
            self.log_result("Node.js Setup", True, "MCP SDK installed")
            return True
        else:
            self.log_result("Node.js Setup", False, "MCP SDK not found")
            return False
    
    def check_python_dependencies(self):
        """Check if Python dependencies are installed"""
        try:
            import mcp
            import aiohttp
            self.log_result("Python Setup", True, "MCP and aiohttp available")
            return True
        except ImportError as e:
            self.log_result("Python Setup", False, f"Missing dependency: {e}")
            return False
    
    async def check_ai_platform(self):
        """Check if AI Platform is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ai_platform_url}/api/v1/health",
                                     headers={"Authorization": "Bearer demo-token"}) as response:
                    if response.status == 200:
                        data = await response.json()
                        services = data.get('services', {})
                        configured_count = sum(1 for v in services.values() 
                                             if v in ['configured', 'operational'])
                        self.log_result("AI Platform", True, 
                                      f"Online - {configured_count} services configured")
                        return True
                    else:
                        self.log_result("AI Platform", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log_result("AI Platform", False, f"Connection error: {e}")
            return False
    
    async def check_tidy_assistant(self):
        """Check if TidyAssistant is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.tidy_assistant_url}/api/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        uptime = data.get('uptime_minutes', 0)
                        self.log_result("TidyAssistant", True, f"Online - {uptime} min uptime")
                        return True
                    else:
                        self.log_result("TidyAssistant", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log_result("TidyAssistant", False, f"Connection error: {e}")
            return False
    
    def check_mcp_server(self):
        """Check if MCP server files exist and are valid"""
        try:
            # Check if Perplexity MCP server exists
            perplexity_server = Path("perplexity_mcp.js")
            ai_platform_server = Path("ai_platform_mcp.py")
            
            if not perplexity_server.exists():
                self.log_result("MCP Server", False, "perplexity_mcp.js not found")
                return False
                
            if not ai_platform_server.exists():
                self.log_result("MCP Server", False, "ai_platform_mcp.py not found")
                return False
            
            # Check if files contain expected content
            with open(perplexity_server, encoding='utf-8') as f:
                perplexity_content = f.read()
            
            with open(ai_platform_server, encoding='utf-8') as f:
                ai_platform_content = f.read()
            
            if "web_search" in perplexity_content and "Server" in perplexity_content:
                if "ai_chat" in ai_platform_content and "platform_health" in ai_platform_content:
                    self.log_result("MCP Server", True, "Both MCP servers configured correctly")
                    return True
                else:
                    self.log_result("MCP Server", False, "AI Platform MCP server missing tools")
                    return False
            else:
                self.log_result("MCP Server", False, "Perplexity MCP server missing tools")
                return False
                
        except Exception as e:
            self.log_result("MCP Server", False, f"Error: {e}")
            return False
    
    async def run_verification(self):
        """Run all verification tests"""
        print("[INFO] MCP Integration Verification")
        print("=" * 40)
        
        # Synchronous checks
        self.check_claude_config()
        self.check_node_dependencies() 
        self.check_python_dependencies()
        self.check_mcp_server()
        
        # Asynchronous checks
        await self.check_ai_platform()
        await self.check_tidy_assistant()
        
        # Summary
        print("\n" + "=" * 40)
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        if passed == total:
            print(f"[SUCCESS] All {total} tests passed! MCP integration is ready.")
            print("\nNext steps:")
            print("1. Restart Claude Desktop if it's running")
            print("2. Look for MCP indicator in conversation input")
            print("3. Try: 'Search the web for latest AI news'")
            print("4. Try: 'Check my AI platform status'")
        else:
            print(f"[WARNING] {passed}/{total} tests passed. Please fix the failing components.")
            print("\nFailed tests:")
            for name, success, details in self.results:
                if not success:
                    print(f"  - {name}: {details}")
        
        return passed == total

async def main():
    """Main verification function"""
    verifier = MCPVerifier()
    success = await verifier.run_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())