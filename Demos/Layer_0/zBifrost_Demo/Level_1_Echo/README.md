[← Back to Level 0](../Level_0_Connection/README.md) | [Next: Level 2 →](../Level_2_Post_Feed/README.md)

# Level 1: Echo Test

**<span style="color:#8FBE6D">Two-way communication—send a message, get it back!</span>**

## What You'll Build

A web page that not only receives messages from the server (like Level 0), but can also **send messages TO the server** and get responses back. This proves true two-way communication works!

Think of it like a conversation: you say something, the other person responds. Not just listening!

## What You'll Learn

1. **<span style="color:#8FBE6D">How to send messages from browser to server</span>** (client → server)
2. **<span style="color:#F8961F">How to receive custom responses</span>** (server → client)
3. **<span style="color:#00D4FF">Two-way communication pattern</span>** (the foundation of all interactive apps)

## Files

- **<span style="color:#F8961F">`level1_backend.py`</span>** - Python server with echo handler (48 lines)
- **<span style="color:#F8961F">`level1_client.html`</span>** - Web page with message input (uses BifrostClient)
- **<span style="color:#F8961F">`styles.css`</span>** - Same purple gradient theme from Level 0

## How to Run

### Step 1: Start the Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_1_Echo
python3 level1_backend.py
```

You should see:

```
Starting zBlog Server (Level 1: Echo Test)...
Goal: Send messages from browser, get echo responses

zBlog server is running!
Open level1_client.html in your browser
Type a message and click 'Send' to test echo!
```

**Keep this terminal window open!**

### Step 2: Open the Web Page

Double-click **<span style="color:#F8961F">`level1_client.html`</span>** (or drag into browser).

**Note:** Like Level 0, BifrostClient automatically detects `file://` protocol and works without an HTTP server!

### Step 3: Test Echo!

1. Click **<span style="color:#8FBE6D">"🚀 Connect to Server"</span>**
2. You'll see the welcome message (like Level 0)
3. **NEW:** An input box appears below!
4. Type any message (e.g., "Hello zBlog!")
5. Click **"📤 Send"** or press Enter
6. Watch the server echo it back: **"Echo: Hello zBlog!"**

**Try it multiple times!** Each message gets echoed back.

## What's Happening Under the Hood

### The Server (Python) - NEW: Custom Handler

```python
# Register custom message handler for echo
async def handle_echo_message(websocket, message_data):
    """Handle echo requests from clients"""
    if message_data.get('event') == 'echo':
        # Echo the message back
        response = {
            "event": "echo_response",
            "original": message_data.get('message', ''),
            "echo": f"Echo: {message_data.get('message', '')}",
            "timestamp": message_data.get('timestamp')
        }
        await z.comm.broadcast_websocket(response)

# Attach the handler to zBifrost
z.comm.bifrost.custom_handlers['echo'] = handle_echo_message
```

**What's new:**
1. We define a custom handler function
2. It listens for messages with `event: 'echo'`
3. When it receives one, it sends back an `echo_response`
4. The response includes the original message + "Echo: " prefix

### The Client (JavaScript) - NEW: Sending Messages

```javascript
async function sendMessage() {
    const message = input.value.trim();
    
    // Create echo request
    const echoRequest = {
        event: 'echo',
        message: message,
        timestamp: Date.now()
    };
    
    // Send via BifrostClient's send() method
    if (client.isConnected()) {
        client.send(echoRequest);  // No need to JSON.stringify!
    }
}

// Handle echo responses
onMessage: (msg) => {
    if (msg.event === 'echo_response') {
        showEchoResponse(msg);  // Display in log
    }
}
```

**What's new:**
1. User types a message
2. We create a JSON object with `event: 'echo'`
3. **NEW API:** Use `client.send(payload)` instead of `client.connection.send()`
4. BifrostClient automatically handles JSON.stringify() for you
5. Server processes it and sends back `echo_response`
6. Our `onMessage` hook catches it and displays it

### The Flow

```
Browser                          Server
   |                               |
   |  1. Connect                   |
   |------------------------------>|
   |                               |
   |  2. connection_info           |
   |<------------------------------|
   |                               |
   |  3. {event: 'echo', message}  |
   |------------------------------>|
   |                               |
   |  4. {event: 'echo_response'}  |
   |<------------------------------|
   |                               |
```

**Key Difference from Level 0:**
- Level 0: Only step 1 & 2 (server → client)
- Level 1: Steps 3 & 4 added (client → server → client)

## Success Checklist

- **<span style="color:#8FBE6D">Server starts</span>** without errors
- **<span style="color:#8FBE6D">Browser connects</span>** (green status)
- **<span style="color:#F8961F">Input box appears</span>** after connecting
- **<span style="color:#00D4FF">Message gets echoed back</span>** when you click Send
- **<span style="color:#EA7171">Multiple messages work</span>** (try sending 3-4 messages)

## Troubleshooting

### "Not connected to server!" alert

**Problem:** Trying to send before connecting.

**Solution:** Click "Connect to Server" first, wait for green status, then send.

### Echo doesn't appear

**Problem:** Server might not have the custom handler registered.

**Solution:**
1. Check terminal for errors
2. Restart `level1_backend.py`
3. Check browser console (F12) for errors

### Input box doesn't show

**Problem:** JavaScript might have an error.

**Solution:**
1. Press F12 → Console tab
2. Look for red error messages
3. Refresh the page

## What's Next?

In **<span style="color:#F8961F">Level 2</span>**, you'll display **multiple blog posts** in a feed! Instead of echoing messages, you'll load 5 posts and display them as cards—building a real blog homepage!

**Key Concept:** Level 1 proves two-way communication. Level 2 introduces arrays of structured data (multiple posts).

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 10 minutes  
**Builds On**: Level 0 (connection basics)
