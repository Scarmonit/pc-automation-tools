#!/usr/bin/env python3
"""
Database Synchronization Layer for AI Swarm Intelligence
Provides distributed database synchronization with conflict resolution and error handling
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
import time
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import aiofiles
import aiosqlite
from concurrent.futures import ThreadPoolExecutor

# Import our error handling system
from error_handling import (
    ErrorHandler, CircuitBreaker, RetryStrategy, SwarmLogger, SwarmError
)

# Configure enhanced logging
logger = SwarmLogger("database_sync").get_logger()

class SyncStatus(Enum):
    """Synchronization status"""
    IDLE = "idle"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    RECOVERING = "recovering"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    MERGE = "merge"
    PRIORITY_BASED = "priority_based"
    MANUAL = "manual"

class SyncOperation(Enum):
    """Types of sync operations"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BULK_SYNC = "bulk_sync"

@dataclass
class SyncRecord:
    """Record for synchronization tracking"""
    record_id: str
    table_name: str
    operation: SyncOperation
    data: Dict[str, Any]
    timestamp: datetime
    agent_id: str
    version: int = 1
    hash_value: str = ""
    sync_status: str = "pending"
    retry_count: int = 0
    
    def __post_init__(self):
        if not self.hash_value:
            self.hash_value = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate hash of the record data"""
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

@dataclass
class DatabaseNode:
    """Database node configuration"""
    node_id: str
    database_path: str
    host: str = "localhost"
    port: int = 0
    priority: int = 1
    is_primary: bool = False
    is_online: bool = True
    last_sync: Optional[datetime] = None
    sync_lag: float = 0.0
    
class DatabaseSyncLayer:
    """
    Comprehensive Database Synchronization Layer
    Handles distributed synchronization with conflict resolution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the database synchronization layer"""
        self.config = config or {}
        
        # Core configuration
        self.node_id = self.config.get("node_id", f"node-{uuid.uuid4().hex[:8]}")
        self.primary_db_path = self.config.get(
            "primary_db_path", 
            os.getenv("SWARM_MEMORY_DB", "swarm_memory.db")
        )
        self.sync_db_path = self.config.get(
            "sync_db_path",
            "swarm_sync.db"
        )
        self.backup_dir = Path(self.config.get("backup_dir", "backups"))
        self.backup_dir.mkdir(exist_ok=True)
        
        # Synchronization settings
        self.sync_interval = self.config.get("sync_interval", 30)  # seconds
        self.conflict_resolution = ConflictResolution(
            self.config.get("conflict_resolution", "latest_wins")
        )
        self.max_sync_retries = self.config.get("max_sync_retries", 3)
        self.batch_size = self.config.get("batch_size", 100)
        self.sync_timeout = self.config.get("sync_timeout", 60)
        
        # Error handling
        self.error_handler = ErrorHandler()
        self.sync_circuit_breaker = CircuitBreaker(
            name="database_sync",
            failure_threshold=5,
            recovery_timeout=60.0,
            expected_exception=Exception
        )
        self.retry_strategy = RetryStrategy(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0
        )
        
        # State management
        self.status = SyncStatus.IDLE
        self.nodes: Dict[str, DatabaseNode] = {}
        self.pending_operations: Dict[str, SyncRecord] = {}
        self.conflict_queue: List[SyncRecord] = []
        self.sync_history: List[Dict[str, Any]] = []
        
        # Threading
        self.sync_lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.sync_task = None
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Statistics
        self.stats = {
            "records_synced": 0,
            "conflicts_resolved": 0,
            "sync_failures": 0,
            "last_full_sync": None,
            "avg_sync_time": 0.0,
            "nodes_online": 0,
            "data_integrity_checks": 0
        }
        
        # Callbacks for monitoring
        self.sync_callbacks: List[Callable] = []
        self.conflict_callbacks: List[Callable] = []
        
    async def initialize(self):
        """Initialize the synchronization layer"""
        logger.info(f"Initializing database sync layer for node {self.node_id}")
        
        try:
            # Initialize error handler
            await self.error_handler.initialize()
            
            # Setup databases
            await self._setup_databases()
            
            # Initialize nodes
            await self._initialize_nodes()
            
            # Start background sync task
            await self._start_sync_task()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            logger.info("Database synchronization layer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database sync layer: {e}")
            raise SwarmError(f"Sync layer initialization failed: {e}")
    
    async def _setup_databases(self):
        """Setup primary and sync tracking databases"""
        # Ensure primary database exists
        if not Path(self.primary_db_path).exists():
            await self._create_primary_database()
        
        # Setup sync tracking database
        await self._create_sync_database()
        
        # Verify database integrity
        await self._verify_database_integrity()
    
    async def _create_primary_database(self):
        """Create the primary database with required tables"""
        logger.info(f"Creating primary database: {self.primary_db_path}")
        
        async with aiosqlite.connect(self.primary_db_path) as db:
            # Agent memory table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    agent_id TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    hash_value TEXT,
                    UNIQUE(namespace, key, agent_id)
                )
            """)
            
            # Task tracking table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_tracking (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    assigned_agent TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    priority INTEGER DEFAULT 3,
                    data TEXT,
                    result TEXT,
                    version INTEGER DEFAULT 1,
                    hash_value TEXT
                )
            """)
            
            # Agent registry table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agent_registry (
                    agent_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    capabilities TEXT,
                    last_heartbeat TEXT,
                    registered_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1,
                    hash_value TEXT
                )
            """)
            
            # Create indexes
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_namespace_key ON agent_memory(namespace, key)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_agent ON agent_memory(agent_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON task_tracking(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_task_agent ON task_tracking(assigned_agent)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_agent_type ON agent_registry(agent_type)")
            
            await db.commit()
    
    async def _create_sync_database(self):
        """Create the synchronization tracking database"""
        logger.info(f"Creating sync database: {self.sync_db_path}")
        
        async with aiosqlite.connect(self.sync_db_path) as db:
            # Sync operations log
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    hash_value TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    synced_at TEXT
                )
            """)
            
            # Sync conflicts
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    local_data TEXT NOT NULL,
                    remote_data TEXT NOT NULL,
                    conflict_type TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT,
                    resolution_strategy TEXT,
                    resolved_data TEXT
                )
            """)
            
            # Node registry
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_nodes (
                    node_id TEXT PRIMARY KEY,
                    database_path TEXT NOT NULL,
                    host TEXT DEFAULT 'localhost',
                    port INTEGER DEFAULT 0,
                    priority INTEGER DEFAULT 1,
                    is_primary BOOLEAN DEFAULT 0,
                    is_online BOOLEAN DEFAULT 1,
                    last_sync TEXT,
                    sync_lag REAL DEFAULT 0.0,
                    registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sync checkpoints
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    last_sync_id INTEGER DEFAULT 0,
                    last_sync_time TEXT NOT NULL,
                    record_count INTEGER DEFAULT 0,
                    checksum TEXT
                )
            """)
            
            await db.commit()
    
    async def _verify_database_integrity(self):
        """Verify database integrity and fix issues"""
        logger.info("Verifying database integrity")
        
        try:
            async with aiosqlite.connect(self.primary_db_path) as db:
                # Check if all expected tables exist
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('agent_memory', 'task_tracking', 'agent_registry')
                """)
                tables = [row[0] for row in await cursor.fetchall()]
                
                expected_tables = ['agent_memory', 'task_tracking', 'agent_registry']
                missing_tables = set(expected_tables) - set(tables)
                
                if missing_tables:
                    logger.warning(f"Missing tables: {missing_tables}, recreating...")
                    await self._create_primary_database()
                
                # Update hash values for existing records
                await self._update_hash_values()
                
                self.stats["data_integrity_checks"] += 1
                
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")
            raise SwarmError(f"Database integrity verification failed: {e}")
    
    async def _update_hash_values(self):
        """Update hash values for existing records"""
        logger.info("Updating hash values for existing records")
        
        async with aiosqlite.connect(self.primary_db_path) as db:
            # Update agent_memory hash values
            cursor = await db.execute("SELECT id, namespace, key, value, agent_id FROM agent_memory WHERE hash_value IS NULL")
            rows = await cursor.fetchall()
            
            for row_id, namespace, key, value, agent_id in rows:
                data = {"namespace": namespace, "key": key, "value": value, "agent_id": agent_id}
                hash_value = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
                await db.execute("UPDATE agent_memory SET hash_value = ? WHERE id = ?", (hash_value, row_id))
            
            # Update task_tracking hash values
            cursor = await db.execute("SELECT task_id, status, data FROM task_tracking WHERE hash_value IS NULL")
            rows = await cursor.fetchall()
            
            for task_id, status, data in rows:
                record_data = {"task_id": task_id, "status": status, "data": data}
                hash_value = hashlib.sha256(json.dumps(record_data, sort_keys=True, default=str).encode()).hexdigest()
                await db.execute("UPDATE task_tracking SET hash_value = ? WHERE task_id = ?", (hash_value, task_id))
            
            await db.commit()
    
    async def _initialize_nodes(self):
        """Initialize database nodes for synchronization"""
        # Register self as a node
        self_node = DatabaseNode(
            node_id=self.node_id,
            database_path=self.primary_db_path,
            is_primary=True,
            is_online=True,
            last_sync=datetime.now()
        )
        self.nodes[self.node_id] = self_node
        
        # Register in sync database
        await self._register_node(self_node)
        
        # Discover other nodes (from config or environment)
        await self._discover_nodes()
    
    async def _register_node(self, node: DatabaseNode):
        """Register a node in the sync database"""
        async with aiosqlite.connect(self.sync_db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO sync_nodes 
                (node_id, database_path, host, port, priority, is_primary, is_online, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node.node_id, node.database_path, node.host, node.port,
                node.priority, node.is_primary, node.is_online, 
                node.last_sync.isoformat() if node.last_sync else None
            ))
            await db.commit()
    
    async def _discover_nodes(self):
        """Discover other database nodes"""
        # Check for additional node configurations
        additional_dbs = os.getenv("SWARM_ADDITIONAL_DBS", "").split(",")
        
        for i, db_path in enumerate(additional_dbs):
            if db_path.strip() and Path(db_path.strip()).exists():
                node_id = f"node-{i+1}"
                node = DatabaseNode(
                    node_id=node_id,
                    database_path=db_path.strip(),
                    priority=2,
                    is_primary=False
                )
                self.nodes[node_id] = node
                await self._register_node(node)
        
        logger.info(f"Discovered {len(self.nodes)} database nodes")
    
    async def _start_sync_task(self):
        """Start the background synchronization task"""
        if self.sync_task and not self.sync_task.done():
            return
        
        self.sync_task = asyncio.create_task(self._sync_loop())
        self.background_tasks.add(self.sync_task)
        self.sync_task.add_done_callback(self.background_tasks.discard)
        
        logger.info("Started background sync task")
    
    async def _start_monitoring_tasks(self):
        """Start monitoring background tasks"""
        # Node health monitoring
        health_task = asyncio.create_task(self._monitor_node_health())
        self.background_tasks.add(health_task)
        health_task.add_done_callback(self.background_tasks.discard)
        
        # Conflict resolution task
        conflict_task = asyncio.create_task(self._process_conflicts())
        self.background_tasks.add(conflict_task)
        conflict_task.add_done_callback(self.background_tasks.discard)
        
        # Backup task
        backup_task = asyncio.create_task(self._backup_loop())
        self.background_tasks.add(backup_task)
        backup_task.add_done_callback(self.background_tasks.discard)
        
        logger.info("Started monitoring tasks")
    
    async def _sync_loop(self):
        """Main synchronization loop"""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                
                if self.status != SyncStatus.IDLE:
                    continue
                
                await self._perform_sync()
                
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(5)
    
    async def _perform_sync(self):
        """Perform synchronization with all nodes"""
        async with self.sync_lock:
            self.status = SyncStatus.SYNCING
            start_time = time.time()
            
            try:
                logger.debug("Starting synchronization")
                
                # Sync pending operations
                await self._sync_pending_operations()
                
                # Perform bi-directional sync with each node
                for node_id, node in self.nodes.items():
                    if node_id != self.node_id and node.is_online:
                        await self._sync_with_node(node)
                
                # Update statistics
                sync_time = time.time() - start_time
                self._update_sync_stats(sync_time)
                
                # Notify callbacks
                await self._notify_sync_callbacks("sync_completed", {"sync_time": sync_time})
                
                self.status = SyncStatus.IDLE
                logger.debug(f"Sync completed in {sync_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Sync failed: {e}")
                self.status = SyncStatus.ERROR
                self.stats["sync_failures"] += 1
                
                # Try recovery
                await self._attempt_sync_recovery()
    
    async def _sync_pending_operations(self):
        """Sync pending operations from the queue"""
        async with aiosqlite.connect(self.sync_db_path) as db:
            cursor = await db.execute("""
                SELECT record_id, table_name, operation, data, timestamp, agent_id, version, hash_value
                FROM sync_operations
                WHERE sync_status = 'pending' AND retry_count < ?
                ORDER BY timestamp
                LIMIT ?
            """, (self.max_sync_retries, self.batch_size))
            
            pending_ops = await cursor.fetchall()
            
            for record_id, table_name, operation, data_str, timestamp, agent_id, version, hash_value in pending_ops:
                try:
                    data = json.loads(data_str)
                    sync_record = SyncRecord(
                        record_id=record_id,
                        table_name=table_name,
                        operation=SyncOperation(operation),
                        data=data,
                        timestamp=datetime.fromisoformat(timestamp),
                        agent_id=agent_id,
                        version=version,
                        hash_value=hash_value
                    )
                    
                    await self._apply_sync_record(sync_record)
                    
                    # Mark as synced
                    await db.execute("""
                        UPDATE sync_operations 
                        SET sync_status = 'synced', synced_at = ? 
                        WHERE record_id = ?
                    """, (datetime.now().isoformat(), record_id))
                    
                    self.stats["records_synced"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync operation {record_id}: {e}")
                    
                    # Increment retry count
                    await db.execute("""
                        UPDATE sync_operations 
                        SET retry_count = retry_count + 1
                        WHERE record_id = ?
                    """, (record_id,))
            
            await db.commit()
    
    async def _sync_with_node(self, node: DatabaseNode):
        """Synchronize with a specific node"""
        try:
            logger.debug(f"Syncing with node {node.node_id}")
            
            if not Path(node.database_path).exists():
                logger.warning(f"Node database not found: {node.database_path}")
                node.is_online = False
                return
            
            # Get changes since last sync
            changes = await self._get_changes_since_last_sync(node)
            
            if changes:
                # Apply changes from remote node
                await self._apply_remote_changes(node, changes)
                
                # Send our changes to remote node
                await self._send_changes_to_node(node)
            
            # Update last sync time
            node.last_sync = datetime.now()
            await self._update_node_sync_time(node)
            
        except Exception as e:
            logger.error(f"Failed to sync with node {node.node_id}: {e}")
            node.is_online = False
    
    async def _get_changes_since_last_sync(self, node: DatabaseNode) -> List[Dict[str, Any]]:
        """Get changes from a node since last sync"""
        changes = []
        
        try:
            async with aiosqlite.connect(node.database_path) as db:
                # Get the last sync checkpoint
                last_sync_time = node.last_sync.isoformat() if node.last_sync else "1970-01-01"
                
                # Check each table for changes
                tables = ["agent_memory", "task_tracking", "agent_registry"]
                
                for table in tables:
                    cursor = await db.execute(f"""
                        SELECT * FROM {table} 
                        WHERE updated_at > ? 
                        ORDER BY updated_at
                        LIMIT ?
                    """, (last_sync_time, self.batch_size))
                    
                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    for row in rows:
                        record = dict(zip(columns, row))
                        record["_table"] = table
                        changes.append(record)
        
        except Exception as e:
            logger.error(f"Failed to get changes from node {node.node_id}: {e}")
        
        return changes
    
    async def _apply_remote_changes(self, node: DatabaseNode, changes: List[Dict[str, Any]]):
        """Apply changes from a remote node"""
        for change in changes:
            try:
                table_name = change.pop("_table")
                
                # Check for conflicts
                conflict = await self._detect_conflict(table_name, change)
                
                if conflict:
                    await self._handle_conflict(table_name, change, conflict)
                else:
                    await self._apply_change_to_primary(table_name, change)
                
            except Exception as e:
                logger.error(f"Failed to apply change from {node.node_id}: {e}")
    
    async def _detect_conflict(self, table_name: str, remote_change: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if a remote change conflicts with local data"""
        async with aiosqlite.connect(self.primary_db_path) as db:
            # Determine the primary key for the table
            primary_key = self._get_table_primary_key(table_name)
            key_value = remote_change.get(primary_key)
            
            if not key_value:
                return None
            
            # Get current local record
            cursor = await db.execute(f"SELECT * FROM {table_name} WHERE {primary_key} = ?", (key_value,))
            local_record = await cursor.fetchone()
            
            if not local_record:
                return None  # No conflict, it's a new record
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            local_dict = dict(zip(columns, local_record))
            
            # Compare hash values or timestamps
            local_hash = local_dict.get("hash_value")
            remote_hash = remote_change.get("hash_value")
            
            local_updated = local_dict.get("updated_at", "")
            remote_updated = remote_change.get("updated_at", "")
            
            if local_hash and remote_hash and local_hash != remote_hash:
                if local_updated != remote_updated:
                    return local_dict  # Conflict detected
            
            return None
    
    def _get_table_primary_key(self, table_name: str) -> str:
        """Get the primary key column name for a table"""
        primary_keys = {
            "agent_memory": "id",
            "task_tracking": "task_id",
            "agent_registry": "agent_id"
        }
        return primary_keys.get(table_name, "id")
    
    async def _handle_conflict(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Handle a synchronization conflict"""
        logger.warning(f"Conflict detected in table {table_name}")
        
        # Log the conflict
        await self._log_conflict(table_name, remote_change, local_record)
        
        # Apply conflict resolution strategy
        if self.conflict_resolution == ConflictResolution.LATEST_WINS:
            await self._resolve_conflict_latest_wins(table_name, remote_change, local_record)
        elif self.conflict_resolution == ConflictResolution.MERGE:
            await self._resolve_conflict_merge(table_name, remote_change, local_record)
        elif self.conflict_resolution == ConflictResolution.PRIORITY_BASED:
            await self._resolve_conflict_priority(table_name, remote_change, local_record)
        else:
            # Queue for manual resolution
            self.conflict_queue.append(SyncRecord(
                record_id=str(uuid.uuid4()),
                table_name=table_name,
                operation=SyncOperation.UPDATE,
                data=remote_change,
                timestamp=datetime.now(),
                agent_id="conflict_resolver"
            ))
        
        self.stats["conflicts_resolved"] += 1
        
        # Notify conflict callbacks
        await self._notify_conflict_callbacks(table_name, remote_change, local_record)
    
    async def _resolve_conflict_latest_wins(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Resolve conflict using latest timestamp wins strategy"""
        remote_time = remote_change.get("updated_at", "")
        local_time = local_record.get("updated_at", "")
        
        if remote_time > local_time:
            await self._apply_change_to_primary(table_name, remote_change)
            logger.info(f"Conflict resolved: remote change wins for {table_name}")
        else:
            logger.info(f"Conflict resolved: local record wins for {table_name}")
    
    async def _resolve_conflict_merge(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Resolve conflict by merging changes"""
        # Simple merge strategy - combine non-conflicting fields
        merged_record = local_record.copy()
        
        # Update with remote changes, preserving local metadata
        for key, value in remote_change.items():
            if key not in ["id", "created_at", "version", "hash_value"]:
                if key not in merged_record or merged_record[key] != value:
                    merged_record[key] = value
        
        # Increment version and update timestamp
        merged_record["version"] = max(
            local_record.get("version", 1),
            remote_change.get("version", 1)
        ) + 1
        merged_record["updated_at"] = datetime.now().isoformat()
        
        # Recalculate hash
        data_for_hash = {k: v for k, v in merged_record.items() 
                        if k not in ["id", "hash_value", "created_at", "updated_at"]}
        merged_record["hash_value"] = hashlib.sha256(
            json.dumps(data_for_hash, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        await self._apply_change_to_primary(table_name, merged_record)
        logger.info(f"Conflict resolved: changes merged for {table_name}")
    
    async def _resolve_conflict_priority(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Resolve conflict based on agent priority"""
        remote_agent = remote_change.get("agent_id", "")
        local_agent = local_record.get("agent_id", "")
        
        # Simple priority: shorter agent ID wins (primary agents typically have shorter IDs)
        if len(remote_agent) < len(local_agent):
            await self._apply_change_to_primary(table_name, remote_change)
            logger.info(f"Conflict resolved: higher priority remote agent for {table_name}")
        else:
            logger.info(f"Conflict resolved: local agent has priority for {table_name}")
    
    async def _log_conflict(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Log a synchronization conflict"""
        async with aiosqlite.connect(self.sync_db_path) as db:
            await db.execute("""
                INSERT INTO sync_conflicts 
                (record_id, table_name, local_data, remote_data, conflict_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                table_name,
                json.dumps(local_record, default=str),
                json.dumps(remote_change, default=str),
                "data_conflict"
            ))
            await db.commit()
    
    async def _apply_change_to_primary(self, table_name: str, change: Dict[str, Any]):
        """Apply a change to the primary database"""
        async with aiosqlite.connect(self.primary_db_path) as db:
            primary_key = self._get_table_primary_key(table_name)
            key_value = change.get(primary_key)
            
            if not key_value:
                return
            
            # Check if record exists
            cursor = await db.execute(f"SELECT 1 FROM {table_name} WHERE {primary_key} = ?", (key_value,))
            exists = await cursor.fetchone()
            
            if exists:
                # Update existing record
                set_clause = ", ".join([f"{k} = ?" for k in change.keys() if k != primary_key])
                values = [v for k, v in change.items() if k != primary_key] + [key_value]
                
                await db.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?", values)
            else:
                # Insert new record
                columns = ", ".join(change.keys())
                placeholders = ", ".join(["?"] * len(change))
                values = list(change.values())
                
                await db.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            
            await db.commit()
    
    async def _apply_sync_record(self, sync_record: SyncRecord):
        """Apply a sync record to the database"""
        if sync_record.operation == SyncOperation.INSERT:
            await self._apply_change_to_primary(sync_record.table_name, sync_record.data)
        elif sync_record.operation == SyncOperation.UPDATE:
            await self._apply_change_to_primary(sync_record.table_name, sync_record.data)
        elif sync_record.operation == SyncOperation.DELETE:
            await self._delete_from_primary(sync_record.table_name, sync_record.data)
    
    async def _delete_from_primary(self, table_name: str, data: Dict[str, Any]):
        """Delete a record from the primary database"""
        async with aiosqlite.connect(self.primary_db_path) as db:
            primary_key = self._get_table_primary_key(table_name)
            key_value = data.get(primary_key)
            
            if key_value:
                await db.execute(f"DELETE FROM {table_name} WHERE {primary_key} = ?", (key_value,))
                await db.commit()
    
    async def _send_changes_to_node(self, node: DatabaseNode):
        """Send our changes to a remote node"""
        # For this implementation, we assume nodes are read-only replicas
        # In a full bi-directional sync, this would push changes to the remote node
        logger.debug(f"Changes sent to node {node.node_id} (placeholder)")
    
    async def _update_node_sync_time(self, node: DatabaseNode):
        """Update the last sync time for a node"""
        async with aiosqlite.connect(self.sync_db_path) as db:
            await db.execute("""
                UPDATE sync_nodes 
                SET last_sync = ?, sync_lag = ?
                WHERE node_id = ?
            """, (
                node.last_sync.isoformat(),
                node.sync_lag,
                node.node_id
            ))
            await db.commit()
    
    def _update_sync_stats(self, sync_time: float):
        """Update synchronization statistics"""
        self.stats["last_full_sync"] = datetime.now().isoformat()
        
        # Update average sync time
        if self.stats["avg_sync_time"] == 0:
            self.stats["avg_sync_time"] = sync_time
        else:
            self.stats["avg_sync_time"] = (self.stats["avg_sync_time"] + sync_time) / 2
        
        # Count online nodes
        self.stats["nodes_online"] = sum(1 for node in self.nodes.values() if node.is_online)
    
    async def _monitor_node_health(self):
        """Monitor the health of all nodes"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for node in self.nodes.values():
                    if node.node_id == self.node_id:
                        continue  # Skip self
                    
                    # Check if database file exists and is accessible
                    if Path(node.database_path).exists():
                        try:
                            # Try to connect and query
                            async with aiosqlite.connect(node.database_path) as db:
                                await db.execute("SELECT 1")
                                
                            if not node.is_online:
                                logger.info(f"Node {node.node_id} is back online")
                                node.is_online = True
                        
                        except Exception as e:
                            if node.is_online:
                                logger.warning(f"Node {node.node_id} went offline: {e}")
                                node.is_online = False
                    else:
                        if node.is_online:
                            logger.warning(f"Node {node.node_id} database not found")
                            node.is_online = False
                
            except Exception as e:
                logger.error(f"Node health monitoring error: {e}")
    
    async def _process_conflicts(self):
        """Process queued conflicts"""
        while True:
            try:
                await asyncio.sleep(30)  # Process conflicts every 30 seconds
                
                if self.conflict_queue:
                    logger.info(f"Processing {len(self.conflict_queue)} queued conflicts")
                    
                    # Process up to 10 conflicts at a time
                    conflicts_to_process = self.conflict_queue[:10]
                    self.conflict_queue = self.conflict_queue[10:]
                    
                    for conflict in conflicts_to_process:
                        # For now, apply latest wins strategy to queued conflicts
                        await self._apply_change_to_primary(conflict.table_name, conflict.data)
                        logger.info(f"Auto-resolved queued conflict for {conflict.table_name}")
                
            except Exception as e:
                logger.error(f"Conflict processing error: {e}")
    
    async def _backup_loop(self):
        """Periodic database backup"""
        while True:
            try:
                await asyncio.sleep(3600)  # Backup every hour
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"swarm_memory_backup_{timestamp}.db"
                
                # Copy the database file
                import shutil
                shutil.copy2(self.primary_db_path, backup_path)
                
                # Keep only the last 24 backups
                backups = sorted(self.backup_dir.glob("swarm_memory_backup_*.db"))
                if len(backups) > 24:
                    for old_backup in backups[:-24]:
                        old_backup.unlink()
                
                logger.info(f"Database backed up to {backup_path}")
                
            except Exception as e:
                logger.error(f"Backup failed: {e}")
    
    async def _attempt_sync_recovery(self):
        """Attempt to recover from sync failures"""
        logger.info("Attempting sync recovery")
        
        self.status = SyncStatus.RECOVERING
        
        try:
            # Check database integrity
            await self._verify_database_integrity()
            
            # Reset circuit breaker
            if hasattr(self.sync_circuit_breaker, 'reset'):
                self.sync_circuit_breaker.reset()
            
            # Clear failed operations
            async with aiosqlite.connect(self.sync_db_path) as db:
                await db.execute("DELETE FROM sync_operations WHERE retry_count >= ?", (self.max_sync_retries,))
                await db.commit()
            
            self.status = SyncStatus.IDLE
            logger.info("Sync recovery completed")
            
        except Exception as e:
            logger.error(f"Sync recovery failed: {e}")
            self.status = SyncStatus.ERROR
    
    # Public API methods
    async def queue_operation(self, table_name: str, operation: SyncOperation, data: Dict[str, Any], agent_id: str):
        """Queue a synchronization operation"""
        sync_record = SyncRecord(
            record_id=str(uuid.uuid4()),
            table_name=table_name,
            operation=operation,
            data=data,
            timestamp=datetime.now(),
            agent_id=agent_id
        )
        
        # Add to sync queue
        async with aiosqlite.connect(self.sync_db_path) as db:
            await db.execute("""
                INSERT INTO sync_operations 
                (record_id, table_name, operation, data, timestamp, agent_id, version, hash_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sync_record.record_id,
                sync_record.table_name,
                sync_record.operation.value,
                json.dumps(sync_record.data, default=str),
                sync_record.timestamp.isoformat(),
                sync_record.agent_id,
                sync_record.version,
                sync_record.hash_value
            ))
            await db.commit()
        
        logger.debug(f"Queued sync operation: {operation.value} on {table_name}")
    
    async def add_sync_callback(self, callback: Callable):
        """Add a callback for sync events"""
        self.sync_callbacks.append(callback)
    
    async def add_conflict_callback(self, callback: Callable):
        """Add a callback for conflict events"""
        self.conflict_callbacks.append(callback)
    
    async def _notify_sync_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Notify sync event callbacks"""
        for callback in self.sync_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Sync callback error: {e}")
    
    async def _notify_conflict_callbacks(self, table_name: str, remote_change: Dict[str, Any], local_record: Dict[str, Any]):
        """Notify conflict event callbacks"""
        for callback in self.conflict_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(table_name, remote_change, local_record)
                else:
                    callback(table_name, remote_change, local_record)
            except Exception as e:
                logger.error(f"Conflict callback error: {e}")
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get comprehensive sync status"""
        return {
            "node_id": self.node_id,
            "status": self.status.value,
            "nodes": {
                node_id: {
                    "is_online": node.is_online,
                    "last_sync": node.last_sync.isoformat() if node.last_sync else None,
                    "sync_lag": node.sync_lag,
                    "is_primary": node.is_primary
                }
                for node_id, node in self.nodes.items()
            },
            "statistics": self.stats,
            "pending_operations": len(self.pending_operations),
            "conflicts_queued": len(self.conflict_queue),
            "conflict_resolution_strategy": self.conflict_resolution.value
        }
    
    async def force_sync(self):
        """Force an immediate synchronization"""
        if self.status == SyncStatus.IDLE:
            await self._perform_sync()
            return True
        return False
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up database sync layer")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close executor
        self.executor.shutdown(wait=True)
        
        # Cleanup error handler
        if hasattr(self.error_handler, 'cleanup'):
            await self.error_handler.cleanup()
        
        logger.info("Database sync layer cleanup complete")

# Standalone testing
async def main():
    """Test database synchronization layer"""
    config = {
        "node_id": "test-node-1",
        "sync_interval": 10,
        "conflict_resolution": "latest_wins"
    }
    
    sync_layer = DatabaseSyncLayer(config)
    
    try:
        await sync_layer.initialize()
        
        # Test queueing operations
        await sync_layer.queue_operation(
            "agent_memory",
            SyncOperation.INSERT,
            {
                "namespace": "test",
                "key": "test_key",
                "value": "test_value",
                "agent_id": "test_agent"
            },
            "test_agent"
        )
        
        # Get status
        status = await sync_layer.get_sync_status()
        print(json.dumps(status, indent=2, default=str))
        
        # Wait a bit for sync
        await asyncio.sleep(15)
        
        # Force sync
        await sync_layer.force_sync()
        
        # Get updated status
        status = await sync_layer.get_sync_status()
        print("Final status:")
        print(json.dumps(status, indent=2, default=str))
        
    finally:
        await sync_layer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())