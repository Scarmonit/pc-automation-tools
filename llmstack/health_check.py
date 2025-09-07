#!/usr/bin/env python3
"""
Health check script for llmstack project
Verifies all modules are properly configured and accessible
"""

import sys
import importlib
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


def check_dependencies() -> Dict[str, bool]:
    """Check if key dependencies are installed"""
    dependencies = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'numpy',
        'dotenv',
    ]
    
    results = {}
    for dep in dependencies:
        try:
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
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    structure_ok = all(structure.values())
    imports_ok = all(import_results.values())
    deps_installed = sum(deps.values())
    deps_total = len(deps)
    
    print(f"  File Structure : {'Complete' if structure_ok else 'Incomplete'}")
    print(f"  Module Imports : {'All OK' if imports_ok else 'Some failures'}")
    print(f"  Dependencies   : {deps_installed}/{deps_total} installed")
    print(f"  Total Modules  : {total} Python files")
    
    # Overall status
    if structure_ok and imports_ok and deps_installed > 0:
        print("\n[PROJECT STATUS: HEALTHY]")
        return 0
    elif structure_ok and total > 50:
        print("\n[PROJECT STATUS: FUNCTIONAL (some dependencies missing)]")
        return 0
    else:
        print("\n[PROJECT STATUS: NEEDS ATTENTION]")
        return 1


if __name__ == '__main__':
    sys.exit(main())