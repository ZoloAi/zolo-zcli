# Wizard Canvas Mode Guide

## Overview

Wizard Canvas Mode is an advanced feature that allows you to build multi-step workflows using a **multi-line buffer**. Unlike normal shell commands that execute immediately, canvas mode lets you **compose complex workflows** before executing them with a single command.

Think of it as a "compose window" or "editor mode" within the shell, where you can:
- Write multiple lines of YAML structure
- Mix shell commands with structured configuration
- Use transactions for atomic operations
- Reference previous step results with `zHat`
- Edit and preview before executing

---

## Core Commands

### Entering Canvas Mode

```bash
wizard --start
```

**Result:**
- Prompt changes from `zCLI>` to `>`
- Multi-line buffer activated
- Each `Enter` adds a line (does not execute)

---

### Working in Canvas Mode

```bash
> wizard --show    # Display current buffer
> wizard --clear   # Clear buffer without exiting
> wizard --run     # Execute buffer with smart format detection
> wizard --stop    # Exit canvas mode (discards buffer)
```

---

## Three Execution Formats

Canvas mode automatically detects the format you're using and executes accordingly.

### 1. Shell Command Format

**Perfect for:** Quick batch operations, simple queries

```bash
wizard --start
> data read users --model $csv_demo --limit 2
> data read posts --model $csv_demo --limit 2
> data insert users --model $csv_demo --name "New User"
> wizard --run
```

**Execution:** Commands run sequentially, one after another.

---

### 2. YAML Structure Format

**Perfect for:** Complex workflows, transaction support, step dependencies

```bash
wizard --start
> _transaction: true
> step1:
>   zData:
>     model: $csv_demo
>     action: read
>     tables: users
>     limit: 1
> step2:
>   zData:
>     model: $csv_demo
>     action: read
>     tables: posts
>     limit: 1
> wizard --run
```

**Execution:** Steps run via `zWizard` with full transaction and persistence support.

**Features:**
- `_transaction: true` enables atomic operations
- Persistent database connections across steps
- Automatic rollback on errors
- Full `zHat` accumulation for step referencing

---

### 3. Hybrid Format (YAML + Shell Commands)

**Perfect for:** Power users who want flexibility

```bash
wizard --start
> _transaction: true
> step1: data read users --model $csv_demo --limit 1
> step2:
>   zData:
>     model: $csv_demo
>     action: read
>     tables: posts
>     limit: 1
> step3: data insert products --model $csv_demo --name "Widget"
> wizard --run
```

**Execution:** Combines the simplicity of shell commands with the power of YAML structure.

---

## Buffer Management

### Viewing the Buffer

```bash
> wizard --show
```

**Output:**
```
Wizard Buffer (5 lines):
──────────────────────────────────────────────────────────────────────
  1: _transaction: true
  2: step1:
  3:   zData:
  4:     model: $csv_demo
  5:     action: read
──────────────────────────────────────────────────────────────────────
```

---

### Clearing the Buffer

```bash
> wizard --clear
[Buffer cleared - 5 lines removed]
```

**Note:** You remain in canvas mode, the buffer is just emptied.

---

### Exiting Without Running

```bash
> wizard --stop
[Exited wizard canvas - 5 lines discarded]
```

**Note:** Buffer is discarded, returns to normal `zCLI>` mode.

---

## Execution Flow

### Automatic Format Detection

When you run `wizard --run`, the system:

1. **Tries YAML parsing** first
   - If valid YAML → Executes via `zWizard` (with transaction support)
   - Detects `_transaction` flag and manages connections

2. **Falls back to shell command format**
   - If not valid YAML → Executes commands sequentially
   - Each command runs independently

---

### Smart Execution

#### YAML Format Execution

```bash
[Detected YAML/Hybrid format]
[Transaction mode: ENABLED]
[Executing 2 steps via zWizard...]
✅ Wizard execution complete
[Buffer cleared after execution]
```

**Features:**
- Connection persistence
- Transaction management
- Automatic rollback on errors
- `zHat` result accumulation

---

#### Shell Command Format Execution

```bash
[Detected shell command format]
[Executing 3 commands sequentially...]

[Step 1/3] data read users --model $csv_demo
[✓] Step 1 complete

[Step 2/3] data read posts --model $csv_demo
[✓] Step 2 complete

[Step 3/3] data insert products --model $csv_demo
[✓] Step 3 complete

[✅ 3 commands executed successfully]
[Buffer cleared after execution]
```

**Features:**
- Simple sequential execution
- Independent command execution
- Clear step-by-step feedback

---

## Use Cases

### Use Case 1: Quick Data Exploration (Shell Commands)

```bash
wizard --start
> load @.zCLI.Schemas.zSchema.csv_demo --as csv_demo
> data read users --model $csv_demo --limit 5
> data read posts --model $csv_demo --where "status=published"
> wizard --run
```

**Best for:** Ad-hoc queries, exploring data, quick operations.

---

### Use Case 2: Atomic Multi-Table Updates (YAML)

```bash
wizard --start
> _transaction: true
> create_user:
>   zData:
>     model: $db
>     action: insert
>     tables: users
>     fields:
>       name: "Alice"
>       email: "alice@example.com"
> create_post:
>   zData:
>     model: $db
>     action: insert
>     tables: posts
>     fields:
>       user_id: zHat[0].inserted_id
>       title: "First Post"
>       content: "Hello World"
> wizard --run
```

**Best for:** Related inserts, referential integrity, atomic operations.

---

### Use Case 3: Complex Workflow (Hybrid)

```bash
wizard --start
> _transaction: true
> step1: load @.zCLI.Schemas.zSchema.prod --as prod
> step2: data read users --model $prod --where "status=pending" --limit 10
> step3:
>   zFunc: "process_pending_users(zHat[1])"
> step4: data update users --model $prod --where "status=pending" --set "status=processed"
> wizard --run
```

**Best for:** ETL workflows, batch processing, mixing data + logic.

---

## Advanced Features

### Transaction Support

```yaml
_transaction: true
```

**Behavior:**
- Creates persistent connection for the entire workflow
- Automatic rollback if any step fails
- Commits only if all steps succeed

**Example with Error Handling:**

```bash
wizard --start
> _transaction: true
> step1:
>   zData:
>     model: $db
>     action: insert
>     tables: users
>     fields: {name: "Test"}
> step2:
>   zData:
>     model: $db
>     action: insert
>     tables: invalid_table  # This will fail
>     fields: {data: "x"}
> wizard --run
```

**Result:**
- Step 1 executes
- Step 2 fails
- **Automatic rollback** of step 1
- No partial data committed

---

### Connection Persistence

When using `_transaction: true` with an aliased schema (`$alias`):

```yaml
step1:
  zData:
    model: $db
    action: read
```

**Behavior:**
- First step creates connection
- Subsequent steps reuse same connection
- Connection closed after wizard completes
- More efficient for multi-step operations

---

### Result Referencing (zHat)

**Future feature:** Reference previous step results in YAML format.

```yaml
step1:
  zData:
    model: $db
    action: insert
    tables: users
    fields: {name: "Alice"}

step2:
  zData:
    model: $db
    action: insert
    tables: posts
    fields:
      user_id: zHat[0].inserted_id  # Reference step1 result
      title: "First Post"
```

---

## Comparison: Canvas vs Normal Mode

| Feature | Normal Mode | Canvas Mode |
|---------|-------------|-------------|
| Execution | Immediate | On-demand (`wizard --run`) |
| Multi-line | No | Yes (preserves indentation) |
| Preview | No | Yes (`wizard --show`) |
| Edit | No | Yes (before running) |
| Format | Shell commands only | YAML, Shell, or Hybrid |
| Transactions | No | Yes (with `_transaction`) |
| Connection Persistence | No | Yes (with wizard) |

---

## Tips and Best Practices

### 1. Use YAML for Complex Workflows

```yaml
_transaction: true
step1: # Simple command
  zData:
    model: $db
    action: read
    tables: users
```

**Why:** Better structure, transaction support, connection persistence.

---

### 2. Use Shell Commands for Quick Tasks

```bash
> data read users --model $csv_demo
> data read posts --model $csv_demo
```

**Why:** Faster to type, no indentation needed.

---

### 3. Always Preview with `wizard --show`

```bash
> wizard --show
# Review your workflow
> wizard --run
```

**Why:** Catch typos, verify logic before execution.

---

### 4. Use Aliases for Clarity

```bash
> load @.zCLI.Schemas.zSchema.prod --as prod
> step1:
>   zData:
>     model: $prod  # Clear and reusable
```

**Why:** More readable than full paths, easier to change.

---

### 5. Clear and Restart on Mistakes

```bash
> wizard --clear
[Buffer cleared]
> # Start over
```

**Why:** Fresh start is cleaner than exiting and re-entering.

---

## Troubleshooting

### Issue: YAML Not Parsing

**Symptom:** Falls back to shell command format unexpectedly.

**Solution:** Check indentation (must use spaces, typically 2 or 4).

```yaml
# BAD (mixed spaces/tabs or wrong indentation)
step1:
zData:
  model: $db

# GOOD
step1:
  zData:
    model: $db
```

---

### Issue: `tables` Not Found

**Symptom:** `Table 'u' not found`, `Table 's' not found`, etc.

**Solution:** Ensure `tables` is a list or single string, not parsed as characters.

```yaml
# BAD (will be parsed as characters)
tables: users  # If not normalized

# GOOD (normalized automatically now)
tables: users
# OR explicitly as list
tables: [users]
```

**Note:** Current implementation automatically normalizes string → list.

---

### Issue: Transaction Not Working

**Symptom:** No transaction behavior, disconnecting after each step.

**Solution:** Ensure you're using `_transaction: true` **and** an aliased schema.

```yaml
_transaction: true  # Must be present
step1:
  zData:
    model: $csv_demo  # Must be an alias ($...)
```

---

## Examples Library

### Example 1: Data Exploration

```bash
zCLI> load @.zCLI.Schemas.zSchema.csv_demo --as csv_demo
zCLI> wizard --start
> data read users --model $csv_demo --limit 5
> data read posts --model $csv_demo --where "status=published"
> data read products --model $csv_demo --order "name"
> wizard --show
> wizard --run
```

---

### Example 2: Batch Insert

```bash
zCLI> wizard --start
> data insert users --model $csv_demo --name "Alice" --email "alice@example.com"
> data insert users --model $csv_demo --name "Bob" --email "bob@example.com"
> data insert users --model $csv_demo --name "Charlie" --email "charlie@example.com"
> wizard --run
```

---

### Example 3: Transactional Workflow

```bash
zCLI> wizard --start
> _transaction: true
> step1_create_user:
>   zData:
>     model: $db
>     action: insert
>     tables: users
>     fields:
>       name: "Diana"
>       email: "diana@example.com"
> step2_create_post:
>   zData:
>     model: $db
>     action: insert
>     tables: posts
>     fields:
>       user_id: 1  # Future: zHat[0].inserted_id
>       title: "Welcome Diana"
>       content: "First post from Diana"
> wizard --show
> wizard --run
```

---

## Summary

Wizard Canvas Mode transforms the zCLI shell into a powerful workflow composer:

- **Compose** multi-step workflows with visual feedback
- **Execute** with automatic format detection (YAML, shell, or hybrid)
- **Transact** with atomic operations and rollback support
- **Persist** connections across steps for efficiency
- **Preview** before running with `wizard --show`

**Key Commands:**
- `wizard --start` → Enter canvas
- `wizard --show` → Preview buffer
- `wizard --run` → Execute buffer
- `wizard --clear` → Clear buffer
- `wizard --stop` → Exit canvas

**Perfect for:**
- Data pipelines and ETL workflows
- Batch operations with atomic guarantees
- Complex multi-table updates
- Interactive data exploration

---

*For more information on zCLI subsystems, see:*
- [zData Guide](../zData_GUIDE.md)
- [zWizard Guide](../zWizard_GUIDE.md) (coming soon)
- [zLoader Guide](../zLoader_GUIDE.md)

