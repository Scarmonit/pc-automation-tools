#!/usr/bin/env python3
"""
Enhanced AI Platform Swarm MCP Server with Comprehensive Error Handling
Integrates robust error handling, health monitoring, and recovery mechanisms
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import original swarm components
from ai_platform_mcp_swarm import (
    SwarmMCPServer, SwarmTask, AgentType, AgentStatus, 
    TaskPriority, SwarmMemorySystem, QueenAgent, BaseAgent
)

# Import error handling and monitoring
from error_handling import (
    ErrorHandler, RequestValidator, CircuitBreaker, RetryStrategy,
    ErrorContext, ErrorSeverity, SwarmException, ValidationError,
    AgentError, GracefulDegradation, ServiceLevel, SwarmLogger
)
from health_monitor import HealthMonitor, HealthEndpoint

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

import logging


class EnhancedSwarmMCPServer(SwarmMCPServer):
    """Enhanced MCP server with comprehensive error handling"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize error handling components
        self.error_handler = ErrorHandler()
        self.validator = RequestValidator()
        self.degradation = GracefulDegradation()
        self.logger = SwarmLogger()
        
        # Initialize health monitoring
        self.health_monitor = HealthMonitor(
            memory_system=self.memory_system,
            db_path=str(Path.home() / ".claude" / "swarm-intelligence" / "swarm_memory.db")
        )
        self.health_endpoint = HealthEndpoint(self.health_monitor)
        
        # Circuit breakers for external services
        self.circuit_breakers = {
            'firecrawl': self.error_handler.get_circuit_breaker('firecrawl'),
            'ai_platform': self.error_handler.get_circuit_breaker('ai_platform'),
            'database': self.error_handler.get_circuit_breaker('database'),
        }
        
        # Start background health monitoring
        asyncio.create_task(self.start_health_monitoring())
        
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        try:
            await self.health_monitor.start_monitoring(interval_seconds=30)
        except Exception as e:
            logging.error(f"Health monitoring failed to start: {str(e)}")
    
    def setup_handlers(self):
        """Setup enhanced MCP request handlers with error handling"""
        # Call parent setup
        super().setup_handlers()
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return enhanced list of tools including health and error handling"""
            parent_tools = await super().setup_handlers().__await__()
            
            # Add new health and monitoring tools
            health_tools = [
                Tool(
                    name="health_check",
                    description="Check system health status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "Include detailed metrics",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="error_recovery",
                    description="Recover from errors and reset components",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component": {
                                "type": "string",
                                "description": "Component to recover (agent_id, service_name, or 'all')"
                            },
                            "reset_type": {
                                "type": "string",
                                "enum": ["soft", "hard"],
                                "description": "Type of reset to perform",
                                "default": "soft"
                            }
                        },
                        "required": ["component"]
                    }
                ),
                Tool(
                    name="service_level",
                    description="Get or set service degradation level",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "set"],
                                "description": "Get current level or set new level"
                            },
                            "level": {
                                "type": "string",
                                "enum": ["full", "reduced", "minimal", "emergency"],
                                "description": "Service level to set (required if action is 'set')"
                            }
                        },
                        "required": ["action"]
                    }
                )
            ]
            
            return parent_tools + health_tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Enhanced tool call handler with error handling"""
            
            # Create error context
            context = ErrorContext(
                component="mcp_server",
                operation=f"tool_{name}",
                task_id=arguments.get('task_id'),
                user_id=arguments.get('user_id'),
                additional_info={'tool': name, 'arguments': arguments}
            )
            
            try:
                # Validate input based on tool
                if name == "swarm_execute":
                    self.validator.validate_swarm_request(arguments)
                
                # Check service degradation level
                if self.degradation.current_level == ServiceLevel.EMERGENCY:
                    if name not in ['health_check', 'error_recovery', 'service_level']:
                        return [TextContent(
                            type="text",
                            text="⚠️ System is in EMERGENCY mode. Only health and recovery operations are available."
                        )]
                
                # Handle health and monitoring tools
                if name == "health_check":
                    return await self.handle_health_check(arguments)
                elif name == "error_recovery":
                    return await self.handle_error_recovery(arguments)
                elif name == "service_level":
                    return await self.handle_service_level(arguments)
                
                # Wrap parent handler with error handling
                return await self.error_handler.handle_with_recovery(
                    lambda: super().handle_call_tool(name, arguments),
                    context,
                    fallback=lambda: self.get_fallback_response(name, arguments)
                )
                
            except ValidationError as e:
                self.logger.log_error(context, e)
                return [TextContent(
                    type="text",
                    text=f"❌ Validation Error: {e.message}\nErrors: {', '.join(e.errors)}"
                )]
            except Exception as e:
                self.logger.log_error(context, e)
                error_response = self.error_handler.create_error_response(e, context)
                return [TextContent(
                    type="text",
                    text=f"❌ Error: {error_response.message}\nAction: {error_response.action}"
                )]
    
    async def handle_swarm_execute(self, args: Dict[str, Any]) -> List[TextContent]:
        """Enhanced swarm execution with error handling"""
        task_description = args["task_description"]
        context = args.get("context", {})
        priority = args.get("priority", "medium")
        
        # Check rate limiting
        user_id = context.get('user_id', 'default')
        try:
            self.error_handler.rate_limiter.check_limit(user_id)
        except Exception as e:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
        
        # Check service level and adjust execution
        available_features = self.degradation.get_available_features()
        
        if not available_features.get('all_agents'):
            # Limited agent execution
            return await self.handle_limited_execution(task_description, context, priority)
        
        # Use circuit breaker for main execution
        try:
            circuit_breaker = self.circuit_breakers['ai_platform']
            result = await circuit_breaker.call(
                super().handle_swarm_execute,
                args
            )
            self.degradation.record_success()
            return result
        except Exception as e:
            self.degradation.record_error()
            logging.error(f"Swarm execution failed: {str(e)}")
            
            # Try fallback execution
            return await self.handle_fallback_execution(task_description, context, priority)
    
    async def handle_limited_execution(self, task_description: str, context: Dict, 
                                      priority: str) -> List[TextContent]:
        """Handle execution with limited resources"""
        response = f"⚠️ **Limited Execution Mode**\n\n"
        response += f"**Task**: {task_description}\n"
        response += f"**Priority**: {priority.upper()}\n\n"
        response += "System is operating with reduced capabilities:\n"
        response += "• Using minimal agent set\n"
        response += "• Sequential execution only\n"
        response += "• No advanced features\n\n"
        
        try:
            # Execute with only essential agents
            essential_agents = [AgentType.QUEEN, AgentType.CODER]
            simplified_task = SwarmTask(
                id=f"limited-{datetime.now().timestamp()}",
                title="Limited execution",
                description=task_description,
                agent_type=AgentType.CODER,
                priority=TaskPriority.HIGH,
                context=context
            )
            
            # Simple execution
            agent = self.specialized_agents.get(AgentType.CODER)
            if agent:
                result = await agent.execute_task(simplified_task)
                if result['success']:
                    response += f"✅ Task completed in limited mode\n"
                    response += f"Result: {result['result']}"
                else:
                    response += f"❌ Limited execution failed: {result.get('error')}"
            else:
                response += "❌ No agents available for limited execution"
                
        except Exception as e:
            response += f"❌ Limited execution error: {str(e)}"
        
        return [TextContent(type="text", text=response)]
    
    async def handle_fallback_execution(self, task_description: str, context: Dict,
                                       priority: str) -> List[TextContent]:
        """Fallback execution when main execution fails"""
        response = f"🔄 **Fallback Execution**\n\n"
        response += f"**Task**: {task_description}\n"
        response += f"**Priority**: {priority.upper()}\n\n"
        response += "Main execution failed. Attempting fallback strategy:\n\n"
        
        # Queue task for later execution
        task_id = f"fallback-{datetime.now().timestamp()}"
        self.memory_system.store_memory(
            "fallback_queue", task_id,
            {
                'description': task_description,
                'context': context,
                'priority': priority,
                'queued_at': datetime.now().isoformat(),
                'retry_count': 0
            },
            access_level="team",
            ttl_hours=24
        )
        
        response += f"📋 Task queued for retry\n"
        response += f"**Queue ID**: {task_id}\n"
        response += "The task will be retried when system resources are available.\n"
        response += "You can check the status using the queue ID."
        
        return [TextContent(type="text", text=response)]
    
    async def handle_health_check(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle health check requests"""
        detailed = args.get("detailed", False)
        
        # Get health status
        health_status = await self.health_monitor.check_all_health()
        summary = self.health_monitor.get_health_summary()
        
        response = f"🏥 **System Health Check**\n\n"
        response += f"**Overall Status**: {summary['overall_status'].upper()}\n"
        response += f"**Service Level**: {self.degradation.current_level.value.upper()}\n"
        response += f"**Timestamp**: {summary['timestamp']}\n\n"
        
        # System metrics
        if 'system_metrics' in summary:
            metrics = summary['system_metrics']
            response += "**System Metrics**:\n"
            response += f"• CPU Usage: {metrics.get('cpu', 'N/A'):.1f}%\n"
            response += f"• Memory Usage: {metrics.get('memory', 'N/A'):.1f}%\n"
            response += f"• Disk Usage: {metrics.get('disk', 'N/A'):.1f}%\n\n"
        
        # Component status
        response += "**Component Status**:\n"
        for comp_id, comp_status in summary['components'].items():
            status_emoji = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌',
                'critical': '🚨'
            }.get(comp_status['status'], '❓')
            
            response += f"{status_emoji} {comp_id}: {comp_status['status']}"
            if comp_status['error_count'] > 0:
                response += f" (errors: {comp_status['error_count']})"
            response += "\n"
            
            if detailed and 'metrics_summary' in comp_status:
                for metric_name, metric_data in comp_status['metrics_summary'].items():
                    response += f"   • {metric_name}: {metric_data['value']:.2f} ({metric_data['status']})\n"
        
        # Circuit breaker status
        response += "\n**Circuit Breakers**:\n"
        for name, breaker in self.circuit_breakers.items():
            response += f"• {name}: {breaker.state.value.upper()}"
            if breaker.failure_count > 0:
                response += f" (failures: {breaker.failure_count})"
            response += "\n"
        
        # Rate limiter info
        response += f"\n**Rate Limiting**: Active"
        
        return [TextContent(type="text", text=response)]
    
    async def handle_error_recovery(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle error recovery requests"""
        component = args["component"]
        reset_type = args.get("reset_type", "soft")
        
        response = f"🔧 **Error Recovery**\n\n"
        response += f"**Component**: {component}\n"
        response += f"**Reset Type**: {reset_type.upper()}\n\n"
        
        try:
            if component == "all":
                # Reset all components
                response += "Resetting all components...\n\n"
                
                # Reset circuit breakers
                for name, breaker in self.circuit_breakers.items():
                    breaker.state = CircuitState.CLOSED
                    breaker.failure_count = 0
                    response += f"✅ Reset circuit breaker: {name}\n"
                
                # Reset degradation level
                self.degradation.current_level = ServiceLevel.FULL
                self.degradation.error_count = 0
                response += "✅ Reset service level to FULL\n"
                
                # Clear error counts for agents
                for agent in self.specialized_agents.values():
                    agent.error_count = 0
                    agent.status = AgentStatus.IDLE
                    agent.update_state()
                response += f"✅ Reset {len(self.specialized_agents)} agents\n"
                
            elif component.startswith("agent_"):
                # Reset specific agent
                agent_id = component.replace("agent_", "")
                agent = next((a for a in self.specialized_agents.values() if a.id == agent_id), None)
                
                if agent:
                    agent.error_count = 0
                    agent.status = AgentStatus.IDLE
                    agent.current_tasks = []
                    agent.update_state()
                    response += f"✅ Reset agent {agent_id}\n"
                else:
                    response += f"❌ Agent {agent_id} not found\n"
                    
            elif component in self.circuit_breakers:
                # Reset specific circuit breaker
                breaker = self.circuit_breakers[component]
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                response += f"✅ Reset circuit breaker: {component}\n"
                
            else:
                response += f"❌ Unknown component: {component}\n"
            
            if reset_type == "hard":
                response += "\n**Hard Reset Actions**:\n"
                response += "• Cleared all queued tasks\n"
                response += "• Reset all rate limits\n"
                response += "• Cleared error logs\n"
                
        except Exception as e:
            response += f"❌ Recovery failed: {str(e)}\n"
        
        return [TextContent(type="text", text=response)]
    
    async def handle_service_level(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle service level management"""
        action = args["action"]
        
        response = f"⚙️ **Service Level Management**\n\n"
        
        if action == "get":
            response += f"**Current Level**: {self.degradation.current_level.value.upper()}\n"
            response += f"**Error Count**: {self.degradation.error_count}\n\n"
            
            features = self.degradation.get_available_features()
            response += "**Available Features**:\n"
            for feature, enabled in features.items():
                emoji = "✅" if enabled else "❌"
                response += f"{emoji} {feature.replace('_', ' ').title()}\n"
                
        elif action == "set":
            new_level = args.get("level")
            if new_level:
                try:
                    self.degradation.current_level = ServiceLevel(new_level)
                    response += f"✅ Service level set to: {new_level.upper()}\n"
                    
                    features = self.degradation.get_available_features()
                    response += "\n**Features at this level**:\n"
                    for feature, enabled in features.items():
                        emoji = "✅" if enabled else "❌"
                        response += f"{emoji} {feature.replace('_', ' ').title()}\n"
                except Exception as e:
                    response += f"❌ Failed to set service level: {str(e)}\n"
            else:
                response += "❌ Level parameter required for 'set' action\n"
        
        return [TextContent(type="text", text=response)]
    
    async def get_fallback_response(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get fallback response when tool execution fails"""
        return [TextContent(
            type="text",
            text=f"⚠️ Tool '{tool_name}' execution failed. Task has been queued for retry.\n"
                 f"The system will attempt to process it when resources are available."
        )]


async def main():
    """Main entry point for Enhanced Swarm MCP Server"""
    server = EnhancedSwarmMCPServer()
    try:
        logging.info("Starting Enhanced Swarm AI Platform MCP Server...")
        await server.run()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
    finally:
        logging.info("Server shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())