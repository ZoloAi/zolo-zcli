#!/usr/bin/env python3
# tests/fixtures.py — Test Database Setup and Teardown
# ───────────────────────────────────────────────────────────────

"""
Test Fixtures for zCLI Test Suite

Provides database setup, teardown, and utility functions for tests.
Creates isolated test database from schema.test.yaml.
"""

import os
import sqlite3
import yaml
from pathlib import Path


# Test database location
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_data.db")
TEST_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schemas/test_schema.yaml")


def setup_test_database():
    """
    Create test database from test_schema.yaml.
    
    Returns:
        str: Path to test database
    """
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"[*] Removed existing test database")
    
    # Load test schema
    with open(TEST_SCHEMA_PATH, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Create database and tables
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    
    # Create tables from schema
    tables_created = []
    
    # Create zUsers table
    if 'zUsers' in schema:
        cur.execute("""
            CREATE TABLE zUsers (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'zUser',
                created_at TEXT NOT NULL
            )
        """)
        tables_created.append('zUsers')
    
    # Create zApps table
    if 'zApps' in schema:
        cur.execute("""
            CREATE TABLE zApps (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL DEFAULT 'web',
                version TEXT DEFAULT '1.0.0',
                created_at TEXT NOT NULL
            )
        """)
        tables_created.append('zApps')
    
    # Create zUserApps table (join table)
    if 'zUserApps' in schema:
        cur.execute("""
            CREATE TABLE zUserApps (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                app_id TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                FOREIGN KEY (user_id) REFERENCES zUsers(id) ON DELETE CASCADE,
                FOREIGN KEY (app_id) REFERENCES zApps(id) ON DELETE CASCADE
            )
        """)
        tables_created.append('zUserApps')
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Test database created: {TEST_DB_PATH}")
    print(f"     Tables created: {', '.join(tables_created)}")
    
    return TEST_DB_PATH


def teardown_test_database():
    """
    Remove test database after tests complete.
    """
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"[OK] Test database removed: {TEST_DB_PATH}")
    else:
        print(f"[*] No test database to remove")


def get_test_db_path():
    """
    Get path to test database.
    
    Returns:
        str: Path to test database
    """
    return TEST_DB_PATH


def get_test_schema_path():
    """
    Get path to test schema.
    
    Returns:
        str: Path to test schema YAML
    """
    return TEST_SCHEMA_PATH


def verify_table_exists(table_name):
    """
    Verify a table exists in the test database.
    
    Args:
        table_name: Name of table to check
        
    Returns:
        bool: True if table exists
    """
    if not os.path.exists(TEST_DB_PATH):
        return False
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    exists = cur.fetchone() is not None
    conn.close()
    
    return exists


def count_rows(table_name):
    """
    Count rows in a table.
    
    Args:
        table_name: Name of table
        
    Returns:
        int: Number of rows
    """
    if not os.path.exists(TEST_DB_PATH):
        return 0
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except sqlite3.OperationalError:
        conn.close()
        return 0


def insert_test_data(table_name, data):
    """
    Insert test data into a table.
    
    Args:
        table_name: Name of table
        data: Dict of column: value pairs
        
    Returns:
        bool: True if successful
    """
    if not os.path.exists(TEST_DB_PATH):
        return False
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    
    columns = list(data.keys())
    placeholders = ['?' for _ in columns]
    values = list(data.values())
    
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    
    try:
        cur.execute(sql, values)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[X] Insert failed: {e}")
        conn.close()
        return False


def clear_table(table_name):
    """
    Clear all rows from a table.
    
    Args:
        table_name: Name of table to clear
        
    Returns:
        int: Number of rows deleted
    """
    if not os.path.exists(TEST_DB_PATH):
        return 0
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute(f"DELETE FROM {table_name}")
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return deleted
    except Exception as e:
        print(f"[X] Clear failed: {e}")
        conn.close()
        return 0


# Convenience context manager for test database
class TestDatabase:
    """Context manager for test database setup/teardown."""
    
    def __enter__(self):
        """Setup test database."""
        self.db_path = setup_test_database()
        return self.db_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Teardown test database."""
        teardown_test_database()
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Test the fixtures
    print("Testing database fixtures...")
    print("=" * 70)
    
    with TestDatabase() as db_path:
        print(f"\n[*] Database created: {db_path}")
        
        # Verify tables
        print("\n[*] Verifying tables...")
        for table in ['zUsers', 'zApps', 'zUserApps']:
            exists = verify_table_exists(table)
            status = "[OK]" if exists else "[X]"
            print(f"     {status} Table '{table}' exists: {exists}")
        
        # Test insert
        print("\n[*] Testing insert...")
        success = insert_test_data('zApps', {
            'id': 'zA_test',
            'name': 'TestApp',
            'type': 'web',
            'version': '1.0.0',
            'created_at': '2025-10-02T00:00:00'
        })
        print(f"     [OK] Insert: {success}")
        
        # Test count
        print("\n[*] Testing count...")
        count = count_rows('zApps')
        print(f"     [OK] Row count: {count}")
        
        # Test clear
        print("\n[*] Testing clear...")
        deleted = clear_table('zApps')
        print(f"     [OK] Rows deleted: {deleted}")
    
    print("\n[OK] Fixtures test complete!")
    print("=" * 70)

