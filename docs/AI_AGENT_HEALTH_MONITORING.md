# 🏥 AI Agent Health Monitoring Guide

## Overview

The enhanced AI agent integration system now includes comprehensive health monitoring, standardized logging, and robust error handling for all AI frameworks.

## Enhanced Features

### 🔍 Health Check System

All AI agents now implement a standardized `health_check()` method that returns detailed status information:

```python
{
    "name": "AgentName",
    "status": "healthy|unhealthy|degraded",
    "timestamp": 1694123456.789,
    "response_time": 0.123,
    "details": {
        "specific_checks": "results"
    },
    "error": "Error message if any"
}
```

### 📊 Agent Status Monitoring

#### Individual Agent Health Checks

```python
from llmstack.ai_frameworks_integration import UnifiedAIOrchestrator, AIConfig

# Initialize with enhanced configuration
config = AIConfig(
    health_check_timeout=10,
    retry_attempts=3,
    retry_delay=1.0
)

orchestrator = UnifiedAIOrchestrator(config)

# Check individual agent health
localai_health = orchestrator.localai.health_check()
autogen_health = orchestrator.autogen.health_check()
```

#### Comprehensive System Health Check

```python
# Get overall system health
health_report = orchestrator.comprehensive_health_check()

print(f"Overall Status: {health_report['overall_status']}")
print(f"Healthy Agents: {health_report['summary']['healthy_agents']}")
print(f"Health Percentage: {health_report['summary']['health_percentage']}%")
```

### 🤖 Agent Registry

Get detailed information about all registered agents:

```python
registry = orchestrator.get_agent_registry()

for agent_name, info in registry.items():
    print(f"Agent: {agent_name}")
    print(f"  Class: {info['class']}")
    print(f"  Status: {'✅ Healthy' if info['health_status'] else '❌ Unhealthy'}")
    print(f"  Last Check: {info['last_health_check']}")
```

## Enhanced Configuration Options

### New AIConfig Parameters

```python
@dataclass
class AIConfig:
    # Existing parameters...
    health_check_timeout: int = 10      # Timeout for health checks
    retry_attempts: int = 3             # Number of retry attempts
    retry_delay: float = 1.0           # Delay between retries
```

### Usage Examples

```python
# Quick health check configuration
config = AIConfig(health_check_timeout=5, retry_attempts=2)

# Production configuration with longer timeouts
config = AIConfig(
    health_check_timeout=30,
    retry_attempts=5,
    retry_delay=2.0
)
```

## 📝 Enhanced Logging

### Logging Patterns

All agents now use consistent emoji-based logging:

- 🚀 **Initialization**: Agent startup and configuration
- 🔍 **Health Checks**: Health monitoring activities
- 🤖 **Operations**: Chat processing and task execution
- ✅ **Success**: Successful operations
- ❌ **Errors**: Failed operations
- ⚠️ **Warnings**: Retry attempts and degraded states

### Example Log Output

```
2025-09-07 22:30:09,029 - ai_frameworks_integration - INFO - 🚀 Initializing Unified AI Orchestrator
2025-09-07 22:30:09,069 - ai_frameworks_integration - INFO - 🔍 Starting health check for LocalAI
2025-09-07 22:30:09,071 - ai_frameworks_integration - ERROR - ❌ LocalAI health check failed: Connection refused
2025-09-07 22:30:09,073 - ai_frameworks_integration - INFO - 🏥 Health check completed: 0/4 agents healthy (0.0%)
```

## 🔧 Multi-Agent Task Execution

### Enhanced Multi-Agent Tasks

```python
# Execute task with multiple agents
results = orchestrator.multi_agent_task(
    "Analyze this code for improvements",
    agents=["autogen", "camel"]
)

for agent_name, result in results.items():
    print(f"{agent_name}: {result['status']}")
    print(f"Response Time: {result['response_time']:.2f}s")
    print(f"Result: {result['result']}")
```

### Async Multi-Agent Execution

```python
import asyncio

# Execute task asynchronously
async def run_async_task():
    results = await orchestrator.async_multi_agent(
        "Generate documentation for this API",
        agents=["localai", "autogen"]
    )
    return results

# Run the async task
results = asyncio.run(run_async_task())
```

## 🛠️ Error Handling and Retry Logic

### Automatic Retry Mechanism

The enhanced system includes automatic retry logic with exponential backoff:

```python
# This will automatically retry failed operations
result = localai_client.chat_completion([
    {"role": "user", "content": "Hello"}
])

# Logs will show retry attempts:
# ⚠️ LocalAI attempt 1 failed: Connection error
# ⚠️ LocalAI attempt 2 failed: Connection error  
# ❌ LocalAI all attempts failed
```

### Graceful Failure Handling

All agents handle failures gracefully and provide informative error messages:

```python
# Even if agents are unavailable, the system continues to function
result = orchestrator.chat("Hello", framework="unavailable_agent")
print(result)  # "Unknown framework 'unavailable_agent'. Available: localai, memgpt, autogen, camel"
```

## 📈 Monitoring Integration

### Health Check Scheduling

For production deployments, you can schedule regular health checks:

```python
import schedule
import time

def perform_health_check():
    health_report = orchestrator.comprehensive_health_check()
    
    if health_report['overall_status'] != 'healthy':
        # Send alert or take corrective action
        print(f"⚠️ System health degraded: {health_report['summary']}")

# Schedule health checks every 5 minutes
schedule.every(5).minutes.do(perform_health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Integration with Monitoring Systems

The health check data can be easily integrated with monitoring systems like Prometheus:

```python
def export_health_metrics():
    health_report = orchestrator.comprehensive_health_check()
    
    # Export to Prometheus, Grafana, etc.
    metrics = {
        'ai_agents_total': health_report['summary']['total_agents'],
        'ai_agents_healthy': health_report['summary']['healthy_agents'],
        'ai_health_percentage': health_report['summary']['health_percentage']
    }
    
    return metrics
```

## 🧪 Testing Enhanced Features

Run the comprehensive test suite to validate all enhancements:

```bash
# Run enhanced AI integration tests
python3 test_enhanced_ai_integration.py

# Run all tests including existing ones
python3 test_automation.py
```

## Best Practices

1. **Regular Health Checks**: Schedule periodic health checks in production
2. **Monitor Response Times**: Track agent response times for performance optimization
3. **Configure Timeouts**: Set appropriate timeouts based on your infrastructure
4. **Log Analysis**: Monitor logs for patterns of failures or degraded performance
5. **Graceful Degradation**: Design your applications to handle agent unavailability

## Next Steps

- Set up monitoring dashboards using the health check data
- Configure alerting for critical agent failures
- Implement load balancing for multiple agent instances
- Add custom health checks for specific use cases