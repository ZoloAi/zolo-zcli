# Layer 0: Cache Demo

**Concepts:** `z.session['zCache']`, cache HIT/MISS, performance comparison, dual-mode rendering

---

## 🎯 What You'll Learn

1. **Session-level caching** - Store expensive results in `z.session['zCache']`
2. **Cache patterns** - Check → Hit (fast) or Miss (slow, then cache)
3. **Performance measurement** - Compare cached vs uncached operations
4. **Dual-mode rendering** - Same code works in Terminal AND browser

---

## 🚀 Quick Start

### Terminal Version (Simplest)

```bash
python3 cache_demo_terminal.py
```

**What happens:**
- Runs 3 operations WITHOUT cache (1.5 seconds)
- Runs 3 operations WITH cache (~0.5 seconds)
- Shows 3x speedup from caching

---

### Browser Version (Same Code!)

```bash
# Terminal 1: Start server
python3 cache_demo_bifrost.py

# Terminal 2: Open HTML in browser (or use Live Server)
open cache_client.html
# Click "Run Cache Demo"
```

**What's different:**
- NOTHING! Same `z.display` calls, rendered in browser
- 🎉 **NEW:** `z.display` now broadcasts automatically in zBifrost mode
- No manual JSON construction needed

---

## 📚 The Cache Pattern

### Without Cache (Slow)

```python
def get_users():
    # Every call hits the database (slow!)
    time.sleep(0.5)  # Simulate query
    return fetch_from_database()

# Call 1: 500ms
# Call 2: 500ms  ← Still slow!
# Call 3: 500ms  ← Still slow!
# Total: 1500ms
```

### With Cache (Fast!)

```python
def get_users_cached():
    cache_key = 'users_list'
    
    # Check cache first
    if cache_key in z.session['zCache']:
        return z.session['zCache'][cache_key]  # ← Instant!
    
    # Cache miss - fetch and save
    result = fetch_from_database()  # 500ms
    z.session['zCache'][cache_key] = result
    return result

# Call 1: 500ms (cache miss)
# Call 2: <1ms  (cache hit!) ← Fast!
# Call 3: <1ms  (cache hit!) ← Fast!
# Total: ~500ms (3x faster!)
```

---

## 🔍 Cache Operations

```python
# Check if cached
if 'my_key' in z.session['zCache']:
    data = z.session['zCache']['my_key']

# Set cache
z.session['zCache']['my_key'] = expensive_data

# Get with default
data = z.session['zCache'].get('my_key', default_value)

# Clear specific key
if 'my_key' in z.session['zCache']:
    del z.session['zCache']['my_key']

# Clear all cache
z.session['zCache'] = {}
```

---

## 💡 When to Use Caching

### ✅ Good Use Cases

- **Database queries** that don't change often (user profiles, settings)
- **API calls** with rate limits or slow responses
- **File I/O** reading large configuration files
- **Computations** that are expensive and deterministic

### ❌ Bad Use Cases

- **Real-time data** that changes frequently (stock prices, live metrics)
- **User-specific data** in multi-user apps (cache collision risk)
- **Large datasets** that consume too much memory
- **Security-sensitive data** (passwords, tokens) - use secure storage instead

---

## 🎨 What's New: Auto-Broadcasting

### Before (Manual JSON Construction)

```python
async def my_handler(websocket, data):
    # Had to manually construct JSON
    await websocket.send(json.dumps({
        "event": "display",
        "type": "success",
        "content": "Hello!"
    }))
```

### After (Automatic Broadcasting) 🎉

```python
async def my_handler(websocket, data):
    # Just call z.display - it broadcasts automatically!
    z.display.success("Hello!")
    z.display.info("This works in Terminal AND browser!")
    z.display.table(data, headers=["Name", "Value"])
```

**How it works:**
- `z.display` detects `zMode: "zBifrost"`
- Automatically broadcasts events via WebSocket
- Same code works everywhere (Terminal, YAML UI, custom handlers)

---

## 🏗️ File Structure

```
zCache_Demo/
├── README.md                    # This file
├── cache_demo_terminal.py       # Terminal version (start here!)
├── cache_demo_bifrost.py        # Browser version (same logic!)
└── cache_client.html            # Browser UI (optional)
```

---

## 🧪 Try It Yourself

### Experiment 1: Change the Delay

In `cache_demo_terminal.py`, find:

```python
def expensive_operation():
    time.sleep(0.5)  # ← Try 0.1 or 1.0
```

**Observation:** Longer delays = bigger cache speedup!

---

### Experiment 2: Clear Cache Mid-Demo

Add this after the first cached call:

```python
z.session['zCache'] = {}  # Clear cache
```

**Observation:** Next call is a cache miss again (slow!)

---

### Experiment 3: Multiple Cache Keys

Try caching different data:

```python
z.session['zCache']['users'] = fetch_users()
z.session['zCache']['posts'] = fetch_posts()
z.session['zCache']['comments'] = fetch_comments()
```

**Observation:** Each key is independent!

---

## 🎓 Next Steps

1. **Master the basics** - Run `cache_demo_terminal.py` and understand the output
2. **See dual-mode** - Run `cache_demo_bifrost.py` to see the same code in a browser
3. **Experiment** - Try the experiments above
4. **Apply to your code** - Use `z.session['zCache']` in your own projects

---

## 📖 Related Concepts

- **zSession** - Runtime context storage (including cache)
- **zConfig** - Configuration hierarchy (machine → environment → session)
- **zDisplay** - Dual-mode rendering (Terminal + WebSocket)
- **zBifrost** - WebSocket bridge for real-time communication

---

## 🐛 Troubleshooting

### "KeyError: 'zCache'"

**Solution:** Initialize cache before use:

```python
if 'zCache' not in z.session:
    z.session['zCache'] = {}
```

### "RuntimeError: No running event loop"

**Solution:** Only use `cache_demo_bifrost.py` in zBifrost mode. For Terminal, use `cache_demo_terminal.py`.

### Browser shows nothing

**Solution:** 
1. Check server is running: `python3 cache_demo_bifrost.py`
2. Check console for errors (F12 in browser)
3. Verify WebSocket connects to `ws://localhost:8765`

---

**🎉 Congratulations!** You've mastered Layer 0 caching and dual-mode rendering!

