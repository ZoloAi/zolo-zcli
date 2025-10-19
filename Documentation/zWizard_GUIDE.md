# zWizard: The Workflow Orchestration Engine

## **Overview**
- **zWizard** is **zCLI**'s core loop engine for stepped execution and workflow orchestration
- Provides sequential step execution, transaction management, result interpolation, and navigation control
- Powers Shell canvas mode, Walker UI navigation, and batch data operations with automatic connection reuse

## **Architecture**

### **Layer 2 Orchestration Engine**
**zWizard** operates as a Layer 2 subsystem, meaning it:
- Initializes after foundation (zConfig, zComm) and display (zDisplay) subsystems
- Provides workflow orchestration for both Shell and Walker modes
- Manages transaction lifecycle via schema_cache
- Depends on zShell for step execution in Shell mode
- Depends on zDispatch for step routing in Walker mode

### **Pure Loop Engine Design**
```
zWizard/
├── zWizard.py                        # Core loop engine
└── zWizard_modules/                  # (Reserved for future extensions)

Execution Logic:
├── Shell Mode: zShell/executor_commands/wizard_step_executor.py
└── Walker Mode: zDispatch/handle() routing
```

**Key Principle**: zWizard is a generic loop engine. Mode-specific execution logic lives in the respective subsystems (zShell for Shell mode, zDispatch for Walker mode).

---

## **Core Features**

### **1. Sequential Step Execution**
- **Ordered Processing**: Steps execute in dictionary order
- **Error Handling**: Graceful error recovery with callbacks
- **Flow Control**: Navigation signals (zBack, stop, error)
- **Context Passing**: Shared context across steps

### **2. Transaction Management**
- **Automatic BEGIN/COMMIT/ROLLBACK**: Managed via schema_cache
- **Connection Reuse**: Single connection across multiple steps
- **Atomic Operations**: All-or-nothing execution
- **Error Recovery**: Automatic rollback on failure

### **3. Result Interpolation (zHat)**
- **Result Storage**: Each step's result stored in zHat array
- **Reference Syntax**: `zHat[0]`, `zHat[1]`, etc.
- **Dynamic Values**: Use previous results in subsequent steps
- **Type Preservation**: Results maintain their original types

### **4. Navigation Callbacks**
- **on_continue**: Called after each successful step
- **on_back**: Handle backward navigation (zBack)
- **on_stop**: Handle stop signals
- **on_error**: Custom error handling

---

## **Workflow Structure**

### **Basic Workflow**
```yaml
step1:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Alice", age: 30}

step2:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Bob", age: 25}
```

### **Transactional Workflow**
```yaml
_transaction: true
step1:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Alice", age: 30}

step2:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Bob", age: 25}
```

**Transaction Behavior:**
- First step with `$alias` or schema path triggers BEGIN
- All subsequent steps reuse the same connection
- Success triggers COMMIT
- Error triggers ROLLBACK
- Finally block clears schema_cache

### **Meta Keys (Underscore Prefix)**
```yaml
_transaction: true        # Enable transaction mode
_config: {...}           # Workflow configuration (future)
_timeout: 30             # Execution timeout (future)
```

Meta keys are skipped during execution but control workflow behavior.

---

## **zHat Result Interpolation**

### **Concept**
zHat is an array that stores the result of each executed step, enabling dependent operations.

### **Usage Pattern**
```yaml
step1:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Alice", age: 30}
  # Returns: True (success)

step2:
  zDisplay:
    event: text
    message: "Previous result: zHat[0]"
  # Displays: "Previous result: True"

step3:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: select
    tables: [users]
    options: {where: "name = 'Alice'"}
  # Returns: [{id: 1, name: "Alice", age: 30}]

step4:
  zDisplay:
    event: text
    message: "User ID: zHat[2][0]['id']"
  # Displays: "User ID: 1"
```

### **Interpolation Rules**
- Only string values are interpolated
- Syntax: `zHat[index]` where index is 0-based
- Results are converted to repr() format
- Invalid indices return "None"

---

## **Transaction Management**

### **Schema Cache Architecture**
```python
schema_cache = {
    "connections": {
        "mydb": <handler_instance>,  # Persistent connection
        "otherdb": <handler_instance>
    }
}
```

### **Transaction Lifecycle**

#### **1. Transaction Start**
```python
# First step with $alias or schema path
if use_transaction and transaction_alias is None:
    if model.startswith("$"):
        alias = model[1:]  # Extract alias
        # Connection created and stored in schema_cache
```

#### **2. Connection Reuse**
```python
# Subsequent steps check schema_cache first
existing_handler = schema_cache.get_connection(alias)
if existing_handler:
    # Reuse existing connection (same transaction)
    return existing_handler
```

#### **3. Transaction Commit**
```python
# On successful completion
if use_transaction and transaction_alias:
    schema_cache.commit_transaction(alias)
    logger.info("✅ Transaction committed for $%s", alias)
```

#### **4. Transaction Rollback**
```python
# On error
if use_transaction and transaction_alias:
    logger.error("❌ Rolling back transaction for $%s", alias)
    schema_cache.rollback_transaction(alias)
```

#### **5. Cleanup**
```python
# Always executed (finally block)
schema_cache.clear()
logger.debug("Schema cache connections cleared")
```

---

## **Shell Mode Integration**

### **Canvas Mode Workflow**
```bash
# 1. Enter canvas mode
> wizard --start

# 2. Add commands (converted to YAML)
> data insert users --model @.zTestSuite.demos.zSchema.sqlite_demo --name "Alice" --age 30
> data insert users --model @.zTestSuite.demos.zSchema.sqlite_demo --name "Bob" --age 25

# 3. Execute workflow
> wizard --run
# Internally calls: zcli.wizard.handle(canvas_yaml)

# 4. Exit canvas mode
> wizard --stop
```

### **Direct YAML Execution**
```python
# From Python code
workflow = {
    "_transaction": True,
    "step1": {
        "zData": {
            "model": "@.zTestSuite.demos.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["users"],
            "options": {"name": "Alice", "age": 30}
        }
    }
}

result = zcli.wizard.handle(workflow)
# Returns: [True] (zHat array)
```

---

## **Walker Mode Integration**

### **UI Navigation**
```python
# Walker uses zWizard for menu navigation
wizard = zWizard(walker=walker_instance)

menu_items = {
    "option1": {"zDisplay": {...}, "zNavigation": {...}},
    "option2": {"zDisplay": {...}, "zNavigation": {...}},
}

result = wizard.execute_loop(
    menu_items,
    navigation_callbacks={
        "on_back": handle_back,
        "on_continue": handle_continue
    }
)
```

### **Navigation Callbacks**
```python
def handle_back(result):
    """Handle backward navigation."""
    return "previous_menu"

def handle_continue(result, key):
    """Handle forward navigation."""
    logger.info(f"Completed step: {key}")

def handle_error(error, key):
    """Handle errors."""
    display.error(f"Error in {key}: {error}")
    return "error_menu"
```

---

## **Step Execution Flow**

### **Shell Mode**
```
zWizard.handle(workflow)
  → For each step:
    → _execute_step(key, value, context)
      → zcli.shell.executor.execute_wizard_step(key, value, context)
        → Route to appropriate handler:
          - zData → execute_data()
          - zFunc → execute_func()
          - zDisplay → display methods
  → Commit transaction
  → Clear schema_cache
```

### **Walker Mode**
```
zWizard.execute_loop(items, dispatch_fn)
  → For each item:
    → dispatch_fn(key, value)
      → walker.dispatch.handle(key, value, context)
        → Route to appropriate handler
  → Handle navigation results
  → Call navigation callbacks
```

---

## **Error Handling**

### **Exception Handling**
```python
try:
    result = dispatch_fn(key, value)
except Exception as e:
    # Log error with full traceback
    logger.error("Error for key '%s': %s", key, e, exc_info=True)
    
    # Display error
    display.zDeclare(f"Dispatch error for: {key}", color="ERROR")
    
    # Call error callback if provided
    if navigation_callbacks and 'on_error' in navigation_callbacks:
        return navigation_callbacks['on_error'](e, key)
    
    # Continue to next step
    continue
```

### **Transaction Rollback**
```python
try:
    # Execute workflow
    for step in workflow:
        execute_step(step)
    commit_transaction()
except Exception as e:
    # Automatic rollback
    rollback_transaction(alias)
    logger.error("❌ Error in zWizard, rolling back transaction")
    raise
finally:
    # Always cleanup
    schema_cache.clear()
```

---

## **Best Practices**

### **1. Use Transactions for Multi-Step Data Operations**
```yaml
# ✅ Good: Atomic operation
_transaction: true
step1:
  zData: {action: insert, ...}
step2:
  zData: {action: insert, ...}

# ❌ Bad: Separate connections, no atomicity
step1:
  zData: {action: insert, ...}
step2:
  zData: {action: insert, ...}
```

### **2. Leverage zHat for Dependent Steps**
```yaml
# ✅ Good: Use previous result
step1:
  zData: {action: insert, ...}  # Returns ID
step2:
  zData:
    action: update
    where: "id = zHat[0]"  # Use returned ID

# ❌ Bad: Hardcoded values
step1:
  zData: {action: insert, ...}
step2:
  zData:
    action: update
    where: "id = 1"  # Fragile
```

### **3. Use Consistent Schema References**
```yaml
# ✅ Good: Same schema path for transaction
_transaction: true
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
step2:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}

# ❌ Bad: Different schemas break transaction
_transaction: true
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
step2:
  zData: {model: "@.zTestSuite.demos.zSchema.postgresql_demo", ...}
```

### **4. Handle Errors Gracefully**
```yaml
# Provide error callbacks in Walker mode
wizard.execute_loop(
    items,
    navigation_callbacks={
        "on_error": lambda e, k: display.error(f"Failed: {e}")
    }
)
```

---

## **Advanced Features**

### **1. Custom Dispatch Functions**
```python
def custom_dispatch(key, value):
    """Custom step execution logic."""
    logger.info(f"Executing custom step: {key}")
    # Your logic here
    return result

wizard.execute_loop(items, dispatch_fn=custom_dispatch)
```

### **2. Context Passing**
```python
context = {
    "wizard_mode": True,
    "schema_cache": schema_cache,
    "user_id": 123,
    "custom_data": {...}
}

wizard.execute_loop(items, context=context)
```

### **3. Start from Specific Key**
```python
# Resume from step3
wizard.execute_loop(items, start_key="step3")
```

---

## **Integration with Other Subsystems**

### **zData Integration**
```python
# zWizard passes context to zData
context = {
    "wizard_mode": True,
    "schema_cache": schema_cache
}

# zData checks for existing connection
if wizard_mode and schema_cache:
    existing_handler = schema_cache.get_connection(alias)
    if existing_handler:
        # Reuse connection (same transaction)
        return existing_handler
```

### **zShell Integration**
```python
# Shell mode execution
def execute_wizard_step(zcli, step_key, step_value, logger, step_context):
    """Execute a wizard step in shell mode."""
    if "zData" in step_value:
        return zcli.data.handle_request(step_value["zData"], context=step_context)
    if "zFunc" in step_value:
        return zcli.funcs.handle(step_value["zFunc"])
    # ... other handlers
```

### **zDisplay Integration**
```python
# Visual feedback during execution
display.zDeclare("Handle zWizard", color="ZWIZARD", style="full")
display.zDeclare(f"zWizard step: {step_key}", color="ZWIZARD", style="single")
display.zDeclare("process_keys → next zKey", color="MAIN", style="single")
```

---

## **Testing**

### **Unit Testing**
```python
import unittest
from zCLI.subsystems.zWizard import zWizard

class TestzWizard(unittest.TestCase):
    def test_basic_workflow(self):
        """Test basic workflow execution."""
        workflow = {
            "step1": {"zData": {...}},
            "step2": {"zData": {...}}
        }
        
        result = self.zcli.wizard.handle(workflow)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0])  # First step succeeded
        self.assertTrue(result[1])  # Second step succeeded
```

### **Transaction Testing**
```python
def test_transaction_commit(self):
    """Test transaction commit on success."""
    workflow = {
        "_transaction": True,
        "step1": {"zData": {...}},
        "step2": {"zData": {...}}
    }
    
    result = self.zcli.wizard.handle(workflow)
    
    # Verify data was committed
    self.zcli.data.load_schema(schema)
    users = self.zcli.data.select("users")
    self.assertEqual(len(users), 2)
```

---

## **Performance Considerations**

### **Connection Reuse**
- **Single Connection**: All steps in a transaction use the same connection
- **No Overhead**: No connection/disconnection between steps
- **Efficient**: Reduces database round trips

### **Schema Cache Lifecycle**
```python
# Start of workflow
schema_cache = {}  # Empty

# First step
schema_cache["mydb"] = handler  # Connection created

# Subsequent steps
handler = schema_cache["mydb"]  # Reused

# End of workflow
schema_cache.clear()  # Cleanup
```

---

## **Troubleshooting**

### **Common Issues**

#### **1. Transaction Not Working**
```yaml
# ❌ Problem: Missing _transaction flag
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}

# ✅ Solution: Add _transaction flag
_transaction: true
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
```

#### **2. Connection Not Reused**
```yaml
# ❌ Problem: Different schema paths
_transaction: true
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
step2:
  zData: {model: "@.zTestSuite.demos.zSchema.other_demo", ...}

# ✅ Solution: Use same schema path
_transaction: true
step1:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
step2:
  zData: {model: "@.zTestSuite.demos.zSchema.sqlite_demo", ...}
```

#### **3. zHat Interpolation Not Working**
```yaml
# ❌ Problem: Non-string value
step1:
  zData: {action: insert, ...}
step2:
  zData:
    action: update
    options: {id: zHat[0]}  # Won't interpolate

# ✅ Solution: Use string context
step1:
  zData: {action: insert, ...}
step2:
  zData:
    action: update
    options: {where: "id = zHat[0]"}  # Will interpolate
```

---

## **Development Notes**

### **Architecture Decisions**
- **Pure Loop Engine**: zWizard doesn't know about specific step types
- **Mode Separation**: Shell and Walker logic lives in respective subsystems
- **Schema Cache**: Managed by zLoader, used by zWizard for transactions
- **Error Handling**: Exceptions logged but don't crash the loop

### **Future Enhancements**
- 📋 Conditional steps (if/else logic)
- 📋 Parallel step execution
- 📋 Step retry logic
- 📋 Workflow templates
- 📋 Step timeout configuration

---

## **Quick Reference**

### **Workflow Structure**
```yaml
_transaction: true           # Enable transactions
_config: {...}              # Meta configuration

step1:                      # Step name
  zData: {...}             # Step action
  
step2:
  zFunc: {...}
  
step3:
  zDisplay: {...}
```

### **Python API**
```python
# Execute workflow
result = zcli.wizard.handle(workflow)

# Execute loop with callbacks
result = wizard.execute_loop(
    items_dict,
    dispatch_fn=custom_fn,
    navigation_callbacks={...},
    context={...},
    start_key="step3"
)
```

### **Transaction Pattern**
```python
try:
    # Execute steps
    for step in workflow:
        execute_step(step)
    # Commit on success
    commit_transaction()
except Exception:
    # Rollback on error
    rollback_transaction()
finally:
    # Always cleanup
    schema_cache.clear()
```

---

## **See Also**
- **zShell**: Canvas mode and workflow execution
- **zData**: Data operations and transaction support
- **zLoader**: Schema loading and cache management
- **zDispatch**: Walker mode routing
- **zDisplay**: Visual feedback during execution

