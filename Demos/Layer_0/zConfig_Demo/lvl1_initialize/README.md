# Level 1: Initialize - Getting Started with zCLI

**Goal:** Learn the basics of zCLI initialization and configuration entry point (zSpark).

## Demos

### 1. Initialize (`1_initialize.py`)
Basic zCLI initialization - one line does everything.

```python
z = zCLI()  # Auto-detects machine, loads configs, initializes logger
```

**Run:**
```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/1_initialize.py
```

---

### 2. zSpark - Production Mode (`2_zspark.py`)
Use zSpark to override configuration at runtime (highest priority).

```python
zSpark = {"deployment": "Production"}  # Silent mode
z = zCLI(zSpark)
```

**Run:**
```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/2_zspark.py
```

---

### 3. Deployment Modes Comparison (`3_deployment_modes.py`) ⭐
Experience all three deployment modes side-by-side.

```python
# Compare: Development vs Testing vs Production
show_mode("Development")  # Full output
show_mode("Testing")      # Clean logs only
show_mode("Production")   # Minimal
```

**Run:**
```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment_modes.py
```

---

## Key Concepts

- **zCLI()** - One-line initialization
- **zSpark** - Runtime configuration override (highest priority)
- **deployment** - Controls environment behavior:
  - `Development` - Full output (banners + INFO logs)
  - `Testing` - Clean logs only (no banners, INFO logs)
  - `Production` - Minimal (no banners, ERROR logs)

## What's Next?

**→ Level 2 (zSettings):** Learn about logger configuration and smart defaults
