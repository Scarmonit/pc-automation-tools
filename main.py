#!/usr/bin/env python3
"""
Unified AI Platform - Main Entry Point
Consolidates all AI platform functionality into a single interface
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def main():
    parser = argparse.ArgumentParser(
        description='Unified AI Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available modules:
  core        - Main AI platform functionality
  security    - Security scanning and analysis tools
  dolphin     - Dolphin model management
  automation  - Swarm and automation tools
  database    - Database management
  monitoring  - Health monitoring and alerts
  integrations- Various service integrations
  pc_tools    - PC automation and screenshot tools
        """
    )
    
    parser.add_argument('module', 
                       choices=['core', 'security', 'dolphin', 'automation', 
                               'database', 'monitoring', 'integrations', 'pc_tools', 'list'],
                       help='Module to run')
    
    parser.add_argument('--action', help='Specific action within module')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.module == 'list':
        list_available_modules()
        return
    
    if args.module == 'core':
        from core import ai_platform
        ai_platform.main()
    
    elif args.module == 'security':
        print("Security Module Options:")
        print("  - Web Scanner")
        print("  - API Scanner")
        print("  - Deep Crawl Engine")
        print("  - Stealth Scanner")
        if args.action == 'webscan':
            from security import ultimate_security_scanner
            ultimate_security_scanner.main()
        elif args.action == 'apiscan':
            from security import web_api_scanner
            web_api_scanner.main()
    
    elif args.module == 'dolphin':
        print("Dolphin Module Options:")
        print("  - Setup Dolphin")
        print("  - Enhance Model")
        print("  - Launch GUI")
        if args.action == 'setup':
            from dolphin import setup_ollama_dolphin
            setup_ollama_dolphin.main()
        elif args.action == 'gui':
            from dolphin import dolphin_gui
            dolphin_gui.main()
    
    elif args.module == 'automation':
        print("Automation Module Options:")
        print("  - Swarm Intelligence")
        print("  - AutoGPT Integration")
        print("  - Distributed Agents")
        if args.action == 'swarm':
            from automation import master_ai_swarm_intelligence
            master_ai_swarm_intelligence.main()
    
    elif args.module == 'database':
        from database import unified_database_system
        unified_database_system.main()
    
    elif args.module == 'monitoring':
        from monitoring import health_monitor
        health_monitor.main()
    
    elif args.module == 'integrations':
        print("Available Integrations:")
        list_integrations()
    
    elif args.module == 'pc_tools':
        print("PC Tools Options:")
        print("  - Screenshot capture")
        print("  - System automation")
        print("  - RunPod management")
        if args.action == 'screenshot':
            from pc_tools import screenshot
            screenshot.main()
        else:
            print("\nUsage: python main.py pc_tools --action screenshot")


def list_available_modules():
    """List all available modules and their components"""
    modules = {
        'Core': Path('src/core').glob('*.py'),
        'Security': Path('src/security').glob('*.py'),
        'Dolphin': Path('src/dolphin').glob('*.py'),
        'Automation': Path('src/automation').glob('*.py'),
        'Database': Path('src/database').glob('*.py'),
        'Monitoring': Path('src/monitoring').glob('*.py'),
        'Integrations': Path('src/integrations').glob('*.py'),
    }
    
    for category, files in modules.items():
        file_list = list(files)
        if file_list:
            print(f"\n{category}:")
            for f in file_list[:5]:  # Show first 5
                print(f"  - {f.stem}")
            if len(file_list) > 5:
                print(f"  ... and {len(file_list)-5} more")


def list_integrations():
    """List available integration modules"""
    integration_path = Path('src/integrations')
    if integration_path.exists():
        for f in integration_path.glob('integrate_*.py'):
            name = f.stem.replace('integrate_', '').replace('_', ' ').title()
            print(f"  - {name}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)