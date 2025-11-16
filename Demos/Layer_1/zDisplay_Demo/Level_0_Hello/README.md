[← Back to Tutorial](../README.md) | [Next: Level 1 →](../Level_1_Display/README.md)

# Level 0: Hello zCLI

**<span style="color:#8FBE6D">Your first zCLI program—Terminal AND browser, same code!</span>**

## What You'll Build

Two versions of the same program:
1. **Terminal Mode** - Runs in your terminal with ANSI colors
2. **zBifrost Mode** - Runs in your browser with WebSocket

**The magic?** The display code is IDENTICAL. Only the initialization differs.

**🎉 NEW:** `z.display` now auto-broadcasts in zBifrost mode—no manual JSON construction needed!

## What You'll Learn

1. **<span style="color:#8FBE6D">Dual-mode rendering</span>** - Same code, Terminal or browser
2. **<span style="color:#F8961F">Zero-config initialization</span>** - One line, everything ready
3. **<span style="color:#00D4FF">Display events</span>** - success, info, text signals
4. **<span style="color:#EA7171">Mode detection</span>** - Automatic adaptation

## Files

- **`hello_terminal.py`** - Terminal version (ANSI output)
- **`hello_bifrost.py`** - Browser version (WebSocket server)
- **`hello_client.html`** - Browser client (connects to server)

## Part 1: Terminal Mode

### The Code

```python
from zCLI import zCLI

# Initialize zCLI (zero config!)
z = zCLI()

# Display output (works in Terminal AND browser!)
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")
```

**That's it!** Three lines of code.

### How to Run

```bash
cd Demos/Layer_1/zDisplay_Demo/Level_0_Hello
python3 hello_terminal.py
```

You should see:

```
✅ Hello from zCLI!
ℹ️  Mode: Terminal
ℹ️  Workspace: /path/to/Level_0_Hello
ℹ️  Deployment: Debug

Available subsystems:
  • z.config   - Configuration management
  • z.display  - Output & rendering
  [... 12 more subsystems ...]
  
✨ All subsystems loaded and ready!
```

**That green checkmark?** That's zDisplay automatically formatting based on signal type. ANSI colors in Terminal, styled elements in browser—automatically.

## Part 2: zBifrost Mode (Browser)

### The Code

```python
from zCLI import zCLI

# Initialize zCLI in zBifrost mode (WebSocket server)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"host": "127.0.0.1", "port": 8765}
})

# THE SAME display code!
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")

# Start WebSocket server
z.walker.run()
```

**Key Point:** Lines 8-9 are IDENTICAL to the terminal version. Only initialization differs!

### How to Run

**Step 1: Start the server**

```bash
python3 hello_bifrost.py
```

You should see:

```
🌉 Starting Hello zCLI Server (zBifrost mode)...
📝 Goal: See the SAME code render in a browser

✅ Server is running on ws://127.0.0.1:8765
👉 Open hello_client.html in your browser
👉 Click 'Connect to Server' to see the magic!
```

**Keep this terminal open!** The server needs to stay running.

**Step 2: Open the browser**

Double-click `hello_client.html` (or drag it into your browser).

**Step 3: Connect**

Click the **"🚀 Connect to Server"** button.

You should see the SAME output as the terminal version, but styled beautifully in your browser!

## What's Happening Under the Hood

### Initialization

```python
# Terminal mode (default)
z = zCLI()
# → mode = "Terminal"
# → Output via print() with ANSI colors

# zBifrost mode (explicit)
z = zCLI({"zMode": "zBifrost", "websocket": {"port": 8765}})
# → mode = "zBifrost"
# → Output via WebSocket JSON events
# → Starts ws://127.0.0.1:8765 server
```

With zero arguments, zCLI automatically:
1. ✅ Detects your machine (OS, hostname, architecture)
2. ✅ Creates config files if they don't exist
3. ✅ Initializes logger
4. ✅ Sets up session context
5. ✅ Loads environment variables from `.zEnv` if present
6. ✅ Sets mode to "Terminal" (default) or "zBifrost" (if specified)

### Display Events

```python
z.display.success("Done!")
```

**Terminal mode:**
- Renders as: `\033[32m✅ Done!\033[0m` (ANSI green)

**zBifrost mode:**
- Sends JSON: `{"event": "success", "content": "Done!"}`
- Browser renders as styled HTML element

**You write it once. zDisplay handles the rest.**

### The BifrostClient

The HTML file uses the `BifrostClient` library:

```javascript
const client = new BifrostClient('ws://127.0.0.1:8765', {
    hooks: {
        onConnected: (info) => console.log('Connected!'),
        onMessage: (msg) => handleMessage(msg)
    }
});

await client.connect();
```

The client:
1. Connects to the WebSocket server
2. Receives JSON events from Python
3. Renders them as styled HTML elements
4. All automatic!

## The zCLI Philosophy

> **<span style="color:#F8961F">Declare once—run everywhere.</span>**

You write:
```python
z.display.success("Done!")
```

zCLI runs it:
- **Terminal**: Green ANSI text
- **Browser**: Styled success notification
- **Mobile**: (future) Native widget
- **Electron**: (future) Desktop notification

**Same code. Zero changes. That's the power of zDisplay.**

## Success Checklist

### Terminal Mode
- **<span style="color:#8FBE6D">Green checkmark appears</span>** ("Hello from zCLI!")
- **<span style="color:#F8961F">Info icons appear</span>** (Mode, Workspace, Deployment)
- **<span style="color:#00D4FF">Subsystems list</span>** (14 items)

### zBifrost Mode
- **<span style="color:#8FBE6D">Server starts</span>** (ws://127.0.0.1:8765)
- **<span style="color:#F8961F">Browser connects</span>** (status: "Connected")
- **<span style="color:#00D4FF">Same output renders</span>** (styled in browser)

## Troubleshooting

### ModuleNotFoundError: No module named 'zCLI'

**Problem:** zCLI is not installed.

**Solution:**
```bash
pip install git+https://github.com/ZoloAi/zolo-zcli.git
```

### Connection failed in browser

**Problem:** Server not running or wrong port.

**Solution:**
1. Check that `hello_bifrost.py` is running
2. Look for "Server is running on ws://127.0.0.1:8765"
3. Refresh the browser page

### Address already in use

**Problem:** Port 8765 is already being used.

**Solution:**
```bash
# Kill whatever is using port 8765
lsof -ti:8765 | xargs kill -9

# Then start the server again
python3 hello_bifrost.py
```

## Experiment!

Try modifying the display code in **hello_bifrost.py**:

```python
# Add more signals
z.display.error("Oops, something broke!")
z.display.warning("Watch out!")

# Add a header
z.display.header("My First zCLI App", color="CYAN")

# Add a table
users = [{"Name": "Alice", "Role": "Admin"}]
z.display.zTable("Users", ["Name", "Role"], users)
```

**Restart the server, reconnect in browser, see the changes!**

The point: Any zDisplay method works in both modes. Experiment freely!

## What's Next?

In **<span style="color:#F8961F">Level 1</span>**, you'll learn about:
- Tables (structured data with pagination)
- Lists and JSON (formatted output)
- Progress bars (visual feedback)
- User input (forms and selections)

**Key Concept:** Level 0 shows dual-mode rendering. Level 1 shows real data display.

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 10 minutes (5 min Terminal + 5 min zBifrost)  
**Prerequisites**: None!
