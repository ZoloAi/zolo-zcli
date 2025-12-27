# zCLI/subsystems/zWizard/zWizard_modules/wizard_rbac.py

"""
Wizard RBAC - Role-Based Access Control for Wizard Steps
=========================================================

Enforces RBAC (Role-Based Access Control) at the zKey level during wizard and
walker execution. Each step can declare authentication and authorization
requirements via `_rbac` metadata.

Core Responsibilities
--------------------
1. **Authentication Check**: Verify user is logged in (`require_auth`)
2. **Role Check**: Verify user has required role(s) (`require_role`)
3. **Permission Check**: Verify user has required permission(s) (`require_permission`)
4. **Access Denial**: Display user-friendly access denied messages
5. **Audit Logging**: Log all access denials for security audit

RBAC Architecture
----------------
### Four-Level Hierarchy
1. **Public Access**: No `_rbac` metadata = accessible to all users
2. **Guest-Only Access**: `zGuest: true` = unauthenticated users only (login/register pages)
3. **Authenticated Access**: `require_auth: true` = logged-in users only
4. **Authorized Access**: `require_role` or `require_permission` = specific users

### Check Order (Short-Circuit)
1. No `_rbac`? → Access granted (public)
2. No auth subsystem? → Access denied (fail-safe)
3. `require_auth` + not authenticated? → Access denied
4. `require_role` + no role? → Access denied
5. `require_permission` + no permission? → Access denied
6. All checks passed? → Access granted

RBAC Metadata Format
-------------------
### In zUI YAML Files
```yaml
^Admin_Feature:
  _rbac:
    require_auth: true                    # Must be logged in
    require_role: "admin"                 # Must have "admin" role
    require_permission: "manage_users"    # Must have permission
  zDisplay:
    event: text
    content: "Admin-only feature"
```

### Metadata Fields
- **zGuest** (bool): Require guest (unauthenticated) - denies authenticated users
- **require_auth** (bool): Require authentication
- **require_role** (str | list): Require role(s) - ANY match grants access
- **require_permission** (str | list): Require permission(s) - ANY match grants access

### Multiple Roles/Permissions (OR Logic)
```yaml
_rbac:
  require_role: ["admin", "moderator"]  # admin OR moderator
  require_permission: ["read", "write"] # read OR write
```

Access Denial Flow
-----------------
### User Experience (Terminal + Bifrost)
```
[ACCESS DENIED] ^Delete_User
  Reason: Role required: admin
  Tip: Check your role/permissions or log in
```

### Display Events Generated
1. Empty text line (spacing)
2. Error event with "ACCESS DENIED" header
3. Text event with denial reason
4. Text event with user tip
5. Empty text line (spacing)

### Logging
```
[RBAC] Access denied for '^Delete_User': Role required: admin
```

Usage Examples
-------------
### Example 1: Guest-Only Access (Login/Register Pages)
```yaml
^zLogin:
  _rbac:
    zGuest: true  # Only show if NOT logged in
  zDialog:
    title: "User Login"
    fields: [email, password]
```

### Example 2: Authentication Only
```yaml
^Profile:
  _rbac:
    require_auth: true
  zDisplay:
    event: text
    content: "Your profile: {{ session.username }}"
```

### Example 2: Role Requirement
```yaml
^Admin_Panel:
  _rbac:
    require_role: "admin"  # Implies authentication
  zDisplay:
    event: text
    content: "Admin panel access"
```

### Example 3: Permission Requirement
```yaml
^Delete_User:
  _rbac:
    require_permission: "users.delete"
  zData:
    operation: delete
    model: "users"
    where: {id: "{{ zHat.user_id }}"}
```

### Example 4: Multiple Requirements
```yaml
^Sensitive_Data:
  _rbac:
    require_auth: true
    require_role: ["admin", "auditor"]
    require_permission: ["data.read", "data.export"]
  zDisplay:
    event: text
    content: "Sensitive data export"
```

Integration with zAuth
----------------------
### Authentication Methods
- `is_authenticated()`: Check if user is logged in
- `has_role(role)`: Check if user has specific role
- `has_permission(permission)`: Check if user has permission

### Context-Aware RBAC
- **zSession Mode**: Session-based authentication
- **Application Mode**: Application-level authentication
- **Dual Mode**: Hybrid authentication context

Error Handling
-------------
- **No auth subsystem**: Fail-safe to "access_denied"
- **Invalid RBAC metadata**: Treated as public (no restrictions)
- **Display unavailable**: Access still checked, message not shown
- **Logger unavailable**: Access still checked, not logged

Constants Reference
-------------------
- RBAC_ACCESS_GRANTED, RBAC_ACCESS_DENIED: Return values
- RBAC_KEY: Dict key for RBAC metadata (_rbac)
- RBAC_REQUIRE_AUTH, RBAC_REQUIRE_ROLE, RBAC_REQUIRE_PERMISSION: RBAC fields
- LOG_MSG_*: Log messages for various scenarios
- MSG_AUTH_REQUIRED, MSG_ROLE_REQUIRED, MSG_PERMISSION_REQUIRED: Display messages
- EVENT_*: Display event types

Dependencies
-----------
- **zAuth**: Authentication and authorization checks
- **zDisplay**: User-friendly access denial messages
- **Logger**: Security audit logging

Best Practices
-------------
1. **Principle of Least Privilege**: Only add RBAC when necessary
2. **Clear Denial Messages**: Use descriptive role/permission names
3. **Audit Trail**: Review RBAC logs regularly for security issues
4. **Graceful Degradation**: UI should work without auth (public features)
5. **Test Coverage**: Test with multiple user roles

Layer: 2, Position: 2 (zWizard subsystem)
Week: 6.14
Version: v1.5.4 Phase 1 (Industry-Grade, RBAC from Week 3.3)
"""

from typing import Any, Optional

__all__ = ["check_rbac_access", "display_access_denied", "display_access_denied_zguest"]


# ═══════════════════════════════════════════════════════════════════════════
# MODULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# RBAC Access Results
RBAC_ACCESS_GRANTED: str = "access_granted"
RBAC_ACCESS_DENIED: str = "access_denied"
RBAC_ACCESS_DENIED_ZGUEST: str = "access_denied_zguest"  # Friendly redirect (no pause needed)

# RBAC Metadata Keys
RBAC_KEY: str = "_rbac"
RBAC_REQUIRE_AUTH: str = "require_auth"
RBAC_REQUIRE_ROLE: str = "require_role"
RBAC_REQUIRE_PERMISSION: str = "require_permission"
RBAC_ZGUEST: str = "zGuest"  # Guest-only access (unauthenticated users)

# Log Messages
LOG_MSG_NO_AUTH_SUBSYSTEM: str = "[RBAC] No auth subsystem available, denying access"
LOG_MSG_ACCESS_GRANTED: str = "[RBAC] Access granted for %s"
LOG_MSG_ACCESS_DENIED: str = "[RBAC] Access denied for '%s': %s"

# Display Messages
MSG_AUTH_REQUIRED: str = "Authentication required"
MSG_ROLE_REQUIRED: str = "Role required: %s"
MSG_PERMISSION_REQUIRED: str = "Permission required: %s"
MSG_ZGUEST_ONLY: str = "You're already logged in!"
MSG_ZGUEST_REDIRECT: str = "This page is for guests only. Redirecting..."
MSG_ACCESS_DENIED_HEADER: str = "[ACCESS DENIED] %s"
MSG_DENIAL_REASON: str = "Reason: %s"
MSG_DENIAL_TIP: str = "Tip: Check your role/permissions or log in"

# Display Event Types
EVENT_TEXT: str = "text"
EVENT_ERROR: str = "error"

# Display Event Keys
KEY_EVENT: str = "event"
KEY_CONTENT: str = "content"
KEY_INDENT: str = "indent"
KEY_BREAK_AFTER: str = "break_after"

# Indentation Levels
INDENT_LEVEL_0: int = 0
INDENT_LEVEL_1: int = 1
INDENT_LEVEL_2: int = 2

# Formatting
FORMAT_ONE_OF: str = "one of %s"


def check_rbac_access(
    key: str,
    value: Any,
    zcli: Optional[Any],
    walker: Optional[Any],
    logger: Any,
    display: Optional[Any]
) -> str:
    """
    Check RBAC access for a zKey before execution (v1.5.4 Week 3.3).
    
    Args:
        key: zKey name (e.g., "^Delete User")
        value: zKey value (parsed item with potential _rbac metadata)
        zcli: zCLI instance (if direct mode)
        walker: zWalker instance (if walker mode)
        logger: Logger instance
        display: Display instance
    
    Returns:
        str: "access_granted" or "access_denied"
    """
    # Extract RBAC metadata (if it exists)
    rbac = None
    if isinstance(value, dict):
        rbac = value.get(RBAC_KEY)
    
    # No RBAC requirements = public access
    if not rbac:
        return RBAC_ACCESS_GRANTED
    
    # Get zCLI instance (from walker or direct)
    zcli_instance = walker.zcli if walker else zcli
    if not zcli_instance or not hasattr(zcli_instance, 'auth'):
        logger.warning(LOG_MSG_NO_AUTH_SUBSYSTEM)
        return RBAC_ACCESS_DENIED
    
    # Check zGuest (guest-only access - user must NOT be authenticated)
    if rbac.get(RBAC_ZGUEST):
        if zcli_instance.auth.is_authenticated():
            # User is authenticated but this is guest-only
            # This is a GOOD thing - user is logged in! Just redirect gracefully
            display_access_denied_zguest(key, MSG_ZGUEST_ONLY, display, logger)
            return RBAC_ACCESS_DENIED_ZGUEST  # Special return code (no pause needed)
    
    # Check require_auth (must be authenticated)
    if rbac.get(RBAC_REQUIRE_AUTH):
        if not zcli_instance.auth.is_authenticated():
            display_access_denied(key, MSG_AUTH_REQUIRED, display, logger)
            return RBAC_ACCESS_DENIED
    
    # Check require_role (implies authentication)
    required_role = rbac.get(RBAC_REQUIRE_ROLE)
    if required_role is not None:
        # Role requirement implies authentication
        if not zcli_instance.auth.is_authenticated():
            display_access_denied(key, MSG_AUTH_REQUIRED, display, logger)
            return RBAC_ACCESS_DENIED
        
        if not zcli_instance.auth.has_role(required_role):
            role_str = required_role if isinstance(required_role, str) else (FORMAT_ONE_OF % required_role)
            display_access_denied(key, MSG_ROLE_REQUIRED % role_str, display, logger)
            return RBAC_ACCESS_DENIED
    
    # Check require_permission (implies authentication)
    required_permission = rbac.get(RBAC_REQUIRE_PERMISSION)
    if required_permission:
        # Permission requirement implies authentication
        if not zcli_instance.auth.is_authenticated():
            display_access_denied(key, MSG_AUTH_REQUIRED, display, logger)
            return RBAC_ACCESS_DENIED
        
        if not zcli_instance.auth.has_permission(required_permission):
            perm_str = required_permission if isinstance(required_permission, str) else (FORMAT_ONE_OF % required_permission)
            display_access_denied(key, MSG_PERMISSION_REQUIRED % perm_str, display, logger)
            return RBAC_ACCESS_DENIED
    
    # All checks passed
    logger.debug(LOG_MSG_ACCESS_GRANTED, key)
    return RBAC_ACCESS_GRANTED


def display_access_denied(
    key: str,
    reason: str,
    display: Optional[Any],
    logger: Any
) -> None:
    """
    Display access denied message (Terminal + zBifrost compatible).
    
    Args:
        key: zKey name that was denied
        reason: Reason for denial
        display: Display instance
        logger: Logger instance
    """
    if display:
        # Display clear access denied message (no break to avoid input prompt in tests)
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: "",
            KEY_INDENT: INDENT_LEVEL_0,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_ERROR,
            KEY_CONTENT: MSG_ACCESS_DENIED_HEADER % key,
            KEY_INDENT: INDENT_LEVEL_1
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: MSG_DENIAL_REASON % reason,
            KEY_INDENT: INDENT_LEVEL_2,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: MSG_DENIAL_TIP,
            KEY_INDENT: INDENT_LEVEL_2,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: "",
            KEY_INDENT: INDENT_LEVEL_0,
            KEY_BREAK_AFTER: False
        })
    
    # Log the denial
    logger.warning(LOG_MSG_ACCESS_DENIED, key, reason)


def display_access_denied_zguest(
    key: str,
    reason: str,
    display: Optional[Any],
    logger: Any
) -> None:
    """
    Display friendly redirect message for zGuest (guest-only) pages.
    
    This is NOT an error - it's a feature! User is logged in, which is good.
    We just redirect them away from login/register pages gracefully.
    
    Args:
        key: zKey name that was denied
        reason: Reason for denial
        display: Display instance
        logger: Logger instance
    """
    if display:
        # Display friendly redirect message (positive tone!)
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: "",
            KEY_INDENT: INDENT_LEVEL_0,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: "✓ " + MSG_ZGUEST_ONLY,
            KEY_INDENT: INDENT_LEVEL_1,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: MSG_ZGUEST_REDIRECT,
            KEY_INDENT: INDENT_LEVEL_1,
            KEY_BREAK_AFTER: False
        })
        display.handle({
            KEY_EVENT: EVENT_TEXT,
            KEY_CONTENT: "",
            KEY_INDENT: INDENT_LEVEL_0,
            KEY_BREAK_AFTER: False
        })
    
    # Log as info (not a warning - this is expected behavior!)
    logger.info(LOG_MSG_ACCESS_DENIED, key, reason)


