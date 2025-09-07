#!/usr/bin/env python3
"""
Database Connection Pool for AI Swarm Intelligence System
High-performance connection pooling with automatic optimization
"""

import sqlite3
import threading
import time
import queue
import logging
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from pathlib import Path

class DatabaseConnectionPool:
    """
    Thread-safe SQLite connection pool with performance optimizations
    """
    
    def __init__(self, db_path: str, pool_size: int = 10, timeout: float = 30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.ConnectionPool")
        
        # Connection pool
        self.pool = queue.Queue(maxsize=pool_size)
        self.active_connections = 0
        self.max_connections = pool_size * 2  # Allow burst capacity
        
        # Performance tracking
        self.connection_stats = {
            'total_requests': 0,
            'total_connections_created': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'average_wait_time': 0.0,
            'active_connections': 0
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with optimized connections"""
        try:
            for i in range(self.pool_size):
                conn = self._create_optimized_connection()
                self.pool.put(conn, block=False)
                self.active_connections += 1
                
            self.logger.info(f"Initialized connection pool with {self.pool_size} connections")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _create_optimized_connection(self) -> sqlite3.Connection:
        """Create a new optimized SQLite connection"""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        
        conn.row_factory = sqlite3.Row
        
        # Apply performance optimizations
        cursor = conn.cursor()
        optimizations = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL",
            "PRAGMA cache_size = 10000",
            "PRAGMA temp_store = memory",
            "PRAGMA mmap_size = 268435456",  # 256MB
            "PRAGMA busy_timeout = 30000",    # 30 seconds
            "PRAGMA wal_autocheckpoint = 1000"
        ]
        
        for pragma in optimizations:
            cursor.execute(pragma)
        
        cursor.close()
        self.connection_stats['total_connections_created'] += 1
        
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Context manager to get a connection from the pool
        Automatically returns connection to pool when done
        """
        start_time = time.time()
        conn = None
        
        try:
            # Update stats
            with self.lock:
                self.connection_stats['total_requests'] += 1
            
            # Try to get connection from pool
            try:
                conn = self.pool.get(timeout=self.timeout)
                with self.lock:
                    self.connection_stats['pool_hits'] += 1
                    
            except queue.Empty:
                # Pool exhausted, create new connection if under limit
                with self.lock:
                    if self.active_connections < self.max_connections:
                        conn = self._create_optimized_connection()
                        self.active_connections += 1
                        self.connection_stats['pool_misses'] += 1
                    else:
                        # Wait longer for pool connection
                        try:
                            conn = self.pool.get(timeout=self.timeout * 2)
                            self.connection_stats['pool_hits'] += 1
                        except queue.Empty:
                            raise Exception("Connection pool timeout - all connections busy")
            
            # Update wait time statistics
            wait_time = time.time() - start_time
            with self.lock:
                current_avg = self.connection_stats['average_wait_time']
                total_requests = self.connection_stats['total_requests']
                self.connection_stats['average_wait_time'] = (
                    (current_avg * (total_requests - 1) + wait_time) / total_requests
                )
                self.connection_stats['active_connections'] = self.active_connections
            
            yield conn
            
        finally:
            if conn:
                try:
                    # Return connection to pool
                    self.pool.put(conn, block=False)
                except queue.Full:
                    # Pool is full, close the connection
                    conn.close()
                    with self.lock:
                        self.active_connections -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            stats = self.connection_stats.copy()
            stats.update({
                'pool_size': self.pool_size,
                'max_connections': self.max_connections,
                'current_pool_size': self.pool.qsize(),
                'efficiency': (stats['pool_hits'] / max(stats['total_requests'], 1)) * 100
            })
            return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the connection pool"""
        try:
            # Test a connection from the pool
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[0] == 1:
                    status = "healthy"
                else:
                    status = "unhealthy"
            
            stats = self.get_stats()
            
            return {
                'status': status,
                'timestamp': time.time(),
                'statistics': stats,
                'database_path': self.db_path
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time(),
                'database_path': self.db_path
            }
    
    def optimize_pool(self):
        """Optimize the connection pool based on usage patterns"""
        stats = self.get_stats()
        
        # If efficiency is low, consider increasing pool size
        if stats['efficiency'] < 80 and stats['pool_size'] < 20:
            self._expand_pool(2)
            self.logger.info("Expanded connection pool due to low efficiency")
        
        # If pool is underutilized, consider shrinking
        elif stats['efficiency'] > 95 and stats['pool_size'] > 5:
            self._shrink_pool(1)
            self.logger.info("Shrunk connection pool due to high efficiency")
    
    def _expand_pool(self, additional_connections: int):
        """Expand the pool with additional connections"""
        try:
            for _ in range(additional_connections):
                conn = self._create_optimized_connection()
                self.pool.put(conn, block=False)
                
            self.pool_size += additional_connections
            
        except Exception as e:
            self.logger.error(f"Failed to expand pool: {e}")
    
    def _shrink_pool(self, connections_to_remove: int):
        """Shrink the pool by removing connections"""
        try:
            for _ in range(connections_to_remove):
                try:
                    conn = self.pool.get(block=False)
                    conn.close()
                    with self.lock:
                        self.active_connections -= 1
                except queue.Empty:
                    break
            
            self.pool_size = max(5, self.pool_size - connections_to_remove)
            
        except Exception as e:
            self.logger.error(f"Failed to shrink pool: {e}")
    
    def close_all(self):
        """Close all connections in the pool"""
        closed_count = 0
        
        # Close pooled connections
        while not self.pool.empty():
            try:
                conn = self.pool.get(block=False)
                conn.close()
                closed_count += 1
            except queue.Empty:
                break
        
        # Reset counters
        with self.lock:
            self.active_connections = 0
            self.connection_stats = {
                'total_requests': 0,
                'total_connections_created': 0,
                'pool_hits': 0,
                'pool_misses': 0,
                'average_wait_time': 0.0,
                'active_connections': 0
            }
        
        self.logger.info(f"Closed {closed_count} pooled connections")

# Global connection pool instance
_connection_pools: Dict[str, DatabaseConnectionPool] = {}

def get_connection_pool(db_path: str, pool_size: int = 10) -> DatabaseConnectionPool:
    """
    Get or create a connection pool for the specified database
    Singleton pattern to ensure one pool per database
    """
    if db_path not in _connection_pools:
        _connection_pools[db_path] = DatabaseConnectionPool(db_path, pool_size)
    
    return _connection_pools[db_path]

def close_all_pools():
    """Close all connection pools"""
    for pool in _connection_pools.values():
        pool.close_all()
    
    _connection_pools.clear()

# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import os
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        test_db = f.name
    
    try:
        # Test connection pool
        pool = DatabaseConnectionPool(test_db, pool_size=5)
        
        # Create test table
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.close()
        
        # Test concurrent access
        def worker_function(worker_id: int, operations: int = 10):
            for i in range(operations):
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO test_table (data) VALUES (?)", (f"worker_{worker_id}_op_{i}",))
                    cursor.close()
        
        import concurrent.futures
        
        # Run concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_function, i) for i in range(10)]
            concurrent.futures.wait(futures)
        
        # Check results and stats
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            cursor.close()
        
        stats = pool.get_stats()
        health = pool.health_check()
        
        print(f"\nTest Results:")
        print(f"Records inserted: {count}")
        print(f"Pool efficiency: {stats['efficiency']:.1f}%")
        print(f"Average wait time: {stats['average_wait_time']*1000:.2f}ms")
        print(f"Pool health: {health['status']}")
        
    finally:
        # Cleanup
        close_all_pools()
        os.unlink(test_db)
        print("Test completed successfully!")