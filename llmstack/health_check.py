#!/usr/bin/env python3
"""
Health check script for llmstack project
Verifies all modules are properly configured and accessible
Enhanced with AI agent service health checks
"""

import sys
import importlib
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def check_module(module_name: str) -> Tuple[bool, str]:
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True, "OK"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_file_structure() -> Dict[str, bool]:
    """Check if all expected directories and files exist"""
    base_path = Path(__file__).parent
    
    structure = {
        'src': base_path / 'src',
        'src/core': base_path / 'src' / 'core',
        'src/security': base_path / 'src' / 'security',
        'src/dolphin': base_path / 'src' / 'dolphin',
        'src/automation': base_path / 'src' / 'automation',
        'src/database': base_path / 'src' / 'database',
        'src/monitoring': base_path / 'src' / 'monitoring',
        'src/integrations': base_path / 'src' / 'integrations',
        'src/tests': base_path / 'src' / 'tests',
        'src/utils': base_path / 'src' / 'utils',
        'docs': base_path / 'docs',
        'config': base_path / 'config',
        'scripts': base_path / 'scripts',
        'main.py': base_path / 'main.py',
        'requirements.txt': base_path / 'requirements.txt',
        '.gitignore': base_path / '.gitignore',
    }
    
    results = {}
    for name, path in structure.items():
        results[name] = path.exists()
    
    return results


def count_modules() -> Dict[str, int]:
    """Count Python files in each module"""
    base_path = Path(__file__).parent / 'src'
    modules = ['core', 'security', 'dolphin', 'automation', 
               'database', 'monitoring', 'integrations', 'utils']
    
    counts = {}
    for module in modules:
        module_path = base_path / module
        if module_path.exists():
            py_files = list(module_path.glob('*.py'))
            counts[module] = len([f for f in py_files if f.name != '__init__.py'])
        else:
            counts[module] = 0
    
    return counts


def check_ai_services() -> Dict[str, Dict[str, str]]:
    """Check AI agent services health"""
    services = {
        'ollama': {
            'url': 'http://localhost:11434/api/tags',
            'name': 'Ollama Local AI',
            'timeout': 5
        },
        'llmstack': {
            'url': 'http://localhost:3000/api/health',
            'name': 'LLMStack UI',
            'timeout': 10
        },
        'flowise': {
            'url': 'http://localhost:3001/api/v1/chatflows',
            'name': 'Flowise AI Workflows',
            'timeout': 10
        },
        'openhands': {
            'url': 'http://localhost:3002/health',
            'name': 'OpenHands Coding Assistant',
            'timeout': 10
        }
    }
    
    results = {}
    for service_id, config in services.items():
        try:
            response = requests.get(
                config['url'], 
                timeout=config['timeout'],
                headers={'User-Agent': 'LLMStack-HealthCheck/1.0'}
            )
            if response.status_code == 200:
                results[service_id] = {
                    'status': 'OK',
                    'message': f"HTTP {response.status_code}",
                    'name': config['name']
                }
            else:
                results[service_id] = {
                    'status': 'ERROR',
                    'message': f"HTTP {response.status_code}",
                    'name': config['name']
                }
        except requests.exceptions.ConnectTimeout:
            results[service_id] = {
                'status': 'TIMEOUT',
                'message': f"Timeout after {config['timeout']}s",
                'name': config['name']
            }
        except requests.exceptions.ConnectionError:
            results[service_id] = {
                'status': 'OFFLINE',
                'message': 'Connection refused',
                'name': config['name']
            }
        except Exception as e:
            results[service_id] = {
                'status': 'ERROR',
                'message': str(e)[:50],
                'name': config['name']
            }
    
    return results


    """Check if key dependencies are installed"""
def check_dependencies() -> Dict[str, bool]:
    """Check if key dependencies are installed"""
    dependencies = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'numpy',
        'requests',
        'python-dotenv',
    ]
    
    results = {}
    for dep in dependencies:
        try:
            if dep == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(dep)
            results[dep] = True
        except ImportError:
            results[dep] = False
    
    return results


def main():
    """Run all health checks"""
    print("=" * 60)
    print("LLMSTACK PROJECT HEALTH CHECK")
    print("=" * 60)
    
    # Check file structure
    print("\n[FILE STRUCTURE CHECK]")
    structure = check_file_structure()
    for name, exists in structure.items():
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {name}")
    
    # Count modules
    print("\n[MODULE STATISTICS]")
    counts = count_modules()
    total = sum(counts.values())
    for module, count in counts.items():
        print(f"  {module:15} : {count:3} files")
    print(f"  {'TOTAL':15} : {total:3} files")
    
    # Check module imports
    print("\n[MODULE IMPORT CHECK]")
    modules_to_check = [
        'core',
        'security',
        'dolphin',
        'automation',
        'database',
        'monitoring',
        'integrations',
        'utils',
    ]
    
    import_results = {}
    for module in modules_to_check:
        success, message = check_module(module)
        import_results[module] = success
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {module:15} : {message}")
    
    # Check dependencies
    print("\n[DEPENDENCY CHECK]")
    deps = check_dependencies()
    for dep, installed in deps.items():
        status = "[INSTALLED]" if installed else "[MISSING]"
        print(f"  {status} {dep}")
    
    # Check AI services
    print("\n[AI SERVICES HEALTH CHECK]")
    ai_services = check_ai_services()
    for service_id, result in ai_services.items():
        status_map = {
            'OK': '[ONLINE]',
            'OFFLINE': '[OFFLINE]',
            'TIMEOUT': '[TIMEOUT]',
            'ERROR': '[ERROR]'
        }
        status = status_map.get(result['status'], '[UNKNOWN]')
        print(f"  {status} {result['name']:25} : {result['message']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    structure_ok = all(structure.values())
    imports_ok = all(import_results.values())
    deps_installed = sum(deps.values())
    deps_total = len(deps)
    ai_services_ok = sum(1 for r in ai_services.values() if r['status'] == 'OK')
    ai_services_total = len(ai_services)
    
    print(f"  File Structure : {'Complete' if structure_ok else 'Incomplete'}")
    print(f"  Module Imports : {'All OK' if imports_ok else 'Some failures'}")
    print(f"  Dependencies   : {deps_installed}/{deps_total} installed")
    print(f"  AI Services    : {ai_services_ok}/{ai_services_total} online")
    print(f"  Total Modules  : {total} Python files")
    
    # Overall status
    if structure_ok and imports_ok and deps_installed > 0:
        if ai_services_ok >= 1:
            print("\n[PROJECT STATUS: HEALTHY WITH AI SERVICES]")
        else:
            print("\n[PROJECT STATUS: HEALTHY (AI services offline)]")
        return 0
    elif structure_ok and total > 50:
        print("\n[PROJECT STATUS: FUNCTIONAL (some components missing)]")
        return 0
    else:
        print("\n[PROJECT STATUS: NEEDS ATTENTION]")
        return 1


if __name__ == '__main__':
    sys.exit(main())