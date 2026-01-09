# User Manager Demo - Clean Patterns

## The "3 Steps Always" Pattern

All zKernel applications follow the same 3-step pattern, regardless of mode:

```python
# Step 1: Import zKernel
from zKernel import zKernel

# Step 2: Create zSpark
z = zKernel({...})

# Step 3: RUN walker
z.walker.run()
```

The **only** difference between Terminal and zBifrost modes is the `zMode` flag in zSpark.

---

## Terminal Mode (run.py)

```python
#!/usr/bin/env python3
from pathlib import Path
from zKernel import zKernel

z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"  # ← Terminal mode
})

z.walker.run()  # Starts interactive menu
```

**Result**: Interactive Terminal menu with user navigation

---

## zBifrost Mode (run_backend.py)

```python
#!/usr/bin/env python3
from pathlib import Path
from zKernel import zKernel

z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "zBifrost",  # ← zBifrost mode
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False,
        "allowed_origins": ["http://localhost", "http://127.0.0.1"],
        "max_connections": 10
    }
})

z.walker.run()  # Starts WebSocket server
```

**Result**: WebSocket server running on port 8765

---

## Multiple Backend Types

The same pattern works for different data backends:

### SQLite (test_sqlite.py)
```python
z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_sqlite",  # ← SQLite UI
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
```

### CSV (test_csv.py)
```python
z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_csv",  # ← CSV UI
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
```

---

## Key Insights

1. **One Pattern**: Terminal and zBifrost use identical code structure
2. **Mode Switch**: Only `zMode` determines behavior
3. **No Internal Imports**: No need to import internal modules
4. **Clean API**: `walker.run()` handles everything based on mode
5. **Auto-Detection**: Walker detects mode and starts appropriate interface

---

## What Happens Internally

### Terminal Mode
- `walker.run()` → loads UI → starts interactive menu loop
- User navigates menus, forms, and commands
- Synchronous, blocking

### zBifrost Mode
- `walker.run()` → detects zBifrost → starts WebSocket server
- Clients connect and send commands
- Walker provides context for command dispatch
- Async, blocking

---

## Files Structure

```
User Manager/
├── run.py                      # Terminal mode entry point
├── run_backend.py              # zBifrost mode entry point
├── test_sqlite.py              # SQLite Terminal demo
├── test_csv.py                 # CSV Terminal demo
├── zUI.users_menu.yaml         # Original UI (uses users_master)
├── zUI.users_sqlite.yaml       # SQLite-specific UI
├── zUI.users_csv.yaml          # CSV-specific UI
├── zSchema.users_master.yaml   # Original SQLite schema
├── zSchema.users_sqlite.yaml   # SQLite schema
└── zSchema.users_csv.yaml      # CSV schema
```

All use the same clean 3-step pattern!

