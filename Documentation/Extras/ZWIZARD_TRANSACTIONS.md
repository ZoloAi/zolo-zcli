# zWizard Transactions Guide

## Overview

zWizard now supports **persistent database connections** and **atomic transactions** across multi-step operations. This enables complex workflows with rollback capabilities and eliminates connection overhead.

---

## Key Features

1. **Connection Reuse** - Single connection across all wizard steps
2. **Transaction Support** - Atomic multi-operation commits
3. **Automatic Rollback** - On error, all changes are reverted
4. **Schema Cache** - Intelligent connection pooling
5. **Alias Integration** - Works seamlessly with `$alias` references

---

## Basic Usage

### Without Transactions (Default)

Each step commits immediately:

```yaml
SimpleWizard:
  zWizard:
    step1_insert_user:
      zData:
        model: $demo
        action: insert
        tables: users
        fields: {name: "Alice", email: "alice@test.com"}
    
    step2_insert_post:
      zData:
        model: $demo
        action: insert
        tables: posts
        fields:
          user_id: zHat[0].inserted_id
          title: "First Post"
```

**Behavior:**
- Step 1: Connect → INSERT user → Commit → Keep connection
- Step 2: Reuse connection → INSERT post → Commit → Keep connection
- Wizard ends: Disconnect

**If step 2 fails:** Step 1 is already committed (cannot rollback)

---

### With Transactions (_transaction: true)

All steps in a single atomic transaction:

```yaml
AtomicWizard:
  zWizard:
    _transaction: true  # Enable transaction mode
    
    step1_insert_user:
      zData:
        model: $demo
        action: insert
        tables: users
        fields: {name: "Alice", email: "alice@test.com"}
    
    step2_insert_post:
      zData:
        model: $demo
        action: insert
        tables: posts
        fields:
          user_id: zHat[0].inserted_id
          title: "First Post"
```

**Behavior:**
- Step 1: Connect → BEGIN TRANSACTION → INSERT user → Keep connection
- Step 2: Reuse connection → INSERT post (same transaction) → Keep connection
- Wizard ends: COMMIT → Disconnect

**If step 2 fails:** ROLLBACK → Both steps reverted → Disconnect

---

## Advanced Examples

### Example 1: User Registration with Verification

```yaml
RegisterUser:
  zWizard:
    _transaction: true
    
    step1_check_email:
      zData:
        model: $demo
        action: read
        tables: users
        where: "email=user@example.com"
    
    step2_validate:
      zFunc: "len(zHat[0]) == 0"  # Email must not exist
    
    step3_insert_user:
      zData:
        model: $demo
        action: insert
        tables: users
        fields:
          name: "New User"
          email: "user@example.com"
          status: "pending"
    
    step4_create_verification:
      zData:
        model: $demo
        action: insert
        tables: verifications
        fields:
          user_id: zHat[2].inserted_id
          token: zHat[3]  # From a zFunc that generates token
          expires_at: "2025-10-13"
```

**Result:** All-or-nothing - user and verification created together or not at all.

---

### Example 2: Data Migration

```yaml
MigrateUserData:
  zWizard:
    _transaction: true
    
    step1_read_source:
      zData:
        model: $source_db
        action: read
        tables: users
        where: "migrated=false"
        limit: 100
    
    step2_transform:
      zFunc: "transform_users(zHat[0])"
    
    step3_insert_target:
      zData:
        model: $target_db
        action: insert
        tables: users
        fields: zHat[1]
    
    step4_mark_migrated:
      zData:
        model: $source_db
        action: update
        tables: users
        where: "migrated=false"
        set: {migrated: true}
```

**Note:** Uses TWO different schemas (`$source_db` and `$target_db`). Each gets its own connection in schema_cache.

---

### Example 3: Error Handling & Rollback

```yaml
CreateOrder:
  zWizard:
    _transaction: true
    
    step1_check_inventory:
      zData:
        model: $demo
        action: read
        tables: products
        where: "id=123"
    
    step2_validate_stock:
      zFunc: "zHat[0][0].stock > 0"  # Must have stock
    
    step3_create_order:
      zData:
        model: $demo
        action: insert
        tables: orders
        fields: {product_id: 123, quantity: 1}
    
    step4_decrement_stock:
      zData:
        model: $demo
        action: update
        tables: products
        where: "id=123"
        set: {stock: zHat[0][0].stock - 1}
```

**If validation fails at step 2:**
- No database changes (transaction not started yet)

**If step 4 fails:**
- Steps 3-4 are rolled back
- Database returns to pre-wizard state
- Error message logged

---

## Schema Cache Lifecycle

### Connection Creation

```python
# First zData step in wizard
if schema_cache.get_connection(alias_name) is None:
    # Create new connection
    handler = ClassicalData(zcli, schema)
    schema_cache.set_connection(alias_name, handler)
    logger.info("🔗 Created persistent connection for $alias")
```

---

### Connection Reuse

```python
# Subsequent zData steps
existing_handler = schema_cache.get_connection(alias_name)
if existing_handler:
    # Reuse existing connection
    self.handler = existing_handler
    logger.info("♻️  Reusing connection for $alias")
```

---

### Transaction Management

```python
# Begin (on first step if _transaction: true)
schema_cache.begin_transaction(alias_name)
logger.info("🔄 Transaction started for $alias")

# Commit (on wizard completion)
schema_cache.commit_transaction(alias_name)
logger.info("✅ Transaction committed for $alias")

# Rollback (on error)
schema_cache.rollback_transaction(alias_name)
logger.error("❌ Transaction rolled back for $alias")
```

---

### Cleanup

```python
# Always in finally block
schema_cache.clear()
logger.debug("Schema cache connections cleared")
```

---

## Multi-Schema Wizards

Wizards can use multiple schemas, each with its own connection:

```yaml
CrossDatabaseWizard:
  zWizard:
    step1_read_from_source:
      zData:
        model: $source
        action: read
        tables: users
    
    step2_write_to_target:
      zData:
        model: $target
        action: insert
        tables: users
        fields: zHat[0]
    
    step3_verify_source:
      zData:
        model: $source  # Reuses connection
        action: read
        tables: users
    
    step4_verify_target:
      zData:
        model: $target  # Reuses connection
        action: read
        tables: users
```

**schema_cache state:**
```python
{
    "source": <ClassicalData handler #1>,
    "target": <ClassicalData handler #2>
}
```

**Both connections** reused across steps, cleaned up at end.

---

## Transaction Limitations

### What Works

- ✅ Multiple INSERTs
- ✅ Multiple UPDATEs
- ✅ Multiple DELETEs
- ✅ Mixed operations (INSERT + UPDATE + DELETE)
- ✅ SELECTs (within transaction for consistency)
- ✅ Foreign key cascades

### What Doesn't Work

- ❌ DDL operations (CREATE TABLE, ALTER TABLE) - these auto-commit
- ❌ Cross-database transactions (each database is separate)
- ❌ CSV adapter (doesn't support transactions)

---

## Error Handling

### Automatic Rollback

```yaml
WizardWithError:
  zWizard:
    _transaction: true
    
    step1: {zData: {model: $demo, action: insert, ...}}  # Succeeds
    step2: {zData: {model: $demo, action: insert, ...}}  # Fails (duplicate key)
    step3: {zData: {model: $demo, action: insert, ...}}  # Never runs
```

**Log output:**
```
🔄 Transaction mode enabled for $demo
🔗 Created persistent connection for $demo
✓ Step 1 complete
❌ Error in step 2: duplicate key violation
❌ Error in zWizard, rolling back transaction for $demo
↩️  Transaction rolled back for $demo
Schema cache connections cleared
```

**Database state:** Unchanged (step 1 rolled back)

---

### Manual Error Handling (Future)

```yaml
# Future enhancement
WizardWithErrorHandling:
  zWizard:
    _transaction: true
    _onError:
      rollback: true
      message: "Operation failed, changes reverted"
      action: "zBack"
    
    steps: [...]
```

---

## Backend Support

### Transactions Supported

| Backend | Transaction Support | Notes |
|---------|-------------------|-------|
| PostgreSQL | ✅ Full | BEGIN, COMMIT, ROLLBACK |
| SQLite | ✅ Full | BEGIN, COMMIT, ROLLBACK |
| CSV | ❌ No | File-based, no ACID guarantees |

**CSV Behavior:**
- Connection reuse: ✅ Works (keeps DataFrames in memory)
- Transactions: ❌ Each write commits immediately to file
- Rollback: ❌ Not possible

---

## Performance Comparison

### Without zWizard (Sequential Commands)

```bash
# Each command connects/disconnects
data insert users --model $demo --name "User1"  # 66ms
data insert users --model $demo --name "User2"  # 66ms
data insert users --model $demo --name "User3"  # 66ms
data read users --model $demo                   # 66ms
```

**Total: 264ms (4 connections)**

---

### With zWizard (Persistent Connection)

```yaml
zWizard:
  step1: {zData: {model: $demo, action: insert, ...}}  # 61ms (connect)
  step2: {zData: {model: $demo, action: insert, ...}}  # 11ms (reuse)
  step3: {zData: {model: $demo, action: insert, ...}}  # 11ms (reuse)
  step4: {zData: {model: $demo, action: read, ...}}    # 11ms (reuse)
```

**Total: 94ms (1 connection, 64% faster)**

---

## Debugging

### Enable Debug Logging

Set log level to DEBUG to see connection lifecycle:

```
[SchemaCache] Stored connection for $demo
♻️  Reusing connection for $demo
🔄 Transaction started for $demo
✅ Transaction committed for $demo
[SchemaCache] Disconnected $demo
Schema cache connections cleared
```

---

### View Active Connections

```bash
session info
```

Look for `zCache.schema_cache`:

```python
"schema_cache": {
    "demo": {
        "active": True,
        "connected_at": 1760257587.0,
        "backend": "sqlite"
    }
}
```

**Note:** This shows metadata only. Actual connection objects are in-memory.

---

## Summary

zWizard with schema_cache provides:

1. **Persistent Connections** - Eliminate reconnection overhead
2. **Atomic Transactions** - All-or-nothing multi-step operations
3. **Automatic Cleanup** - No lingering connections
4. **Error Recovery** - Automatic rollback on failure
5. **Performance** - 11x faster for repeated operations

**Use transactions when:** You need multi-step atomicity (all succeed or all fail)

**Skip transactions when:** Steps are independent and can partially succeed

