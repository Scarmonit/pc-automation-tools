#!/usr/bin/env python3
"""
Docker entry point for AI Swarm Intelligence System
Handles environment setup and startup
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Set up the container environment"""
    print("Setting up AI Swarm environment...")
    
    # Create required directories
    directories = ['/data', '/logs', '/config', '/backups']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True, parents=True)
        print(f"Created directory: {directory}")
    
    # Set up database path
    db_path = Path('/data/unified_swarm.db')
    if not db_path.exists():
        print("Initializing database...")
        # Create a basic database structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables (simplified version)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id TEXT UNIQUE,
                name TEXT,
                status TEXT DEFAULT 'inactive',
                active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE,
                event_type TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add initial integration
        cursor.execute("""
            INSERT OR IGNORE INTO integrations (integration_id, name, status, active)
            VALUES ('integration_01', 'Docker Swarm Core', 'active', 1)
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO events (event_id, event_type, message)
            VALUES ('docker_init', 'system', 'Docker container initialized')
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized")
    
    # Create a simplified AI platform
    return True

def run_simplified_server():
    """Run a simplified HTTP server for testing"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class SwarmHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'service': 'AI Swarm Docker',
                    'containers': ['swarm-master', 'swarm-cache', 'portainer'],
                    'database': os.path.exists('/data/unified_swarm.db')
                }
                
                self.wfile.write(json.dumps(health_data, indent=2).encode())
            
            elif self.path == '/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Get database info
                integrations = 0
                events = 0
                if os.path.exists('/data/unified_swarm.db'):
                    try:
                        conn = sqlite3.connect('/data/unified_swarm.db')
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM integrations")
                        integrations = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM events")
                        events = cursor.fetchone()[0]
                        conn.close()
                    except:
                        pass
                
                status_data = {
                    'service': 'AI Swarm Intelligence System',
                    'version': '2.0 Docker',
                    'status': 'running',
                    'integrations': integrations,
                    'events': events,
                    'uptime': 'Running in Docker',
                    'timestamp': datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(status_data, indent=2).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
        
        def log_message(self, format, *args):
            # Custom log format
            print(f"[{datetime.now().isoformat()}] {format % args}")
    
    print("Starting AI Swarm HTTP Server on port 8000...")
    server = HTTPServer(('0.0.0.0', 8000), SwarmHandler)
    server.serve_forever()

def main():
    """Main entry point"""
    print("="*60)
    print("AI SWARM INTELLIGENCE SYSTEM - DOCKER STARTUP")
    print("="*60)
    print(f"Starting at: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Setup environment
    if not setup_environment():
        print("Failed to setup environment")
        sys.exit(1)
    
    print("Environment setup complete")
    print("Starting simplified AI Swarm server...")
    print("Access endpoints:")
    print("  - Health: http://localhost:8000/health")
    print("  - Status: http://localhost:8000/status")
    print("="*60)
    
    try:
        run_simplified_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()