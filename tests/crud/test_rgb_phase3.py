#!/usr/bin/env python3
# Test RGB Phase 3 - Advanced Features

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from zCLI.subsystems.zData.zData_modules.infrastructure import zTables, handle_zData
from zCLI.subsystems.zData.zData_modules.migration import ZMigrate
import sqlite3
import tempfile
import time

def create_test_schema():
    """Create a test schema for advanced RGB features."""
    return {
        "test_users": {
            "id": {"type": "TEXT", "primary_key": True},
            "username": {"type": "TEXT", "not_null": True},
            "email": {"type": "TEXT", "not_null": True},
            "age": {"type": "int"}
        },
        "test_products": {
            "id": {"type": "TEXT", "primary_key": True},
            "name": {"type": "TEXT", "not_null": True},
            "price": {"type": "int"}
        },
        "Meta": {
            "Data_Type": "sqlite",
            "Data_path": "test.db"
        }
    }

def test_rgb_decay_system():
    """Test RGB decay system."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test schema
        schema = create_test_schema()
        schema["Meta"]["Data_path"] = db_path
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "path": db_path,
            "ready": True
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        zData["cursor"] = cur
        zData["conn"] = conn
        
        # Create test tables
        zTables("test_users", schema["test_users"], cur, conn)
        zTables("test_products", schema["test_products"], cur, conn)
        
        # Insert test data with initial RGB values
        cur.execute("INSERT INTO test_users (id, username, email, age) VALUES (?, ?, ?, ?)", 
                   ("user1", "alice", "alice@example.com", 25))
        cur.execute("INSERT INTO test_products (id, name, price) VALUES (?, ?, ?)", 
                   ("prod1", "Widget", 100))
        
        # Set some initial G values to test decay properly
        cur.execute("UPDATE test_users SET weak_force_g = 10 WHERE id = 'user1'")
        cur.execute("UPDATE test_products SET weak_force_g = 5 WHERE id = 'prod1'")
        conn.commit()
        
        # Get initial RGB values
        cur.execute("SELECT weak_force_r, weak_force_g, weak_force_b FROM test_users WHERE id = 'user1'")
        initial_r, initial_g, initial_b = cur.fetchone()
        
        print(f"Initial RGB values: R={initial_r}, G={initial_g}, B={initial_b}")
        
        # Apply RGB decay
        migrator = ZMigrate()
        rows_affected = migrator._apply_rgb_decay(zData)
        
        print(f"RGB decay applied to {rows_affected} rows")
        
        # Check RGB values after decay
        cur.execute("SELECT weak_force_r, weak_force_g, weak_force_b FROM test_users WHERE id = 'user1'")
        decayed_r, decayed_g, decayed_b = cur.fetchone()
        
        print(f"RGB after decay: R={decayed_r}, G={decayed_g}, B={decayed_b}")
        
        # Verify decay occurred
        assert decayed_r < initial_r, f"R should have decayed from {initial_r} to {decayed_r}"
        # G can't decay below 0, so if initial_g was 0, it stays 0
        if initial_g > 0:
            assert decayed_g < initial_g, f"G should have decayed from {initial_g} to {decayed_g}"
        assert decayed_b == initial_b, f"B should not decay, was {initial_b}, now {decayed_b}"
        
        print("✅ RGB decay system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ RGB decay test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_health_analytics():
    """Test RGB health analytics system."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test schema
        schema = create_test_schema()
        schema["Meta"]["Data_path"] = db_path
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "path": db_path,
            "ready": True
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        zData["cursor"] = cur
        zData["conn"] = conn
        
        # Create test tables and ensure migration table exists
        zTables("test_users", schema["test_users"], cur, conn)
        zTables("test_products", schema["test_products"], cur, conn)
        
        migrator = ZMigrate()
        migrator._ensure_migrations_table(zData)
        
        # Insert test data with different RGB states
        cur.execute("INSERT INTO test_users (id, username, email, age) VALUES (?, ?, ?, ?)", 
                   ("user1", "alice", "alice@example.com", 25))
        
        # Manually set different RGB values to test analytics
        cur.execute("UPDATE test_users SET weak_force_r = 200, weak_force_g = 150, weak_force_b = 180 WHERE id = 'user1'")
        
        cur.execute("INSERT INTO test_products (id, name, price) VALUES (?, ?, ?)", 
                   ("prod1", "Widget", 100))
        
        # Set poor RGB values for products
        cur.execute("UPDATE test_products SET weak_force_r = 50, weak_force_g = 30, weak_force_b = 80 WHERE id = 'prod1'")
        
        conn.commit()
        
        # Generate health report
        health_report = migrator.get_rgb_health_report(zData)
        
        print("📊 RGB Health Report:")
        for table_name, health_data in health_report.items():
            print(f"  {table_name}:")
            print(f"    RGB: {health_data['avg_rgb']}")
            print(f"    Health Score: {health_data['health_score']}")
            print(f"    Status: {health_data['status']}")
            print(f"    Migrations: {health_data['migration_count']}")
        
        # Verify health report structure
        assert "test_users" in health_report, "test_users should be in health report"
        assert "test_products" in health_report, "test_products should be in health report"
        
        users_health = health_report["test_users"]
        products_health = health_report["test_products"]
        
        # Verify health calculations
        assert users_health["health_score"] > products_health["health_score"], "Users should have better health than products"
        assert users_health["status"] in ["EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL"], "Status should be valid"
        
        print("✅ Health analytics working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Health analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_migration_suggestions():
    """Test migration suggestions based on RGB health."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test schema
        schema = create_test_schema()
        schema["Meta"]["Data_path"] = db_path
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "path": db_path,
            "ready": True
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        zData["cursor"] = cur
        zData["conn"] = conn
        
        # Create test tables and ensure migration table exists
        zTables("test_users", schema["test_users"], cur, conn)
        zTables("test_products", schema["test_products"], cur, conn)
        
        migrator = ZMigrate()
        migrator._ensure_migrations_table(zData)
        
        # Insert test data with poor RGB values to trigger suggestions
        cur.execute("INSERT INTO test_users (id, username, email, age) VALUES (?, ?, ?, ?)", 
                   ("user1", "alice", "alice@example.com", 25))
        
        # Set poor RGB values to trigger suggestions
        cur.execute("UPDATE test_users SET weak_force_r = 20, weak_force_g = 10, weak_force_b = 50 WHERE id = 'user1'")
        
        cur.execute("INSERT INTO test_products (id, name, price) VALUES (?, ?, ?)", 
                   ("prod1", "Widget", 100))
        
        # Set moderate RGB values
        cur.execute("UPDATE test_products SET weak_force_r = 100, weak_force_g = 80, weak_force_b = 60 WHERE id = 'prod1'")
        
        conn.commit()
        
        # Generate migration suggestions
        suggestions = migrator.suggest_migrations_for_rgb_health(zData, threshold=0.3)
        
        print("💡 Migration Suggestions:")
        for suggestion in suggestions:
            print(f"  Table: {suggestion['table']}")
            print(f"    Issue: {suggestion['issue']}")
            print(f"    RGB State: {suggestion['rgb_state']}")
            print(f"    Priority: {suggestion['priority']}")
            print(f"    Suggestions: {suggestion['suggestions']}")
            print()
        
        # Verify suggestions were generated
        assert len(suggestions) > 0, "Should have generated migration suggestions"
        
        # Check that test_users has suggestions (due to poor RGB values)
        users_suggestions = [s for s in suggestions if s["table"] == "test_users"]
        assert len(users_suggestions) > 0, "test_users should have suggestions due to poor health"
        
        print("✅ Migration suggestions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Migration suggestions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_comprehensive_rgb_system():
    """Test the complete RGB system with all Phase 3 features."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create test schema
        schema = create_test_schema()
        schema["Meta"]["Data_path"] = db_path
        
        # Create zData object
        zData = {
            "type": "sqlite",
            "path": db_path,
            "ready": True
        }
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        zData["cursor"] = cur
        zData["conn"] = conn
        
        # Create test tables
        zTables("test_users", schema["test_users"], cur, conn)
        zTables("test_products", schema["test_products"], cur, conn)
        
        migrator = ZMigrate()
        migrator._ensure_migrations_table(zData)
        
        # Insert test data
        cur.execute("INSERT INTO test_users (id, username, email, age) VALUES (?, ?, ?, ?)", 
                   ("user1", "alice", "alice@example.com", 25))
        cur.execute("INSERT INTO test_products (id, name, price) VALUES (?, ?, ?)", 
                   ("prod1", "Widget", 100))
        conn.commit()
        
        print("🌅 Initial state:")
        health_report = migrator.get_rgb_health_report(zData)
        for table_name, health_data in health_report.items():
            print(f"  {table_name}: RGB={health_data['avg_rgb']}, Health={health_data['health_score']:.3f}, Status={health_data['status']}")
        
        # Apply some ALTER TABLE operations to test migration tracking
        print("\n🔧 Applying ALTER TABLE operations...")
        
        # Drop column
        drop_request = {
            "action": "alter_table",
            "table": "test_users",
            "operation": "drop_column",
            "column": "age"
        }
        
        zCRUD_Preped = {
            "zRequest": drop_request,
            "zForm": schema,
            "walker": None
        }
        
        result = handle_zData(zCRUD_Preped)
        assert result, "DROP COLUMN should succeed"
        
        print("✅ DROP COLUMN applied")
        
        # Apply RGB decay
        print("\n⏰ Applying RGB decay...")
        rows_affected = migrator._apply_rgb_decay(zData)
        print(f"Decay applied to {rows_affected} rows")
        
        # Generate final health report
        print("\n🌆 Final state:")
        health_report = migrator.get_rgb_health_report(zData)
        for table_name, health_data in health_report.items():
            print(f"  {table_name}: RGB={health_data['avg_rgb']}, Health={health_data['health_score']:.3f}, Status={health_data['status']}")
        
        # Generate migration suggestions
        print("\n💡 Migration suggestions:")
        suggestions = migrator.suggest_migrations_for_rgb_health(zData)
        for suggestion in suggestions:
            print(f"  {suggestion['table']}: {suggestion['issue']} (Priority: {suggestion['priority']})")
        
        # Verify comprehensive system works
        assert len(health_report) >= 2, "Should have health data for both tables"
        assert any(h["migration_count"] > 0 for h in health_report.values()), "Some tables should have migration history"
        
        print("\n✅ Comprehensive RGB system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive RGB system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def main():
    """Run all RGB Phase 3 tests."""
    print("🧪 Testing RGB Phase 3 - Advanced Features")
    print("=" * 60)
    
    success1 = test_rgb_decay_system()
    print("\n" + "=" * 60)
    
    success2 = test_health_analytics()
    print("\n" + "=" * 60)
    
    success3 = test_migration_suggestions()
    print("\n" + "=" * 60)
    
    success4 = test_comprehensive_rgb_system()
    
    if success1 and success2 and success3 and success4:
        print("\n🎉 Phase 3 tests passed!")
        print("✅ RGB decay system operational!")
        print("✅ Health analytics working!")
        print("✅ Migration suggestions functional!")
        print("🌈 Complete quantum weak nuclear force system operational!")
        print("🚀 zCLI v1.3.0 ready for release!")
        return True
    else:
        print("\n❌ Phase 3 tests failed!")
        print("Check the implementation and try again")
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
