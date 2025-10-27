# zCLI Agent Reference (v1.5.4+)

**Target**: AI coding assistants | **Focus**: Layer 0 Production-Ready Patterns

**Latest**: v1.5.4 - Layer 0 Complete (70% coverage, 907 tests passing)

---

## 3 Steps - Always

1. Import zCLI
2. Create zSpark
3. RUN walker

```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"  # OR "zBifrost"
})

z.walker.run()
```

**Note:** All zCLI sparks work identically for Terminal and zBifrost. Always use a Terminal spark for terminal feedback. If in zBifrost mode, create a separate Terminal test spark.

---

## Code Rules (STRICT)

- ❌ NO `print()` statements - use `z.display` or `z.logger`
- ❌ NO verbose comments - code should be self-documenting
- ✅ Keep code slim and focused
- ✅ Use zCLI's built-in tools for all output

---

## zUI File Structure (CRITICAL FOR AGENTS)

**⚠️ COMMON AGENT MISTAKE**: Inventing syntax that "looks right" but doesn't work!

### ✅ Valid zUI Events (FROM zDispatch)

**ONLY use these declarative events in zUI files:**

```yaml
# Data operations
"^List Users":
  zData:
    model: "@.zSchema.users"
    action: read
    table: users

# Display output
"^Show Info":
  zDisplay:
    event: text        # Valid: text, header, error, warning, success, info
    content: "Hello!"
    indent: 1

# User input
"^Get User":
  zDialog:
    model: UserForm
    fields: ["username", "email"]
    onSubmit:
      zData:           # onSubmit MUST be a valid zDispatch event!
        action: insert
        table: users
        data:
          username: "zConv.username"

# Function calls
"^Process":
  zFunc: "&plugin_name.function_name"

# Navigation
"^Go Back":
  zLink: "../previous_menu"

# Wizard steps
"^Multi Step":
  zWizard:
    steps: ["step1", "step2"]
```

### ❌ INVALID Patterns (DO NOT USE)

```yaml
# ❌ WRONG: Plain string in onSubmit (not a valid event)
"^Login":
  zDialog:
    fields: ["username"]
    onSubmit:
      "Login submitted"  # ❌ WRONG! Not a zDispatch event!

# ❌ WRONG: Invented event name
"^Show Data":
  zCustomEvent:        # ❌ WRONG! Not in zDispatch
    data: "..."

# ❌ WRONG: Missing event type in zDisplay
"^Display":
  zDisplay:
    content: "..."     # ❌ WRONG! Missing "event: text"
```

### Valid zDisplay Events

From `zDisplay._event_map` (the ONLY valid events):

**Output**: `text`, `header`, `line`
**Signals**: `error`, `warning`, `success`, `info`, `zMarker`
**Data**: `list`, `json`, `json_data`, `zTable`
**System**: `zDeclare`, `zSession`, `zCrumbs`, `zMenu`, `zDialog`
**Inputs**: `selection`, `read_string`, `read_password`
**Primitives**: `write_raw`, `write_line`, `write_block`

### How to Verify

Before writing zUI files, check:
1. **zDispatch/launcher.py** - What events does `_launch_dict()` recognize?
2. **zDisplay/zDisplay.py** - What events are in `_event_map`?
3. **Existing zUI files** - Use them as templates (e.g., `Demos/User Manager/zUI.users_csv.yaml`)

**Remember**: zCLI is **declarative** - you can't invent syntax, only use what the dispatcher recognizes!

---

## zAuth Modular Architecture (v1.5.4 Refactor)

### Overview

**zAuth** uses a modular architecture with the **facade pattern** for clean separation of concerns:

**Module Structure**:
```
zCLI/subsystems/zAuth/
├── zAuth.py (facade orchestrator, 302 lines)
└── zAuth_modules/
    ├── password_security.py (bcrypt hashing - 118 lines)
    ├── session_persistence.py (SQLite sessions - 213 lines)
    ├── authentication.py (login/logout - 193 lines)
    └── rbac.py (roles & permissions - 268 lines)
```

### Module Responsibilities

1. **password_security.py**: Pure bcrypt hashing (no dependencies)
2. **session_persistence.py**: SQLite session management (7-day expiry)
3. **authentication.py**: Login/logout operations (local + remote)
4. **rbac.py**: Role-Based Access Control with permissions

### Public API (Unchanged)

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# All methods work identically (facade delegates to modules)
hashed = z.auth.hash_password("password")          # → password_security
z.auth.login(username, password, persist=True)     # → authentication + session_persistence
z.auth.has_role("admin")                           # → rbac
z.auth.grant_permission(user_id, "users.delete")  # → rbac
```

### Benefits

- 📉 Main file: 719 lines → 302 lines (58% reduction)
- ✅ Testable in isolation (each module independent)
- ✅ Clear separation of concerns
- ✅ Extensible (add OAuth, JWT, 2FA easily)
- ✅ Backwards compatible (facade pattern)

---

## RBAC Directives (v1.5.4 Week 3.3)

**Default**: PUBLIC ACCESS (no `_rbac` = no restrictions)  
**Only add `_rbac` when you need to RESTRICT access**

### ✅ Valid RBAC Patterns (Inline)

```yaml
zVaF:
  ~Root*: ["^Login", "^View Data", "^Edit Data", "^Admin Panel"]
  
  # Public access (no _rbac specified)
  "^Login":
    zDisplay:
      event: text
      content: "Anyone can login"
  
  # Requires authentication (any role)
  "^View Data":
    _rbac:
      require_auth: true
    zDisplay:
      event: text
      content: "Must be logged in"
  
  # Specific role (auth implied)
  "^Edit Data":
    _rbac:
      require_role: "user"
    zDisplay:
      event: text
      content: "User role required"
  
  # Multiple roles + permission (auth implied)
  "^Admin Panel":
    _rbac:
      require_role: ["admin", "moderator"]
      require_permission: "admin.access"
    zDisplay:
      event: text
      content: "Admin/moderator + permission required"
```

### RBAC Directive Types

**Authentication Only**:
```yaml
_rbac:
  require_auth: true  # User must be logged in (any role)
```

**Single Role** (auth implied):
```yaml
_rbac:
  require_role: "admin"  # User must have "admin" role
```

**Multiple Roles** (OR logic, auth implied):
```yaml
_rbac:
  require_role: ["admin", "moderator"]  # User must have ANY of these roles
```

**Permission Required** (auth implied):
```yaml
_rbac:
  require_permission: "users.delete"  # User must have this permission
```

**Combined** (AND logic, auth implied):
```yaml
_rbac:
  require_role: "admin"
  require_permission: "data.delete"  # User must have BOTH role AND permission
```

### Key Design Principles

1. **Default is PUBLIC** - No `_rbac` = accessible to everyone
2. **Inline per item** - RBAC is defined directly in each zKey's dict
3. **Auth is implied** - `require_role` or `require_permission` automatically requires authentication
4. **Clean syntax** - Only add restrictions where needed, not on every item

### Implementation Notes

- **Enforcement**: Checked in `zWizard.execute_loop()` before dispatch
- **Access denied**: User sees clear message with reason, item is skipped
- **No conflict with `!` suffix**: `_rbac` is a dict key, not a YAML directive
- **Logging**: All access denials are logged for audit trail

---

## Data Validation (Week 5.1 - zData)

**zCLI provides comprehensive validation through `DataValidator` class (191 lines)**

### ✅ Validation Rules (Already Implemented!)

All validation rules are defined under the `rules:` key in `zSchema` files:

```yaml
# In zSchema.users.yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
      min_length: 3
      max_length: 20
  
  email:
    type: str
    required: true
    rules:
      format: email
      max_length: 255
      error_message: "Please enter a valid email address (user@domain.com)"
  
  age:
    type: int
    rules:
      min: 18
      max: 120
      error_message: "Age must be between 18 and 120"
```

### Available Validation Rules

| Rule | Type | Example | Description |
|------|------|---------|-------------|
| `required` | All | `required: true` | Field must be present (top-level, not in `rules:`) |
| `min_length` | String | `min_length: 3` | Minimum string length |
| `max_length` | String | `max_length: 100` | Maximum string length |
| `min` | Numeric | `min: 0` | Minimum value |
| `max` | Numeric | `max: 999.99` | Maximum value |
| `pattern` | String | `pattern: "^[a-z0-9-]+$"` | Regex pattern (IMPLEMENTED!) |
| `pattern_message` | String | `pattern_message: "Use lowercase only"` | Custom regex error message |
| `format` | String | `format: email` | Built-in validator (email, url, phone) |
| `error_message` | All | `error_message: "Custom error"` | Override default error message |

### Built-in Format Validators

```yaml
email:
  type: str
  rules:
    format: email  # Validates user@domain.com

website:
  type: str
  rules:
    format: url  # Validates http://example.com or https://example.com

phone:
  type: str
  rules:
    format: phone  # Validates 10-15 digits (accepts +, spaces, dashes, parentheses)
```

### Common Regex Patterns

```yaml
# Username (alphanumeric + underscore, 3-20 chars)
username:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9_]{3,20}$"
    pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"

# URL Slug (lowercase, hyphens)
slug:
  type: str
  rules:
    pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    pattern_message: "Slug must be lowercase letters, numbers, and hyphens (e.g., my-blog-post)"

# Product SKU (ABC-1234 format)
sku:
  type: str
  rules:
    pattern: "^[A-Z]{2,4}-[0-9]{4,6}$"
    pattern_message: "SKU must follow format: ABC-1234 (2-4 uppercase letters, dash, 4-6 digits)"

# Tags (comma-separated words)
tags:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9,\\s]+$"
    pattern_message: "Tags must be comma-separated words (e.g., python, coding, tutorial)"
```

### Validation Execution Order

DataValidator checks rules in this order:
1. **required** - Is the field present? (if `required: true`)
2. **String rules** - `min_length`, `max_length`
3. **Numeric rules** - `min`, `max`
4. **Pattern rules** - `pattern` (regex)
5. **Format rules** - `format` (email, url, phone)

If any rule fails, validation stops and returns the error message.

### Automatic Validation

Validation happens automatically for:

```python
# INSERT - All fields checked, required fields enforced
result = z.data.insert("users", {
    "username": "invalid user!",  # Fails pattern validation
    "email": "user@example.com"
})
# Returns: {"error": {"username": "Username must be 3-20 characters (letters, numbers, underscore only)"}}

# UPDATE - Only provided fields checked, required fields NOT enforced
result = z.data.update("users", {"id": 1}, {
    "email": "invalid-email"  # Fails format validation
})
# Returns: {"error": {"email": "Invalid email address format"}}
```

### Combining Multiple Rules

You can stack multiple validation rules:

```yaml
username:
  type: str
  required: true
  rules:
    min_length: 3      # Checked first
    max_length: 20     # Checked second
    pattern: "^[a-zA-Z0-9_]+$"  # Checked third
    pattern_message: "Username must contain only letters, numbers, and underscores"

email:
  type: str
  required: true
  rules:
    format: email      # Built-in email validator
    max_length: 255    # Also enforce max length
    error_message: "Please enter a valid email address (max 255 characters)"

price:
  type: float
  required: true
  rules:
    min: 0.01          # At least 1 cent
    max: 999999.99     # At most $999,999.99
    error_message: "Price must be between $0.01 and $999,999.99"
```

### Common Validation Patterns

**User Registration:**
```yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
  
  email:
    type: str
    required: true
    rules:
      format: email
      max_length: 255
  
  password_hash:
    type: str
    required: true
    rules:
      min_length: 60  # bcrypt hash length
  
  age:
    type: int
    rules:
      min: 18
      max: 120
```

**Product Inventory:**
```yaml
products:
  sku:
    type: str
    required: true
    rules:
      pattern: "^[A-Z]{2,4}-[0-9]{4,6}$"
      pattern_message: "SKU must follow format: ABC-1234"
  
  price:
    type: float
    required: true
    rules:
      min: 0.01
      max: 999999.99
      error_message: "Price must be between $0.01 and $999,999.99"
  
  stock:
    type: int
    default: 0
    rules:
      min: 0
      error_message: "Stock cannot be negative"
```

**Blog Posts:**
```yaml
posts:
  title:
    type: str
    required: true
    rules:
      min_length: 5
      max_length: 200
  
  slug:
    type: str
    required: true
    rules:
      pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      pattern_message: "Slug must be lowercase letters, numbers, and hyphens"
  
  tags:
    type: str
    rules:
      pattern: "^[a-zA-Z0-9,\\s]+$"
      pattern_message: "Tags must be comma-separated words"
```

### Testing Validation

```python
# Test pattern validation
result = z.data.insert("users", {
    "username": "invalid user!",  # Contains space and exclamation
    "email": "user@example.com"
})
assert "error" in result
assert "username" in result["error"]

# Test format validation
result = z.data.insert("users", {
    "username": "validuser",
    "email": "not-an-email"  # Invalid email format
})
assert result["error"]["email"] == "Invalid email address format"

# Test numeric range
result = z.data.insert("users", {
    "username": "validuser",
    "email": "user@example.com",
    "age": 150  # Exceeds max
})
assert "Age must be between 18 and 120" in result["error"]["age"]
```

### Common Validation Mistakes

**❌ Wrong: Using `.yaml` extension in zPath**
```python
z.loader.handle('@.zSchema.users.yaml')  # WRONG - double extension!
```

**✅ Right: No extension (framework auto-adds .yaml)**
```python
z.loader.handle('@.zSchema.users')  # Correct
```

**❌ Wrong: Forgetting `rules:` key**
```yaml
username:
  type: str
  pattern: "^[a-z]+$"  # WRONG - pattern must be under rules:
```

**✅ Right: All validation rules under `rules:` key**
```yaml
username:
  type: str
  rules:
    pattern: "^[a-z]+$"  # Correct
```

**❌ Wrong: Using `validator:` for built-in formats**
```yaml
email:
  type: str
  rules:
    validator: "email"  # WRONG - use format: email
```

**✅ Right: Use `format:` for built-in validators**
```yaml
email:
  type: str
  rules:
    format: email  # Correct
```

---

## zDialog Auto-Validation (Week 5.2 - CRITICAL FEATURE!)

**🎯 Forms now auto-validate against zSchema rules BEFORE submission!**

### The Problem (Before Week 5.2)

Forms would collect data and submit it to the server, where validation would happen. If validation failed, the user would get an error AFTER the round-trip.

❌ **Poor UX**: User fills form → submits → server validates → error returned  
❌ **Wasted round-trip**: Network delay for validation that could happen client-side  
❌ **Inconsistent**: Manual validation code in plugins  

### The Solution (Week 5.2)

When `model: '@.zSchema.users'` is specified in a `zDialog`, the form data is **automatically validated** against the schema's rules **before** the `onSubmit` action executes.

✅ **Great UX**: User fills form → auto-validates → errors shown BEFORE submit  
✅ **No wasted round-trip**: Immediate feedback  
✅ **Declarative**: No manual validation code needed  

### How to Enable Auto-Validation

Simply add `model: '@.zSchema.table_name'` to your `zDialog`:

```yaml
# In zUI.users.yaml
"^Register User":
  zDialog:
    title: "User Registration"
    model: '@.zSchema.users'  # 🎯 AUTO-VALIDATION ENABLED!
    fields:
      - username
      - email
      - age
  zData:
    action: insert
    table: users
    data: zConv  # Use collected form data
  zDisplay:
    text: |
      
      ✅ User registered successfully!
```

### What Happens When model: is Specified

1. ✅ zDialog loads the schema using `z.loader.handle()`
2. ✅ Extracts validation rules for each field
3. ✅ Validates form data using `DataValidator` **BEFORE** `onSubmit`
4. ✅ Displays errors if validation fails (Terminal + zBifrost modes)
5. ✅ Only proceeds to `zData.insert` if validation passes

### Validation Error Display

**Terminal Mode:**
```
❌ Validation failed for table 'users':
  • username: Username must be 3-20 characters (letters, numbers, underscore only)
  • email: Invalid email address format
  • age: Age must be between 18 and 120

💡 Hint: Check your input and try again.
```

**zBifrost Mode (WebSocket):**
```javascript
// Client receives validation_error event:
{
  "event": "validation_error",
  "table": "users",
  "errors": {
    "username": "Username must be 3-20 characters...",
    "email": "Invalid email address format",
    "age": "Age must be between 18 and 120"
  },
  "fields": ["username", "email", "age"]
}
```

### Complete Example

```yaml
# In zSchema.users.yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
  
  email:
    type: str
    required: true
    rules:
      format: email
      error_message: "Please enter a valid email address"
  
  age:
    type: int
    rules:
      min: 18
      max: 120
      error_message: "Age must be between 18 and 120"
```

```yaml
# In zUI.users.yaml
"^Add User (With Validation)":
  zDialog:
    title: "User Registration"
    model: '@.zSchema.users'  # 🎯 Auto-validation!
    fields:
      - username
      - email
      - age
  zData:
    action: insert
    table: users
    data: zConv
  zDisplay:
    text: |
      
      ✅ User registered successfully!

"^Add User (Manual Entry - No Auto-Validation)":
  zDialog:
    # ❌ No model specified - server-side validation only
    fields: [username, email, age]
  zData:
    action: insert
    table: users
    # Validation happens here (DataValidator in zData)
```

### Backward Compatibility

**Forms without `model:` continue to work (manual validation):**

```yaml
"^Add User (Legacy)":
  zDialog:
    # No model - no auto-validation
    fields: [username, email]
  zData:
    action: insert
    table: users
    # Server-side validation still works via DataValidator
```

**Non-zPath models are skipped gracefully:**

```yaml
"^Add User (Legacy Model)":
  zDialog:
    model: "User"  # Not a zPath (@.), auto-validation skipped
    fields: [name]
  zData:
    action: insert
    table: users
```

### Common Auto-Validation Mistakes

❌ **Wrong: Forgetting `model:` attribute**
```yaml
"^Add User":
  zDialog:
    # ❌ Missing model - no auto-validation!
    fields: [username, email]
```

✅ **Right: Include `model:` with zPath**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'  # ✅ Auto-validation enabled
    fields: [username, email]
```

---

❌ **Wrong: Using non-zPath model**
```yaml
"^Add User":
  zDialog:
    model: "User"  # ❌ Not a zPath, no auto-validation
```

✅ **Right: Use zPath format (`@.zSchema.table_name`)**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'  # ✅ zPath format
```

---

❌ **Wrong: Mismatched table names**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'
  zData:
    table: accounts  # ❌ Different table, validation uses 'users' schema
```

✅ **Right: Match table names**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'
  zData:
    table: users  # ✅ Matches schema table name
```

### Demo

See `Demos/validation_demo/` for a complete working example:
- ✅ Valid data scenarios
- ✅ Invalid data scenarios (shows validation errors)
- ✅ All validation types (pattern, format, min/max, length, required)
- ✅ Terminal mode demonstration

Run: `python3 Demos/validation_demo/demo_validation.py`

### Test Coverage

Auto-validation is tested with **12 comprehensive tests** in `zTestSuite/zDialog_AutoValidation_Test.py`:

- ✅ Valid data (should succeed)
- ✅ Invalid username pattern
- ✅ Invalid email format
- ✅ Age out of range
- ✅ Missing required fields
- ✅ Graceful fallback (no model, invalid model, schema load error)
- ✅ WebSocket error broadcast (zBifrost mode)
- ✅ onSubmit integration (only called after successful validation)

**All 1113/1113 tests passing (100%)** 🎉

### Benefits

✅ **Immediate Feedback** - No wasted server round-trips  
✅ **Consistent Validation** - Same rules in forms AND database  
✅ **Declarative** - No manual validation code in plugins  
✅ **Dual-Mode** - Works in Terminal AND zBifrost  
✅ **Backward Compatible** - Forms without `model:` work as before  
✅ **Actionable Errors** - Uses Week 4.3 ValidationError with 💡 hints  

---

## Plugin Validators (Week 5.4 - zData Extension Point)

**🎯 Extend built-in validation with custom business logic using zCLI's native plugin pattern!**

### Core Design Philosophy

**AUGMENT, NOT REPLACE** - Plugin validators run AFTER built-in validators (layered validation):

```
Validation Order (fail-fast):
  Layer 1: String rules (min_length, max_length)
  Layer 2: Numeric rules (min, max)
  Layer 3: Pattern rules (regex)
  Layer 4: Format rules (email, url, phone)
  Layer 5: Plugin validator (custom business logic) ← NEW!
```

**Key Principle**: Built-in validators check structural validity, plugin validators enforce business rules.

### Syntax

Plugin validators use the same `&PluginName.function(args)` pattern as `zFunc` and `zDispatch`:

```yaml
email:
  type: str
  required: true
  rules:
    format: email  # Built-in (Layer 4): Is this an email?
    validator: "&validators.check_email_domain(['company.com', 'partner.org'])"  # Plugin (Layer 5): Is this from approved domain?
    error_message: "Email must be from approved domain"
```

### When to Use Each

| Validation Type | Purpose | Example |
|----------------|---------|---------|
| **Built-in** | Structural validation | "Is this an email?" (`format: email`) |
| **Plugin** | Business logic | "Is this from approved domain?" (`&validators.check_domain`) |
| **Both (Recommended)** | Layered validation | Format + domain check (structural + business) |

### Plugin Validator Contract

Plugin validators must follow this signature:

```python
# In plugins/validators.py
def validator_name(user_args, value, field_name, **kwargs):
    """Custom validator docstring.
    
    Args:
        user_args: User-provided from schema (e.g., ['company.com'])
        value: Field value (auto-injected by DataValidator)
        field_name (str): Field name (auto-injected)
        **kwargs: Context (table, full_data) for cross-field validation
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    """
    # Your validation logic
    if not_valid:
        return False, "Error message explaining why"
    
    return True, None  # ✅ Valid
```

### Example: Email Domain Validator

```python
# plugins/validators.py
def check_email_domain(allowed_domains, value, field_name, **kwargs):
    """Validate email domain against allowed list."""
    if '@' not in value:
        return False, f"{field_name} must be a valid email"
    
    domain = value.split('@')[1].lower()
    allowed_lower = [d.lower() for d in allowed_domains]
    
    if domain not in allowed_lower:
        return False, f"{field_name} must use approved domain: {', '.join(allowed_domains)}"
    
    return True, None  # ✅ Valid
```

**Usage in schema:**

```yaml
email:
  type: str
  required: true
  rules:
    format: email  # Built-in (structural)
    validator: "&validators.check_email_domain(['company.com', 'partner.org'])"  # Plugin (business)
    error_message: "Email must be from approved domain (company.com or partner.org)"
```

### Layered Validation Flow

**Example 1: Both validators pass**

```
Input: "test@company.com"
1. format: email → ✅ PASS (valid email structure)
2. validator: &validators.check_email_domain(['company.com']) → ✅ PASS (approved domain)
Result: ✅ Valid
```

**Example 2: Built-in fails, plugin skipped (fail-fast)**

```
Input: "not-an-email"
1. format: email → ❌ FAIL (invalid email structure)
2. validator: &validators.check_email_domain(...) → ⏭️ SKIPPED (fail-fast)
Result: ❌ Invalid (email format error)
```

**Example 3: Built-in passes, plugin fails**

```
Input: "test@gmail.com"
1. format: email → ✅ PASS (valid email structure)
2. validator: &validators.check_email_domain(['company.com']) → ❌ FAIL (wrong domain)
Result: ❌ Invalid (domain not approved)
```

### More Example Validators

**Username Blacklist**

```python
def check_username_blacklist(blacklist, value, field_name, **kwargs):
    """Ensure username is not reserved."""
    if value.lower() in [name.lower() for name in blacklist]:
        return False, f"{field_name} '{value}' is reserved and cannot be used"
    return True, None
```

```yaml
username:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9_]{3,20}$"  # Built-in
    validator: "&validators.check_username_blacklist(['admin', 'root', 'system'])"  # Plugin
```

**Cross-Field Validation**

```python
def check_cross_field_match(other_field, value, field_name, **kwargs):
    """Validate field matches another field (e.g., password confirmation)."""
    full_data = kwargs.get('full_data', {})
    other_value = full_data.get(other_field)
    
    if value != other_value:
        return False, f"{field_name} must match {other_field}"
    
    return True, None
```

```yaml
password_confirm:
  type: str
  rules:
    validator: "&validators.check_cross_field_match('password')"
    error_message: "Passwords must match"
```

**Age Eligibility**

```python
def check_age_eligibility(min_age, value, field_name, **kwargs):
    """Validate age meets minimum requirement."""
    if value < min_age:
        return False, f"Must be {min_age} or older"
    return True, None
```

```yaml
age:
  type: int
  rules:
    min: 0  # Built-in (structural)
    max: 150  # Built-in (structural)
    validator: "&validators.check_age_eligibility(18)"  # Plugin (business rule)
    error_message: "Must be 18 or older to register"
```

### Benefits

✅ **Consistent Syntax** - Same `&plugin.function()` as zFunc/zDispatch  
✅ **Reuses Infrastructure** - Plugin cache, auto-injection, existing patterns  
✅ **Declarative** - Business rules in YAML, not Python code  
✅ **Layered Validation** - Structural → Business logic (clear separation)  
✅ **Fail-Fast** - Skip expensive plugin logic if basic format invalid  
✅ **Auto-Wired** - Works with Week 5.2 zDialog auto-validation automatically!  
✅ **Testable** - Pure functions, easy to unit test  
✅ **Reusable** - Same validator across multiple schemas  
✅ **Graceful Degradation** - Missing plugin = log warning + skip (no crash)  

### Common Mistakes

❌ **WRONG**: Trying to override built-in validators

```yaml
email:
  type: str
  rules:
    validator: "&validators.check_email()"  # ❌ Don't reimplement email validation!
```

✅ **RIGHT**: Use built-in + plugin for layered validation

```yaml
email:
  type: str
  rules:
    format: email  # ✅ Built-in (structural)
    validator: "&validators.check_email_domain(['company.com'])"  # ✅ Plugin (business)
```

---

❌ **WRONG**: Incorrect return format

```python
def bad_validator(value, field_name):
    if not valid:
        return False  # ❌ Missing error message!
    return True  # ❌ Not a tuple!
```

✅ **RIGHT**: Always return tuple (bool, str or None)

```python
def good_validator(value, field_name):
    if not valid:
        return False, "Error message"  # ✅ Tuple with message
    return True, None  # ✅ Tuple (None for no error)
```

---

❌ **WRONG**: Missing `&` prefix

```yaml
rules:
  validator: "validators.check_email_domain(['company.com'])"  # ❌ Missing &
```

✅ **RIGHT**: Use `&` prefix for plugin invocation

```yaml
rules:
  validator: "&validators.check_email_domain(['company.com'])"  # ✅ With &
```

### Demo

See `Demos/validation_demo/` for complete working examples:

- ✅ `validators.py` - 6 example plugin validators
- ✅ `zSchema.demo_users.yaml` - Plugin validator usage
- ✅ Email domain validation
- ✅ Username blacklist
- ✅ Age eligibility

Run: `python3 Demos/validation_demo/demo_validation.py`

### Test Coverage

Plugin validators are tested with **14 comprehensive tests** in `zTestSuite/zData_PluginValidation_Test.py`:

- ✅ Plugin execution (valid/invalid)
- ✅ Layered validation (fail-fast behavior)
- ✅ Plugin not found (graceful degradation)
- ✅ Function not found (graceful skip)
- ✅ Plugin exceptions (error handling)
- ✅ Context injection (table, full_data)
- ✅ Multiple validators (all pass, one fails)
- ✅ No zcli instance (graceful skip)
- ✅ Invalid syntax (missing &)
- ✅ Custom error messages
- ✅ Invalid return format

**All 1127/1127 tests passing (100%)** 🎉 (was 1113, +14 from Week 5.4)

---

## Actionable Error Messages (Week 4.3)

**All zCLI exceptions include context-aware hints for resolution**

### Exception Types (from `zCLI.utils.zExceptions`)

```python
from zCLI.utils.zExceptions import (
    SchemaNotFoundError,      # Schema file not found or not loaded
    FormModelNotFoundError,   # Form model not in schema
    TableNotFoundError,       # Table not in loaded schema
    DatabaseNotInitializedError,  # INSERT before CREATE
    InvalidzPathError,        # Malformed zPath
    AuthenticationRequiredError,  # Login required
    PermissionDeniedError,    # Insufficient permissions
    zUIParseError,           # YAML syntax/structure error
    ConfigurationError,      # Invalid zSpark config
    PluginNotFoundError,     # Plugin file missing
    ValidationError          # Data validation failed
)
```

### Pattern: Automatic Actionable Hints

**Every exception includes:**
- **Clear error message** - What went wrong
- **💡 Actionable hint** - How to fix it
- **Context storage** - For debugging (`.context` dict)

**Example - SchemaNotFoundError:**
```python
# User tries to load missing schema
z.data.handle({"action": "read", "model": "@.zSchema.users"})

# zCLI raises:
# SchemaNotFoundError: Schema 'users' not found
# 💡 Load it first: z.loader.handle('@.zSchema.users')
#    Expected file: zSchema.users.yaml in workspace
```

### zPath Syntax Rules (CRITICAL)

**✅ Correct:**
```python
z.loader.handle("@.zSchema.users")          # Python: NO .yaml extension
model: "@.zSchema.products"                 # YAML: NO .yaml extension  
```

**❌ Wrong:**
```python
z.loader.handle("@.zSchema.users.yaml")     # Double extension!
model: "@.zSchema.products.yaml"            # Double extension!
```

**Why:** The framework auto-adds `.yaml` for `zSchema.*`, `zUI.*`, and `zConfig.*` files.

### zMachine Path Resolution (Week 4.4)

**zMachine** resolves to **platform-specific user data directories** via `platformdirs`:
- macOS: `~/Library/Application Support/zolo-zcli/...`
- Linux: `~/.local/share/zolo-zcli/...`
- Windows: `%LOCALAPPDATA%\zolo-zcli\...`

**Two Different Syntaxes (Context-Dependent):**

**1. In zSchema `Data_Path` (NO dot):**
```yaml
# ✅ Correct - NO dot after zMachine
Meta:
  Data_Type: sqlite
  Data_Path: "zMachine"  # Resolves to user_data_dir

# ❌ Wrong
Meta:
  Data_Path: "zMachine."  # Extra dot causes issues
```

**2. In zVaFile References (WITH dot):**
```python
# ✅ Correct - WITH dot for file paths
z.loader.handle("zMachine.zSchema.users")      # zPath syntax
z.loader.handle("~.zMachine.zSchema.users")    # Alternative syntax
```

**When to Use zMachine vs @ vs ~:**
- **zMachine:** ✅ User data that persists across projects (global configs, shared schemas)
- **@ (workspace):** ✅ Project-specific data (instance isolation, no global state)
- **~ (absolute):** ✅ Explicit absolute paths (when you need full control)

**Common zMachine Mistake:**
```python
# ❌ WRONG: Using zMachine for project data
Meta:
  Data_Path: "zMachine"  # Global path - pollutes across projects!

# ✅ CORRECT: Use workspace isolation
Meta:
  Data_Path: "@"  # Instance-isolated (The Secret Sauce!)
```

**File Not Found Error Example:**
```
zMachinePathError: zMachine path error: zMachine.zSchema.users

💡 File not found at zMachine path.

🔍 Resolution on Darwin:
   zMachine.zSchema.users
   → /Users/john/Library/Application Support/zolo-zcli/zSchema/users.yaml

💡 Options:
   1. Create the file at the resolved path
   2. Use workspace path instead: '@.zSchema.users'
   3. Use absolute path: '~./path/to/file'
```

### Context-Aware Hints

Exceptions provide different hints based on where they occur:

**Python Context:**
```python
SchemaNotFoundError("users", context_type="python")
# Hint: Load it first: z.loader.handle('@.zSchema.users')
```

**YAML zData Context:**
```python
SchemaNotFoundError("users", context_type="yaml_zdata")
# Hint: In zUI files, use zPath syntax:
#   zData:
#     model: '@.zSchema.users'  # NO .yaml extension!
#     action: read
```

**YAML zDialog Context:**
```python
FormModelNotFoundError("User", available_models=["SearchForm", "DeleteForm"])
# Hint: Available models: SearchForm, DeleteForm
#   Define it in zSchema.users.yaml:
#   Models:
#     User:
#       fields:
#         field1: {type: string}
```

### Common Mistakes & Solutions

**1. INSERT before CREATE (Most Common)**
```python
# ❌ WRONG: Trying to insert before creating table
z.data.handle({"action": "insert", "table": "users", ...})
# Raises: DatabaseNotInitializedError
# 💡 Initialize the database first:
#    Step 1: Create table structure
#    z.data.handle({'action': 'create', 'model': '@.zSchema.users'})
#    
#    Step 2: Then perform operations
#    z.data.handle({'action': 'insert', ...})
```

**2. Double Extension in zPath**
```python
# ❌ WRONG
z.loader.handle("@.zSchema.users.yaml")
# Raises: InvalidzPathError
# 💡 zPath syntax:
#    '@.zSchema.name' - workspace-relative (NO .yaml extension)
```

**3. Missing Form Model**
```yaml
# ❌ WRONG: Form model not defined in schema
zDialog:
  model: NonExistent
  fields: [name, email]
# Raises: FormModelNotFoundError
# 💡 Available models: User, SearchForm, DeleteForm
#    Define it in zSchema.users.yaml:
#    Models:
#      NonExistent:
#        fields: ...
```

### Integration with zTraceback

**Actionable errors work seamlessly with `zTraceback` and `ExceptionContext`:**

```python
from zCLI.utils.zTraceback import ExceptionContext
from zCLI.utils.zExceptions import SchemaNotFoundError

with ExceptionContext(
    zcli.zTraceback,
    operation="schema loading",
    context={'model': model_path},
    default_return=None
):
    schema = load_schema(model_path)
    if not schema:
        raise SchemaNotFoundError(schema_name, context_type="python")

# What happens:
# 1. Exception is raised with actionable hint
# 2. ExceptionContext catches it
# 3. zTraceback logs full traceback + context
# 4. User sees: error + hint + traceback + context
# 5. Interactive mode allows retry
```

---

## zSpark Configuration (Layer 0)

**Minimal** (Terminal Mode):
```python
z = zCLI({"zWorkspace": "."})
```

**Full** (All Options):
```python
z = zCLI({
    # Required
    "zWorkspace": ".",  # ALWAYS required, validates early
    
    # Mode
    "zMode": "Terminal",  # OR "zBifrost" for WebSocket
    
    # UI/Navigation
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    
    # WebSocket (zBifrost mode)
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    },
    
    # HTTP Server (optional)
    "http_server": {
        "enabled": True,
        "port": 8080,
        "serve_path": "."
    }
})
```

**Validation**: Config is validated early (fail-fast principle). Invalid configs raise `ConfigValidationError` immediately.

---

## zBifrost Level 0

**Backend**:
```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"host": "127.0.0.1", "port": 8765, "require_auth": False}
})

z.walker.run()
```

**Frontend**:
```html
<script type="module">
class SimpleBifrostClient {
    constructor(url, options) {
        this.url = url;
        this.ws = null;
        this.hooks = options.hooks || {};
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            this.ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.event === 'connection_info' && this.hooks.onConnected) {
                    this.hooks.onConnected(msg.data);
                }
            };
            this.ws.onopen = () => resolve();
            this.ws.onerror = (e) => reject(e);
        });
    }
    
    disconnect() { this.ws?.close(); }
    isConnected() { return this.ws?.readyState === WebSocket.OPEN; }
}

const client = new SimpleBifrostClient('ws://localhost:8765', {
    hooks: { onConnected: (info) => console.log(info) }
});
await client.connect();
</script>
```

**Result**: Server on 8765. Client connects, `onConnected` hook fires with server info.

## Production BifrostClient (v1.5.5+)

**Architecture**: Lazy loading - modules load dynamically only when needed

**Why**: Solves ES6 CDN issues while staying modular at runtime

**Usage via CDN**:
```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client_modular.js"></script>
<script>
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // true loads zTheme CSS automatically
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onMessage: (msg) => console.log('Message:', msg)
    }
});

await client.connect();  // Modules load here dynamically

// CRUD operations
const users = await client.read('users');
await client.create('users', {name: 'John', email: 'j@e.com'});

// Or dispatch zUI commands
const result = await client.send({event: 'dispatch', zKey: '^Ping'});
</script>
```

**Key features**:
- Works via CDN (no import resolution issues)
- Lazy loads: connection, message_handler, renderer, theme_loader
- Full CRUD API: `create()`, `read()`, `update()`, `delete()`
- zCLI operations: `zFunc()`, `zLink()`, `zOpen()`
- Auto-rendering: `renderTable()`, `renderMenu()`, `renderForm()`

## zServer (Optional HTTP Static Files)

**Purpose**: Serve HTML/CSS/JS files alongside zBifrost WebSocket server

**Features**:
- Built-in Python http.server (no dependencies)
- Optional - not everyone needs it
- Runs in background thread
- CORS enabled for local development

**Method 1: Auto-Start** (Industry Pattern):
```python
from zCLI import zCLI

z = zCLI({
    "http_server": {"port": 8080, "serve_path": ".", "enabled": True}
})

# Server auto-started! Access via z.server
print(z.server.get_url())  # http://127.0.0.1:8080
```

**Method 2: Manual Start**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Create and start manually
http_server = z.comm.create_http_server(port=8080)
http_server.start()
```

**With zBifrost (Full-Stack)**:
```python
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "enabled": True}
})

# Both servers auto-started!
# HTTP: z.server
# WebSocket: via z.walker.run()
z.walker.run()
```

**Access**: http://localhost:8080/your_file.html

**Methods**:
- `z.server.start()` - Start (if manual)
- `z.server.stop()` - Stop server
- `z.server.is_running()` - Check status
- `z.server.get_url()` - Get URL
- `z.server.health_check()` - Get status dict

---

## Layer 0 Best Practices (v1.5.4)

### Health Checks (NEW)

**Check zBifrost Status**:
```python
status = z.comm.websocket_health_check()
# Returns: {running, host, port, url, clients, authenticated_clients, require_auth}
```

**Check HTTP Server Status**:
```python
status = z.server.health_check()
# Returns: {running, host, port, url, serve_path}
```

**Check All Services**:
```python
status = z.comm.health_check_all()
# Returns: {websocket: {...}, http_server: {...}}
```

### Graceful Shutdown (NEW)

**Handle Ctrl+C Cleanly**:
```python
# Signal handlers automatically registered (SIGINT, SIGTERM)
z = zCLI({...})

# Manual shutdown (closes all connections, saves state)
z.shutdown()
```

**What gets cleaned up**:
1. WebSocket connections (notify clients, close gracefully)
2. HTTP server (stop serving, close sockets)
3. Database connections (if any)
4. Logger (flush buffers)

### Path Resolution Patterns

**Workspace-relative** (`@.`):
```python
"zVaFile": "@.zUI.users_menu"  # Resolves to {zWorkspace}/zUI.users_menu.yaml
```

**Absolute path** (`~.`):
```python
"zVaFile": "~./path/to/file"  # Resolves to absolute path
```

**Machine data dir** (`zMachine.`):
```python
"zVaFile": "zMachine.zUI.file"  # Resolves to user data directory (cross-platform)
```

See `Documentation/zPath_GUIDE.md` for comprehensive guide.

---

## Testing Patterns (Layer 0)

### Unit Tests (Behavior Validation)
```python
def test_message_handler_cache_miss(self):
    """Should execute command on cache miss"""
    ws = AsyncMock()
    data = {"zKey": "^List.users"}
    
    # Mock cache operations
    self.cache.get_query = Mock(return_value=None)  # Cache miss
    
    # Test behavior
    result = await self.handler._handle_dispatch(ws, data, broadcast)
    
    # Verify
    self.assertTrue(result)
    ws.send.assert_called_once()
```

### Integration Tests (Real Execution)
```python
@requires_network  # Skips in CI/sandbox
async def test_real_websocket_connection(self):
    """Should handle real WebSocket client"""
    z = zCLI({"zWorkspace": temp_dir, "zMode": "Terminal"})
    bifrost = zBifrost(z.logger, walker=z.walker, zcli=z, port=56901)
    
    # Start REAL server
    server_task = asyncio.create_task(bifrost.start_socket_server())
    await asyncio.sleep(0.5)
    
    # Connect REAL client
    async with websockets.connect(f"ws://127.0.0.1:56901") as ws:
        await ws.send(json.dumps({"event": "cache_stats"}))
        response = await ws.recv()
        # Verify real response
        self.assertIn("result", json.loads(response))
```

**Strategy**: Unit tests (mocks) for behavior + Integration tests (real execution) for coverage

See `Documentation/TESTING_STRATEGY.md` for comprehensive guide.

---

## Common Pitfalls (Learn from v1.5.4)

### ❌ Wrong: Direct `print()` usage
```python
print("Processing users...")  # NO!
```

### ✅ Right: Use zCLI tools
```python
z.logger.info("Processing users...")
# OR
z.display.zHorizontal("Processing users...")
```

### ❌ Wrong: Invalid zSpark
```python
z = zCLI({"zMode": "Terminal"})  # Missing zWorkspace!
# Raises ConfigValidationError immediately
```

### ✅ Right: Valid zSpark
```python
z = zCLI({"zWorkspace": ".", "zMode": "Terminal"})
```

### ❌ Wrong: Forgetting to enable HTTP server
```python
z = zCLI({"http_server": {"port": 8080}})
# Server NOT created (enabled defaults to False)
```

### ✅ Right: Enable HTTP server
```python
z = zCLI({"http_server": {"enabled": True, "port": 8080}})
```

### ❌ Wrong: zData INSERT before CREATE TABLE
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# Try to insert (FAILS - table doesn't exist!)
z.data.insert(table="sessions", fields=[...], values=[...])
# Error: no such table: sessions
```

### ✅ Right: CREATE TABLE before INSERT
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# CREATE TABLE first (DDL operation)
if not z.data.table_exists("sessions"):
    z.data.create_table("sessions")

# NOW you can INSERT (DML operation)
z.data.insert(table="sessions", fields=[...], values=[...])
```

**💡 Key Insight**: zData separates DDL (CREATE/DROP) from DML (INSERT/SELECT/UPDATE/DELETE).  
Loading a schema doesn't auto-create tables - you must explicitly call `create_table()`.

---

## Quick Reference Card

| Component | Config Key | Default | Purpose |
|-----------|-----------|---------|---------|
| zConfig | `zWorkspace` | *Required* | Base directory |
| zMode | `zMode` | `"Terminal"` | `"Terminal"` or `"zBifrost"` |
| zBifrost | `websocket` | Disabled | WebSocket server config |
| zServer | `http_server` | Disabled | HTTP static file server |
| zWalker | `zVaFile`, `zBlock` | None | UI navigation |

| Method | Purpose | Returns |
|--------|---------|---------|
| `z.walker.run()` | Start application | None (blocks) |
| `z.shutdown()` | Graceful cleanup | Status dict |
| `z.server.health_check()` | HTTP status | Status dict |
| `z.comm.health_check_all()` | All services | Status dict |

---

## Documentation Index

**Layer 0 (Foundation)**:
- `AGENT.md` - This file (quick reference)
- `Documentation/TESTING_STRATEGY.md` - Testing approach
- `Documentation/TESTING_GUIDE.md` - How to write tests
- `Documentation/DEFERRED_COVERAGE.md` - Intentionally deferred items
- `Documentation/zPath_GUIDE.md` - Path resolution
- `Documentation/zConfig_GUIDE.md` - Configuration
- `Documentation/zComm_GUIDE.md` - Communication subsystem
- `Documentation/zServer_GUIDE.md` - HTTP server
- `Documentation/SEPARATION_CHECKLIST.md` - Architecture validation

**See**: `Documentation/` for all 25+ subsystem guides

---

---

## Layer 1: zAuth with bcrypt (Week 3.1 - NEW)

### Password Hashing (Security-First)

**BREAKING CHANGE**: v1.5.4+ uses bcrypt. Plaintext passwords no longer supported.

**Hash Password**:
```python
hashed = z.auth.hash_password("user_password")
# Returns: '$2b$12$...' (60 chars, bcrypt hash)
```

**Verify Password**:
```python
is_valid = z.auth.verify_password("user_input", stored_hash)
# Returns: True/False (timing-safe comparison)
```

**Security Features**:
- ✅ bcrypt with 12 rounds (~0.3s per hash)
- ✅ Random salt per password
- ✅ 72-byte limit (auto-truncated)
- ✅ Case-sensitive
- ✅ Special characters supported (UTF-8)
- ✅ One-way (cannot recover plaintext)

**Example Usage**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Register user
password_hash = z.auth.hash_password("secure_password")
# Store in database: users.password_hash = password_hash

# Login user
user_input = "secure_password"
if z.auth.verify_password(user_input, password_hash):
    print("Login successful!")
else:
    print("Invalid password")
```

---

## Layer 1: Persistent Sessions (Week 3.2 - NEW)

### "Remember Me" Functionality

**Goal**: Login once, stay authenticated for 7 days (survives app restarts).

**The zCLI Way**: Declarative schema + `z.data.Create/Read/Update/Delete` (no raw SQL!)

### Setup (Automatic)

When `zAuth` initializes, it:
1. Loads `zSchema.sessions.yaml` from `zCLI/subsystems/zAuth/`
2. Creates `sessions.db` at `z.config.sys_paths.user_data_dir / "sessions.db"`
3. Restores any valid (non-expired) session

**Schema** (`zSchema.sessions.yaml`):
```yaml
Meta:
  Data_Type: sqlite
  Data_Label: "sessions"
  Data_Path: "zMachine"  # Uses platformdirs

sessions:
  session_id: {type: str, pk: true, required: true}
  user_id: {type: str, required: true}
  username: {type: str, required: true}
  password_hash: {type: str, required: true}  # bcrypt from Week 3.1
  token: {type: str, required: true}
  created_at: {type: datetime, default: now}
  expires_at: {type: datetime, required: true}  # 7 days from creation
  last_accessed: {type: datetime, default: now}
```

### Login with Persistence (Default)

```python
from zCLI import zCLI
import os

# Enable remote API
os.environ["ZOLO_USE_REMOTE_API"] = "true"

z = zCLI({"zWorkspace": "."})

# Login with persistence (default: persist=True)
result = z.auth.login(
    username="alice",
    password="secure_password",
    persist=True  # ← Saves to sessions.db
)

# Session saved! Close app, reopen → still logged in for 7 days
```

### Login WITHOUT Persistence

```python
# One-time session (doesn't survive restart)
result = z.auth.login(
    username="bob",
    password="temp_password",
    persist=False  # ← Session-only (in-memory)
)
```

### Logout (Deletes Persistent Session)

```python
z.auth.logout()
# - Deletes session from sessions.db
# - Clears in-memory session
# - Next startup = not logged in
```

### Session Lifecycle

**On Startup**:
1. `zAuth.__init__()` calls `_ensure_sessions_db()`
   - Loads schema
   - Creates table if needed (CREATE vs INSERT!)
   - Cleans up expired sessions
2. Calls `_load_session()`
   - Queries for valid session (not expired)
   - Restores to in-memory `z.session["zAuth"]`
   - Updates `last_accessed` timestamp

**On Login (persist=True)**:
1. Authenticate user (remote API or local)
2. Hash password with bcrypt
3. Generate unique `session_id` and `token` (secrets.token_urlsafe)
4. Calculate `expires_at` = now + 7 days
5. Delete any existing sessions for user (single session per user)
6. Insert new session via `z.data.insert()`

**On Logout**:
1. Delete session from `sessions.db` via `z.data.delete()`
2. Clear in-memory session

**Cleanup**:
- Expired sessions auto-deleted on startup
- Manual cleanup: `z.auth._cleanup_expired()`

### Cross-Platform Paths

Sessions database location (automatic via platformdirs):
- **macOS**: `~/Library/Application Support/zolo-zcli/sessions.db`
- **Linux**: `~/.local/share/zolo-zcli/sessions.db`
- **Windows**: `%LOCALAPPDATA%\zolo-zcli\sessions.db`

```python
# Access the path programmatically
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
print(f"Sessions stored at: {sessions_db}")
```

### Security Notes

✅ **Password hashes** (bcrypt) stored in sessions.db, not plaintext  
✅ **Random tokens** (32 bytes) for each session  
✅ **7-day expiry** (configurable via `z.auth.session_duration_days`)  
✅ **Single session per user** (old session deleted on new login)  
✅ **Auto-cleanup** on startup  
⚠️ **Role not persisted** (privacy: role comes from remote API only)

### Testing

**10 new tests** in `zTestSuite/zAuth_Test.py`:
- `test_ensure_sessions_db_success` - Schema loading + table creation
- `test_save_session_creates_record` - Correct fields inserted
- `test_save_session_generates_unique_tokens` - Token uniqueness
- `test_load_session_restores_valid_session` - Restore on startup
- `test_load_session_ignores_expired_session` - Expired sessions ignored
- `test_cleanup_expired_removes_old_sessions` - Housekeeping
- `test_logout_deletes_persistent_session` - Logout cleanup
- `test_login_with_persist_saves_session` - persist=True
- `test_login_with_persist_false_skips_save` - persist=False
- `test_session_duration_is_7_days` - Expiry calculation

**Total zAuth tests**: 41 (was 31, +10 from Week 3.2) ✅

---

### Cross-Platform Path Access (Layer 0)

**For Week 3.2 (Sessions) and beyond**, use these paths:

```python
# User data directory (databases, persistent files)
data_dir = z.config.sys_paths.user_data_dir
# macOS:   ~/Library/Application Support/zolo-zcli
# Linux:   ~/.local/share/zolo-zcli
# Windows: %LOCALAPPDATA%\zolo-zcli

# User config directory (config files)
config_dir = z.config.sys_paths.user_config_dir

# User cache directory (temporary data)
cache_dir = z.config.sys_paths.user_cache_dir

# User logs directory
logs_dir = z.config.sys_paths.user_logs_dir
```

**Example: Week 3.2 Sessions Database**:
```python
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
sessions_db.parent.mkdir(parents=True, exist_ok=True)
# Automatically cross-platform!
```

---

**Version**: 1.5.4  
**Layer 0 Status**: ✅ Production-Ready (70% coverage, 907 tests passing)  
**Layer 1 Status**: 🚧 In Progress (Weeks 3.1-3.2 complete)
- Week 3.1: ✅ bcrypt password hashing (14 tests)
- Week 3.2: ✅ Persistent sessions with zData (10 tests)
**Total Tests**: 931 passing (100% pass rate) 🎉  
**Next**: Week 3.3 - Enhanced RBAC decorators

