## Level 1 Demo: zMachine / zEnv / zSession Get

Once you've seen the initialization, the next micro-step is learning how to retrieve those machine, environment, and session values on demand.  
`Demos/Layer_0/zConfig_Demo/Level_1_Get/` contains three scripts (`zmachine_get.py`, `zenv_get.py`, `zsession_get.py`) that are **only** about reading `z.config.get_machine()` / `z.config.get_environment()` / `z.session` and copying those access lines into your own code.

**Run them:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_1_Get/zmachine_get.py
python3 Demos/Layer_0/zConfig_Demo/Level_1_Get/zenv_get.py
python3 Demos/Layer_0/zConfig_Demo/Level_1_Get/zsession_get.py
```

> <span style="color:#8FBE6D">**Level 1A: zMachine Get**</span>

#### 1. Grab the machine dict

```python
z = zCLI()
machine = z.config.get_machine()  # Returns the entire zMachine payload
```

### 2. Copy/paste-ready getters

```python
print("OS:", machine.get("os"))
print("Host:", machine.get("hostname"))
print("Browser:", machine.get("browser"))
print("IDE:", machine.get("ide"))
print("Terminal:", machine.get("terminal"))
print("Shell:", machine.get("shell"))
print("CPU cores:", machine.get("cpu_cores"))
print("Memory (GB):", machine.get("memory_gb"))
print("Python version:", machine.get("python_version"))
```

Need a single value without caching the dict? Use the built-in getter directly:

```python
hostname = z.config.get_machine("hostname")
```

The Level 1 demo prints **every available key** in this format so you can copy/paste the lines you need (e.g., for diagnostics, telemetry, or conditional logic).  
Need deployment/logging/network values instead? Run `zenv_get.py` in the same folder to mirror this flow for `z.config.get_environment()`.  
Want to see runtime session state? Run `zsession_get.py` to access `z.session` values.

> <span style="color:#8FBE6D">**Level 1B: zEnv Get**</span>

`Demos/Layer_0/zConfig_Demo/Level_1_Get/zenv_get.py` mirrors the same idea for environment settings.

```python
env = z.config.get_environment()

print("Deployment:", env.get("deployment"))
print("Log level:", env.get("logging", {}).get("level"))
print("Network host:", env.get("network", {}).get("host"))
print("WebSocket port:", env.get("websocket", {}).get("port"))
```

Same philosophy: fetch once, print the fields you care about, or call  
`z.config.get_environment("deployment")` directly when you only need a single value.

> <span style="color:#8FBE6D">**Level 1C: zSession Get**</span>

`Demos/Layer_0/zConfig_Demo/Level_1_Get/zsession_get.py` shows how to access runtime session values that are influenced by zSpark and zConfig initialization.

```python
session = z.session

print("zS_id:", session.get("zS_id"))
print("zSpace:", session.get("zSpace"))
print("zMode:", session.get("zMode"))
print("zLogger:", session.get("zLogger"))
print("zTraceback:", session.get("zTraceback"))
print("zSpark:", session.get("zSpark"))
print("zVars:", session.get("zVars"))
```

The session contains runtime state created during zCLI initialization. Values like `zMode` and `zSpace` can be overridden via `zSpark_obj` when creating the zCLI instance, while others (like `zS_id`) are auto-generated per session.
