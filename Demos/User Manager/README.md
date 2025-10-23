# User Manager Demo

A complete, production-ready **User Management System** built with **zCLI** — demonstrating full CRUD operations with a modern declarative interface.

## 🪄 What it does
- Complete user management: Create, Read, Update, Delete users
- SQLite database stored locally (project directory)
- **zUI-based interactive menu** with **zDialog forms** for data validation
- zCLI automatically creates tables and manages connections
- No external dependencies, no server setup needed

## 🚀 Quick start

### CLI Mode (Terminal Interface)
```bash
# 1) Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2) Run the user management interface
python run.py
```

### Web Mode (zBifrost Real-Time UI) 🌉
```bash
# 1) Start the WebSocket backend
python run_backend.py

# 2) Open the frontend in your browser
# Either double-click index.html OR run:
python -m http.server 8000
# Then visit: http://localhost:8000
```

**zBifrost** enables real-time CLI-to-Web communication with zero additional code — the same YAML schemas and UI definitions power both CLI and web interfaces!

## 📋 Features
The interactive menu provides:
1. **Setup Database** - Create tables (first-time setup)
2. **List Users** - View all users with pagination (most recent first)
3. **Add User** - Add new users via zDialog form (email + name validation)
4. **Search User** - Search by email or name with LIKE queries
5. **Delete User** - Remove users by ID
6. **Stop** - Exit the application

---

## 🗂 Project layout

```
Demos/User Manager/
├─ README.md                    # This file
├─ BIFROST_README.md            # zBifrost technical details
├─ requirements.txt             # Python dependencies
├─ run.py                       # CLI mode entry point
├─ run_backend.py               # Web mode backend (zBifrost WebSocket server)
├─ index.html                   # Web mode frontend (connects to zBifrost)
├─ zSchema.users_master.yaml    # Database schema definition
└─ zUI.users_menu.yaml          # Interactive menu interface
```

---

## ⚙️ Technical Details

### Architecture
- **zUI**: Menu-driven interface (`zUI.users_menu.yaml`)
- **zDialog**: Form-based data entry with validation
- **zData**: Automatic schema loading and connection management
- **zWalker**: Navigation and workflow orchestration

### Files
- **Database**: `users_master.db` (auto-created in demo directory)
- **Schema**: `zSchema.users_master.yaml` (defines table structure and validation)
- **UI Menu**: `zUI.users_menu.yaml` (declarative interface definition)
- **Entry Point**: `run.py` (minimal Python launcher - 36 lines)

### Key Highlights
- ✅ **Zero SQL**: All database operations defined in YAML
- ✅ **Zero UI Code**: Complete interface defined declaratively
- ✅ **Production Patterns**: Error handling, validation, user feedback
- ✅ **Full CRUD**: Create, Read, Update, Delete operations
- ✅ **Modern UX**: Forms, search, pagination, graceful error handling
