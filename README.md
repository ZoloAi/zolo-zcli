# zolo-zcli

**A beginner-friendly command-line framework for building interactive menus and managing data - no programming required!**

Perfect for students, educators, and anyone who wants to create powerful CLI tools using simple YAML files.

---

## 🎯 What is zCLI?

Think of zCLI as a **"website builder for the command line"** - instead of clicking buttons, you type commands. Instead of HTML, you use simple YAML files to create:

- 📊 **Interactive menus** (like a choose-your-own-adventure)
- 🗄️ **Database management** (store homework, contacts, inventory)
- 🔄 **Automated workflows** (run multiple steps at once)
- 🔌 **Custom plugins** (add your own features)

**No programming knowledge required to get started!**

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

### Step 3: Try Your First Commands

```bash
# Get help
> help

# See where you are
> pwd

# List files
> ls

# Load a demo database
> load @.zTestSuite.demos.zSchema.sqlite_demo --as demo

# View data
> data read users --model $demo --limit 5

# Exit when done
> exit
```

**🎉 Congratulations!** You just used zCLI!

---

## 📚 Learn More

### For Beginners (Start Here!)

1. **[zShell Guide](Documentation/zShell_GUIDE.md)** - Learn the shell commands (like pwd, ls, cd)
2. **[zUI Guide](Documentation/zUI_GUIDE.md)** - Build interactive menus with YAML
3. **[zSchema Guide](Documentation/zSchema_GUIDE.md)** - Define your data (like a spreadsheet)

### For Advanced Users

4. **[zData Guide](Documentation/zData_GUIDE.md)** - Database operations (SQLite, CSV, PostgreSQL)
5. **[zWizard Guide](Documentation/zWizard_GUIDE.md)** - Multi-step workflows
6. **[zPlugin Guide](Documentation/zPlugin_GUIDE.md)** - Create custom plugins
7. **[zParser Guide](Documentation/zParser_GUIDE.md)** - Path resolution and syntax
8. **[zLoader Guide](Documentation/zLoader_GUIDE.md)** - Caching system
9. **[zWalker Guide](Documentation/zWalker_GUIDE.md)** - UI navigation

### For Developers & AI

10. **[zCLI Guide](Documentation/zCLI_GUIDE.md)** - Complete framework guide for building applications
11. **[AGENT.md](Documentation/AGENT.md)** - LLM-optimized technical reference
12. **[INSTALL.md](Documentation/INSTALL.md)** - Complete installation & uninstall guide

---

## 🎓 What Can You Build?

### Example Projects (Great for Learning!)

- **📝 Homework Tracker** - Track assignments, due dates, grades
- **📇 Contact Manager** - Store friends, family, phone numbers
- **📦 Inventory System** - Manage items, quantities, locations
- **🎮 Text Adventure Game** - Create interactive stories with menus
- **💰 Budget Tracker** - Track income, expenses, savings
- **📚 Book Library** - Catalog books, track reading progress

All using simple YAML files - no coding required!

---

## ✨ Key Features

### 🎯 Beginner-Friendly
- **Simple YAML syntax** - If you can write a list, you can use zCLI
- **Interactive shell** - Type commands, get instant results
- **Built-in help** - Type `help` anytime to see what's available
- **Practice exercises** - Learn by doing with guided tutorials

### 🔧 Powerful Tools
- **20 shell commands** - Like bash, but easier (pwd, cd, ls, echo, etc.)
- **3 database formats** - SQLite, CSV, PostgreSQL
- **Plugin system** - Extend with Python functions
- **Transaction support** - All-or-nothing operations (safe!)

### 🎨 Declarative Design
- **YAML menus** - Build UIs without code
- **YAML schemas** - Define data structure simply
- **YAML workflows** - Automate multi-step tasks
- **Cross-platform** - Works on Mac, Linux, Windows

---

## 🧪 Testing

zCLI includes a comprehensive test suite to ensure everything works correctly.

### Run All Tests

```bash
cd zTestSuite
python3 run_all_tests.py
```

**Current Status:** ✅ **524/524 tests passing (100%)**

### Run Specific Tests

```bash
# Test individual subsystems
python3 zTestSuite/zConfig_Test.py    # Configuration
python3 zTestSuite/zData_Test.py      # Database operations
python3 zTestSuite/zShell_Test.py     # Shell commands
python3 zTestSuite/zWizard_Test.py    # Workflows
python3 zTestSuite/zWalker_Test.py    # UI navigation
```

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

## 🎓 Perfect For Education

### High School Students
- Learn command-line basics (pwd, cd, ls)
- Understand databases (tables, fields, queries)
- Practice YAML (simple, readable syntax)
- Build real projects (homework tracker, contact list)

### Computer Science Classes
- Introduction to CLI tools
- Database fundamentals
- Configuration management
- Software architecture concepts

### Self-Learners
- No programming background needed
- Step-by-step tutorials included
- Practice exercises with solutions
- Real-world examples

---

## 🏗️ Architecture

zCLI is built with a clean 3-layer architecture:

**Layer 0 - Foundation**
- Configuration, paths, session management

**Layer 1 - Core**
- Display, authentication, parsing, caching

**Layer 2 - Services**
- Shell, data, workflows, dialogs, functions

**Layer 3 - Orchestrator**
- UI navigation and menu systems

**Total:** 15 integrated subsystems, all tested and production-ready

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

### Example 2: Create Alias
```bash
> alias showusers="data read users --model $db --limit 10"
> showusers
```

### Example 3: Multi-Step Workflow
```bash
> wizard --start
> data insert users --model $db --fields name,age --values "Alice",16
> data insert users --model $db --fields name,age --values "Bob",17
> wizard --run
```

### Example 4: Load Plugin
```bash
> plugin load @.zTestSuite.demos.test_plugin
> func test_plugin.hello_world()
```

---

## 💬 Get Help

- **In the shell:** Type `help` or `help <command>`
- **Documentation:** Read the [guides](Documentation/)
- **Issues:** Open a [GitHub issue](https://github.com/ZoloAi/zolo-zcli/issues)
- **Email:** gal@zolo.media

---

## 🌟 Why zCLI?

**For Students:**
- Learn professional tools (command line, databases)
- Build real projects for school
- No programming required to start
- Grow into advanced features when ready

**For Educators:**
- Teach CLI basics without complexity
- Demonstrate database concepts visually
- Assign practical projects
- Cross-platform (works everywhere)

**For Developers:**
- Rapid prototyping with YAML
- Plugin system for custom logic
- Clean architecture (15 subsystems)
- 100% test coverage

**For Everyone:**
- Simple to start, powerful when needed
- Declarative design (describe what, not how)
- Production-ready and well-tested
- Free and open source

---

**Ready to get started?** Install zCLI and type `help` - you've got this! 🚀

---

**Made with ❤️ by Gal Nachshon** | **Version 1.5.1** | **© 2024**
