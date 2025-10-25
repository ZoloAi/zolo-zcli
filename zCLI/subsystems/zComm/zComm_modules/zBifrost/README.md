# zBifrost - WebSocket Bridge for zCLI

## Overview

zBifrost provides real-time WebSocket communication between zCLI backends and web frontends, enabling dual-mode applications (CLI + Web) with zero configuration.
The bridge now mirrors zDisplay's event-driven contract. All messages flow
through a single handler that routes by `event` into dedicated domain packages
(`client`, `cache`, `discovery`, `dispatch`). This alignment removes duplicated
conditional logic and makes future extensions significantly easier to reason
about.

---

## Directory Structure

```
zBifrost/
├── README.md                      # This file
├── HOOKS_GUIDE.md                 # Comprehensive hooks documentation
├── MESSAGE_PROTOCOL.md            # Canonical WebSocket event contracts (NEW)
├── MIGRATION_GUIDE.md             # Legacy action → event migration steps (NEW)
├── __init__.py                    # Python package export
├── bifrost_bridge_modular.py      # Event-driven WebSocket bridge (default)
├── bifrost_bridge.py              # Legacy bridge (deprecated shim)
├── bifrost_client.js              # Production client (monolithic, v1.5.4)
├── bifrost_client_modular.js      # Modular client (ES module)
│
├── bridge_modules/                # Server-side modular components
│   ├── __init__.py
│   ├── authentication.py          # Origin + token validation
│   ├── cache_manager.py           # Schema & query cache orchestration
│   ├── connection_info.py         # Server metadata snapshots
│   ├── message_handler.py         # Dispatch + compatibility helpers
│   └── events/                    # Event-domain routers (NEW)
│       ├── __init__.py
│       ├── client_events.py
│       ├── cache_events.py
│       ├── discovery_events.py
│       └── dispatch_events.py
│
├── _modules/                      # Client-side modular bundle
│   ├── connection.js
│   ├── message_handler.js
│   ├── renderer.js
│   ├── theme_loader.js
│   ├── logger.js
│   └── hooks.js
│
└── _deprecated/                   # Legacy demo files
    ├── zBifrost_Demo.html
    └── zBifrost_Demo.js
```

---

## Files

### Production Files

#### `bifrost_client.js` (Current Production)
- **Status**: ✅ Production Ready (v1.5.4)
- **Type**: Monolithic (single file, 816 lines)
- **Use**: Import directly in HTML
- **CDN**: `https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client.js`

#### `bifrost_client_modular.js` (New Modular)
- **Status**: ✅ Production Ready (v1.5.4+)
- **Type**: Modular (uses `_modules/`)
- **Use**: Import as ES6 module
- **Benefits**: Better maintainability, tree-shaking

#### `bifrost_bridge_modular.py` (Server-Side Default)
- **Status**: ✅ Production Ready (event-driven)
- **Type**: Python WebSocket server with modular event packages
- **Use**: Loaded automatically via `zCLI.subsystems.zComm`
- **Highlights**: Central event map, shared handlers, backward-compatible fallbacks

#### `bifrost_bridge.py` (Legacy)
- **Status**: ⚠️ Deprecated (kept for transition)
- **Type**: Legacy monolithic bridge
- **Use**: Emits `DeprecationWarning`; migrate imports to `bifrost_bridge_modular`

### Documentation

#### `HOOKS_GUIDE.md`
Comprehensive guide to customizing BifrostClient behavior:
- All available hooks explained
- Usage patterns and examples
- Custom rendering without zTheme
- Best practices

#### `MESSAGE_PROTOCOL.md`
Authoritative reference for the standardized `event` field and handler payloads
shared between zDisplay and zBifrost.

#### `MIGRATION_GUIDE.md`
Step-by-step instructions for upgrading legacy integrations that relied on the
`action` field or the monolithic bridge.

### Deprecated

#### `_deprecated/zBifrost_Demo.*`
- Legacy demo files from v1.5.3
- Kept for reference only
- **Do not use in new projects**

---

## Quick Start

### Option 1: Monolithic Client (Easiest)

```html
<!-- Load from CDN -->
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client.js"></script>

<script>
  const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true,
    hooks: {
      onConnected: () => console.log('Connected!')
    }
  });
  
  await client.connect();
</script>
```

### Option 2: Modular Client (Best for Large Projects)

```html
<script type="module">
  import { BifrostClient } from './bifrost_client_modular.js';
  
  const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true
  });
  
  await client.connect();
</script>
```

### Option 3: Without zTheme (Custom Styling)

```javascript
const client = new BifrostClient('ws://localhost:8765', {
  autoTheme: false,  // 🚫 Don't load zTheme CSS
  hooks: {
    onDisplay: (data) => {
      // Your custom rendering logic
      if (Array.isArray(data)) {
        myCustomTableRenderer(data);
      }
    }
  }
});
```

---

## Features

### ✅ WebSocket Management
- Auto-connect with exponential backoff
- Connection state tracking
- Automatic reconnection
- Request/response correlation

### ✅ Primitive Hooks System
- `onConnected`, `onDisconnected`
- `onMessage`, `onError`, `onBroadcast`
- `onDisplay`, `onInput`
- Runtime hook registration

### ✅ CRUD Operations
- `create(model, data)`
- `read(model, filters, options)`
- `update(model, filters, data)`
- `delete(model, filters)`

### ✅ zCLI Integration
- `zFunc(command)` - Execute functions
- `zLink(path)` - Navigate menus
- `zOpen(command)` - Open resources

### ✅ Auto-Rendering (Optional)
- `renderTable(data, container)` - Tables with zTheme
- `renderForm(fields, container, onSubmit)` - Forms
- `renderMenu(items, container)` - Button menus
- `renderMessage(text, type, container)` - Alerts

### ✅ zTheme Integration (Optional)
- Auto-load zTheme CSS
- Graceful fallback if CSS fails
- Can be disabled (`autoTheme: false`)

---

## Architecture

### Modular Components (`_modules/`)

Each module handles a specific concern:

1. **connection.js**: WebSocket lifecycle
2. **message_handler.js**: Message parsing & correlation
3. **renderer.js**: DOM rendering with zTheme
4. **theme_loader.js**: Dynamic CSS loading
5. **logger.js**: Debug logging
6. **hooks.js**: Event hook management

### Benefits of Modular Architecture

- **Maintainability**: Each module is < 200 lines
- **Testability**: Modules can be tested independently
- **Tree-Shaking**: Import only what you need
- **Extensibility**: Easy to add new modules

---

## Configuration Options

```javascript
new BifrostClient(url, {
  // Theme
  autoTheme: true,           // Auto-load zTheme CSS
  
  // Connection
  autoReconnect: true,       // Auto-reconnect on disconnect
  reconnectDelay: 3000,      // Delay between reconnects (ms)
  timeout: 30000,            // Request timeout (ms)
  
  // Authentication
  token: 'your-api-key',     // Authentication token
  
  // Debugging
  debug: false,              // Enable console logging
  
  // Hooks
  hooks: {
    onConnected: (info) => {},
    onDisconnected: (reason) => {},
    onMessage: (msg) => {},
    onError: (error) => {},
    onBroadcast: (msg) => {},
    onDisplay: (data) => {},
    onInput: (request) => {}
  }
});
```

---

## Examples

### Example 1: Basic Usage with zTheme

```javascript
const client = new BifrostClient('ws://localhost:8765', {
  autoTheme: true
});

await client.connect();
const users = await client.read('users');
client.renderTable(users, '#app');
```

### Example 2: Custom Rendering (No zTheme)

```javascript
const client = new BifrostClient('ws://localhost:8765', {
  autoTheme: false,
  hooks: {
    onDisplay: (data) => {
      // Use React, Vue, or vanilla JS
      ReactDOM.render(<MyTable data={data} />, container);
    }
  }
});
```

### Example 3: Real-Time Updates

```javascript
const client = new BifrostClient('ws://localhost:8765', {
  hooks: {
    onBroadcast: (msg) => {
      if (msg.type === 'user_joined') {
        addUserToList(msg.user);
      }
    }
  }
});
```

---

## Demos

### User Manager v2
**Location**: `Demos/User Manager/index_v2.html`

Full-featured CRUD application demonstrating:
- ✅ BifrostClient with zTheme
- ✅ All CRUD operations
- ✅ Primitive hooks
- ✅ Auto-rendering methods
- ✅ 62% less code than v1

**Run it**:
```bash
cd Demos/User\ Manager
python run_backend.py
# Open index_v2.html in browser
```

---

## Migration Guide

### From zBifrost_Demo.js → bifrost_client.js

**Old**:
```javascript
const client = new zBifrost(url, token, { debug: true });
await client.connect();
const result = await client.send({ zKey: 'command' });
```

**New**:
```javascript
const client = new BifrostClient(url, { 
  token, 
  debug: true 
});
await client.connect();
const result = await client.send({ zKey: 'command' });
```

**Changes**:
- Constructor now takes options object
- Added primitive hooks system
- Added auto-rendering methods
- Added zTheme integration

---

## Testing

```bash
# Run backend
python run_backend.py

# Open test page
open Demos/User\ Manager/index_v2.html

# Check console for debug logs
# Enable with: { debug: true }
```

---

## Performance

- **Connection**: < 100ms to establish
- **Message**: < 10ms round-trip
- **Rendering**: < 50ms for 1000 rows
- **Memory**: ~2MB for client library
- **Bundle Size**: 26KB (minified), 8KB (gzipped)

---

## Browser Compatibility

- ✅ Chrome/Edge 88+
- ✅ Firefox 78+
- ✅ Safari 14+
- ✅ All browsers with WebSocket and ES6 support

---

## Contributing

When adding features:
1. Add module to `_modules/` if appropriate
2. Update `bifrost_client_modular.js` to use it
3. Add tests for the module
4. Update this README
5. Update HOOKS_GUIDE.md if adding hooks

---

## See Also

- [HOOKS_GUIDE.md](./HOOKS_GUIDE.md) - Complete hooks documentation
- [zComm Guide](../../../../../../Documentation/zComm_GUIDE.md) - Communication subsystem
- [Release Notes](../../../../../../Documentation/Release/RELEASE_1.5.4.md) - What's new in v1.5.4

---

**Version**: 1.5.4  
**License**: MIT  
**Author**: Gal Nachshon

