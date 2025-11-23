## zConfig Demo (Layer 0)

Micro-step tutorials for the zConfig subsystem. Start at Level 0 and work your way up.

### Level 0 — `Level_0_Hello/hello_config.py`
- Initialize zCLI (zConfig loads automatically).
- Read the machine hostname and current deployment.
- Print the active workspace path.
- **Run:** `python Demos/Layer_0/zConfig_Demo/Level_0_Hello/hello_config.py`

### Level 1 — `Level_1_Get/`
- `zmachine_get.py`: Show all zMachine values via `z.config.get_machine()`.
- `zenv_get.py`: Show all environment values via `z.config.get_environment()`.
- Copy/paste-ready accessor lines for diagnostics.
- **Run:**  
  - `python Demos/Layer_0/zConfig_Demo/Level_1_Get/zmachine_get.py`  
  - `python Demos/Layer_0/zConfig_Demo/Level_1_Get/zenv_get.py`

### Level 2 — `Level_2_zSpark/`
- `zspark_demo.py`: Guided walkthrough of zSpark overrides (custom `.zEnv`, custom workspace).
- `demo_env.zEnv`: Local .zEnv used only by the demo.
- **Run:**  
  - `python Demos/Layer_0/zConfig_Demo/Level_2_zSpark/zspark_demo.py`

### Level 3 — `simple_inventory_demo.py`
- Standalone shell that loads only zConfig (no other subsystems).
- Reads `.zEnv` automatically (no python-dotenv import needed).
- Detects machine info (hostname, OS, preferred IDE).
- Prints a simple “low stock” summary using values from `.zEnv`.
- **Run:** `python Demos/Layer_0/zConfig_Demo/simple_inventory_demo.py`

### Required file
- `.zEnv` (example included) defines deployment-specific settings used by the demos.

