#!/usr/bin/env python3
"""
API Key Scanner Demo - Safe demonstration of scanning capabilities
"""

import asyncio
import json
from datetime import datetime
from web_api_scanner import WebAPIKeyScanner, WebTarget

def run_api_key_scanner_demo():
    """Run a demonstration of the API key scanner"""
    print("\n" + "="*70)
    print("API KEY SCANNER DEMONSTRATION")
    print("="*70)
    print("\n[!] This is a demonstration using example/test URLs")
    print("[!] For educational purposes only - scan only authorized targets\n")
    
    # Initialize scanner
    scanner = WebAPIKeyScanner()
    
    # Demo targets (safe examples)
    demo_targets = [
        # GitHub's public API (safe to scan)
        WebTarget(
            url="https://api.github.com",
            domain="api.github.com",
            depth=1,  # Shallow scan
            max_pages=5,  # Limit pages
            scan_js=False,  # Skip JS for demo
            scan_css=False  # Skip CSS for demo
        ),
        # JSONPlaceholder - Free fake API for testing
        WebTarget(
            url="https://jsonplaceholder.typicode.com",
            domain="jsonplaceholder.typicode.com",
            depth=1,
            max_pages=3
        )
    ]
    
    print(f"Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Targets: {len(demo_targets)}\n")
    
    all_results = []
    
    for i, target in enumerate(demo_targets, 1):
        print(f"\n[{i}/{len(demo_targets)}] Scanning: {target.url}")
        print("-" * 50)
        
        try:
            # Scan the target
            result = scanner.scan_target(target)
            
            # Display results
            print(f"  Pages scanned: {result.pages_scanned}")
            print(f"  URLs discovered: {len(result.urls_discovered)}")
            print(f"  Scan duration: {result.scan_duration:.2f}s")
            
            if result.findings:
                print(f"  [!] Findings: {len(result.findings)}")
                for finding in result.findings[:3]:  # Show first 3
                    print(f"      - Type: {finding.get('pattern_type', 'unknown')}")
                    print(f"        Confidence: {finding.get('confidence', 0):.2%}")
                    print(f"        Risk: {finding.get('risk_level', 'unknown')}")
            else:
                print("  [+] No API keys or secrets found (good!)")
            
            if result.errors:
                print(f"  [!] Errors encountered: {len(result.errors)}")
            
            # Store results
            all_results.append({
                "target": target.url,
                "pages_scanned": result.pages_scanned,
                "findings": len(result.findings),
                "duration": result.scan_duration
            })
            
        except Exception as e:
            print(f"  [ERROR] Scan failed: {str(e)}")
            all_results.append({
                "target": target.url,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*70)
    print("SCAN SUMMARY")
    print("="*70)
    
    total_findings = sum(r.get('findings', 0) for r in all_results)
    total_pages = sum(r.get('pages_scanned', 0) for r in all_results)
    total_time = sum(r.get('duration', 0) for r in all_results)
    
    print(f"\nTotal targets scanned: {len(demo_targets)}")
    print(f"Total pages analyzed: {total_pages}")
    print(f"Total findings: {total_findings}")
    print(f"Total scan time: {total_time:.2f}s")
    
    # Save report
    report_file = f"api_scan_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = {
        "scan_date": datetime.now().isoformat(),
        "targets": len(demo_targets),
        "total_findings": total_findings,
        "total_pages": total_pages,
        "total_duration": total_time,
        "results": all_results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[+] Report saved to: {report_file}")
    
    # Security recommendations
    print("\n" + "="*70)
    print("SECURITY RECOMMENDATIONS")
    print("="*70)
    print("\n1. Never commit API keys to public repositories")
    print("2. Use environment variables for sensitive data")
    print("3. Rotate API keys regularly")
    print("4. Implement proper access controls")
    print("5. Monitor for exposed credentials continuously")
    
    return report


if __name__ == "__main__":
    # Run the demo
    report = run_api_key_scanner_demo()
    
    print("\n[+] API Key Scanner demonstration complete!")
    print("[!] Remember: Only scan targets you have permission to test")