## Level 2 Demo: zSpark Logger Control

This demo introduces **zSpark** as the first entry point for runtime configuration.  
Its purpose is to show how to control logger level **before** any YAML files or environment variables are loaded.

**Run it:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py
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

