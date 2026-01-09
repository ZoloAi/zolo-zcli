# RBAC Testing Demo (v1.5.4 Week 3.3)

This demo tests the declarative RBAC system with `!` prefix directives.

## Quick Test

```bash
cd Demos/rbac_demo

# Test 1: Anonymous user (not logged in)
python testzRBAC.py

# Test 2: User role
python test_user.py

# Test 3: Admin role (no permissions)
python test_admin.py
```

## RBAC Patterns Demonstrated

**Default**: PUBLIC ACCESS (no `zRBAC` = no restrictions)

### Public Access (No RBAC)
```yaml
"^Login":
  zDisplay:
    event: text
    content: "Anyone can access"
```

### Authentication Required
```yaml
"^View Dashboard":
  zRBAC:
    require_auth: true
  zDisplay:
    event: text
    content: "Requires authentication"
```

### Specific Role (auth implied)
```yaml
"^Edit Settings":
  zRBAC:
    require_role: "user"
  zDisplay:
    event: text
    content: "User role required"
```

### Multiple Roles (OR Logic, auth implied)
```yaml
"^Moderator Panel":
  zRBAC:
    require_role: ["admin", "moderator"]
  zDisplay:
    event: text
    content: "Admin OR moderator can access"
```

### Role + Permission (AND Logic, auth implied)
```yaml
"^Delete Data":
  zRBAC:
    require_role: "admin"
    require_permission: "data.delete"
  zDisplay:
    event: text
    content: "Needs admin role AND data.delete permission"
```

## Manual Testing

1. Run zKernel:
```bash
cd Demos/rbac_demo
python -m zKernel
```

2. Change authentication in Python console:
```python
# Set role
z.session["zAuth"]["role"] = "admin"

# Grant permission (for testing)
z.auth.grant_permission("admin001", "data.delete")
z.auth.grant_permission("admin001", "system.shutdown")
```

3. Navigate menu and observe:
- **[ACCESS DENIED]** messages for unauthorized items
- Items are skipped in menu loop
- Access denied reasons are displayed

## Expected Results

| Menu Item        | Anonymous | User | Admin | Admin + Perms |
|------------------|-----------|------|-------|---------------|
| Login            | ✓         | ✓    | ✓     | ✓             |
| Public Info      | ✓         | ✓    | ✓     | ✓             |
| View Dashboard   | ✗         | ✓    | ✓     | ✓             |
| Edit Settings    | ✗         | ✓    | ✗     | ✗             |
| Moderator Panel  | ✗         | ✗    | ✓     | ✓             |
| Delete Data      | ✗         | ✗    | ✗     | ✓             |
| Admin Only       | ✗         | ✗    | ✗     | ✓             |

## Files

- `zUI.rbac_test.yaml` - Test UI with RBAC directives (uses proper zDisplay events)
- `testzRBAC.py` - Test as anonymous user
- `test_user.py` - Test as regular user
- `test_admin.py` - Test as admin (no permissions)

## Proper zKernel Syntax

The demo uses **actual zDisplay events**, not invented strings:

```yaml
"^Menu Item":
  zDisplay:
    event: text      # Valid event from zDisplay._event_map
    content: "..."   # Message to display
    indent: 1        # Indentation level
```

Valid zDisplay events: `text`, `header`, `error`, `warning`, `success`, `info`, `list`, `json_data`, `zTable`, `zDeclare`, etc.

## Implementation

RBAC enforcement happens in:
1. **zParser** - Extracts `!require_*` directives from YAML
2. **zWizard** - Checks access before executing each zKey
3. **zAuth** - Validates roles and permissions

Access denied is graceful:
- Item is skipped in menu loop
- Error message displayed to user
- Event logged for audit trail
