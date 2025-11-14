[← Back to zBifrost Guide](../../../../Documentation/zBifrost_GUIDE.md) | [Next: Level 1 →](../Level_1_Echo/README.md)

# Level 0: Hello zBlog

**<span style="color:#8FBE6D">Your first WebSocket connection—just say hello!</span>**

## What You'll Build

A simple web page that connects to a Python server and displays a welcome message. That's it! No database, no fancy features—just proving that your browser can talk to the server.

Think of it like making a phone call: you dial (connect), say hello, then hang up (disconnect).

## What You'll Learn

1. **<span style="color:#8FBE6D">How to start a WebSocket server</span>** in Python (10 lines of code!)
2. **<span style="color:#F8961F">How to connect from a web browser</span>** (just click a button)
3. **<span style="color:#00D4FF">How messages flow</span>** between server and browser

## Files

- **<span style="color:#F8961F">`level0_backend.py`</span>** - The Python server (25 lines)
- **<span style="color:#F8961F">`level0_client.html`</span>** - The web page (uses BifrostClient library)
- **<span style="color:#F8961F">`styles.css`</span>** - The styling (purple gradient theme)

## How to Run

### Step 1: Start the Server

Open your terminal and run:

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_0_Connection
python3 level0_backend.py
```

You should see:

```
🌉 Starting zBlog Server (Level 0)...
📝 Goal: Connect from browser and see welcome message

✅ zBlog server is running!
👉 Open level0_client.html in your browser
👉 Click 'Connect' to see the magic!
```

**Keep this terminal window open!** The server needs to stay running.

### Step 2: Open the Web Page

Just double-click **<span style="color:#F8961F">`level0_client.html`</span>** (or drag it into your browser).

You'll see a purple page with a big "Connect to Server" button.

### Step 3: Connect!

1. Click **<span style="color:#8FBE6D">"🚀 Connect to Server"</span>**
2. You should see:
   - Status changes to **"✅ Connected to zBlog!"**
   - A welcome message appears: **"🎉 Hello from zBlog!"**
3. Click **<span style="color:#EA7171">"👋 Disconnect"</span>** when you're done

**That's it!** You just made your first WebSocket connection! 🎉

## What's Happening Under the Hood

### The Server (Python)

```python
z = zCLI({
    "zMode": "zBifrost",  # This tells zCLI to start a WebSocket server
    "websocket": {
        "host": "127.0.0.1",  # localhost (your computer)
        "port": 8765           # The "phone number" to call
    }
})

z.walker.run()  # Keep the server running
```

When you run this, zCLI automatically:
1. Starts a WebSocket server on port 8765
2. Waits for browsers to connect
3. Sends a welcome message when they do

### The Client (JavaScript)

```javascript
// Use BifrostClient library (production-ready!)
const client = new BifrostClient('ws://127.0.0.1:8765', {
    hooks: {
        onConnected: () => showConnected(),
        onMessage: (msg) => {
            if (msg.event === 'connection_info') {
                showWelcome();  // Show "Hello from zBlog!"
            }
        }
    }
});

// Connect with one line!
await client.connect();
```

The browser:
1. Loads BifrostClient library (handles all WebSocket complexity)
2. Connects to `ws://127.0.0.1:8765` (like dialing a phone number)
3. BifrostClient automatically parses JSON and calls your hooks
4. Displays the welcome message when it arrives

**Key Point:** You're using the same production-ready library that powers all of zCLI's WebSocket features!

### Why This Approach? (Imperative vs Declarative)

**Level 0 is intentionally imperative** - you're learning the fundamentals:

```javascript
// You manually handle each message type
onMessage: (msg) => {
    if (msg.event === 'connection_info') {
        showWelcome();  // You decide what to do
    }
}
```

**This teaches you:**
- How WebSocket communication works
- How to use BifrostClient with conventional tools
- The hooks pattern (foundational for all levels)
- How to handle messages imperatively (useful for custom apps)

**In future levels, this becomes declarative:**

**Level 3+** (Backend does the work):
```python
# Backend: Just describe what you want
z.display.success("Hello from zBlog!")
z.display.header("Welcome to Level 3")
```

```javascript
// Frontend: Auto-renders based on event type!
onDisplay: (data) => {
    // BifrostClient automatically renders
    // success → green box
    // header → big title
    // No manual if/else needed!
}
```

**The progression:**
- **Level 0**: Learn the plumbing (imperative)
- **Level 3**: See the magic (declarative zDisplay events)
- **Level 5+**: Pure productivity (auto-rendering)

This is the **zCLI teaching philosophy**: understand the foundation, then leverage the abstractions.

### Development vs Production

**Right now (Development):**
- The HTML loads BifrostClient from your local zCLI installation
- Works offline, no internet required
- Path: `../../../../zCLI/subsystems/zComm/zComm_modules/bifrost/bifrost_client_modular.js`

**In Production (After deploying):**
- Switch to CDN: `https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.5/...`
- Works from anywhere with internet
- Same code, just different source!

This is the **zolo way**: develop locally, deploy globally with one line change.

## Success Checklist

- **<span style="color:#8FBE6D">Server starts</span>** without errors
- **<span style="color:#8FBE6D">Browser connects</span>** (green status)
- **<span style="color:#F8961F">Welcome message appears</span>** ("Hello from zBlog!")
- **<span style="color:#EA7171">Disconnect works</span>** (status turns red)

## Troubleshooting

### "Connection failed! Is the server running?"

**Problem:** The browser can't find the server.

**Solution:**
1. Check that `level0_backend.py` is still running in your terminal
2. Look for the message "✅ zBlog server is running!"
3. If not, run `python3 level0_backend.py` again

### "Address already in use"

**Problem:** Port 8765 is already being used by another program.

**Solution:**
```bash
# Kill whatever is using port 8765
lsof -ti:8765 | xargs kill -9

# Then start the server again
python3 level0_backend.py
```

### Nothing happens when I click Connect

**Problem:** JavaScript might be disabled or there's a browser issue.

**Solution:**
1. Press `F12` to open Developer Tools
2. Click the "Console" tab
3. Look for error messages (red text)
4. Try a different browser (Chrome, Firefox, Safari)

## What's Next?

In **<span style="color:#F8961F">Level 1</span>**, you'll learn to send messages FROM the browser TO the server (two-way communication!). You'll type a message, send it, and get an echo back—like a parrot! 🦜

**Key Concept:** Level 0 is one-way (server → browser). Level 1 is two-way (browser ↔ server).

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 5 minutes
