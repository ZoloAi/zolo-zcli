# zCLI Utils

Common utility modules for zCLI subsystems.

## 📁 Available Utilities

### StyledPrinter (`styled_printer.py`)

Provides styled console output capabilities for subsystems that need to print before zDisplay is available.

#### Features:
- **Styled Ready Messages** - Consistent subsystem ready banners
- **Fallback Support** - Works even if zDisplay colors aren't available
- **Multiple Message Types** - Success, error, warning, info messages
- **Configurable** - Customizable colors, widths, and styles

#### Usage Examples:

```python
# Centralized import (recommended)
from zCLI import print_ready

# Or direct import
from zCLI.utils.styled_printer import print_ready, StyledPrinter

# Global function - works with any subsystem
print_ready("zConfig")      # Auto-maps to SCHEMA color
print_ready("zAuth")        # Auto-maps to AUTH color  
print_ready("zData")        # Auto-maps to DATA color
print_ready("zShell")       # Auto-maps to SHELL color
print_ready("CustomSubsystem")  # Falls back to SCHEMA color

# Custom color override
print_ready("zConfig", "ERROR")  # Override auto-mapping

# General styled printing
StyledPrinter.print_success("Operation completed", "Data saved successfully")
StyledPrinter.print_error("Operation failed", "File not found")
StyledPrinter.print_warning("Deprecated feature", "Will be removed in v2.0")

# Custom banner
StyledPrinter.print_banner("Welcome to zCLI", "=", 60)
```

#### Available Functions:

**Subsystem Ready Messages:**
- `print_ready(subsystem_name, color=None)` - ✨ **Global function** - accepts any subsystem
- `print_subsystem_ready(name, color)` - Low-level function
- `print_config_ready()` - Backward compatibility
- `print_auth_ready()` - Backward compatibility  
- `print_data_ready()` - Backward compatibility
- `print_shell_ready()` - Backward compatibility

**Styled Messages:**
- `StyledPrinter.print_success(message, details)`
- `StyledPrinter.print_error(message, details)`
- `StyledPrinter.print_warning(message, details)`
- `StyledPrinter.print_info(message, details)`

**Custom Styling:**
- `StyledPrinter.print_ready(label, color, width)`
- `StyledPrinter.print_banner(text, char, width)`
- `StyledPrinter.print_section(title, char, width)`

#### Color Support:

The printer automatically detects and uses zDisplay colors when available, with graceful fallback to plain text.

**Auto-mapped colors:**
- `zConfig` → `SCHEMA` (green)
- `zAuth` → `AUTH` (blue) 
- `zData` → `DATA` (purple)
- `zShell` → `SHELL` (yellow)
- `zDisplay` → `DISPLAY`
- `zWalker` → `WALKER`
- `zWizard` → `WIZARD`
- `zNavigation` → `NAV`
- `zDialog` → `DIALOG`
- `zDispatch` → `DISPATCH`
- `zFunc` → `FUNC`
- `zLoader` → `LOADER`
- `zLogger` → `LOGGER`
- `zOpen` → `OPEN`
- `zParser` → `PARSER`
- `zSession` → `SESSION`
- `zUtils` → `UTILS`
- **Unknown subsystems** → `SCHEMA` (default)

**Available colors:** `SCHEMA`, `AUTH`, `DATA`, `SHELL`, `ERROR`, `SUCCESS`, `WARNING`, `INFO`

## 🎯 Design Principles

### ✅ **Early Subsystem Support**
- Works before zDisplay is initialized
- No circular dependencies
- Graceful fallbacks

### ✅ **Consistent Styling**
- Standardized ready messages across subsystems
- Consistent error/success message formatting
- Unified visual language

### ✅ **Extensible**
- Easy to add new subsystem ready messages
- Customizable colors and styles
- Modular design

## 🔧 Integration

### For New Subsystems:

```python
# In your subsystem's __init__ method
from zCLI import print_ready  # Centralized import

def __init__(self):
    # ... initialization code ...
    print_ready("zYourSubsystem")  # Auto-maps color, or falls back to SCHEMA
    # OR with custom color:
    print_ready("zYourSubsystem", "YOUR_COLOR")
```

### For Error Handling:

```python
from zCLI.utils.styled_printer import StyledPrinter

try:
    # ... risky operation ...
    StyledPrinter.print_success("Operation completed")
except Exception as e:
    StyledPrinter.print_error("Operation failed", str(e))
```

## 📚 Related Documentation

- `../subsystems/zDisplay/` - Full display system (when available)
- `../subsystems/zConfig/` - Configuration management
- `../../Documentation/` - User guides and references
