# zBifrost Client (JavaScript)

Production-ready JavaScript WebSocket client for zCLI's zBifrost bridge.

## Structure

```
client/
├── src/                       # Source files
│   ├── bifrost_client.js      # Main BifrostClient class
│   ├── core/                  # Core modules (connection, hooks, logger, message_handler)
│   ├── rendering/             # Rendering modules (renderer, theme_loader)
│   └── api/                   # API wrappers (CRUD, zCLI operations)
└── README.md                  # This file
```

## Usage

### Swiper-Style Elegance (Recommended)

```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@main/zCLI/subsystems/zComm/zComm_modules/bifrost/client/src/bifrost_client.js"></script>

<div id="zVaF"></div> <!-- Default zCLI container (zView and Function) -->

<script>
  // One declaration, everything happens automatically!
  const client = new BifrostClient('ws://localhost:8765', {
    autoConnect: true,              // Auto-connect on instantiation
    zTheme: true,                   // Enable zTheme CSS & rendering
    // targetElement: 'zVaF',       // Optional: default is 'zVaF'
    autoRequest: 'my_event',        // Auto-send on connect
    onConnected: (info) => console.log('✅ Connected!', info)
  });
</script>
```

### Traditional (More Control)

```html
<script>
  const client = new BifrostClient('ws://localhost:8765', {
    zTheme: true,
    hooks: {
      onConnected: (info) => console.log('Connected!', info),
      onDisconnected: (reason) => console.log('Disconnected:', reason),
      onMessage: (msg) => console.log('Message:', msg),
      onError: (error) => console.error('Error:', error)
    }
  });
  
  await client.connect();
  client.send({event: 'my_event'});
</script>
```

### Local Development

```html
<script src="../../../../zCLI/subsystems/zComm/zComm_modules/bifrost/client/src/bifrost_client.js"></script>
```

## Features

- **Swiper-Style Elegance**: `autoConnect`, `zTheme`, `autoRequest` for one-line initialization
- **Lazy Loading**: Modules load dynamically only when needed
- **Auto-Reconnect**: Automatic reconnection with exponential backoff
- **zTheme Integration**: Optional CSS loading & automatic rendering
- **Hooks System**: Lifecycle callbacks (onConnected, onDisconnected, onMessage, etc.)
- **CRUD Operations**: `create()`, `read()`, `update()`, `delete()` methods
- **Auto-Rendering**: `renderTable()`, `renderForm()`, `renderMenu()` helpers
- **zCLI Integration**: `zFunc()`, `zLink()`, `zOpen()` for backend commands

## Documentation

See [`../docs/`](../docs/) for:
- `ARCHITECTURE.md` - Client architecture & design
- `MESSAGE_PROTOCOL.md` - WebSocket message format
- `HOOKS_GUIDE.md` - Hooks system reference
- `CRUD_API.md` - CRUD operations API reference

## Demos

See [`../../../../Demos/Layer_0/zBifrost_Demo/`](../../../../Demos/Layer_0/zBifrost_Demo/) for progressive tutorials:
- Level 0: Hello zBlog (basic connection)
- Level 1: Echo Test (two-way communication)
- Level 2: Post Feed (structured data)
- Level 4a+: Multi-zone layout with zDisplay events

