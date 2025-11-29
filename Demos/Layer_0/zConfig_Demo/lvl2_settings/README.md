# Level 2: zSettings - Logger & Error Handling

**Goal:** Learn to use zCLI's built-in logger through hands-on experience, discovering the relationship between deployment and logging.

## Learning Flow

This level follows a **learn-by-doing** approach:
1. **Use the logger** → Experience it working
2. **Compare modes** → Discover smart defaults
3. **Override defaults** → Understand independence
4. **Deployment-aware methods** → Advanced techniques
5. **Error handling** → Automatic exceptions

## Demos

### 1. Logger Basics (`1_logger_basics.py`)
**Action:** Use the built-in logger in your application code.

```python
zSpark = {"deployment": "Development"}
z = zCLI(zSpark)

z.logger.info("Application started")
z.logger.warning("Rate limit approaching")
z.logger.error("Connection failed")
```

**Discovery:** Logger works out of the box, no imports needed!

---

### 2. Smart Defaults (`2_smart_defaults.py`) ⭐ NEW
**Action:** Run the same code with Development vs Production.

```python
# Compares side-by-side:
demo_with_deployment("Development")       # → INFO logging
demo_with_deployment("Production")  # → ERROR logging
```

**Discovery:** Deployment mode automatically sets logger defaults!
- Development → INFO (show details)
- Production → ERROR (minimal output)

**Key Insight:** They're separate concerns but work together intelligently.

---

### 3. Logger Override (`3_logger_override.py`)
**Action:** Override smart defaults when you need different behavior.

```python
# Production behavior + DEBUG logging (troubleshooting)
zSpark = {
    "deployment": "Production",
    "logger": "DEBUG",
}
z = zCLI(zSpark)
```

**Discovery:** Deployment and logger are INDEPENDENT - mix them however you need!

---

### 4. Logger Methods (`4_logger_methods.py`)
**Action:** Learn deployment-aware logging methods.

```python
zSpark = {"deployment": "Production"}
z = zCLI(zSpark)

z.logger.dev("Cache hit rate: 87%")        # Hidden in Production
z.logger.user("Processing 1,247 records")  # Always visible
```

**Discovery:** These methods check deployment mode, not log level!

---

### 5. zTraceback (`5_ztraceback.py`)
**Action:** Enable automatic exception handling.

```python
zSpark = {
    "deployment": "Production",
    "zTraceback": True,
}
z = zCLI(zSpark)

result = handle_request()  # Errors launch interactive menu
```

**Discovery:** No try/except needed - automatic error interception!

---

## Key Concepts

- **z.logger** - Pre-configured Python logger (no imports)
- **Smart defaults** - Deployment modes set intelligent logger defaults
- **Separation of concerns** - Deployment (behavior) ≠ Logger (verbosity)
- **Independent control** - Override either one as needed
- **.dev() / .user()** - Deployment-aware logging methods
- **zTraceback: True** - Automatic exception handling

## Pedagogical Approach

**We teach by DOING first, EXPLAINING second:**

1. ✅ Use it (Demo 1)
2. ✅ Experience the relationship (Demo 2)
3. ✅ Understand independence (Demo 3)
4. ✅ Master advanced techniques (Demos 4-5)

This follows zCLI's philosophy: Start with familiar patterns, gradually reveal the declarative power.

## What's Next?

**→ Level 3 (Get):** Learn to read machine, environment, and session configuration values

