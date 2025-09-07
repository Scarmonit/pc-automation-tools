#!/usr/bin/env python3
"""
Batch Web Scanner - Enterprise multi-target scanning system
Batch processing capabilities for comprehensive web security assessment
"""

import json
import csv
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from web_api_scanner import WebAPIKeyScanner, WebTarget, WebScanResult


@dataclass
class ScanTarget:
    """Batch scan target with priority and metadata"""
    url: str
    domain: str
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    depth: int = 2
    max_pages: int = 50
    scan_js: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchScanResult:
    """Results from batch scanning operation"""
    targets_scanned: int = 0
    total_findings: int = 0
    high_risk_findings: int = 0
    total_scan_time: float = 0.0
    results: List[WebScanResult] = field(default_factory=list)
    failed_targets: List[str] = field(default_factory=list)


class BatchWebScanner:
    """Enterprise batch web scanner"""
    
    def __init__(self, max_threads: int = 3):
        self.scanner = WebAPIKeyScanner()
        self.max_threads = max_threads
        self.scan_results = []
        self.scan_lock = threading.Lock()
    
    def scan_targets_from_file(self, file_path: str, output_path: str = None) -> BatchScanResult:
        """Scan targets loaded from CSV or JSON file"""
        targets = self._load_targets_from_file(file_path)
        return self.scan_targets_batch(targets, output_path)
    
    def scan_targets_batch(self, targets: List[ScanTarget], 
                          output_path: str = None) -> BatchScanResult:
        """Perform batch scanning of multiple targets"""
        start_time = time.time()
        batch_result = BatchScanResult()
        
        # Sort targets by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_targets = sorted(targets, key=lambda t: priority_order.get(t.priority, 2))
        
        print(f"Starting batch scan of {len(targets)} targets...")
        
        # Create thread pool for scanning
        threads = []
        target_chunks = self._chunk_targets(sorted_targets, self.max_threads)
        
        for chunk in target_chunks:
            thread = threading.Thread(
                target=self._scan_target_chunk,
                args=(chunk, batch_result)
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Calculate totals
        batch_result.total_scan_time = time.time() - start_time
        batch_result.targets_scanned = len(batch_result.results)
        batch_result.total_findings = sum(len(r.findings) for r in batch_result.results)
        batch_result.high_risk_findings = sum(
            len([f for f in r.findings if getattr(f, 'risk_level', 'LOW') in ['HIGH', 'CRITICAL']])
            for r in batch_result.results
        )
        
        # Save results if output path provided
        if output_path:
            self._save_batch_results(batch_result, output_path)
        
        print(f"Batch scan complete: {batch_result.targets_scanned} targets, "
              f"{batch_result.total_findings} findings, "
              f"{batch_result.total_scan_time:.2f}s")
        
        return batch_result
    
    def _load_targets_from_file(self, file_path: str) -> List[ScanTarget]:
        """Load scan targets from CSV or JSON file"""
        targets = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {file_path}")
        
        if path.suffix.lower() == '.csv':
            targets = self._load_targets_from_csv(file_path)
        elif path.suffix.lower() == '.json':
            targets = self._load_targets_from_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return targets
    
    def _load_targets_from_csv(self, file_path: str) -> List[ScanTarget]:
        """Load targets from CSV file"""
        targets = []
        
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                target = ScanTarget(
                    url=row['url'],
                    domain=row.get('domain', self._extract_domain(row['url'])),
                    priority=row.get('priority', 'MEDIUM').upper(),
                    depth=int(row.get('depth', 2)),
                    max_pages=int(row.get('max_pages', 50)),
                    scan_js=row.get('scan_js', 'true').lower() == 'true'
                )
                
                # Add any additional metadata
                for key, value in row.items():
                    if key not in ['url', 'domain', 'priority', 'depth', 'max_pages', 'scan_js']:
                        target.metadata[key] = value
                
                targets.append(target)
        
        return targets
    
    def _load_targets_from_json(self, file_path: str) -> List[ScanTarget]:
        """Load targets from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
        
        targets = []
        
        if isinstance(data, list):
            # Array of target objects
            for item in data:
                target = ScanTarget(
                    url=item['url'],
                    domain=item.get('domain', self._extract_domain(item['url'])),
                    priority=item.get('priority', 'MEDIUM').upper(),
                    depth=item.get('depth', 2),
                    max_pages=item.get('max_pages', 50),
                    scan_js=item.get('scan_js', True),
                    metadata=item.get('metadata', {})
                )
                targets.append(target)
        
        elif isinstance(data, dict) and 'targets' in data:
            # Object with targets array
            for item in data['targets']:
                target = ScanTarget(
                    url=item['url'],
                    domain=item.get('domain', self._extract_domain(item['url'])),
                    priority=item.get('priority', 'MEDIUM').upper(),
                    depth=item.get('depth', 2),
                    max_pages=item.get('max_pages', 50),
                    scan_js=item.get('scan_js', True),
                    metadata=item.get('metadata', {})
                )
                targets.append(target)
        
        return targets
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def _chunk_targets(self, targets: List[ScanTarget], chunk_size: int) -> List[List[ScanTarget]]:
        """Split targets into chunks for parallel processing"""
        chunks = []
        for i in range(0, len(targets), chunk_size):
            chunks.append(targets[i:i + chunk_size])
        return chunks
    
    def _scan_target_chunk(self, targets: List[ScanTarget], batch_result: BatchScanResult):
        """Scan a chunk of targets in a single thread"""
        for target in targets:
            try:
                print(f"Scanning: {target.url} (Priority: {target.priority})")
                
                # Convert to WebTarget
                web_target = WebTarget(
                    url=target.url,
                    domain=target.domain,
                    depth=target.depth,
                    max_pages=target.max_pages,
                    scan_js=target.scan_js
                )
                
                # Perform scan
                scan_result = self.scanner.scan_target(web_target)
                
                # Thread-safe result storage
                with self.scan_lock:
                    batch_result.results.append(scan_result)
                
                print(f"  Complete: {len(scan_result.findings)} findings, "
                      f"{scan_result.pages_scanned} pages, "
                      f"{scan_result.scan_duration:.2f}s")
                
            except Exception as e:
                print(f"  Error scanning {target.url}: {e}")
                with self.scan_lock:
                    batch_result.failed_targets.append(target.url)
    
    def _save_batch_results(self, batch_result: BatchScanResult, output_path: str):
        """Save batch scan results to file"""
        timestamp = datetime.now().isoformat()
        
        # Prepare results data
        results_data = {
            "batch_scan_summary": {
                "timestamp": timestamp,
                "targets_scanned": batch_result.targets_scanned,
                "total_findings": batch_result.total_findings,
                "high_risk_findings": batch_result.high_risk_findings,
                "total_scan_time": batch_result.total_scan_time,
                "failed_targets": batch_result.failed_targets
            },
            "scan_results": []
        }
        
        # Add individual scan results
        for result in batch_result.results:
            result_data = {
                "target_url": result.target.url,
                "target_domain": result.target.domain,
                "pages_scanned": result.pages_scanned,
                "scan_duration": result.scan_duration,
                "findings_count": len(result.findings),
                "urls_discovered": len(result.urls_discovered),
                "findings": [
                    {
                        "pattern_type": getattr(f, 'pattern_type', 'unknown'),
                        "value": str(getattr(f, 'value', ''))[:100],  # Truncate long values
                        "confidence": getattr(f, 'confidence', 0),
                        "risk_level": getattr(f, 'risk_level', 'UNKNOWN'),
                        "url": getattr(f, 'url', ''),
                        "category": getattr(f, 'category', 'unknown')
                    }
                    for f in result.findings
                ],
                "errors": result.errors
            }
            results_data["scan_results"].append(result_data)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_path}")
    
    def create_sample_targets_file(self, file_path: str, format_type: str = "json"):
        """Create a sample targets file for testing"""
        sample_targets = [
            {
                "url": "https://httpbin.org",
                "domain": "httpbin.org",
                "priority": "HIGH",
                "depth": 2,
                "max_pages": 10,
                "scan_js": True,
                "metadata": {
                    "description": "HTTP testing service",
                    "category": "testing"
                }
            },
            {
                "url": "https://jsonplaceholder.typicode.com",
                "domain": "jsonplaceholder.typicode.com", 
                "priority": "MEDIUM",
                "depth": 1,
                "max_pages": 5,
                "scan_js": True,
                "metadata": {
                    "description": "JSON API testing service",
                    "category": "testing"
                }
            },
            {
                "url": "https://reqres.in",
                "domain": "reqres.in",
                "priority": "LOW",
                "depth": 1,
                "max_pages": 5,
                "scan_js": False,
                "metadata": {
                    "description": "REST API testing service",
                    "category": "testing"
                }
            }
        ]
        
        if format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"targets": sample_targets}, f, indent=2)
        
        elif format_type.lower() == "csv":
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['url', 'domain', 'priority', 'depth', 'max_pages', 'scan_js', 'description', 'category']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for target in sample_targets:
                    row = {
                        'url': target['url'],
                        'domain': target['domain'],
                        'priority': target['priority'],
                        'depth': target['depth'],
                        'max_pages': target['max_pages'],
                        'scan_js': target['scan_js'],
                        'description': target['metadata']['description'],
                        'category': target['metadata']['category']
                    }
                    writer.writerow(row)
        
        print(f"Sample targets file created: {file_path}")
    
    def generate_executive_report(self, batch_result: BatchScanResult) -> Dict[str, Any]:
        """Generate executive summary report"""
        # Calculate risk distribution
        risk_distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        pattern_distribution = {}
        
        for result in batch_result.results:
            for finding in result.findings:
                risk_level = getattr(finding, 'risk_level', 'LOW')
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
                
                pattern_type = getattr(finding, 'pattern_type', 'unknown')
                pattern_distribution[pattern_type] = pattern_distribution.get(pattern_type, 0) + 1
        
        # Calculate success metrics
        success_rate = (batch_result.targets_scanned / 
                       (batch_result.targets_scanned + len(batch_result.failed_targets))) * 100
        
        avg_findings_per_target = (batch_result.total_findings / 
                                  batch_result.targets_scanned) if batch_result.targets_scanned > 0 else 0
        
        return {
            "executive_summary": {
                "scan_timestamp": datetime.now().isoformat(),
                "targets_processed": batch_result.targets_scanned + len(batch_result.failed_targets),
                "successful_scans": batch_result.targets_scanned,
                "failed_scans": len(batch_result.failed_targets),
                "success_rate_percent": round(success_rate, 2),
                "total_scan_time_minutes": round(batch_result.total_scan_time / 60, 2),
                "total_security_findings": batch_result.total_findings,
                "high_risk_findings": batch_result.high_risk_findings,
                "avg_findings_per_target": round(avg_findings_per_target, 2)
            },
            "risk_analysis": {
                "findings_by_risk_level": risk_distribution,
                "critical_risk_ratio": round((risk_distribution.get("CRITICAL", 0) / 
                                            max(batch_result.total_findings, 1)) * 100, 2),
                "high_risk_ratio": round((risk_distribution.get("HIGH", 0) / 
                                        max(batch_result.total_findings, 1)) * 100, 2)
            },
            "pattern_analysis": {
                "top_patterns": sorted(pattern_distribution.items(), 
                                     key=lambda x: x[1], reverse=True)[:10],
                "unique_pattern_types": len(pattern_distribution)
            },
            "performance_metrics": {
                "total_pages_scanned": sum(r.pages_scanned for r in batch_result.results),
                "avg_pages_per_target": round(sum(r.pages_scanned for r in batch_result.results) / 
                                            max(batch_result.targets_scanned, 1), 2),
                "avg_scan_time_per_target": round(batch_result.total_scan_time / 
                                                max(batch_result.targets_scanned, 1), 2)
            },
            "recommendations": self._generate_recommendations(batch_result, risk_distribution)
        }
    
    def _generate_recommendations(self, batch_result: BatchScanResult, 
                                risk_distribution: Dict[str, int]) -> List[Dict[str, str]]:
        """Generate security recommendations based on scan results"""
        recommendations = []
        
        if risk_distribution.get("CRITICAL", 0) > 0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Immediate Action Required",
                "recommendation": f"Found {risk_distribution['CRITICAL']} critical security issues. "
                                "Immediately investigate and remediate all critical findings.",
                "impact": "High risk of data breach or system compromise"
            })
        
        if risk_distribution.get("HIGH", 0) > batch_result.targets_scanned:
            recommendations.append({
                "priority": "HIGH", 
                "category": "Security Hardening",
                "recommendation": "High number of security findings detected. "
                                "Implement comprehensive security review and hardening measures.",
                "impact": "Significant security vulnerabilities present"
            })
        
        if len(batch_result.failed_targets) > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Scan Coverage",
                "recommendation": f"{len(batch_result.failed_targets)} targets failed to scan. "
                                "Review network accessibility and scan configuration.",
                "impact": "Incomplete security assessment coverage"
            })
        
        return recommendations