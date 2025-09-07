#!/usr/bin/env python3
"""
Parallel Security Orchestrator - Multi-Agent Deep Analysis System
Coordinates multiple security agents running in parallel for comprehensive analysis
"""

import asyncio
import aiohttp
import json
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from queue import Queue, PriorityQueue
import hashlib
from enum import Enum

# Import all scanning modules
from advanced_pattern_scanner import AdvancedPatternScanner
from web_api_scanner import WebAPIKeyScanner, WebTarget
from stealth_web_scanner import StealthWebScanner, StealthConfig
from deep_crawl_engine import DeepCrawlEngine, CrawlTarget
from batch_web_scanner import BatchWebScanner


class AgentType(Enum):
    """Types of security analysis agents"""
    PATTERN_HUNTER = "pattern_hunter"
    WEB_CRAWLER = "web_crawler" 
    STEALTH_INFILTRATOR = "stealth_infiltrator"
    DEEP_EXPLORER = "deep_explorer"
    VULNERABILITY_ANALYZER = "vulnerability_analyzer"
    THREAT_CORRELATOR = "threat_correlator"
    RISK_ASSESSOR = "risk_assessor"
    RECONNAISSANCE = "reconnaissance"


@dataclass
class AgentTask:
    """Task assignment for an agent"""
    task_id: str
    agent_type: AgentType
    target: Any
    priority: int = 5
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ParallelAnalysisResult:
    """Aggregated results from parallel analysis"""
    analysis_id: str
    target_url: str
    timestamp: str
    total_agents: int
    completed_agents: int
    total_findings: int
    critical_findings: List[Any] = field(default_factory=list)
    high_risk_findings: List[Any] = field(default_factory=list)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    correlations: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0
    analysis_duration: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class SecurityAgent:
    """Base security agent for parallel execution"""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.current_task = None
        self.results_queue = Queue()
        
    async def execute_task(self, task: AgentTask) -> Any:
        """Execute assigned security analysis task"""
        self.status = "working"
        self.current_task = task
        task.start_time = time.time()
        
        try:
            if self.agent_type == AgentType.PATTERN_HUNTER:
                result = await self._pattern_hunt(task)
            elif self.agent_type == AgentType.WEB_CRAWLER:
                result = await self._web_crawl(task)
            elif self.agent_type == AgentType.STEALTH_INFILTRATOR:
                result = await self._stealth_infiltrate(task)
            elif self.agent_type == AgentType.DEEP_EXPLORER:
                result = await self._deep_explore(task)
            elif self.agent_type == AgentType.VULNERABILITY_ANALYZER:
                result = await self._analyze_vulnerabilities(task)
            elif self.agent_type == AgentType.THREAT_CORRELATOR:
                result = await self._correlate_threats(task)
            elif self.agent_type == AgentType.RISK_ASSESSOR:
                result = await self._assess_risk(task)
            elif self.agent_type == AgentType.RECONNAISSANCE:
                result = await self._reconnaissance(task)
            else:
                result = None
                
            task.result = result
            task.status = "completed"
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            
        task.end_time = time.time()
        self.status = "idle"
        self.current_task = None
        
        return task
    
    async def _pattern_hunt(self, task: AgentTask) -> Dict[str, Any]:
        """Hunt for patterns in content"""
        scanner = AdvancedPatternScanner()
        findings = []
        
        if "content" in task.parameters:
            content = task.parameters["content"]
            url = task.parameters.get("url", "unknown")
            findings = scanner.scan_content(content, url)
        elif "file_path" in task.parameters:
            with open(task.parameters["file_path"], 'rb') as f:
                content = f.read()
            findings = scanner.process_file_content(
                task.parameters["file_path"], content
            )
        
        return {
            "agent_id": self.agent_id,
            "findings": findings,
            "patterns_checked": len(scanner.patterns),
            "high_confidence": [f for f in findings if f.confidence > 0.8]
        }
    
    async def _web_crawl(self, task: AgentTask) -> Dict[str, Any]:
        """Crawl web targets for vulnerabilities"""
        scanner = WebAPIKeyScanner()
        
        web_target = WebTarget(
            url=task.target,
            domain=task.parameters.get("domain", ""),
            depth=task.parameters.get("depth", 2),
            max_pages=task.parameters.get("max_pages", 20)
        )
        
        result = await asyncio.to_thread(scanner.scan_target, web_target)
        
        return {
            "agent_id": self.agent_id,
            "pages_scanned": result.pages_scanned,
            "findings": result.findings,
            "urls_discovered": list(result.urls_discovered),
            "scan_duration": result.scan_duration
        }
    
    async def _stealth_infiltrate(self, task: AgentTask) -> Dict[str, Any]:
        """Perform stealth infiltration with evasion"""
        config = StealthConfig(
            randomize_headers=True,
            mimic_human_behavior=True,
            avoid_honeypots=True
        )
        
        scanner = StealthWebScanner(config)
        
        web_target = WebTarget(
            url=task.target,
            domain=task.parameters.get("domain", ""),
            depth=task.parameters.get("depth", 2),
            max_pages=task.parameters.get("max_pages", 15)
        )
        
        result = await scanner.scan_with_stealth(web_target)
        
        return {
            "agent_id": self.agent_id,
            "stealth_score": result.stealth_score,
            "findings": result.findings,
            "evasion_techniques": result.evasion_techniques_used,
            "detection_events": result.detection_events,
            "pages_scanned": result.pages_scanned
        }
    
    async def _deep_explore(self, task: AgentTask) -> Dict[str, Any]:
        """Deep exploration and discovery"""
        engine = DeepCrawlEngine()
        
        crawl_target = CrawlTarget(
            url=task.target,
            domain=task.parameters.get("domain", ""),
            max_depth=task.parameters.get("max_depth", 5),
            max_pages=task.parameters.get("max_pages", 50),
            discover_apis=True,
            discover_admin_panels=True,
            discover_backup_files=True
        )
        
        result = await engine.deep_crawl(crawl_target)
        
        return {
            "agent_id": self.agent_id,
            "urls_discovered": len(result.discovered_urls),
            "api_endpoints": list(result.api_endpoints),
            "admin_panels": list(result.admin_panels),
            "sensitive_files": result.sensitive_files,
            "technology_stack": result.technology_stack,
            "security_findings": result.security_findings
        }
    
    async def _analyze_vulnerabilities(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze vulnerabilities from collected data"""
        findings = task.parameters.get("findings", [])
        
        vulnerabilities = {
            "sql_injection": [],
            "xss": [],
            "credential_exposure": [],
            "path_traversal": [],
            "information_disclosure": []
        }
        
        # Categorize findings
        for finding in findings:
            if hasattr(finding, 'pattern_type'):
                pattern = finding.pattern_type.lower()
                if 'sql' in pattern:
                    vulnerabilities["sql_injection"].append(finding)
                elif 'script' in pattern or 'xss' in pattern:
                    vulnerabilities["xss"].append(finding)
                elif 'key' in pattern or 'token' in pattern or 'password' in pattern:
                    vulnerabilities["credential_exposure"].append(finding)
                elif 'path' in pattern or 'directory' in pattern:
                    vulnerabilities["path_traversal"].append(finding)
                else:
                    vulnerabilities["information_disclosure"].append(finding)
        
        return {
            "agent_id": self.agent_id,
            "vulnerability_categories": vulnerabilities,
            "total_vulnerabilities": sum(len(v) for v in vulnerabilities.values()),
            "critical_count": len([f for f in findings 
                                 if hasattr(f, 'risk_level') and f.risk_level == 'CRITICAL'])
        }
    
    async def _correlate_threats(self, task: AgentTask) -> Dict[str, Any]:
        """Correlate threats across different findings"""
        agent_results = task.parameters.get("agent_results", {})
        
        correlations = []
        threat_chains = []
        
        # Find correlated threats
        all_findings = []
        for agent_data in agent_results.values():
            if isinstance(agent_data, dict) and "findings" in agent_data:
                all_findings.extend(agent_data["findings"])
        
        # Group by similarity
        grouped = {}
        for finding in all_findings:
            if hasattr(finding, 'pattern_type'):
                key = finding.pattern_type
                if key not in grouped:
                    grouped[key] = []
                grouped[key].append(finding)
        
        # Identify threat chains
        for pattern_type, group in grouped.items():
            if len(group) > 1:
                correlations.append({
                    "pattern": pattern_type,
                    "occurrences": len(group),
                    "locations": [getattr(f, 'url', 'unknown') for f in group[:5]],
                    "risk_amplification": min(len(group) * 0.2, 2.0)
                })
        
        return {
            "agent_id": self.agent_id,
            "correlations": correlations,
            "threat_patterns": list(grouped.keys()),
            "correlation_strength": len(correlations) / max(len(grouped), 1)
        }
    
    async def _assess_risk(self, task: AgentTask) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        agent_results = task.parameters.get("agent_results", {})
        
        risk_factors = {
            "credential_exposure": 0,
            "public_accessibility": 0,
            "technology_vulnerabilities": 0,
            "configuration_issues": 0,
            "stealth_detection": 0
        }
        
        # Calculate risk factors
        for agent_id, data in agent_results.items():
            if "findings" in data:
                for finding in data["findings"]:
                    if hasattr(finding, 'risk_level'):
                        if finding.risk_level == 'CRITICAL':
                            risk_factors["credential_exposure"] += 10
                        elif finding.risk_level == 'HIGH':
                            risk_factors["credential_exposure"] += 5
                        else:
                            risk_factors["credential_exposure"] += 1
            
            if "stealth_score" in data:
                risk_factors["stealth_detection"] = (1 - data["stealth_score"]) * 10
            
            if "technology_stack" in data:
                risk_factors["technology_vulnerabilities"] = len(data["technology_stack"]) * 2
        
        # Calculate overall risk score
        total_risk = sum(risk_factors.values())
        risk_score = min(100, total_risk)
        
        # Generate recommendations
        recommendations = []
        if risk_factors["credential_exposure"] > 20:
            recommendations.append("CRITICAL: Rotate all exposed credentials immediately")
        if risk_factors["stealth_detection"] > 7:
            recommendations.append("HIGH: Implement better anti-scanning measures")
        if risk_factors["technology_vulnerabilities"] > 10:
            recommendations.append("MEDIUM: Update and patch identified technologies")
        
        return {
            "agent_id": self.agent_id,
            "risk_factors": risk_factors,
            "overall_risk_score": risk_score,
            "risk_level": self._classify_risk(risk_score),
            "recommendations": recommendations
        }
    
    async def _reconnaissance(self, task: AgentTask) -> Dict[str, Any]:
        """Initial reconnaissance and information gathering"""
        target_url = task.target
        recon_data = {
            "dns_records": [],
            "subdomains": [],
            "technologies": [],
            "headers": {},
            "robots_txt": None,
            "sitemap": None
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get headers and basic info
                async with session.get(target_url) as response:
                    recon_data["headers"] = dict(response.headers)
                    recon_data["status_code"] = response.status
                
                # Check robots.txt
                robots_url = f"{target_url}/robots.txt"
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        recon_data["robots_txt"] = await response.text()
                
                # Check sitemap
                sitemap_url = f"{target_url}/sitemap.xml"
                async with session.get(sitemap_url) as response:
                    if response.status == 200:
                        recon_data["sitemap"] = True
        except:
            pass
        
        return {
            "agent_id": self.agent_id,
            "reconnaissance": recon_data,
            "target": target_url
        }
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk level based on score"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"


class ParallelSecurityOrchestrator:
    """Orchestrates parallel security analysis with multiple agents"""
    
    def __init__(self, max_agents: int = 8):
        self.max_agents = max_agents
        self.agents = {}
        self.task_queue = PriorityQueue()
        self.results = {}
        self.analysis_id = None
        
    def initialize_agents(self):
        """Initialize the agent swarm"""
        agent_configs = [
            ("hunter_alpha", AgentType.PATTERN_HUNTER),
            ("hunter_beta", AgentType.PATTERN_HUNTER),
            ("crawler_prime", AgentType.WEB_CRAWLER),
            ("stealth_one", AgentType.STEALTH_INFILTRATOR),
            ("explorer_deep", AgentType.DEEP_EXPLORER),
            ("vuln_analyzer", AgentType.VULNERABILITY_ANALYZER),
            ("threat_correlator", AgentType.THREAT_CORRELATOR),
            ("risk_assessor", AgentType.RISK_ASSESSOR),
            ("recon_scout", AgentType.RECONNAISSANCE)
        ]
        
        for agent_id, agent_type in agent_configs[:self.max_agents]:
            self.agents[agent_id] = SecurityAgent(agent_id, agent_type)
        
        print(f"Initialized {len(self.agents)} security agents")
    
    async def orchestrate_deep_analysis(self, target_url: str, 
                                       analysis_depth: str = "comprehensive") -> ParallelAnalysisResult:
        """Orchestrate parallel deep security analysis"""
        self.analysis_id = hashlib.sha256(
            f"{target_url}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        start_time = time.time()
        
        result = ParallelAnalysisResult(
            analysis_id=self.analysis_id,
            target_url=target_url,
            timestamp=datetime.now().isoformat(),
            total_agents=len(self.agents),
            completed_agents=0,
            total_findings=0
        )
        
        print(f"Starting parallel deep analysis of {target_url}")
        print(f"Analysis ID: {self.analysis_id}")
        print(f"Depth: {analysis_depth}")
        print("-" * 50)
        
        # Phase 1: Reconnaissance
        print("Phase 1: Reconnaissance")
        recon_tasks = self._create_reconnaissance_tasks(target_url)
        recon_results = await self._execute_phase(recon_tasks)
        
        # Phase 2: Parallel scanning
        print("Phase 2: Parallel Scanning")
        scan_tasks = self._create_scanning_tasks(target_url, analysis_depth)
        scan_results = await self._execute_phase(scan_tasks)
        
        # Phase 3: Deep analysis
        print("Phase 3: Deep Analysis")
        analysis_tasks = self._create_analysis_tasks(scan_results)
        analysis_results = await self._execute_phase(analysis_tasks)
        
        # Phase 4: Correlation and risk assessment
        print("Phase 4: Threat Correlation & Risk Assessment")
        correlation_tasks = self._create_correlation_tasks({
            **recon_results, **scan_results, **analysis_results
        })
        final_results = await self._execute_phase(correlation_tasks)
        
        # Aggregate all results
        all_results = {**recon_results, **scan_results, **analysis_results, **final_results}
        result.agent_results = all_results
        result.completed_agents = len(all_results)
        
        # Extract key findings
        self._aggregate_findings(result, all_results)
        
        # Calculate final metrics
        result.analysis_duration = time.time() - start_time
        
        print(f"\nAnalysis complete in {result.analysis_duration:.2f}s")
        print(f"Total findings: {result.total_findings}")
        print(f"Critical findings: {len(result.critical_findings)}")
        print(f"Risk score: {result.risk_score:.1f}/100")
        
        return result
    
    def _create_reconnaissance_tasks(self, target_url: str) -> List[AgentTask]:
        """Create reconnaissance phase tasks"""
        domain = self._extract_domain(target_url)
        
        return [
            AgentTask(
                task_id="recon_001",
                agent_type=AgentType.RECONNAISSANCE,
                target=target_url,
                priority=1,
                parameters={"domain": domain}
            )
        ]
    
    def _create_scanning_tasks(self, target_url: str, depth: str) -> List[AgentTask]:
        """Create parallel scanning tasks"""
        domain = self._extract_domain(target_url)
        
        # Adjust parameters based on depth
        if depth == "quick":
            max_pages, crawl_depth = 10, 1
        elif depth == "standard":
            max_pages, crawl_depth = 30, 2
        else:  # comprehensive
            max_pages, crawl_depth = 100, 3
        
        tasks = [
            AgentTask(
                task_id="scan_web_001",
                agent_type=AgentType.WEB_CRAWLER,
                target=target_url,
                priority=2,
                parameters={
                    "domain": domain,
                    "depth": crawl_depth,
                    "max_pages": max_pages
                }
            ),
            AgentTask(
                task_id="scan_stealth_001",
                agent_type=AgentType.STEALTH_INFILTRATOR,
                target=target_url,
                priority=2,
                parameters={
                    "domain": domain,
                    "depth": crawl_depth,
                    "max_pages": max_pages // 2
                }
            ),
            AgentTask(
                task_id="scan_deep_001",
                agent_type=AgentType.DEEP_EXPLORER,
                target=target_url,
                priority=3,
                parameters={
                    "domain": domain,
                    "max_depth": crawl_depth + 2,
                    "max_pages": max_pages * 2
                }
            )
        ]
        
        return tasks
    
    def _create_analysis_tasks(self, scan_results: Dict[str, Any]) -> List[AgentTask]:
        """Create analysis tasks based on scan results"""
        tasks = []
        
        # Collect all findings for analysis
        all_findings = []
        for agent_id, result in scan_results.items():
            if "findings" in result:
                all_findings.extend(result["findings"])
        
        # Pattern hunting on discovered content
        if all_findings:
            tasks.append(
                AgentTask(
                    task_id="analyze_patterns_001",
                    agent_type=AgentType.PATTERN_HUNTER,
                    target=None,
                    priority=4,
                    parameters={
                        "content": "\n".join([str(f) for f in all_findings[:100]]),
                        "url": "aggregated_findings"
                    }
                )
            )
        
        # Vulnerability analysis
        tasks.append(
            AgentTask(
                task_id="analyze_vuln_001",
                agent_type=AgentType.VULNERABILITY_ANALYZER,
                target=None,
                priority=4,
                parameters={"findings": all_findings}
            )
        )
        
        return tasks
    
    def _create_correlation_tasks(self, all_results: Dict[str, Any]) -> List[AgentTask]:
        """Create correlation and risk assessment tasks"""
        return [
            AgentTask(
                task_id="correlate_001",
                agent_type=AgentType.THREAT_CORRELATOR,
                target=None,
                priority=5,
                parameters={"agent_results": all_results}
            ),
            AgentTask(
                task_id="risk_001",
                agent_type=AgentType.RISK_ASSESSOR,
                target=None,
                priority=5,
                parameters={"agent_results": all_results}
            )
        ]
    
    async def _execute_phase(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute a phase of tasks in parallel"""
        results = {}
        
        # Create async tasks for parallel execution
        async_tasks = []
        assigned_agents = set()  # Track which agents are assigned
        
        for task in tasks:
            # Find available agent of the right type
            for agent_id, agent in self.agents.items():
                if (agent.agent_type == task.agent_type and 
                    agent.status == "idle" and 
                    agent_id not in assigned_agents):
                    async_tasks.append(agent.execute_task(task))
                    assigned_agents.add(agent_id)  # Mark agent as assigned
                    break
        
        # Execute all tasks in parallel
        completed_tasks = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Collect results
        for task_result in completed_tasks:
            if isinstance(task_result, AgentTask):
                results[task_result.task_id] = task_result.result
            elif isinstance(task_result, Exception):
                print(f"Task failed: {task_result}")
        
        return results
    
    def _aggregate_findings(self, result: ParallelAnalysisResult, all_results: Dict[str, Any]):
        """Aggregate findings from all agents"""
        all_findings = []
        
        for agent_data in all_results.values():
            if isinstance(agent_data, dict):
                if "findings" in agent_data:
                    all_findings.extend(agent_data["findings"])
                if "security_findings" in agent_data:
                    all_findings.extend(agent_data["security_findings"])
        
        # Categorize by risk level
        for finding in all_findings:
            if hasattr(finding, 'risk_level'):
                if finding.risk_level == 'CRITICAL':
                    result.critical_findings.append(finding)
                elif finding.risk_level == 'HIGH':
                    result.high_risk_findings.append(finding)
        
        result.total_findings = len(all_findings)
        
        # Extract risk score if available
        for agent_data in all_results.values():
            if isinstance(agent_data, dict) and "overall_risk_score" in agent_data:
                result.risk_score = agent_data["overall_risk_score"]
                result.recommendations = agent_data.get("recommendations", [])
        
        # Extract correlations
        for agent_data in all_results.values():
            if isinstance(agent_data, dict) and "correlations" in agent_data:
                result.correlations = agent_data["correlations"]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def generate_parallel_report(self, result: ParallelAnalysisResult) -> Dict[str, Any]:
        """Generate comprehensive parallel analysis report"""
        return {
            "analysis_summary": {
                "analysis_id": result.analysis_id,
                "target": result.target_url,
                "timestamp": result.timestamp,
                "duration_seconds": round(result.analysis_duration, 2),
                "agents_deployed": result.total_agents,
                "agents_completed": result.completed_agents
            },
            "security_findings": {
                "total_findings": result.total_findings,
                "critical_findings": len(result.critical_findings),
                "high_risk_findings": len(result.high_risk_findings),
                "risk_score": round(result.risk_score, 1),
                "risk_level": self._classify_risk_score(result.risk_score)
            },
            "threat_intelligence": {
                "correlations_found": len(result.correlations),
                "correlation_details": result.correlations[:10],  # Top 10
                "threat_patterns": self._extract_threat_patterns(result)
            },
            "agent_performance": {
                agent_id: {
                    "status": "completed" if agent_id in result.agent_results else "pending",
                    "findings": len(result.agent_results.get(agent_id, {}).get("findings", [])),
                    "metrics": self._extract_agent_metrics(result.agent_results.get(agent_id, {}))
                }
                for agent_id in self.agents.keys()
            },
            "recommendations": result.recommendations,
            "detailed_findings": {
                "critical": [
                    {
                        "pattern": getattr(f, 'pattern_type', 'unknown'),
                        "value": str(getattr(f, 'value', ''))[:50],
                        "confidence": getattr(f, 'confidence', 0),
                        "location": getattr(f, 'url', 'unknown')
                    }
                    for f in result.critical_findings[:5]
                ],
                "high_risk": [
                    {
                        "pattern": getattr(f, 'pattern_type', 'unknown'),
                        "confidence": getattr(f, 'confidence', 0)
                    }
                    for f in result.high_risk_findings[:5]
                ]
            }
        }
    
    def _classify_risk_score(self, score: float) -> str:
        """Classify risk score into levels"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _extract_threat_patterns(self, result: ParallelAnalysisResult) -> List[str]:
        """Extract unique threat patterns"""
        patterns = set()
        for finding in result.critical_findings + result.high_risk_findings:
            if hasattr(finding, 'pattern_type'):
                patterns.add(finding.pattern_type)
        return list(patterns)
    
    def _extract_agent_metrics(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from agent data"""
        metrics = {}
        
        if "pages_scanned" in agent_data:
            metrics["pages_scanned"] = agent_data["pages_scanned"]
        if "stealth_score" in agent_data:
            metrics["stealth_score"] = round(agent_data["stealth_score"], 3)
        if "urls_discovered" in agent_data:
            metrics["urls_discovered"] = len(agent_data.get("urls_discovered", []))
        if "scan_duration" in agent_data:
            metrics["scan_duration"] = round(agent_data["scan_duration"], 2)
        
        return metrics


async def demo_parallel_analysis():
    """Demonstrate parallel multi-agent security analysis"""
    print("PARALLEL SECURITY ORCHESTRATOR - Multi-Agent Deep Analysis")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ParallelSecurityOrchestrator(max_agents=8)
    orchestrator.initialize_agents()
    
    # Target for analysis
    target_url = "https://httpbin.org"
    
    print(f"\nTarget: {target_url}")
    print(f"Analysis type: Comprehensive parallel deep scan")
    print(f"Agents deployed: {len(orchestrator.agents)}")
    print("-" * 50)
    
    # Run parallel analysis
    result = await orchestrator.orchestrate_deep_analysis(
        target_url=target_url,
        analysis_depth="quick"  # Use quick for demo
    )
    
    # Generate report
    report = orchestrator.generate_parallel_report(result)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"parallel_analysis_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 60)
    print("PARALLEL ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Analysis ID: {result.analysis_id}")
    print(f"Duration: {result.analysis_duration:.2f}s")
    print(f"Agents completed: {result.completed_agents}/{result.total_agents}")
    print(f"Total findings: {result.total_findings}")
    print(f"Critical findings: {len(result.critical_findings)}")
    print(f"High-risk findings: {len(result.high_risk_findings)}")
    print(f"Threat correlations: {len(result.correlations)}")
    print(f"Risk score: {result.risk_score:.1f}/100")
    print(f"Risk level: {orchestrator._classify_risk_score(result.risk_score)}")
    
    if result.recommendations:
        print("\nTop Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    print(f"\nFull report saved: {report_file}")
    
    return result


if __name__ == "__main__":
    asyncio.run(demo_parallel_analysis())