## Level 2 Demos: zSpark & Logger Usage

This level introduces **zSpark** as the first entry point for runtime configuration and shows how to **use the built-in logger** in your code.

**Four micro-step demos:**

1. **`zspark_demo.py`** - Control logger level with zSpark
2. **`zlogger_demo.py`** - Use standard z.logger methods in your code
3. **`zlogger_user_demo.py`** - Use custom .dev() and .user() methods for clean production logging
4. **`ztraceback_demo.py`** - Enable automatic exception handling with interactive UI

**Run them:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_demo.py
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_user_demo.py
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/ztraceback_demo.py
```

---

### <span style="color:#8FBE6D">What is zSpark?</span>

**zSpark** is a dictionary you pass directly to `zCLI()` to override runtime settings.

```python
z = zCLI({
    "zMode": "Terminal",
    "logger": "PROD",
})
```

It's the **highest priority** in the configuration hierarchy:
- **zSpark** → Virtual Env → System Env → Config Files → Defaults

This makes it perfect for:
- Quick experiments (no file editing)
- Testing different modes
- Production deployments with specific logger settings
- CI/CD environments with controlled output

---

### <span style="color:#8FBE6D">Why Focus on Logger Level?</span>

The logger level is the **cleanest example** of zSpark because:

1. **Single concern** - Controls only console/file logging behavior
2. **Immediate visible impact** - See results instantly
3. **No side effects** - Doesn't change workflow or require additional setup
4. **Production-ready** - `PROD` mode is essential for deployed applications

This demo intentionally **avoids mixing concerns** with workspace paths, modes, or complex settings.

---

### <span style="color:#8FBE6D">Available Logger Levels</span>

| Level | Console Output | File Output | System Messages | Use Case |
|-------|----------------|-------------|-----------------|----------|
| **DEBUG** | ✓ Everything | ✓ Everything | ✓ Show | Development debugging |
| **INFO** | ✓ General info | ✓ General info | ✓ Show | Default mode, normal operations |
| **WARNING** | ✓ Warnings+ | ✓ Warnings+ | ✓ Show | Production with visibility |
| **ERROR** | ✓ Errors only | ✓ Errors only | ✓ Show | Quiet mode, errors only |
| **CRITICAL** | ✓ Critical only | ✓ Critical only | ✓ Show | Minimal output |
| **PROD** | ✗ None | ✓ Everything | ✗ Hidden | **Production: Silent console, full file logs** |

#### <span style="color:#EA7171">PROD Mode (Special)</span>

**PROD** is designed for production deployments:

```python
z = zCLI({"logger": "PROD"})
```

- **Console:** Completely silent (no initialization noise, no "Ready" banners)
- **File:** Full logs written to `~/Library/Application Support/zolo-zcli/logs/zolo-zcli.log`
- **System Messages:** All aesthetic "Ready" banners suppressed
- **Errors:** Always visible (even in PROD mode)

This gives you **clean production output** while maintaining **full audit trails** in log files.

---

### <span style="color:#8FBE6D">What This Demo Shows</span>

The demo initializes zCLI with `PROD` logger mode and displays the resulting session state:

```python
z = zCLI({
    "zMode": "Terminal",
    "logger": "PROD",
})
session = z.session

# Read back the values
print(f"zMode           : {session.get('zMode')}")
print(f"zLogger (level) : {session.get('zLogger')}")  # "PROD"
print(f"Stored zSpark   : {session.get('zSpark')}")   # {"zMode": "Terminal", "logger": "PROD"}
```

**Key observations:**

1. **Initialization is silent** - No "Ready" banners or system messages in PROD mode
2. **zSpark is preserved** - The dict you passed is stored in `session["zSpark"]`
3. **Logger level is set** - Accessible via `session["zLogger"]`
4. **Session reflects choices** - All settings are immediately available

---

### <span style="color:#8FBE6D">Compare the Output</span>

**With INFO level** (default):
```
[zConfigPaths] Initialized for OS: Darwin
[MachineConfig] Auto-detecting machine information...
[MachineDetector] Found default browser: Chrome
...
═══════════════════ MachineConfig Ready ════════════════════
═════════════════ EnvironmentConfig Ready ══════════════════
═══════════════════ SessionConfig Ready ════════════════════
════════════════════ LoggerConfig Ready ════════════════════
══════════════════ WebSocketConfig Ready ═══════════════════
══════════════════ HttpServerConfig Ready ══════════════════
══════════════════════ zConfig Ready ═══════════════════════
═══════════════════════ zComm Ready ════════════════════════
══════════════════════ ZDISPLAY Ready ══════════════════════
... (12+ more subsystems)

# Session state:
zMode           : Terminal
zLogger (level) : INFO
```

**With PROD level**:
```
# Session state:
zMode           : Terminal
zLogger (level) : PROD
```

The difference is dramatic - **PROD mode gives you clean, production-ready output.**

---

### <span style="color:#8FBE6D">Try Different Levels</span>

Edit the demo and experiment:

```python
# Silent production mode
z = zCLI({"logger": "PROD"})

# Verbose debugging
z = zCLI({"logger": "DEBUG"})

# Warnings and errors only
z = zCLI({"logger": "WARNING"})

# Combine with other settings
z = zCLI({
    "zMode": "Terminal",
    "logger": "PROD",
    "zTraceback": False,
})
```

Each change takes effect **immediately**, with no file editing required.

---

### <span style="color:#8FBE6D">Demo 2: Using z.logger in Your Code</span>

**Run it:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_demo.py
```

Once you understand how to **control** the logger level, the next micro-step is learning how to **use** the logger in your own application code.

**The built-in logger** is already configured and ready to use:

```python
z = zCLI({"logger": "INFO"})

# Use it in your code - no imports, no configuration needed
z.logger.info("Starting application initialization...")
z.logger.debug("Debug details: configuration loaded")
z.logger.warning("Rate limit approaching threshold")
z.logger.error("Failed to connect to external API")
```

**Key benefits:**

1. **No setup required** - No `import logging`, no `logging.getLogger()`, no handler configuration
2. **Already configured** - Console + file handlers set up based on your logger level
3. **Level-aware** - Respects the logger level you set via zSpark
4. **Production-ready** - Works seamlessly with PROD mode for clean console output

**Compare the output:**

With `logger: "INFO"`:
```
[2024-11-23 10:15:23] INFO     Starting application initialization...
[2024-11-23 10:15:23] INFO     Processing user data...
[2024-11-23 10:15:23] WARNING  Rate limit approaching threshold
[2024-11-23 10:15:23] ERROR    Failed to connect to external API
```

With `logger: "PROD"`:
```
# (Console silent, all logs go to file)
```

This demonstrates how **zSpark + z.logger** gives you a complete logging solution with **zero configuration overhead.**

---

### <span style="color:#8FBE6D">Demo 3: Custom Logger Methods - .dev() and .user()</span>

**Run it:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_user_demo.py
```

Building on basic logger usage, this demo introduces **two custom logger methods** designed for production applications that need clean, focused logging.

**The Problem:**

In production deployments, you want:
- ✅ Your application's important messages visible (startup, processing, completion)
- ❌ zCLI's internal system logs hidden (config loading, subsystem initialization, "Ready" banners)

**The Solution:**

```python
z = zCLI({"logger": "PROD"})

# Development diagnostics (hidden in PROD, shown in INFO+)
z.logger.dev("Cache hit rate: 87%")
z.logger.dev("Database query took 23ms")

# User application logs (ALWAYS visible, even in PROD)
z.logger.user("Application started successfully")
z.logger.user("Processing 1,247 records...")
z.logger.user("Application ready on port 8080")
```

**Method Comparison:**

| Method | INFO Mode | PROD Mode | Purpose |
|--------|-----------|-----------|---------|
| `.info()` | ✓ Shown | ✗ Hidden | System logs |
| `.warning()` | ✓ Shown | ✗ Hidden | System warnings |
| `.error()` | ✓ Shown | ✗ Hidden (console) | System errors |
| **`.dev()`** | **✓ Shown** | **✗ Hidden** | **Development diagnostics** |
| **`.user()`** | **✓ Shown** | **✓ SHOWN** | **User app messages** |

**PROD Mode Output (Clean!):**

```
Application started successfully
Processing 1,247 records...
Application ready on port 8080
```

**INFO Mode Output (Full visibility):**

```
[System initialization logs...]
═══════════════════════ zConfig Ready ═══════════════════════
[More system logs...]
Cache hit rate: 87%              ← .dev() message
Database query took 23ms         ← .dev() message
Application started successfully ← .user() message
Processing 1,247 records...      ← .user() message
Application ready on port 8080   ← .user() message
```

**When to use each:**

- **`.dev()`** - Internal diagnostics, performance metrics, debugging info you want during development but not in production
- **`.user()`** - Application lifecycle messages, business logic events, anything your users/operators need to see in production

This gives you **production-grade logging** with clean console output while maintaining full diagnostic capabilities during development.

---

### <span style="color:#8FBE6D">Demo 4: Automatic Exception Handling with zTraceback</span>

**Run it:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/ztraceback_demo.py
```

The final micro-step demonstrates **automatic exception interception** - the simplest way to add interactive error handling to your applications.

**The Magic:**

```python
z = zCLI({
    "logger": "PROD",       # Keep console clean
    "zTraceback": True,     # Enable automatic exception handling
})

# Just let errors happen - zTraceback catches them automatically!
result = handle_request()  # This will fail
```

**No try/except needed.** No manual error handling. Just enable `zTraceback: True` and any uncaught exception automatically launches an interactive menu.

**Interactive Menu:**

When an error occurs, you get:
- **View Details** - Error summary with location and context
- **Full Traceback** - Complete nested call stack

**What You See:**

```
# Triggering error (will be caught automatically)...
# No try/except needed!

zCrumbs:
  @.UI.zUI.zcli_sys.Traceback[~Root*]

  [0] ^View Details
  [1] ^Full Traceback
  [2] exit
```

**View Details Output:**

```
══════════════════════ Error Details ═══════════════════════
ZeroDivisionError: division by zero

Location:
  File: .../ztraceback_demo.py
  Line: 36
  Function: failing_operation()
──────────────────────── Context ────────────────────────────
  {
    "type": "ZeroDivisionError",
    "auto_caught": true
  }
```

**Full Traceback Output:**

Shows the complete 4-level nested call stack:
```
Traceback (most recent call last):
  File "ztraceback_demo.py", line 64, in <module>
    result = handle_request()
  File "ztraceback_demo.py", line 47, in handle_request
    return process_data(5)
  File "ztraceback_demo.py", line 41, in process_data
    result = failing_operation()
  File "ztraceback_demo.py", line 36, in failing_operation
    return 10 / 0
ZeroDivisionError: division by zero
```

**How It Works:**

1. **`zTraceback: True`** installs `sys.excepthook` during initialization
2. Any uncaught exception is automatically intercepted
3. Interactive menu launches instantly
4. Clean, scannable error display with full context

**Combined with PROD Mode:**

```python
z = zCLI({
    "logger": "PROD",       # Silent console
    "zTraceback": True,     # Interactive errors
})
```

This gives you:
- ✅ Clean console output (no system logs)
- ✅ Interactive error handling (when errors occur)
- ✅ Full diagnostic traces (in the interactive UI)
- ✅ Zero boilerplate (no try/except blocks)

**Perfect for:**
- Development debugging with clean output
- Production deployments with interactive error recovery
- Scripts that need robust error handling without verbose code

This is **the simplest entry point** to zCLI's interactive traceback system - just enable it and let it work.

---

### <span style="color:#8FBE6D">Next Steps</span>

Now that you understand zSpark logger control:

- **Level 3:** Workspace-specific settings with `.zEnv` files
- **Level 4:** Persistent preferences via `zConfig.environment.yaml`
- **Level 5:** Machine-specific overrides via `zConfig.machine.yaml`

But for most quick experiments and production deployments, **zSpark + logger level is all you need.**

---

### <span style="color:#8FBE6D">Key Takeaway</span>

**zSpark is your first line of control.**

Pass it to `zCLI()` to set logger level, mode, and other runtime settings **without touching any files.** This is the cleanest entry point for understanding configuration hierarchy - one setting, immediate results, no side effects.

