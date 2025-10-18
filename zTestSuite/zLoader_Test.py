#!/usr/bin/env python3
# zTestSuite/zLoader_Test.py

"""
Comprehensive test suite for zLoader subsystem.
Tests file loading, caching (system, pinned, schema), and cache orchestration.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import tempfile

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zLoader import zLoader
from zCLI.subsystems.zLoader.zLoader_modules import (
    CacheOrchestrator, SystemCache, PinnedCache, SchemaCache
)


class TestzLoaderInitialization(unittest.TestCase):
    """Test zLoader initialization and basic setup."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zparser.zPath_decoder = Mock(return_value=("/path/to/file", "file.json"))
        self.mock_zcli.zparser.identify_zFile = Mock(return_value=("/path/to/file.json", ".json"))
        self.mock_zcli.zparser.parse_file_content = Mock(return_value={"test": "data"})

    def test_initialization_with_valid_zcli(self):
        """Test zLoader initializes correctly with valid zCLI instance."""
        loader = zLoader(self.mock_zcli)
        
        self.assertIsNotNone(loader)
        self.assertEqual(loader.zcli, self.mock_zcli)
        self.assertEqual(loader.zSession, self.mock_zcli.session)
        self.assertEqual(loader.logger, self.mock_zcli.logger)
        self.assertEqual(loader.mycolor, "LOADER")
        self.assertIsInstance(loader.cache, CacheOrchestrator)

    def test_ready_message_displayed(self):
        """Test ready message is displayed on initialization."""
        loader = zLoader(self.mock_zcli)
        
        # Should call zDeclare for ready message
        self.mock_zcli.display.zDeclare.assert_called_with(
            "zLoader Ready", color="LOADER", indent=0, style="full"
        )


class TestSystemCache(unittest.TestCase):
    """Test SystemCache functionality."""

    def setUp(self):
        """Set up test session and logger."""
        self.session = {"zCache": {}}
        self.logger = Mock()
        self.cache = SystemCache(self.session, self.logger, max_size=3)

    def test_initialization(self):
        """Test SystemCache initializes correctly."""
        self.assertIn("system_cache", self.session["zCache"])
        self.assertEqual(self.cache.max_size, 3)

    def test_set_and_get(self):
        """Test setting and getting cache entries."""
        result = self.cache.set("key1", "value1")
        self.assertEqual(result, "value1")
        
        retrieved = self.cache.get("key1")
        self.assertEqual(retrieved, "value1")

    def test_cache_miss(self):
        """Test cache miss returns default."""
        result = self.cache.get("nonexistent", default="default_value")
        self.assertEqual(result, "default_value")

    def test_lru_eviction(self):
        """Test LRU eviction when max_size is exceeded."""
        # Add 3 items (max_size)
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Add 4th item - should evict key1
        self.cache.set("key4", "value4")
        
        # key1 should be evicted
        self.assertIsNone(self.cache.get("key1"))
        self.assertEqual(self.cache.get("key4"), "value4")

    def test_mtime_tracking(self):
        """Test mtime tracking for file freshness."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            filepath = f.name
        
        try:
            # Set with filepath
            self.cache.set("key1", "value1", filepath=filepath)
            
            # Get should succeed with matching mtime
            result = self.cache.get("key1", filepath=filepath)
            self.assertEqual(result, "value1")
        finally:
            Path(filepath).unlink()

    def test_invalidate(self):
        """Test cache invalidation."""
        self.cache.set("key1", "value1")
        self.cache.invalidate("key1")
        
        result = self.cache.get("key1")
        self.assertIsNone(result)

    def test_clear_all(self):
        """Test clearing entire cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_clear_pattern(self):
        """Test clearing cache by pattern."""
        self.cache.set("test:key1", "value1")
        self.cache.set("test:key2", "value2")
        self.cache.set("other:key3", "value3")
        
        self.cache.clear(pattern="test*")
        
        self.assertIsNone(self.cache.get("test:key1"))
        self.assertIsNone(self.cache.get("test:key2"))
        self.assertEqual(self.cache.get("other:key3"), "value3")

    def test_get_stats(self):
        """Test cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")
        self.cache.get("nonexistent")
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertIn("hit_rate", stats)


class TestPinnedCache(unittest.TestCase):
    """Test PinnedCache functionality."""

    def setUp(self):
        """Set up test session and logger."""
        self.session = {"zCache": {}}
        self.logger = Mock()
        self.cache = PinnedCache(self.session, self.logger)

    def test_initialization(self):
        """Test PinnedCache initializes correctly."""
        self.assertIn("pinned_cache", self.session["zCache"])

    def test_load_alias(self):
        """Test loading an alias."""
        schema = {"test": "schema"}
        result = self.cache.load_alias("myalias", schema, "@models.user")
        
        self.assertEqual(result, schema)
        self.assertTrue(self.cache.has_alias("myalias"))

    def test_get_alias(self):
        """Test getting an alias."""
        schema = {"test": "schema"}
        self.cache.load_alias("myalias", schema, "@models.user")
        
        retrieved = self.cache.get_alias("myalias")
        self.assertEqual(retrieved, schema)

    def test_get_nonexistent_alias(self):
        """Test getting non-existent alias returns None."""
        result = self.cache.get_alias("nonexistent")
        self.assertIsNone(result)

    def test_has_alias(self):
        """Test checking if alias exists."""
        self.assertFalse(self.cache.has_alias("myalias"))
        
        self.cache.load_alias("myalias", {"test": "schema"}, "@models.user")
        
        self.assertTrue(self.cache.has_alias("myalias"))

    def test_remove_alias(self):
        """Test removing an alias."""
        self.cache.load_alias("myalias", {"test": "schema"}, "@models.user")
        
        result = self.cache.remove_alias("myalias")
        
        self.assertTrue(result)
        self.assertFalse(self.cache.has_alias("myalias"))

    def test_remove_nonexistent_alias(self):
        """Test removing non-existent alias."""
        result = self.cache.remove_alias("nonexistent")
        self.assertFalse(result)

    def test_list_aliases(self):
        """Test listing all aliases."""
        self.cache.load_alias("alias1", {"test": "schema1"}, "@models.user")
        self.cache.load_alias("alias2", {"test": "schema2"}, "@models.product")
        
        aliases = self.cache.list_aliases()
        
        self.assertEqual(len(aliases), 2)
        alias_names = [a["name"] for a in aliases]
        self.assertIn("alias1", alias_names)
        self.assertIn("alias2", alias_names)

    def test_get_info(self):
        """Test getting alias metadata."""
        self.cache.load_alias("myalias", {"test": "schema"}, "@models.user")
        
        info = self.cache.get_info("myalias")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "myalias")
        self.assertEqual(info["zpath"], "@models.user")
        self.assertIn("age", info)

    def test_clear_all(self):
        """Test clearing all aliases."""
        self.cache.load_alias("alias1", {"test": "schema1"}, "@models.user")
        self.cache.load_alias("alias2", {"test": "schema2"}, "@models.product")
        
        count = self.cache.clear()
        
        self.assertEqual(count, 2)
        self.assertEqual(len(self.cache.list_aliases()), 0)

    def test_clear_pattern(self):
        """Test clearing aliases by pattern."""
        self.cache.load_alias("user_alias", {"test": "schema1"}, "@models.user")
        self.cache.load_alias("user_profile", {"test": "schema2"}, "@models.profile")
        self.cache.load_alias("product_alias", {"test": "schema3"}, "@models.product")
        
        count = self.cache.clear(pattern="user*")
        
        self.assertEqual(count, 2)
        self.assertFalse(self.cache.has_alias("user_alias"))
        self.assertFalse(self.cache.has_alias("user_profile"))
        self.assertTrue(self.cache.has_alias("product_alias"))


class TestSchemaCache(unittest.TestCase):
    """Test SchemaCache functionality."""

    def setUp(self):
        """Set up test session and logger."""
        self.session = {"zCache": {}}
        self.logger = Mock()
        self.cache = SchemaCache(self.session, self.logger)

    def test_initialization(self):
        """Test SchemaCache initializes correctly."""
        self.assertIn("schema_cache", self.session["zCache"])
        self.assertEqual(len(self.cache.connections), 0)

    def test_set_and_get_connection(self):
        """Test setting and getting connections."""
        mock_handler = Mock()
        mock_handler.schema = {"Meta": {"Data_Type": "postgresql"}}
        
        self.cache.set_connection("mydb", mock_handler)
        
        retrieved = self.cache.get_connection("mydb")
        self.assertEqual(retrieved, mock_handler)

    def test_has_connection(self):
        """Test checking if connection exists."""
        self.assertFalse(self.cache.has_connection("mydb"))
        
        mock_handler = Mock()
        mock_handler.schema = {"Meta": {"Data_Type": "postgresql"}}
        self.cache.set_connection("mydb", mock_handler)
        
        self.assertTrue(self.cache.has_connection("mydb"))

    def test_disconnect(self):
        """Test disconnecting a connection."""
        mock_handler = Mock()
        mock_handler.schema = {"Meta": {"Data_Type": "postgresql"}}
        mock_handler.disconnect = Mock()
        
        self.cache.set_connection("mydb", mock_handler)
        self.cache.disconnect("mydb")
        
        mock_handler.disconnect.assert_called_once()
        self.assertFalse(self.cache.has_connection("mydb"))

    def test_list_connections(self):
        """Test listing all connections."""
        mock_handler1 = Mock()
        mock_handler1.schema = {"Meta": {"Data_Type": "postgresql"}}
        mock_handler2 = Mock()
        mock_handler2.schema = {"Meta": {"Data_Type": "mysql"}}
        
        self.cache.set_connection("db1", mock_handler1)
        self.cache.set_connection("db2", mock_handler2)
        
        connections = self.cache.list_connections()
        
        self.assertEqual(len(connections), 2)

    def test_clear(self):
        """Test clearing all connections."""
        mock_handler = Mock()
        mock_handler.schema = {"Meta": {"Data_Type": "postgresql"}}
        mock_handler.disconnect = Mock()
        
        self.cache.set_connection("db1", mock_handler)
        self.cache.clear()
        
        self.assertEqual(len(self.cache.connections), 0)


class TestCacheOrchestrator(unittest.TestCase):
    """Test CacheOrchestrator functionality."""

    def setUp(self):
        """Set up test session and logger."""
        self.session = {"zCache": {}}
        self.logger = Mock()
        self.orchestrator = CacheOrchestrator(self.session, self.logger)

    def test_initialization(self):
        """Test CacheOrchestrator initializes all tiers."""
        self.assertIsInstance(self.orchestrator.system_cache, SystemCache)
        self.assertIsInstance(self.orchestrator.pinned_cache, PinnedCache)
        self.assertIsInstance(self.orchestrator.schema_cache, SchemaCache)

    def test_system_cache_routing(self):
        """Test routing to system cache."""
        self.orchestrator.set("key1", "value1", cache_type="system")
        result = self.orchestrator.get("key1", cache_type="system")
        
        self.assertEqual(result, "value1")

    def test_pinned_cache_routing(self):
        """Test routing to pinned cache."""
        schema = {"test": "schema"}
        self.orchestrator.set("myalias", schema, cache_type="pinned", zpath="@models.user")
        result = self.orchestrator.get("myalias", cache_type="pinned")
        
        self.assertEqual(result, schema)

    def test_schema_cache_routing(self):
        """Test routing to schema cache."""
        mock_handler = Mock()
        mock_handler.schema = {"Meta": {"Data_Type": "postgresql"}}
        
        self.orchestrator.set("mydb", mock_handler, cache_type="schema")
        result = self.orchestrator.get("mydb", cache_type="schema")
        
        self.assertEqual(result, mock_handler)

    def test_has_system(self):
        """Test checking existence in system cache."""
        self.orchestrator.set("key1", "value1", cache_type="system")
        
        self.assertTrue(self.orchestrator.has("key1", cache_type="system"))
        self.assertFalse(self.orchestrator.has("nonexistent", cache_type="system"))

    def test_has_pinned(self):
        """Test checking existence in pinned cache."""
        self.orchestrator.set("myalias", {"test": "schema"}, cache_type="pinned", zpath="@models.user")
        
        self.assertTrue(self.orchestrator.has("myalias", cache_type="pinned"))
        self.assertFalse(self.orchestrator.has("nonexistent", cache_type="pinned"))

    def test_clear_system(self):
        """Test clearing system cache."""
        self.orchestrator.set("key1", "value1", cache_type="system")
        self.orchestrator.clear(cache_type="system")
        
        result = self.orchestrator.get("key1", cache_type="system")
        self.assertIsNone(result)

    def test_clear_all(self):
        """Test clearing all caches."""
        self.orchestrator.set("key1", "value1", cache_type="system")
        self.orchestrator.set("alias1", {"test": "schema"}, cache_type="pinned", zpath="@models.user")
        
        self.orchestrator.clear(cache_type="all")
        
        self.assertIsNone(self.orchestrator.get("key1", cache_type="system"))
        self.assertIsNone(self.orchestrator.get("alias1", cache_type="pinned"))

    def test_get_stats_all(self):
        """Test getting stats for all caches."""
        stats = self.orchestrator.get_stats(cache_type="all")
        
        self.assertIn("system_cache", stats)
        self.assertIn("pinned_cache", stats)
        self.assertIn("schema_cache", stats)

    def test_get_stats_system(self):
        """Test getting stats for system cache only."""
        stats = self.orchestrator.get_stats(cache_type="system")
        
        self.assertIn("system_cache", stats)
        self.assertNotIn("pinned_cache", stats)

    def test_unknown_cache_type_get(self):
        """Test handling unknown cache type in get."""
        result = self.orchestrator.get("key1", cache_type="unknown")
        self.assertIsNone(result)

    def test_unknown_cache_type_set(self):
        """Test handling unknown cache type in set."""
        result = self.orchestrator.set("key1", "value1", cache_type="unknown")
        self.assertEqual(result, "value1")


class TestzLoaderFileLoading(unittest.TestCase):
    """Test zLoader file loading functionality."""

    def setUp(self):
        """Set up mock zCLI instance for testing."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zMode": "Terminal", "zWorkspace": "/test/workspace"}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zparser = Mock()

    @patch('zCLI.subsystems.zLoader.zLoader_modules.loader_io.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_file_with_cache_miss(self, mock_file):
        """Test loading file when not in cache."""
        self.mock_zcli.zparser.zPath_decoder = Mock(return_value=("/path/to/file", "file.json"))
        self.mock_zcli.zparser.identify_zFile = Mock(return_value=("/path/to/file.json", ".json"))
        self.mock_zcli.zparser.parse_file_content = Mock(return_value={"test": "data"})
        
        loader = zLoader(self.mock_zcli)
        result = loader.handle("@models.user")
        
        self.assertEqual(result, {"test": "data"})
        self.mock_zcli.zparser.parse_file_content.assert_called_once()

    @patch('zCLI.subsystems.zLoader.zLoader_modules.loader_io.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_file_with_cache_hit(self, mock_file):
        """Test loading file when already in cache."""
        self.mock_zcli.zparser.zPath_decoder = Mock(return_value=("/path/to/file", "file.json"))
        self.mock_zcli.zparser.identify_zFile = Mock(return_value=("/path/to/file.json", ".json"))
        self.mock_zcli.zparser.parse_file_content = Mock(return_value={"test": "data"})
        
        loader = zLoader(self.mock_zcli)
        
        # First load - cache miss
        result1 = loader.handle("@models.user")
        
        # Second load - cache hit
        result2 = loader.handle("@models.user")
        
        self.assertEqual(result1, result2)
        # parse_file_content should only be called once
        self.assertEqual(self.mock_zcli.zparser.parse_file_content.call_count, 1)


def run_tests(verbose=False):
    """Run all zLoader tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzLoaderInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemCache))
    suite.addTests(loader.loadTestsFromTestCase(TestPinnedCache))
    suite.addTests(loader.loadTestsFromTestCase(TestSchemaCache))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestzLoaderFileLoading))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

