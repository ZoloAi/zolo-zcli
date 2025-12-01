# Level 6: User Input (Bifrost Mode)

**Difficulty:** Intermediate  
**Prerequisites:** Level 0-3 (Connection, Display, Inputs), zVars concept from Level 2 Config

---

## 🎯 What You'll Build

A **Bifrost web application** that collects user inputs via HTML forms and stores them in `session["zVars"]` for cross-mode compatibility.

**Key Pattern:**
- ✅ Backend: Async handlers use `await` for input collection
- ✅ Storage: Inputs immediately stored in `session["zVars"]`
- ✅ Display: Logic reads from zVars synchronously (no `await` needed)
- ✅ Frontend: BifrostClient auto-renders forms via `onInput` hook

---

## 🚀 Quick Start

### 1. Start the Python Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_6_inputs
python3 input_bifrost.py
```

Expected output:
```
============================================================
🚀 zBifrost Input Demo Server Starting...
============================================================
📡 WebSocket: ws://127.0.0.1:8765
🌐 Client: Open input_client.html in your browser
💡 Pattern: Async inputs → zVars → Sync display
============================================================
```

### 2. Open the HTML Client

Open `input_client.html` in your browser (use Live Server or file://)

**What Happens:**
1. ✅ Auto-connects to WebSocket server
2. ✅ Sends `show_inputs` request
3. ✅ Backend displays headers and prompts
4. ✅ BifrostClient renders HTML input forms
5. ✅ You submit → Backend stores in zVars → Displays results

---

## 📚 What You'll Learn

### 1. Async Input Collection Pattern

**Backend (Python):**
```python
# Async handler collects inputs with await
async def handle_show_inputs(zcli, parsed, websocket):
    # Collect and store in zVars
    zcli.session["zVars"]["name"] = await zcli.display.read_string("Name: ")
    
    # Display from zVars (sync, no await)
    zcli.display.success(f"Hello, {zcli.session['zVars']['name']}!")
```

**Key Insight:**
- ✅ `await` only appears in input collection
- ✅ Display logic reads from zVars synchronously
- ✅ Clean separation of async concerns

### 2. BifrostClient Auto-Rendering

**Frontend (HTML):**
```javascript
const client = new BifrostClient('ws://127.0.0.1:8765', {
    autoConnect: true,
    zTheme: true,
    autoRequest: 'show_inputs',
    debug: true
});
```

**What Happens Automatically:**
1. ✅ BifrostClient's `onInput` hook detects `input_request` events
2. ✅ Calls `zDisplayRenderer.renderInputRequest()`
3. ✅ Dynamically creates HTML `<form>` with `<input>` fields
4. ✅ Submits → `client.sendInputResponse(requestId, value)`
5. ✅ Backend receives → Resolves `asyncio.Future` → Populates zVars

### 3. Session Variables (zVars)

**Why Use zVars?**
- ✅ **Cross-mode:** Same pattern works in Terminal & Bifrost
- ✅ **Async isolation:** Input collection = `await`, display = sync
- ✅ **Session-wide:** Accessible across all handlers
- ✅ **Clean code:** No scattered `await` calls in display logic

**Example:**
```python
# Store once
zcli.session["zVars"]["email"] = await zcli.display.read_string("Email: ")

# Access many times (no await)
zcli.display.info(f"Email: {zcli.session['zVars']['email']}")
zcli.display.text(f"Domain: {zcli.session['zVars']['email'].split('@')[1]}")
```

---

## 🎨 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser                             │
│                                                             │
│  1. BifrostClient connects                                  │
│  2. Sends "show_inputs" request                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  onInput Hook (Auto-registered)                      │  │
│  │  ↓                                                    │  │
│  │  zDisplayRenderer.renderInputRequest()               │  │
│  │  ↓                                                    │  │
│  │  Creates <form> with <input> dynamically             │  │
│  │  ↓                                                    │  │
│  │  User submits → sendInputResponse(requestId, value)  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend (zBifrost)                  │
│                                                             │
│  async def handle_show_inputs(zcli, parsed, websocket):    │
│                                                             │
│  1. Display headers, text (broadcast immediately)           │
│  2. await read_string() → Sends input_request              │
│     ↓                                                       │
│  3. Wait for input_response from client                     │
│     ↓                                                       │
│  4. Store in session["zVars"]["name"]                       │
│     ↓                                                       │
│  5. Display results from zVars (sync, no await)             │
│                                                             │
│  Result: Clean async isolation! ✨                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Compare: Terminal vs. Bifrost

### Terminal Mode (Level 3):
```python
# Direct synchronous input
z.session["zVars"]["name"] = z.display.read_string("Name: ")
z.display.success(f"Hello, {z.session['zVars']['name']}!")
```

### Bifrost Mode (Level 6):
```python
# Async input with await
z.session["zVars"]["name"] = await z.display.read_string("Name: ")
z.display.success(f"Hello, {z.session['zVars']['name']}!")
```

**Key Difference:**
- ✅ Terminal: Returns `str` immediately
- ✅ Bifrost: Returns `asyncio.Future`, requires `await`
- ✅ Storage pattern: **Identical** (zVars in both)

---

## 🧪 Try It Yourself

### Experiment 1: Add More Inputs

Add an email input to `input_bifrost.py`:

```python
# Collect email
zcli.session["zVars"]["email"] = await zcli.display.read_string("Email: ")

# Display email domain
domain = zcli.session["zVars"]["email"].split("@")[1]
zcli.display.info(f"Domain: {domain}")
```

**No frontend changes needed!** BifrostClient auto-renders the form.

### Experiment 2: Validate Input

Add validation logic:

```python
# Collect age
age_str = await zcli.display.read_string("Age: ")
zcli.session["zVars"]["age"] = int(age_str)

# Validate
if zcli.session["zVars"]["age"] < 18:
    zcli.display.warning("You must be 18+ to continue")
else:
    zcli.display.success("Age verified!")
```

### Experiment 3: Conditional Inputs

```python
# Ask for subscription preference
wants_newsletter = await zcli.display.read_string("Subscribe? (yes/no): ")

if wants_newsletter.lower() == "yes":
    # Only ask for email if they want newsletter
    zcli.session["zVars"]["email"] = await zcli.display.read_string("Email: ")
    zcli.display.success("Subscribed!")
```

---

## 💡 Key Takeaways

1. ✅ **zVars Pattern:** Store inputs in `session["zVars"]` for clean async handling
2. ✅ **Async Isolation:** `await` only in input collection, display logic is sync
3. ✅ **BifrostClient Magic:** Auto-renders forms, handles async responses
4. ✅ **Cross-Mode:** Same pattern works in Terminal & Bifrost
5. ✅ **No Custom Frontend:** BifrostClient's `onInput` hook does all the work

---

## 📖 Next Steps

- **Explore Level 5:** Learn advanced zDisplay events (tables, JSON, progress)
- **Read zVars Guide:** Understand session variable architecture
- **Build a Form:** Create multi-step registration with validation
- **Add Complex Inputs:** Learn `selection()`, `zMenu()`, `zDialog()` (advanced)

---

**Congratulations!** 🎉 You've mastered primitive input collection in Bifrost mode with the zVars pattern!

