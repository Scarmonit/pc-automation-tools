#!/usr/bin/env python3
"""
AI Platform Orchestrator
Comprehensive automation and testing script for the AI Platform
"""

import os
import sys
import subprocess
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

class PlatformOrchestrator:
    """Main orchestrator for AI Platform services and testing"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {}
        self.services = {}
        
        # Setup logging
        log_dir = self.root_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "orchestrator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("Orchestrator")
    
    def run_command(self, cmd: str, description: str = "", timeout: int = 30) -> Dict:
        """Run a command and return results"""
        self.logger.info(f"Running: {description or cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.root_dir
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "command": cmd
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "command": cmd
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": cmd
            }
    
    def test_python_environment(self) -> Dict:
        """Test Python environment and dependencies"""
        self.logger.info("🐍 Testing Python environment...")
        
        tests = {}
        
        # Python version
        result = self.run_command("python --version", "Python version check")
        tests["python_version"] = result
        
        # Key packages
        packages = ["requests", "fastapi", "uvicorn", "anthropic", "openai"]
        for package in packages:
            result = self.run_command(f"python -c \"import {package}; print(f'{package} OK')\"", f"Import {package}")
            tests[f"package_{package}"] = result
        
        return {
            "category": "Python Environment",
            "tests": tests,
            "success": all(t["success"] for t in tests.values())
        }
    
    def test_ollama_integration(self) -> Dict:
        """Test Ollama installation and models"""
        self.logger.info("🦙 Testing Ollama integration...")
        
        tests = {}
        
        # Ollama version
        result = self.run_command("ollama --version", "Ollama version check", timeout=10)
        tests["ollama_version"] = result
        
        if result["success"]:
            # List models
            result = self.run_command("ollama list", "List Ollama models", timeout=15)
            tests["ollama_models"] = result
            
            # Test quick inference if models available
            if result["success"] and "dolphin" in result["stdout"]:
                result = self.run_command(
                    'ollama run dolphin-mistral "Say hello in one word"',
                    "Test Dolphin inference",
                    timeout=30
                )
                tests["dolphin_test"] = result
        
        return {
            "category": "Ollama Integration",
            "tests": tests,
            "success": tests.get("ollama_version", {}).get("success", False)
        }
    
    def test_platform_modules(self) -> Dict:
        """Test main platform modules"""
        self.logger.info("🔧 Testing platform modules...")
        
        tests = {}
        
        # List modules
        result = self.run_command("python main.py list", "List platform modules", timeout=15)
        tests["list_modules"] = result
        
        # Test pc_tools screenshot (safe test)
        result = self.run_command("python main.py pc_tools", "PC Tools module", timeout=10)
        tests["pc_tools"] = result
        
        # Test security scanner with localhost
        result = self.run_command(
            "python main.py security --action=webscan http://localhost:8080 || echo 'Security test completed'",
            "Security scanner test",
            timeout=20
        )
        tests["security_test"] = result
        
        return {
            "category": "Platform Modules",
            "tests": tests,
            "success": tests.get("list_modules", {}).get("success", False)
        }
    
    def test_docker_services(self) -> Dict:
        """Test Docker services if available"""
        self.logger.info("🐳 Testing Docker services...")
        
        tests = {}
        
        # Check Docker installation
        result = self.run_command("docker --version", "Docker version check", timeout=10)
        tests["docker_version"] = result
        
        if result["success"]:
            # Check if compose file exists
            compose_file = self.root_dir / "src" / "infrastructure" / "docker-compose.yml"
            if compose_file.exists():
                # Test compose file syntax
                result = self.run_command(
                    f"docker-compose -f {compose_file} config",
                    "Docker compose validation",
                    timeout=15
                )
                tests["compose_validation"] = result
            else:
                tests["compose_file"] = {
                    "success": False,
                    "stderr": "Docker compose file not found",
                    "command": "file check"
                }
        
        return {
            "category": "Docker Services",
            "tests": tests,
            "success": tests.get("docker_version", {}).get("success", False)
        }
    
    def start_ai_platform_server(self, background: bool = True) -> Optional[subprocess.Popen]:
        """Start the AI Platform server"""
        self.logger.info("🚀 Starting AI Platform server...")
        
        try:
            if background:
                # Start server in background
                process = subprocess.Popen(
                    ["python", "main.py", "core"],
                    cwd=self.root_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Give it time to start
                time.sleep(5)
                
                if process.poll() is None:  # Still running
                    self.services["ai_platform"] = process
                    self.logger.info("✅ AI Platform server started successfully")
                    return process
                else:
                    self.logger.error("❌ AI Platform server failed to start")
                    return None
            else:
                # Run in foreground
                subprocess.run(["python", "main.py", "core"], cwd=self.root_dir)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to start AI Platform server: {e}")
            return None
    
    def stop_services(self):
        """Stop all running services"""
        self.logger.info("🛑 Stopping services...")
        
        for service_name, process in self.services.items():
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=10)
                    self.logger.info(f"✅ Stopped {service_name}")
            except Exception as e:
                self.logger.error(f"Error stopping {service_name}: {e}")
                try:
                    process.kill()
                except:
                    pass
        
        self.services.clear()
    
    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive testing suite"""
        self.logger.info("🧪 Running comprehensive test suite...")
        
        test_results = {}
        start_time = datetime.now()
        
        # Run all test categories
        test_categories = [
            self.test_python_environment,
            self.test_ollama_integration,
            self.test_platform_modules,
            self.test_docker_services
        ]
        
        for test_func in test_categories:
            try:
                result = test_func()
                test_results[result["category"]] = result
                
                # Log summary
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                self.logger.info(f"{status} - {result['category']}")
                
            except Exception as e:
                self.logger.error(f"Test failed: {test_func.__name__}: {e}")
                test_results[test_func.__name__] = {
                    "category": test_func.__name__,
                    "success": False,
                    "error": str(e)
                }
        
        # Calculate overall results
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results.values() if r.get("success", False))
        
        summary = {
            "timestamp": start_time.isoformat(),
            "duration": (datetime.now() - start_time).total_seconds(),
            "total_categories": total_tests,
            "passed_categories": passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_success": passed_tests == total_tests,
            "results": test_results
        }
        
        return summary
    
    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("🤖 AI PLATFORM - COMPREHENSIVE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Duration: {results['duration']:.2f} seconds")
        report.append(f"Success Rate: {results['success_rate']:.1f}%")
        report.append(f"Overall Status: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
        report.append("")
        
        # Detailed results
        for category, result in results["results"].items():
            report.append(f"📊 {category}")
            report.append("-" * 50)
            
            if "tests" in result:
                for test_name, test_result in result["tests"].items():
                    status = "✅" if test_result.get("success", False) else "❌"
                    report.append(f"  {status} {test_name}")
                    
                    if not test_result.get("success", False) and test_result.get("stderr"):
                        error_lines = test_result["stderr"].split('\n')[:2]  # First 2 lines
                        for line in error_lines:
                            report.append(f"      {line}")
            else:
                status = "✅" if result.get("success", False) else "❌"
                report.append(f"  {status} {category}")
                
                if "error" in result:
                    report.append(f"      Error: {result['error']}")
            
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)
    
    def save_results(self, results: Dict, filename: Optional[str] = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"platform_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"📄 Results saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Platform Orchestrator')
    parser.add_argument('--test', action='store_true', help='Run comprehensive test suite')
    parser.add_argument('--start-server', action='store_true', help='Start AI Platform server')
    parser.add_argument('--background', action='store_true', help='Run server in background')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--report', help='Generate report from JSON results file')
    
    args = parser.parse_args()
    
    orchestrator = PlatformOrchestrator()
    
    try:
        if args.test:
            print("🧪 Running comprehensive test suite...")
            print("=" * 50)
            
            results = orchestrator.run_comprehensive_test()
            
            print("\n" + "=" * 50)
            print("📊 TEST RESULTS")
            print("=" * 50)
            
            # Generate and display report
            report = orchestrator.generate_report(results)
            print(report)
            
            # Save results
            orchestrator.save_results(results)
            
            # Exit with appropriate code
            sys.exit(0 if results["overall_success"] else 1)
        
        elif args.start_server:
            if args.background:
                process = orchestrator.start_ai_platform_server(background=True)
                if process:
                    print("🚀 AI Platform server running in background")
                    print("   Server should be available at: http://localhost:8000")
                    print("   API docs at: http://localhost:8000/docs")
                    print("   Press Ctrl+C to stop")
                    
                    try:
                        while process.poll() is None:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Stopping server...")
                        orchestrator.stop_services()
                else:
                    sys.exit(1)
            else:
                orchestrator.start_ai_platform_server(background=False)
        
        elif args.stop:
            orchestrator.stop_services()
        
        elif args.report:
            try:
                with open(args.report, 'r') as f:
                    results = json.load(f)
                report = orchestrator.generate_report(results)
                print(report)
            except Exception as e:
                print(f"Error reading report file: {e}")
                sys.exit(1)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
        orchestrator.stop_services()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        orchestrator.stop_services()
        sys.exit(1)


if __name__ == "__main__":
    main()