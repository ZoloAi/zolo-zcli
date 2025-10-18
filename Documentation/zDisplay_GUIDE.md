# zDisplay: The Display Subsystem

## **Overview**
- **zDisplay** is **zCLI**'s display and rendering subsystem
- Provides dual-mode output (Terminal/GUI), primitive I/O operations, event-based rendering, and user interaction
- Initializes after zComm and zAuth, providing display services to all other subsystems

## **Architecture**

### **Layer 1 Display Services**
**zDisplay** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm)
- Provides display services to all other subsystems
- Depends on zCLI session and logger configuration
- Establishes the rendering foundation for zCLI

### **Modular Design**
```
zDisplay/
├── zDisplay.py                       # Main display manager
└── zDisplay_modules/
    ├── zPrimitives.py                # Core I/O primitives
    ├── zEvents.py                    # Event orchestrator
    └── zEvents_packages/
        ├── BasicOutputs.py           # Basic text and headers
        ├── BasicInputs.py            # Input collection (selection)
        ├── Signals.py                # Feedback messages (error, success, etc.)
        ├── BasicData.py              # Data display (list, json)
        ├── AdvancedData.py           # Tables with pagination
        └── zSystem.py                # System introspection (session, crumbs)
```

---

## **Core Features**

### **1. Dual-Mode Architecture**
- **Terminal Mode**: Direct console I/O with formatting and interaction
- **GUI Mode**: WebSocket-based clean events for frontend rendering
- Automatic mode detection and seamless switching

### **2. Primitive Foundation**
- **6 Core Primitives**: `write_raw()`, `write_line()`, `write_block()`, `read_string()`, `read_password()`, `send_gui_event()`
- Raw I/O operations form the foundation for all display capabilities

### **3. Event Package System**
- **7-Layer Composition**: Primitives → BasicOutputs → BasicInputs → Signals → BasicData → AdvancedData → zSystem
- Each package composes lower layers, eliminating code duplication
- Clean separation of concerns with maximum code reuse

### **4. Advanced Features**
- **Smart Pagination**: Positive (top) and negative (bottom) limits, offset support
- **Unified Selection**: Single event replaces radio/checkbox/dropdown redundancy
- **Interactive Menus**: Display-only or interactive with selection collection

---

## **Quick Start**

### **Initialization**
```python
from zCLI import zCLI

# zDisplay initializes automatically
zcli = zCLI()

# Access display services
display = zcli.display
```

### **Basic Output**
```python
# Headers and text
display.header("Section Title", color="CYAN")
display.text("Content here", break_after=False)

# Signals
display.success("Operation completed!")
display.error("Something went wrong")
display.info("Information message")
```

### **Data Display**
```python
# Lists and JSON
display.list(["Item 1", "Item 2", "Item 3"])
display.json_data({"key": "value", "number": 42})

# Tables with pagination
display.zTable("Users", ["ID", "Name"], rows, limit=10)    # First 10 rows
display.zTable("Users", ["ID", "Name"], rows, limit=-10)   # Last 10 rows
```

### **User Interaction**
```python
# Input collection
name = display.read_string("Enter name: ")
password = display.read_password("Password: ")

# Selection menus
option = display.selection("Choose option:", ["A", "B", "C"])
multi_selection = display.selection("Choose items:", items, multi=True)

# Interactive menus
display.zMenu([(1, "View"), (2, "Edit")], return_selection=False)  # Display only
selection = display.zMenu([(1, "View"), (2, "Edit")], return_selection=True)  # Interactive
```

### **System Events**
```python
# System introspection
display.zSession(session_data)
display.zCrumbs(session_data)
display.zDeclare("System Message")
```

---

## 🖥️ **Command Line Interface**

### **Available Methods**

#### **Primitive Operations**
```python
display.write_raw(content)           # Raw output without formatting
display.write_line(content)          # Single line with newline
display.write_block(content)         # Multi-line block
display.read_string(prompt)          # Read string input
display.read_password(prompt)        # Read masked password input
```

#### **Output Events**
```python
display.header(label, color, indent, style)      # Section headers
display.text(content, indent, break_after)       # Formatted text
display.zDeclare(label, color, indent, style)    # System messages
```

#### **Signal Events**
```python
display.error(content, indent)       # Red error messages
display.warning(content, indent)     # Yellow warning messages
display.success(content, indent)     # Green success messages
display.info(content, indent)        # Cyan info messages
display.zMarker(label, color, indent) # Flow markers
```

#### **Data Events**
```python
display.list(items, style, indent)                    # Bulleted/numbered lists
display.json_data(data, indent_size, indent, color)  # Pretty JSON display
display.zTable(title, columns, rows, limit, offset)   # Paginated tables
```

#### **Input Events**
```python
display.selection(prompt, options, multi, default, style)  # Unified selection
```

#### **System Events**
```python
display.zSession(session_data, break_after, break_message)  # Session display
display.zCrumbs(session_data)                              # Navigation breadcrumbs
display.zMenu(menu_items, prompt, return_selection)        # Menu display/interaction
display.zDialog(context, zcli, walker)                     # Form dialogs
```

---

## 🔧 **API Reference**

### **Core Architecture**

#### **zDisplay Class**
```python
class zDisplay:
    def __init__(self, zcli):
        """Initialize with zCLI instance and session data."""
```

#### **Primitive Layer**
```python
class zPrimitives:
    def write_raw(self, content):           # Raw string output
    def write_line(self, content):          # Line with newline
    def write_block(self, content):         # Multi-line block
    def read_string(self, prompt):          # String input
    def read_password(self, prompt):        # Password input
    def send_gui_event(self, event, data):  # GUI event dispatch
```

#### **Event Packages**

##### **BasicOutputs**
```python
def header(self, label, color="RESET", indent=0, style="full"):
    """Section headers with styling and indentation."""
    
def text(self, content, indent=0, break_after=True, break_message=None):
    """Formatted text with optional pause control."""
```

##### **Signals**
```python
def error(self, content, indent=0):        # Error messages
def warning(self, content, indent=0):      # Warning messages  
def success(self, content, indent=0):      # Success messages
def info(self, content, indent=0):         # Info messages
def zMarker(self, label, color, indent):   # Flow markers
```

##### **BasicInputs**
```python
def selection(self, prompt, options, multi=False, default=None, style="numbered"):
    """Unified selection - replaces radio/checkbox/dropdown."""
```

##### **AdvancedData**
```python
def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
    """Paginated table display with smart slicing."""
```

#### **Pagination Helper**
```python
class Pagination:
    @staticmethod
    def paginate(data, limit=None, offset=0):
        """Smart pagination:
        - limit=10: First 10 items
        - limit=-10: Last 10 items  
        - offset=5: Skip first 5 items
        """
```

---

## **Examples**

### **Table Pagination**
```python
# Show first 10 rows
display.zTable("Users", ["ID", "Name", "Email"], user_rows, limit=10)

# Show last 5 rows  
display.zTable("Recent Activity", columns, activity_rows, limit=-5)

# Skip 20 rows, show next 10
display.zTable("Paged Results", columns, data_rows, limit=10, offset=20)
```

### **Menu Interaction**
```python
# Display-only menu
display.zMenu([(1, "View Profile"), (2, "Settings"), (3, "Exit")])

# Interactive menu with selection
choice = display.zMenu(
    [(1, "View Profile"), (2, "Settings"), (3, "Exit")],
    prompt="What would you like to do?",
    return_selection=True
)
```

### **Selection Types**
```python
# Single selection (radio-style)
option = display.selection("Choose mode:", ["Terminal", "GUI"], multi=False)

# Multi-selection (checkbox-style)  
features = display.selection("Enable features:", feature_list, multi=True)
```

---

## **Migration Notes**

### **Legacy Compatibility**
- Legacy `handle()` method maintains backward compatibility
- Event dict format: `display.handle({"event": "text", "content": "..."})`
- Gradually migrate to direct method calls: `display.text("...")`

### **Event Mapping**
```python
# Old format
display.handle({"event": "error", "content": "Failed"})

# New format  
display.error("Failed")
```

---

## **Integration**

zDisplay integrates closely with:
- **zAuth**: Authentication status display
- **zConfig**: Session and configuration display
- **zWalker**: Menu and navigation rendering
- **zShell**: Command output and interaction
- **All subsystems**: Consistent display interface
