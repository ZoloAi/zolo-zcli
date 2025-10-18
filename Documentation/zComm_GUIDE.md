# zComm: The Communication Subsystem

## **Overview**
- **zComm** is **zCLI**'s communication and service management subsystem
- Provides WebSocket server management, HTTP client functionality, service orchestration, and secure communication infrastructure
- Initializes in Layer 0 (foundation) alongside zConfig, establishing communication services for all other subsystems

## **Architecture**

### **Layer 0 Foundation**
**zComm** operates as a Layer 0 (foundation) subsystem, meaning it:
- Initializes early in the zCLI lifecycle (after zConfig)
- Provides communication services to the entire zCLI ecosystem
- Has minimal dependencies (only requires zConfig for configuration)
- Establishes the communication foundation for zCLI

### **Modular Design**
```
zComm/
├── zComm.py                           # Main communication manager
└── zComm_modules/
    ├── zBifrost/                      # WebSocket bridge module
    │   ├── bifrost_bridge.py          # Secure WebSocket server with authentication
    │   ├── zBifrost_Demo.html         # WebSocket demo interface
    │   └── zBifrost_Demo.js           # WebSocket demo client
    ├── service_manager.py             # Local service orchestration
    └── services/                      # Service definitions
        └── postgresql_service.py      # PostgreSQL service management
```

---

## **Core Features**

### **1. WebSocket Server Management**
- **zBifrost** - Secure WebSocket server with origin validation and authentication
- Auto-start in GUI mode, on-demand in terminal mode
- Real-time bidirectional communication for zWalker and external clients
- Built-in security with CSRF protection and API key authentication

### **2. HTTP Client Services**
- Pure HTTP communication without authentication logic
- Used by zAuth for remote authentication requests
- Configurable timeouts and error handling
- Clean separation of concerns (zComm handles transport, zAuth handles auth)

### **3. Service Management**
- Local service orchestration (PostgreSQL)
- Service lifecycle management (start, stop, restart, status)
- Connection information and health monitoring
- Cross-platform service management

### **4. Security & Authentication Integration**
- WebSocket authentication via API keys and zAuth integration
- Origin validation to prevent CSRF attacks
- Secure credential handling through zAuth subsystem
- Configurable security policies

---

## 📁 **Configuration**

### **WebSocket Configuration**
```yaml
# zConfig.websocket.yaml
websocket:
  host: "127.0.0.1"           # Bind address
  port: 56891                 # WebSocket port
  require_auth: true          # Enable authentication
  allowed_origins:            # CSRF protection
    - "http://localhost:3000"
    - "https://app.example.com"
```

### **Service Configuration**
```yaml
# zConfig.services.yaml
services:
  postgres:
    enabled: true
    port: 5432
    data_dir: "~/.zolo/data/postgres"
```

### **Environment Variables**
```bash
# WebSocket configuration
ZOLO_WS_HOST=127.0.0.1
ZOLO_WS_PORT=56891
ZOLO_WS_REQUIRE_AUTH=true

# Service management
ZOLO_SERVICES_ENABLED=postgres
ZOLO_POSTGRES_PORT=5432
```

---

## 🎮 **Usage**

### **Initialization**
```python
from zCLI import zCLI

# zComm initializes automatically in Layer 0
zcli = zCLI()

# Access communication services
comm = zcli.comm
```

### **WebSocket Management**
```python
# Create WebSocket server
websocket = comm.create_websocket()

# Start WebSocket server (async)
await comm.start_websocket(socket_ready, walker=walker)

# Broadcast message to all clients
await comm.broadcast_websocket(message, sender=sender)
```

### **HTTP Communication**
```python
# Make HTTP POST request (used by zAuth)
response = comm.http_post("http://api.example.com/auth", {
    "username": "user",
    "password": "pass"
})

if response:
    data = response.json()
```

### **Service Management**
```python
# Start a service
result = comm.start_service("postgres", port=5432)

# Check service status
status = comm.service_status("postgres")

# Stop a service
comm.stop_service("postgres")

# Get connection info
info = comm.get_service_connection_info("postgres")
```

---

## 🖥️ **Command Line Interface**

### **Available Commands**
```bash
# Test suite
zolo test

# Shell mode (default)
zolo shell

# Configuration management
zolo config
```

---

## 🔧 **API Reference**

### **Core Methods**

#### **WebSocket Management**
```python
def create_websocket(self, walker=None, port=None, host=None):
    """Create WebSocket server instance using zCLI configuration."""
    
async def start_websocket(self, socket_ready, walker=None):
    """Start WebSocket server."""
    
async def broadcast_websocket(self, message, sender=None):
    """Broadcast message to all WebSocket clients."""
```

#### **HTTP Communication**
```python
def http_post(self, url, data=None, timeout=10):
    """Make HTTP POST request - pure communication, no auth logic."""
```

#### **Service Management**
```python
def start_service(self, service_name, **kwargs):
    """Start a local service."""
    
def stop_service(self, service_name):
    """Stop a running service."""
    
def restart_service(self, service_name):
    """Restart a service."""
    
def service_status(self, service_name=None):
    """Get service status."""
    
def get_service_connection_info(self, service_name):
    """Get connection information for a service."""
```

#### **Utility Methods**
```python
def check_port(self, port):
    """Check if a port is available."""
```

---

## 🏗️ **Architecture Details**

### **Initialization Order**
1. **zConfig** - Load configuration and establish foundation
2. **zComm** - Initialize communication services
3. **zDisplay** - Initialize display subsystem
4. **zAuth** - Initialize authentication (uses zComm for HTTP)
5. **Other subsystems** - Initialize with communication services available

### **WebSocket Security Model**
```
Client Connection → Origin Validation → Authentication → Message Processing
     ↓                    ↓                    ↓              ↓
  CSRF Check         API Key Check      zAuth Integration   zDispatch
```

### **Service Integration**
```
zComm → ServiceManager → Service Definitions → Local Services
  ↓           ↓                ↓                    ↓
Config    Lifecycle        PostgreSQL         Data Storage
         Management
```

### **Dependencies**
- **Requires:** zConfig (for configuration)
- **Provides:** Communication services to all subsystems
- **Integrates with:** zAuth (for authentication), zDisplay (for status messages)

---

## 🎨 **Integration with zCLI**

### **Subsystem Integration**
```python
# zAuth uses zComm for HTTP requests
class zAuth:
    def __init__(self, zcli):
        self.zcli = zcli
        # zComm provides HTTP client services
    
    def authenticate_remote(self, username, password):
        # Use zComm for pure HTTP communication
        response = self.zcli.comm.http_post(url, data)
```

### **WebSocket Integration**
```python
# zWalker uses zComm WebSocket for real-time communication
class zWalker:
    def __init__(self, zcli):
        self.zcli = zcli
        # WebSocket server managed by zComm
```

### **Service Integration**
```python
# zData uses zComm services for database connections
class zData:
    def __init__(self, zcli):
        self.zcli = zcli
        # PostgreSQL service managed by zComm
```

---

## 🔍 **Debugging & Troubleshooting**

### **Common Issues**

#### **WebSocket Server Won't Start**
- Check if port is already in use: `comm.check_port(56891)`
- Verify WebSocket configuration in zConfig
- Check firewall settings for port access

#### **Service Management Issues**
- Verify service definitions exist in `zComm_modules/services/`
- Check service configuration and dependencies
- Review service logs for error details

#### **HTTP Communication Failures**
- Verify network connectivity and URL accessibility
- Check timeout settings for slow networks
- Review zAuth integration for authentication issues

### **Debug Commands**
```bash
# Run test suite for diagnostics
zolo test

# Check port availability programmatically
comm.check_port(56891)
```

---

## 🚀 **Advanced Usage**

### **Custom WebSocket Handlers**
```python
# Extend zBifrost for custom message handling
class CustomBifrost(zBifrost):
    async def handle_custom_message(self, ws, message):
        # Custom message processing
        pass
```

### **Service Plugin Development**
```python
# Create custom service definitions
class CustomService:
    def start(self, **kwargs):
        # Custom service startup logic
        pass
    
    def stop(self):
        # Custom service shutdown logic
        pass
```

### **WebSocket Client Integration**
```javascript
// Connect to zBifrost WebSocket
const ws = new WebSocket('ws://localhost:56891?token=api_key_12345');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle zCLI messages
};
```

---

## 📚 **Examples**

### **Basic WebSocket Server**
```python
from zCLI import zCLI
import asyncio

# Initialize zCLI
zcli = zCLI()

# Create and start WebSocket server
async def start_server():
    socket_ready = asyncio.Event()
    await zcli.comm.start_websocket(socket_ready)
    await socket_ready.wait()
    print("WebSocket server ready!")

asyncio.run(start_server())
```

### **HTTP API Integration**
```python
# zAuth using zComm for remote authentication
def authenticate_user(username, password):
    response = zcli.comm.http_post(
        "http://api.example.com/auth",
        {"username": username, "password": password}
    )
    
    if response and response.status_code == 200:
        return response.json()
    return None
```

### **Service Management**
```python
# Start PostgreSQL service
result = zcli.comm.start_service("postgres", port=5432)
if result:
    print("PostgreSQL started successfully")
    
    # Get connection info
    info = zcli.comm.get_service_connection_info("postgres")
    print(f"Connect to: {info['host']}:{info['port']}")
```

---

## 🎯 **Best Practices**

### **WebSocket Management**
1. **Use authentication** for production WebSocket servers
2. **Configure allowed origins** to prevent CSRF attacks
3. **Handle connection errors** gracefully
4. **Monitor WebSocket connections** for resource management

### **HTTP Communication**
1. **Use zComm for transport only** - keep auth logic in zAuth
2. **Set appropriate timeouts** for network requests
3. **Handle connection failures** with proper error messages
4. **Validate responses** before processing

### **Service Management**
1. **Check service status** before operations
2. **Handle service failures** gracefully
3. **Use connection info** for database connections
4. **Monitor service health** in production

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **WebSocket Clustering** - Multi-instance WebSocket coordination
- **Service Discovery** - Automatic service detection and registration
- **Load Balancing** - HTTP request distribution across multiple endpoints
- **Message Queuing** - Reliable message delivery with persistence

---

## 📖 **Related Documentation**

- **[zAuth Guide](zAuth_GUIDE.md)** - Authentication integration with zComm
- **[zConfig Guide](zConfig_GUIDE.md)** - Configuration management
- **[zDisplay Guide](zDisplay_GUIDE.md)** - Display integration

---

## 🏆 **Summary**

zComm is the communication and service management subsystem that:

- **🌐 Provides** WebSocket server management with zBifrost security and authentication
- **⚡ Establishes** the communication foundation for all zCLI subsystems
- **🔧 Manages** local services with lifecycle control and health monitoring
- **🔒 Integrates** with zAuth for secure authentication and credential handling
- **📡 Supports** HTTP client services for external API communication
- **🛡️ Implements** security features including origin validation and CSRF protection
- **🎯 Offers** clean separation of concerns between transport and authentication
- **📊 Provides** service orchestration with PostgreSQL and custom services
- **🔄 Automates** WebSocket server lifecycle with GUI/terminal mode detection
- **🎨 Delivers** professional communication infrastructure with comprehensive error handling

As a Layer 0 foundation subsystem, zComm provides essential communication services that enable zCLI's real-time capabilities, service management, and secure external integrations. It works seamlessly with zAuth for authentication while maintaining clean architectural boundaries, ensuring zCLI operates as both a standalone CLI tool and a communication hub for distributed applications.

---

**Initialization Order:** [zConfig Guide](zConfig_GUIDE.md) → **zComm Guide** → [zAuth Guide](zAuth_GUIDE.md)
