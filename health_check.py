#!/usr/bin/env python3
"""
AI Platform Health Check
Comprehensive system validation and testing
"""

import sys
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Tuple


class HealthChecker:
    """Comprehensive health checker for AI Platform"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def add_result(self, category: str, test_name: str, details: str = ""):
        """Add a test result"""
        self.results[category].append({
            'test': test_name,
            'details': details
        })
    
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.add_result('passed', 'Python Version', f"{version.major}.{version.minor}")
        else:
            self.add_result('failed', 'Python Version', f"Need 3.8+, got {version.major}.{version.minor}")
    
    def check_core_modules(self):
        """Check if core modules can be imported"""
        sys.path.insert(0, str(Path('src')))
        
        core_modules = [
            ('core.ai_platform', 'Core AI Platform'),
            ('pc_tools.screenshot', 'Screenshot Tool'),
            ('database.unified_database_system', 'Database System'),
            ('monitoring.health_monitor', 'Health Monitor')
        ]
        
        for module_path, display_name in core_modules:
            try:
                importlib.import_module(module_path)
                self.add_result('passed', f'Module: {display_name}', 'Import successful')
            except ImportError as e:
                self.add_result('failed', f'Module: {display_name}', f'Import failed: {e}')
            except Exception as e:
                self.add_result('warnings', f'Module: {display_name}', f'Import warning: {e}')
    
    def check_main_entry_point(self):
        """Test main.py entry point"""
        try:
            result = subprocess.run([
                sys.executable, 'main.py', 'list'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'Core:' in result.stdout:
                self.add_result('passed', 'Main Entry Point', 'CLI working')
            else:
                self.add_result('failed', 'Main Entry Point', f'CLI failed: {result.stderr}')
        except Exception as e:
            self.add_result('failed', 'Main Entry Point', f'Test failed: {e}')
    
    def check_dependencies(self):
        """Check critical dependencies"""
        critical_deps = [
            ('requests', 'HTTP requests'),
            ('pathlib', 'Path handling'),
            ('asyncio', 'Async operations'),
            ('json', 'JSON processing')
        ]
        
        optional_deps = [
            ('pyautogui', 'Screenshot capture'),
            ('PIL', 'Image processing'),
            ('fastapi', 'Web API'),
            ('uvicorn', 'ASGI server')
        ]
        
        for dep, description in critical_deps:
            try:
                importlib.import_module(dep)
                self.add_result('passed', f'Dependency: {description}', dep)
            except ImportError:
                self.add_result('failed', f'Dependency: {description}', f'{dep} missing')
        
        for dep, description in optional_deps:
            try:
                importlib.import_module(dep)
                self.add_result('passed', f'Optional: {description}', dep)
            except ImportError:
                self.add_result('warnings', f'Optional: {description}', f'{dep} not available')
    
    def check_file_structure(self):
        """Check critical file structure"""
        critical_files = [
            'main.py',
            'requirements.txt',
            'setup_new.py',
            'src/__init__.py',
            'src/core/__init__.py',
            'src/pc_tools/__init__.py'
        ]
        
        for file_path in critical_files:
            path = Path(file_path)
            if path.exists():
                self.add_result('passed', f'File: {file_path}', 'Exists')
            else:
                self.add_result('failed', f'File: {file_path}', 'Missing')
    
    def check_llmstack_integration(self):
        """Check LLMStack deployment system"""
        llmstack_files = [
            'llmstack/deploy.sh',
            'llmstack/docker/docker-compose.yml',
            'llmstack/scripts/check_system.sh',
            'llmstack/scripts/validate_deployment.sh'
        ]
        
        for file_path in llmstack_files:
            path = Path(file_path)
            if path.exists():
                self.add_result('passed', f'LLMStack: {path.name}', 'Available')
            else:
                self.add_result('warnings', f'LLMStack: {path.name}', 'Missing')
    
    def check_screenshot_functionality(self):
        """Test screenshot functionality"""
        try:
            from pc_tools.screenshot import ScreenshotManager
            manager = ScreenshotManager('temp_screenshots')
            
            # Test screenshot creation
            path = manager.take_screenshot('health_check_test.png')
            test_path = Path(path) if path else None
            
            if test_path and test_path.exists():
                # Clean up test file
                test_path.unlink()
                test_path.parent.rmdir() if test_path.parent.name == 'temp_screenshots' else None
                self.add_result('passed', 'Screenshot Function', 'Working')
            else:
                self.add_result('failed', 'Screenshot Function', 'Failed to create screenshot')
                
        except Exception as e:
            self.add_result('failed', 'Screenshot Function', f'Error: {e}')
    
    def check_git_repository(self):
        """Check Git repository status"""
        try:
            result = subprocess.run([
                'git', 'remote', '-v'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'pc-automation-tools' in result.stdout:
                self.add_result('passed', 'Git Repository', 'Connected to pc-automation-tools')
            else:
                self.add_result('warnings', 'Git Repository', 'Not connected or different repo')
        except Exception as e:
            self.add_result('warnings', 'Git Repository', f'Git check failed: {e}')
    
    def run_all_checks(self):
        """Run all health checks"""
        print("[INFO] Running AI Platform Health Check...")
        print("=" * 50)
        
        checks = [
            ('Python Version', self.check_python_version),
            ('File Structure', self.check_file_structure),
            ('Dependencies', self.check_dependencies),
            ('Core Modules', self.check_core_modules),
            ('Main Entry Point', self.check_main_entry_point),
            ('Screenshot Function', self.check_screenshot_functionality),
            ('LLMStack Integration', self.check_llmstack_integration),
            ('Git Repository', self.check_git_repository)
        ]
        
        for check_name, check_func in checks:
            print(f"\n[CHECK] {check_name}...")
            try:
                check_func()
            except Exception as e:
                self.add_result('failed', check_name, f'Check failed: {e}')
        
        self.print_summary()
    
    def print_summary(self):
        """Print health check summary"""
        print("\n" + "=" * 50)
        print("[SUMMARY] Health Check Summary")
        print("=" * 50)
        
        # Passed tests
        if self.results['passed']:
            print(f"\n[OK] PASSED ({len(self.results['passed'])} tests)")
            for result in self.results['passed']:
                details = f" - {result['details']}" if result['details'] else ""
                print(f"   [OK] {result['test']}{details}")
        
        # Warnings
        if self.results['warnings']:
            print(f"\n[WARNING] WARNINGS ({len(self.results['warnings'])} tests)")
            for result in self.results['warnings']:
                details = f" - {result['details']}" if result['details'] else ""
                print(f"   [WARN] {result['test']}{details}")
        
        # Failed tests
        if self.results['failed']:
            print(f"\n[ERROR] FAILED ({len(self.results['failed'])} tests)")
            for result in self.results['failed']:
                details = f" - {result['details']}" if result['details'] else ""
                print(f"   [FAIL] {result['test']}{details}")
        
        # Overall status
        total_critical = len(self.results['passed']) + len(self.results['failed'])
        success_rate = (len(self.results['passed']) / total_critical * 100) if total_critical > 0 else 0
        
        print(f"\n[STATUS] Overall Health: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("[EXCELLENT] System is in EXCELLENT health!")
        elif success_rate >= 75:
            print("[GOOD] System is in GOOD health")
        elif success_rate >= 50:
            print("[ATTENTION] System needs ATTENTION")
        else:
            print("[CRITICAL] System has CRITICAL issues")
        
        print("\n[NEXT STEPS] Next steps:")
        if self.results['failed']:
            print("   1. Address failed tests above")
        if self.results['warnings']:
            print("   2. Consider resolving warnings for full functionality")
        print("   3. Run 'python main.py list' to verify all modules")
        print("   4. Try 'python main.py pc_tools --action screenshot' to test tools")
        
        return len(self.results['failed']) == 0


def main():
    """Main health check execution"""
    try:
        checker = HealthChecker()
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Health check cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()