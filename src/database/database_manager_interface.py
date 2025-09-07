#!/usr/bin/env python3
"""
Database Management Interface for AI Swarm Intelligence
Interactive CLI and API for managing the unified database
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
from unified_database_system import UnifiedSwarmDatabase

class DatabaseManager:
    """Interactive database management interface"""
    
    def __init__(self):
        self.db = UnifiedSwarmDatabase()
        
    def status(self):
        """Get overall database status"""
        cursor = self.db.conn.cursor()
        
        print("\n" + "="*80)
        print("DATABASE STATUS REPORT")
        print("="*80)
        
        # Get table statistics
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        total_records = 0
        print("\nTABLE STATISTICS:")
        print("-"*40)
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue
                
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            
            if count > 0:
                print(f"{table_name:20} : {count:,} records")
        
        print("-"*40)
        print(f"{'TOTAL':20} : {total_records:,} records")
        
        # Get database size
        db_path = Path(self.db.config.main_db)
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"\nDatabase Size: {size_mb:.2f} MB")
        
        # Active integrations
        cursor.execute("SELECT COUNT(*) FROM integrations WHERE active = 1")
        active_integrations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM integrations")
        total_integrations = cursor.fetchone()[0]
        
        print(f"\nINTEGRATIONS:")
        print(f"  Active: {active_integrations}/{total_integrations}")
        
        # Agent status
        cursor.execute("SELECT status, COUNT(*) FROM agents GROUP BY status")
        agent_status = cursor.fetchall()
        
        if agent_status:
            print(f"\nAGENTS:")
            for status, count in agent_status:
                print(f"  {status}: {count}")
        
        # Recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE created_at > datetime('now', '-1 hour')
        """)
        recent_events = cursor.fetchone()[0]
        
        print(f"\nRECENT ACTIVITY:")
        print(f"  Events (last hour): {recent_events}")
        
        # Performance metrics
        cursor.execute("""
            SELECT metric_type, AVG(metric_value), COUNT(*)
            FROM metrics
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY metric_type
        """)
        metrics = cursor.fetchall()
        
        if metrics:
            print(f"\nPERFORMANCE METRICS (last hour):")
            for metric_type, avg_value, count in metrics:
                print(f"  {metric_type}: {avg_value:.2f} (samples: {count})")
        
        print("="*80)
    
    def list_integrations(self, active_only=False):
        """List all integrations"""
        integrations = self.db.get_integration_status()
        
        print("\n" + "="*80)
        print("INTEGRATION LIST")
        print("="*80)
        
        active_count = 0
        for integration in integrations:
            if active_only and not integration['active']:
                continue
            
            status = "[ACTIVE]" if integration['active'] else "[INACTIVE]"
            health = integration['health_score'] * 100
            
            print(f"\n[{integration['integration_id']}] {integration['name']}")
            print(f"  Status: {status}")
            print(f"  Health: {health:.1f}%")
            
            if integration['capabilities']:
                print(f"  Capabilities: {', '.join(integration['capabilities'][:3])}")
            
            if integration['active']:
                active_count += 1
        
        print("\n" + "-"*40)
        print(f"Total: {len(integrations)} integrations ({active_count} active)")
        print("="*80)
    
    def activate_integration(self, integration_id: str):
        """Activate an integration"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            UPDATE integrations 
            SET active = 1, status = 'active', last_activity = datetime('now')
            WHERE integration_id = ?
        """, (integration_id,))
        self.db.conn.commit()
        
        print(f"[OK] Activated integration: {integration_id}")
    
    def deactivate_integration(self, integration_id: str):
        """Deactivate an integration"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            UPDATE integrations 
            SET active = 0, status = 'inactive'
            WHERE integration_id = ?
        """, (integration_id,))
        self.db.conn.commit()
        
        print(f"[PAUSED] Deactivated integration: {integration_id}")
    
    def query(self, sql: str):
        """Execute a raw SQL query"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(sql)
            
            if sql.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                if results:
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Print results in table format
                    print("\n" + "-"*80)
                    print(" | ".join(columns))
                    print("-"*80)
                    
                    for row in results[:20]:  # Limit to 20 rows
                        print(" | ".join(str(val) for val in row))
                    
                    if len(results) > 20:
                        print(f"\n... and {len(results) - 20} more rows")
                else:
                    print("No results found")
            else:
                self.db.conn.commit()
                print(f"[OK] Query executed. Rows affected: {cursor.rowcount}")
                
        except sqlite3.Error as e:
            print(f"[ERROR] Query error: {e}")
    
    def export_data(self, table: str, output_file: str):
        """Export table data to JSON"""
        cursor = self.db.conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"[OK] Exported {len(data)} records from {table} to {output_file}")
            
        except sqlite3.Error as e:
            print(f"[ERROR] Export error: {e}")
    
    def cleanup(self, days: int = 7):
        """Clean up old data"""
        cursor = self.db.conn.cursor()
        
        print(f"\nCleaning up data older than {days} days...")
        
        tables_to_clean = [
            ('events', 'created_at'),
            ('metrics', 'timestamp'),
            ('communications', 'created_at'),
            ('api_calls', 'created_at')
        ]
        
        total_deleted = 0
        for table, timestamp_col in tables_to_clean:
            try:
                cursor.execute(f"""
                    DELETE FROM {table} 
                    WHERE {timestamp_col} < datetime('now', '-{days} days')
                """)
                deleted = cursor.rowcount
                total_deleted += deleted
                
                if deleted > 0:
                    print(f"  Deleted {deleted} records from {table}")
                    
            except sqlite3.Error as e:
                print(f"  Error cleaning {table}: {e}")
        
        self.db.conn.commit()
        
        # Vacuum to reclaim space
        cursor.execute("VACUUM")
        
        print(f"\n[OK] Cleanup complete. Removed {total_deleted} old records")
    
    def interactive_mode(self):
        """Interactive CLI mode"""
        print("\n" + "="*80)
        print("AI SWARM DATABASE MANAGER - Interactive Mode")
        print("="*80)
        print("\nCommands:")
        print("  status              - Show database status")
        print("  integrations        - List all integrations")
        print("  activate <id>       - Activate an integration")
        print("  deactivate <id>     - Deactivate an integration")
        print("  query <sql>         - Execute SQL query")
        print("  export <table> <file> - Export table to JSON")
        print("  cleanup <days>      - Clean up old data")
        print("  help                - Show this help")
        print("  exit                - Exit interactive mode")
        print()
        
        while True:
            try:
                command = input("\ndb> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == 'exit':
                    break
                elif cmd == 'status':
                    self.status()
                elif cmd == 'integrations':
                    self.list_integrations()
                elif cmd == 'activate' and len(parts) > 1:
                    self.activate_integration(parts[1])
                elif cmd == 'deactivate' and len(parts) > 1:
                    self.deactivate_integration(parts[1])
                elif cmd == 'query':
                    sql = ' '.join(parts[1:])
                    self.query(sql)
                elif cmd == 'export' and len(parts) > 2:
                    self.export_data(parts[1], parts[2])
                elif cmd == 'cleanup':
                    days = int(parts[1]) if len(parts) > 1 else 7
                    self.cleanup(days)
                elif cmd == 'help':
                    self.interactive_mode.__doc__
                else:
                    print(f"Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Swarm Database Manager')
    parser.add_argument('--status', action='store_true', help='Show database status')
    parser.add_argument('--integrations', action='store_true', help='List integrations')
    parser.add_argument('--activate', type=str, help='Activate an integration')
    parser.add_argument('--deactivate', type=str, help='Deactivate an integration')
    parser.add_argument('--query', type=str, help='Execute SQL query')
    parser.add_argument('--export', nargs=2, metavar=('TABLE', 'FILE'), help='Export table to JSON')
    parser.add_argument('--cleanup', type=int, default=7, help='Clean up old data (days)')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    manager = DatabaseManager()
    
    try:
        if args.status:
            manager.status()
        elif args.integrations:
            manager.list_integrations()
        elif args.activate:
            manager.activate_integration(args.activate)
        elif args.deactivate:
            manager.deactivate_integration(args.deactivate)
        elif args.query:
            manager.query(args.query)
        elif args.export:
            manager.export_data(args.export[0], args.export[1])
        elif args.cleanup:
            manager.cleanup(args.cleanup)
        elif args.interactive:
            manager.interactive_mode()
        else:
            # Default to interactive mode
            manager.interactive_mode()
            
    finally:
        manager.close()


if __name__ == "__main__":
    main()