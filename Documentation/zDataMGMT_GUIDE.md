# zData Management Guide

## Introduction

**zData Management** is the comprehensive data handling system of `zolo-zcli`, combining schema design, database operations, form handling, and command-line interfaces into a unified workflow. This guide covers how **zSchema**, **zCRUD**, **zDialog**, and **zShell** work together to provide complete data management capabilities.

> **Note:** This guide covers the data management workflow and subsystem integration. For detailed technical documentation, see the individual subsystem guides: [zCRUD_GUIDE.md](zCRUD_GUIDE.md), [zShell_GUIDE.md](zShell_GUIDE.md), [zWalker_GUIDE.md](zWalker_GUIDE.md).

---

## Data Management Architecture

zData Management follows a layered architecture where each subsystem has a specific role:

```
┌─────────────────────────────────────────────────────────────┐
│                     zData Management                        │
├─────────────────────────────────────────────────────────────┤
│   zSchema (Design) → zCRUD (Operations) → zWalker (UI)      │
│        ↓                    ↓                    ↓          │
│   YAML Schemas         Database Ops        Menu/Form UI     │
│        ↓                    ↓                    ↓          │
│   Validation Rules     SQL Generation      zDialog/zFunc    │
│        ↓                    ↓                    ↓          │
│   Auto-Migration       RGB Tracking        CRUD Integration │
└─────────────────────────────────────────────────────────────┘
                              ↓
                        zShell (Commands)
                              ↓
                    Command-Line Interface
```

### Core Subsystems

| Subsystem | Purpose | Key Features |
|-----------|---------|--------------|
| **zSchema** | Schema design & validation | YAML schemas, validation rules, auto-migration |
| **zCRUD** | Database operations | CREATE, READ, UPDATE, DELETE, UPSERT |
| **zWalker** | UI framework | Menu navigation, zDialog forms, zFunc integration |
| **zShell** | Command interface | CRUD commands, session management |

---

## zSchema - Schema Design

### Schema Structure

**Schema zVaFiles** define table structures, relationships, and validation rules:

```yaml
# schema.users.yaml
zUsers:
  id:
    type: str
    pk: true
    source: generate_id(zU)
  
  username:
    type: str
    unique: true
    required: true
    rules:
      min_length: 3
      max_length: 50
      pattern: ^[a-zA-Z0-9_]+$
  
  email:
    type: str
    unique: true
    required: true
    rules:
      format: email
      error_message: "Invalid email address"
  
  role:
    type: enum
    options: [admin, user, guest]
    default: user
  
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_path: data/app.db
```

### Schema Features

**Field Types:**
- `str` - Text fields with validation rules
- `int` - Integer fields with min/max constraints
- `float` - Decimal numbers
- `datetime` - Timestamps with auto-population
- `enum` - Predefined value lists

**Validation Rules:**
- `required` - Field must be provided
- `unique` - No duplicate values
- `min_length` / `max_length` - String length limits
- `min` / `max` - Number ranges
- `pattern` - Regex validation
- `format` - Email, URL, phone presets
- `error_message` - Custom validation messages

**Relationships:**
```yaml
zPosts:
  user_id:
    type: str
    fk: zUsers.id
    on_delete: CASCADE
    required: true
```

**Indexes:**
```yaml
zUsers:
  # ... fields ...
  
  indexes:
    - name: idx_email
      columns: [email]
      unique: true
    - name: idx_username_role
      columns: [username, role]
```

> **Note:** For detailed schema documentation, see [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md) and [VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)

---

## zCRUD - Database Operations

### Core Operations

**CREATE** - Insert new records:
```python
zRequest = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
result = handle_zCRUD(zRequest)
```

**READ** - Query records:
```python
zRequest = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "where": {"role": "admin"},
    "order_by": "created_at DESC",
    "limit": 10
}
results = handle_zCRUD(zRequest)
```

**UPDATE** - Modify records:
```python
zRequest = {
    "action": "update",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "values": {"role": "admin"},
    "where": {"username": "john"}
}
result = handle_zCRUD(zRequest)
```

**DELETE** - Remove records:
```python
zRequest = {
    "action": "delete",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "where": {"username": "john"}
}
result = handle_zCRUD(zRequest)
```

**UPSERT** - Insert or update:
```python
zRequest = {
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "fields": ["id", "username", "email"],
    "values": ["user1", "john", "john@example.com"]
}
result = handle_zCRUD(zRequest)
```

### Advanced Features

**JOIN Operations:**
```python
zRequest = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "auto_join": True,  # Automatic JOIN based on foreign keys
    "join": [           # Manual JOIN specifications
        {
            "type": "LEFT",
            "table": "zPosts",
            "on": "zUsers.id = zPosts.user_id"
        }
    ]
}
```

**Advanced WHERE Operators:**
```python
zRequest = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "where": {
        "role": ["admin", "moderator"],        # IN
        "created_at": {">": "2024-01-01"},     # Comparison
        "email": {"LIKE": "%@company.com"},    # Pattern
        "deleted_at": None                      # IS NULL
    }
}
```

### Auto-Migration

zCRUD automatically detects schema changes and applies them:

1. **Schema Change Detection** - Compares current schema with database
2. **Automatic Migration** - Executes ALTER TABLE statements
3. **Migration Logging** - Records all changes in history
4. **RGB Tracking** - Updates data integrity metrics

> **Note:** For detailed CRUD documentation, see [zCRUD_GUIDE.md](zCRUD_GUIDE.md)

---

## zWalker - UI Framework

### Walker Integration

**zWalker** provides the UI framework that hosts forms and integrates with CRUD operations through zDialog and zFunc components.

### zDialog - Form Integration

**zDialog** creates interactive forms within Walker that integrate with CRUD operations:

```yaml
# In UI YAML file
zKey_create_user:
  zDialog:
    model: "@.schemas.schema.users"
    fields: ["username", "email", "role"]
    onSubmit: "zFunc(@.utils.users.create_user, zConv)"
```

### Form Processing

**Python function for form submission:**
```python
def create_user(zConv):
    """Create user from dialog form data."""
    zRequest = {
        "action": "create",
        "tables": ["zUsers"],
        "model": "@.schemas.schema.users",
        "fields": ["username", "email", "role"],
        "values": [zConv["username"], zConv["email"], zConv["role"]]
    }
    return handle_zCRUD(zRequest)
```

### Form Features

**Automatic Validation:**
- Field type validation based on schema
- Required field checking
- Custom validation rules
- Error message display

**Data Binding:**
- Form fields map to schema fields
- Automatic type conversion
- Default value population
- Enum option handling

**CRUD Integration:**
- Form submission triggers CRUD operations
- Success/error feedback
- Automatic form reset
- Navigation after submission

### Walker Menu Integration

**Complete User Management Menu:**
```yaml
# In UI YAML file
zKey_user_management:
  zMenu:
    options: ["Create User", "List Users", "Edit User", "Delete User"]
    
    Create User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username", "email", "role"]
        onSubmit: "zFunc(@.utils.users.create_user, zConv)"
    
    List Users:
      zFunc: "zFunc(@.utils.users.list_users)"
    
    Edit User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username", "email", "role"]
        prefill: "zFunc(@.utils.users.get_user, {id: zContext.user_id})"
        onSubmit: "zFunc(@.utils.users.update_user, zConv)"
    
    Delete User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username"]
        onSubmit: "zFunc(@.utils.users.delete_user, zConv)"
```

### zFunc - Direct CRUD Integration

**Execute CRUD operations directly from Walker menus:**
```yaml
^Create_User: "zFunc(@.utils.users.create_user, {username: 'john', email: 'john@example.com'})"
^List_Users: "zFunc(@.utils.users.list_users)"
^Update_User: "zFunc(@.utils.users.update_user, {id: 'user1', role: 'admin'})"
^Delete_User: "zFunc(@.utils.users.delete_user, {username: 'john'})"
```

> **Note:** For detailed Walker documentation, see [zWalker_GUIDE.md](zWalker_GUIDE.md)

---

## zShell - Command Interface

### CRUD Commands

Access database operations through Shell mode:

```bash
# Start Shell mode
zolo-zcli --shell

# Configure session
session set zWorkspace /path/to/project
session set zAuth authenticated_user

# CREATE operations
crud create zUsers --username "john" --email "john@example.com"
crud create zUsers --model @.schemas.schema.users --username "jane" --email "jane@example.com"

# READ operations
crud read zUsers
crud read zUsers --limit 10
crud read zUsers --where "role=admin"
crud read zUsers --model @.schemas.schema.users

# UPDATE operations
crud update zUsers --set role=admin --where username=john
crud update zUsers --set email=new@example.com --where id=user1

# DELETE operations
crud delete zUsers --where username=john
crud delete zUsers --where "created_at < '2023-01-01'"

# UPSERT operations (v1.3.0+)
crud upsert zUsers --id user1 --username john --email john@example.com

# Schema management
alter_table zUsers drop_column old_field
alter_table zUsers rename_column username user_name
```

### Session Management

**Session Configuration:**
```bash
# View current session
session info

# Set session fields
session set zWorkspace /path/to/project
session set zAuth authenticated_user
session set zMode Terminal

# Get session values
session get zWorkspace
session get zAuth
```

**Session Requirements:**
- `zWorkspace` - Project workspace path (for zPath resolution)
- `zAuth` - Authentication context (if required)
- `zMode` - Operation mode (Terminal/zGUI)

### Command Features

**Parameterized Queries:**
- All commands use parameterized queries for SQL injection protection
- Automatic type conversion based on schema
- Validation applied before database operations

**Error Handling:**
- Detailed error messages for troubleshooting
- Graceful handling of constraint violations
- Transaction rollback on errors

**History & Logging:**
- Command history within session
- All operations logged for debugging
- Performance metrics tracking

> **Note:** For detailed Shell documentation, see [zShell_GUIDE.md](zShell_GUIDE.md)

---

## Data Management Workflow

### 1. Schema Design

**Start with schema definition:**
```yaml
# schema.users.yaml
zUsers:
  id:
    type: str
    pk: true
    source: generate_id(zU)
  
  username:
    type: str
    unique: true
    required: true
    rules:
      min_length: 3
      max_length: 50
  
  email:
    type: str
    unique: true
    required: true
    rules:
      format: email

Meta:
  Data_Type: sqlite
  Data_path: data/users.db
```

### 2. Database Operations

**Use zCRUD for data operations:**
```python
# Create user
result = handle_zCRUD({
    "action": "create",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
})

# Query users
users = handle_zCRUD({
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.users",
    "where": {"role": "admin"}
})
```

### 3. Walker UI Integration

**Create Walker UI with forms and menus:**
```yaml
# ui.management.yaml
zKey_user_management:
  zMenu:
    options: ["Create User", "List Users", "Edit User", "Delete User"]
    
    Create User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username", "email", "role"]
        onSubmit: "zFunc(@.utils.users.create_user, zConv)"
    
    List Users:
      zFunc: "zFunc(@.utils.users.list_users)"
    
    Edit User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username", "email", "role"]
        prefill: "zFunc(@.utils.users.get_user, {id: zContext.user_id})"
        onSubmit: "zFunc(@.utils.users.update_user, zConv)"
    
    Delete User:
      zDialog:
        model: "@.schemas.schema.users"
        fields: ["username"]
        onSubmit: "zFunc(@.utils.users.delete_user, zConv)"
```

### 4. Command-Line Access

**Use zShell for administration:**
```bash
# Start shell
zolo-zcli --shell

# Configure session
session set zWorkspace /path/to/project

# Manage data
crud create zUsers --username admin --email admin@example.com
crud read zUsers --where "role=admin"
crud update zUsers --set role=superadmin --where username=admin
```

---

## Integration Patterns

### Schema → CRUD → Walker Flow

1. **Define Schema** - Create YAML schema with validation rules
2. **Auto-Migration** - zCRUD automatically creates/updates database tables
3. **Walker UI** - Create Walker UI with zMenu and zDialog components
4. **Form Generation** - zDialog uses schema for form field definitions
5. **Validation** - Both CRUD and Walker use same validation rules
6. **Data Operations** - Forms submit to CRUD operations via zFunc

### Shell → Walker Integration

1. **Shell Configuration** - Set up session in Shell mode
2. **Walker Launch** - Use `walker run` to start UI mode
3. **Shared Session** - Both modes use same session and authentication
4. **Seamless Switching** - Exit Walker to return to Shell

### Multi-Environment Support

1. **Development** - Use Shell mode for testing and debugging
2. **Production** - Use Walker mode for user interfaces
3. **Administration** - Use Shell mode for maintenance tasks
4. **Integration** - Use Python API for automated processes

---

## Best Practices

### Schema Design

1. **Start Simple** - Begin with basic fields, add complexity gradually
2. **Use Validation** - Define comprehensive validation rules
3. **Plan Relationships** - Design foreign keys and constraints carefully
4. **Add Indexes** - Include indexes for frequently queried fields
5. **Document Changes** - Keep schema files well-documented

### CRUD Operations

1. **Always Validate** - Use schema validation for all operations
2. **Handle Errors** - Implement proper error handling and recovery
3. **Use Transactions** - Leverage automatic transaction safety
4. **Monitor Performance** - Use indexes and query optimization
5. **Track Changes** - Review migration history regularly

### Form Design

1. **Schema-Driven** - Use schema definitions for form fields
2. **User-Friendly** - Provide clear labels and validation messages
3. **Progressive Enhancement** - Start with basic forms, add features
4. **Error Handling** - Display validation errors clearly
5. **Success Feedback** - Confirm successful operations

### Development Workflow

1. **Schema First** - Define schema before implementing operations
2. **Test Incrementally** - Start with basic operations, add complexity
3. **Use Auto-Migration** - Let zCRUD handle schema evolution
4. **Monitor Health** - Check RGB data integrity regularly
5. **Document Everything** - Keep schemas and operations documented

---

## Troubleshooting

### Common Issues

**Schema Problems:**
- **Invalid YAML** - Check YAML syntax and structure
- **Missing Meta** - Ensure schema has Meta section with Data_Type and Data_path
- **Invalid zPath** - Verify zPath resolution works correctly

**CRUD Errors:**
- **Table Missing** - Ensure schema exists and tables are created
- **Validation Failed** - Check field types and validation rules
- **Foreign Key Violations** - Verify referenced records exist

**Form Issues:**
- **Field Mismatch** - Ensure form fields match schema fields
- **Validation Errors** - Check validation rules and error messages
- **CRUD Integration** - Verify form submission functions work correctly

**Shell Problems:**
- **Session Not Set** - Ensure zWorkspace and other required fields are set
- **Command Errors** - Check command syntax and parameters
- **Permission Issues** - Verify database file permissions

### Debugging Steps

1. **Check Logs** - Review zCLI logs for detailed error information
2. **Validate Schema** - Use YAML validator for schema files
3. **Test zPath** - Verify zPath resolution works correctly
4. **Test Incrementally** - Start with simple operations
5. **Review Documentation** - Check relevant subsystem guides

---

## Related Documentation

For detailed subsystem documentation:

- **[zCRUD_GUIDE.md](zCRUD_GUIDE.md)** - Complete CRUD operations reference
- **[zShell_GUIDE.md](zShell_GUIDE.md)** - Shell mode commands and usage
- **[zWalker_GUIDE.md](zWalker_GUIDE.md)** - Walker mode and form integration
- **[CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)** - Detailed CRUD features
- **[VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)** - Validation rules reference
- **[WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)** - Advanced query operators
- **[JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)** - JOIN operations

---

**zData Management - Unified data handling across schema, CRUD, forms, and commands** 📊
