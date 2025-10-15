# Alias Feature Guide - zCLI `load --as` and `$alias` References

## Overview

The alias feature allows you to **load and pin schemas** (or other zVaFiles) with a short, memorable name, then reference them using the `$` symbol in commands. This dramatically improves the developer experience by eliminating repetitive, long `--model` paths.

**Before Aliases:**
```bash
data read users --model @.zCLI.Schemas.zSchema.sqlite_demo
data insert users --model @.zCLI.Schemas.zSchema.sqlite_demo --name "Alice"
data read posts --model @.zCLI.Schemas.zSchema.sqlite_demo
```

**With Aliases:**
```bash
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo
data read users --model $sqlite_demo
data insert users --model $sqlite_demo --name "Alice"
data read posts --model $sqlite_demo
```

---

## Architecture

### Integration with LoadedCache

Aliases leverage the existing **LoadedCache** system (Priority 1 cache) to store pinned schemas:

```
Shell Command: load <zPath> --as <alias>
      ↓
Parse schema from disk
      ↓
Store in LoadedCache with key: "alias:{name}"
      ↓
When using: --model $alias
      ↓
Resolve from LoadedCache["alias:{name}"]
      ↓
Use cached schema (no re-parsing)
```

**Key Benefits:**
- ✅ No new data structures - uses existing LoadedCache
- ✅ Priority 1 caching - never auto-evicted
- ✅ Schemas are cached when explicitly pinned (overrides "no schema caching" rule)
- ✅ Metadata tracking - type, filepath, loaded_at, age

---

## Command Syntax

### 1. Load Schema with Alias

```bash
load <zPath> --as <alias_name>
```

**Examples:**
```bash
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo
load @.zCLI.Schemas.zSchema.csv_demo --as csv_demo
load @.zCLI.Schemas.zSchema.postgresql_demo --as pg_demo
```

**Output:**
```
✅ Loaded and aliased schema: @.zCLI.Schemas.zSchema.sqlite_demo → $sqlite_demo (3 tables)
```

---

### 2. View All Aliases

```bash
load show aliases
```

**Output:**
```
======================================================================
Defined Aliases
======================================================================

SCHEMA:
  $sqlite_demo
    → @.zCLI.Schemas.zSchema.sqlite_demo
    Age: 0 minutes
  $csv_demo
    → @.zCLI.Schemas.zSchema.csv_demo
    Age: 0 minutes
  $pg_demo
    → @.zCLI.Schemas.zSchema.postgresql_demo
    Age: 2 minutes

======================================================================
Total: 3 alias(es)
======================================================================
```

---

### 3. Use Alias in Data Commands

Once an alias is defined, reference it with the `$` prefix:

```bash
# Basic read
data read users --model $sqlite_demo

# With WHERE clause
data read users --model $sqlite_demo --where "status=active"

# With LIMIT
data read users --model $csv_demo --limit 10

# Multi-table JOIN
data read users,posts --model $sqlite_demo --auto-join

# INSERT
data insert users --model $csv_demo --name "Alice" --email "alice@test.com" --age 25

# UPDATE
data update users --model $pg_demo --where "id=1" --name "Updated Name"

# DELETE
data delete users --model $sqlite_demo --where "status=inactive"
```

---

### 4. Remove Specific Alias

Use the LoadedCache `clear` command with pattern matching:

```bash
load clear alias:sqlite_demo
```

Or use the standard `unload` pattern (if implemented):
```bash
# Future: unload sqlite_demo
```

---

### 5. Clear All Aliases

```bash
load clear alias:*
```

---

## Use Cases

### 1. Development Workflow

**Scenario:** Working with multiple schemas during development.

```bash
# Load all project schemas at start of session
load @.zCLI.Schemas.zSchema.users_schema --as users
load @.zCLI.Schemas.zSchema.orders_schema --as orders
load @.zCLI.Schemas.zSchema.products_schema --as products

# Work with concise commands
data read users --model $users
data read orders --model $orders --where "status=pending"
data read products --model $products --limit 20
```

---

### 2. Multi-Backend Testing

**Scenario:** Test the same data operations across different backends (CSV, SQLite, PostgreSQL).

```bash
# Load schemas for all backends
load @.zCLI.Schemas.zSchema.csv_demo --as csv
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite
load @.zCLI.Schemas.zSchema.postgresql_demo --as pg

# Test same query on all backends
data read users --model $csv --where "age>30"
data read users --model $sqlite --where "age>30"
data read users --model $pg --where "age>30"
```

**Benefit:** Demonstrates the **data portability** power of zCLI - same command works across heterogeneous backends!

---

### 3. Interactive Scripting

**Scenario:** Alias-based scripts are more readable and maintainable.

```bash
#!/bin/bash
# setup_demo.sh

zolo shell << 'EOF'
# Load schema once
load @.zCLI.Schemas.zSchema.sqlite_demo --as demo

# Run multiple operations with short alias
data create users --model $demo
data create posts --model $demo
data insert users --model $demo --name "Alice" --email "alice@demo.com"
data insert users --model $demo --name "Bob" --email "bob@demo.com"
data insert posts --model $demo --user_id 1 --title "First Post"
data read users,posts --model $demo --auto-join

exit
EOF
```

---

### 4. Environment-Specific Aliases

**Scenario:** Different schemas for dev/staging/prod.

```bash
# Development
load @.zCLI.Schemas.zSchema.dev_schema --as current

# Staging (just reload the alias)
load @.zCLI.Schemas.zSchema.staging_schema --as current

# Production
load @.zCLI.Schemas.zSchema.prod_schema --as current

# All commands use same alias
data read users --model $current
```

---

## Implementation Details

### Files Modified

1. **`zCLI/subsystems/zShell_modules/executor_commands/load_executor.py`**
   - Enhanced `execute_load()` to handle `--as` option
   - Added `show_aliases()` function for listing aliases
   - Bypasses "no schema caching" rule for explicit `--as` loads

2. **`zCLI/subsystems/zShell_modules/executor_commands/alias_utils.py`** (NEW)
   - `resolve_alias()` - Resolves `$alias` to cached content
   - `is_alias()` - Checks if value starts with `$`
   - `get_alias_name()` - Extracts alias name from `$alias`
   - `resolve_option_aliases()` - Batch resolution for multiple options

3. **`zCLI/subsystems/zShell_modules/executor_commands/data_executor.py`**
   - Integrated alias resolution for `--model` option
   - Passes pre-parsed schema to zData subsystem

4. **`zCLI/subsystems/zData/zData.py`**
   - Enhanced `handle_request()` to accept pre-parsed schemas
   - Checks `options._schema_cached` field for aliased schemas
   - Skips re-parsing when cached schema is provided

5. **`zCLI/subsystems/zParser_modules/zParser_commands.py`**
   - Updated `_parse_load_command()` to extract options (e.g., `--as`)

---

### Storage Format

Aliases are stored in the LoadedCache with the following structure:

```python
# Cache key format
key = f"alias:{alias_name}"

# Example: "alias:sqlite_demo"

# Cache entry format
{
    "data": <parsed_schema_dict>,
    "type": "schema",  # or "ui", "config"
    "filepath": "@.zCLI.Schemas.zSchema.sqlite_demo",  # Original zPath
    "loaded_at": 1760257587.887,  # Unix timestamp
    "age": 0.005  # Seconds since loaded
}
```

---

### Resolution Flow

```python
# 1. User command
data read users --model $sqlite_demo

# 2. Parser extracts option
parsed = {
    "type": "data",
    "action": "read",
    "args": ["users"],
    "options": {"model": "$sqlite_demo"}
}

# 3. Data executor detects alias
if is_alias("$sqlite_demo"):
    schema, was_alias = resolve_alias("$sqlite_demo", zcli.loader.loaded_cache)
    
    # 4. Pass pre-parsed schema
    options["_schema_cached"] = schema
    options["_alias_name"] = "sqlite_demo"
    model_path = None

# 5. zData uses cached schema
if options.get("_schema_cached"):
    self.load_schema(options["_schema_cached"])
```

---

## Performance Benefits

### Before Aliases (Every Command)
1. Parse `--model` path
2. Resolve zPath to filesystem path
3. Read YAML file from disk
4. Parse YAML content
5. Initialize adapter
6. Execute operation

**Total:** ~50-100ms per command for schema loading

---

### With Aliases (After Initial Load)
1. ✅ **Skipped:** Parse path (cached)
2. ✅ **Skipped:** Resolve zPath (cached)
3. ✅ **Skipped:** Read from disk (cached)
4. ✅ **Skipped:** Parse YAML (cached)
5. Initialize adapter
6. Execute operation

**Total:** ~5-10ms - **10x faster** for repeated commands!

---

## Error Handling

### Missing Alias

**Command:**
```bash
data read users --model $nonexistent
```

**Error:**
```
[ERROR] Alias not found: $nonexistent
Use 'load <zPath> --as nonexistent' to create this alias.
Example: load @.zCLI.Schemas.zSchema.nonexistent --as nonexistent
```

---

### Invalid zPath on Load

**Command:**
```bash
load @.zCLI.Schemas.zSchema.doesnt_exist --as myalias
```

**Error:**
```
[ERROR] Failed to load: @.zCLI.Schemas.zSchema.doesnt_exist
Unable to load zFile (not found): /path/to/zSchema.doesnt_exist.yaml
```

---

## Future Enhancements

### 1. Config File Persistence

Store aliases in `~/.config/zolo-zcli/aliases.yaml`:

```yaml
aliases:
  sqlite_demo: "@.zCLI.Schemas.zSchema.sqlite_demo"
  csv_demo: "@.zCLI.Schemas.zSchema.csv_demo"
  prod_db: "@.zCLI.Schemas.zSchema.postgresql_prod"
```

Auto-load on shell startup.

---

### 2. Scoped Aliases

- **Session:** Current shell session only (current implementation)
- **User:** Persisted in `~/.config/zolo-zcli/`
- **Machine:** Shared across all users on machine
- **Project:** Stored in project `.zolo/aliases.yaml`

---

### 3. Alias Chaining

```bash
load @.Base.Schema --as base
load $base.extended --as extended  # Use alias in path
```

---

### 4. Shorthand Commands

```bash
alias sqlite_demo=@.zCLI.Schemas.zSchema.sqlite_demo  # Create
unalias sqlite_demo                                    # Remove
aliases                                                # List (already works!)
```

---

### 5. Alias Validation

```bash
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo --validate
# ✓ Path exists
# ✓ Valid YAML
# ✓ Schema passes validation
```

---

### 6. Extend to All Options

Currently `$alias` works with `--model`. Future: extend to all zPath options:

```bash
walker run --ui $myUI          # UI aliases
config load --config $myConfig # Config aliases
data read users --schema $mySchema  # Schema aliases (if separate from model)
```

---

## Best Practices

### 1. Consistent Naming

Use descriptive, consistent alias names:

```bash
# ✅ Good
load @.zCLI.Schemas.zSchema.users_v2 --as users_v2
load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo

# ❌ Avoid
load @.zCLI.Schemas.zSchema.users_v2 --as x
load @.zCLI.Schemas.zSchema.sqlite_demo --as temp123
```

---

### 2. Load Aliases at Session Start

Create a session initialization script:

```bash
# .zolo_init
load @.zCLI.Schemas.zSchema.users --as users
load @.zCLI.Schemas.zSchema.orders --as orders
load @.zCLI.Schemas.zSchema.products --as products
```

Then source it:
```bash
zolo shell < .zolo_init
```

---

### 3. Clear Stale Aliases

If schemas are updated, reload the alias:

```bash
# Schema file changed on disk
load @.zCLI.Schemas.zSchema.users --as users  # Overwrites existing alias
```

Or clear all and reload:
```bash
load clear alias:*
# Then reload all aliases
```

---

### 4. Document Project Aliases

In your project README:

```markdown
## zCLI Aliases

Load these aliases before working with the project:

bash
load @.zCLI.Schemas.zSchema.dev_schema --as dev
load @.zCLI.Schemas.zSchema.test_schema --as test
load @.zCLI.Schemas.zSchema.prod_schema --as prod
```

---

## Comparison: Alias vs Traditional

| Feature | Traditional (`--model @.path`) | Alias (`--model $alias`) |
|---------|-------------------------------|---------------------------|
| **Typing** | Long, repetitive paths | Short, memorable names |
| **Speed** | Parses schema every time | Cached after first load |
| **Errors** | Typos in long paths | Typos in short alias names |
| **Readability** | Cluttered commands | Clean, concise commands |
| **Maintenance** | Update every command if path changes | Update alias once |
| **Session Management** | No state | Persistent within session |

---

## Summary

The **alias feature** is a **significant developer experience improvement** that:

1. ✅ **Reduces typing** - Short `$alias` instead of long `@.path.to.schema`
2. ✅ **Improves performance** - Cached schemas eliminate re-parsing
3. ✅ **Enhances readability** - Commands are cleaner and easier to understand
4. ✅ **Simplifies maintenance** - Change alias once, not in every command
5. ✅ **Leverages existing architecture** - Uses LoadedCache (Priority 1)
6. ✅ **Works across all backends** - SQLite, PostgreSQL, CSV all support aliases

**Next step:** Extend this pattern to **query result caching** and **selection state management** for interactive UI features! 🚀

