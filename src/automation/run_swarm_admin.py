#!/usr/bin/env python3
"""
Admin Access Master Swarm Controller
Using SystemAdmin credentials for full swarm access
"""

import asyncio
import json
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the current directory to path
sys.path.append("C:/Users/scarm/src/ai_platform")

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_admin_credentials():
    """Load SystemAdmin credentials"""
    creds_path = "C:/Users/scarm/auth_config/credentials.json"
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
            admin_creds = creds['api_keys']['SystemAdmin']
            logger.info(f"[ADMIN] Loaded credentials for SystemAdmin")
            logger.info(f"[ADMIN] Scopes: {', '.join(admin_creds['scopes'])}")
            return admin_creds
    except Exception as e:
        logger.error(f"Failed to load admin credentials: {e}")
        return None

def create_admin_task(task_type: str, description: str, priority: int = 10):
    """Create a high-priority admin task"""
    import sqlite3
    
    db_path = "C:/Users/scarm/.claude/swarm-intelligence/swarm_memory.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create admin task
        cursor.execute("""
            INSERT INTO agent_tasks 
            (agent_id, task_type, task_description, priority, status)
            VALUES (1, ?, ?, ?, 'pending')
        """, (task_type, description, priority))
        
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"[ADMIN] Created task {task_id}: {task_type} - {description}")
        return task_id
    except Exception as e:
        logger.error(f"Failed to create admin task: {e}")
        return None

def grant_full_system_access():
    """Grant full administrative access across all swarm systems"""
    admin_creds = load_admin_credentials()
    if not admin_creds:
        return False
    
    logger.info("[ADMIN] =" * 60)
    logger.info("[ADMIN] MASTER SWARM ADMINISTRATIVE ACCESS GRANTED")
    logger.info("[ADMIN] =" * 60)
    
    # Create administrative tasks
    admin_tasks = [
        ("system_audit", "Comprehensive system audit and health check", 10),
        ("permission_validation", "Validate all system permissions and access levels", 9),
        ("integration_status", "Check status of all 32 swarm integrations", 8),
        ("performance_optimization", "Optimize system performance and resource allocation", 7),
        ("security_scan", "Run security scan across all components", 8),
        ("database_maintenance", "Perform database optimization and cleanup", 6),
        ("coordination_test", "Test inter-agent coordination and communication", 7)
    ]
    
    created_tasks = []
    for task_type, description, priority in admin_tasks:
        task_id = create_admin_task(task_type, description, priority)
        if task_id:
            created_tasks.append(task_id)
    
    logger.info(f"[ADMIN] Created {len(created_tasks)} administrative tasks")
    logger.info(f"[ADMIN] Task IDs: {created_tasks}")
    
    # Show admin permissions
    logger.info("[ADMIN] Active Permissions:")
    for scope in admin_creds['scopes']:
        logger.info(f"[ADMIN]   ✓ {scope}")
    
    return True

def show_system_status():
    """Show current system status with admin privileges"""
    import sqlite3
    
    db_path = "C:/Users/scarm/.claude/swarm-intelligence/swarm_memory.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get agents
        cursor.execute("SELECT COUNT(*), status FROM swarm_agents GROUP BY status")
        agent_stats = cursor.fetchall()
        
        # Get tasks
        cursor.execute("SELECT COUNT(*), status FROM agent_tasks GROUP BY status")
        task_stats = cursor.fetchall()
        
        # Get recent errors
        cursor.execute("SELECT COUNT(*) FROM error_logs WHERE occurred_at > datetime('now', '-1 hour')")
        recent_errors = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info("[ADMIN] SYSTEM STATUS REPORT:")
        logger.info("[ADMIN] Agents:")
        for count, status in agent_stats:
            logger.info(f"[ADMIN]   {status}: {count}")
        
        logger.info("[ADMIN] Tasks:")
        for count, status in task_stats:
            logger.info(f"[ADMIN]   {status}: {count}")
        
        logger.info(f"[ADMIN] Recent Errors: {recent_errors}")
        
    except Exception as e:
        logger.error(f"[ADMIN] Failed to get system status: {e}")

async def run_swarm_with_admin():
    """Run the swarm system with full administrative privileges"""
    logger.info("Starting Master AI Swarm Intelligence System")
    logger.info("Administrative Mode: ENABLED")
    
    # Grant admin access
    if not grant_full_system_access():
        logger.error("Failed to grant admin access")
        return
    
    # Show system status
    show_system_status()
    
    # Try to import and run the master system
    try:
        from master_ai_swarm_intelligence import MasterAISwarmIntelligence
        
        system = MasterAISwarmIntelligence()
        
        # Start with admin privileges
        logger.info("[ADMIN] Starting swarm system...")
        await system.start_master_swarm()
        
        # Run coordination for 30 seconds
        logger.info("[ADMIN] Executing coordination scenarios...")
        await system.execute_swarm_coordination(30)
        
        # Generate report
        logger.info("[ADMIN] Generating system report...")
        from master_ai_swarm_intelligence import generate_master_report
        report = generate_master_report(system)
        
        # Save admin report
        report_file = "C:/Users/scarm/src/ai_platform/admin_swarm_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"ADMINISTRATIVE ACCESS REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Admin User: SystemAdmin\n")
            f.write(f"{'='*80}\n\n")
            f.write(report)
        
        logger.info(f"[ADMIN] Report saved to: {report_file}")
        
        # Shutdown gracefully
        await system.shutdown_swarm()
        
    except Exception as e:
        logger.error(f"[ADMIN] Swarm execution error: {e}")

def main():
    """Main entry point"""
    try:
        asyncio.run(run_swarm_with_admin())
    except KeyboardInterrupt:
        logger.info("[ADMIN] System interrupted by user")
    except Exception as e:
        logger.error(f"[ADMIN] System error: {e}")

if __name__ == "__main__":
    main()