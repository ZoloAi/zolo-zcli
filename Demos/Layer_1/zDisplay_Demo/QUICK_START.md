# Quick Start: Terminal Tutorial

**<span style="color:#8FBE6D">Get started with zCLI in 5 minutes!</span>**

## Prerequisites

```bash
# Install zCLI
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# Verify installation
zolo --version
```

## Run Level 0: Hello zCLI

```bash
cd Demos/Layer_0/Terminal_Tutorial/Level_0_Hello
python3 hello.py
```

You should see:
```
✅ Hello from zCLI!
ℹ️  Mode: Terminal
ℹ️  Workspace: /path/to/Terminal_Tutorial/Level_0_Hello
ℹ️  Deployment: Debug

Available subsystems:
  • z.config   - Configuration management
  • z.display  - Output & rendering
  • z.comm     - HTTP client & services
  ...
✨ All subsystems loaded and ready!
```

**Congratulations!** You just ran your first zCLI program!

## Next Steps

### Level 1: Display & Signals (10 minutes)
Learn about tables, lists, and formatted output:
```bash
cd ../Level_1_Display
python3 display_demo.py
```

### Level 2: Config & Paths (10 minutes)
Learn about configuration and path resolution:
```bash
cd ../Level_2_Config
python3 config_demo.py
```

### Level 3: User Input (15 minutes)
Learn about collecting user input:
```bash
cd ../Level_3_Input
python3 input_demo.py
```

## What You'll Learn

- **Level 0**: Initialization and basics (3 lines of code!)
- **Level 1**: Tables, lists, progress bars, and signals
- **Level 2**: Configuration hierarchy and path resolution
- **Level 3**: User input, selections, and menus

## Total Time: ~30 minutes

## After the Tutorial

Once you complete all levels, you'll understand:
- ✅ How to initialize zCLI (zero-config)
- ✅ How to display data (tables, lists, JSON)
- ✅ How to read configuration (machine, environment, .zEnv)
- ✅ How to collect user input (strings, passwords, selections)

**Ready for more?**
- Try zBifrost: Turn Terminal apps into web GUIs
- Learn zWalker: Build UIs from YAML
- Explore zData: Database operations
- Build a real app: Combine all layers

---

**Version**: 1.5.5  
**Mode**: Terminal only  
**Prerequisites**: Python 3.8+  
**Difficulty**: Beginner

