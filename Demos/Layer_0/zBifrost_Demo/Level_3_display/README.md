[← Back to Level 2](../Level_2_Post_Feed/README.md) | [Next: Level 4 →](../Level_4_zTheme/README.md)

# Level 3: zDisplay Events

**<span style="color:#8FBE6D">The game changer—declarative display events replace manual DOM manipulation!</span>**

## What You'll Build

The same blog interface, but instead of manually creating HTML elements with JavaScript, you'll use **zDisplay events** from Python! The backend describes what to show (headers, lists, signals), and the frontend automatically renders them.

Think of it like writing HTML in Python—but it works everywhere: Terminal AND browser!

## What You'll Learn

1. **<span style="color:#8FBE6D">How zDisplay events work</span>** (declarative vs imperative)
2. **<span style="color:#F8961F">Dual-mode rendering</span>** (same code works in Terminal and browser)
3. **<span style="color:#00D4FF">Auto-broadcasting</span>** (`z.display.*` calls automatically send to WebSocket)
4. **<span style="color:#667eea">Toast-style alerts</span>** (auto-fade signals with × dismiss button)
5. **<span style="color:#EA7171">HERO headers</span>** (indent=0 for centered, large titles)
6. **<span style="color:#8FBE6D">Semantic HTML headers</span>** (indent=1-6 maps to h1-h6)

## Files

- **<span style="color:#F8961F">`hello_bifrost.py`</span>** - Python server with zDisplay events (104 lines)
- **<span style="color:#F8961F">`hello_client.html`</span>** - Web page with custom rendering logic (313 lines)
- **<span style="color:#667eea">No separate CSS file</span>** - Styles are inline (will be replaced by zTheme in Level 4)

## How to Run

### Step 1: Start the Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_3_display
python3 hello_bifrost.py
```

You should see:

```
🌉 Starting Hello zCLI Server (zBifrost mode)...
📝 Goal: See the SAME code render in a browser
🎉 NEW: z.display now broadcasts automatically - no manual JSON!

✓ Hello handler registered!
✅ Server is running on ws://127.0.0.1:8765
👉 Open hello_client.html in your browser
👉 Click 'Connect to Server' to see the magic!
```

**Keep this terminal window open!**

### Step 2: Open the Web Page

Double-click **<span style="color:#F8961F">`hello_client.html`</span>** (or drag into browser).

**Note:** Like previous levels, this works with `file://` protocol!

### Step 3: Connect and Watch the Magic!

1. Click **<span style="color:#8FBE6D">"🚀 Connect to Server"</span>**
2. **NEW:** Content appears **automatically** (no "Load Feed" button needed!)
3. Watch the **toast-style signals** at the top auto-fade after 5 seconds
4. Dismiss them early with the **×** button
5. See the **HERO header** centered and prominent
6. Scroll through **h1-h6 header examples**
7. See the **bulleted list** of subsystems

**That's declarative magic!** ✨

## What's Happening Under the Hood

### The Server (Python) - NEW: zDisplay Events

```python
# These are zDisplay events - they work in Terminal AND browser!
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")
z.display.success("✨ All subsystems loaded and ready!")

# HERO header (indent=0 → centered, large, prominent)
z.display.header("🎨 zDisplay Events Showcase", color="CYAN", indent=0)

# Regular headers (indent=1-6 → h1-h6)
z.display.header("Level 1 Header (h1)", color="CYAN", indent=1)
z.display.header("Level 2 Header (h2)", color="CYAN", indent=2)
# ... h3, h4, h5, h6

# List event (no manual loops!)
z.display.list(subsystems, style="bullet", indent=1)
```

**What's new:**
1. **No manual JSON construction!** Just call `z.display.*()` methods
2. **Auto-broadcasting:** Each call automatically sends to WebSocket
3. **Declarative:** You describe WHAT to show, not HOW to render it
4. **Dual-mode:** The SAME code works in Terminal (ANSI colors) and browser (HTML)

### The Client (JavaScript) - NEW: Event-Based Rendering

```javascript
function handleMessage(msg) {
    // Handle both old format (event: "success") and new format (display_event: "success")
    const event = msg.display_event || msg.event;
    
    switch(event) {
        case 'success':
            appendMessage(content, 'success', indent);
            break;
        case 'info':
            appendMessage(content, 'info', indent);
            break;
        case 'header':
            // Render header based on indent (0=HERO, 1-6=h1-h6)
            break;
        case 'list':
            // Render list with bullets
            break;
    }
}
```

**What's new:**
1. We handle **display events** (not custom events like Level 2)
2. The server DESCRIBES the UI ("show a success message")
3. The client RENDERS based on event type
4. **Still imperative** on frontend (manual switch/case) - Level 4 fixes this!

### The Handler Registration

```python
# Register the handler for the client to trigger display
z.comm.websocket._event_map['show_hello'] = handle_show_hello
```

When the client sends `{event: 'show_hello'}`, the server:
1. Routes to `handle_show_hello()` function
2. Executes all `z.display.*()` calls
3. Each call **auto-broadcasts** to WebSocket
4. Client receives and renders each event

### The Flow

```
Browser                          Server
   |                               |
   |  1. Connect                   |
   |------------------------------>|
   |                               |
   |  2. {event: 'show_hello'}     |
   |------------------------------>|
   |                               |
   |  3. Execute handle_show_hello |
   |     z.display.success(...)    |
   |     z.display.header(...)     |
   |     z.display.list(...)       |
   |                               |
   |  4. Auto-broadcast each event |
   |  {display_event: 'success'..} |
   |<------------------------------|
   |  {display_event: 'header'...} |
   |<------------------------------|
   |  {display_event: 'list'...}   |
   |<------------------------------|
   |                               |
   |  5. Render each event         |
   |     (custom switch/case)      |
   |                               |
```

**Key Difference from Level 2:**
- Level 2: Manual JSON, manual rendering, custom events
- Level 3: **zDisplay events, auto-broadcasting, standard event types**

## Success Checklist

- **<span style="color:#8FBE6D">Server starts</span>** without errors
- **<span style="color:#8FBE6D">Browser connects</span>** (status shows connected)
- **<span style="color:#F8961F">Toast signals appear at top</span>** and auto-fade after 5 seconds
- **<span style="color:#00D4FF">× button dismisses signals</span>** immediately
- **<span style="color:#667eea">HERO header appears centered</span>** and large
- **<span style="color:#EA7171">h1-h6 headers render</span>** with proper sizing
- **<span style="color:#8FBE6D">Bulleted list appears</span>** with proper formatting

## New Features Showcase

### 🎯 Toast-Style Alerts (Auto-Fade)

The signals (`success`, `info`, `warning`, `error`) now:
- ✅ Auto-fade after **5 seconds** with slide-up animation
- ✅ Can be **manually dismissed** with × button
- ✅ Smooth **fade-in** when they appear
- ✅ Pure **zTheme CSS** (no Bootstrap!)

### 🦸 HERO Headers (indent=0)

```python
z.display.header("🎨 zDisplay Events Showcase", color="CYAN", indent=0)
```

Creates a centered, large, prominent title:
- Font size: **3rem** (48px)
- Weight: **900** (ultra-bold)
- Alignment: **centered**
- Color: **Primary green** (`--color-primary`)

### 📐 Semantic Headers (indent=1-6)

```python
z.display.header("Level 1 Header (h1)", color="CYAN", indent=1)
z.display.header("Level 2 Header (h2)", color="CYAN", indent=2)
# ... etc
```

Maps to proper HTML:
- `indent=1` → `<h1>` (largest)
- `indent=2` → `<h2>`
- ...
- `indent=6` → `<h6>` (smallest)

### 📝 List Events

```python
z.display.list(subsystems, style="bullet", indent=1)
```

Renders a proper `<ul>` with:
- Bullet points (or numbered if `style="numbered"`)
- Proper indentation
- Clean styling via `.zList` class

## Troubleshooting

### Signals don't appear

**Problem:** Handler might not be registered.

**Solution:**
1. Check terminal for "✓ Hello handler registered!"
2. Restart `hello_bifrost.py`
3. Check browser console (F12) for errors

### Headers look wrong

**Problem:** CSS might not be loading correctly.

**Solution:**
1. Refresh the page (hard refresh: Cmd+Shift+R or Ctrl+F5)
2. Check browser console for CSS errors
3. Verify inline styles in `hello_client.html`

### List appears as text instead of bullets

**Problem:** JavaScript might not be handling `list` event.

**Solution:**
1. Open browser console (F12)
2. Look for `Received:` messages showing `display_event: 'list'`
3. Check if `handleMessage()` has a `case 'list':`

### Signals don't auto-fade

**Problem:** CSS animations might not be working.

**Solution:**
1. Check if your browser supports CSS animations (all modern browsers do)
2. Try manually dismissing with × to test the fade-out
3. Check browser console for JavaScript errors

## The Declarative Shift 🎨

**Level 3 is a MAJOR shift** from imperative to declarative:

### Before (Level 2 - Imperative):
```python
# Server: Manual JSON construction
response = {
    "event": "posts_data",
    "posts": BLOG_POSTS,
    "count": len(BLOG_POSTS)
}
await websocket.send(json.dumps(response))
```

```javascript
// Client: Manual DOM manipulation
const card = document.createElement('div');
const title = document.createElement('h3');
title.textContent = post.title;
card.appendChild(title);
// ... 50 more lines of DOM manipulation
```

### Now (Level 3 - Declarative):
```python
# Server: Just describe what you want!
z.display.success("✨ All subsystems loaded and ready!")
z.display.header("🎨 zDisplay Events Showcase", indent=0)
z.display.list(subsystems, style="bullet", indent=1)
# Auto-broadcasts, auto-formats, auto-works everywhere!
```

```javascript
// Client: Still imperative (for now)
switch(event) {
    case 'success':
        appendMessage(content, 'success');
        break;
    // ... still manual, but simpler
}
```

**The progression:**
- **Level 2**: 100% imperative (both server and client)
- **Level 3**: Declarative server, imperative client (halfway there!)
- **Level 4**: 100% declarative (server describes, zTheme auto-renders!) 🚀

## What's Next?

In **<span style="color:#F8961F">Level 4</span>**, you'll see **THE ULTIMATE SIMPLICITY**! The same interface, but with `zTheme: true` - the client auto-renders EVERYTHING! No more switch/case, no more manual DOM manipulation. Just pure magic! ✨

**Key Concept:** Level 3 makes the server declarative. Level 4 makes the client declarative too (full stack declarative!).

---

**Version**: 1.5.5  
**Difficulty**: Intermediate  
**Time**: 20 minutes  
**Builds On**: Level 2 (imperative patterns)  
**Major Shift**: From imperative to declarative paradigm

