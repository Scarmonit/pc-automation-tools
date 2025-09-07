#!/usr/bin/env python3
"""
Stealth Web Scanner with Advanced Evasion Techniques
Advanced penetration testing capabilities with stealth scanning, evasion, and deep crawling
"""

import asyncio
import aiohttp
import random
import time
import json
import re
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from dataclasses import dataclass, field
import ssl
from advanced_pattern_scanner import AdvancedPatternScanner
from web_api_scanner import WebAPIKeyScanner, WebTarget, WebScanResult


@dataclass 
class StealthConfig:
    """Configuration for stealth scanning operations"""
    # User agent rotation
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ])
    
    # Timing evasion
    request_delay_range: Tuple[float, float] = (0.5, 3.0)
    burst_delay_range: Tuple[float, float] = (5.0, 15.0)
    burst_size: int = 5
    
    # IP rotation and proxy support
    proxy_list: List[str] = field(default_factory=list)
    rotate_proxies: bool = False
    
    # Request fingerprint evasion
    randomize_headers: bool = True
    spoof_referrer: bool = True
    randomize_accept_language: bool = True
    
    # Advanced evasion
    cookie_jar_persistence: bool = True
    javascript_execution: bool = False  # Requires additional deps
    form_auto_submission: bool = False
    
    # Deep crawling settings
    max_depth: int = 5
    follow_redirects: bool = True
    scan_subdomains: bool = False
    scan_hidden_directories: bool = True
    
    # Content analysis
    analyze_comments: bool = True
    analyze_metadata: bool = True
    decode_obfuscated: bool = True
    
    # Detection evasion
    avoid_honeypots: bool = True
    respect_rate_limits: bool = True
    mimic_human_behavior: bool = True


@dataclass
class StealthScanResult:
    """Enhanced scan result with stealth operation metadata"""
    target: WebTarget
    findings: List[Any] = field(default_factory=list)
    pages_scanned: int = 0
    scan_duration: float = 0.0
    evasion_techniques_used: List[str] = field(default_factory=list)
    detection_events: List[str] = field(default_factory=list)
    blocked_requests: int = 0
    proxy_rotations: int = 0
    fingerprint_variations: int = 0
    stealth_score: float = 0.0  # Success rate avoiding detection


class StealthWebScanner:
    """Advanced stealth web scanner with evasion capabilities"""
    
    def __init__(self, config: Optional[StealthConfig] = None):
        self.config = config or StealthConfig()
        self.pattern_scanner = AdvancedPatternScanner()
        self.web_scanner = WebAPIKeyScanner()
        
        # Stealth state tracking
        self.session_cookies = {}
        self.visited_urls = set()
        self.failed_requests = set()
        self.proxy_index = 0
        self.request_count = 0
        self.last_request_time = 0
        
        # Evasion techniques
        self.common_paths = [
            '/robots.txt', '/.well-known/security.txt', '/sitemap.xml',
            '/.git/config', '/.env', '/config.json', '/package.json',
            '/admin/', '/api/', '/dashboard/', '/login/', '/wp-admin/',
            '/phpmyadmin/', '/administrator/', '/manager/', '/console/'
        ]
        
        self.suspicious_extensions = [
            '.backup', '.bak', '.old', '.tmp', '.swp', '.orig',
            '.config', '.conf', '.ini', '.yaml', '.yml', '.json',
            '.env', '.log', '.sql', '.db'
        ]

    async def scan_with_stealth(self, target: WebTarget) -> StealthScanResult:
        """Perform stealth scan with advanced evasion techniques"""
        start_time = time.time()
        result = StealthScanResult(target=target)
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl.create_default_context()),
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            
            try:
                # Phase 1: Reconnaissance with stealth
                await self._stealth_reconnaissance(session, target, result)
                
                # Phase 2: Deep crawling with evasion
                await self._deep_crawl_with_evasion(session, target, result)
                
                # Phase 3: Hidden resource discovery
                await self._discover_hidden_resources(session, target, result)
                
                # Phase 4: Advanced content analysis
                await self._advanced_content_analysis(session, target, result)
                
            except Exception as e:
                result.detection_events.append(f"Scan interrupted: {str(e)}")
            
            result.scan_duration = time.time() - start_time
            result.stealth_score = self._calculate_stealth_score(result)
            
        return result

    async def _stealth_reconnaissance(self, session: aiohttp.ClientSession, 
                                   target: WebTarget, result: StealthScanResult):
        """Initial reconnaissance with maximum stealth"""
        result.evasion_techniques_used.append("stealth_reconnaissance")
        
        # Check robots.txt first (common, non-suspicious)
        robots_url = urljoin(target.url, '/robots.txt')
        robots_content = await self._stealth_request(session, robots_url, result)
        
        if robots_content:
            # Parse robots.txt for interesting paths
            hidden_paths = self._parse_robots_txt(robots_content)
            for path in hidden_paths[:10]:  # Limit to avoid detection
                full_url = urljoin(target.url, path)
                await self._stealth_request(session, full_url, result)
                await self._random_delay()

    async def _deep_crawl_with_evasion(self, session: aiohttp.ClientSession,
                                     target: WebTarget, result: StealthScanResult):
        """Deep crawling with human-like behavior simulation"""
        result.evasion_techniques_used.append("deep_crawl_evasion")
        
        to_visit = [(target.url, 0)]  # (url, depth)
        visited = set()
        
        while to_visit and len(visited) < target.max_pages:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > self.config.max_depth:
                continue
                
            visited.add(url)
            
            # Human-like browsing pattern
            await self._simulate_human_behavior(session, url, result)
            
            content = await self._stealth_request(session, url, result)
            if content:
                # Analyze content for API keys
                findings = await self._analyze_content_stealth(content, url)
                result.findings.extend(findings)
                
                # Extract links for further crawling
                links = self._extract_links_advanced(content, url)
                for link in links[:5]:  # Limit to avoid being obvious
                    if self._should_follow_link(link, target.url):
                        to_visit.append((link, depth + 1))
            
            result.pages_scanned += 1
            await self._adaptive_delay(result)

    async def _discover_hidden_resources(self, session: aiohttp.ClientSession,
                                       target: WebTarget, result: StealthScanResult):
        """Discover hidden directories and files with stealth"""
        result.evasion_techniques_used.append("hidden_resource_discovery")
        
        base_url = target.url.rstrip('/')
        
        # Test common hidden paths with randomized order
        test_paths = self.common_paths.copy()
        random.shuffle(test_paths)
        
        for path in test_paths[:15]:  # Limit to avoid detection
            test_url = base_url + path
            
            # Vary request patterns to avoid detection
            headers = await self._generate_stealth_headers(target.url)
            
            try:
                async with session.get(test_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Analyze discovered content
                        findings = await self._analyze_content_stealth(content, test_url)
                        result.findings.extend(findings)
                        
                        result.evasion_techniques_used.append(f"discovered_hidden:{path}")
                        
            except Exception as e:
                result.detection_events.append(f"Hidden resource failed: {path}")
            
            await self._random_delay()

    async def _advanced_content_analysis(self, session: aiohttp.ClientSession,
                                       target: WebTarget, result: StealthScanResult):
        """Advanced analysis of discovered content"""
        result.evasion_techniques_used.append("advanced_content_analysis")
        
        # Analyze JavaScript files more thoroughly
        js_urls = [url for url in self.visited_urls if url.endswith('.js')]
        
        for js_url in js_urls[:10]:  # Limit analysis
            content = await self._stealth_request(session, js_url, result)
            if content:
                # Deobfuscate and analyze JavaScript
                deobfuscated = self._deobfuscate_javascript(content)
                findings = await self._analyze_content_stealth(deobfuscated, js_url)
                result.findings.extend(findings)
                
                await self._random_delay()

    async def _stealth_request(self, session: aiohttp.ClientSession, 
                             url: str, result: StealthScanResult) -> Optional[str]:
        """Make HTTP request with full stealth capabilities"""
        try:
            # Implement request delay and bursting
            await self._adaptive_delay(result)
            
            # Generate stealth headers
            headers = await self._generate_stealth_headers(url)
            
            # Proxy rotation if configured
            proxy = self._get_next_proxy()
            
            self.request_count += 1
            result.fingerprint_variations += 1
            
            async with session.get(
                url, 
                headers=headers, 
                proxy=proxy,
                allow_redirects=self.config.follow_redirects
            ) as response:
                
                # Check for anti-bot measures
                if self._detect_anti_bot_measures(response):
                    result.detection_events.append(f"Anti-bot detected: {url}")
                    result.blocked_requests += 1
                    return None
                
                if response.status == 200:
                    content = await response.text()
                    self.visited_urls.add(url)
                    return content
                    
                elif response.status in [403, 429, 503]:
                    result.blocked_requests += 1
                    result.detection_events.append(f"Blocked {response.status}: {url}")
                    
                return None
                
        except Exception as e:
            result.detection_events.append(f"Request failed: {url} - {str(e)}")
            return None

    async def _generate_stealth_headers(self, url: str) -> Dict[str, str]:
        """Generate randomized headers to avoid fingerprinting"""
        parsed = urlparse(url)
        
        headers = {
            'User-Agent': random.choice(self.config.user_agents),
            'Accept': self._random_accept_header(),
            'Accept-Language': self._random_accept_language() if self.config.randomize_accept_language else 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Host': parsed.netloc
        }
        
        # Randomize additional headers
        if self.config.randomize_headers:
            if random.random() < 0.3:
                headers['DNT'] = '1'
            if random.random() < 0.5:
                headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0'])
        
        # Spoof referrer
        if self.config.spoof_referrer and random.random() < 0.7:
            referrers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                f'https://{parsed.netloc}/',
                ''
            ]
            headers['Referer'] = random.choice(referrers)
        
        return headers

    def _random_accept_header(self) -> str:
        """Generate randomized Accept header"""
        accepts = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        ]
        return random.choice(accepts)

    def _random_accept_language(self) -> str:
        """Generate randomized Accept-Language header"""
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.8,es;q=0.6',
            'en-US,en;q=0.9,fr;q=0.8',
            'en,en-US;q=0.8'
        ]
        return random.choice(languages)

    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation if configured"""
        if not self.config.rotate_proxies or not self.config.proxy_list:
            return None
            
        proxy = self.config.proxy_list[self.proxy_index % len(self.config.proxy_list)]
        self.proxy_index += 1
        return proxy

    async def _adaptive_delay(self, result: StealthScanResult):
        """Implement adaptive delays based on response patterns"""
        current_time = time.time()
        
        # Basic request delay
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            min_delay = random.uniform(*self.config.request_delay_range)
            
            if time_since_last < min_delay:
                await asyncio.sleep(min_delay - time_since_last)
        
        # Burst control
        if self.request_count % self.config.burst_size == 0:
            burst_delay = random.uniform(*self.config.burst_delay_range)
            await asyncio.sleep(burst_delay)
        
        # Adaptive delay based on blocked requests
        if result.blocked_requests > 3:
            adaptive_delay = min(30.0, result.blocked_requests * 2.0)
            await asyncio.sleep(adaptive_delay)
        
        self.last_request_time = current_time

    async def _random_delay(self):
        """Random delay to mimic human behavior"""
        delay = random.uniform(0.1, 2.0)
        await asyncio.sleep(delay)

    async def _simulate_human_behavior(self, session: aiohttp.ClientSession, 
                                     url: str, result: StealthScanResult):
        """Simulate human browsing behavior"""
        if not self.config.mimic_human_behavior:
            return
        
        # Occasionally load common resources like favicon
        if random.random() < 0.1:
            favicon_url = urljoin(url, '/favicon.ico')
            try:
                async with session.get(favicon_url) as response:
                    pass  # Just make the request
            except:
                pass
        
        # Simulate reading time
        if random.random() < 0.3:
            read_time = random.uniform(1.0, 5.0)
            await asyncio.sleep(read_time)

    def _detect_anti_bot_measures(self, response: aiohttp.ClientResponse) -> bool:
        """Detect if anti-bot measures are active"""
        # Check for common anti-bot indicators
        headers = response.headers
        
        # Cloudflare challenge
        if 'cf-ray' in headers and response.status == 503:
            return True
        
        # Rate limiting headers
        if any(h in headers for h in ['x-ratelimit-remaining', 'retry-after']):
            if headers.get('x-ratelimit-remaining') == '0':
                return True
        
        # Common bot detection services
        if any(service in headers.get('server', '').lower() for service in ['cloudflare', 'incapsula']):
            if response.status in [403, 503]:
                return True
        
        return False

    def _parse_robots_txt(self, content: str) -> List[str]:
        """Parse robots.txt to find interesting paths"""
        paths = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Disallow:') or line.startswith('Allow:'):
                path = line.split(':', 1)[1].strip()
                if path and path != '/' and len(path) > 1:
                    paths.append(path)
        
        return paths[:20]  # Limit results

    def _extract_links_advanced(self, content: str, base_url: str) -> List[str]:
        """Advanced link extraction with stealth considerations"""
        links = []
        
        # HTML links
        html_links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', content)
        
        # JavaScript URLs
        js_links = re.findall(r'[\'"]([^\'"]*/[^\'"]*\.[a-z]{2,4})[\'"]', content)
        
        # API endpoints
        api_links = re.findall(r'[\'"]([^\'"]*\/api\/[^\'"]*)[\'"]', content)
        
        all_links = html_links + js_links + api_links
        
        for link in all_links:
            if link and not link.startswith('#'):
                full_url = urljoin(base_url, link)
                if self._is_valid_url(full_url):
                    links.append(full_url)
        
        return list(set(links))

    def _should_follow_link(self, url: str, base_url: str) -> bool:
        """Determine if a link should be followed based on stealth criteria"""
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # Same domain check
        if not self.config.scan_subdomains and parsed_url.netloc != parsed_base.netloc:
            return False
        
        # Avoid obvious traps
        suspicious_patterns = ['logout', 'signout', 'delete', 'remove', 'admin/users']
        path_lower = parsed_url.path.lower()
        
        if any(pattern in path_lower for pattern in suspicious_patterns):
            return False
        
        return True

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for scanning"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False

    def _deobfuscate_javascript(self, content: str) -> str:
        """Basic JavaScript deobfuscation"""
        # Decode base64 strings
        b64_pattern = r'atob\([\'"]([A-Za-z0-9+/=]+)[\'"]\)'
        matches = re.findall(b64_pattern, content)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                content += f'\n// Decoded: {decoded}'
            except:
                pass
        
        # URL decode
        url_pattern = r'decodeURIComponent\([\'"]([^\'"]+)[\'"]\)'
        matches = re.findall(url_pattern, content)
        
        for match in matches:
            try:
                decoded = unquote(match)
                content += f'\n// URL Decoded: {decoded}'
            except:
                pass
        
        return content

    async def _analyze_content_stealth(self, content: str, url: str) -> List[Any]:
        """Analyze content for API keys with stealth considerations"""
        findings = []
        
        # Use the advanced pattern scanner
        pattern_findings = self.pattern_scanner.scan_content(content, url)
        
        # Filter out potential false positives in stealth mode
        for finding in pattern_findings:
            # Skip very low confidence findings to avoid false alarms
            if finding.confidence > 0.3:
                findings.append(finding)
        
        return findings

    def _calculate_stealth_score(self, result: StealthScanResult) -> float:
        """Calculate how stealthy the scan was"""
        total_requests = result.pages_scanned + result.blocked_requests
        if total_requests == 0:
            return 1.0
        
        # Base score from successful requests
        success_rate = result.pages_scanned / total_requests
        
        # Penalties for detection events
        detection_penalty = min(0.5, len(result.detection_events) * 0.1)
        
        # Bonus for evasion techniques used
        evasion_bonus = min(0.2, len(result.evasion_techniques_used) * 0.02)
        
        stealth_score = success_rate - detection_penalty + evasion_bonus
        return max(0.0, min(1.0, stealth_score))

    def generate_stealth_report(self, results: List[StealthScanResult]) -> Dict[str, Any]:
        """Generate comprehensive stealth scan report"""
        total_findings = sum(len(r.findings) for r in results)
        avg_stealth_score = sum(r.stealth_score for r in results) / len(results) if results else 0
        total_evasion_techniques = sum(len(r.evasion_techniques_used) for r in results)
        
        return {
            "scan_summary": {
                "targets_scanned": len(results),
                "total_findings": total_findings,
                "average_stealth_score": round(avg_stealth_score, 3),
                "total_evasion_techniques": total_evasion_techniques,
                "scan_timestamp": datetime.now().isoformat()
            },
            "stealth_metrics": {
                "total_pages_scanned": sum(r.pages_scanned for r in results),
                "total_blocked_requests": sum(r.blocked_requests for r in results),
                "total_detection_events": sum(len(r.detection_events) for r in results),
                "proxy_rotations": sum(r.proxy_rotations for r in results),
                "fingerprint_variations": sum(r.fingerprint_variations for r in results)
            },
            "evasion_techniques": {
                technique: sum(1 for r in results if technique in r.evasion_techniques_used)
                for technique in set().union(*(r.evasion_techniques_used for r in results))
            },
            "results": [
                {
                    "target_url": r.target.url,
                    "findings_count": len(r.findings),
                    "stealth_score": r.stealth_score,
                    "pages_scanned": r.pages_scanned,
                    "blocked_requests": r.blocked_requests,
                    "detection_events": len(r.detection_events),
                    "scan_duration": round(r.scan_duration, 2)
                }
                for r in results
            ]
        }


async def demo_stealth_scan():
    """Demonstrate stealth scanning capabilities"""
    print("Advanced Stealth Web Scanner - Penetration Testing Demo")
    print("=" * 60)
    
    # Configure stealth settings
    stealth_config = StealthConfig(
        max_depth=2,
        randomize_headers=True,
        mimic_human_behavior=True,
        avoid_honeypots=True,
        respect_rate_limits=True
    )
    
    scanner = StealthWebScanner(stealth_config)
    
    # Safe testing targets with stealth scanning
    test_targets = [
        WebTarget(
            url="https://httpbin.org",
            domain="httpbin.org",
            depth=1,
            max_pages=3,
            scan_js=True
        ),
        WebTarget(
            url="https://jsonplaceholder.typicode.com", 
            domain="jsonplaceholder.typicode.com",
            depth=1,
            max_pages=3,
            scan_js=True
        )
    ]
    
    results = []
    for target in test_targets:
        print(f"Stealth scanning {target.url}...")
        result = await scanner.scan_with_stealth(target)
        results.append(result)
        
        print(f"  Stealth Score: {result.stealth_score:.3f}")
        print(f"  Pages Scanned: {result.pages_scanned}")
        print(f"  Findings: {len(result.findings)}")
        print(f"  Evasion Techniques: {len(result.evasion_techniques_used)}")
        print(f"  Detection Events: {len(result.detection_events)}")
        print()
    
    # Generate report
    report = scanner.generate_stealth_report(results)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"stealth_scan_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Stealth scan report saved: {report_file}")
    print(f"Average Stealth Score: {report['scan_summary']['average_stealth_score']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(demo_stealth_scan())