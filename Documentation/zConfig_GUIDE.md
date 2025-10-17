# zConfig: The Settings Subsystem

## **Overview**
- **zConfig** is **zCLI**'s foundational configuration management subsystem
- Provides hierarchical configuration loading, machine detection, environment management, and session-logger integration
- Initializes first in zCLI, establishing the configuration foundation for all other subsystems

## **Architecture**

### **Layer 0 Foundation**
**zConfig** operates as a Layer 0 (foundation) subsystem, meaning it:
- Initializes before all other subsystems
- Provides configuration services to the entire zCLI ecosystem
- Has no dependencies on other zCLI subsystems
- Establishes the configuration foundation for zCLI

### **Modular Design**
```
zConfig/
├── zConfig.py                    # Main configuration manager
└── zConfig_modules/
    ├── config_paths.py          # Cross-platform path resolution
    ├── config_machine.py        # Machine-specific configuration
    ├── config_environment.py    # Environment and deployment settings
    ├── config_session.py        # Session management with logger integration
    ├── config_logger.py         # Logger configuration and management
    ├── config_persistence.py    # Configuration persistence and validation
    └── helpers/
        ├── config_helpers.py    # Shared configuration utilities
        ├── environment_helpers.py # Environment detection helpers
        └── machine_detectors.py  # Machine capability detection
```
---

## **Core Features**

### **1. Hierarchical Configuration Loading**
- **zSpark Object** → **Virtual Environment** → **System Environment** → **Config Files** → **Defaults**
- Cross-platform path resolution and YAML-based configuration files
- Logger level hierarchy with environment variable support

### **2. Machine Configuration Management**
- Auto-detection of system capabilities (OS, architecture, tools)
- User preference management (browser, IDE, terminal)
- Persistent zConfig.machine.yaml configuration

### **3. Session and Logger Integration**
- Integrated session management with automatic logger initialization
- Atomic session creation with logger as part of session lifecycle
- Environment-based logger configuration

### **4. Configuration Persistence**
- Runtime configuration updates with disk persistence
- Validation and error handling
- Reset to auto-detected defaults

### **5. Environment Configuration**
- Environment-specific settings (deployment, datacenter, cluster)
- Network, security, and performance configuration
- Custom field support for extensibility

---

## 📁 **Configuration Files**

### **Package Configuration**
```
config/
└── zConfig.default.yaml        # Package defaults (copied to user on first run)
```

### **User Configuration**
```
~/Library/Application Support/zolo-zcli/  # macOS
~/.local/share/zolo-zcli/                 # Linux
%APPDATA%/zolo-zcli/                      # Windows
├── zConfigs/                            # Configuration files
│   ├── zConfig.machine.yaml            # Machine-specific settings
│   └── zConfig.zEnvironment.yaml       # Environment configuration
└── Data/                               # User data
    ├── Config/
    └── Cache/
```

### **Environment Variables**
```bash
# Environment selection
ZOLO_ENV=dev|prod|staging|lfs
ZOLO_DEPLOYMENT=Debug|Info|Production

# Logger configuration
ZOLO_LOGGER=DEBUG|INFO|WARNING|ERROR|CRITICAL

# Database credentials
ZOLO_DB_USERNAME=user
ZOLO_DB_PASSWORD=pass
ZOLO_DB_HOST=localhost

# API credentials
ZOLO_API_MASTER_KEY=key
ZOLO_JWT_SECRET=secret

# SSL certificates
ZOLO_SSL_CERT_PATH=/path/to/cert
ZOLO_SSL_KEY_PATH=/path/to/key
```

---

## 🎮 **Usage**

### **Initialization**
```python
from zCLI import zCLI

# zConfig initializes automatically as first subsystem
zcli = zCLI()

# Access configuration
config = zcli.config
```

### **Configuration Access**
```python
# Machine configuration
machine = config.get_machine()
browser = config.get_machine("browser")
hostname = config.get_machine("hostname")

# Environment configuration
env = config.get_environment()
deployment = config.get_environment("deployment")
```

### **Configuration Persistence**
```python
# Update machine configuration
config.persistence.persist_machine("browser", "Chrome")
config.persistence.persist_machine("ide", "cursor")

# Show current configuration
config.persistence.persist_machine(show=True)

# Reset to defaults
config.persistence.persist_machine("browser", reset=True)
```

---

## 🖥️ **Command Line Interface**

### **Configuration Commands**
```bash
# Set machine preferences
zolo config machine browser Chrome
zolo config machine ide cursor

# Show current configuration
zolo config machine --show

# Reset to auto-detected defaults
zolo config machine --reset browser

# Environment configuration
zolo config environment deployment Production
zolo config environment --show
```

### **Valid Configuration Keys**
```bash
# Machine (user-editable)
browser, ide, terminal, shell, cpu_cores, memory_gb

# Environment (user-editable)
deployment, role, datacenter, cluster, node_id
network.host, network.port, security.require_auth
logging.level, performance.max_workers
```

---

## 🔧 **API Reference**

### **Core Methods**

#### **Configuration Access**
```python
def get_machine(self, key=None, default=None):
    """Get machine configuration value."""
    
def get_environment(self, key=None, default=None):
    """Get environment configuration value."""
    
def create_logger(self, session_data):
    """Create logger instance with session data."""
```

#### **Configuration Persistence**
```python
def persist_machine(self, key=None, value=None, show=False, reset=False):
    """Persist machine configuration changes to disk."""
    
def persist_environment(self, key=None, value=None, show=False, reset=False):
    """Persist environment configuration changes to disk."""
```

---

## 🏗️ **Architecture Details**

### **Initialization Order**
1. **Path Resolution** - Initialize cross-platform paths
2. **Machine Config** - Load machine-specific settings with auto-detection
3. **Environment Config** - Load environment and deployment settings
4. **Session Config** - Create session with logger level hierarchy detection
5. **Logger Config** - Initialize logger using session's detected level
6. **zConfig Ready** - Display styled ready message

### **Configuration Hierarchy**
```
1. zSpark Object (runtime configuration)
2. Virtual Environment Variables (ZOLO_LOGGER when in venv)
3. System Environment Variables (ZOLO_LOGGER, ZOLO_DEPLOYMENT, etc.)
4. Environment Config File (zConfig.zEnvironment.yaml)
5. Default Values (fallback)
```

### **Dependencies**
- **None** - zConfig is a foundation subsystem
- **Provides** configuration services to all other subsystems
- **Uses** standard Python libraries (os, yaml, pathlib)

---

## 🎨 **Integration with zCLI**

### **Subsystem Integration**
```python
# All subsystems receive zConfig via zCLI instance
class zData:
    def __init__(self, zcli):
        self.config = zcli.config
        self.machine = zcli.config.get_machine()
```

### **Session Integration**
```python
# Machine config updates sync with session
if self.zcli and hasattr(self.zcli, 'session'):
    self.zcli.session["zMachine"][key] = value
```

---

## 🔍 **Debugging & Troubleshooting**

### **Common Issues**

#### **Configuration Not Loading**
- Check file permissions on config directories
- Verify YAML syntax in configuration files
- Ensure environment variables are set correctly

#### **Machine Config Not Persisting**
- Verify write permissions to user config directory
- Check for YAML syntax errors in zConfig.machine.yaml
- Ensure valid configuration keys are used

### **Debug Commands**
```bash
# Show current configuration
zolo config machine --show
zolo config environment --show
```

---

## 🚀 **Advanced Usage**

### **Programmatic Configuration Updates**
```python
# Update multiple settings
settings = {
    "browser": "Chrome",
    "ide": "cursor"
}

for key, value in settings.items():
    config.persistence.persist_machine(key, value)
```

---

## 📚 **Examples**

### **Basic Configuration Access**
```python
from zCLI import zCLI

# Initialize zCLI (zConfig initializes automatically)
zcli = zCLI()

# Access configuration
config = zcli.config

# Get machine information
hostname = config.get_machine("hostname")
browser = config.get_machine("browser")
os_type = config.get_machine("os")

# Get environment information
deployment = config.get_environment("deployment")
role = config.get_environment("role")
```

### **Configuration Persistence**
```python
# Update user preferences
config.persistence.persist_machine("browser", "Firefox")
config.persistence.persist_machine("ide", "vscode")

# Show current configuration
config.persistence.persist_machine(show=True)

# Reset browser to auto-detected default
config.persistence.persist_machine("browser", reset=True)
```

---

## 🎯 **Best Practices**

### **Configuration Management**
1. **Let auto-detection work** for system capabilities
2. **Override only when necessary** for user preferences
3. **Use valid keys** from the predefined list
4. **Test configuration changes** in development first

### **Configuration Persistence**
1. **Validate values** before persisting
2. **Handle errors gracefully** when persistence fails
3. **Use reset functionality** for troubleshooting

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **Configuration Templates** - Predefined configuration sets
- **Configuration Validation** - Schema-based validation
- **Configuration Migration** - Automatic configuration updates

---

## 📖 **Related Documentation**

- **[zSession Guide](zSession_GUIDE.md)** - Session management integration
- **[zComm Guide](zComm_GUIDE.md)** - Communication configuration

---

## 🏆 **Summary**

zConfig is the foundational configuration management subsystem that:

- **🎯 Provides** hierarchical configuration loading with zSpark → environment → config file priority
- **⚡ Establishes** the configuration foundation for all zCLI subsystems  
- **🏗️ Manages** machine-specific settings with cross-platform auto-detection
- **🔧 Integrates** session management with atomic logger initialization
- **📊 Supports** environment-specific configuration with deployment settings
- **🚀 Offers** configuration persistence with validation and error handling
- **📁 Organizes** all configuration files in a dedicated `zConfigs` folder
- **🔄 Automates** first-run setup with package defaults and machine detection
- **🎨 Provides** clean, professional output with styled ready messages

As the first subsystem in zCLI's initialization order, zConfig sets the stage for a robust, configurable, and maintainable CLI framework that adapts to any environment and user preferences with a clean, organized configuration structure and integrated session-logger architecture.

---

**Next in Initialization Order:** [zSession Guide](zSession_GUIDE.md) → [zComm Guide](zComm_GUIDE.md)
