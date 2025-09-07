#!/usr/bin/env python3
"""
AI Platform MCP Server
Provides access to your multi-AI platform (Claude, OpenAI, Perplexity) via MCP
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
import aiohttp
import logging

# MCP SDK imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        CallToolRequest, 
        ListToolsRequest,
        TextContent,
        Tool,
        INVALID_REQUEST,
        INTERNAL_ERROR
    )
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configuration
AI_PLATFORM_BASE_URL = "http://localhost:8000"
TIDY_ASSISTANT_BASE_URL = "http://localhost:8001"
DEMO_TOKEN = "demo-token"

class AIPlatformMCPServer:
    def __init__(self):
        self.server = Server("ai-platform-mcp")
        self.session = None
        
    async def setup_session(self):
        """Setup HTTP session for API calls"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    def setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return list of available tools"""
            return [
                Tool(
                    name="ai_chat",
                    description="Chat with AI models (Claude, OpenAI, Perplexity)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The message to send to the AI"
                            },
                            "model": {
                                "type": "string", 
                                "description": "AI model to use",
                                "enum": ["claude-3-haiku-20240307", "gpt-4o", "gpt-4o-mini", "sonar-pro", "sonar-small"],
                                "default": "claude-3-haiku-20240307"
                            },
                            "max_tokens": {
                                "type": "number",
                                "description": "Maximum tokens for response",
                                "default": 1000
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="platform_health",
                    description="Check AI Platform system health and status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),
                Tool(
                    name="upload_document",
                    description="Upload and analyze a document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to upload"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis to perform",
                                "enum": ["summarize", "extract", "analyze"],
                                "default": "summarize"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="search_documents",
                    description="Search through uploaded documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "top_k": {
                                "type": "number",
                                "description": "Number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="tidy_status",
                    description="Check TidyAssistant status and system monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),
                Tool(
                    name="trigger_cleanup",
                    description="Trigger manual cleanup operation via TidyAssistant",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "force": {
                                "type": "boolean",
                                "description": "Force cleanup even if system is not idle",
                                "default": False
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            await self.setup_session()
            
            try:
                if name == "ai_chat":
                    return await self.handle_ai_chat(arguments)
                elif name == "platform_health":
                    return await self.handle_platform_health()
                elif name == "upload_document":
                    return await self.handle_upload_document(arguments)
                elif name == "search_documents":
                    return await self.handle_search_documents(arguments)
                elif name == "tidy_status":
                    return await self.handle_tidy_status()
                elif name == "trigger_cleanup":
                    return await self.handle_trigger_cleanup(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_ai_chat(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle AI chat requests"""
        prompt = args["prompt"]
        model = args.get("model", "claude-3-haiku-20240307")
        max_tokens = args.get("max_tokens", 1000)
        
        payload = {
            "prompt": prompt,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEMO_TOKEN}"
        }
        
        # Choose endpoint based on model
        if model.startswith("sonar"):
            endpoint = f"{AI_PLATFORM_BASE_URL}/api/v1/ai/search"
            payload = {"query": prompt, "model": model, "max_tokens": max_tokens}
        else:
            endpoint = f"{AI_PLATFORM_BASE_URL}/api/v1/ai/generate"
        
        async with self.session.post(endpoint, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                content = data.get("content", "No response")
                
                # Format response with metadata
                formatted_response = f"**AI Response ({model}):**\n\n{content}\n\n"
                if "usage" in data:
                    usage = data["usage"]
                    formatted_response += f"*Tokens: {usage.get('input_tokens', 0)} in, {usage.get('output_tokens', 0)} out*\n"
                formatted_response += f"*Processing time: {data.get('processing_time_ms', 0)}ms*"
                
                return [TextContent(type="text", text=formatted_response)]
            else:
                error_text = await response.text()
                return [TextContent(type="text", text=f"AI Platform Error ({response.status}): {error_text}")]

    async def handle_platform_health(self) -> List[TextContent]:
        """Check AI Platform health"""
        headers = {"Authorization": f"Bearer {DEMO_TOKEN}"}
        
        async with self.session.get(f"{AI_PLATFORM_BASE_URL}/api/v1/health", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                health_report = "**AI Platform Health Status:**\n\n"
                health_report += f"• **Status**: {data.get('status', 'Unknown')}\n"
                health_report += f"• **Version**: {data.get('version', 'Unknown')}\n"
                
                services = data.get('services', {})
                health_report += "\n**Service Status:**\n"
                for service, status in services.items():
                    emoji = "✅" if status == "configured" or status == "operational" else "❌"
                    health_report += f"• {emoji} **{service.title()}**: {status}\n"
                
                paths = data.get('paths', {})
                if paths:
                    health_report += "\n**System Paths:**\n"
                    for path_name, path_value in paths.items():
                        health_report += f"• **{path_name}**: {path_value}\n"
                
                return [TextContent(type="text", text=health_report)]
            else:
                return [TextContent(type="text", text=f"Failed to get health status: {response.status}")]

    async def handle_upload_document(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle document upload (placeholder - would need file handling)"""
        file_path = args["file_path"]
        analysis_type = args.get("analysis_type", "summarize")
        
        return [TextContent(type="text", text=f"Document upload feature requires file handling implementation.\nRequested: {file_path} (analysis: {analysis_type})")]

    async def handle_search_documents(self, args: Dict[str, Any]) -> List[TextContent]:
        """Search documents in AI Platform"""
        query = args["query"]
        top_k = args.get("top_k", 5)
        
        headers = {"Authorization": f"Bearer {DEMO_TOKEN}"}
        params = {"query": query, "top_k": top_k}
        
        async with self.session.get(f"{AI_PLATFORM_BASE_URL}/api/v1/documents/search", 
                                   params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                results = data.get("results", [])
                
                if not results:
                    return [TextContent(type="text", text=f"No documents found for query: '{query}'")]
                
                search_report = f"**Document Search Results for: '{query}'**\n\n"
                for i, result in enumerate(results, 1):
                    search_report += f"**{i}. Document ID: {result.get('id', 'Unknown')}**\n"
                    search_report += f"Snippet: {result.get('snippet', 'No snippet')}\n"
                    search_report += f"Score: {result.get('score', 0)}\n\n"
                
                return [TextContent(type="text", text=search_report)]
            else:
                return [TextContent(type="text", text=f"Search failed: {response.status}")]

    async def handle_tidy_status(self) -> List[TextContent]:
        """Get TidyAssistant status"""
        try:
            async with self.session.get(f"{TIDY_ASSISTANT_BASE_URL}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    status_report = "**TidyAssistant Status:**\n\n"
                    status_report += f"• **Running**: {'Yes' if data.get('running', False) else 'No'}\n"
                    status_report += f"• **Uptime**: {data.get('uptime_minutes', 0)} minutes\n"
                    status_report += f"• **Monitoring Paths**: {data.get('monitoring_paths', 0)}\n"
                    
                    components = data.get('components', {})
                    active_components = sum(1 for v in components.values() if v)
                    status_report += f"• **Active Components**: {active_components}/{len(components)}\n"
                    
                    return [TextContent(type="text", text=status_report)]
                else:
                    return [TextContent(type="text", text=f"TidyAssistant not accessible: {response.status}")]
        except Exception as e:
            return [TextContent(type="text", text=f"TidyAssistant connection error: {str(e)}")]

    async def handle_trigger_cleanup(self, args: Dict[str, Any]) -> List[TextContent]:
        """Trigger cleanup operation"""
        force = args.get("force", False)
        
        # This would need to be implemented in TidyAssistant API
        return [TextContent(type="text", text="Manual cleanup trigger not yet implemented in TidyAssistant API")]

    async def run(self):
        """Run the MCP server"""
        self.setup_handlers()
        
        async with self.server.stdio_transport() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ai-platform-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                )
            )

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main entry point"""
    server = AIPlatformMCPServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        pass
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())