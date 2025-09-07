#!/usr/bin/env python3
"""
Enhanced AI Platform MCP Server
Provides access to your multi-AI platform with advanced prompt management and security
Incorporates best practices from Cursor, Claude Code, Cline, and other AI tools
"""

import asyncio
import json
import sys
import os
import hashlib
from typing import Any, Dict, List, Optional
import aiohttp
import logging
from datetime import datetime

# MCP SDK imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
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

class PromptManager:
    """Advanced prompt management system inspired by leading AI tools"""
    
    def __init__(self):
        self.prompts = {
            "coding_assistant": {
                "system": """You are a highly skilled software engineer with extensive knowledge in programming languages, 
                frameworks, design patterns, and best practices. You provide accurate, efficient, and well-structured solutions 
                while maintaining security and following coding standards.""",
                "context": "coding, development, debugging",
                "model_preferences": ["claude-3-haiku-20240307", "gpt-4o"]
            },
            "code_review": {
                "system": """You are an expert code reviewer focused on identifying bugs, security vulnerabilities, 
                performance issues, and maintainability concerns. Provide constructive feedback with specific suggestions 
                for improvement.""",
                "context": "review, analysis, security",
                "model_preferences": ["claude-3-haiku-20240307"]
            },
            "documentation": {
                "system": """You are a technical documentation specialist. Create clear, comprehensive, and user-friendly 
                documentation that follows best practices. Focus on clarity, completeness, and practical examples.""",
                "context": "documentation, explanation, tutorials",
                "model_preferences": ["gpt-4o", "claude-3-haiku-20240307"]
            },
            "creative_problem_solving": {
                "system": """You are an innovative problem solver who approaches challenges from multiple angles. 
                Think creatively, consider edge cases, and propose novel solutions while maintaining practicality.""",
                "context": "problem-solving, innovation, brainstorming",
                "model_preferences": ["gpt-4o", "sonar-pro"]
            },
            "research_analysis": {
                "system": """You are a research analyst who provides thorough, well-sourced, and objective analysis. 
                Verify information, consider multiple perspectives, and present findings with appropriate caveats.""",
                "context": "research, analysis, fact-checking",
                "model_preferences": ["sonar-pro", "gpt-4o"]
            }
        }
    
    def get_prompt(self, category: str, user_context: str = "") -> Dict[str, Any]:
        """Get appropriate prompt based on category and context"""
        if category not in self.prompts:
            category = "coding_assistant"  # Default fallback
        
        prompt_data = self.prompts[category].copy()
        if user_context:
            prompt_data["system"] += f"\n\nContext: {user_context}"
        
        return prompt_data
    
    def get_best_model(self, category: str, available_models: List[str]) -> str:
        """Get the best model for a specific prompt category"""
        if category not in self.prompts:
            return available_models[0] if available_models else "claude-3-haiku-20240307"
        
        preferences = self.prompts[category]["model_preferences"]
        for model in preferences:
            if model in available_models:
                return model
        
        return available_models[0] if available_models else "claude-3-haiku-20240307"

class SecurityManager:
    """Security validation inspired by Claude Code and Cursor security practices"""
    
    DANGEROUS_PATTERNS = [
        r'(?i)eval\s*\(',
        r'(?i)exec\s*\(',
        r'(?i)__import__\s*\(',
        r'(?i)os\.system\s*\(',
        r'(?i)subprocess\.',
        r'(?i)shell=True',
        r'(?i)rm\s+-rf',
        r'(?i)del\s+/',
        r'(?i)<script',
        r'(?i)javascript:',
    ]
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate prompt for security concerns"""
        import re
        
        issues = []
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt):
                issues.append(f"Potentially dangerous pattern detected: {pattern}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "sanitized": self._sanitize_prompt(prompt)
        }
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Basic prompt sanitization"""
        # Remove potential injection attempts
        sanitized = prompt.replace("</system>", "").replace("<system>", "")
        sanitized = sanitized.replace("</user>", "").replace("<user>", "")
        sanitized = sanitized.replace("</assistant>", "").replace("<assistant>", "")
        
        return sanitized

class EnhancedAIPlatformMCPServer:
    """Enhanced AI Platform MCP Server with advanced capabilities"""
    
    def __init__(self):
        self.server = Server("ai-platform-mcp-enhanced")
        self.session = None
        self.prompt_manager = PromptManager()
        self.security_manager = SecurityManager()
        self.available_models = [
            "claude-3-haiku-20240307", "gpt-4o", "gpt-4o-mini", 
            "sonar-pro", "sonar-small"
        ]
        
    async def setup_session(self):
        """Setup HTTP session for API calls"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    def setup_handlers(self):
        """Setup MCP request handlers with enhanced capabilities"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return list of available tools with enhanced capabilities"""
            return [
                Tool(
                    name="smart_ai_chat",
                    description="Advanced AI chat with intelligent prompt selection and security validation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The message to send to the AI"
                            },
                            "category": {
                                "type": "string",
                                "description": "Type of assistance needed",
                                "enum": ["coding_assistant", "code_review", "documentation", 
                                        "creative_problem_solving", "research_analysis"],
                                "default": "coding_assistant"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context about the task",
                                "default": ""
                            },
                            "model": {
                                "type": "string",
                                "description": "Specific model to use (optional - will auto-select if not provided)",
                                "enum": ["claude-3-haiku-20240307", "gpt-4o", "gpt-4o-mini", "sonar-pro", "sonar-small"]
                            },
                            "max_tokens": {
                                "type": "number",
                                "description": "Maximum tokens for response",
                                "default": 2000
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Response creativity (0.0-1.0)",
                                "default": 0.7,
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="batch_ai_analysis",
                    description="Analyze multiple pieces of content with different AI models for comparison",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The analysis prompt"
                            },
                            "models": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of models to use for analysis",
                                "default": ["claude-3-haiku-20240307", "gpt-4o"]
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="prompt_optimization",
                    description="Optimize prompts for better AI responses based on best practices",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The prompt to optimize"
                            },
                            "target_category": {
                                "type": "string",
                                "description": "Target use case category",
                                "enum": ["coding_assistant", "code_review", "documentation", 
                                        "creative_problem_solving", "research_analysis"]
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
                    name="security_check",
                    description="Validate content for security concerns before processing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to validate"
                            }
                        },
                        "required": ["content"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Enhanced tool call handling with security and intelligence"""
            await self.setup_session()
            
            try:
                if name == "smart_ai_chat":
                    return await self.handle_smart_ai_chat(arguments)
                elif name == "batch_ai_analysis":
                    return await self.handle_batch_analysis(arguments)
                elif name == "prompt_optimization":
                    return await self.handle_prompt_optimization(arguments)
                elif name == "platform_health":
                    return await self.handle_platform_health()
                elif name == "security_check":
                    return await self.handle_security_check(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logging.error(f"Tool execution error: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_smart_ai_chat(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle smart AI chat with enhanced prompt management"""
        user_prompt = args["prompt"]
        category = args.get("category", "coding_assistant")
        context = args.get("context", "")
        max_tokens = args.get("max_tokens", 2000)
        temperature = args.get("temperature", 0.7)
        
        # Security validation
        security_check = self.security_manager.validate_prompt(user_prompt)
        if not security_check["safe"]:
            return [TextContent(type="text", 
                text=f"Security Warning: {', '.join(security_check['issues'])}\n\nPrompt blocked for safety.")]
        
        # Get optimized prompt and model
        prompt_data = self.prompt_manager.get_prompt(category, context)
        
        # Select best model
        specified_model = args.get("model")
        if specified_model and specified_model in self.available_models:
            selected_model = specified_model
        else:
            selected_model = self.prompt_manager.get_best_model(category, self.available_models)
        
        # Construct enhanced prompt
        system_prompt = prompt_data["system"]
        enhanced_prompt = f"{system_prompt}\n\nUser Request: {security_check['sanitized']}"
        
        payload = {
            "prompt": enhanced_prompt,
            "model": selected_model,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEMO_TOKEN}"
        }
        
        # Choose endpoint based on model
        if selected_model.startswith("sonar"):
            endpoint = f"{AI_PLATFORM_BASE_URL}/api/v1/ai/search"
            payload = {"query": user_prompt, "model": selected_model, "max_tokens": max_tokens}
        else:
            endpoint = f"{AI_PLATFORM_BASE_URL}/api/v1/ai/generate"
        
        try:
            async with self.session.post(endpoint, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "No response")
                    
                    # Enhanced response formatting
                    formatted_response = f"**Enhanced AI Response** ({selected_model})\n"
                    formatted_response += f"*Category: {category.replace('_', ' ').title()}*\n\n"
                    formatted_response += f"{content}\n\n"
                    
                    if "usage" in data:
                        usage = data["usage"]
                        formatted_response += f"📊 *Usage: {usage.get('input_tokens', 0)} in → {usage.get('output_tokens', 0)} out*\n"
                    
                    formatted_response += f"⏱️ *Processing: {data.get('processing_time_ms', 0)}ms*\n"
                    formatted_response += f"🛡️ *Security: Validated*"
                    
                    return [TextContent(type="text", text=formatted_response)]
                else:
                    error_text = await response.text()
                    return [TextContent(type="text", text=f"AI Platform Error ({response.status}): {error_text}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Connection error: {str(e)}")]

    async def handle_batch_analysis(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle batch analysis with multiple models"""
        prompt = args["prompt"]
        models = args.get("models", ["claude-3-haiku-20240307", "gpt-4o"])
        
        # Security check
        security_check = self.security_manager.validate_prompt(prompt)
        if not security_check["safe"]:
            return [TextContent(type="text", 
                text=f"Security Warning: Cannot proceed with batch analysis due to security concerns.")]
        
        results = []
        for model in models:
            if model not in self.available_models:
                continue
                
            payload = {
                "prompt": security_check["sanitized"],
                "model": model,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEMO_TOKEN}"
            }
            
            endpoint = f"{AI_PLATFORM_BASE_URL}/api/v1/ai/generate"
            
            try:
                async with self.session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            "model": model,
                            "content": data.get("content", "No response"),
                            "usage": data.get("usage", {}),
                            "time": data.get("processing_time_ms", 0)
                        })
            except Exception as e:
                results.append({
                    "model": model,
                    "content": f"Error: {str(e)}",
                    "usage": {},
                    "time": 0
                })
        
        # Format comparative results
        formatted_response = "**Batch AI Analysis Results**\n\n"
        for i, result in enumerate(results, 1):
            formatted_response += f"## {i}. {result['model'].upper()}\n"
            formatted_response += f"{result['content']}\n\n"
            if result['usage']:
                formatted_response += f"*Tokens: {result['usage'].get('input_tokens', 0)}→{result['usage'].get('output_tokens', 0)} | Time: {result['time']}ms*\n\n"
        
        formatted_response += "---\n*Use batch analysis to compare different AI perspectives on complex problems.*"
        
        return [TextContent(type="text", text=formatted_response)]

    async def handle_prompt_optimization(self, args: Dict[str, Any]) -> List[TextContent]:
        """Optimize prompts based on best practices"""
        original_prompt = args["prompt"]
        target_category = args.get("target_category", "coding_assistant")
        
        # Get category-specific guidance
        prompt_data = self.prompt_manager.get_prompt(target_category)
        
        optimization_suggestions = []
        
        # Basic optimization checks
        if len(original_prompt) < 20:
            optimization_suggestions.append("• Consider adding more context and specific requirements")
        
        if "?" not in original_prompt and not original_prompt.endswith('.'):
            optimization_suggestions.append("• End with a clear question or specific request")
        
        if original_prompt.isupper():
            optimization_suggestions.append("• Use normal capitalization for better readability")
        
        if target_category == "coding_assistant" and "code" not in original_prompt.lower():
            optimization_suggestions.append("• Specify the programming language or framework")
        
        # Generate optimized version
        optimized_prompt = f"{prompt_data['system']}\n\nOptimized Request: {original_prompt}"
        
        if not optimization_suggestions:
            optimization_suggestions.append("• Your prompt is well-structured!")
        
        result = f"**Prompt Optimization Analysis**\n\n"
        result += f"**Original:** {original_prompt}\n\n"
        result += f"**Category:** {target_category.replace('_', ' ').title()}\n\n"
        result += f"**Suggestions:**\n" + "\n".join(optimization_suggestions) + "\n\n"
        result += f"**Recommended Model:** {self.prompt_manager.get_best_model(target_category, self.available_models)}\n\n"
        result += f"**Context Keywords:** {prompt_data.get('context', 'General')}"
        
        return [TextContent(type="text", text=result)]

    async def handle_security_check(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform security validation on content"""
        content = args["content"]
        
        security_result = self.security_manager.validate_prompt(content)
        
        result = f"**Security Validation Report**\n\n"
        result += f"**Status:** {'✅ Safe' if security_result['safe'] else '⚠️ Potential Issues Detected'}\n\n"
        
        if security_result["issues"]:
            result += f"**Issues Found:**\n"
            for issue in security_result["issues"]:
                result += f"• {issue}\n"
            result += "\n"
        
        result += f"**Content Length:** {len(content)} characters\n"
        result += f"**Sanitization Applied:** {'Yes' if content != security_result['sanitized'] else 'No'}\n\n"
        
        if not security_result["safe"]:
            result += "**Recommendation:** Review and modify content before processing."
        else:
            result += "**Recommendation:** Content is safe to process."
        
        return [TextContent(type="text", text=result)]

    async def handle_platform_health(self) -> List[TextContent]:
        """Enhanced platform health check"""
        headers = {"Authorization": f"Bearer {DEMO_TOKEN}"}
        
        try:
            async with self.session.get(f"{AI_PLATFORM_BASE_URL}/api/v1/health", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    health_report = "**🏥 AI Platform Health Status**\n\n"
                    health_report += f"• **Status**: {data.get('status', 'Unknown')}\n"
                    health_report += f"• **Version**: {data.get('version', 'Unknown')}\n"
                    health_report += f"• **Uptime**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    
                    services = data.get('services', {})
                    health_report += "**🔧 Service Status:**\n"
                    for service, status in services.items():
                        emoji = "✅" if status in ["configured", "operational", "healthy"] else "❌"
                        health_report += f"• {emoji} **{service.title()}**: {status}\n"
                    
                    health_report += f"\n**🤖 Available Models:** {len(self.available_models)}\n"
                    health_report += f"**🛡️ Security**: Active\n"
                    health_report += f"**📝 Prompt Categories**: {len(self.prompt_manager.prompts)}\n"
                    
                    return [TextContent(type="text", text=health_report)]
                else:
                    return [TextContent(type="text", text=f"Health check failed: {response.status}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Health check error: {str(e)}")]

    async def run(self):
        """Run the enhanced MCP server"""
        self.setup_handlers()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ai-platform-mcp-enhanced",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={
                            "smart_prompts": True,
                            "security_validation": True,
                            "batch_analysis": True
                        },
                    ),
                )
            )

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main entry point for enhanced AI Platform MCP Server"""
    server = EnhancedAIPlatformMCPServer()
    try:
        logging.info("Starting Enhanced AI Platform MCP Server...")
        await server.run()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
    finally:
        await server.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())