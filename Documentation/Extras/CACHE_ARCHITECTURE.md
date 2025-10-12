# Cache Architecture - Three-Tier System

## Overview

zCLI uses a sophisticated three-tier caching system managed by the `CacheOrchestrator`. This architecture provides intelligent routing between lightweight parsed data, auto-cached files, and heavyweight database connections.

---

## Architecture Diagram

```
CacheOrchestrator (Smart Router)
    ↓ routes to
session["zCache"] = {
    "pinned_cache": {},   # Tier 1: User-loaded aliases (static, never evicts)
    "system_cache": {},   # Tier 2: Auto-cached files (LRU, mtime checking)
    "schema_cache": {}    # Tier 3: Active connections (wizard-only, ephemeral)
}
```

---

## Cache Tiers

### Tier 1: PinnedCache (Aliases)

**Purpose:** User-loaded aliases for frequently used schemas

**Characteristics:**
- Lightweight (parsed schemas only, no connections)
- Never auto-evicts (user must explicitly clear)
- Session-scoped (persists across commands)
- Highest priority (checked first)
- Supports `$alias` references

**Usage:**
```bash
# Load schema as alias
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo

# Use alias
data read users --model $sqlite_demo
```

**Storage Format:**
```python
session["zCache"]["pinned_cache"] = {
    "alias:sqlite_demo": {
        "data": {...parsed_schema_dict...},
        "zpath": "@.zCLI.Schemas.zSchema.sqlite_demo",
        "type": "schema",
        "loaded_at": 1760257587.887
    }
}
```

**API:**
- `load_alias(alias_name, parsed_schema, zpath)` - Store alias
- `get_alias(alias_name)` - Retrieve alias
- `has_alias(alias_name)` - Check if exists
- `remove_alias(alias_name)` - Remove specific alias
- `list_aliases()` - List all aliases
- `clear(pattern)` - Clear aliases

---

### Tier 2: SystemCache (Auto-Cached Files)

**Purpose:** Automatically cache UI and config files with LRU eviction

**Characteristics:**
- Auto-cached (no user intervention)
- LRU eviction (max 100 entries by default)
- mtime checking (auto-invalidates on file changes)
- Performance tracking (hits, misses, evictions)

**Usage:**
Automatic - zLoader uses this for UI and config files

**Storage Format:**
```python
session["zCache"]["system_cache"] = OrderedDict({
    "parsed:@.UI.main": {
        "data": {...parsed_ui_dict...},
        "cached_at": 1760257587.0,
        "accessed_at": 1760257600.0,
        "hits": 5,
        "mtime": 1760257500.0,
        "filepath": "/path/to/file.yaml"
    }
})
```

**API:**
- `get(key, filepath, default)` - Retrieve with mtime check
- `set(key, value, filepath)` - Store with mtime tracking
- `invalidate(key)` - Manual removal
- `clear(pattern)` - Bulk removal
- `get_stats()` - Performance metrics

**Features:**
- File modification detection
- Automatic invalidation
- LRU ordering (OrderedDict)
- Statistics tracking

---

### Tier 3: SchemaCache (Active Connections)

**Purpose:** Manage active database connections during zWizard execution

**Characteristics:**
- Heavyweight (active connections, not just data)
- Wizard-only (only exists during zWizard execution)
- Ephemeral (cleared when wizard completes)
- Transaction-aware
- In-memory (connections not serialized to session)

**Usage:**
Automatic - managed by zWizard, invisible to user

**Storage Format:**
```python
# In-memory (not in session)
schema_cache.connections = {
    "sqlite_demo": <ClassicalData handler instance>
}

# Metadata in session
session["zCache"]["schema_cache"] = {
    "sqlite_demo": {
        "active": True,
        "connected_at": 1760257587.0,
        "backend": "sqlite"
    }
}
```

**API:**
- `get_connection(alias_name)` - Get active connection
- `set_connection(alias_name, handler)` - Store connection
- `begin_transaction(alias_name)` - Start transaction
- `commit_transaction(alias_name)` - Commit transaction
- `rollback_transaction(alias_name)` - Rollback transaction
- `disconnect(alias_name)` - Close specific connection
- `clear()` - Close all connections
- `list_connections()` - List active connections

**Lifecycle:**
1. zWizard starts → SchemaCache created
2. First zData step → Connection established, stored in cache
3. Subsequent steps → Connection reused
4. zWizard completes → All connections closed

---

## CacheOrchestrator

The `CacheOrchestrator` is the intelligent router that delegates requests to the appropriate cache tier.

**Responsibilities:**
- Route get/set requests to correct tier
- Expose unified API for all caches
- Manage tier initialization
- Provide aggregate statistics

**API:**
```python
# Get from specific tier
orchestrator.get(key, cache_type="pinned")    # From pinned_cache
orchestrator.get(key, cache_type="system")    # From system_cache
orchestrator.get(key, cache_type="schema")    # From schema_cache

# Set to specific tier
orchestrator.set(key, value, cache_type="pinned", zpath="...")
orchestrator.set(key, value, cache_type="system", filepath="...")
orchestrator.set(key, value, cache_type="schema")

# Check existence
orchestrator.has(key, cache_type="pinned")

# Clear caches
orchestrator.clear(cache_type="all")
orchestrator.clear(cache_type="pinned", pattern="alias:*")

# Get statistics
orchestrator.get_stats(cache_type="all")
```

---

## Data Flow

### Single Command (One-Shot Mode)

```
User: data read users --model $sqlite_demo
  ↓
1. Resolve alias from pinned_cache
  ↓
2. Create ClassicalData handler with schema
  ↓
3. Connect to database
  ↓
4. Execute query
  ↓
5. Disconnect
  ↓
6. Return result
```

**Connection:** Created and destroyed per command

---

### zWizard (Persistent Mode)

```
zWizard:
  _transaction: true
  step1: {zData: {model: $demo, action: insert, ...}}
  step2: {zData: {model: $demo, action: insert, ...}}
  step3: {zData: {model: $demo, action: read, ...}}

Flow:
  ↓
1. zWizard starts → schema_cache created
  ↓
2. Step 1: Resolve $demo from pinned_cache
         → Create handler, connect
         → Store in schema_cache
         → Begin transaction
         → Execute INSERT
  ↓
3. Step 2: Check schema_cache for $demo
         → REUSE existing connection
         → Execute INSERT (same transaction)
  ↓
4. Step 3: Check schema_cache for $demo
         → REUSE existing connection
         → Execute READ (same transaction)
  ↓
5. All steps succeed → Commit transaction
  ↓
6. zWizard completes → Clear schema_cache (disconnect all)
```

**Connection:** Created once, reused across all steps, cleaned up at end

---

## Performance Benefits

### Before (No Caching)

Every command:
1. Parse path → 10ms
2. Read YAML from disk → 20ms
3. Parse YAML → 30ms
4. Connect to database → 50ms
5. Execute query → 10ms
6. Disconnect → 5ms

**Total: ~125ms per command**

---

### After (Three-Tier Caching)

#### With Alias (One-Shot):
1. Resolve alias (cached) → 1ms
2. ~~Read YAML~~ (skipped)
3. ~~Parse YAML~~ (skipped)
4. Connect to database → 50ms
5. Execute query → 10ms
6. Disconnect → 5ms

**Total: ~66ms (47% faster)**

#### With Alias (zWizard):
First command:
1. Resolve alias → 1ms
2. Connect → 50ms
3. Execute → 10ms

**Total: ~61ms**

Subsequent commands:
1. Resolve alias → 1ms
2. ~~Connect~~ (reused)
3. Execute → 10ms

**Total: ~11ms (11x faster!)**

---

## Key Principles

### 1. Separation of Concerns

- **PinnedCache** = Lightweight static data
- **SystemCache** = Auto-managed file caching
- **SchemaCache** = Heavyweight connection pooling

Each tier has a single, clear responsibility.

---

### 2. Lifecycle Management

| Tier | Created | Destroyed | Scope |
|------|---------|-----------|-------|
| PinnedCache | On `load --as` | On `clear` or session end | Session |
| SystemCache | Automatic | LRU eviction or session end | Session |
| SchemaCache | zWizard start | zWizard end | Wizard execution |

---

### 3. Priority Routing

When loading a resource, CacheOrchestrator checks in order:
1. pinned_cache (if alias reference)
2. system_cache (if not schema file)
3. Disk (cache miss)

---

### 4. Connection Reuse Strategy

**Without zWizard:**
- Each command = new connection
- Safe, simple, stateless

**With zWizard:**
- First step = create connection
- Subsequent steps = reuse connection
- End of wizard = disconnect all
- On error = rollback + disconnect

---

## Monitoring & Debugging

### View All Cache Tiers

```bash
load show
```

**Output:**
```
╔═══ Tier 1: Pinned Cache (User-Loaded Aliases) ═══╗
  $sqlite_demo → @.zCLI.Schemas.zSchema.sqlite_demo (Age: 5 minutes)

╔═══ Tier 2: System Cache (Auto-Cached Files) ═══╗
  Size: 8/100
  Hit Rate: 75.0%
  Hits: 15 | Misses: 5
  Evictions: 0 | Invalidations: 2

╔═══ Tier 3: Disk I/O (Fallback) ═══╗
  Always available
```

---

### View Specific Tier

```bash
load show pinned    # Tier 1 only
load show cached    # Tier 2 only
load show aliases   # Tier 1 aliases
```

---

### View Session Cache

```bash
session info
```

Shows `zCache` structure with all three tiers.

---

## Best Practices

### 1. Use Aliases for Repeated Schemas

```bash
# At session start
load @.zCLI.Schemas.zSchema.main --as main

# Throughout session
data read users --model $main
data insert posts --model $main --title "..."
data read posts --model $main
```

**Benefit:** 10x faster repeated commands

---

### 2. Use zWizard for Multi-Step Operations

```yaml
CreateUserWithPosts:
  zWizard:
    _transaction: true
    
    step1_user:
      zData:
        model: $demo
        action: insert
        tables: users
        fields: {name: "Alice"}
    
    step2_post:
      zData:
        model: $demo
        action: insert
        tables: posts
        fields: {user_id: zHat[0].id, title: "First Post"}
```

**Benefit:** Single connection, atomic transactions

---

### 3. Clear Stale Aliases

```bash
# If schema file changes
load @.zCLI.Schemas.zSchema.main --as main  # Overwrites

# Or clear all and reload
load clear alias:*
```

---

## Summary

The three-tier cache architecture provides:

1. **Performance** - 10x faster with aliases, 11x faster in zWizard
2. **Efficiency** - Connection pooling eliminates reconnection overhead
3. **Safety** - Automatic cleanup, transaction support
4. **Simplicity** - Invisible to users, managed automatically
5. **Flexibility** - One-shot or persistent modes

**The right tool for the right job:** Lightweight caching for static data, heavyweight pooling for active connections.

