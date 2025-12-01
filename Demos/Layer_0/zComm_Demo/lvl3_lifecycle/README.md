## Level 3: Service Lifecycle

Advanced service management - programmatically start, stop, and control local services.

### What You'll Learn

- Start services programmatically (no manual `brew services start`)
- Check service status before/after operations
- Handle service start failures gracefully
- Get connection info for newly started services
- Full service lifecycle control from code

### Installation Requirements

Service lifecycle management requires PostgreSQL installed and optional dependencies:

```bash
# Install PostgreSQL (macOS)
brew install postgresql

# Install PostgreSQL (Linux)
sudo apt-get install postgresql

# Install zCLI with PostgreSQL support
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git[postgresql]
```

See [Installation Guide](../../../Documentation/INSTALL.md) for complete setup instructions.

### System Permissions

Starting/stopping services may require:
- **macOS**: Homebrew services access
- **Linux**: `sudo` permissions for systemd
- **Windows**: Administrator privileges for Windows services

### Demos

#### **`service_start.py`** - Service Lifecycle Management
- Declare: Start service with one call
- Declare: Get connection info
- zComm handles orchestration (check, start, wait, verify)
- No manual status checks or waiting
- Pure declarative pattern

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/lvl3_lifecycle/service_start.py
```

**Expected Output (if PostgreSQL installed):**
```
=== Service Lifecycle ===

Starting PostgreSQL...
✓ Service started

Connection ready:
  localhost:5432

Connect: psql -h localhost -p 5432

=============================================
Stop: z.comm.stop_service('postgresql')
```

**Expected Output (if not installed):**
```
=== Service Lifecycle ===

Starting PostgreSQL...
✗ Failed to start

Requirements:
  brew install postgresql  (macOS)
  sudo apt-get install postgresql  (Linux)
```

### Key Takeaways

- **Declarative control:** `z.comm.start_service()` - that's it
- **No orchestration:** zComm handles check/start/wait/verify internally
- **Simple API:** One call to start, one call for connection info
- **Cross-platform:** Works on macOS, Linux, and Windows
- **Error handling:** Returns boolean success/failure
- **Level 3 pattern:** Declare WHAT you want, not HOW to do it

