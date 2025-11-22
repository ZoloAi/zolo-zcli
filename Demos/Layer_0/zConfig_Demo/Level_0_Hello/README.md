## Level 0 Demo: Hello zConfig

The first demo is intentionally minimal.  
Its purpose is to show what happens the moment you initialize zCLI.

**Run it:**
```bash
python3 Demos/Layer_0/zConfig_Demo/Level_0_Hello/hello_config.py
```

### <span style="color:#8FBE6D">1. Importing zCLI</span>
Once you've installed the package, the `zCLI` module will be available for import in your Python environment.

```python
from zCLI import zCLI
```

> For detailed installation instructions and troubleshooting, see [@Documentation/INSTALL.md](INSTALL.md).

**Importing zCLI does not start any subsystem yet.**  
It simply makes the framework available in your environment.

### <span style="color:#8FBE6D">2. Creating a zCLI Instance</span>

```python
z = zCLI()
```

**This line is the core of zConfig_Demo/Level_0_Hello.**

The moment you call `zCLI()`:

- <span style="color:#F8961F">zConfig initializes automatically</span> and validates your config input (zSpark) before touching disk  
- It builds the path resolver and ensures your OS-native support folders exist:
  - **macOS:** `~/Library/Application Support/zolo-zcli/zConfigs`
  - **Linux:** `~/.config/zolo-zcli/zConfigs`
  - **Windows:** `%APPDATA%\zolo-zcli\zConfigs`
  
  Corresponding `zUIs/` and `logs/` directories are also prepared.  
  Machine and environment YAML files are then loaded, creating first-run defaults if missing.
- `SessionConfig` starts the runtime session, creates the logger, wires `zTraceback`, and attaches everything back onto the zCLI instance  
- WebSocket and HTTP config objects are prepared so later subsystems can rely on them with **no YAML, no dotenv, and no manual setup**

### <span style="color:#8FBE6D">3. Reading Built-In Values</span>

The Level 0 demo then reads:

- a <span style="color:#F8961F">machine property</span>  
  (`z.config.get_machine("hostname")`)  
- an <span style="color:#F8961F">environment property</span>  
  (`z.config.environment.get("deployment", "Debug")`)  
- the <span style="color:#F8961F">workspace directory</span>  
  (`z.config.sys_paths.workspace_dir`)  

All of these values exist **before** you create any files or write any settings.  
They are part of zConfig’s built-in structure.

