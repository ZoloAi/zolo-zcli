# zConfig: <br> The Settings Subsystem

## **Overview**
- **zConfig** is **zCLI**'s foundational, machine-specific, settings management subsystem. It provides auto cross-platform configuration loading, , environment management, and `zSession` persistence.
> **Note:** As the first subsystem initialized in **zCLI**, <u>it establishes the configuration foundation for all other subsystems</u>.

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
    ├── config_loader.py         # Hierarchical configuration loading
    └── machine_config.py        # Machine-specific configuration
```
---

## **Core Features**

### **1. Hierarchical Configuration Loading**
- **Package Defaults** → **Environment-Specific** → **User Overrides**
- Automatic environment detection (dev, prod, staging, lfs)
- Cross-platform path resolution
- YAML-based configuration files

### **2. Machine Configuration Management**
- Auto-detection of system capabilities (OS, architecture, tools)
- User preference management (browser, IDE, terminal)
- Deployment environment settings
- Persistent machine.yaml configuration

### **3. Configuration Persistence**
- **NEW:** Integrated configuration persistence (formerly zExport)
- Runtime configuration updates with disk persistence
- Validation and error handling
- Reset to auto-detected defaults

### **4. Secret Management**
- Environment variable-based secret loading
- Secure credential handling
- Database, API, and service credentials
- SSL certificate path management

---

## 📁 **Configuration Files**

### **Package Configuration**
```
config/
├── zConfig.default.yaml         # Package defaults
├── zConfig.dev.yaml            # Development environment
├── zConfig.prod.yaml           # Production environment
├── zConfig.kernel.yaml         # Kernel-specific settings
└── zConfig.machine.yaml        # Machine-specific defaults
```

### **User Configuration**
```
~/.config/zolo-zcli/
├── machine.yaml                # User machine preferences
└── config.yaml                 # User application settings (future)
```

### **Environment Variables**
```bash
# Environment selection
ZOLO_ENV=dev|prod|staging|lfs

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
from zCLI.zCLI import zCLI

# zConfig initializes automatically as first subsystem
zcli = zCLI({'zSpark': {}, 'plugins': []})

# Access configuration
config = zcli.config
```

### **Configuration Access**
```python
# Get configuration values
value = config.get("logging.level")
section = config.get_section("database")
all_config = config.get_all()

# Machine configuration
machine = config.get_machine()
browser = config.get_machine("browser")
hostname = config.get_machine("hostname")
```

### **Configuration Persistence**
```python
# Update machine configuration
config.persist_machine("browser", "Chrome")
config.persist_machine("ide", "cursor")
config.persist_machine("deployment", "prod")

# Show current configuration
config.persist_machine(show=True)

# Reset to defaults
config.persist_machine("browser", reset=True)
```

### **Secret Access**
```python
# Get secrets
db_user = config.get_secret("db_username")
api_key = config.get_secret("api_master_key")

# Check secret availability
has_ssl = config.has_secret("ssl_cert_path")
```

---

## 🖥️ **Command Line Interface**

### **Configuration Persistence Commands**
```bash
# Set machine preferences
config machine browser Chrome
config machine ide cursor
config machine deployment prod
config machine role development

# Show current configuration
config machine --show

# Reset to auto-detected defaults
config machine --reset browser
config machine --reset ide

# Future: Application configuration
config config logging.level debug
config config cache.max_size 1000
```

### **Valid Machine Configuration Keys**
```bash
# Identity (auto-detected, user-overridable)
os, hostname, architecture, python_version

# Deployment (user-configurable)
deployment: dev|prod|staging|lfs
role: development|production|testing|staging

# Tool Preferences (user-configurable)
browser, ide, terminal, shell

# System Capabilities (auto-detected, user-overridable)
cpu_cores, memory_gb
```

---

## 🔧 **API Reference**

### **Core Methods**

#### **Configuration Access**
```python
def get(self, path, default=None):
    """Get configuration value by dot-notation path."""
    
def get_section(self, section):
    """Get entire configuration section."""
    
def get_all(self):
    """Get complete configuration."""
    
def get_machine(self, key=None, default=None):
    """Get machine configuration value."""
```

#### **Configuration Persistence**
```python
def persist_machine(self, key=None, value=None, show=False, reset=False):
    """Persist machine configuration changes to disk."""
    
def persist_config(self, key=None, value=None, show=False):
    """Persist application configuration changes to disk."""
```

#### **Secret Management**
```python
def get_secret(self, key, default=None):
    """Get secret value from environment variables."""
    
def has_secret(self, key):
    """Check if secret is available."""
```

#### **Utility Methods**
```python
def get_environment(self):
    """Get current environment name."""
    
def get_paths_info(self):
    """Get path information for debugging."""
    
def get_config_sources(self):
    """Get list of config sources that were loaded."""
    
def print_info(self):
    """Print configuration information for debugging."""
```

---

## 🏗️ **Architecture Details**

### **Initialization Order**
1. **Path Resolution** - Initialize cross-platform paths
2. **Machine Config** - Load machine-specific settings
3. **Environment Detection** - Determine deployment environment
4. **Config Loading** - Load hierarchical configuration
5. **Secret Loading** - Load environment-based secrets
6. **Display Setup** - Prepare for zCLI integration

### **Configuration Hierarchy**
```
1. Package Defaults (zConfig.default.yaml)
2. Environment Defaults (zConfig.dev.yaml)
3. Machine Defaults (zConfig.machine.yaml)
4. User Machine Config (~/.config/zolo-zcli/machine.yaml)
5. Environment Variables (ZOLO_*)
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
        self.secrets = zcli.config.get_secret("db_password")
```

### **Display Integration**
```python
# Configuration persistence uses zDisplay when available
if self.zcli and self.zcli.display:
    self.zcli.display.handle({
        "event": "success",
        "message": f"Updated machine config: {key}",
        "details": f"{current_value} → {value}"
    })
```

### **Session Integration**
```python
# Machine config updates sync with session
if self.zcli and hasattr(self.zcli, 'session'):
    self.zcli.session["zMachine"][key] = value
```

---

## 🔍 **Debugging & Troubleshooting**

### **Configuration Information**
```python
# Print complete configuration info
config.print_info()

# Get debug information
env = config.get_environment()
paths = config.get_paths_info()
sources = config.get_config_sources()
```

### **Common Issues**

#### **Configuration Not Loading**
- Check file permissions on config directories
- Verify YAML syntax in configuration files
- Ensure environment variables are set correctly

#### **Machine Config Not Persisting**
- Verify write permissions to user config directory
- Check for YAML syntax errors in machine.yaml
- Ensure valid configuration keys are used

#### **Secrets Not Available**
- Verify environment variables are set
- Check variable naming (ZOLO_* prefix required)
- Ensure environment variables are exported

### **Debug Commands**
```bash
# Show current configuration
config machine --show

# Check configuration sources
config check

# Validate configuration
config validate

# Show debug information
config info
```

---

## 🚀 **Advanced Usage**

### **Custom Configuration Loading**
```python
# Load configuration for specific environment
config = zConfig(environment="staging")

# Access with custom defaults
value = config.get("custom.setting", default="fallback")
```

### **Programmatic Configuration Updates**
```python
# Update multiple settings
settings = {
    "browser": "Chrome",
    "ide": "cursor", 
    "deployment": "prod"
}

for key, value in settings.items():
    config.persist_machine(key, value)
```

### **Configuration Validation**
```python
# Validate configuration values
validation = config._validate_machine_value("deployment", "prod")
if not validation["valid"]:
    print(f"Error: {validation['error']}")
```

---

## 📚 **Examples**

### **Basic Configuration Access**
```python
from zCLI.zCLI import zCLI

# Initialize zCLI (zConfig initializes automatically)
zcli = zCLI({'zSpark': {}, 'plugins': []})

# Access configuration
config = zcli.config

# Get application settings
log_level = config.get("logging.level", "INFO")
db_host = config.get("database.host", "localhost")

# Get machine information
hostname = config.get_machine("hostname")
browser = config.get_machine("browser")
os_type = config.get_machine("os")
```

### **Configuration Persistence**
```python
# Update user preferences
config.persist_machine("browser", "Firefox")
config.persist_machine("ide", "vscode")

# Show current configuration
config.persist_machine(show=True)

# Reset browser to auto-detected default
config.persist_machine("browser", reset=True)
```

### **Secret Management**
```python
# Database connection
db_user = config.get_secret("db_username")
db_pass = config.get_secret("db_password")
db_host = config.get_secret("db_host", "localhost")

# API authentication
api_key = config.get_secret("api_master_key")
if api_key:
    # Use API key for authentication
    pass
```

### **Environment-Specific Configuration**
```python
# Check current environment
env = config.get_environment()
print(f"Running in {env} environment")

# Get environment-specific settings
if env == "prod":
    debug_mode = False
    log_level = "WARNING"
else:
    debug_mode = True
    log_level = "DEBUG"
```

---

## 🎯 **Best Practices**

### **Configuration Management**
1. **Use dot notation** for nested configuration access
2. **Provide defaults** for optional configuration values
3. **Validate configuration** before applying changes
4. **Use environment variables** for sensitive data

### **Machine Configuration**
1. **Let auto-detection work** for system capabilities
2. **Override only when necessary** for user preferences
3. **Use valid keys** from the predefined list
4. **Test configuration changes** in development first

### **Secret Management**
1. **Never hardcode secrets** in configuration files
2. **Use environment variables** for all sensitive data
3. **Check secret availability** before using
4. **Use secure storage** for production secrets

### **Configuration Persistence**
1. **Validate values** before persisting
2. **Handle errors gracefully** when persistence fails
3. **Provide user feedback** on configuration changes
4. **Use reset functionality** for troubleshooting

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **Config.yaml Persistence** - User application configuration
- **Configuration Templates** - Predefined configuration sets
- **Remote Configuration** - Cloud-based configuration management
- **Configuration Encryption** - Encrypted sensitive configuration
- **Configuration Validation** - Schema-based validation
- **Configuration Migration** - Automatic configuration updates

### **Integration Plans**
- **zDisplay Integration** - Enhanced configuration display
- **zDialog Integration** - Interactive configuration setup
- **zData Integration** - Configuration-driven data connections
- **zAuth Integration** - Configuration-based authentication

---

## 📖 **Related Documentation**

- **[zSession Guide](zSession_GUIDE.md)** - Session management integration
- **[zComm Guide](zComm_GUIDE.md)** - Communication configuration
- **[zData Guide](zData_GUIDE.md)** - Data configuration integration
- **[zAuth Guide](zAuth_GUIDE.md)** - Authentication configuration

---

## 🏆 **Summary**

zConfig is the foundational configuration management subsystem that:

- **🎯 Provides** hierarchical configuration loading and management
- **⚡ Establishes** the configuration foundation for all zCLI subsystems  
- **🏗️ Manages** machine-specific settings and user preferences
- **🔧 Offers** configuration persistence with validation and error handling
- **🔐 Handles** secure secret management via environment variables
- **🚀 Supports** cross-platform configuration with automatic environment detection

As the first subsystem in zCLI's initialization order, zConfig sets the stage for a robust, configurable, and maintainable CLI framework that adapts to any environment and user preferences.

---

**Next in Initialization Order:** [zSession Guide](zSession_GUIDE.md) → [zComm Guide](zComm_GUIDE.md)
