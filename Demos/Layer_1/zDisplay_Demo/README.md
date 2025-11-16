# Layer 0: Terminal Tutorial

**<span style="color:#8FBE6D">Learn zCLI fundamentals—Terminal only, no browser required!</span>**

This tutorial introduces you to zCLI's Layer 0 (Foundation) subsystems through hands-on Terminal examples. No WebSocket, no web browser, no complex setup—just pure Terminal goodness.

## What You'll Learn

1. **<span style="color:#8FBE6D">Level 0: Hello zCLI</span>** - Your first zCLI program (3 lines!)
2. **<span style="color:#F8961F">Level 1: Display & Signals</span>** - Output text, tables, and feedback
3. **<span style="color:#00D4FF">Level 2: Config & Paths</span>** - Read config files and resolve paths
4. **<span style="color:#EA7171">Level 3: User Input</span>** - Collect input and validate data

## Prerequisites

```bash
# Just zCLI installed
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# Verify
zolo --version
```

## Structure

Each level is a standalone Python script you can run immediately:

```
Terminal_Tutorial/
├── Level_0_Hello/
│   ├── hello.py          # Your first zCLI program
│   └── README.md         # Step-by-step guide
├── Level_1_Display/
│   ├── display_demo.py   # Text, tables, signals
│   └── README.md
├── Level_2_Config/
│   ├── config_demo.py    # Configuration hierarchy
│   ├── .zEnv             # Environment variables
│   └── README.md
├── Level_3_Input/
│   ├── input_demo.py     # User input & validation
│   └── README.md
└── README.md             # You are here!
```

## How to Use This Tutorial

**Option 1: Sequential Learning (Recommended)**
- Start with Level 0 and work your way up
- Each level builds on the previous
- Takes ~30 minutes total

**Option 2: Jump to What You Need**
- Need output? → Level 1 (Display)
- Need config? → Level 2 (Config)
- Need input? → Level 3 (Input)

## What Makes This "Layer 0"?

**Layer 0** in zCLI means **Foundation** - the core subsystems everything else depends on:

- **<span style="color:#8FBE6D">zConfig</span>**: Configuration & paths
- **<span style="color:#F8961F">zDisplay</span>**: Output & rendering
- **<span style="color:#00D4FF">zComm</span>**: Communication (HTTP client, services)

These three subsystems power the entire zCLI framework. Master them and you'll understand how the magic works!

## The zCLI Philosophy

> **<span style="color:#F8961F">Declare once—run everywhere.</span>**

This tutorial teaches you to write code that:
- ✅ Works in Terminal immediately
- ✅ Works in GUI (zBifrost) without changes
- ✅ Is declarative (describe WHAT, not HOW)
- ✅ Is minimal (no boilerplate)

**Example:**
```python
z.display.table(data, headers=["Name", "Email"])
```

This works in Terminal (ANSI table) AND in a browser (HTML table). Same code. Zero changes.

## After This Tutorial

Once you complete Layer 0, you'll be ready for:

- **<span style="color:#F8961F">Layer 1</span>** (Core Services): zAuth, zDispatch, zNavigation, zParser, zLoader, zUtils
- **<span style="color:#EA7171">Layer 2</span>** (Business Logic): zFunc, zDialog, zOpen, zWizard, zData
- **<span style="color:#AE84D3">Layer 3</span>** (Orchestration): zShell, zWalker, zServer

But first, let's master the foundation!

---

**Ready?** → Start with [Level 0: Hello zCLI](Level_0_Hello/README.md)

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: ~30 minutes  
**Mode**: Terminal only

