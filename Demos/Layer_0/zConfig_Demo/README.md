## zConfig Demo (Layer 0)

Standalone example that loads **only** the zConfig subsystem (`Demos/Layer_0/zConfig_Demo/`).

### `simple_inventory_demo.py`
- Reads `.zEnv` automatically (no python-dotenv import needed).
- Detects machine info (hostname, OS, preferred IDE).
- Prints a simple “low stock” summary using values from `.zEnv`.

### Required file
- `.zEnv` (example included) defines deployment-specific settings used by the demo.

