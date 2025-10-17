# zCLI Configuration Hierarchy

## Production-Ready Config Structure

### 📁 System Config Directory
**Location:**
- Linux: `/etc/zolo-zcli/`
- macOS: `/etc/zolo-zcli/`
- Windows: `C:\ProgramData\zolo-zcli\`

**Files:**
- `zConfig.defaults.yaml` - Base system defaults (created on first run)
- `zMachine.yaml` - Machine identity and capabilities

**Permissions:** Admin/root to write, all users can read

---

### 👤 User Config Directory
**Location:**
- Linux: `~/.config/zolo-zcli/`
- macOS: `~/Library/Application Support/zolo-zcli/`
- Windows: `%APPDATA%\zolo-zcli\`

**Subdirectories:**
- `zConfigs/` - User configuration files
  - `zConfig.yaml` - User config overrides
  - `zConfig.machine.yaml` - User machine settings
  - `zConfig.{env}.yaml` - Environment-specific configs

**Legacy Support:**
- `~/.zolo-zcli/` - Checked for backward compatibility

**Permissions:** User read/write, no admin needed

---

## 🔄 Configuration Priority Hierarchy

Configuration is loaded and merged in this order (lowest to highest priority):

### 1. **System Defaults** (Lowest Priority)
```
/etc/zolo-zcli/zConfig.defaults.yaml
```
- Base configuration shipped with installation
- Created on first run
- Provides sensible defaults for all settings

### 2. **User Config**
```
~/.config/zolo-zcli/zConfigs/zConfig.yaml
```
- Per-user overrides of system defaults
- User-specific preferences and settings
- No admin permissions required

### 3. **zSpark Object** (Runtime Config)
```python
# Passed to zCLI at initialization
zSpark_obj = {
    "logger": "DEBUG",  # Overrides all file and env configs
    "zWorkspace": "/path/to/workspace",
    # ... other runtime settings
}
zcli = zCLI(zSpark_obj)
```
- Runtime configuration passed at initialization
- Highest priority for initial settings
- Useful for programmatic control

### 4. **Environment Variables**
```
# From .env file or shell exports
export ZOLO_ENV=production
export ZOLO_LOGGER=debug
```
- Runtime configuration via environment
- Overrides file-based configs
- Useful for CI/CD and deployment automation

### 5. **Session Runtime** (Highest Priority)
```python
# In-memory overrides during CLI session
zcli.session["config"]["key"] = "value"
```
- Handled by zSession subsystem
- Temporary, in-memory modifications
- Highest priority, overrides everything

---

## 🚀 Production Design Principles

### ✅ What We Did Right

1. **No Current Directory Configs** - Removed `Path.cwd()` based configs
   - CLI tools are system-wide, not per-project
   - Prevents confusion about which config is active
   - Consistent behavior regardless of where command runs

2. **Clear Hierarchy** - Explicit priority order
   - System defaults (base)
   - User overrides (personalization)
   - Environment exports (deployment)
   - Session runtime (temporary)

3. **Admin vs User Separation**
   - System config: Admin to write, all to read
   - User config: No special permissions needed
   - Most users never need sudo

4. **Backward Compatibility**
   - Checks legacy `~/.zolo-zcli/` for old installations
   - Gracefully migrates to new structure

### 📝 Configuration Flow

```
┌─────────────────────────────────────────┐
│  System Defaults                        │
│  /etc/zolo-zcli/zConfig.defaults.yaml   │
│  (Base configuration)                   │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  User Config                            │
│  ~/.config/zolo-zcli/zConfigs/          │
│  (Per-user overrides)                   │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  Environment Variables                  │
│  ZOLO_ENV, ZOLO_LOGGER, .env file       │
│  (Deployment settings)                  │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  zSpark Object                          │
│  Passed at zCLI initialization          │
│  (Programmatic runtime config)          │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  Session Runtime                        │
│  In-memory (zSession)                   │
│  (Temporary overrides)                  │
└─────────────────────────────────────────┘
```

---

## 🔧 First Run Behavior

1. **Check System Config**
   - If `/etc/zolo-zcli/zConfig.defaults.yaml` doesn't exist
   - Attempt to create with base defaults
   - If no permissions, warn but continue

2. **Create User Config**
   - Always create `~/.config/zolo-zcli/zConfigs/`
   - Copy defaults to user space
   - User can modify without admin access

3. **Auto-detect Machine**
   - Detect OS, hostname, hardware
   - Save to `zConfig.machine.yaml`
   - Used for machine-specific settings

---

## 📊 Config File Locations Reference

| Config Type | Linux | macOS | Windows |
|------------|-------|-------|---------|
| System defaults | `/etc/zolo-zcli/` | `/etc/zolo-zcli/` | `C:\ProgramData\zolo-zcli\` |
| User config | `~/.config/zolo-zcli/` | `~/Library/Application Support/zolo-zcli/` | `%APPDATA%\zolo-zcli\` |
| User data | `~/.local/share/zolo-zcli/` | `~/Library/Application Support/zolo-zcli/` | `%LOCALAPPDATA%\zolo-zcli\` |
| User cache | `~/.cache/zolo-zcli/` | `~/Library/Caches/zolo-zcli/` | `%LOCALAPPDATA%\zolo-zcli\Cache\` |
| Legacy (compat) | `~/.zolo-zcli/` | `~/.zolo-zcli/` | `~/.zolo-zcli/` |

---

## 🔍 Logger Level Hierarchy (Specific Example)

The logger level follows a specific hierarchy that demonstrates the configuration priority system:

### Priority Order (Highest to Lowest)
1. **zSpark Object** - `zSpark_obj["logger"]`
2. **Virtual Environment Variable** - `$ZOLO_LOGGER` (when in venv)
3. **System Environment Variable** - `$ZOLO_LOGGER`
4. **Environment Config File** - `zConfig.zEnvironment.yaml` → `logging.level`
5. **Default** - `INFO`

### Example Usage

```python
# 1. Via zSpark_obj (highest priority)
zSpark_obj = {"logger": "DEBUG"}
zcli = zCLI(zSpark_obj)

# 2. Via virtual environment (when in venv)
# In your venv activation:
export ZOLO_LOGGER=DEBUG

# 3. Via system environment
export ZOLO_LOGGER=WARNING

# 4. Via config file (lowest priority)
# In ~/.config/zolo-zcli/zConfigs/zConfig.zEnvironment.yaml:
zEnv:
  logging:
    level: "INFO"
```

### Detection Output
The system will print which source the logger level came from:
```
[SessionConfig] Logger level from zSpark: DEBUG
[SessionConfig] Logger level from virtual env: DEBUG
[SessionConfig] Logger level from system env: WARNING
[SessionConfig] Logger level from zEnvironment config: INFO
[SessionConfig] Logger level defaulting to: INFO
```

---

## 🎯 Environment Variable Support

### Current Implementation
```bash
# Logger level (fully implemented)
export ZOLO_LOGGER=DEBUG

# Deployment environment
export ZOLO_DEPLOYMENT=production
export ZOLO_ENV=production
```

### Planned Enhancements
```python
# Load from .env file in user config dir
dotenv_file = user_config_dir / ".env"

# Additional environment variables
os.getenv("ZOLO_DEBUG")
os.getenv("ZOLO_DATACENTER")
os.getenv("ZOLO_CLUSTER")

# These override file-based configs but are
# overridden by session runtime settings
```

### Use Cases
- ✅ Logger level control (implemented)
- ✅ Deployment environment detection (implemented)
- 🔄 CI/CD pipelines (partially implemented)
- 🔄 Docker containers (partially implemented)
- 🔄 Different deployment environments (partially implemented)
- 🔄 Testing with temporary settings (partially implemented)

---

## 📚 Related Documentation

- `zConfig_GUIDE.md` - Full configuration guide
- `INSTALL.md` - Installation instructions
- Test suite: `zTestSuite/zConfig_Test.py`

