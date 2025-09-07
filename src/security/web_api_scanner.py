#!/usr/bin/env python3
"""
Web API Key Scanner - Multi-target web vulnerability scanning
Advanced web crawling and API key detection system
"""

import requests
import re
import json
import time
import threading
from urllib.parse import urljoin, urlparse, quote
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from advanced_pattern_scanner import AdvancedPatternScanner


@dataclass
class WebTarget:
    """Web scanning target configuration"""
    url: str
    domain: str
    depth: int = 2
    max_pages: int = 50
    scan_js: bool = True
    scan_css: bool = True
    follow_external: bool = False
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class WebScanResult:
    """Web scan results"""
    target: WebTarget
    findings: List[Any] = field(default_factory=list)
    pages_scanned: int = 0
    scan_duration: float = 0.0
    urls_discovered: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)


class WebAPIKeyScanner:
    """Web API key scanner with crawling capabilities"""
    
    def __init__(self):
        self.pattern_scanner = AdvancedPatternScanner()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Web-specific patterns for client-side detection
        self.web_patterns = {
            'firebase_config': r'apiKey:\s*["\']AIza[0-9A-Za-z\-_]{35}["\']',
            'js_api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([A-Za-z0-9\-_\.]{16,})["\']',
            'env_api_key': r'(?i)REACT_APP_[A-Z_]+[=:]\s*[A-Za-z0-9\-_\.]{16,}',
            'url_api_key': r'[?&]api[_-]?key=([A-Za-z0-9\-_\.]{16,})',
            'stripe_publishable': r'\b(pk_live_[0-9a-zA-Z]{24,})\b',
            'google_api_key': r'\b(AIza[0-9A-Za-z\-_]{35})\b',
            'mapbox_token': r'\b(pk\.[a-zA-Z0-9]{60,})\b',
            'jwt_token': r'\b(eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*)\b'
        }
    
    def scan_target(self, target: WebTarget) -> WebScanResult:
        """Scan a web target for API keys and credentials"""
        start_time = time.time()
        result = WebScanResult(target=target)
        
        try:
            # Update session with target-specific settings
            if target.cookies:
                self.session.cookies.update(target.cookies)
            if target.headers:
                self.session.headers.update(target.headers)
            
            # Start crawling from target URL
            to_crawl = [target.url]
            crawled = set()
            
            for depth in range(target.depth + 1):
                if not to_crawl or len(crawled) >= target.max_pages:
                    break
                
                current_level = to_crawl.copy()
                to_crawl = []
                
                for url in current_level:
                    if url in crawled or len(crawled) >= target.max_pages:
                        continue
                    
                    crawled.add(url)
                    
                    # Scan the page
                    page_result = self._scan_page(url, target)
                    if page_result:
                        result.findings.extend(page_result['findings'])
                        result.urls_discovered.update(page_result['links'])
                        
                        # Add new links for next depth level
                        for link in page_result['links']:
                            if link not in crawled and self._should_crawl_url(link, target):
                                to_crawl.append(link)
                    
                    result.pages_scanned += 1
                    
                    # Rate limiting
                    time.sleep(0.5)
        
        except Exception as e:
            result.errors.append(f"Scan error: {str(e)}")
        
        result.scan_duration = time.time() - start_time
        return result
    
    def _scan_page(self, url: str, target: WebTarget) -> Optional[Dict[str, Any]]:
        """Scan a single web page"""
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            content = response.text
            findings = []
            links = set()
            
            # Scan content with pattern scanner
            pattern_findings = self.pattern_scanner.scan_content(content, url)
            findings.extend(pattern_findings)
            
            # Scan with web-specific patterns
            for pattern_name, pattern in self.web_patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    if len(value) > 10:  # Skip very short matches
                        findings.append({
                            'pattern_type': pattern_name,
                            'value': value,
                            'url': url,
                            'confidence': 0.8,
                            'risk_level': 'HIGH' if 'live' in value else 'MEDIUM'
                        })
            
            # Extract links
            link_patterns = [
                r'href=["\']([^"\']*)["\']',
                r'src=["\']([^"\']*)["\']'
            ]
            
            for link_pattern in link_patterns:
                matches = re.finditer(link_pattern, content, re.IGNORECASE)
                for match in matches:
                    link = match.group(1)
                    if link and not link.startswith('#') and not link.startswith('mailto:'):
                        full_url = urljoin(url, link)
                        links.add(full_url)
            
            # Scan JavaScript files if enabled
            if target.scan_js:
                js_links = [link for link in links if link.endswith('.js')]
                for js_link in js_links[:10]:  # Limit JS file scanning
                    js_findings = self._scan_javascript_file(js_link)
                    findings.extend(js_findings)
            
            return {
                'findings': findings,
                'links': links
            }
            
        except Exception as e:
            return None
    
    def _scan_javascript_file(self, js_url: str) -> List[Dict[str, Any]]:
        """Scan JavaScript file for sensitive data"""
        findings = []
        
        try:
            response = self.session.get(js_url, timeout=10)
            if response.status_code == 200:
                js_content = response.text
                
                # Scan with pattern scanner
                js_findings = self.pattern_scanner.scan_content(js_content, js_url)
                findings.extend(js_findings)
                
                # Additional JS-specific patterns
                js_patterns = {
                    'config_object': r'(?i)config\s*[=:]\s*\{[^}]*["\']?([A-Za-z0-9\-_]{20,})["\']?[^}]*\}',
                    'api_endpoint': r'["\']([^"\']*\/api\/[^"\']*)["\']',
                    'token_var': r'(?i)(token|key)\s*[=:]\s*["\']([A-Za-z0-9\-_\.]{16,})["\']'
                }
                
                for pattern_name, pattern in js_patterns.items():
                    matches = re.finditer(pattern, js_content)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        findings.append({
                            'pattern_type': f'js_{pattern_name}',
                            'value': value,
                            'url': js_url,
                            'confidence': 0.7,
                            'risk_level': 'MEDIUM'
                        })
        
        except Exception:
            pass
        
        return findings
    
    def _should_crawl_url(self, url: str, target: WebTarget) -> bool:
        """Determine if URL should be crawled"""
        try:
            parsed = urlparse(url)
            target_parsed = urlparse(target.url)
            
            # Same domain check
            if not target.follow_external and parsed.netloc != target_parsed.netloc:
                return False
            
            # Avoid common traps
            avoid_patterns = ['logout', 'signout', 'delete', 'remove']
            url_lower = url.lower()
            
            if any(pattern in url_lower for pattern in avoid_patterns):
                return False
            
            # Skip binary files
            if any(url.lower().endswith(ext) for ext in ['.pdf', '.zip', '.exe', '.img']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def scan_multiple_targets(self, targets: List[WebTarget]) -> List[WebScanResult]:
        """Scan multiple targets concurrently"""
        results = []
        threads = []
        
        def scan_target_thread(target):
            result = self.scan_target(target)
            results.append(result)
        
        # Start threads for each target
        for target in targets:
            thread = threading.Thread(target=scan_target_thread, args=(target,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return results