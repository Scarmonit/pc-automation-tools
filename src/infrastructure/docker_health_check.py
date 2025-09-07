#!/usr/bin/env python3
"""
Docker Health Check Script for AI Swarm Intelligence System
Comprehensive health monitoring for all services
"""

import os
import sys
import json
import time
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

class SwarmHealthChecker:
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'api': self.check_api,
            'redis': self.check_redis,
            'integrations': self.check_integrations,
            'resources': self.check_resources
        }
        
    def check_database(self):
        """Check database connectivity and health"""
        try:
            db_path = os.getenv('DATABASE_PATH', '/data/unified_swarm.db')
            
            if not os.path.exists(db_path):
                return False, "Database file not found"
            
            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            if table_count < 10:  # Should have at least 10 tables
                return False, f"Insufficient tables: {table_count}"
            
            # Check recent activity
            cursor.execute("SELECT COUNT(*) FROM events WHERE created_at > datetime('now', '-1 hour')")
            recent_events = cursor.fetchone()[0]
            
            conn.close()
            
            return True, f"Database OK: {table_count} tables, {recent_events} recent events"
            
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def check_api(self):
        """Check API endpoints"""
        try:
            # Check main API
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code != 200:
                return False, f"API unhealthy: {response.status_code}"
            
            # Check API bridge
            try:
                bridge_response = requests.get('http://localhost:8002/health', timeout=3)
                bridge_ok = bridge_response.status_code == 200
            except:
                bridge_ok = False
            
            return True, f"API OK, Bridge: {'OK' if bridge_ok else 'Down'}"
            
        except Exception as e:
            return False, f"API error: {str(e)}"
    
    def check_redis(self):
        """Check Redis connectivity"""
        try:
            import redis
            r = redis.Redis(host='swarm-cache', port=6379, db=0, socket_timeout=3)
            r.ping()
            return True, "Redis OK"
        except ImportError:
            return True, "Redis client not installed (optional)"
        except Exception as e:
            return False, f"Redis error: {str(e)}"
    
    def check_integrations(self):
        """Check AI Swarm integrations status"""
        try:
            from unified_database_system import UnifiedSwarmDatabase
            
            db = UnifiedSwarmDatabase()
            cursor = db.conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM integrations WHERE active = 1")
            active = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM integrations")
            total = cursor.fetchone()[0]
            
            db.close()
            
            health_percent = (active / total) * 100 if total > 0 else 0
            
            if health_percent < 50:
                return False, f"Low integration health: {active}/{total} ({health_percent:.1f}%)"
            
            return True, f"Integrations OK: {active}/{total} ({health_percent:.1f}%)"
            
        except Exception as e:
            return False, f"Integration check error: {str(e)}"
    
    def check_resources(self):
        """Check system resources"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                return False, f"High CPU usage: {cpu_percent}%"
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return False, f"High memory usage: {memory.percent}%"
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 95:
                return False, f"High disk usage: {disk_percent:.1f}%"
            
            return True, f"Resources OK: CPU {cpu_percent}%, MEM {memory.percent}%, DISK {disk_percent:.1f}%"
            
        except ImportError:
            return True, "psutil not installed (optional)"
        except Exception as e:
            return False, f"Resource check error: {str(e)}"
    
    def run_all_checks(self):
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                healthy, message = check_func()
                results[check_name] = {
                    'healthy': healthy,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                
                if not healthy:
                    overall_healthy = False
                    
            except Exception as e:
                results[check_name] = {
                    'healthy': False,
                    'message': f"Check failed: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }
                overall_healthy = False
        
        results['overall'] = {
            'healthy': overall_healthy,
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def run_single_check(self, check_name):
        """Run a single health check"""
        if check_name not in self.checks:
            return {'healthy': False, 'message': f'Unknown check: {check_name}'}
        
        try:
            healthy, message = self.checks[check_name]()
            return {
                'healthy': healthy,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Check failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

def main():
    """Main health check entry point"""
    checker = SwarmHealthChecker()
    
    # Parse command line arguments
    check_type = 'all'
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check' and len(sys.argv) > 2:
            check_type = sys.argv[2]
    
    # Run checks
    if check_type == 'all':
        results = checker.run_all_checks()
        healthy = results['overall']['healthy']
    else:
        result = checker.run_single_check(check_type)
        results = {check_type: result}
        healthy = result['healthy']
    
    # Output results
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if healthy else 1)

if __name__ == '__main__':
    main()