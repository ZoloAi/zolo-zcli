# zDialog: The Interactive Form/Dialog Subsystem

## **Overview**
- **zDialog** is **zCLI**'s interactive form and dialog subsystem for collecting and validating user input
- Provides form rendering, field collection, placeholder injection, and submission handling
- Initializes after zFunc, providing dialog services to all subsystems

## **Architecture**

### **Layer 1 Dialog Services**
**zDialog** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm, zDisplay, zParser, zFunc)
- Provides interactive form services to all other subsystems
- Depends on zDisplay for rendering, zParser for path resolution, and zFunc for submission processing
- Establishes the dialog foundation for zCLI

### **Modular Design**
```
zDialog/
├── __init__.py                       # Module exports
├── zDialog.py                        # Main dialog class
└── zDialog_modules/
    ├── dialog_context.py             # Context creation and placeholder injection
    └── dialog_submit.py              # Submission handling (dict/string)
```

**Note:** Clean separation between context management and submission processing.

---

## **Core Features**

### **1. Form Rendering**
- **Field Collection**: Interactive input collection for multiple fields
- **Model-Based**: Forms tied to data models for validation
- **Context Management**: Maintains form state and collected data
- **Display Integration**: Uses zDisplay for consistent rendering

### **2. Placeholder Injection**
- **zConv Access**: Reference collected form data via `zConv`
- **Dot Notation**: `zConv.field` for field access
- **Bracket Notation**: `zConv['field']` or `zConv["field"]`
- **Nested Structures**: Recursive injection in dicts and lists

### **3. Submission Handling**
- **Dual Format**: String-based (zFunc) or dict-based (zDispatch)
- **Automatic Routing**: Routes to appropriate handler based on type
- **Context Injection**: Passes form data to submission handlers
- **Error Handling**: Graceful error handling and logging

### **4. Backward Compatibility**
- **Legacy Support**: `handle_zDialog()` function for older code
- **Walker Integration**: Optional walker parameter for legacy workflows
- **Modern API**: Direct zCLI instance usage for new code

---

## **Dialog Structure**

### **Basic Dialog Configuration**

```python
zHorizontal = {
    "zDialog": {
        "model": "User",                    # Data model name
        "fields": ["username", "email"],    # Fields to collect
        "onSubmit": "zFunc(@utils.save)"   # Optional submission handler
    }
}

result = zcli.dialog.handle(zHorizontal)
```

### **Dialog Without Submission**

```python
# Collect data only, no processing
zHorizontal = {
    "zDialog": {
        "model": "User",
        "fields": ["username", "email", "age"]
    }
}

# Returns collected data
zConv = zcli.dialog.handle(zHorizontal)
# Result: {"username": "testuser", "email": "test@example.com", "age": 25}
```

---

## **Placeholder Injection**

### **Accessing Form Data**

#### **Entire zConv Dictionary**
```python
"onSubmit": {
    "zCRUD": {
        "action": "create",
        "data": "zConv"  # Injects entire form data
    }
}
```

#### **Dot Notation**
```python
"onSubmit": "zFunc(@utils.process, zConv.username, zConv.email)"
# Injects specific fields
```

#### **Bracket Notation**
```python
{
    "user": "zConv['username']",
    "contact": "zConv[\"email\"]"
}
```

### **Nested Structures**

```python
{
    "data": {
        "user": "zConv.username",
        "details": ["zConv.email", "zConv.age"],
        "metadata": {
            "source": "form",
            "id": "zConv.id"
        }
    }
}
```

**Result after injection:**
```python
{
    "data": {
        "user": "testuser",
        "details": ["test@example.com", 25],
        "metadata": {
            "source": "form",
            "id": 12345
        }
    }
}
```

---

## **Submission Handling**

### **String-Based Submission (zFunc)**

Routes to zFunc for external function execution:

```python
zHorizontal = {
    "zDialog": {
        "model": "User",
        "fields": ["username", "email"],
        "onSubmit": "zFunc(@utils.save_user, zConv.username, zConv.email)"
    }
}

result = zcli.dialog.handle(zHorizontal)
```

**Flow:**
1. Collect form data → `zConv`
2. Parse zFunc expression
3. Inject placeholders from `zConv`
4. Execute function via `zcli.zfunc.handle()`
5. Return function result

### **Dict-Based Submission (zDispatch)**

Routes to zDispatch for command execution:

```python
zHorizontal = {
    "zDialog": {
        "model": "User",
        "fields": ["username", "email", "password"],
        "onSubmit": {
            "zCRUD": {
                "action": "create",
                "data": "zConv",
                "model": "User"
            }
        }
    }
}

result = zcli.dialog.handle(zHorizontal)
```

**Flow:**
1. Collect form data → `zConv`
2. Inject placeholders into dict
3. Route to `zDispatch.handle()`
4. Execute CRUD operation
5. Return operation result

---

## **API Reference**

### **zDialog Class**

#### **Initialization**
```python
zdialog = zDialog(zcli, walker=None)
```

**Parameters:**
- `zcli` (zCLI): Required zCLI instance
- `walker` (optional): Legacy walker instance for compatibility

**Attributes:**
- `self.zcli`: zCLI instance
- `self.session`: Session dictionary
- `self.logger`: Logger instance
- `self.display`: zDisplay instance
- `self.zparser`: zParser instance
- `self.zfunc`: zFunc instance
- `self.walker`: Optional walker instance
- `self.mycolor`: "ZDIALOG"

#### **handle(zHorizontal)**
```python
result = zcli.dialog.handle(zHorizontal)
```

**Parameters:**
- `zHorizontal` (dict): Dialog configuration

**Returns:**
- `zConv` (dict): Collected form data (if no onSubmit)
- `result` (any): Submission result (if onSubmit provided)

**Raises:**
- `TypeError`: If zHorizontal is not a dict
- `KeyError`: If required fields (model, fields) are missing
- `Exception`: If submission processing fails

---

### **Dialog Modules**

#### **create_dialog_context(model, fields, logger, zConv=None)**
```python
from zCLI.subsystems.zDialog.zDialog_modules import create_dialog_context

context = create_dialog_context("User", ["username", "email"], logger)
```

**Returns:** Dialog context dictionary with model and fields

#### **inject_placeholders(obj, zContext, logger)**
```python
from zCLI.subsystems.zDialog.zDialog_modules import inject_placeholders

result = inject_placeholders({"user": "zConv.username"}, zContext, logger)
```

**Returns:** Object with placeholders replaced by actual values

#### **handle_submit(submit_expr, zContext, logger, walker=None)**
```python
from zCLI.subsystems.zDialog.zDialog_modules import handle_submit

result = handle_submit(submit_expr, zContext, logger, walker=walker)
```

**Returns:** Submission result (function return or dispatch result)

---

### **Backward Compatibility**

#### **handle_zDialog(zHorizontal, walker=None, zcli=None)**
```python
from zCLI.subsystems.zDialog import handle_zDialog

# Modern usage
result = handle_zDialog(zHorizontal, zcli=zcli)

# Legacy usage
result = handle_zDialog(zHorizontal, walker=walker)
```

**Parameters:**
- `zHorizontal` (dict): Dialog configuration
- `walker` (optional): Walker instance with zcli attribute
- `zcli` (optional): Direct zCLI instance

**Returns:** Dialog result (collected data or submission result)

---

## **Usage Examples**

### **Simple Form Collection**

```python
# Define dialog
dialog_config = {
    "zDialog": {
        "model": "User",
        "fields": ["username", "email", "age"]
    }
}

# Collect data
user_data = zcli.dialog.handle(dialog_config)

# Use collected data
print(f"Username: {user_data['username']}")
print(f"Email: {user_data['email']}")
print(f"Age: {user_data['age']}")
```

### **Form with Function Submission**

```python
# Dialog with zFunc submission
dialog_config = {
    "zDialog": {
        "model": "User",
        "fields": ["username", "email", "password"],
        "onSubmit": "zFunc(@auth.register, zConv.username, zConv.email, zConv.password)"
    }
}

# Collect and submit
result = zcli.dialog.handle(dialog_config)

if result.get("status") == "success":
    print(f"User registered: {result['user_id']}")
```

### **Form with CRUD Submission**

```python
# Dialog with zCRUD submission
dialog_config = {
    "zDialog": {
        "model": "Product",
        "fields": ["name", "price", "category"],
        "onSubmit": {
            "zCRUD": {
                "action": "create",
                "data": {
                    "name": "zConv.name",
                    "price": "zConv.price",
                    "category": "zConv.category",
                    "created_at": "now()"
                }
            }
        }
    }
}

# Collect and create
result = zcli.dialog.handle(dialog_config)

if result.get("status") == "created":
    print(f"Product created with ID: {result['id']}")
```

### **Nested Placeholder Injection**

```python
# Complex submission with nested placeholders
dialog_config = {
    "zDialog": {
        "model": "Order",
        "fields": ["customer_id", "product_id", "quantity"],
        "onSubmit": {
            "zCRUD": {
                "action": "create",
                "model": "Order",
                "data": {
                    "customer": {
                        "id": "zConv.customer_id"
                    },
                    "items": [
                        {
                            "product_id": "zConv.product_id",
                            "quantity": "zConv.quantity"
                        }
                    ],
                    "metadata": {
                        "source": "dialog",
                        "timestamp": "now()"
                    }
                }
            }
        }
    }
}

result = zcli.dialog.handle(dialog_config)
```

---

## **Architecture Improvements**

### **Security Enhancements**
- **Removed `eval()`**: Replaced unsafe `eval()` with safe string parsing
- **Bracket Parsing**: Manual parsing of bracket notation instead of code execution
- **Error Handling**: Graceful fallback on malformed placeholders

### **Dependency Management**
- **zFunc Integration**: Direct access to `zcli.zfunc` for function execution
- **zParser Integration**: Uses `zcli.zparser` for path resolution
- **zDisplay Integration**: Uses `zcli.display.zDeclare()` for new architecture

### **Code Organization**
- **Modular Design**: Separate modules for context and submission
- **Clean Separation**: Context management vs. submission processing
- **No Cross-Dependencies**: Each module is self-contained

---

## **Migration Notes**

### **From Old to New Architecture**

**Old (Legacy):**
```python
from zCLI.subsystems.zDialog import handle_zDialog

result = handle_zDialog(zHorizontal, walker=walker)
```

**New (Modern):**
```python
result = zcli.dialog.handle(zHorizontal)
```

### **Display Method Updates**

**Old:**
```python
walker.display.handle({"event": "sysmsg", "label": "zDialog", ...})
```

**New:**
```python
walker.display.zDeclare("zDialog", color="ZDIALOG", indent=1, style="single")
```

### **Security Updates**

**Old (Unsafe):**
```python
return eval(obj, {}, {"zConv": zconv_data})  # Security risk
```

**New (Safe):**
```python
# Manual bracket parsing
if "[" in obj and "]" in obj:
    start = obj.index("[") + 1
    end = obj.index("]")
    field = obj[start:end].strip("'\"")
    return zconv_data.get(field)
```

---

## **Testing**

### **Test Coverage**
- ✅ Initialization and setup
- ✅ Context creation and management
- ✅ Placeholder injection (all formats)
- ✅ Form handling (with/without submission)
- ✅ String-based submission (zFunc)
- ✅ Dict-based submission (zDispatch)
- ✅ Backward compatibility
- ✅ Error handling and edge cases

### **Running Tests**
```bash
# Run zDialog tests only
python3 zTestSuite/zDialog_Test.py

# Run all tests including zDialog
python3 zTestSuite/run_all_tests.py
# Select option 9 for zDialog
# Select option 0 for all tests
```

---

## **Best Practices**

### **Form Design**
1. **Clear Model Names**: Use descriptive model names that match your data structure
2. **Minimal Fields**: Only collect necessary fields to reduce user friction
3. **Validation**: Implement validation in submission handlers, not in dialog
4. **Error Feedback**: Provide clear error messages on submission failure

### **Placeholder Usage**
1. **Dot Notation First**: Use `zConv.field` for simple field access
2. **Bracket for Special**: Use brackets only for fields with special characters
3. **Nested Carefully**: Keep nested structures simple and readable
4. **Test Thoroughly**: Test placeholder injection with various data types

### **Submission Handling**
1. **Choose Right Type**: Use zFunc for custom logic, zCRUD for database operations
2. **Error Handling**: Always wrap submission in try-catch blocks
3. **Return Values**: Ensure submission handlers return meaningful results
4. **Logging**: Log submission attempts for debugging and auditing

### **Security**
1. **Validate Input**: Always validate collected form data
2. **Sanitize Data**: Sanitize user input before database operations
3. **No Direct Eval**: Never use `eval()` on user input
4. **Safe Placeholders**: Use safe placeholder injection methods only

---

## **Common Patterns**

### **User Registration**
```python
{
    "zDialog": {
        "model": "User",
        "fields": ["username", "email", "password"],
        "onSubmit": "zFunc(@auth.register, zConv)"
    }
}
```

### **Data Entry**
```python
{
    "zDialog": {
        "model": "Record",
        "fields": ["field1", "field2", "field3"],
        "onSubmit": {
            "zCRUD": {
                "action": "create",
                "data": "zConv"
            }
        }
    }
}
```

### **Multi-Step Forms**
```python
# Step 1: Basic info
step1_data = zcli.dialog.handle({
    "zDialog": {
        "model": "User",
        "fields": ["username", "email"]
    }
})

# Step 2: Additional info (with step1 data in context)
step2_data = zcli.dialog.handle({
    "zDialog": {
        "model": "UserProfile",
        "fields": ["age", "location"],
        "onSubmit": "zFunc(@user.complete_registration, zConv, step1_data)"
    }
})
```

---

**Last Updated:** 2025-10-18  
**Version:** 1.4.0  
**Status:** Production Ready

