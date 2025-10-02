# zCLI Framework

A powerful CLI framework that uses YAML for configuration and routing, featuring an interactive shell, TUI mode, and a comprehensive plugin system. Built for rapid development of command-line tools with rich interactive features and session persistence.

**🔐 Authentication Required** - zCLI is a private Zolo product. Contact gal@zolo.media for access.

## 🚀 Quick Start

📘 **[Full Installation Guide](Documentation/INSTALL.md)** - Detailed setup instructions, troubleshooting, and authentication

### Installation (Authorized Users Only)

zCLI is distributed via private GitHub repository. You must have repository access to install.

```bash
# Install from private GitHub (requires authentication)
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git

# Or with personal access token
pip install git+https://TOKEN@github.com/ZoloAi/zolo-zcli.git
```

### Basic Usage

```bash
# Show version
zolo-zcli --version

# Start interactive shell mode (authentication required)
zolo-zcli --shell
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
- **Interactive Input**: Built-in input handling for fields, menus and confirmations
- **Color Support**: Rich ANSI color system for terminal output

### Subsystems
- **CRUD Operations**: Database operations with field validation and rule enforcement
- **Display System**: Terminal UI rendering with consistent styling and formatting
- **Parser System**: YAML schema validation and expression parsing
- **Socket System**: WebSocket support for real-time communication
- **Authentication**: Built-in auth system for apps extending beyond zCLI
- **Logger**: Structured logging with color-coded output levels

