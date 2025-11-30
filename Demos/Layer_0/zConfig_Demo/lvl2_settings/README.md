# Level 2: zSettings - Logger & Error Handling

**Goal:** Learn to use zCLI's built-in logger through hands-on experience, mastering the dual logger architecture and discovering the unique PROD level.

## Learning Flow

This level follows a **learn-by-doing** approach:
1. **Use the logger** → Experience it working (5 standard levels)
2. **Customize everything** → Directory, filename, level overrides
3. **Discover PROD level** → zCLI's unique 6th level (silent console + DEBUG file)
4. **Error handling** → Automatic exceptions

## Demos

### 1. Logger Basics (`1_logger_basics.py`)
**Action:** Use the built-in logger with Production deployment.

```python
zSpark = {
    "deployment": "Production",  # Minimal console output
    "logger": "INFO",  # But with INFO logging
}
z = zCLI(zSpark)

z.logger.debug("DEBUG: Detailed diagnostics")
z.logger.info("INFO: Application status")
z.logger.warning("WARNING: Needs attention")
z.logger.error("ERROR: Something failed")
z.logger.critical("CRITICAL: System failure")
```

**Discovery:**
- Five standard log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Logs appear in console AND file automatically
- Two separate loggers: `z.logger` (app) + `z.logger.framework` (internal)
- App logs: `zcli-app.log` in zCLI support folder
- Framework logs: `zcli-framework.log` (automatic, transparent)

---

### 2. Advanced Control (`2_logger_advanced.py`)
**Action:** Take full control: custom directory and filename.

```python
zSpark = {
    "deployment": "Production",  # No banners/sysmsg
    "title": "my-production-api",  # Filename: my-production-api.log
    "logger": "INFO",  # Override Production default (ERROR)
    "logger_path": "./logs",  # Directory: ./logs/
}
z = zCLI(zSpark)
# Result: ./logs/my-production-api.log
```

**Discovery:**
- `logger_path` = WHERE (directory)
- `title` = WHAT (filename)
- Result: `logger_path/title.log`
- Clean separation of concerns

---

### 3. Logger PROD (`3_logger_prod.py`) ⭐ NEW
**Action:** Discover the 6th logger level (zCLI innovation).

```python
zSpark = {
    "deployment": "Production",
    "title": "my-production-api",  # Custom log filename
    "logger": "PROD",  # The special 6th level!
    "logger_path": "./logs",  # Custom directory
    "zTraceback": True,  # Error handling enabled
}
z = zCLI(zSpark)

z.logger.info("API started")  # Silent in console, DEBUG in file
z.logger.debug("Cache initialized")  # Also silent, but logged
```

**Discovery:**
- PROD is NOT a standard Python log level (zCLI innovation)
- Console: Completely silent (zero output)
- File: DEBUG level (captures everything)
- Perfect for: APIs, microservices, daemons
- All 6 log messages captured, even DEBUG

---

### 4. zTraceback (`4_ztraceback.py`)
**Action:** Enable automatic exception handling with clean UI.

```python
zSpark = {
    "deployment": "Production",  # Clean zTraceback UI (no framework noise)
    "title": "my-production-api",
    "logger": "INFO",
    "logger_path": "./logs",
    "zTraceback": True,  # Enable automatic exception handling
}
z = zCLI(zSpark)

# Nested calls to demonstrate traceback depth
level_1()  # → level_2() → level_3() → ERROR (interactive menu launches!)
```

**Discovery:**
- No try/except needed - automatic error interception!
- Interactive menu with error details and full traceback
- Production deployment keeps the UI clean
- Perfect for development debugging

---

## Key Concepts

- **Dual logger architecture** - `z.logger` (your app) + `z.logger.framework` (internal zCLI)
- **App log files** - Default: `{script_name}.log` or custom via `title` parameter
- **Framework logs** - Always separate in `zcli-framework.log` (transparent, non-configurable)
- **Six logger levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL, **PROD** (zCLI innovation)
- **PROD level** - Unique feature: silent console, DEBUG to file (for production services)
- **Smart defaults** - Production→ERROR, Development/Testing→INFO (unless overridden)
- **Separation of concerns** - `deployment` (framework behavior) ≠ `logger` (app logs) ≠ `logger_path` (where)
- **Full customization** - `title` (filename), `logger_path` (directory), `logger` (level)
- **zTraceback: True** - Automatic exception handling with interactive menu
- **Clean debugging** - Production deployment + zTraceback = clean error UI (no framework noise)

## Pedagogical Approach

**We teach by DOING first, EXPLAINING second:**

1. ✅ **Use it** (Demo 1) - Five standard levels, dual logger architecture
2. ✅ **Customize it** (Demo 2) - Full control: `title`, `logger_path`, `logger` override
3. ✅ **Discover PROD** (Demo 3) - zCLI's unique 6th level (silent console, DEBUG file)
4. ✅ **Handle errors** (Demo 4) - Automatic exception handling with clean UI

**Progression:**
- Demo 1: Learn the basics (5 levels, see them work)
- Demo 2: Take control (customize where and what)
- Demo 3: Discover innovation (PROD = silent production)
- Demo 4: Debug automatically (no try/except needed)

This follows zCLI's philosophy: Start with familiar patterns, gradually reveal the power.

## What's Next?

**→ Level 3 (Get):** Learn to read machine, environment, and session configuration values

