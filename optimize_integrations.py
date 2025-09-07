#!/usr/bin/env python3
"""
Optimize and verify active integrations in the AI Swarm System
"""

import json
from pathlib import Path
from datetime import datetime

def analyze_integrations():
    """Analyze current integration status and provide optimization recommendations"""
    
    # Load swarm status
    status_file = Path("C:/Users/scarm/src/ai_platform/swarm_status.json")
    if not status_file.exists():
        print("[ERROR] Swarm status file not found")
        return
    
    with open(status_file, 'r') as f:
        status = json.load(f)
    
    # Analyze integrations
    total_integrations = 0
    active_integrations = 0
    inactive_integrations = []
    low_health = []
    optimization_candidates = []
    
    for int_id, integration in status['integrations'].items():
        total_integrations += 1
        
        if integration['active']:
            active_integrations += 1
            
            # Check health
            if integration['health_score'] < 0.85:
                low_health.append({
                    'id': int_id,
                    'name': integration['name'],
                    'health': integration['health_score']
                })
            
            # Check for optimization candidates (good health but could be better utilized)
            if 0.85 <= integration['health_score'] < 0.95:
                optimization_candidates.append({
                    'id': int_id,
                    'name': integration['name'],
                    'health': integration['health_score'],
                    'capabilities': integration['capabilities']
                })
        else:
            inactive_integrations.append({
                'id': int_id,
                'name': integration['name']
            })
    
    # Generate report
    print("\n" + "="*80)
    print("AI SWARM INTEGRATION OPTIMIZATION REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(f"OVERVIEW:")
    print(f"  Total Integrations: {total_integrations}")
    print(f"  Active: {active_integrations}")
    print(f"  Inactive: {len(inactive_integrations)}")
    overall_health = status.get('metrics', {}).get('overall_health', 
                            status.get('overall_health', 0))
    print(f"  Overall Health: {overall_health:.1f}%")
    print()
    
    if low_health:
        print(f"LOW HEALTH INTEGRATIONS (< 85%):")
        for item in sorted(low_health, key=lambda x: x['health']):
            print(f"  [{item['id']}] {item['name']}: {item['health']*100:.1f}%")
        print()
    
    if optimization_candidates:
        print(f"OPTIMIZATION CANDIDATES (85-95% health):")
        for item in sorted(optimization_candidates, key=lambda x: x['health'], reverse=True):
            print(f"  [{item['id']}] {item['name']}: {item['health']*100:.1f}%")
            print(f"    Capabilities: {', '.join(item['capabilities'][:3])}")
        print()
    
    # Recommendations
    print("OPTIMIZATION RECOMMENDATIONS:")
    print()
    
    if active_integrations < total_integrations * 0.5:
        print("1. ACTIVATION OPPORTUNITY:")
        print(f"   Only {active_integrations}/{total_integrations} integrations are active.")
        print("   Consider activating more integrations for better coverage:")
        for item in inactive_integrations[:5]:  # Show top 5
            print(f"   - {item['name']}")
        print()
    
    if low_health:
        print("2. HEALTH IMPROVEMENTS NEEDED:")
        print("   The following integrations need immediate attention:")
        for item in low_health[:3]:  # Top 3 worst
            print(f"   - {item['name']}: Consider restarting or reconfiguring")
        print()
    
    comm_latency = status.get('metrics', {}).get('communication_latency', 0)
    if comm_latency > 20:
        print("3. COMMUNICATION OPTIMIZATION:")
        print(f"   Current latency: {comm_latency:.1f}ms")
        print("   Consider:")
        print("   - Reducing message queue size")
        print("   - Optimizing network paths")
        print("   - Implementing message batching")
        print()
    
    resource_util = status.get('metrics', {}).get('resource_utilization', 0)
    if resource_util > 80:
        print("4. RESOURCE OPTIMIZATION:")
        print(f"   Current utilization: {resource_util:.1f}%")
        print("   Consider:")
        print("   - Scaling down non-critical integrations")
        print("   - Implementing resource pooling")
        print("   - Adding load balancing")
        print()
    
    print("QUICK ACTIONS:")
    print("  1. Run: python master_ai_swarm_intelligence.py --optimize")
    print("  2. Run: python master_ai_swarm_intelligence.py --health-check")
    print("  3. Run: python fast_swarm_launcher.py --turbo  (for speed mode)")
    print()
    
    # Save optimization report
    report_path = Path("C:/Users/scarm/src/ai_platform/optimization_report.json")
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_integrations': total_integrations,
        'active_integrations': active_integrations,
        'low_health': low_health,
        'optimization_candidates': optimization_candidates,
        'inactive': inactive_integrations,
        'metrics': status.get('metrics', {})
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"[OK] Full report saved to: {report_path}")
    print("="*80)

if __name__ == "__main__":
    analyze_integrations()