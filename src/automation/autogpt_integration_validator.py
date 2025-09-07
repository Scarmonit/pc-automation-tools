#!/usr/bin/env python3
"""
AutoGPT Integration Validator
Pre-flight checks to ensure system readiness for AutoGPT integration
Prevents common errors and validates all prerequisites
"""

import asyncio
import socket
import subprocess
import psutil
import sqlite3
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import aiohttp
import docker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation check"""
    def __init__(self, name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'passed': self.passed,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class IntegrationValidator:
    """Comprehensive validator for AutoGPT-Swarm integration"""
    
    def __init__(self):
        self.results = []
        self.critical_ports = [3000, 8001, 8002, 8006]
        self.required_memory_gb = 8
        self.required_disk_gb = 20
        self.required_api_keys = [
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY'
        ]
        self.optional_api_keys = [
            'PERPLEXITY_API_KEY',
            'FIRECRAWL_API_KEY'
        ]
        self.swarm_paths = {
            'swarm_root': Path(r'C:\Users\scarm\.claude\swarm-intelligence'),
            'autogpt_dir': Path(r'C:\Users\scarm\.claude\swarm-intelligence\agents\autogpt'),
            'db_path': Path(r'C:\Users\scarm\.claude\swarm-intelligence\swarm_memory.db'),
            'config_path': Path(r'C:\Users\scarm\.claude\swarm-intelligence\swarm_config.json')
        }
        
    async def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation checks"""
        logger.info("Starting comprehensive integration validation...")
        
        # System checks
        await self.check_operating_system()
        await self.check_docker()
        await self.check_docker_compose()
        await self.check_python_version()
        
        # Resource checks
        await self.check_memory()
        await self.check_disk_space()
        await self.check_cpu()
        
        # Network checks
        await self.check_ports()
        await self.check_docker_network()
        await self.check_internet_connectivity()
        
        # Configuration checks
        await self.check_api_keys()
        await self.check_paths()
        await self.check_database()
        await self.check_config_files()
        
        # Service checks
        await self.check_existing_services()
        await self.check_container_conflicts()
        
        # Security checks
        await self.check_file_permissions()
        await self.check_firewall()
        
        # Calculate overall result
        all_passed = all(r.passed for r in self.results if r.name.startswith('critical_'))
        
        return all_passed, self.results
    
    async def check_operating_system(self) -> ValidationResult:
        """Check if OS is compatible"""
        try:
            import platform
            os_info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine()
            }
            
            is_windows = platform.system() == 'Windows'
            is_compatible = is_windows or platform.system() in ['Linux', 'Darwin']
            
            result = ValidationResult(
                'critical_os_check',
                is_compatible,
                f"Operating system: {platform.system()} {platform.release()}",
                os_info
            )
            
            if is_windows:
                # Check for WSL if on Windows
                try:
                    wsl_check = subprocess.run(['wsl', '--list'], capture_output=True, text=True)
                    has_wsl = wsl_check.returncode == 0
                    result.details['wsl_available'] = has_wsl
                except:
                    result.details['wsl_available'] = False
                    
        except Exception as e:
            result = ValidationResult(
                'critical_os_check',
                False,
                f"Failed to check OS: {str(e)}"
            )
        
        self.results.append(result)
        logger.info(f"OS Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_docker(self) -> ValidationResult:
        """Check if Docker is installed and running"""
        try:
            client = docker.from_env()
            info = client.info()
            
            result = ValidationResult(
                'critical_docker_check',
                True,
                f"Docker is running (version {info.get('ServerVersion', 'unknown')})",
                {
                    'version': info.get('ServerVersion'),
                    'containers': info.get('Containers', 0),
                    'images': info.get('Images', 0),
                    'memory': info.get('MemTotal', 0) / (1024**3) if info.get('MemTotal') else 0
                }
            )
            client.close()
            
        except docker.errors.DockerException as e:
            result = ValidationResult(
                'critical_docker_check',
                False,
                f"Docker not available: {str(e)}",
                {'error': str(e)}
            )
        except Exception as e:
            result = ValidationResult(
                'critical_docker_check',
                False,
                f"Docker check failed: {str(e)}"
            )
        
        self.results.append(result)
        logger.info(f"Docker Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_docker_compose(self) -> ValidationResult:
        """Check if Docker Compose is installed"""
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                validation_result = ValidationResult(
                    'critical_docker_compose_check',
                    True,
                    f"Docker Compose available: {version}",
                    {'version': version}
                )
            else:
                validation_result = ValidationResult(
                    'critical_docker_compose_check',
                    False,
                    "Docker Compose not found"
                )
                
        except FileNotFoundError:
            validation_result = ValidationResult(
                'critical_docker_compose_check',
                False,
                "Docker Compose not installed"
            )
        except Exception as e:
            validation_result = ValidationResult(
                'critical_docker_compose_check',
                False,
                f"Docker Compose check failed: {str(e)}"
            )
        
        self.results.append(validation_result)
        logger.info(f"Docker Compose Check: {'[OK]' if validation_result.passed else '[FAIL]'} {validation_result.message}")
        return validation_result
    
    async def check_python_version(self) -> ValidationResult:
        """Check Python version compatibility"""
        import sys
        
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        is_compatible = version_info.major == 3 and version_info.minor >= 8
        
        result = ValidationResult(
            'python_version_check',
            is_compatible,
            f"Python {version_str}",
            {
                'version': version_str,
                'executable': sys.executable,
                'compatible': is_compatible
            }
        )
        
        self.results.append(result)
        logger.info(f"Python Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_memory(self) -> ValidationResult:
        """Check available memory"""
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        total_gb = memory.total / (1024**3)
        
        has_enough = available_gb >= self.required_memory_gb
        
        result = ValidationResult(
            'critical_memory_check',
            has_enough,
            f"Memory: {available_gb:.1f}GB available of {total_gb:.1f}GB total",
            {
                'available_gb': available_gb,
                'total_gb': total_gb,
                'required_gb': self.required_memory_gb,
                'percent_used': memory.percent
            }
        )
        
        self.results.append(result)
        logger.info(f"Memory Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_disk_space(self) -> ValidationResult:
        """Check available disk space"""
        disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
        available_gb = disk.free / (1024**3)
        total_gb = disk.total / (1024**3)
        
        has_enough = available_gb >= self.required_disk_gb
        
        result = ValidationResult(
            'critical_disk_check',
            has_enough,
            f"Disk: {available_gb:.1f}GB available of {total_gb:.1f}GB total",
            {
                'available_gb': available_gb,
                'total_gb': total_gb,
                'required_gb': self.required_disk_gb,
                'percent_used': disk.percent
            }
        )
        
        self.results.append(result)
        logger.info(f"Disk Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_cpu(self) -> ValidationResult:
        """Check CPU resources"""
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        has_enough_cores = cpu_count >= 4  # Minimum 4 cores recommended
        
        result = ValidationResult(
            'cpu_check',
            has_enough_cores,
            f"CPU: {cpu_count} cores, {cpu_percent}% usage",
            {
                'cores': cpu_count,
                'usage_percent': cpu_percent,
                'recommended_cores': 4
            }
        )
        
        self.results.append(result)
        logger.info(f"CPU Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_ports(self) -> ValidationResult:
        """Check if required ports are available"""
        unavailable_ports = []
        port_status = {}
        
        for port in self.critical_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            is_available = result != 0
            port_status[port] = 'available' if is_available else 'in use'
            
            if not is_available:
                unavailable_ports.append(port)
        
        all_available = len(unavailable_ports) == 0
        
        result = ValidationResult(
            'critical_port_check',
            all_available,
            f"Ports: {', '.join(f'{p}' for p in unavailable_ports)} in use" if unavailable_ports else "All ports available",
            {
                'ports': port_status,
                'required': self.critical_ports,
                'unavailable': unavailable_ports
            }
        )
        
        self.results.append(result)
        logger.info(f"Port Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_docker_network(self) -> ValidationResult:
        """Check if Docker network exists"""
        try:
            client = docker.from_env()
            networks = client.networks.list()
            
            swarm_network = None
            for network in networks:
                if 'swarm-network' in network.name or 'swarm_network' in network.name:
                    swarm_network = network
                    break
            
            if swarm_network:
                result = ValidationResult(
                    'docker_network_check',
                    True,
                    f"Docker network '{swarm_network.name}' exists",
                    {
                        'network_name': swarm_network.name,
                        'driver': swarm_network.attrs.get('Driver', 'unknown')
                    }
                )
            else:
                result = ValidationResult(
                    'docker_network_check',
                    False,
                    "Swarm network not found",
                    {'available_networks': [n.name for n in networks]}
                )
            
            client.close()
            
        except Exception as e:
            result = ValidationResult(
                'docker_network_check',
                False,
                f"Failed to check Docker network: {str(e)}"
            )
        
        self.results.append(result)
        logger.info(f"Network Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_internet_connectivity(self) -> ValidationResult:
        """Check internet connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.github.com', timeout=5) as response:
                    is_connected = response.status == 200
                    
            result = ValidationResult(
                'internet_check',
                is_connected,
                "Internet connectivity available" if is_connected else "No internet connection",
                {'tested_endpoint': 'https://api.github.com'}
            )
            
        except Exception as e:
            result = ValidationResult(
                'internet_check',
                False,
                f"Internet check failed: {str(e)}"
            )
        
        self.results.append(result)
        logger.info(f"Internet Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_api_keys(self) -> ValidationResult:
        """Check if API keys are configured"""
        env_path = self.swarm_paths['swarm_root'] / '.env'
        
        found_keys = {}
        missing_required = []
        missing_optional = []
        
        # Check environment variables
        for key in self.required_api_keys:
            value = os.getenv(key)
            if value and value != 'your_api_key_here' and len(value) > 10:
                found_keys[key] = 'configured'
            else:
                missing_required.append(key)
                found_keys[key] = 'missing'
        
        for key in self.optional_api_keys:
            value = os.getenv(key)
            if value and value != 'your_api_key_here' and len(value) > 10:
                found_keys[key] = 'configured'
            else:
                missing_optional.append(key)
                found_keys[key] = 'optional_missing'
        
        # Check .env file if exists
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    env_content = f.read()
                    for key in self.required_api_keys + self.optional_api_keys:
                        if key in env_content:
                            line = [l for l in env_content.split('\n') if l.startswith(key)][0]
                            value = line.split('=', 1)[1].strip()
                            if value and value != 'your_api_key_here' and len(value) > 10:
                                found_keys[key] = 'configured'
            except Exception as e:
                logger.warning(f"Could not read .env file: {e}")
        
        all_required_present = len(missing_required) == 0
        
        result = ValidationResult(
            'critical_api_key_check',
            all_required_present,
            f"Missing required keys: {', '.join(missing_required)}" if missing_required else "All required API keys configured",
            {
                'keys': found_keys,
                'missing_required': missing_required,
                'missing_optional': missing_optional,
                'env_file': str(env_path) if env_path.exists() else None
            }
        )
        
        self.results.append(result)
        logger.info(f"API Key Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_paths(self) -> ValidationResult:
        """Check if required paths exist"""
        missing_paths = []
        path_status = {}
        
        for name, path in self.swarm_paths.items():
            exists = path.exists()
            path_status[name] = {
                'path': str(path),
                'exists': exists
            }
            
            if not exists and name in ['swarm_root', 'autogpt_dir']:
                missing_paths.append(name)
        
        all_exist = len(missing_paths) == 0
        
        result = ValidationResult(
            'critical_path_check',
            all_exist,
            f"Missing paths: {', '.join(missing_paths)}" if missing_paths else "All required paths exist",
            {
                'paths': path_status,
                'missing': missing_paths
            }
        )
        
        self.results.append(result)
        logger.info(f"Path Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_database(self) -> ValidationResult:
        """Check database accessibility and integrity"""
        db_path = self.swarm_paths['db_path']
        
        if not db_path.exists():
            # Database will be created, not a critical error
            result = ValidationResult(
                'database_check',
                True,
                "Database will be created on first run",
                {'path': str(db_path), 'exists': False}
            )
        else:
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Test write
                cursor.execute("CREATE TEMP TABLE test_write (id INTEGER)")
                cursor.execute("DROP TABLE test_write")
                
                conn.close()
                
                result = ValidationResult(
                    'database_check',
                    True,
                    f"Database accessible with {len(tables)} tables",
                    {
                        'path': str(db_path),
                        'tables': tables,
                        'size_mb': db_path.stat().st_size / (1024*1024) if db_path.exists() else 0
                    }
                )
                
            except Exception as e:
                result = ValidationResult(
                    'database_check',
                    False,
                    f"Database error: {str(e)}",
                    {'error': str(e)}
                )
        
        self.results.append(result)
        logger.info(f"Database Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_config_files(self) -> ValidationResult:
        """Check if configuration files are valid"""
        config_path = self.swarm_paths['config_path']
        
        if not config_path.exists():
            result = ValidationResult(
                'config_check',
                False,
                "Configuration file not found",
                {'path': str(config_path)}
            )
        else:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Check for AutoGPT configuration
                has_autogpt = 'autogpt' in config.get('agent_types', {})
                
                result = ValidationResult(
                    'config_check',
                    has_autogpt,
                    "AutoGPT configured" if has_autogpt else "AutoGPT not in configuration",
                    {
                        'path': str(config_path),
                        'has_autogpt': has_autogpt,
                        'agent_types': list(config.get('agent_types', {}).keys())
                    }
                )
                
            except json.JSONDecodeError as e:
                result = ValidationResult(
                    'config_check',
                    False,
                    f"Invalid JSON in config file: {str(e)}"
                )
            except Exception as e:
                result = ValidationResult(
                    'config_check',
                    False,
                    f"Config file error: {str(e)}"
                )
        
        self.results.append(result)
        logger.info(f"Config Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_existing_services(self) -> ValidationResult:
        """Check if existing services are running"""
        services = {}
        
        # Check common services
        service_urls = {
            'ai_platform': 'http://localhost:8000/health',
            'swarm_api': 'http://localhost:8001/health',
            'api_bridge': 'http://localhost:8002/health'
        }
        
        async with aiohttp.ClientSession() as session:
            for name, url in service_urls.items():
                try:
                    async with session.get(url, timeout=2) as response:
                        services[name] = {
                            'url': url,
                            'status': response.status,
                            'running': response.status == 200
                        }
                except:
                    services[name] = {
                        'url': url,
                        'status': None,
                        'running': False
                    }
        
        result = ValidationResult(
            'service_check',
            True,  # Not critical
            f"Services: {sum(1 for s in services.values() if s['running'])}/{len(services)} running",
            services
        )
        
        self.results.append(result)
        logger.info(f"Service Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_container_conflicts(self) -> ValidationResult:
        """Check for conflicting Docker containers"""
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            
            conflicting = []
            for container in containers:
                # Check for name conflicts
                if any(name in container.name for name in ['autogpt', 'swarm-autogpt']):
                    conflicting.append({
                        'name': container.name,
                        'status': container.status,
                        'id': container.short_id
                    })
                
                # Check for port conflicts
                if container.status == 'running':
                    for port in container.ports:
                        if port in ['3000/tcp', '8002/tcp']:
                            conflicting.append({
                                'name': container.name,
                                'port': port,
                                'status': container.status
                            })
            
            client.close()
            
            no_conflicts = len(conflicting) == 0
            
            result = ValidationResult(
                'container_conflict_check',
                no_conflicts,
                f"Found {len(conflicting)} conflicting containers" if conflicting else "No container conflicts",
                {'conflicts': conflicting}
            )
            
        except Exception as e:
            result = ValidationResult(
                'container_conflict_check',
                False,
                f"Failed to check containers: {str(e)}"
            )
        
        self.results.append(result)
        logger.info(f"Container Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_file_permissions(self) -> ValidationResult:
        """Check file permissions on Windows"""
        import stat
        
        permission_issues = []
        
        for name, path in self.swarm_paths.items():
            if path.exists():
                try:
                    # Check if writable
                    if path.is_file():
                        with open(path, 'a'):
                            pass
                    elif path.is_dir():
                        test_file = path / '.permission_test'
                        test_file.touch()
                        test_file.unlink()
                except Exception as e:
                    permission_issues.append({
                        'path': str(path),
                        'error': str(e)
                    })
        
        no_issues = len(permission_issues) == 0
        
        result = ValidationResult(
            'permission_check',
            no_issues,
            f"Found {len(permission_issues)} permission issues" if permission_issues else "All paths writable",
            {'issues': permission_issues}
        )
        
        self.results.append(result)
        logger.info(f"Permission Check: {'[OK]' if result.passed else '[FAIL]'} {result.message}")
        return result
    
    async def check_firewall(self) -> ValidationResult:
        """Check Windows firewall settings"""
        try:
            # Check if Docker Desktop is allowed through firewall
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=Docker Desktop'],
                capture_output=True,
                text=True
            )
            
            docker_allowed = 'Enabled:' in result.stdout and 'Yes' in result.stdout
            
            validation_result = ValidationResult(
                'firewall_check',
                True,  # Not critical
                "Docker Desktop firewall rules configured" if docker_allowed else "Docker Desktop firewall rules may need configuration",
                {'docker_allowed': docker_allowed}
            )
            
        except Exception as e:
            validation_result = ValidationResult(
                'firewall_check',
                True,  # Not critical
                f"Could not check firewall: {str(e)}"
            )
        
        self.results.append(validation_result)
        logger.info(f"Firewall Check: {'[OK]' if validation_result.passed else '[FAIL]'} {validation_result.message}")
        return validation_result
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*60)
        print("AUTOGPT INTEGRATION VALIDATION REPORT")
        print("="*60)
        
        critical_results = [r for r in self.results if r.name.startswith('critical_')]
        optional_results = [r for r in self.results if not r.name.startswith('critical_')]
        
        print("\nCRITICAL CHECKS:")
        print("-"*40)
        for result in critical_results:
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status}: {result.message}")
        
        print("\nOPTIONAL CHECKS:")
        print("-"*40)
        for result in optional_results:
            status = "[PASS]" if result.passed else "[WARN]"
            print(f"{status}: {result.message}")
        
        # Summary
        critical_passed = sum(1 for r in critical_results if r.passed)
        critical_total = len(critical_results)
        optional_passed = sum(1 for r in optional_results if r.passed)
        optional_total = len(optional_results)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Critical: {critical_passed}/{critical_total} passed")
        print(f"Optional: {optional_passed}/{optional_total} passed")
        
        all_critical_passed = critical_passed == critical_total
        
        if all_critical_passed:
            print("\n[SUCCESS] SYSTEM READY FOR AUTOGPT INTEGRATION")
        else:
            print("\n[ERROR] SYSTEM NOT READY - FIX CRITICAL ISSUES FIRST")
        
        print("="*60)
        
        return all_critical_passed
    
    def save_report(self, filepath: Optional[str] = None):
        """Save validation report to file"""
        if not filepath:
            filepath = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'critical_passed': sum(1 for r in self.results if r.name.startswith('critical_') and r.passed),
                'critical_total': sum(1 for r in self.results if r.name.startswith('critical_')),
                'optional_passed': sum(1 for r in self.results if not r.name.startswith('critical_') and r.passed),
                'optional_total': sum(1 for r in self.results if not r.name.startswith('critical_'))
            },
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {filepath}")
        return filepath


async def main():
    """Run validation and print report"""
    validator = IntegrationValidator()
    
    print("\n[*] Starting AutoGPT Integration Validation...")
    print("This may take a few moments...\n")
    
    all_passed, results = await validator.validate_all()
    
    validator.print_report()
    validator.save_report()
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())