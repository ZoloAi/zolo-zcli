# zCLI Agent Reference

## 3 Steps - Always

1. Import zCLI
2. Create zSpark
3. RUN walker

```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"  # OR "zBifrost"
})

z.walker.run()
```

**Note:** All zCLI sparks work identically for Terminal and zBifrost. Always use a Terminal spark for terminal feedback. If in zBifrost mode, create a separate Terminal test spark.

## Code Rules

- NO needless prints or verboseness
- Keep code slim
- If output needed: use `z.display` or `z.logger` ONLY

## zBifrost Level 0

**Backend**:
```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"host": "127.0.0.1", "port": 8765, "require_auth": False}
})

z.walker.run()
```

**Frontend**:
```html
<script type="module">
class SimpleBifrostClient {
    constructor(url, options) {
        this.url = url;
        this.ws = null;
        this.hooks = options.hooks || {};
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            this.ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.event === 'connection_info' && this.hooks.onConnected) {
                    this.hooks.onConnected(msg.data);
                }
            };
            this.ws.onopen = () => resolve();
            this.ws.onerror = (e) => reject(e);
        });
    }
    
    disconnect() { this.ws?.close(); }
    isConnected() { return this.ws?.readyState === WebSocket.OPEN; }
}

const client = new SimpleBifrostClient('ws://localhost:8765', {
    hooks: { onConnected: (info) => console.log(info) }
});
await client.connect();
</script>
```

**Result**: Server on 8765. Client connects, `onConnected` hook fires with server info.

## Production BifrostClient (v1.5.5+)

**Architecture**: Lazy loading - modules load dynamically only when needed

**Why**: Solves ES6 CDN issues while staying modular at runtime

**Usage via CDN**:
```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client_modular.js"></script>
<script>
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // true loads zTheme CSS automatically
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onMessage: (msg) => console.log('Message:', msg)
    }
});

await client.connect();  // Modules load here dynamically

// CRUD operations
const users = await client.read('users');
await client.create('users', {name: 'John', email: 'j@e.com'});

// Or dispatch zUI commands
const result = await client.send({event: 'dispatch', zKey: '^Ping'});
</script>
```

**Key features**:
- Works via CDN (no import resolution issues)
- Lazy loads: connection, message_handler, renderer, theme_loader
- Full CRUD API: `create()`, `read()`, `update()`, `delete()`
- zCLI operations: `zFunc()`, `zLink()`, `zOpen()`
- Auto-rendering: `renderTable()`, `renderMenu()`, `renderForm()`

