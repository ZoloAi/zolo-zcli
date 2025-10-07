# Zolo-zCLI

> **`zolo-zcli` is a powerful universal framework that combines traditional CLI commands with declarative configuration files (YAML/JSON), enabling rapid development of both command-line tools and web applications with unified backend/frontend architecture.**

**🔐 Authentication Required** - zCLI is a private Zolo product. Contact gal@zolo.media for access.

## 🚀 Quick Start

📘 **[Full Installation Guide](Documentation/INSTALL.md)** - Detailed setup instructions, troubleshooting, and authentication

### Installation (Authorized Users Only)

`zolo-zcli` is distributed via private GitHub repository. You must have repository access to install.

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

# Start shell mode (authentication required)
zolo-zcli --shell
```

### Python API

```python
from zCLI import zCLI

# Create a zCLI instance
cli = zCLI()

# Start shell mode
cli.run_shell()
```

## 📋 Features

### Core Capabilities
- **Dual Mode Operation**: Shell mode for commands, UI mode for menus
- **Session Isolation**: Each instance maintains its own isolated session
- **Plugin System**: Extensible through external plugin modules
- **YAML Configuration**: Drive UI and behavior through YAML files
- **Interactive Input**: Built-in input handling for fields, menus and confirmations
- **Color Support**: Rich ANSI color system for terminal output

