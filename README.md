# zCLI Framework

A YAML-driven CLI framework for interactive applications, providing both shell and UI modes with comprehensive session management and plugin support.

## 🚀 Quick Start

### Installation

```bash
pip install zolo-zcli
```

### Basic Usage

```bash
# Start interactive shell mode
zolo-zcli --shell

# Show version
zolo-zcli --version
```

### Python API

```python
from zCLI import zCLI

# Create a zCLI instance
cli = zCLI()

# Start interactive shell
cli.run_interactive()
```

## 📋 Features

### Core Capabilities
- **Dual Mode Operation**: Shell mode for commands, UI mode for menus
- **Session Isolation**: Each instance maintains its own isolated session
- **Plugin System**: Extensible through external plugin modules
- **YAML Configuration**: Drive UI and behavior through YAML files
- **Comprehensive Testing**: 79 tests covering all functionality

### Subsystems
- **CRUD Operations**: Database operations with validation and JOIN support
- **Function Execution**: Dynamic function calling with parameter handling
- **Display System**: Rich UI rendering with colors and formatting
- **Session Management**: Isolated session handling for multi-user support
- **Parser System**: YAML and expression parsing capabilities
- **Socket Communication**: WebSocket support for real-time features

## 🏗️ Architecture

```
zCLI/
├── zCore/           # Core CLI functionality (shell mode)
├── subsystems/      # Shared subsystems (CRUD, Display, etc.)
├── walker/          # UI/Walker mode (YAML-driven menus)
├── utils/           # Utility modules (logging, plugins)
└── Documentation/   # Comprehensive documentation
```

### Core Components

- **`zCLI`**: Main engine that manages all subsystems
- **`InteractiveShell`**: Command-line interface for shell mode
- **`zWalker`**: YAML-driven menu navigation for UI mode
- **`ZParser`**: YAML and expression parsing
- **`ZCRUD`**: Database operations with validation
- **`ZUtils`**: Core utilities (ID generation, plugin loading)

## 🔧 Configuration

### Session Configuration

```python
zcli = zCLI({
    "zWorkspace": "/path/to/workspace",
    "zMode": "Terminal",  # or "UI"
    "zVaFilename": "ui.yaml",  # for UI mode
    "zVaFile_path": ".ui.yaml"
})
```

### Plugin Loading

```python
# Load external plugins (e.g., zCloud utilities)
zcli.utils.load_plugins([
    "zCloud.Logic.zCloudUtils",
    "/path/to/plugin.py"
])
```

## 🧪 Testing

The framework includes a comprehensive test suite with 79 tests covering:

- **Session Isolation**: Multi-instance session management
- **Subsystem Integration**: All subsystems working together
- **Parser Functionality**: YAML and expression parsing
- **Plugin Loading**: External module integration
- **Version Management**: Package version handling

Run tests:
```bash
# Via CLI
zolo-zcli --shell
> test run

# Via Python
from zCLI.zCore.zCLI_Test import run_all_tests
run_all_tests()
```

## 📚 Documentation

Comprehensive documentation is available in the `Documentation/` folder:

- **`zCore_README.md`**: Core functionality documentation
- **`ARCHITECTURE.md`**: CRUD subsystem architecture
- **`JOIN_GUIDE.md`**: Multi-table query guide
- **`VALIDATION_GUIDE.md`**: Data validation documentation
- **`ZBACK_FIX.md`**: Walker system fixes and improvements

## 🔌 Plugin Development

Create custom plugins for zCLI:

```python
# my_plugin.py
def my_function(param):
    return f"Hello, {param}!"

def get_plugin_info():
    return {
        "name": "My Plugin",
        "version": "1.0.0",
        "functions": ["my_function"]
    }
```

Load the plugin:
```python
zcli.utils.load_plugins(["/path/to/my_plugin.py"])
result = zcli.utils.my_function("World")  # "Hello, World!"
```

## 🎯 Use Cases

- **Interactive CLI Tools**: Build rich command-line interfaces
- **Configuration Management**: YAML-driven application configuration
- **Database Operations**: CRUD operations with validation
- **Multi-step Workflows**: Wizard-based user flows
- **Plugin-based Extensions**: Modular application architecture

## 📦 Package Information

- **Name**: `zolo-zcli`
- **Version**: 1.0.0
- **Author**: Gal Nachshon
- **License**: Private - All Rights Reserved
- **Python**: >=3.8

## 🤝 Contributing

This is a private project. For questions or support, contact the development team.

## 📄 License

Private - All Rights Reserved

---

**zCLI Framework** - Making CLI development powerful and flexible.
