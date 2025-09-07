#!/usr/bin/env python3
"""
Simple Security Demo - Basic security testing without complex dependencies
"""

import requests
import socket
import ssl
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
import json

class SimpleSecurityScanner:
    """Simple security scanner for basic assessments"""
    
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scan_target(self, target_url: str) -> Dict:
        """Perform basic security scan of target"""
        self.results = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        print(f"🔍 Scanning target: {target_url}")
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(target_url)
            if not parsed.scheme:
                target_url = "https://" + target_url
                parsed = urllib.parse.urlparse(target_url)
        except Exception as e:
            self.results["error"] = f"Invalid URL: {e}"
            return self.results
        
        # Basic connectivity test
        self.test_connectivity(target_url)
        
        # SSL/TLS test
        if parsed.scheme == "https":
            self.test_ssl_tls(parsed.hostname, parsed.port or 443)
        
        # HTTP headers analysis
        self.test_security_headers(target_url)
        
        # Basic endpoint testing
        self.test_common_endpoints(target_url)
        
        return self.results
    
    def test_connectivity(self, url: str):
        """Test basic connectivity to target"""
        print("  📡 Testing connectivity...")
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            self.results["tests"]["connectivity"] = {
                "status": "success",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "final_url": response.url
            }
            print(f"     ✅ Connected (HTTP {response.status_code})")
        except Exception as e:
            self.results["tests"]["connectivity"] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"     ❌ Connection failed: {e}")
    
    def test_ssl_tls(self, hostname: str, port: int):
        """Test SSL/TLS configuration"""
        print("  🔒 Testing SSL/TLS...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    self.results["tests"]["ssl_tls"] = {
                        "status": "success",
                        "version": version,
                        "cipher": cipher[0] if cipher else None,
                        "cert_subject": dict(x[0] for x in cert.get('subject', [])),
                        "cert_issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "not_after": cert.get('notAfter')
                    }
                    print(f"     ✅ SSL/TLS {version} - {cipher[0] if cipher else 'Unknown'}")
        except Exception as e:
            self.results["tests"]["ssl_tls"] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"     ❌ SSL/TLS test failed: {e}")
    
    def test_security_headers(self, url: str):
        """Test for security headers"""
        print("  🛡️  Testing security headers...")
        try:
            response = self.session.get(url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                'Content-Security-Policy': headers.get('Content-Security-Policy'),
                'X-Frame-Options': headers.get('X-Frame-Options'),
                'X-XSS-Protection': headers.get('X-XSS-Protection'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                'Referrer-Policy': headers.get('Referrer-Policy'),
                'Permissions-Policy': headers.get('Permissions-Policy')
            }
            
            present_headers = {k: v for k, v in security_headers.items() if v}
            missing_headers = [k for k, v in security_headers.items() if not v]
            
            self.results["tests"]["security_headers"] = {
                "status": "success",
                "present": present_headers,
                "missing": missing_headers,
                "score": len(present_headers) / len(security_headers) * 100
            }
            
            print(f"     ✅ Found {len(present_headers)}/{len(security_headers)} security headers")
            if missing_headers:
                print(f"     ⚠️  Missing: {', '.join(missing_headers[:3])}{'...' if len(missing_headers) > 3 else ''}")
                
        except Exception as e:
            self.results["tests"]["security_headers"] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"     ❌ Security headers test failed: {e}")
    
    def test_common_endpoints(self, base_url: str):
        """Test common endpoints that might be exposed"""
        print("  🔍 Testing common endpoints...")
        
        common_paths = [
            '/robots.txt',
            '/.well-known/security.txt',
            '/sitemap.xml',
            '/admin',
            '/login',
            '/api',
            '/.git',
            '/.env'
        ]
        
        found_endpoints = []
        
        for path in common_paths:
            try:
                url = base_url.rstrip('/') + path
                response = self.session.get(url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    found_endpoints.append({
                        "path": path,
                        "status_code": response.status_code,
                        "content_type": response.headers.get('Content-Type', 'Unknown'),
                        "content_length": len(response.content)
                    })
                    print(f"     ✅ Found: {path} (HTTP {response.status_code})")
                
            except Exception:
                continue  # Skip failed requests
        
        self.results["tests"]["common_endpoints"] = {
            "status": "success",
            "found": found_endpoints,
            "tested": len(common_paths),
            "discovered": len(found_endpoints)
        }
        
        if not found_endpoints:
            print("     ℹ️  No common endpoints discovered")
    
    def generate_report(self) -> str:
        """Generate a formatted security report"""
        if not self.results:
            return "No scan results available"
        
        report = []
        report.append("="*60)
        report.append("🔒 SECURITY SCAN REPORT")
        report.append("="*60)
        report.append(f"Target: {self.results.get('target', 'Unknown')}")
        report.append(f"Scan Time: {self.results.get('timestamp', 'Unknown')}")
        report.append("")
        
        for test_name, test_result in self.results.get("tests", {}).items():
            report.append(f"🔹 {test_name.replace('_', ' ').title()}")
            report.append("-" * 30)
            
            if test_result.get("status") == "success":
                if test_name == "security_headers":
                    score = test_result.get("score", 0)
                    report.append(f"   Score: {score:.1f}%")
                    if test_result.get("missing"):
                        report.append(f"   Missing: {', '.join(test_result['missing'][:3])}")
                
                elif test_name == "ssl_tls":
                    report.append(f"   Version: {test_result.get('version', 'Unknown')}")
                    report.append(f"   Cipher: {test_result.get('cipher', 'Unknown')}")
                
                elif test_name == "common_endpoints":
                    found = test_result.get("discovered", 0)
                    tested = test_result.get("tested", 0)
                    report.append(f"   Discovered: {found}/{tested} endpoints")
                
                elif test_name == "connectivity":
                    report.append(f"   Status: HTTP {test_result.get('status_code', 'Unknown')}")
                    report.append(f"   Response Time: {test_result.get('response_time', 0):.3f}s")
            else:
                report.append(f"   ❌ Failed: {test_result.get('error', 'Unknown error')}")
            
            report.append("")
        
        report.append("="*60)
        return "\n".join(report)


def main():
    """Main function for security scanning"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python simple_security_demo.py <target_url>")
        print("Example: python simple_security_demo.py https://example.com")
        sys.exit(1)
    
    target = sys.argv[1]
    scanner = SimpleSecurityScanner()
    
    print("🚀 Starting Simple Security Scanner...")
    print("="*50)
    
    results = scanner.scan_target(target)
    
    print("\n" + "="*50)
    print("📊 SCAN COMPLETE")
    print("="*50)
    
    # Generate and display report
    report = scanner.generate_report()
    print(report)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"security_scan_{timestamp}.json"
    
    try:
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")

if __name__ == "__main__":
    main()