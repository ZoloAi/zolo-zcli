# zLoader: The File Loading & Caching Subsystem

## **Overview**
- **zLoader** is **zCLI**'s intelligent file loading and multi-tier caching subsystem
- Provides file loading, three-tier caching (system, pinned, schema), and cache orchestration
- Initializes after zParser, providing cached file access to all subsystems

## **Architecture**

### **Layer 1 Loading Services**
**zLoader** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm, zDisplay, zParser)
- Provides cached file loading to all other subsystems
- Depends on zParser for path resolution and file parsing
- Establishes the caching foundation for zCLI

### **Orchestrator Pattern Design**
```
zLoader/
├── __init__.py                       # Module exports
├── zLoader.py                        # Main loader class
└── zLoader_modules/
    ├── cache_orchestrator.py         # Routes requests to cache tiers
    ├── system_cache.py               # LRU cache for UI/config files
    ├── pinned_cache.py               # User-loaded aliases (no eviction)
    ├── schema_cache.py               # Active database connections
    └── loader_io.py                  # File I/O operations
```

**Note:** Clean orchestrator pattern with no cross-module dependencies between cache classes.

---

## **Core Features**

### **1. Three-Tier Caching**
- **System Cache**: LRU eviction, mtime tracking, automatic invalidation
- **Pinned Cache**: User-loaded aliases, never auto-evicts, highest priority
- **Schema Cache**: Active database connections, in-memory only

### **2. Intelligent File Loading**
- **Path Resolution**: Delegates to zParser for symbol-based paths
- **Format Detection**: Auto-detects JSON/YAML file types
- **Cache-First**: Checks cache before disk I/O
- **Freshness Tracking**: mtime-based invalidation for system cache

### **3. Schema Handling**
- **No Caching**: Schema files always loaded fresh
- **Connection Management**: Active database connections in schema cache
- **Transaction Support**: Begin/commit/rollback operations

### **4. Cache Orchestration**
- **Unified Interface**: Single API for all cache tiers
- **Type-Based Routing**: Automatic routing to correct cache
- **Statistics**: Per-tier and aggregate cache statistics

---

## **Cache Tiers**

### **System Cache (Tier 1)**

**Purpose:** Cache UI and config files with LRU eviction

**Features:**
- LRU eviction when max_size exceeded
- mtime tracking for file freshness
- Automatic invalidation on file changes
- Pattern-based clearing

**Usage:**
```python
# Automatic via zLoader
result = zcli.loader.handle("@ui.main")  # Cached in system cache

# Direct access
zcli.loader.cache.set("key", value, cache_type="system", filepath="/path/to/file")
cached = zcli.loader.cache.get("key", cache_type="system", filepath="/path/to/file")
```

**Configuration:**
- Default max_size: 100 entries
- Eviction: Least Recently Used (LRU)
- Storage: Session-based (`session["zCache"]["system_cache"]`)

### **Pinned Cache (Tier 2)**

**Purpose:** Store user-loaded aliases (never auto-evicts)

**Features:**
- No automatic eviction
- User-controlled lifecycle
- Metadata tracking (zpath, type, loaded_at, age)
- Pattern-based removal

**Usage:**
```python
# Load alias via command
# load @models.user --as mymodel

# Access via cache
schema = zcli.loader.cache.get("mymodel", cache_type="pinned")

# List all aliases
aliases = zcli.loader.cache.pinned_cache.list_aliases()

# Remove alias
zcli.loader.cache.pinned_cache.remove_alias("mymodel")
```

**Storage:** Session-based (`session["zCache"]["pinned_cache"]`)

### **Schema Cache (Tier 3)**

**Purpose:** Manage active database connections

**Features:**
- In-memory connection storage (not serialized)
- Transaction support (begin/commit/rollback)
- Connection metadata in session
- Automatic cleanup on disconnect

**Usage:**
```python
# Set connection (typically done by zWizard)
zcli.loader.cache.set("mydb", handler, cache_type="schema")

# Get connection
handler = zcli.loader.cache.get("mydb", cache_type="schema")

# Transaction management
zcli.loader.cache.schema_cache.begin_transaction("mydb")
zcli.loader.cache.schema_cache.commit_transaction("mydb")
zcli.loader.cache.schema_cache.rollback_transaction("mydb")

# Disconnect
zcli.loader.cache.schema_cache.disconnect("mydb")
```

**Storage:** 
- Connections: In-memory only (`connections` dict)
- Metadata: Session-based (`session["zCache"]["schema_cache"]`)

---

## **File Loading**

### **Basic Loading**

```python
# Load file via zLoader
result = zcli.loader.handle("@ui.main")
# 1. Resolves path via zParser
# 2. Checks system cache
# 3. Loads from disk if cache miss
# 4. Parses via zParser
# 5. Caches result
# 6. Returns parsed data
```

### **Cache Behavior**

**UI/Config Files (Cached):**
```python
result = zcli.loader.handle("@ui.main")
# ✅ Cached in system cache
# ✅ Subsequent loads return cached version
# ✅ Auto-invalidated if file changes (mtime)
```

**Schema Files (Not Cached):**
```python
result = zcli.loader.handle("@schemas.user")
# ❌ NOT cached - loaded fresh each time
# ✅ Ensures latest schema structure
```

### **Cache Keys**

System cache uses dotted path as key:
```python
# For: zcli.loader.handle("@ui.main")
cache_key = "parsed:@.main"  # zPath-based key

# For: zcli.loader.handle("@models.user.schema")
cache_key = "parsed:@models.user.schema"
```

---

## **Cache Operations**

### **Get from Cache**

```python
# System cache with freshness check
result = zcli.loader.cache.get(
    "parsed:@.main", 
    cache_type="system",
    filepath="/path/to/file.json"
)

# Pinned cache (alias)
schema = zcli.loader.cache.get("myalias", cache_type="pinned")

# Schema cache (connection)
handler = zcli.loader.cache.get("mydb", cache_type="schema")
```

### **Set in Cache**

```python
# System cache with mtime tracking
zcli.loader.cache.set(
    "parsed:@.main",
    {"data": "value"},
    cache_type="system",
    filepath="/path/to/file.json"
)

# Pinned cache (alias)
zcli.loader.cache.set(
    "myalias",
    schema_data,
    cache_type="pinned",
    zpath="@models.user"
)

# Schema cache (connection)
zcli.loader.cache.set("mydb", handler, cache_type="schema")
```

### **Check Existence**

```python
# Check if key exists
exists = zcli.loader.cache.has("key", cache_type="system")
has_alias = zcli.loader.cache.has("myalias", cache_type="pinned")
has_conn = zcli.loader.cache.has("mydb", cache_type="schema")
```

### **Clear Cache**

```python
# Clear specific tier
zcli.loader.cache.clear(cache_type="system")
zcli.loader.cache.clear(cache_type="pinned")
zcli.loader.cache.clear(cache_type="schema")

# Clear all tiers
zcli.loader.cache.clear(cache_type="all")

# Clear by pattern
zcli.loader.cache.clear(cache_type="system", pattern="ui*")
zcli.loader.cache.clear(cache_type="pinned", pattern="user*")
```

### **Get Statistics**

```python
# All cache tiers
stats = zcli.loader.cache.get_stats(cache_type="all")
# Returns: {
#     "system_cache": {...},
#     "pinned_cache": {...},
#     "schema_cache": {...}
# }

# Specific tier
system_stats = zcli.loader.cache.get_stats(cache_type="system")
# Returns: {
#     "namespace": "system_cache",
#     "size": 42,
#     "max_size": 100,
#     "hits": 150,
#     "misses": 20,
#     "hit_rate": "88.2%",
#     "evictions": 5,
#     "invalidations": 3
# }
```

---

## **System Cache Details**

### **LRU Eviction**

```python
# Max size: 100 entries
cache = SystemCache(session, logger, max_size=100)

# When 101st item added, oldest (least recently used) is evicted
cache.set("key1", "value1")  # Entry 1
# ... 99 more entries ...
cache.set("key100", "value100")  # Entry 100
cache.set("key101", "value101")  # Entry 101 - evicts key1
```

### **mtime Tracking**

```python
# Set with filepath - tracks mtime
cache.set("key", value, filepath="/path/to/file.json")

# Get with filepath - checks freshness
result = cache.get("key", filepath="/path/to/file.json")
# If file changed (mtime different), returns None and invalidates
```

### **Manual Operations**

```python
# Invalidate specific key
cache.invalidate("key")

# Clear all
cache.clear()

# Clear by pattern
cache.clear(pattern="ui*")  # Clears all keys containing "ui"

# Get statistics
stats = cache.get_stats()
```

---

## **Pinned Cache Details**

### **Alias Management**

```python
# Load alias
cache.load_alias("mymodel", schema_data, "@models.user")

# Get alias
schema = cache.get_alias("mymodel")

# Check existence
exists = cache.has_alias("mymodel")

# Get metadata
info = cache.get_info("mymodel")
# Returns: {
#     "name": "mymodel",
#     "zpath": "@models.user",
#     "type": "schema",
#     "loaded_at": 1234567890,
#     "age": 3600,
#     "size": 1024
# }

# List all aliases
aliases = cache.list_aliases()

# Remove alias
cache.remove_alias("mymodel")
```

### **Pattern Clearing**

```python
# Clear matching aliases
count = cache.clear(pattern="user*")
# Removes: user_alias, user_profile, etc.

# Clear all
count = cache.clear()
```

---

## **Schema Cache Details**

### **Connection Management**

```python
# Set connection
cache.set_connection("mydb", handler)

# Get connection
handler = cache.get_connection("mydb")

# Check existence
exists = cache.has_connection("mydb")

# List all connections
connections = cache.list_connections()
# Returns: [{
#     "alias": "mydb",
#     "backend": "postgresql",
#     "connected_at": 1234567890,
#     "age": 3600,
#     "transaction_active": False
# }]

# Disconnect
cache.disconnect("mydb")

# Clear all
cache.clear()
```

### **Transaction Support**

```python
# Begin transaction
cache.begin_transaction("mydb")

# Commit transaction
cache.commit_transaction("mydb")

# Rollback transaction
cache.rollback_transaction("mydb")

# Check if transaction active
is_active = cache.is_transaction_active("mydb")
```

---

## **API Reference**

### **zLoader Methods**

#### `handle(zPath=None)`
Main entry point for file loading.

**Parameters:**
- `zPath`: Dotted path to file (e.g., `"@ui.main"`)

**Returns:** Parsed file content (dict)

**Behavior:**
1. Resolves path via zParser
2. Checks if schema file (skips cache)
3. Checks system cache for hit
4. Loads from disk if cache miss
5. Parses via zParser
6. Caches result (if not schema)
7. Returns parsed data

### **CacheOrchestrator Methods**

#### `get(key, cache_type="system", **kwargs)`
Get value from specified cache tier.

#### `set(key, value, cache_type="system", **kwargs)`
Set value in specified cache tier.

#### `has(key, cache_type="system")`
Check if key exists in specified cache tier.

#### `clear(cache_type="all", pattern=None)`
Clear cache entries in specified tier(s).

#### `get_stats(cache_type="all")`
Get cache statistics for specified tier(s).

### **SystemCache Methods**

#### `get(key, filepath=None, default=None)`
Get value with optional freshness check.

#### `set(key, value, filepath=None)`
Set value with optional mtime tracking.

#### `invalidate(key)`
Remove specific key from cache.

#### `clear(pattern=None)`
Clear cache entries (optionally by pattern).

#### `get_stats()`
Return cache statistics.

### **PinnedCache Methods**

#### `load_alias(alias_name, parsed_schema, zpath)`
Load alias from `load --as` command.

#### `get_alias(alias_name)`
Get alias by name.

#### `has_alias(alias_name)`
Check if alias exists.

#### `remove_alias(alias_name)`
Remove specific alias.

#### `list_aliases()`
List all aliases.

#### `get_info(alias_name)`
Get metadata about an alias.

#### `clear(pattern=None)`
Clear pinned resources (optionally by pattern).

### **SchemaCache Methods**

#### `get_connection(alias_name)`
Get active connection for alias.

#### `set_connection(alias_name, handler)`
Store active connection (in-memory).

#### `has_connection(alias_name)`
Check if connection exists for alias.

#### `begin_transaction(alias_name)`
Begin transaction for alias.

#### `commit_transaction(alias_name)`
Commit transaction for alias.

#### `rollback_transaction(alias_name)`
Rollback transaction for alias.

#### `is_transaction_active(alias_name)`
Check if transaction is active for alias.

#### `disconnect(alias_name)`
Disconnect specific connection.

#### `clear()`
Disconnect all connections and clear cache.

#### `list_connections()`
List all active connections.

---

## **Best Practices**

### **1. Use zLoader for File Access**
```python
# Good: Use zLoader
data = zcli.loader.handle("@ui.main")

# Avoid: Direct file reading
with open("ui/main.json") as f:
    data = json.load(f)
```

### **2. Let Cache Handle Freshness**
```python
# Good: Cache handles mtime checking
data = zcli.loader.handle("@ui.main")

# Avoid: Manual freshness checks
if file_changed:
    data = load_file()
```

### **3. Use Pinned Cache for User Data**
```python
# Good: User-loaded schemas in pinned cache
# load @models.user --as mymodel
schema = zcli.loader.cache.get("mymodel", cache_type="pinned")

# Avoid: Re-loading user schemas
schema = zcli.loader.handle("@models.user")  # Reloads each time
```

### **4. Clear Cache Strategically**
```python
# Good: Clear specific patterns
zcli.loader.cache.clear(cache_type="system", pattern="ui*")

# Avoid: Clearing all unnecessarily
zcli.loader.cache.clear(cache_type="all")
```

---

## **Testing**

### **Test Coverage**
The zLoader subsystem has **42 comprehensive tests** covering:
- ✅ Initialization and setup
- ✅ System cache (LRU, mtime, eviction, patterns)
- ✅ Pinned cache (aliases, metadata, persistence)
- ✅ Schema cache (connections, transactions)
- ✅ Cache orchestrator (routing, statistics)
- ✅ File loading (cache hits/misses)
- ✅ Edge cases and error handling

### **Run Tests**
```bash
# Run all tests
python3 zTestSuite/run_all_tests.py

# Run zLoader tests only
python3 zTestSuite/run_all_tests.py
# Select option 7
```

---

## **Summary**

**zLoader** provides intelligent file loading and caching for zCLI:
- ✅ **Three-Tier Caching**: System (LRU), Pinned (user), Schema (connections)
- ✅ **Orchestrator Pattern**: Clean architecture with no cross-dependencies
- ✅ **Intelligent Loading**: Cache-first with automatic freshness tracking
- ✅ **Schema Awareness**: Fresh loading for schemas, caching for UI/config
- ✅ **Comprehensive Testing**: 42 tests with 100% pass rate
- ✅ **Clean API**: Unified interface for all cache operations

The subsystem is production-ready with proper encapsulation, comprehensive testing, and clear documentation.

