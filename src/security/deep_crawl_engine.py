#!/usr/bin/env python3
"""
Deep Crawl Engine with Advanced Discovery Capabilities
Comprehensive deep web crawling for thorough security assessment
"""

import asyncio
import aiohttp
import aiofiles
import json
import re
import hashlib
import mimetypes
import zipfile
import tarfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from urllib.parse import urljoin, urlparse, parse_qs, unquote, quote
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET
from advanced_pattern_scanner import AdvancedPatternScanner


@dataclass
class CrawlTarget:
    """Deep crawling target configuration"""
    url: str
    domain: str
    max_depth: int = 10
    max_pages: int = 1000
    
    # Content types to analyze
    scan_javascript: bool = True
    scan_css: bool = True
    scan_images: bool = False
    scan_documents: bool = True
    scan_archives: bool = True
    scan_configs: bool = True
    
    # Advanced discovery
    discover_apis: bool = True
    discover_admin_panels: bool = True
    discover_backup_files: bool = True
    discover_temp_files: bool = True
    discover_version_control: bool = True
    
    # Crawling behavior
    follow_external_links: bool = False
    follow_subdomains: bool = True
    extract_from_sitemaps: bool = True
    extract_from_robots: bool = True
    
    # Authentication
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class CrawlResult:
    """Deep crawl result with comprehensive findings"""
    target: CrawlTarget
    discovered_urls: Set[str] = field(default_factory=set)
    analyzed_files: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: Set[str] = field(default_factory=set)
    admin_panels: Set[str] = field(default_factory=set)
    sensitive_files: Dict[str, List[str]] = field(default_factory=dict)
    technology_stack: Dict[str, str] = field(default_factory=dict)
    security_findings: List[Any] = field(default_factory=list)
    crawl_statistics: Dict[str, int] = field(default_factory=dict)


class DeepCrawlEngine:
    """Advanced deep crawling engine for comprehensive discovery"""
    
    def __init__(self):
        self.pattern_scanner = AdvancedPatternScanner()
        
        # Directory and file discovery wordlists
        self.common_directories = [
            'admin', 'administrator', 'api', 'app', 'apps', 'assets', 'backup', 'backups',
            'bin', 'blog', 'cache', 'cgi-bin', 'cms', 'config', 'configs', 'console',
            'content', 'control', 'css', 'dashboard', 'data', 'db', 'debug', 'dev',
            'development', 'doc', 'docs', 'download', 'downloads', 'etc', 'files',
            'ftp', 'help', 'home', 'html', 'http', 'images', 'img', 'include',
            'includes', 'js', 'json', 'lib', 'library', 'log', 'logs', 'mail',
            'media', 'members', 'old', 'pages', 'panel', 'php', 'private', 'public',
            'resources', 'scripts', 'secure', 'server', 'setup', 'src', 'static',
            'system', 'temp', 'templates', 'test', 'tests', 'tmp', 'tools', 'upload',
            'uploads', 'user', 'users', 'var', 'web', 'webdav', 'www', 'xml'
        ]
        
        self.sensitive_files = [
            '.env', '.env.local', '.env.production', 'config.json', 'config.xml',
            'web.config', 'database.yml', 'secrets.yml', 'credentials.json',
            'aws.json', 'firebase.json', 'google-services.json', 'app.json',
            'package.json', 'composer.json', 'requirements.txt', 'Pipfile',
            'docker-compose.yml', 'Dockerfile', 'kubernetes.yml', 'deployment.yml',
            'backup.sql', 'dump.sql', 'database.sql', 'db_backup.sql',
            'error.log', 'access.log', 'debug.log', 'application.log',
            'phpinfo.php', 'info.php', 'test.php', 'debug.php',
            'readme.txt', 'README.md', 'CHANGELOG.md', 'TODO.txt',
            'robots.txt', 'sitemap.xml', 'crossdomain.xml', 'humans.txt'
        ]
        
        self.backup_extensions = [
            '.backup', '.bak', '.old', '.orig', '.copy', '.save', '.tmp',
            '.swp', '.swo', '.dist', '.sample', '.example', '.test',
            '~', '.1', '.2', '_backup', '_old', '_copy'
        ]
        
        self.admin_paths = [
            'admin', 'administrator', 'admin.php', 'admin.html', 'admin/',
            'wp-admin', 'wp-admin/', 'phpmyadmin', 'phpmyadmin/',
            'manager', 'manager/', 'console', 'console/', 'dashboard',
            'dashboard/', 'panel', 'panel/', 'control', 'control/',
            'login', 'login/', 'signin', 'signin/', 'auth', 'auth/'
        ]
        
        # API discovery patterns
        self.api_patterns = [
            r'/api/v\d+/', r'/api/', r'/v\d+/', r'/rest/', r'/graphql',
            r'/webhook/', r'/endpoints/', r'/services/', r'/rpc/'
        ]
        
        # Technology fingerprints
        self.tech_fingerprints = {
            'server_headers': {
                'Apache': 'Apache',
                'nginx': 'nginx',
                'IIS': 'Microsoft-IIS',
                'Cloudflare': 'cloudflare'
            },
            'powered_by': {
                'PHP': 'X-Powered-By.*PHP',
                'ASP.NET': 'X-Powered-By.*ASP.NET',
                'Express': 'X-Powered-By.*Express'
            },
            'content_patterns': {
                'WordPress': 'wp-content|wp-includes|wordpress',
                'Drupal': 'drupal|sites/default',
                'Joomla': 'joomla|administrator/index.php',
                'Laravel': 'laravel_session|_token',
                'Django': 'csrfmiddlewaretoken|Django',
                'React': 'react|ReactDOM',
                'Angular': 'ng-app|angular',
                'Vue.js': 'vue|v-if|v-for'
            }
        }

    async def deep_crawl(self, target: CrawlTarget) -> CrawlResult:
        """Perform comprehensive deep crawling"""
        result = CrawlResult(target=target)
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=target.headers,
            cookies=target.cookies
        ) as session:
            
            # Phase 1: Initial discovery
            await self._initial_discovery(session, target, result)
            
            # Phase 2: Recursive crawling
            await self._recursive_crawl(session, target, result)
            
            # Phase 3: Directory and file discovery
            await self._directory_discovery(session, target, result)
            
            # Phase 4: Backup and sensitive file discovery
            await self._backup_file_discovery(session, target, result)
            
            # Phase 5: API endpoint discovery
            await self._api_discovery(session, target, result)
            
            # Phase 6: Admin panel discovery
            await self._admin_panel_discovery(session, target, result)
            
            # Phase 7: Technology stack fingerprinting
            await self._technology_fingerprinting(session, target, result)
            
            # Phase 8: Archive and document analysis
            await self._archive_analysis(session, target, result)
        
        # Generate statistics
        result.crawl_statistics = self._generate_statistics(result)
        
        return result

    async def _initial_discovery(self, session: aiohttp.ClientSession,
                                target: CrawlTarget, result: CrawlResult):
        """Initial URL discovery from standard sources"""
        
        # Discover from robots.txt
        if target.extract_from_robots:
            await self._discover_from_robots(session, target, result)
        
        # Discover from sitemap.xml
        if target.extract_from_sitemaps:
            await self._discover_from_sitemaps(session, target, result)
        
        # Discover from main page
        await self._discover_from_page(session, target.url, target, result, depth=0)

    async def _discover_from_robots(self, session: aiohttp.ClientSession,
                                  target: CrawlTarget, result: CrawlResult):
        """Extract URLs from robots.txt"""
        robots_url = urljoin(target.url, '/robots.txt')
        
        try:
            async with session.get(robots_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse robots.txt
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith(('Disallow:', 'Allow:', 'Sitemap:')):
                            path = line.split(':', 1)[1].strip()
                            if path and path != '/':
                                if path.startswith('http'):
                                    result.discovered_urls.add(path)
                                else:
                                    full_url = urljoin(target.url, path)
                                    result.discovered_urls.add(full_url)
        except Exception:
            pass

    async def _discover_from_sitemaps(self, session: aiohttp.ClientSession,
                                    target: CrawlTarget, result: CrawlResult):
        """Extract URLs from sitemap files"""
        sitemap_urls = [
            urljoin(target.url, '/sitemap.xml'),
            urljoin(target.url, '/sitemap_index.xml'),
            urljoin(target.url, '/sitemaps/sitemap.xml')
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                async with session.get(sitemap_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse XML sitemap
                        urls = re.findall(r'<loc>(.*?)</loc>', content)
                        for url in urls[:100]:  # Limit to avoid overwhelming
                            if self._should_crawl_url(url, target):
                                result.discovered_urls.add(url)
            except Exception:
                continue

    async def _recursive_crawl(self, session: aiohttp.ClientSession,
                             target: CrawlTarget, result: CrawlResult):
        """Recursive crawling of discovered URLs"""
        to_crawl = list(result.discovered_urls)
        to_crawl.append(target.url)
        crawled = set()
        
        depth = 0
        while to_crawl and depth < target.max_depth and len(crawled) < target.max_pages:
            current_batch = to_crawl[:50]  # Process in batches
            to_crawl = to_crawl[50:]
            
            for url in current_batch:
                if url not in crawled:
                    crawled.add(url)
                    new_urls = await self._discover_from_page(session, url, target, result, depth)
                    
                    # Add new URLs for next depth level
                    for new_url in new_urls:
                        if new_url not in crawled and new_url not in to_crawl:
                            to_crawl.append(new_url)
            
            depth += 1

    async def _discover_from_page(self, session: aiohttp.ClientSession, url: str,
                                target: CrawlTarget, result: CrawlResult, depth: int) -> Set[str]:
        """Discover URLs and analyze content from a single page"""
        new_urls = set()
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return new_urls
                
                content = await response.text()
                content_type = response.headers.get('content-type', '')
                
                # Analyze content for security findings
                findings = self.pattern_scanner.scan_content(content, url)
                result.security_findings.extend(findings)
                
                # Store analyzed file info
                result.analyzed_files[url] = {
                    'content_type': content_type,
                    'size': len(content),
                    'status_code': response.status,
                    'findings_count': len(findings)
                }
                
                # Extract links
                if 'text/html' in content_type.lower():
                    new_urls.update(self._extract_html_links(content, url, target))
                
                # Extract JavaScript URLs
                if target.scan_javascript:
                    new_urls.update(self._extract_js_links(content, url))
                
                # Extract CSS URLs
                if target.scan_css:
                    new_urls.update(self._extract_css_links(content, url))
                
        except Exception:
            pass
        
        return new_urls

    async def _directory_discovery(self, session: aiohttp.ClientSession,
                                 target: CrawlTarget, result: CrawlResult):
        """Discover directories using common wordlists"""
        base_url = target.url.rstrip('/')
        
        for directory in self.common_directories[:50]:  # Limit to avoid being too aggressive
            test_url = f"{base_url}/{directory}/"
            
            try:
                async with session.get(test_url, allow_redirects=False) as response:
                    if response.status in [200, 301, 302, 403]:
                        result.discovered_urls.add(test_url)
                        
                        # If accessible, crawl this directory
                        if response.status == 200:
                            await self._discover_from_page(session, test_url, target, result, 0)
                        
            except Exception:
                continue
            
            # Rate limiting
            await asyncio.sleep(0.1)

    async def _backup_file_discovery(self, session: aiohttp.ClientSession,
                                   target: CrawlTarget, result: CrawlResult):
        """Discover backup and sensitive files"""
        base_url = target.url.rstrip('/')
        
        # Test common sensitive files
        for filename in self.sensitive_files:
            test_url = f"{base_url}/{filename}"
            
            try:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Categorize sensitive files
                        category = self._categorize_sensitive_file(filename)
                        if category not in result.sensitive_files:
                            result.sensitive_files[category] = []
                        
                        result.sensitive_files[category].append({
                            'url': test_url,
                            'size': len(content),
                            'findings': len(self.pattern_scanner.scan_content(content, test_url))
                        })
                        
            except Exception:
                continue
        
        # Test backup versions of discovered files
        for url in list(result.discovered_urls)[:20]:  # Limit to avoid too many requests
            if url.endswith('.php') or url.endswith('.html') or url.endswith('.js'):
                for ext in self.backup_extensions[:5]:
                    backup_url = url + ext
                    try:
                        async with session.get(backup_url) as response:
                            if response.status == 200:
                                if 'backup_files' not in result.sensitive_files:
                                    result.sensitive_files['backup_files'] = []
                                
                                result.sensitive_files['backup_files'].append({
                                    'url': backup_url,
                                    'original': url
                                })
                    except Exception:
                        continue

    async def _api_discovery(self, session: aiohttp.ClientSession,
                           target: CrawlTarget, result: CrawlResult):
        """Discover API endpoints"""
        if not target.discover_apis:
            return
        
        base_url = target.url.rstrip('/')
        
        # Common API paths
        api_paths = [
            '/api', '/api/v1', '/api/v2', '/api/v3',
            '/rest', '/rest/v1', '/graphql', '/webhook',
            '/endpoints', '/services'
        ]
        
        for path in api_paths:
            test_url = f"{base_url}{path}"
            
            try:
                async with session.get(test_url) as response:
                    if response.status in [200, 401, 403]:  # API might be protected
                        result.api_endpoints.add(test_url)
                        
                        # Try to discover API documentation
                        for doc_path in ['/docs', '/documentation', '/swagger', '/openapi']:
                            doc_url = test_url + doc_path
                            try:
                                async with session.get(doc_url) as doc_response:
                                    if doc_response.status == 200:
                                        result.api_endpoints.add(doc_url)
                            except Exception:
                                continue
                        
            except Exception:
                continue

    async def _admin_panel_discovery(self, session: aiohttp.ClientSession,
                                   target: CrawlTarget, result: CrawlResult):
        """Discover administrative panels"""
        if not target.discover_admin_panels:
            return
        
        base_url = target.url.rstrip('/')
        
        for path in self.admin_paths:
            test_url = f"{base_url}/{path}"
            
            try:
                async with session.get(test_url, allow_redirects=False) as response:
                    if response.status in [200, 301, 302, 401, 403]:
                        result.admin_panels.add(test_url)
                        
                        # If accessible, analyze the admin panel
                        if response.status == 200:
                            content = await response.text()
                            admin_findings = self.pattern_scanner.scan_content(content, test_url)
                            result.security_findings.extend(admin_findings)
                        
            except Exception:
                continue

    async def _technology_fingerprinting(self, session: aiohttp.ClientSession,
                                       target: CrawlTarget, result: CrawlResult):
        """Fingerprint technology stack"""
        try:
            async with session.get(target.url) as response:
                content = await response.text()
                headers = response.headers
                
                # Analyze server headers
                server_header = headers.get('server', '').lower()
                for tech, pattern in self.tech_fingerprints['server_headers'].items():
                    if pattern.lower() in server_header:
                        result.technology_stack[tech] = f"Server: {pattern}"
                
                # Analyze powered-by headers
                powered_by = headers.get('x-powered-by', '').lower()
                for tech, pattern in self.tech_fingerprints['powered_by'].items():
                    if re.search(pattern.lower(), powered_by):
                        result.technology_stack[tech] = f"X-Powered-By: {powered_by}"
                
                # Analyze content patterns
                content_lower = content.lower()
                for tech, pattern in self.tech_fingerprints['content_patterns'].items():
                    if re.search(pattern.lower(), content_lower):
                        result.technology_stack[tech] = "Content analysis"
                
        except Exception:
            pass

    async def _archive_analysis(self, session: aiohttp.ClientSession,
                              target: CrawlTarget, result: CrawlResult):
        """Analyze archives and documents for sensitive content"""
        if not target.scan_archives:
            return
        
        # Look for common archive files
        base_url = target.url.rstrip('/')
        archive_files = [
            'backup.zip', 'backup.tar.gz', 'backup.tar', 'site.zip',
            'www.zip', 'public.zip', 'files.zip', 'documents.zip',
            'export.zip', 'dump.tar.gz', 'archive.zip'
        ]
        
        for archive in archive_files:
            archive_url = f"{base_url}/{archive}"
            
            try:
                async with session.get(archive_url) as response:
                    if response.status == 200:
                        # Download and analyze archive
                        archive_data = await response.read()
                        findings = await self._analyze_archive_content(archive_data, archive_url)
                        result.security_findings.extend(findings)
                        
            except Exception:
                continue

    async def _analyze_archive_content(self, data: bytes, url: str) -> List[Any]:
        """Analyze content of archive files"""
        findings = []
        
        try:
            # Try to extract as ZIP
            if url.endswith('.zip'):
                import io
                with zipfile.ZipFile(io.BytesIO(data), 'r') as zip_ref:
                    for file_info in zip_ref.filelist[:50]:  # Limit files analyzed
                        try:
                            file_content = zip_ref.read(file_info.filename).decode('utf-8', errors='ignore')
                            file_findings = self.pattern_scanner.scan_content(file_content, f"{url}:{file_info.filename}")
                            findings.extend(file_findings)
                        except Exception:
                            continue
        except Exception:
            pass
        
        return findings

    def _extract_html_links(self, content: str, base_url: str, target: CrawlTarget) -> Set[str]:
        """Extract links from HTML content"""
        links = set()
        
        # Extract href links
        href_pattern = r'href=[\'"]([^\'"]*)[\'"]'
        matches = re.findall(href_pattern, content, re.IGNORECASE)
        
        for match in matches:
            if match and not match.startswith('#') and not match.startswith('mailto:'):
                full_url = urljoin(base_url, match)
                if self._should_crawl_url(full_url, target):
                    links.add(full_url)
        
        # Extract src links (for resources)
        src_pattern = r'src=[\'"]([^\'"]*)[\'"]'
        matches = re.findall(src_pattern, content, re.IGNORECASE)
        
        for match in matches:
            if match and not match.startswith('#'):
                full_url = urljoin(base_url, match)
                if self._should_crawl_url(full_url, target):
                    links.add(full_url)
        
        return links

    def _extract_js_links(self, content: str, base_url: str) -> Set[str]:
        """Extract URLs from JavaScript content"""
        links = set()
        
        # Common JavaScript URL patterns
        js_patterns = [
            r'[\'"]([^\'"]*\.js)[\'"]',
            r'[\'"]([^\'"]*\/api\/[^\'"]*)[\'"]',
            r'[\'"]([^\'"]*\.json)[\'"]'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                full_url = urljoin(base_url, match)
                links.add(full_url)
        
        return links

    def _extract_css_links(self, content: str, base_url: str) -> Set[str]:
        """Extract URLs from CSS content"""
        links = set()
        
        # CSS URL patterns
        css_pattern = r'url\([\'"]?([^\'"]*)[\'"]?\)'
        matches = re.findall(css_pattern, content)
        
        for match in matches:
            full_url = urljoin(base_url, match)
            links.add(full_url)
        
        return links

    def _should_crawl_url(self, url: str, target: CrawlTarget) -> bool:
        """Determine if URL should be crawled"""
        try:
            parsed = urlparse(url)
            target_parsed = urlparse(target.url)
            
            # Check domain restrictions
            if not target.follow_external_links and parsed.netloc != target_parsed.netloc:
                if not target.follow_subdomains or not parsed.netloc.endswith(f".{target_parsed.netloc}"):
                    return False
            
            # Avoid common trap URLs
            avoid_patterns = [
                'logout', 'signout', 'delete', 'remove', 'destroy',
                'mailto:', 'javascript:', 'tel:', 'ftp:'
            ]
            
            url_lower = url.lower()
            if any(pattern in url_lower for pattern in avoid_patterns):
                return False
            
            return True
            
        except Exception:
            return False

    def _categorize_sensitive_file(self, filename: str) -> str:
        """Categorize sensitive files by type"""
        if filename.startswith('.env'):
            return 'environment_files'
        elif filename.endswith(('.json', '.yml', '.yaml', '.xml')):
            return 'configuration_files'
        elif filename.endswith(('.sql', '.db')):
            return 'database_files'
        elif filename.endswith(('.log', '.txt')) and 'log' in filename:
            return 'log_files'
        elif filename.endswith(('.php', '.asp', '.aspx')) and 'info' in filename:
            return 'info_pages'
        else:
            return 'other_sensitive'

    def _generate_statistics(self, result: CrawlResult) -> Dict[str, int]:
        """Generate crawling statistics"""
        return {
            'total_urls_discovered': len(result.discovered_urls),
            'total_files_analyzed': len(result.analyzed_files),
            'api_endpoints_found': len(result.api_endpoints),
            'admin_panels_found': len(result.admin_panels),
            'sensitive_files_found': sum(len(files) for files in result.sensitive_files.values()),
            'security_findings': len(result.security_findings),
            'technologies_identified': len(result.technology_stack),
            'file_types_analyzed': len(set(
                info.get('content_type', '').split(';')[0] 
                for info in result.analyzed_files.values()
            ))
        }

    def generate_comprehensive_report(self, result: CrawlResult) -> Dict[str, Any]:
        """Generate comprehensive deep crawl report"""
        return {
            "crawl_summary": {
                "target_url": result.target.url,
                "crawl_timestamp": datetime.now().isoformat(),
                "statistics": result.crawl_statistics
            },
            "discovered_resources": {
                "total_urls": len(result.discovered_urls),
                "api_endpoints": list(result.api_endpoints),
                "admin_panels": list(result.admin_panels),
                "sensitive_files": result.sensitive_files
            },
            "technology_stack": result.technology_stack,
            "security_assessment": {
                "total_findings": len(result.security_findings),
                "findings_by_type": self._categorize_findings(result.security_findings),
                "high_risk_findings": [
                    {
                        "pattern": f.pattern_type,
                        "confidence": f.confidence,
                        "location": f.url,
                        "risk_level": f.risk_level
                    }
                    for f in result.security_findings 
                    if hasattr(f, 'risk_level') and f.risk_level in ['HIGH', 'CRITICAL']
                ]
            },
            "coverage_analysis": {
                "crawl_depth_achieved": min(result.target.max_depth, 10),
                "pages_vs_target": f"{len(result.analyzed_files)}/{result.target.max_pages}",
                "content_types_found": list(set(
                    info.get('content_type', '').split(';')[0] 
                    for info in result.analyzed_files.values()
                ))
            }
        }

    def _categorize_findings(self, findings: List[Any]) -> Dict[str, int]:
        """Categorize security findings by type"""
        categories = {}
        for finding in findings:
            if hasattr(finding, 'pattern_type'):
                category = finding.pattern_type
                categories[category] = categories.get(category, 0) + 1
        return categories


async def demo_deep_crawl():
    """Demonstrate deep crawling capabilities"""
    print("Deep Crawl Engine - Comprehensive Discovery Demo")
    print("=" * 50)
    
    # Configure deep crawling target
    target = CrawlTarget(
        url="https://httpbin.org",
        domain="httpbin.org",
        max_depth=3,
        max_pages=20,
        discover_apis=True,
        discover_admin_panels=True,
        discover_backup_files=True
    )
    
    engine = DeepCrawlEngine()
    
    print(f"Deep crawling {target.url}...")
    result = await engine.deep_crawl(target)
    
    # Generate and save report
    report = engine.generate_comprehensive_report(result)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"deep_crawl_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    print(f"\nDeep Crawl Results:")
    print(f"URLs Discovered: {len(result.discovered_urls)}")
    print(f"Files Analyzed: {len(result.analyzed_files)}")
    print(f"API Endpoints: {len(result.api_endpoints)}")
    print(f"Admin Panels: {len(result.admin_panels)}")
    print(f"Sensitive Files: {sum(len(files) for files in result.sensitive_files.values())}")
    print(f"Security Findings: {len(result.security_findings)}")
    print(f"Technologies: {len(result.technology_stack)}")
    print(f"\nReport saved: {report_file}")
    
    return result


if __name__ == "__main__":
    asyncio.run(demo_deep_crawl())