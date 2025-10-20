# zCLI Demo Applications

This folder contains complete, production-ready applications built with **zCLI** framework. Each demo showcases different capabilities and patterns.

**Important**: These demos are included in the Git repository but **not** in pip package distributions. Clone the repository to access them.

---

## 📦 Available Demos

### **User Manager** (`User Manager/`)

A complete User Management System demonstrating full CRUD operations with SQLite.

**Features**:
- ✅ Complete CRUD: Create, Read, Update, Delete users
- ✅ Zero SQL code: All database operations in YAML
- ✅ Zero UI code: Complete interface defined declaratively
- ✅ Production patterns: Error handling, validation, user feedback
- ✅ Modern UX: Forms, search, pagination, graceful errors

**Quick Start**:
```bash
cd "User Manager"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

**What You'll Learn**:
- zUI menu systems with bounce-back navigation
- zDialog forms with validation
- zData CRUD operations with SQLite
- Error handling and user feedback
- Schema design with type validation

---

## 🎯 More Demos Coming Soon

We're working on additional demos to showcase:
- **Blog Engine** - Multi-table relationships and joins
- **Task Manager** - Workflow orchestration with zWizard
- **REST API** - WebSocket service with zComm
- **Plugin System** - Custom business logic with zUtils

---

## 📚 Learning Path

1. **Start Here**: User Manager - Learn basic CRUD and navigation
2. **Test Suite**: `../zTestSuite/demos/` - Explore integration patterns
3. **Documentation**: `../Documentation/` - Deep dive into each subsystem

---

## 🛠️ Building Your Own

Each demo follows the same pattern:

```
MyApp/
├─ README.md                    # Setup and usage
├─ requirements.txt             # Dependencies
├─ run.py                       # Entry point (minimal Python)
├─ zSchema.*.yaml               # Data schemas
└─ zUI.*.yaml                   # Interface definitions
```

**Key Principles**:
- Keep `run.py` minimal (just initialization)
- Define everything in YAML (UI, data, workflows)
- Use zPath for workspace-relative files (`@.`)
- Leverage modifiers for navigation (`^`, `~`, `*`)

---

## 📖 Resources

- **Framework Guide**: [`../Documentation/zCLI_GUIDE.md`](../Documentation/zCLI_GUIDE.md)
- **UI Guide**: [`../Documentation/zUI_GUIDE.md`](../Documentation/zUI_GUIDE.md)
- **Schema Guide**: [`../Documentation/zSchema_GUIDE.md`](../Documentation/zSchema_GUIDE.md)
- **Test Examples**: [`../zTestSuite/demos/`](../zTestSuite/demos/)

---

## 💡 Tips

- **Start Simple**: Begin with a single-table CRUD app
- **Use Bounce**: The `^` modifier makes actions return to the menu
- **Test Early**: Run `zolo shell` to test schemas and commands
- **Read Logs**: Set `LOG_LEVEL=DEBUG` for detailed execution flow
- **Explore Tests**: The test suite has dozens of working examples

---

## 🤝 Contributing

Have a demo app you'd like to share? We welcome contributions!

1. Create a new folder in `Demos/`
2. Follow the structure above
3. Include a comprehensive README
4. Test on a fresh virtual environment
5. Submit a PR to the main repository

---

**Questions?** Check the [main README](../README.md) or open an issue on GitHub.

