#!/usr/bin/env python3
"""
Ultimate Security Scanner - Integrated Penetration Testing Platform
Combines all scanning capabilities for comprehensive security assessment
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from advanced_pattern_scanner import AdvancedPatternScanner
from web_api_scanner import WebAPIKeyScanner, WebTarget
from stealth_web_scanner import StealthWebScanner, StealthConfig
from deep_crawl_engine import DeepCrawlEngine, CrawlTarget
from batch_web_scanner import BatchWebScanner


@dataclass
class UltimateTarget:
    """Comprehensive target configuration for ultimate security assessment"""
    url: str
    domain: str
    
    # Scanning modes
    enable_basic_scan: bool = True
    enable_stealth_scan: bool = True
    enable_deep_crawl: bool = True
    enable_pattern_analysis: bool = True
    
    # Basic scan config
    basic_max_pages: int = 50
    basic_depth: int = 2
    
    # Stealth scan config
    stealth_max_pages: int = 30
    stealth_depth: int = 3
    use_evasion_techniques: bool = True
    
    # Deep crawl config
    crawl_max_pages: int = 100
    crawl_depth: int = 5
    discover_all_resources: bool = True
    
    # Authentication
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class UltimateResult:
    """Comprehensive security assessment results"""
    target: UltimateTarget
    
    # Results from each scanner
    basic_scan_result: Any = None
    stealth_scan_result: Any = None
    deep_crawl_result: Any = None
    
    # Consolidated findings
    all_findings: List[Any] = field(default_factory=list)
    unique_urls: set = field(default_factory=set)
    
    # Risk assessment
    overall_risk_level: str = "UNKNOWN"
    critical_findings: List[Any] = field(default_factory=list)
    high_risk_findings: List[Any] = field(default_factory=list)
    
    # Security metrics
    vulnerability_score: float = 0.0
    stealth_detection_score: float = 0.0
    coverage_completeness: float = 0.0
    
    # Performance metrics
    total_scan_time: float = 0.0
    total_pages_analyzed: int = 0
    total_requests_made: int = 0


class UltimateSecurityScanner:
    """Ultimate security scanner combining all capabilities"""
    
    def __init__(self):
        # Initialize all scanner components
        self.pattern_scanner = AdvancedPatternScanner()
        self.web_scanner = WebAPIKeyScanner()
        self.stealth_scanner = None  # Will be initialized with custom config
        self.deep_crawler = DeepCrawlEngine()
        self.batch_scanner = BatchWebScanner()
        
        # Risk assessment weights
        self.risk_weights = {
            'api_keys': 10.0,
            'database_credentials': 15.0,
            'cloud_credentials': 12.0,
            'payment_tokens': 20.0,
            'admin_panels': 8.0,
            'sensitive_files': 6.0,
            'backup_files': 7.0,
            'info_disclosure': 5.0
        }

    async def ultimate_scan(self, target: UltimateTarget) -> UltimateResult:
        """Perform comprehensive security assessment"""
        start_time = time.time()
        result = UltimateResult(target=target)
        
        print(f"Starting Ultimate Security Assessment: {target.url}")
        print("=" * 60)
        
        try:
            # Phase 1: Basic Web Scanning
            if target.enable_basic_scan:
                print("Phase 1: Basic Web Scanning...")
                result.basic_scan_result = await self._basic_web_scan(target)
                print(f"   Found {len(result.basic_scan_result.findings)} basic findings")
            
            # Phase 2: Stealth Penetration Testing
            if target.enable_stealth_scan:
                print("Phase 2: Stealth Penetration Testing...")
                result.stealth_scan_result = await self._stealth_penetration_test(target)
                print(f"   Stealth Score: {result.stealth_scan_result.stealth_score:.3f}")
                print(f"   Found {len(result.stealth_scan_result.findings)} stealth findings")
            
            # Phase 3: Deep Crawling and Discovery
            if target.enable_deep_crawl:
                print("Phase 3: Deep Crawling and Discovery...")
                result.deep_crawl_result = await self._deep_crawl_assessment(target)
                print(f"   Analyzed {len(result.deep_crawl_result.analyzed_files)} files")
                print(f"   Found {len(result.deep_crawl_result.security_findings)} crawl findings")
            
            # Phase 4: Advanced Pattern Analysis
            if target.enable_pattern_analysis:
                print("Phase 4: Advanced Pattern Analysis...")
                await self._advanced_pattern_analysis(result)
                print(f"   Completed comprehensive pattern analysis")
            
            # Phase 5: Risk Assessment and Consolidation
            print("Phase 5: Risk Assessment...")
            await self._consolidate_and_assess_risk(result)
            
        except Exception as e:
            print(f"Scan error: {e}")
        
        result.total_scan_time = time.time() - start_time
        print(f"\nUltimate Security Assessment Complete ({result.total_scan_time:.2f}s)")
        
        return result

    async def _basic_web_scan(self, target: UltimateTarget):
        """Perform basic web vulnerability scanning"""
        web_target = WebTarget(
            url=target.url,
            domain=target.domain,
            depth=target.basic_depth,
            max_pages=target.basic_max_pages,
            scan_js=True,
            scan_css=True
        )
        
        # Add authentication if provided
        if target.cookies:
            web_target.cookies = target.cookies
        if target.headers:
            web_target.headers = target.headers
        
        return await asyncio.create_task(
            asyncio.to_thread(self.web_scanner.scan_target, web_target)
        )

    async def _stealth_penetration_test(self, target: UltimateTarget):
        """Perform stealth penetration testing"""
        stealth_config = StealthConfig(
            max_depth=target.stealth_depth,
            randomize_headers=target.use_evasion_techniques,
            mimic_human_behavior=target.use_evasion_techniques,
            avoid_honeypots=True,
            respect_rate_limits=True
        )
        
        stealth_scanner = StealthWebScanner(stealth_config)
        
        web_target = WebTarget(
            url=target.url,
            domain=target.domain,
            depth=target.stealth_depth,
            max_pages=target.stealth_max_pages,
            scan_js=True
        )
        
        return await stealth_scanner.scan_with_stealth(web_target)

    async def _deep_crawl_assessment(self, target: UltimateTarget):
        """Perform deep crawling assessment"""
        crawl_target = CrawlTarget(
            url=target.url,
            domain=target.domain,
            max_depth=target.crawl_depth,
            max_pages=target.crawl_max_pages,
            scan_javascript=True,
            scan_css=True,
            scan_documents=True,
            scan_archives=True,
            discover_apis=target.discover_all_resources,
            discover_admin_panels=target.discover_all_resources,
            discover_backup_files=target.discover_all_resources,
            cookies=target.cookies,
            headers=target.headers
        )
        
        return await self.deep_crawler.deep_crawl(crawl_target)

    async def _advanced_pattern_analysis(self, result: UltimateResult):
        """Perform advanced pattern analysis on all discovered content"""
        all_content = []
        
        # Collect content from all scans
        if result.basic_scan_result:
            all_content.extend([
                (f.content, f.url) for f in result.basic_scan_result.findings 
                if hasattr(f, 'content')
            ])
        
        if result.stealth_scan_result:
            all_content.extend([
                (f.content, f.url) for f in result.stealth_scan_result.findings 
                if hasattr(f, 'content')
            ])
        
        if result.deep_crawl_result:
            for url, file_info in result.deep_crawl_result.analyzed_files.items():
                if 'content' in file_info:
                    all_content.append((file_info['content'], url))
        
        # Run advanced pattern analysis
        for content, url in all_content[:50]:  # Limit to prevent overwhelming
            advanced_findings = self.pattern_scanner.scan_content(content, url)
            result.all_findings.extend(advanced_findings)

    async def _consolidate_and_assess_risk(self, result: UltimateResult):
        """Consolidate all findings and assess overall risk"""
        
        # Consolidate findings from all scanners
        all_findings = []
        unique_urls = set()
        
        if result.basic_scan_result:
            all_findings.extend(result.basic_scan_result.findings)
            result.total_pages_analyzed += result.basic_scan_result.pages_scanned
        
        if result.stealth_scan_result:
            all_findings.extend(result.stealth_scan_result.findings)
            result.total_pages_analyzed += result.stealth_scan_result.pages_scanned
            result.stealth_detection_score = result.stealth_scan_result.stealth_score
        
        if result.deep_crawl_result:
            all_findings.extend(result.deep_crawl_result.security_findings)
            unique_urls.update(result.deep_crawl_result.discovered_urls)
            result.total_pages_analyzed += len(result.deep_crawl_result.analyzed_files)
        
        # Add advanced pattern findings
        all_findings.extend(result.all_findings)
        
        result.all_findings = all_findings
        result.unique_urls = unique_urls
        
        # Categorize findings by risk level
        critical_findings = []
        high_risk_findings = []
        
        for finding in all_findings:
            if hasattr(finding, 'risk_level'):
                if finding.risk_level == 'CRITICAL':
                    critical_findings.append(finding)
                elif finding.risk_level == 'HIGH':
                    high_risk_findings.append(finding)
            elif hasattr(finding, 'confidence') and finding.confidence > 0.8:
                high_risk_findings.append(finding)
        
        result.critical_findings = critical_findings
        result.high_risk_findings = high_risk_findings
        
        # Calculate vulnerability score
        result.vulnerability_score = self._calculate_vulnerability_score(all_findings)
        
        # Determine overall risk level
        if len(critical_findings) > 0:
            result.overall_risk_level = "CRITICAL"
        elif len(high_risk_findings) > 2:
            result.overall_risk_level = "HIGH"  
        elif len(all_findings) > 10:
            result.overall_risk_level = "MEDIUM"
        else:
            result.overall_risk_level = "LOW"
        
        # Calculate coverage completeness
        result.coverage_completeness = min(1.0, result.total_pages_analyzed / 100.0)

    def _calculate_vulnerability_score(self, findings: List[Any]) -> float:
        """Calculate numerical vulnerability score"""
        score = 0.0
        
        for finding in findings:
            base_score = 1.0
            
            # Weight by pattern type
            if hasattr(finding, 'pattern_type'):
                pattern_type = finding.pattern_type.lower()
                for risk_type, weight in self.risk_weights.items():
                    if risk_type in pattern_type:
                        base_score *= weight
                        break
            
            # Weight by confidence
            if hasattr(finding, 'confidence'):
                base_score *= finding.confidence
            
            # Weight by risk level
            if hasattr(finding, 'risk_level'):
                risk_multipliers = {
                    'CRITICAL': 5.0,
                    'HIGH': 3.0,
                    'MEDIUM': 1.5,
                    'LOW': 1.0
                }
                base_score *= risk_multipliers.get(finding.risk_level, 1.0)
            
            score += base_score
        
        return min(100.0, score)

    def generate_ultimate_report(self, result: UltimateResult) -> Dict[str, Any]:
        """Generate comprehensive ultimate security report"""
        
        # Executive summary
        executive_summary = {
            "overall_risk_level": result.overall_risk_level,
            "vulnerability_score": round(result.vulnerability_score, 2),
            "total_findings": len(result.all_findings),
            "critical_findings": len(result.critical_findings),
            "high_risk_findings": len(result.high_risk_findings),
            "stealth_detection_score": round(result.stealth_detection_score, 3),
            "coverage_completeness": round(result.coverage_completeness * 100, 1)
        }
        
        # Detailed findings breakdown
        findings_breakdown = {
            "by_risk_level": self._categorize_by_risk_level(result.all_findings),
            "by_pattern_type": self._categorize_by_pattern_type(result.all_findings),
            "by_location": self._categorize_by_location(result.all_findings)
        }
        
        # Scanner-specific results
        scanner_results = {
            "basic_web_scan": self._summarize_basic_scan(result.basic_scan_result),
            "stealth_penetration_test": self._summarize_stealth_scan(result.stealth_scan_result),
            "deep_crawl_assessment": self._summarize_deep_crawl(result.deep_crawl_result)
        }
        
        # Security recommendations
        recommendations = self._generate_security_recommendations(result)
        
        # Technical details
        technical_details = {
            "scan_metadata": {
                "target_url": result.target.url,
                "scan_timestamp": datetime.now().isoformat(),
                "total_scan_time": round(result.total_scan_time, 2),
                "total_pages_analyzed": result.total_pages_analyzed,
                "unique_urls_discovered": len(result.unique_urls)
            },
            "scanner_configurations": {
                "basic_scan_enabled": result.target.enable_basic_scan,
                "stealth_scan_enabled": result.target.enable_stealth_scan,
                "deep_crawl_enabled": result.target.enable_deep_crawl,
                "pattern_analysis_enabled": result.target.enable_pattern_analysis
            }
        }
        
        return {
            "executive_summary": executive_summary,
            "findings_breakdown": findings_breakdown,
            "scanner_results": scanner_results,
            "security_recommendations": recommendations,
            "technical_details": technical_details,
            "critical_findings_detail": [
                {
                    "pattern": f.pattern_type if hasattr(f, 'pattern_type') else 'Unknown',
                    "location": f.url if hasattr(f, 'url') else 'Unknown',
                    "confidence": f.confidence if hasattr(f, 'confidence') else 0,
                    "risk_level": f.risk_level if hasattr(f, 'risk_level') else 'Unknown',
                    "description": str(f)[:200]
                }
                for f in result.critical_findings[:10]  # Top 10 critical findings
            ]
        }

    def _categorize_by_risk_level(self, findings: List[Any]) -> Dict[str, int]:
        """Categorize findings by risk level"""
        categories = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        
        for finding in findings:
            if hasattr(finding, 'risk_level'):
                categories[finding.risk_level] = categories.get(finding.risk_level, 0) + 1
            else:
                categories["UNKNOWN"] += 1
        
        return categories

    def _categorize_by_pattern_type(self, findings: List[Any]) -> Dict[str, int]:
        """Categorize findings by pattern type"""
        categories = {}
        
        for finding in findings:
            pattern_type = finding.pattern_type if hasattr(finding, 'pattern_type') else 'unknown'
            categories[pattern_type] = categories.get(pattern_type, 0) + 1
        
        return categories

    def _categorize_by_location(self, findings: List[Any]) -> Dict[str, int]:
        """Categorize findings by location type"""
        categories = {"html": 0, "javascript": 0, "css": 0, "api": 0, "config": 0, "other": 0}
        
        for finding in findings:
            if hasattr(finding, 'location_type'):
                location = finding.location_type.lower()
                if location in categories:
                    categories[location] += 1
                else:
                    categories["other"] += 1
            else:
                categories["other"] += 1
        
        return categories

    def _summarize_basic_scan(self, result) -> Dict[str, Any]:
        """Summarize basic scan results"""
        if not result:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "pages_scanned": result.pages_scanned,
            "scan_duration": round(result.scan_duration, 2),
            "findings": len(result.findings)
        }

    def _summarize_stealth_scan(self, result) -> Dict[str, Any]:
        """Summarize stealth scan results"""
        if not result:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "pages_scanned": result.pages_scanned,
            "stealth_score": round(result.stealth_score, 3),
            "evasion_techniques_used": len(result.evasion_techniques_used),
            "detection_events": len(result.detection_events),
            "blocked_requests": result.blocked_requests,
            "findings": len(result.findings)
        }

    def _summarize_deep_crawl(self, result) -> Dict[str, Any]:
        """Summarize deep crawl results"""
        if not result:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "urls_discovered": len(result.discovered_urls),
            "files_analyzed": len(result.analyzed_files),
            "api_endpoints": len(result.api_endpoints),
            "admin_panels": len(result.admin_panels),
            "sensitive_files": sum(len(files) for files in result.sensitive_files.values()),
            "technologies_identified": len(result.technology_stack),
            "findings": len(result.security_findings)
        }

    def _generate_security_recommendations(self, result: UltimateResult) -> List[Dict[str, str]]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Critical findings recommendations
        if len(result.critical_findings) > 0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Credential Exposure",
                "recommendation": "Immediately review and rotate all exposed API keys, tokens, and credentials found during scanning.",
                "impact": "High risk of data breach and unauthorized access"
            })
        
        # High risk findings recommendations
        if len(result.high_risk_findings) > 2:
            recommendations.append({
                "priority": "HIGH",
                "category": "Security Hardening",
                "recommendation": "Implement security headers, remove debug information, and secure administrative interfaces.",
                "impact": "Reduces attack surface and information disclosure"
            })
        
        # Stealth detection recommendations
        if result.stealth_detection_score < 0.7:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Detection and Monitoring",
                "recommendation": "Enhance web application firewall rules and implement behavioral monitoring to detect automated scanning.",
                "impact": "Improves ability to detect and respond to reconnaissance activities"
            })
        
        # Coverage recommendations
        if result.coverage_completeness < 0.5:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Security Testing",
                "recommendation": "Conduct more comprehensive security testing to identify additional vulnerabilities.",
                "impact": "Ensures thorough coverage of potential security weaknesses"
            })
        
        return recommendations


async def demo_ultimate_scan():
    """Demonstrate ultimate security scanning capabilities"""
    print("ULTIMATE SECURITY SCANNER - Full Penetration Testing Suite")
    print("=" * 70)
    
    # Configure comprehensive target
    target = UltimateTarget(
        url="https://httpbin.org",
        domain="httpbin.org",
        enable_basic_scan=True,
        enable_stealth_scan=True,
        enable_deep_crawl=True,
        enable_pattern_analysis=True,
        basic_max_pages=10,
        stealth_max_pages=8,
        crawl_max_pages=15,
        use_evasion_techniques=True,
        discover_all_resources=True
    )
    
    scanner = UltimateSecurityScanner()
    
    # Perform ultimate security assessment
    result = await scanner.ultimate_scan(target)
    
    # Generate comprehensive report
    report = scanner.generate_ultimate_report(result)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"ultimate_security_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display executive summary
    print("\n" + "="*60)
    print("ULTIMATE SECURITY ASSESSMENT RESULTS")
    print("="*60)
    print(f"Target: {target.url}")
    print(f"Overall Risk Level: {result.overall_risk_level}")
    print(f"Vulnerability Score: {result.vulnerability_score:.1f}/100")
    print(f"Total Findings: {len(result.all_findings)}")
    print(f"Critical Findings: {len(result.critical_findings)}")
    print(f"High Risk Findings: {len(result.high_risk_findings)}")
    print(f"Stealth Score: {result.stealth_detection_score:.3f}")
    print(f"Coverage: {result.coverage_completeness*100:.1f}%")
    print(f"Scan Duration: {result.total_scan_time:.2f}s")
    print(f"Pages Analyzed: {result.total_pages_analyzed}")
    print(f"URLs Discovered: {len(result.unique_urls)}")
    
    print(f"\nFull Report Saved: {report_file}")
    print("\nUltimate Security Assessment Complete!")
    
    return result, report


if __name__ == "__main__":
    asyncio.run(demo_ultimate_scan())