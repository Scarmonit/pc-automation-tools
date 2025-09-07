#!/usr/bin/env python3
"""
Distributed Agent Swarm - Massive parallel security analysis with distributed agents
Scalable multi-agent system for enterprise-level deep security analysis
"""

import asyncio
import aiohttp
import json
import time
import uuid
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
import multiprocessing as mp
from queue import Queue
import threading
import hashlib

from parallel_security_orchestrator import (
    SecurityAgent, AgentType, AgentTask, 
    ParallelSecurityOrchestrator, ParallelAnalysisResult
)


@dataclass 
class SwarmNode:
    """Individual node in the distributed swarm"""
    node_id: str
    node_type: str
    capacity: int
    current_load: int = 0
    status: str = "active"
    agents: List[SecurityAgent] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class SwarmTask:
    """Task for distributed execution"""
    task_id: str
    target: str
    priority: int
    task_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    assigned_node: Optional[str] = None
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    retries: int = 0
    max_retries: int = 3


@dataclass
class SwarmAnalysisResult:
    """Aggregated results from distributed swarm analysis"""
    swarm_id: str
    targets_analyzed: List[str]
    total_nodes: int
    total_agents: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_findings: int
    critical_findings: int
    execution_time: float
    node_metrics: Dict[str, Any] = field(default_factory=dict)
    aggregated_results: Dict[str, Any] = field(default_factory=dict)
    threat_intelligence: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class DistributedAgentSwarm:
    """Distributed swarm coordinator for massive parallel analysis"""
    
    def __init__(self, num_nodes: int = 4, agents_per_node: int = 5):
        self.swarm_id = str(uuid.uuid4())[:8]
        self.num_nodes = num_nodes
        self.agents_per_node = agents_per_node
        self.nodes = {}
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Performance metrics
        self.metrics = {
            "tasks_processed": 0,
            "avg_task_time": 0,
            "node_utilization": {},
            "agent_performance": defaultdict(lambda: {"tasks": 0, "avg_time": 0})
        }
        
    async def initialize_swarm(self):
        """Initialize the distributed swarm network"""
        print(f"Initializing Distributed Agent Swarm [{self.swarm_id}]")
        print(f"Deploying {self.num_nodes} nodes with {self.agents_per_node} agents each")
        print("-" * 60)
        
        # Create swarm nodes
        node_types = ["scanner", "analyzer", "correlator", "explorer"]
        
        for i in range(self.num_nodes):
            node_id = f"node_{i:02d}"
            node_type = node_types[i % len(node_types)]
            
            node = SwarmNode(
                node_id=node_id,
                node_type=node_type,
                capacity=self.agents_per_node
            )
            
            # Initialize agents for this node
            await self._initialize_node_agents(node)
            
            self.nodes[node_id] = node
            self.metrics["node_utilization"][node_id] = 0
            
            print(f"  Node {node_id} ({node_type}): {len(node.agents)} agents ready")
        
        print(f"\nSwarm initialized: {len(self.nodes)} nodes, "
              f"{sum(len(n.agents) for n in self.nodes.values())} total agents")
    
    async def _initialize_node_agents(self, node: SwarmNode):
        """Initialize agents for a specific node"""
        agent_types_by_node = {
            "scanner": [
                AgentType.WEB_CRAWLER, 
                AgentType.STEALTH_INFILTRATOR,
                AgentType.PATTERN_HUNTER
            ],
            "analyzer": [
                AgentType.VULNERABILITY_ANALYZER,
                AgentType.PATTERN_HUNTER,
                AgentType.DEEP_EXPLORER
            ],
            "correlator": [
                AgentType.THREAT_CORRELATOR,
                AgentType.RISK_ASSESSOR,
                AgentType.PATTERN_HUNTER
            ],
            "explorer": [
                AgentType.DEEP_EXPLORER,
                AgentType.RECONNAISSANCE,
                AgentType.WEB_CRAWLER
            ]
        }
        
        available_types = agent_types_by_node.get(
            node.node_type, 
            list(AgentType)
        )
        
        for i in range(node.capacity):
            agent_type = random.choice(available_types)
            agent_id = f"{node.node_id}_agent_{i:02d}"
            agent = SecurityAgent(agent_id, agent_type)
            node.agents.append(agent)
    
    async def execute_swarm_analysis(self, targets: List[str], 
                                    analysis_depth: str = "comprehensive") -> SwarmAnalysisResult:
        """Execute distributed swarm analysis on multiple targets"""
        start_time = time.time()
        
        print(f"\nStarting Distributed Swarm Analysis")
        print(f"Targets: {len(targets)}")
        print(f"Analysis depth: {analysis_depth}")
        print("-" * 60)
        
        # Create swarm result container
        result = SwarmAnalysisResult(
            swarm_id=self.swarm_id,
            targets_analyzed=targets,
            total_nodes=len(self.nodes),
            total_agents=sum(len(n.agents) for n in self.nodes.values()),
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            total_findings=0,
            critical_findings=0,
            execution_time=0
        )
        
        # Phase 1: Task generation
        print("\nPhase 1: Generating analysis tasks")
        tasks = await self._generate_swarm_tasks(targets, analysis_depth)
        result.total_tasks = len(tasks)
        
        # Phase 2: Task distribution
        print(f"Phase 2: Distributing {len(tasks)} tasks across {len(self.nodes)} nodes")
        await self._distribute_tasks(tasks)
        
        # Phase 3: Parallel execution
        print("Phase 3: Executing parallel analysis")
        execution_results = await self._execute_distributed_tasks()
        
        # Phase 4: Result aggregation
        print("Phase 4: Aggregating results")
        await self._aggregate_swarm_results(execution_results, result)
        
        # Phase 5: Threat correlation
        print("Phase 5: Correlating threats across targets")
        await self._correlate_swarm_threats(result)
        
        # Phase 6: Generate recommendations
        print("Phase 6: Generating recommendations")
        self._generate_swarm_recommendations(result)
        
        # Calculate final metrics
        result.execution_time = time.time() - start_time
        result.completed_tasks = len(self.completed_tasks)
        result.failed_tasks = len(self.failed_tasks)
        
        # Update node metrics
        for node_id, node in self.nodes.items():
            result.node_metrics[node_id] = {
                "agents": len(node.agents),
                "load": node.current_load,
                "status": node.status,
                "tasks_processed": node.metrics.get("tasks_processed", 0)
            }
        
        print(f"\n" + "=" * 60)
        print("DISTRIBUTED SWARM ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Swarm ID: {self.swarm_id}")
        print(f"Execution time: {result.execution_time:.2f}s")
        print(f"Tasks completed: {result.completed_tasks}/{result.total_tasks}")
        print(f"Total findings: {result.total_findings}")
        print(f"Critical findings: {result.critical_findings}")
        
        return result
    
    async def _generate_swarm_tasks(self, targets: List[str], 
                                   depth: str) -> List[SwarmTask]:
        """Generate distributed tasks for all targets"""
        tasks = []
        
        # Define task parameters based on depth
        if depth == "quick":
            max_pages, scan_depth = 5, 1
        elif depth == "standard":
            max_pages, scan_depth = 20, 2
        else:  # comprehensive
            max_pages, scan_depth = 50, 3
        
        for target in targets:
            domain = self._extract_domain(target)
            
            # Generate diverse task types for each target
            task_types = [
                ("reconnaissance", 1),
                ("web_scan", 2),
                ("stealth_scan", 2),
                ("deep_crawl", 3),
                ("pattern_hunt", 3),
                ("vulnerability_analysis", 4),
                ("threat_correlation", 5)
            ]
            
            for task_type, priority in task_types:
                task = SwarmTask(
                    task_id=f"{task_type}_{uuid.uuid4().hex[:8]}",
                    target=target,
                    priority=priority,
                    task_type=task_type,
                    parameters={
                        "domain": domain,
                        "max_pages": max_pages,
                        "depth": scan_depth,
                        "analysis_depth": depth
                    }
                )
                tasks.append(task)
        
        return tasks
    
    async def _distribute_tasks(self, tasks: List[SwarmTask]):
        """Distribute tasks across swarm nodes"""
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        # Round-robin distribution with load balancing
        node_list = list(self.nodes.values())
        node_index = 0
        
        for task in sorted_tasks:
            # Find least loaded node
            least_loaded_node = min(node_list, key=lambda n: n.current_load)
            
            task.assigned_node = least_loaded_node.node_id
            least_loaded_node.current_load += 1
            
            await self.task_queue.put(task)
            self.active_tasks[task.task_id] = task
    
    async def _execute_distributed_tasks(self) -> Dict[str, Any]:
        """Execute tasks in parallel across all nodes"""
        execution_tasks = []
        
        # Create execution tasks for each node
        for node_id, node in self.nodes.items():
            execution_task = asyncio.create_task(
                self._node_execution_loop(node)
            )
            execution_tasks.append(execution_task)
        
        # Wait for all nodes to complete their tasks
        await asyncio.gather(*execution_tasks)
        
        return self.completed_tasks
    
    async def _node_execution_loop(self, node: SwarmNode):
        """Execution loop for a single node"""
        while not self.task_queue.empty():
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                if task.assigned_node != node.node_id:
                    # Task not for this node, put it back
                    await self.task_queue.put(task)
                    continue
                
                # Find available agent for this task type
                agent = self._find_agent_for_task(node, task)
                
                if agent:
                    # Execute task
                    task.started_at = time.time()
                    task.status = "executing"
                    
                    result = await self._execute_agent_task(agent, task)
                    
                    task.completed_at = time.time()
                    task.status = "completed"
                    task.result = result
                    
                    # Update metrics
                    node.current_load -= 1
                    node.metrics["tasks_processed"] = node.metrics.get("tasks_processed", 0) + 1
                    
                    # Store completed task
                    self.completed_tasks[task.task_id] = task
                    del self.active_tasks[task.task_id]
                    
                else:
                    # No suitable agent, retry later
                    task.retries += 1
                    if task.retries < task.max_retries:
                        await self.task_queue.put(task)
                    else:
                        task.status = "failed"
                        self.failed_tasks[task.task_id] = task
                        del self.active_tasks[task.task_id]
                
            except asyncio.TimeoutError:
                # No more tasks for now
                continue
            except Exception as e:
                print(f"Node {node.node_id} execution error: {e}")
    
    def _find_agent_for_task(self, node: SwarmNode, task: SwarmTask) -> Optional[SecurityAgent]:
        """Find suitable agent for task type"""
        task_to_agent_mapping = {
            "reconnaissance": AgentType.RECONNAISSANCE,
            "web_scan": AgentType.WEB_CRAWLER,
            "stealth_scan": AgentType.STEALTH_INFILTRATOR,
            "deep_crawl": AgentType.DEEP_EXPLORER,
            "pattern_hunt": AgentType.PATTERN_HUNTER,
            "vulnerability_analysis": AgentType.VULNERABILITY_ANALYZER,
            "threat_correlation": AgentType.THREAT_CORRELATOR
        }
        
        required_type = task_to_agent_mapping.get(task.task_type)
        
        if required_type:
            for agent in node.agents:
                if agent.agent_type == required_type and agent.status == "idle":
                    return agent
        
        # Fallback to any available agent
        for agent in node.agents:
            if agent.status == "idle":
                return agent
        
        return None
    
    async def _execute_agent_task(self, agent: SecurityAgent, task: SwarmTask) -> Any:
        """Execute a task with a specific agent"""
        # Convert SwarmTask to AgentTask
        agent_task = AgentTask(
            task_id=task.task_id,
            agent_type=agent.agent_type,
            target=task.target,
            priority=task.priority,
            parameters=task.parameters
        )
        
        # Execute and return result
        result = await agent.execute_task(agent_task)
        return result.result if result else None
    
    async def _aggregate_swarm_results(self, execution_results: Dict[str, Any], 
                                      result: SwarmAnalysisResult):
        """Aggregate results from all swarm tasks"""
        all_findings = []
        target_results = defaultdict(list)
        
        # Group results by target
        for task_id, task in self.completed_tasks.items():
            if task.result:
                target_results[task.target].append(task.result)
                
                # Extract findings
                if isinstance(task.result, dict):
                    if "findings" in task.result:
                        all_findings.extend(task.result["findings"])
                    if "security_findings" in task.result:
                        all_findings.extend(task.result["security_findings"])
        
        # Count critical findings
        for finding in all_findings:
            if hasattr(finding, 'risk_level') and finding.risk_level == 'CRITICAL':
                result.critical_findings += 1
        
        result.total_findings = len(all_findings)
        result.aggregated_results = dict(target_results)
    
    async def _correlate_swarm_threats(self, result: SwarmAnalysisResult):
        """Correlate threats across all targets"""
        threat_patterns = defaultdict(list)
        cross_target_threats = []
        
        # Analyze patterns across targets
        for target, target_results in result.aggregated_results.items():
            for task_result in target_results:
                if isinstance(task_result, dict) and "findings" in task_result:
                    for finding in task_result["findings"]:
                        if hasattr(finding, 'pattern_type'):
                            threat_patterns[finding.pattern_type].append({
                                "target": target,
                                "confidence": getattr(finding, 'confidence', 0),
                                "risk_level": getattr(finding, 'risk_level', 'UNKNOWN')
                            })
        
        # Identify cross-target threats
        for pattern, occurrences in threat_patterns.items():
            if len(occurrences) > 1:
                unique_targets = set(o["target"] for o in occurrences)
                if len(unique_targets) > 1:
                    cross_target_threats.append({
                        "pattern": pattern,
                        "affected_targets": list(unique_targets),
                        "occurrences": len(occurrences),
                        "max_risk": max(o["risk_level"] for o in occurrences)
                    })
        
        result.threat_intelligence = {
            "threat_patterns": dict(threat_patterns),
            "cross_target_threats": cross_target_threats,
            "unique_patterns": len(threat_patterns),
            "pattern_frequency": {
                pattern: len(occurrences) 
                for pattern, occurrences in threat_patterns.items()
            }
        }
    
    def _generate_swarm_recommendations(self, result: SwarmAnalysisResult):
        """Generate recommendations based on swarm analysis"""
        recommendations = []
        
        # Critical finding recommendations
        if result.critical_findings > 0:
            recommendations.append(
                f"CRITICAL: {result.critical_findings} critical vulnerabilities found. "
                "Immediate remediation required across affected targets."
            )
        
        # Cross-target threat recommendations
        cross_threats = result.threat_intelligence.get("cross_target_threats", [])
        if cross_threats:
            recommendations.append(
                f"HIGH: {len(cross_threats)} vulnerability patterns found across multiple targets. "
                "Indicates systemic security issues requiring organization-wide remediation."
            )
        
        # High finding density recommendation
        if result.total_findings > result.total_tasks * 5:
            recommendations.append(
                "HIGH: High vulnerability density detected. "
                "Comprehensive security review and hardening recommended."
            )
        
        # Node performance recommendations
        failed_rate = result.failed_tasks / max(result.total_tasks, 1)
        if failed_rate > 0.1:
            recommendations.append(
                "MEDIUM: High task failure rate detected. "
                "Review target accessibility and scanning configuration."
            )
        
        result.recommendations = recommendations
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def generate_swarm_report(self, result: SwarmAnalysisResult) -> Dict[str, Any]:
        """Generate comprehensive swarm analysis report"""
        return {
            "swarm_metadata": {
                "swarm_id": result.swarm_id,
                "total_nodes": result.total_nodes,
                "total_agents": result.total_agents,
                "targets_analyzed": result.targets_analyzed,
                "execution_time": round(result.execution_time, 2)
            },
            "execution_summary": {
                "total_tasks": result.total_tasks,
                "completed_tasks": result.completed_tasks,
                "failed_tasks": result.failed_tasks,
                "success_rate": round(
                    (result.completed_tasks / max(result.total_tasks, 1)) * 100, 2
                )
            },
            "security_findings": {
                "total_findings": result.total_findings,
                "critical_findings": result.critical_findings,
                "findings_per_target": round(
                    result.total_findings / max(len(result.targets_analyzed), 1), 2
                )
            },
            "threat_intelligence": {
                "unique_patterns": result.threat_intelligence.get("unique_patterns", 0),
                "cross_target_threats": len(
                    result.threat_intelligence.get("cross_target_threats", [])
                ),
                "top_threat_patterns": sorted(
                    result.threat_intelligence.get("pattern_frequency", {}).items(),
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]
            },
            "node_performance": result.node_metrics,
            "recommendations": result.recommendations,
            "detailed_analysis": {
                "timestamp": datetime.now().isoformat(),
                "analysis_depth": "distributed_swarm",
                "parallelism_level": result.total_agents
            }
        }


async def demo_distributed_swarm():
    """Demonstrate distributed agent swarm analysis"""
    print("DISTRIBUTED AGENT SWARM - Massive Parallel Security Analysis")
    print("=" * 70)
    
    # Initialize swarm
    swarm = DistributedAgentSwarm(num_nodes=4, agents_per_node=3)
    await swarm.initialize_swarm()
    
    # Multiple targets for analysis
    targets = [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com",
        "https://reqres.in"
    ]
    
    print(f"\nTargets for analysis: {len(targets)}")
    for target in targets:
        print(f"  - {target}")
    
    # Execute swarm analysis
    result = await swarm.execute_swarm_analysis(
        targets=targets,
        analysis_depth="quick"  # Quick for demo
    )
    
    # Generate report
    report = swarm.generate_swarm_report(result)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"swarm_analysis_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display results
    print("\n" + "=" * 70)
    print("SWARM ANALYSIS RESULTS")
    print("=" * 70)
    print(f"Swarm ID: {result.swarm_id}")
    print(f"Nodes deployed: {result.total_nodes}")
    print(f"Total agents: {result.total_agents}")
    print(f"Tasks executed: {result.completed_tasks}/{result.total_tasks}")
    print(f"Success rate: {(result.completed_tasks/max(result.total_tasks,1))*100:.1f}%")
    print(f"Total findings: {result.total_findings}")
    print(f"Critical findings: {result.critical_findings}")
    
    # Display threat intelligence
    cross_threats = result.threat_intelligence.get("cross_target_threats", [])
    if cross_threats:
        print(f"\nCross-target threats detected: {len(cross_threats)}")
        for threat in cross_threats[:3]:
            print(f"  - {threat['pattern']}: {len(threat['affected_targets'])} targets affected")
    
    if result.recommendations:
        print("\nTop Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    print(f"\nFull report saved: {report_file}")
    
    return result


if __name__ == "__main__":
    asyncio.run(demo_distributed_swarm())