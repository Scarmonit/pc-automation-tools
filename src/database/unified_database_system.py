#!/usr/bin/env python3
"""
Unified Database System for AI Swarm Intelligence
Comprehensive database architecture for all swarm components
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading

@dataclass
class DatabaseConfig:
    """Database configuration"""
    main_db: str = "C:/Users/scarm/.claude/swarm-intelligence/unified_swarm.db"
    backup_db: str = "C:/Users/scarm/.claude/swarm-intelligence/backups/unified_swarm_backup.db"
    connection_pool_size: int = 20
    enable_wal: bool = True
    enable_foreign_keys: bool = True

class UnifiedSwarmDatabase:
    """Unified database system for all AI Swarm components"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.logger = logging.getLogger(__name__)
        self.conn = None
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database connection and create schema"""
        try:
            # Ensure directory exists
            Path(self.config.main_db).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(
                self.config.main_db,
                check_same_thread=False,
                isolation_level=None
            )
            
            # Enable optimizations
            if self.config.enable_wal:
                self.conn.execute("PRAGMA journal_mode=WAL")
            if self.config.enable_foreign_keys:
                self.conn.execute("PRAGMA foreign_keys=ON")
            
            # Performance optimizations
            self.conn.execute("PRAGMA cache_size=10000")
            self.conn.execute("PRAGMA temp_store=MEMORY")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            
            # Create schema
            self._create_schema()
            
            self.logger.info(f"Database initialized at {self.config.main_db}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_schema(self):
        """Create comprehensive database schema"""
        
        # Core tables
        schemas = [
            # 1. INTEGRATIONS TABLE - All 43 integrations
            """
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                module_path TEXT,
                description TEXT,
                category TEXT,
                status TEXT DEFAULT 'inactive',
                health_score REAL DEFAULT 1.0,
                active BOOLEAN DEFAULT 0,
                capabilities TEXT,  -- JSON array
                config TEXT,        -- JSON config
                last_activity TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 2. AGENTS TABLE - All swarm agents
            """
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT,
                integration_id TEXT,
                status TEXT DEFAULT 'active',
                capabilities TEXT,  -- JSON array
                config TEXT,        -- JSON config
                memory_size INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (integration_id) REFERENCES integrations(integration_id)
            )
            """,
            
            # 3. TASKS TABLE - All agent tasks
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                agent_id TEXT,
                integration_id TEXT,
                type TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                input_data TEXT,    -- JSON
                output_data TEXT,   -- JSON
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
                FOREIGN KEY (integration_id) REFERENCES integrations(integration_id)
            )
            """,
            
            # 4. METRICS TABLE - Performance metrics
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT,
                source_id TEXT,
                source_type TEXT,
                tags TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 5. MEMORY TABLE - Agent memory and learning
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE NOT NULL,
                agent_id TEXT,
                type TEXT NOT NULL,  -- 'short_term', 'long_term', 'episodic', 'semantic'
                category TEXT,
                content TEXT NOT NULL,
                embedding TEXT,      -- Vector embedding for similarity search
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                decay_rate REAL DEFAULT 0.1,
                metadata TEXT,       -- JSON metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
            """,
            
            # 6. COMMUNICATIONS TABLE - Inter-agent messages
            """
            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                from_agent_id TEXT,
                to_agent_id TEXT,
                broadcast BOOLEAN DEFAULT 0,
                message_type TEXT NOT NULL,
                protocol TEXT,       -- 'signalr', 'mqtt', 'graphql', etc.
                content TEXT NOT NULL,
                headers TEXT,        -- JSON headers
                status TEXT DEFAULT 'sent',
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_at TIMESTAMP,
                acknowledged_at TIMESTAMP,
                FOREIGN KEY (from_agent_id) REFERENCES agents(agent_id),
                FOREIGN KEY (to_agent_id) REFERENCES agents(agent_id)
            )
            """,
            
            # 7. WORKFLOWS TABLE - Orchestrated workflows
            """
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                definition TEXT NOT NULL,  -- JSON workflow definition
                input_data TEXT,           -- JSON
                output_data TEXT,          -- JSON
                error_message TEXT,
                created_by TEXT,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
            """,
            
            # 8. WORKFLOW_STEPS TABLE - Individual workflow steps
            """
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_id TEXT UNIQUE NOT NULL,
                workflow_id TEXT NOT NULL,
                agent_id TEXT,
                step_number INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                input_data TEXT,    -- JSON
                output_data TEXT,   -- JSON
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
            """,
            
            # 9. CONFIGURATIONS TABLE - System and component configs
            """
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                category TEXT,
                description TEXT,
                data_type TEXT,     -- 'string', 'number', 'boolean', 'json'
                is_encrypted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 10. EVENTS TABLE - System events and logs
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                source_id TEXT,
                source_type TEXT,
                message TEXT NOT NULL,
                details TEXT,
                stack_trace TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 11. RESOURCES TABLE - System resources tracking
            """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT UNIQUE NOT NULL,
                resource_type TEXT NOT NULL,  -- 'cpu', 'memory', 'disk', 'network', 'api'
                resource_name TEXT NOT NULL,
                total_capacity REAL,
                used_capacity REAL,
                available_capacity REAL,
                utilization_percent REAL,
                owner_id TEXT,
                owner_type TEXT,
                metadata TEXT,      -- JSON metadata
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 12. API_CALLS TABLE - External API tracking
            """
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT UNIQUE NOT NULL,
                integration_id TEXT,
                api_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                headers TEXT,       -- JSON headers
                request_body TEXT,  -- JSON
                response_body TEXT, -- JSON
                status_code INTEGER,
                response_time_ms INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (integration_id) REFERENCES integrations(integration_id)
            )
            """,
            
            # 13. KNOWLEDGE_BASE TABLE - Accumulated knowledge
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                confidence REAL DEFAULT 0.5,
                verification_status TEXT DEFAULT 'unverified',
                reference_links TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP
            )
            """,
            
            # 14. SESSIONS TABLE - User/system sessions
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,  -- 'user', 'system', 'maintenance'
                status TEXT DEFAULT 'active',
                metadata TEXT,       -- JSON session data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP
            )
            """,
            
            # 15. AUDIT_LOG TABLE - Security and compliance
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT UNIQUE NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id TEXT,
                old_value TEXT,
                new_value TEXT,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                metadata TEXT,       -- JSON metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        # Create all tables
        for schema in schemas:
            try:
                self.conn.execute(schema)
            except sqlite3.Error as e:
                self.logger.error(f"Failed to create table: {e}")
                # Continue with other tables
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_integrations_status ON integrations(status)",
            "CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, priority)",
            "CREATE INDEX IF NOT EXISTS idx_memory_agent ON memory(agent_id, type)",
            "CREATE INDEX IF NOT EXISTS idx_communications_agents ON communications(from_agent_id, to_agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status)",
            "CREATE INDEX IF NOT EXISTS idx_api_calls_integration ON api_calls(integration_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_source ON metrics(source_id, source_type)",
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity)"
        ]
        
        for index in indexes:
            try:
                self.conn.execute(index)
            except sqlite3.Error:
                pass  # Index might already exist
        
        self.conn.commit()
        self.logger.info("Database schema created successfully")
    
    def insert_integration(self, integration_data: Dict[str, Any]) -> int:
        """Insert or update an integration"""
        with self.lock:
            cursor = self.conn.cursor()
            
            # Convert lists/dicts to JSON
            if 'capabilities' in integration_data and isinstance(integration_data['capabilities'], list):
                integration_data['capabilities'] = json.dumps(integration_data['capabilities'])
            if 'config' in integration_data and isinstance(integration_data['config'], dict):
                integration_data['config'] = json.dumps(integration_data['config'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO integrations 
                (integration_id, name, module_path, description, category, status, 
                 health_score, active, capabilities, config, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                integration_data.get('integration_id'),
                integration_data.get('name'),
                integration_data.get('module_path'),
                integration_data.get('description'),
                integration_data.get('category'),
                integration_data.get('status', 'inactive'),
                integration_data.get('health_score', 1.0),
                integration_data.get('active', False),
                integration_data.get('capabilities'),
                integration_data.get('config'),
                integration_data.get('last_activity', datetime.now())
            ))
            
            return cursor.lastrowid
    
    def insert_agent(self, agent_data: Dict[str, Any]) -> int:
        """Insert or update an agent"""
        with self.lock:
            cursor = self.conn.cursor()
            
            # Convert lists/dicts to JSON
            if 'capabilities' in agent_data and isinstance(agent_data['capabilities'], list):
                agent_data['capabilities'] = json.dumps(agent_data['capabilities'])
            if 'config' in agent_data and isinstance(agent_data['config'], dict):
                agent_data['config'] = json.dumps(agent_data['config'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO agents 
                (agent_id, name, type, role, integration_id, status, 
                 capabilities, config, memory_size, tasks_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_data.get('agent_id'),
                agent_data.get('name'),
                agent_data.get('type'),
                agent_data.get('role'),
                agent_data.get('integration_id'),
                agent_data.get('status', 'active'),
                agent_data.get('capabilities'),
                agent_data.get('config'),
                agent_data.get('memory_size', 0),
                agent_data.get('tasks_completed', 0)
            ))
            
            return cursor.lastrowid
    
    def record_metric(self, metric_type: str, metric_name: str, value: float, 
                     source_id: str = None, source_type: str = 'system', tags: Dict = None):
        """Record a performance metric"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO metrics (metric_type, metric_name, metric_value, 
                                   source_id, source_type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric_type, metric_name, value, source_id, source_type,
                json.dumps(tags) if tags else None
            ))
    
    def log_event(self, event_type: str, message: str, severity: str = 'info', 
                  details: Dict = None, source_id: str = None):
        """Log a system event"""
        with self.lock:
            import time
            import random
            cursor = self.conn.cursor()
            event_id = f"evt_{time.time()}_{random.randint(1000, 9999)}"
            cursor.execute("""
                INSERT INTO events (event_id, event_type, severity, source_id, 
                                  message, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id, event_type, severity, source_id, message,
                json.dumps(details) if details else None
            ))
    
    def get_integration_status(self) -> List[Dict]:
        """Get status of all integrations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT integration_id, name, status, health_score, active, 
                   capabilities, last_activity
            FROM integrations
            ORDER BY name
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'integration_id': row[0],
                'name': row[1],
                'status': row[2],
                'health_score': row[3],
                'active': bool(row[4]),
                'capabilities': json.loads(row[5]) if row[5] else [],
                'last_activity': row[6]
            })
        
        return results
    
    def get_system_metrics(self, hours: int = 24) -> Dict:
        """Get system metrics for the last N hours"""
        cursor = self.conn.cursor()
        cutoff = datetime.now().timestamp() - (hours * 3600)
        
        cursor.execute("""
            SELECT metric_type, metric_name, AVG(metric_value) as avg_value,
                   MIN(metric_value) as min_value, MAX(metric_value) as max_value
            FROM metrics
            WHERE timestamp > datetime(?, 'unixepoch')
            GROUP BY metric_type, metric_name
        """, (cutoff,))
        
        metrics = {}
        for row in cursor.fetchall():
            metric_key = f"{row[0]}.{row[1]}"
            metrics[metric_key] = {
                'avg': row[2],
                'min': row[3],
                'max': row[4]
            }
        
        return metrics
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Initialize the unified database
    db = UnifiedSwarmDatabase()
    
    print("="*80)
    print("UNIFIED AI SWARM DATABASE INITIALIZED")
    print("="*80)
    print(f"Database location: {db.config.main_db}")
    print("\nTables created:")
    
    # List all tables
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for i, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"{i:2}. {table[0]:25} - {count:,} records")
    
    print("\n[SUCCESS] Unified database system is ready!")
    print("="*80)
    
    db.close()