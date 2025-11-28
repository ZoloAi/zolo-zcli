# Level 0: Hello zConfig

**Initialize zCLI - that's it.**

## Run it

```bash
python3 Demos/Layer_0/zConfig_Demo/Level_1_Hello/1_initialize.py
```

## What it does

```python
from zCLI import zCLI

z = zCLI()
```

**That one line initializes all 18 subsystems.**

When you run this demo, watch your terminal—you'll see each subsystem initialize in order:
- zConfig detects your machine, OS, browser, IDE
- Creates config folders in OS-native directories
- Loads the 5-layer hierarchy (defaults → machine → environment → env vars → session)
- Initializes logger and session
- Prepares all other subsystems

**Zero configuration. Zero boilerplate. One line.**

## Next Steps

- **Level 1 (Get)**: Learn how to read machine, environment, and session values
- **Level 2 (zSettings)**: Configure logger, zSpark, and advanced settings

