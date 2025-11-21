# Level 7: Animations & Progress (Bifrost Mode)

**Difficulty:** Intermediate  
**Prerequisites:** Level 0-6 (Connection, Display, Inputs), Level 4 Terminal Animations
**Builds On:** Level 6 (Fire-and-Forget Pattern)

---

## 🎯 What You'll Build

A **Bifrost web application** that demonstrates **time-based zDisplay events** animating in real-time over WebSocket:

- ✅ **Progress bars** with live percentage/ETA updates
- ✅ **Spinners** with multiple animation styles
- ✅ **Progress iterators** that auto-update per loop iteration
- ✅ **Swiper carousel** with touch gestures and auto-advance

**Key Pattern:**
- ✅ Backend: Async handlers with `await asyncio.sleep()` for timing
- ✅ Transport: WebSocket events broadcast animation state
- ✅ Frontend: BifrostClient + zTheme render animations in CSS
- ✅ Real-time: Smooth updates as backend progresses through work

---

## 🚀 Quick Start

### 1. Start the Python Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_7_Animations
python3 animations_bifrost.py
```

Expected output:
```
╔════════════════════════════════════════════════════════════╗
║   🎡 zBifrost Animations Demo Server Starting...          ║
╚════════════════════════════════════════════════════════════╝
📡 WebSocket: ws://127.0.0.1:8765
🌐 Client: Open animations_client.html in your browser
💡 Pattern: Time-based events → WebSocket → CSS animations
════════════════════════════════════════════════════════════
```

### 2. Open the HTML Client

Open `animations_client.html` in your browser (use Live Server or file://)

**What Happens:**
1. ✅ Auto-connects to WebSocket server
2. ✅ Sends `show_animations` request
3. ✅ Backend broadcasts animation events as they occur
4. ✅ BifrostClient receives events and renders animations
5. ✅ Watch progress bars fill, spinners spin, and slides advance!

---

## 📚 What You'll Learn

### 1. Time-Based Events in Bifrost Mode

**The 4 Animation Events:**

| Event | Terminal | Bifrost (Browser) | WebSocket Event |
|-------|----------|-------------------|-----------------|
| **progress_bar** | ANSI frames | CSS progress widget | `progress_bar` |
| **spinner** | Text frames | CSS spinner | `spinner_start/stop` |
| **progress_iterator** | Line updates | Real-time updates | `progress_bar` |
| **swiper** | Keyboard nav | Touch + buttons | `swiper_init/update` |

### 2. Async Timing with `asyncio.sleep()`

**Backend (Python):**
```python
# Progress bar - manual updates with async sleep
for i in range(total + 1):
    z.display.progress_bar(current=i, total=total, label="Processing")
    await asyncio.sleep(0.05)  # ← Must use asyncio.sleep in async context!

# Spinner - context manager with async sleep
with z.display.spinner("Loading"):
    await asyncio.sleep(2)  # ← Async work happens here

# Progress iterator - async sleep in loop
for item in z.display.progress_iterator(items, "Processing"):
    await asyncio.sleep(0.1)  # ← Each iteration sleeps
```

**⚠️ Critical:** In async handlers, always use `await asyncio.sleep()`, never `time.sleep()` (blocks event loop!)

### 3. WebSocket Animation Protocol

**How It Works:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python)                         │
│                                                             │
│  for i in range(100):                                       │
│      z.display.progress_bar(i, 100, "Processing")          │
│      await asyncio.sleep(0.05)                              │
│      ↓                                                      │
│  Broadcasts: {"event": "progress_bar", "current": i, ...}  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket (Real-time)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (Browser)                         │
│                                                             │
│  BifrostClient receives event                               │
│  ↓                                                          │
│  zDisplayRenderer._renderProgressBar()                      │
│  ↓                                                          │
│  Updates CSS progress bar: width = current/total * 100%     │
│  ↓                                                          │
│  Smooth animation! ✨                                       │
└─────────────────────────────────────────────────────────────┘
```

### 4. Swiper in Bifrost Mode

**Backend:**
```python
z.display.zEvents.TimeBased.swiper(
    slides=["Slide 1", "Slide 2", "Slide 3"],
    label="Tutorial",
    auto_advance=True,
    delay=5
)
```

**Frontend (Automatic):**
- ✅ Touch gestures: Swipe left/right to navigate
- ✅ Slide indicators: Dots showing position (1/3, 2/3, etc.)
- ✅ Auto-advance: Slides progress automatically
- ✅ Navigation buttons: Optional prev/next controls

---

## 🔍 Compare: Level 4 vs Level 7

### Level 4 (Terminal Animations):
```python
# Synchronous - blocks terminal
for i in range(100):
    z.display.progress_bar(i, 100, "Processing")
    time.sleep(0.05)  # ← Blocks terminal
```

### Level 7 (Bifrost Animations):
```python
# Asynchronous - non-blocking WebSocket
for i in range(100):
    z.display.progress_bar(i, 100, "Processing")
    await asyncio.sleep(0.05)  # ← Non-blocking, allows WebSocket to send
```

**Key Differences:**
- ✅ Terminal: Overwrites same line with `\r` (carriage return)
- ✅ Bifrost: Broadcasts events, frontend updates DOM
- ✅ Terminal: `time.sleep()` blocks
- ✅ Bifrost: `await asyncio.sleep()` yields to event loop

---

## 🎨 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 animations_client.html                       │
│                                                              │
│  BifrostClient('ws://127.0.0.1:8765', {                     │
│      autoConnect: true,                                      │
│      zTheme: true,              ← Auto-loads CSS             │
│      autoRequest: 'show_animations',  ← Triggers demo       │
│      debug: true                                             │
│  });                                                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  zDisplayRenderer (Auto-registered)                    │ │
│  │  ↓                                                      │ │
│  │  Handles animation events:                             │ │
│  │  • progress_bar → CSS progress widget                  │ │
│  │  • spinner_start → CSS spinner                         │ │
│  │  • swiper_init → Touch-enabled carousel                │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket (Real-time events)
                            ↓
┌──────────────────────────────────────────────────────────────┐
│               animations_bifrost.py                          │
│                                                              │
│  async def handle_show_animations(_ws, _data):              │
│                                                              │
│  1. Progress bar loop with await asyncio.sleep(0.05)        │
│     → Broadcasts {"event": "progress_bar", ...} 50 times    │
│                                                              │
│  2. Spinner context manager                                 │
│     → Broadcasts {"event": "spinner_start/stop", ...}       │
│                                                              │
│  3. Progress iterator loop                                  │
│     → Broadcasts progress per iteration                     │
│                                                              │
│  4. Swiper initialization                                   │
│     → Broadcasts {"event": "swiper_init", slides: [...]}    │
│                                                              │
│  Result: Smooth real-time animations! ✨                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧪 Try It Yourself

### Experiment 1: Adjust Animation Speed

**Faster Progress:**
```python
for i in range(total + 1):
    z.display.progress_bar(i, total, "Fast!")
    await asyncio.sleep(0.01)  # ← 10ms (10x faster!)
```

**Slower Spinner:**
```python
with z.display.spinner("Slow load"):
    await asyncio.sleep(5)  # ← 5 seconds
```

### Experiment 2: Add More Swiper Slides

```python
slides = [
    "Slide 1: Welcome!",
    "Slide 2: Features",
    "Slide 3: Architecture",
    "Slide 4: Demo",
    "Slide 5: Thank you!"
]

z.display.zEvents.TimeBased.swiper(
    slides=slides,
    label="Extended Tour",
    auto_advance=True,
    delay=3,  # ← 3 seconds per slide
    loop=True  # ← Loop back to start
)
```

### Experiment 3: Nested Progress

```python
# Outer loop
for batch in range(5):
    z.display.header(f"Batch {batch + 1}/5", color="CYAN")
    
    # Inner progress bar
    for i in range(20):
        z.display.progress_bar(i, 20, f"Batch {batch + 1}")
        await asyncio.sleep(0.05)
    
    z.display.success(f"✅ Batch {batch + 1} complete!")
```

---

## 💡 Key Takeaways

1. ✅ **Async Timing:** Always use `await asyncio.sleep()` in Bifrost handlers
2. ✅ **Real-time Updates:** WebSocket broadcasts each animation frame
3. ✅ **CSS Rendering:** Frontend receives events and updates DOM smoothly
4. ✅ **Same API:** `z.display.progress_bar()` works in Terminal AND Bifrost
5. ✅ **Swiper Magic:** Touch gestures and auto-advance work automatically

---

## 🐛 Troubleshooting

### Progress bars show as text instead of CSS widget

**Problem:** The CSS renderer for `progress_bar` may not be fully implemented yet.

**Solution:**
1. Check `zCLI/subsystems/zComm/zComm_modules/bifrost/client/src/rendering/zdisplay_renderer.js`
2. Look for `_renderProgressBar()` method
3. If missing, progress bars will display as text (still functional!)

### Swiper doesn't appear

**Problem:** Swiper events may not be fully wired up in Bifrost mode yet.

**Solution:**
1. Check console for `swiper_init` events being received
2. Verify `zdisplay_renderer.js` has swiper handling
3. For now, swiper works best in Terminal mode (Level 4)

### Animations are choppy

**Problem:** Network latency or too many events.

**Solution:**
```python
# Reduce update frequency
await asyncio.sleep(0.1)  # Instead of 0.05
```

---

## 📖 Next Steps

- **Compare with Level 4:** Run Terminal version to see synchronous animations
- **Read TimeBased Guide:** Learn about threading and animation architecture
- **Build Progress UI:** Add progress bars to long-running operations
- **Customize Spinners:** Try all 6 spinner styles (dots, arc, line, etc.)

---

## 🎓 Learning Progression

This demo builds on:

- **Level 0-2:** WebSocket connection and basic display
- **Level 3:** Declarative server-side rendering
- **Level 4:** zTheme auto-rendering
- **Level 5:** Advanced display events (tables, JSON)
- **Level 6:** Async input collection with Fire-and-Forget pattern
- **Level 7:** Time-based animations over WebSocket ← **YOU ARE HERE**

**What's different from Level 6:**
- ✅ Level 6: Async **input** collection (wait for user)
- ✅ Level 7: Async **animation** timing (visual feedback)

Both use `async/await`, but for different purposes!

---

**Congratulations!** 🎉 You've mastered time-based animations in Bifrost mode!

**Next:** Explore combining animations with inputs for rich interactive UIs!

---

**Version**: 1.5.5  
**Difficulty**: Intermediate  
**Time**: 15 minutes  
**Builds On**: Level 6 (Inputs) + Level 4 Terminal (Animations)  
**Major Feature**: Real-time animations over WebSocket

