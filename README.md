# zCLI Framework v1.3.0 🚀

A powerful CLI framework that uses YAML for configuration and routing, featuring an interactive shell, TUI mode, comprehensive CRUD operations, and a revolutionary **quantum-inspired data integrity system**. Built for rapid development of command-line tools with rich interactive features and session persistence.

**🔐 Authentication Required** - zCLI is a private Zolo product. Contact gal@zolo.media for access.

**🌈 NEW in v1.3.0:** UPSERT operations, Full ALTER TABLE support, Migration history tracking, and RGB Weak Nuclear Force System for automatic data health monitoring!

## 🚀 Quick Start

📘 **[Full Installation Guide](Documentation/INSTALL.md)** - Detailed setup instructions, troubleshooting, and authentication

### Installation (Authorized Users Only)

zCLI is distributed via private GitHub repository. You must have repository access to install.

```bash
# Install latest version (v1.3.0)
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.3.0

# Or install from main branch
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git

# Or with personal access token
pip install git+https://TOKEN@github.com/ZoloAi/zolo-zcli.git@v1.3.0
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
- **CRUD Operations**: Complete database management with advanced features
  - ✅ Create, Read, Update, Delete
  - ✅ **UPSERT** (v1.3.0) - Atomic insert-or-update
  - ✅ JOIN support with nested relationships
  - ✅ Advanced WHERE operators (LIKE, IN, BETWEEN, OR)
  - ✅ Composite primary keys
  - ✅ Index support (simple, composite, unique, partial)
- **Schema Migration**: Automatic schema evolution
  - ✅ **ADD COLUMN** - Automatic detection and migration
  - ✅ **DROP COLUMN** (v1.3.0) - Safe column removal
  - ✅ **RENAME COLUMN** (v1.3.0) - Column renaming
  - ✅ **RENAME TABLE** (v1.3.0) - Table renaming
  - ✅ **Migration History** (v1.3.0) - Complete audit trail
- **RGB System** (v1.3.0): Quantum-inspired data integrity monitoring
  - 🔴 Time freshness tracking
  - 🟢 Access frequency monitoring
  - 🔵 Migration stability analysis
  - 📊 Health analytics and reporting
  - 💡 Intelligent migration suggestions
- **Display System**: Terminal UI rendering with consistent styling and formatting
- **Parser System**: YAML schema validation and expression parsing
- **Socket System**: WebSocket support for real-time communication
- **Authentication**: Built-in auth system for apps extending beyond zCLI
- **Logger**: Structured logging with color-coded output levels

