# zDialog Guide

## Introduction

**zDialog** is the interactive form and dialog subsystem for `zolo-zcli`. It provides schema-driven user input collection with validation, flexible submission handling, and seamless integration with zData for CRUD operations.

> **Note:** zDialog is a shared subsystem used by both Walker (UI mode) and Shell (command mode) for collecting structured user input based on schema definitions.

---

## Dialog Structure

### Basic Dialog Syntax:

```yaml
# In UI file (Walker mode)
CreateUser:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username, email, password, role]
    onSubmit:
      action: create
      tables: [zUsers]
      values: zConv
```

### Dialog Components:

| Component | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | ✅ Yes | Schema model path (zPath format) |
| `fields` | array | ✅ Yes | List of fields to collect |
| `onSubmit` | dict/string | ❌ No | Action to perform with collected data |

---

## Dialog Workflow

### Step-by-Step Flow:

```
1. User triggers dialog (via Walker menu or Shell command)
        ↓
2. zDialog loads schema model (via zLoader)
        ↓
3. zDialog creates context (model + fields)
        ↓
4. zDisplay renders form and collects input
        ↓
5. Input stored in zConv dict
        ↓
6. onSubmit executed (if provided)
        ↓
7. Result returned to caller
```

### Data Flow Diagram:

```
User Input
    ↓
zDialog.handle(zHorizontal)
    ↓
zLoader.handle(model)  ← Load schema
    ↓
SmartCache["files"]    ← Cache schema
    ↓
zDisplay.render_zConv()  ← Render form
    ↓
zConv = {collected data}
    ↓
onSubmit → zDispatch/zFunc → zData
```

---

## Model Loading

### Schema Model Path:

```yaml
model: "@.schemas.schema.zUsers"
       ↑  ↑       ↑      ↑
       │  │       │      └─ Table/zBlock name
       │  │       └──────── Schema filename
       │  └──────────────── Directory path
       └─────────────────── Workspace symbol
```

### Model Resolution:

1. **zDialog receives:** `"@.schemas.schema.zUsers"`
2. **zLoader resolves:** `/workspace/schemas/schema.yaml`
3. **zLoader loads:** Entire schema file (all tables)
4. **zLoader caches:** In `zCache["files"]["parsed:/workspace/schemas/schema.yaml"]`
5. **zDialog extracts:** `zUsers` table definition

### Caching Behavior:

```python
# First dialog with this model
zDialog → zLoader → Read file → Parse YAML → Cache → Return
# Time: ~50ms

# Subsequent dialogs with same model
zDialog → zLoader → Check cache → Return cached
# Time: ~1ms (50x faster!)
```

---

## Field Collection

### Field Definitions:

Fields are defined in the schema model:

```yaml
# schema.yaml
zUsers:
  username:
    type: str
    required: true
    unique: true
  email:
    type: str
    required: true
    rules:
      format: email
  role:
    type: enum
    options: [zAdmin, zBuilder, zUser]
    default: zUser
```

### Input Types:

| Type | Input Method | Validation |
|------|--------------|------------|
| `str` | Free-form text | Length, format rules |
| `int` | Numeric input | Range validation |
| `enum` | Selection menu | Must match options |
| `bool` | Yes/No prompt | True/False only |
| `datetime` | ISO format | Date parsing |

### Example Collection:

```
* username (str):
  Enter username: john_doe

* email (str):
  Enter email: john@example.com

* role (enum):
  0: zAdmin
  1: zBuilder
  2: zUser
  Select role [0-2]: 2

✅ Collected: {
  "username": "john_doe",
  "email": "john@example.com",
  "role": "zUser"
}
```

---

## Submission Handling

### onSubmit Syntax:

#### **Dict-based (Recommended):**

```yaml
CreateUser:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username, email, password]
    onSubmit:
      action: create
      tables: [zUsers]
      fields: [username, email, password]
      values: zConv
```

#### **String-based (Legacy):**

```yaml
CreateUser:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username, email]
    onSubmit: "zFunc(create_user(zConv))"
```

### Placeholder Injection:

The `zConv` placeholder is replaced with collected data:

```yaml
# Before injection:
onSubmit:
  action: create
  values: zConv

# After injection:
onSubmit:
  action: create
  values: {
    "username": "john_doe",
    "email": "john@example.com"
  }
```

### Field-specific Placeholders:

```yaml
# Access specific fields:
onSubmit:
  action: update
  where:
    id: zConv.id        # ← Access zConv["id"]
  values:
    username: zConv.username
    email: zConv.email
```

---

## Usage Examples

### Example 1: Simple Create Dialog

```yaml
# ui.main.yaml
CreateProduct:
  zDialog:
    model: "@.schemas.schema.zProducts"
    fields: [name, price, category]
    onSubmit:
      # Direct CRUD (no wrapper)
      action: create
      tables: [zProducts]
      values: zConv
```

**Flow:**
1. User selects "CreateProduct" menu item
2. Dialog prompts for: name, price, category
3. User enters data
4. onSubmit creates new product in database
5. Returns to menu

---

### Example 2: Update Dialog with WHERE

```yaml
# ui.main.yaml
UpdateUser:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [id, username, email]
    onSubmit:
      action: update
      tables: [zUsers]
      where:
        id: zConv.id
      values:
        username: zConv.username
        email: zConv.email
```

**Flow:**
1. Dialog collects: id, username, email
2. onSubmit updates user WHERE id matches
3. Only username and email are updated

---

### Example 3: Custom Function Submit

```yaml
# ui.main.yaml
ProcessOrder:
  zDialog:
    model: "@.schemas.schema.zOrders"
    fields: [order_id, status]
    onSubmit: "zFunc(process_order(zConv))"
```

**Flow:**
1. Dialog collects order data
2. onSubmit calls custom `process_order()` function
3. Function receives zConv dict as argument

---

### Example 4: No onSubmit (Data Collection Only)

```yaml
# ui.main.yaml
GetUserInfo:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username, email]
  # No onSubmit - just collect and return data
```

**Flow:**
1. Dialog collects data
2. Returns zConv to caller
3. Caller decides what to do with data

---

## Context Management

### Dialog Context Structure:

```python
zContext = {
    "model": "@.schemas.schema.zUsers",
    "fields": ["username", "email", "password"],
    "zConv": {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "hashed_password"
    }
}
```

### Context Lifecycle:

1. **Creation:** `create_dialog_context(model, fields)`
2. **Population:** `zConv` added after input collection
3. **Injection:** Placeholders replaced in onSubmit
4. **Submission:** Passed to handler (zDispatch/zFunc)

---

## Modular Architecture

### zDialog Structure:

```
zCLI/subsystems/
├── zDialog.py                    # Main handler
└── zDialog_modules/
    ├── __init__.py              # Module exports
    ├── dialog_context.py        # Context creation & placeholders
    └── dialog_submit.py         # Submission handling
```

### Module Responsibilities:

#### **zDialog.py** - Main Handler
- `ZDialog` class - Orchestrates dialog flow
- `handle_zDialog()` - Backward-compatible function
- Entry point for all dialog operations

#### **dialog_context.py** - Context Management
- `create_dialog_context()` - Build dialog context
- `inject_placeholders()` - Replace zConv placeholders
- Supports: `zConv`, `zConv.field`, `zConv['field']`

#### **dialog_submit.py** - Submission Handling
- `handle_submit()` - Main submission router
- `handle_dict_submit()` - Dict-based syntax (via zDispatch)
- `handle_string_submit()` - String-based syntax (via zFunc)

---

## Walker Integration

### In UI Files:

```yaml
# ui.main.yaml
MainMenu:
  CreateUser:
    label: "Create New User"
    zDialog:
      model: "@.schemas.schema.zUsers"
      fields: [username, email, password, role]
      onSubmit:
        # Direct CRUD (no wrapper)
        action: create
        tables: [zUsers]
        values: zConv
  
  UpdateUser:
    label: "Update User"
    zDialog:
      model: "@.schemas.schema.zUsers"
      fields: [id, username, email]
      onSubmit:
        # Direct CRUD (no wrapper)
        action: update
        tables: [zUsers]
          where: {id: zConv.id}
        values: {username: zConv.username, email: zConv.email}
```

### Walker Flow:

```
User selects menu item
    ↓
zMenu detects zDialog key
    ↓
zDispatch.zLauncher(zHorizontal)
    ↓
handle_zDialog(zHorizontal, walker)
    ↓
ZDialog.handle() → collect input → submit
    ↓
Result returned to Walker
```

---

## Shell Integration (Future)

### Planned Shell Usage:

```bash
# Shell command
crud create zUsers --model @.schemas.schema

# Should internally trigger:
zDialog.handle({
    "zDialog": {
        "model": "@.schemas.schema.zUsers",
        "fields": ["username", "email", "password"],
        "onSubmit": {
            "zCRUD": {
                "action": "create",
                "values": "zConv"
            }
        }
    }
})
```

**Current Status:** Shell currently bypasses zDialog and uses zDisplay directly (inefficient).

**Future:** Shell should use zDialog for consistency and caching benefits.

---

## Validation

### Schema-based Validation:

```yaml
# schema.yaml
zUsers:
  email:
    type: str
    required: true
    rules:
      format: email
      error_message: "Please provide a valid email address"
  
  password:
    type: str
    required: true
    rules:
      min_length: 8
      error_message: "Password must be at least 8 characters"
```

### Validation Flow:

1. **Field Definition:** Schema defines validation rules
2. **Input Collection:** zDisplay prompts user
3. **Validation:** zData validates against schema
4. **Error Handling:** Display error messages and retry
5. **Success:** Proceed with submission

---

## Performance & Caching

### Schema Caching:

```python
# First dialog with model
zDialog → zLoader → Read schema.yaml → Parse → Cache
# Time: ~50ms

# Second dialog with same model
zDialog → zLoader → Return from cache (mtime checked)
# Time: ~1ms

# If schema modified externally
zDialog → zLoader → Detect stale (mtime changed) → Reload
# Time: ~50ms (automatic freshness!)
```

### Cache Benefits:

- ✅ **50x faster** for repeated dialogs
- ✅ **Automatic freshness** via mtime checking
- ✅ **Session-scoped** (isolated per user)
- ✅ **LRU eviction** (max 100 files)

---

## Advanced Features

### Multi-step Workflows with zWizard:

```yaml
# ui.main.yaml
UserRegistration:
  zWizard:
    step1:
      zDialog:
        model: "@.schemas.schema.zUsers"
      fields: [username, email, password]
    
    step2:
      zDialog:
        model: "@.schemas.schema.zProfiles"
      fields: [bio, avatar]
    
    step3:
      # Direct CRUD (no wrapper)
      action: create
      tables: [zUsers]
      values: zHat[0]  # ← Data from step1
```

### Conditional Submission:

```yaml
# ui.main.yaml
ConditionalCreate:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username, email, role]
    onSubmit:
      zFunc: "conditional_create(zConv)"
```

```python
# In custom function
def conditional_create(zConv):
    if zConv["role"] == "zAdmin":
        # Require approval
        return "Admin creation requires approval"
    else:
        # Auto-create
        return handle_zCRUD({
            "action": "create",
            "tables": ["zUsers"],
            "values": zConv
        })
```

---

## Error Handling

### Common Errors:

#### **1. Missing Model:**
```yaml
BadDialog:
  zDialog:
    fields: [username]  # ← Missing model!
```
**Error:** `KeyError: 'model'`  
**Fix:** Always specify model path

#### **2. Invalid Model Path:**
```yaml
BadDialog:
  zDialog:
    model: "@.nonexistent.schema.zUsers"
    fields: [username]
```
**Error:** `FileNotFoundError: No zFile found`  
**Fix:** Verify schema file exists

#### **3. Invalid Field:**
```yaml
BadDialog:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [nonexistent_field]  # ← Not in schema!
```
**Error:** Field not found in schema  
**Fix:** Use fields defined in schema

#### **4. Submission Failure:**
```yaml
BadDialog:
  zDialog:
    model: "@.schemas.schema.zUsers"
    fields: [username]
    onSubmit:
      # Direct CRUD (no wrapper)
      action: create
        # Missing tables!
```
**Error:** CRUD operation fails  
**Fix:** Provide complete onSubmit configuration

---

## Best Practices

### 1. Use Dict-based onSubmit:

```yaml
# ✅ Good: Clear and structured
onSubmit:
  # Direct CRUD (no wrapper)
    action: create
    tables: [zUsers]
    values: zConv

# ❌ Avoid: String expressions (legacy)
onSubmit: "zFunc(create_user(zConv))"
```

### 2. Specify Required Fields Only:

```yaml
# ✅ Good: Only collect what's needed
fields: [username, email, password]

# ❌ Avoid: Collecting unnecessary fields
fields: [id, username, email, password, created_at, updated_at]
```

### 3. Use Field-specific Placeholders:

```yaml
# ✅ Good: Explicit field access
onSubmit:
  # Direct CRUD (no wrapper)
    action: update
    where: {id: zConv.id}
    values: {username: zConv.username}

# ❌ Avoid: Passing entire zConv when not needed
onSubmit:
  # Direct CRUD (no wrapper)
    action: update
    values: zConv  # ← Might include fields not meant for update
```

### 4. Leverage Schema Validation:

```yaml
# Define validation in schema
zUsers:
  email:
    type: str
    rules:
      format: email
      error_message: "Invalid email format"

# Dialog automatically validates
zDialog:
  model: "@.schemas.schema.zUsers"
  fields: [email]  # ← Validation applied automatically
```

---

## API Reference

### ZDialog Class:

```python
class ZDialog:
    def __init__(self, walker=None):
        """Initialize dialog subsystem."""
        
    def handle(self, zHorizontal):
        """
        Main entry point for dialog handling.
        
        Args:
            zHorizontal: Dialog configuration dict
            
        Returns:
            zConv or submission result
        """
```

### Functions:

```python
def handle_zDialog(zHorizontal, walker=None):
    """
    Backward-compatible function for dialog handling.
    
    Args:
        zHorizontal: Dialog configuration dict
        walker: Optional walker instance
        
    Returns:
        zConv or submission result
    """
```

### Module Functions:

```python
# dialog_context.py
def create_dialog_context(model, fields, zConv=None):
    """Create dialog context."""

def inject_placeholders(obj, zContext):
    """Replace zConv placeholders with actual values."""

# dialog_submit.py
def handle_submit(submit_expr, zContext, walker=None):
    """Handle onSubmit expression."""

def handle_dict_submit(submit_dict, zContext, walker=None):
    """Handle dict-based onSubmit."""

def handle_string_submit(submit_expr, zContext, walker=None):
    """Handle string-based onSubmit."""
```

---

## Related Subsystems

- **[zData_GUIDE.md](zData_GUIDE.md)** - Data management and CRUD operations
- **[zLoader_GUIDE.md](zLoader_GUIDE.md)** - File loading and caching
- **[zDisplay_GUIDE.md](zDisplay_GUIDE.md)** - Display and rendering
- **[zWalker_GUIDE.md](zWalker_GUIDE.md)** - Walker UI navigation
- **[zVaFiles_GUIDE.md](zVaFiles_GUIDE.md)** - zVaFile format reference

---

**End of Guide**
