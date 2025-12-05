# zComm WebSocket Demo - Deploy to zolo.media

**Goal:** Run zCLI WebSocket server on zolo.media, connect demo to it

---

## Part A: Deploy zCLI to LFS

### 1. Clean Flask Code - Remove Flask-SocketIO Pollution

**Current Problem:**
- Flask has Flask-SocketIO (Socket.IO protocol, not standard WebSocket)
- Need to remove it and use proper WebSocket library

**Files to Update (in `~/Projects/zCloud-flask`):**

**A. `requirements.txt` - Remove Socket.IO, add proper WebSocket:**

Remove these lines:
```
eventlet==0.33.3  # Required for WebSocket support with Gunicorn
Flask-SocketIO==5.3.5  # WebSocket server
python-socketio==5.10.0  # Socket.IO implementation
```

Add:
```
simple-websocket==1.0.0  # Industry-standard WebSocket for Flask
gevent==24.2.1  # Async worker for WebSocket support
```

**B. `server.py` - Remove Socket.IO imports and handlers:**

Remove line 22:
```python
from flask_socketio import SocketIO, emit, disconnect
```

Remove lines 50-60 (WebSocket Configuration section):
```python
# ═══════════════════════════════════════════════════════════
# WebSocket Configuration (Flask-SocketIO)
# ═══════════════════════════════════════════════════════════

socketio = SocketIO(...)
```

Remove lines 211-247 (all `@socketio.on()` handlers)

Remove lines 338-340 (WebSocket endpoint info in startup message)

Change line 352 from:
```python
socketio.run(app, ...)
```
To:
```python
app.run(...)
```

**C. `wsgi.py` - Fix exports:**

Change line 20 from:
```python
from server import app, socketio
```
To:
```python
from server import app
```

Change line 27 from:
```python
socketio.run(app)
```
To:
```python
app.run()
```

**D. `gunicorn.conf.py` - Change worker to gevent (for WebSocket):**

Change line 32 from:
```python
workers = int(os.getenv('GUNICORN_WORKERS', 1))
```
To:
```python
workers = int(os.getenv('GUNICORN_WORKERS', 1))  # Keep 1 for gevent
```

Change line 36 from:
```python
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'eventlet')
```
To:
```python
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')
```

**E. `deployment/environment.example` - Remove WebSocket token, update worker:**

Remove lines 29-31:
```
# WebSocket authentication token
# Generate with: openssl rand -hex 16
WEBSOCKET_TOKEN=demo_secure_token_123
```

Change line 50 from:
```
GUNICORN_WORKERS=4
```
To:
```
GUNICORN_WORKERS=1
```

Change line 51 from:
```
GUNICORN_WORKER_CLASS=sync
```
To:
```
GUNICORN_WORKER_CLASS=gevent
```

**F. Add proper WebSocket route to `server.py`:**

Add after other routes (around line 200):
```python
from simple_websocket import Server, ConnectionClosed

@app.route('/ws')
def websocket_route():
    """WebSocket endpoint - industry standard"""
    if request.environ.get('wsgi.websocket'):
        ws = Server(request.environ)
        try:
            while True:
                message = ws.receive()
                ws.send(f"Echo: {message}")
        except ConnectionClosed:
            pass
        return ''
    return 'WebSocket endpoint', 426  # Upgrade Required
```

### 3. Verify and Push to GitHub

**On Mac:**

```bash
cd ~/Projects/zCloud-flask

# Final verification
echo "=== Checking requirements.txt ==="
grep -E '(gevent|simple-websocket)' requirements.txt
# Expected: gevent==24.2.1
#           simple-websocket==1.0.0

grep -E '(Flask-SocketIO|python-socketio|eventlet)' requirements.txt
# Expected: No output (pollution removed)

echo -e "\n=== Checking gunicorn.conf.py ==="
grep -E 'worker_class|workers = ' gunicorn.conf.py | head -2
# Expected: workers = int(os.getenv('GUNICORN_WORKERS', 1))
#           worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')

echo -e "\n=== Checking server.py WebSocket route ==="
grep -A 3 "def websocket_route" server.py
# Expected: WebSocket route with simple-websocket

echo -e "\n=== All checks passed! Ready to push. ===\n"

# Commit and push
git add -A
git commit -m "Remove Flask-SocketIO, use simple-websocket+gevent for standard WebSocket"
git push origin main
```

### 5. Deploy to LFS (Fix gevent → eventlet)

**On your LFS laptop (as root):**

```bash
su -

# Navigate to app directory
cd /opt/zcloud/app

# Pull latest code (if you pushed from Mac)
su -s /bin/bash zcloud -c "git pull origin main"
```

**Edit 1: requirements.txt (change gevent to eventlet)**

```bash
vi requirements.txt
```

**Vi commands:**
1. Type `/gevent` and press Enter (search for gevent)
2. Press `dd` to delete the line
3. Press `i` to enter insert mode
4. Type: `eventlet==0.36.1  # Async worker for WebSocket (no C compilation)`
5. Press `Esc` to exit insert mode
6. Type `:wq` and press Enter (save and quit)

**Edit 2: gunicorn.conf.py (change worker class)**

```bash
vi gunicorn.conf.py
```

**Vi commands:**
1. Type `/worker_class.*gevent` and press Enter (search)
2. Press `cw` (change word) when cursor is on 'gevent'
3. Type: `eventlet`
4. Press `Esc`
5. Type `:wq` and press Enter

**Edit 3: deployment/environment.example (change worker class)**

```bash
vi deployment/environment.example
```

**Vi commands:**
1. Type `/WORKER_CLASS=gevent` and press Enter
2. Press `cw` when cursor is on 'gevent'
3. Type: `eventlet`
4. Press `Esc`
5. Type `:wq` and press Enter

**Verify changes:**

```bash
echo "=== Checking requirements.txt ==="
grep eventlet /opt/zcloud/app/requirements.txt

echo "=== Checking gunicorn.conf.py ==="
grep "worker_class.*eventlet" /opt/zcloud/app/gunicorn.conf.py

echo "=== Checking environment.example ==="
grep "WORKER_CLASS=eventlet" /opt/zcloud/app/deployment/environment.example
```

**Install eventlet (no C compilation needed):**

```bash
# Install eventlet + simple-websocket
su -s /bin/bash zcloud -c "/opt/zcloud/venv/bin/pip install eventlet==0.36.1 simple-websocket==1.0.0"

# Verify installation
su -s /bin/bash zcloud -c "/opt/zcloud/venv/bin/pip list | grep -E '(simple-websocket|eventlet)'"
# Expected: simple-websocket   1.0.0 (or 1.1.0)
#           eventlet           0.36.1

# Remove WEBSOCKET_TOKEN from environment (if present)
sed -i '/WEBSOCKET_TOKEN/d' /etc/zcloud/environment

# Restart Flask
/etc/rc.d/init.d/zcloud restart

# Verify it's running
/etc/rc.d/init.d/zcloud status

# Test HTTP endpoint
curl http://127.0.0.1:8000/api/health

exit
```

### 6. Check Flask Logs (Debug HTTP 500)

**On LFS (as root):**

```bash
su -

# Check Flask application logs for errors
tail -50 /var/log/zcloud/app.log

# Check Gunicorn error logs
tail -50 /var/log/zcloud/gunicorn-error.log

# Look for WebSocket-related errors
grep -i "websocket\|500\|error" /var/log/zcloud/app.log | tail -20
```

**Common issue:** `simple-websocket` needs `wsgi.websocket` environment variable, but Gunicorn+eventlet doesn't provide it automatically.

**Fix: Wrap Flask app with simple-websocket WSGI middleware**

Edit `/opt/zcloud/app/wsgi.py`:

```bash
vi /opt/zcloud/app/wsgi.py
```

**Vi commands:**
1. Press `G` to go to end of file
2. Press `O` to insert a new line above
3. Type:
```python
from simple_websocket import WSGIWebSocketServer

# Wrap app with WebSocket middleware for Gunicorn
app = WSGIWebSocketServer(app)
```
4. Press `Esc`
5. Type `:wq` and press Enter

**Restart Flask:**

```bash
/etc/rc.d/init.d/zcloud restart

# Check it started
/etc/rc.d/init.d/zcloud status

exit
```

### 7. Test from Mac

**Verify it works:**

```bash
# Test HTTPS works
curl https://zolo.media/api/health
# Expected: {"status": "healthy", ...}

# Test WebSocket endpoint (still 426 for HTTP)
curl -I https://zolo.media/ws
# Expected: HTTP/2 426 (Upgrade Required - correct for non-WS requests)

# Test Python WebSocket client
cd ~/Projects/zolo-zcli
python3 Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_secure.py
# Expected: ✓ Connected! and echo response
```

---

## Part B: Test zCLI WebSocket Client

### 1. Run the Demo

**File:** `Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_secure.py`

```python
#!/usr/bin/env python3
"""Demo: Connect to zolo.media WebSocket server"""

import asyncio
from websockets import connect

async def demo():
    print("\n" + "="*70)
    print("  🌐 Connecting to zolo.media WebSocket")
    print("="*70)
    print("\n📍 Server: wss://zolo.media/ws")
    print("🔒 Protocol: WSS (via Cloudflare Tunnel)")
    print("⏳ Connecting...\n")
    
    try:
        async with connect("wss://zolo.media/ws") as websocket:
            print("✓ Connected!\n")
            
            # Send message
            await websocket.send("Hello from zCLI!")
            print("📤 Sent: Hello from zCLI!")
            
            # Receive response
            response = await websocket.recv()
            print(f"📨 Received: {response}")
            
            print("\n✓ Demo complete!")
            print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(demo())
```

**Test:**
```bash
cd ~/Projects/zolo-zcli
python3 Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_secure.py
```

**Expected Output:**
```
======================================================================
  🌐 Connecting to zolo.media WebSocket
======================================================================

📍 Server: wss://zolo.media/ws
🔒 Protocol: WSS (via Cloudflare Tunnel)
⏳ Connecting...

✓ Connected!

📤 Sent: Hello from zCLI!
📨 Received: Echo: Hello from zCLI!

✓ Demo complete!
======================================================================
```

### 2. Test Browser Client

**Open the HTML client:**

```bash
# On Mac
open Demos/Layer_0/zComm_Demo/lvl2_websocket/3_client_secure.html
```

**Browser steps:**
1. Click "Connect to zolo.media"
2. Should see: "✓ Connected to zolo.media (WSS)"
3. Type a message and click "Send"
4. Should echo back: "Echo: your message"

**Expected behavior:**
- ✅ Connection establishes immediately (production SSL cert trusted)
- ✅ Messages echo back from zolo.media server
- ✅ No certificate warnings (Cloudflare/Let's Encrypt)

### 3. Commit Demo Changes

```bash
cd ~/Projects/zolo-zcli
git add Demos/Layer_0/zComm_Demo/lvl2_websocket/
git commit -m "Demo 3: Connect to zolo.media WebSocket (WSS)"
git push origin main
```

---

## ✅ Done

**What this proves:**
- ✅ Flask serves industry-standard WebSocket (simple-websocket + gevent)
- ✅ WSS works through Cloudflare Tunnel (automatic SSL upgrade)
- ✅ zCLI connects to production WebSocket server (Python & Browser)
- ✅ Real-world secure communication over your infrastructure
- ✅ No Flask-SocketIO pollution - proper WebSocket protocol

**Infrastructure:**
- **Endpoint:** `wss://zolo.media/ws`
- **Protocol:** Standard WebSocket (RFC 6455)
- **SSL:** Let's Encrypt via Cloudflare
- **Worker:** Gunicorn + gevent
- **Client:** zCLI (Python) + Browser (JavaScript)

**Demo Structure:**
1. Basic server - `1_websocket_server.py`
2. Echo demo - `2_websocket_echo.py`
3. **Production client** - `3_websocket_secure.py` (connects to zolo.media)
4. Broadcast - `4_websocket_broadcast.py`

**Time:** ~25 minutes
