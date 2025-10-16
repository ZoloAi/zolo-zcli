# Zolo-zCLI

> **`zolo-zcli` is a powerful universal framework that combines traditional CLI commands with declarative configuration files (YAML/JSON), enabling rapid development of both command-line tools and web applications with unified backend/frontend architecture.**

**🏷️ Trademark Notice:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

**📄 License:** MIT License with Ethical Use Clause - See [LICENSE](LICENSE) for details.

## 🚀 Quick Start

📘 **[Full Installation Guide](Documentation/INSTALL.md)** - Detailed setup instructions, troubleshooting, and authentication

### Installation

`zolo-zcli` is available on PyPI and GitHub.

```bash
# Install from PyPI (recommended)
pip install zolo-zcli

# Or install from GitHub
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# Or install specific version
pip install git+https://github.com/ZoloAi/zolo-zcli.git@v1.4.0
```

### Basic Usage

```bash
# Show version
zolo-zcli --version

# Start shell mode (authentication required)
zolo-zcli shell
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

