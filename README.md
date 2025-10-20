# zolo-zcli

**A declarative command-line framework for building interactive applications and data management tools.**

zCLI provides a clean, YAML-driven approach to CLI development with a full-featured shell, multi-backend database support, and extensible plugin architecture.

---

## 🎯 What is zCLI?

zCLI is a **declarative CLI framework** that separates interface definition from implementation. Think of it as "React for the command line" - you define your application structure in YAML, then zCLI handles the execution:

- 📊 **Interactive TUI** - Declare menus and navigation flows in YAML
- 🗄️ **Multi-backend data layer** - SQLite, CSV, PostgreSQL with unified interface
- 🔄 **Workflow orchestration** - Multi-step processes with transaction support
- 🔌 **Plugin architecture** - Extend functionality with Python modules
- ⚡ **Shell environment** - Full-featured CLI with 20+ built-in commands

---

## 🚀 Quick Start

### Step 1: Install

```bash
# Install from GitHub (requires SSH key setup)
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git

# Or install specific version
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.5.0

# Verify installation
zolo --version
```

📘 **Need help?** See the [Full Installation Guide](Documentation/INSTALL.md) for SSH setup, HTTPS alternatives, and troubleshooting.

### Step 2: Start the Shell

```bash
# Launch interactive shell
zolo-zcli shell

# You'll see:
╔═══════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                 ║
╚═══════════════════════════════════════════════════════════╝

Type 'help' for available commands
>
```

### Step 3: Explore the Framework

```bash
# Get help and see available commands
> help

# Navigate and explore
> pwd
> ls

# Load a demo schema to see data operations
> load @.zTestSuite.demos.zSchema.sqlite_demo --as demo

# Execute database operations
> data read users --model $demo --limit 5
> data insert users --model $demo --fields name,email --values "John","john@example.com"

# Exit when done
> exit
```

**Ready to build your application!**

---

## 📚 Documentation

### Core Concepts

1. **[zShell Guide](Documentation/zShell_GUIDE.md)** - Shell commands and navigation (pwd, ls, cd, aliases)
2. **[zUI Guide](Documentation/zUI_GUIDE.md)** - Declarative UI definition with YAML menus
3. **[zSchema Guide](Documentation/zSchema_GUIDE.md)** - Data schema definition and validation

### Framework Components

4. **[zData Guide](Documentation/zData_GUIDE.md)** - Multi-backend data operations (SQLite, CSV, PostgreSQL)
5. **[zWizard Guide](Documentation/zWizard_GUIDE.md)** - Multi-step workflow orchestration
6. **[zPlugin Guide](Documentation/zPlugin_GUIDE.md)** - Plugin development and extension system
7. **[zParser Guide](Documentation/zParser_GUIDE.md)** - zPath resolution and command parsing
8. **[zLoader Guide](Documentation/zLoader_GUIDE.md)** - File caching and resource management
9. **[zWalker Guide](Documentation/zWalker_GUIDE.md)** - UI navigation and menu system

### Advanced Resources

10. **[zCLI Guide](Documentation/zCLI_GUIDE.md)** - Complete framework architecture and application development
11. **[AGENT.md](Documentation/AGENT.md)** - Technical reference optimized for AI assistants
12. **[INSTALL.md](Documentation/INSTALL.md)** - Installation, configuration, and deployment guide

---

## 🚀 Use Cases

### Application Examples

- **📝 Project Management** - Track tasks, deadlines, and team members
- **📇 CRM Systems** - Customer relationship management with search and reporting
- **📦 Inventory Management** - Stock tracking with automated workflows
- **🎮 Interactive Tools** - CLI games, calculators, and utilities
- **💰 Financial Applications** - Budget trackers, expense managers, reporting dashboards
- **📚 Content Management** - Document catalogs, knowledge bases, reference systems

### Development Workflows

- **Rapid Prototyping** - Define UI and data layers declaratively
- **Data Migration Tools** - Multi-step ETL processes with transaction safety
- **System Administration** - Automated server management and monitoring
- **DevOps Utilities** - Deployment pipelines and environment management
- **Code Generation** - Scaffolding and template-based development

---

## ✨ Key Features

### 🏗️ Architecture
- **Layered design** - Clean separation between foundation, core, services, and orchestration layers
- **Declarative configuration** - Define application structure in YAML, not code
- **Plugin architecture** - Extensible with Python modules and custom functions
- **Multi-backend support** - SQLite, CSV, and PostgreSQL with unified interface

### ⚡ Core Components
- **Interactive shell** - 20+ built-in commands (pwd, cd, ls, echo, alias, history, etc.)
- **Transaction management** - ACID-compliant operations with rollback support
- **Path resolution** - zPath syntax for workspace-relative, absolute, and machine paths
- **Caching system** - Intelligent file and schema caching for performance

### 🎨 Developer Experience
- **Type safety** - Schema validation and data type enforcement
- **Error handling** - Comprehensive error reporting and recovery
- **Testing framework** - 524 tests with 100% passing rate
- **Cross-platform** - Native support for macOS, Linux, and Windows
- **Documentation** - Complete API reference and usage guides

---

## 🧪 Testing

zCLI maintains comprehensive test coverage to ensure reliability and correctness.

### Test Framework

```bash
# Run full test suite
python3 -m unittest discover -s zTestSuite -p "*_Test.py" -v

# Run specific subsystem tests
python3 zTestSuite/zData_Test.py      # Database operations
python3 zTestSuite/zUtils_Test.py     # Plugin system
python3 zTestSuite/zWizard_Test.py    # Workflow orchestration
python3 zTestSuite/zWalker_Test.py    # UI navigation
python3 zTestSuite/zShell_Test.py     # Shell commands
```

**Test Status:** ✅ **524/524 tests passing (100%)**

### Test Coverage

| Subsystem | Tests | Status |
|-----------|-------|--------|
| zConfig   | 30    | ✅ 100% |
| zComm     | 34    | ✅ 100% |
| zDisplay  | 49    | ✅ 100% |
| zAuth     | 17    | ✅ 100% |
| zDispatch | 37    | ✅ 100% |
| zParser   | 39    | ✅ 100% |
| zLoader   | 50    | ✅ 100% |
| zFunc     | 29    | ✅ 100% |
| zDialog   | 34    | ✅ 100% |
| zOpen     | 38    | ✅ 100% |
| zShell    | 47    | ✅ 100% |
| zWizard   | 26    | ✅ 100% |
| zUtils    | 40    | ✅ 100% |
| zData     | 37    | ✅ 100% |
| zWalker   | 17    | ✅ 100% |
| **TOTAL** | **524** | **✅ 100%** |

---

## 🎯 Framework Benefits

### For Developers
- **Rapid prototyping** - Define complex UIs and workflows declaratively
- **Production ready** - Full transaction support and error handling
- **Extensible** - Plugin system for custom business logic
- **Testable** - Comprehensive test suite ensures code quality

### For Teams
- **Consistent interface** - Standardized YAML configuration across projects
- **Maintainable** - Separation of concerns between UI, data, and logic
- **Scalable** - Multi-backend support grows with your needs
- **Documentation** - Self-documenting YAML configurations

### For Operations
- **Cross-platform** - Deploy on any operating system
- **Lightweight** - Minimal dependencies and fast startup
- **Reliable** - Extensive testing and error recovery mechanisms
- **Configurable** - Environment-specific settings and deployment options

---

## 🏗️ Architecture

zCLI implements a clean layered architecture with clear separation of concerns:

**Layer 0 - Foundation (zConfig)**
- Configuration management, path resolution, session handling
- Cross-platform compatibility and environment detection

**Layer 1 - Core Services**
- Display system (zDisplay), authentication (zAuth), parsing (zParser)
- Caching and resource management (zLoader), command dispatch (zDispatch)

**Layer 2 - Business Logic**
- Data operations (zData), shell interface (zShell), workflow engine (zWizard)
- Dialog system (zDialog), function execution (zFunc), utilities (zUtils)

**Layer 3 - Orchestration (zWalker)**
- UI navigation, menu systems, and application flow control

**Total:** 15 integrated subsystems with comprehensive testing and production-ready reliability

---

## 📦 Installation Options

### Basic Install (SQLite only)
```bash
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git
```

### With CSV Support
```bash
pip install "zolo-zcli[csv] @ git+ssh://git@github.com/ZoloAi/zolo-zcli.git"
```

### With PostgreSQL Support
```bash
pip install "zolo-zcli[postgresql] @ git+ssh://git@github.com/ZoloAi/zolo-zcli.git"
```

### Full Install (All Features)
```bash
pip install "zolo-zcli[all] @ git+ssh://git@github.com/ZoloAi/zolo-zcli.git"
```

### Development Install
```bash
git clone git@github.com:ZoloAi/zolo-zcli.git
cd zolo-zcli
pip install -e .
```

📘 **More options:** See [INSTALL.md](Documentation/INSTALL.md) for SSH key setup, HTTPS alternatives, and troubleshooting.

---

## 🗑️ Uninstalling

### Keep Your Data (Safe for Upgrades)
```bash
zolo-zcli uninstall
```

### Remove Everything
```bash
zolo-zcli uninstall --clean
```

📘 **More options:** See [INSTALL.md](Documentation/INSTALL.md) for dependency management and manual cleanup.

---

## 🤝 Contributing

We welcome contributions! Whether you're:
- 🐛 Reporting bugs
- 💡 Suggesting features
- 📝 Improving documentation
- 🧪 Adding tests
- 🔧 Fixing issues

Please open an issue or pull request on GitHub.

---

## 📄 License

**MIT License with Ethical Use Clause**

Free for educational, personal, and commercial use. See [LICENSE](LICENSE) for full details.

**🏷️ Trademark Notice:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

---

## 🔗 Links

- **GitHub:** [https://github.com/ZoloAi/zolo-zcli](https://github.com/ZoloAi/zolo-zcli)
- **Documentation:** [Documentation/](Documentation/)
- **Issues:** [GitHub Issues](https://github.com/ZoloAi/zolo-zcli/issues)
- **PyPI:** [https://pypi.org/project/zolo-zcli/](https://pypi.org/project/zolo-zcli/)

---

## 📊 Project Stats

- **Version:** 1.5.1
- **Python:** 3.8+
- **Tests:** 524 (100% passing)
- **Subsystems:** 15
- **Shell Commands:** 20
- **Documentation:** 15 guides
- **Status:** ✅ Production Ready

---

## 🎯 Quick Examples

### Example 1: View Data
```bash
> load @.zTestSuite.demos.zSchema.sqlite_demo --as db
> data read users --model $db --limit 5
```

### Example 2: Command Aliasing
```bash
> alias showusers="data read users --model $db --limit 10"
> showusers
```

### Example 3: Transaction Workflow
```bash
> wizard --start
> data insert users --model $db --fields name,age --values "Alice",16
> data insert users --model $db --fields name,age --values "Bob",17
> wizard --run  # Commits all changes atomically
```

### Example 4: Plugin Integration
```bash
> plugin load @.zTestSuite.demos.test_plugin
> func test_plugin.generate_uuid()
```

---

## 💬 Get Help

- **In the shell:** Type `help` or `help <command>`
- **Documentation:** Read the [guides](Documentation/)
- **Issues:** Open a [GitHub issue](https://github.com/ZoloAi/zolo-zcli/issues)
- **Email:** gal@zolo.media

---

## 🌟 Why Choose zCLI?

**Declarative Development**
- Define application structure in YAML, focus on business logic
- Separation of concerns between interface and implementation
- Configuration-driven development reduces boilerplate code

**Production Quality**
- Comprehensive test suite (524 tests, 100% passing)
- Transaction support ensures data integrity
- Cross-platform compatibility without modification
- Extensive error handling and recovery mechanisms

**Developer Productivity**
- Rapid prototyping with minimal code
- Plugin architecture for extensibility
- Built-in shell with 20+ commands
- Clear documentation and examples

**Enterprise Ready**
- Multi-backend database support (SQLite, CSV, PostgreSQL)
- Layered architecture supports maintainable codebases
- Type safety and schema validation
- Configurable for different environments

---

**Ready to build your next CLI application?** Install zCLI and start with `help` - the framework handles the complexity! 🚀

---

**Made with ❤️ by Gal Nachshon** | **Version 1.5.1** | **© 2024**
