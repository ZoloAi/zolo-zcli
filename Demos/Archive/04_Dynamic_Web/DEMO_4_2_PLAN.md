# Demo 4.2 - Dual-Mode zUI via zBifrost

## Architecture (Correct Approach)

### NOT This (What I was doing wrong):
```
❌ PageRenderer manually parses YAML → HTML
❌ "Web mode" that doesn't exist
❌ Server-side rendering of zUI
```

### YES This (The zKernel Way):
```
✅ zBifrost Client (JS) + WebSocket
✅ Server executes zUI in "zBifrost" mode
✅ zDisplay → JSON → WebSocket → Client renders
```

## Flow

1. **HTTP Request**: `GET /dashboard`
2. **zServer**: Serves HTML with zBifrost client embedded
3. **zBifrost Client**: Connects to WebSocket server (port 56891)
4. **Client Sends**: `{event: "execute_ui", zVaFile: "zUI_web_dashboard", zBlock: "zVaF"}`
5. **Server Executes**: `zWalker.run()` with `session['zMode'] = "zBifrost"`
6. **zDisplay Events**: Fire → JSON via `send_gui_event()`
7. **WebSocket**: Broadcasts JSON to client
8. **Client Renders**: `onDisplay` hook converts JSON → HTML

## Components Needed

### 1. Dynamic Route Handler (EXISTS)
- ✅ `handler.py` - Dynamic route handling
- ✅ `router.py` - Route matching + RBAC
- ✅ `zServer_routes.yaml` - Route definitions

### 2. HTML Template with zBifrost Client (NEW)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <script src="/bifrost_client_modular.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        const client = new BifrostClient('ws://localhost:56891', {
            autoTheme: true,
            hooks: {
                onDisplay: (data) => {
                    // Render zDisplay JSON events as HTML
                    renderDisplayEvent(data);
                }
            }
        });
        
        await client.connect();
        
        // Ask server to execute zUI
        await client.zFunc(`execute_ui zUI_web_dashboard zVaF`);
    </script>
</body>
</html>
```

### 3. WebSocket Server (EXISTS!)
- ✅ `zBifrost` subsystem in zComm
- ✅ Already handles `broadcast_websocket()`
- ✅ Already integrated with zDisplay

### 4. Bifrost Command Handler (MAYBE NEW?)
Need a command like `execute_ui <zVaFile> <zBlock>` that:
- Sets `session['zMode'] = "zBifrost"`
- Runs `zWalker.run(zVaFile, zBlock)`
- Returns when complete

## Terminal vs Web Modes

### Terminal Mode (WORKS):
```bash
python3 test_terminal_mode.py
# → session['zMode'] = "Terminal"
# → zDisplay prints to console
# → User sees output in terminal
```

### Web/Bifrost Mode (TO IMPLEMENT):
```javascript
const client = new BifrostClient('ws://localhost:56891');
await client.connect();
await client.zFunc('execute_ui zUI_web_dashboard');
# → session['zMode'] = "zBifrost"
# → zDisplay sends JSON via WebSocket
# → Client renders JSON as HTML
```

## Key Insight from User

> "zDisplay events suppose to output json for zBifrost mode if set up properly"
> "the capture should happen in the zBifrost client"

This means:
- ✅ zDisplay ALREADY supports JSON output (via `send_gui_event()`)
- ✅ zBifrost client ALREADY knows how to render it
- ❌ I was reinventing the wheel with PageRenderer!

## Next Steps

1. ✅ Understand the architecture (DONE)
2. Check if `execute_ui` command exists or needs to be created
3. Create HTML template with zBifrost client
4. Test in browser with WebSocket connection
5. Verify dual-mode (Terminal + Web) works with same zUI file

## Questions

1. Does zBifrost have an `execute_ui` command, or do we need to create it?
2. Should the WebSocket server run on the same walker instance as zServer?
3. How do we handle navigation? (zLink in zBifrost mode)

