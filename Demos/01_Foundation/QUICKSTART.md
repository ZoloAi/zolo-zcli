# 🏗️ Foundation Layer - Quick Start

## Run the Demo

```bash
cd Demos/01_Foundation
python3 foundation_walker.py
```

## What You'll See

```
zCrumbs:
  @.zUI.foundation_demo.zVaF[~Root*]

  [0] ^1.1 Display Basics
  [1] ^1.2 Navigation Demo
  [2] ^1.3 Nested Menus
  [3] ^1.4 Path Resolution
  [4] ^Jump to zBlock Delta
  [5] stop
```

## Test Each Feature

| Option | Feature | Tests |
|--------|---------|-------|
| **0** | Display Basics | All zDisplay events (header, text, success, error, warning, info, line) |
| **1** | Navigation | Declarative `~Root*` menus, auto-numbering, zDispatch routing |
| **2** | Nested Menus | Multi-level navigation, breadcrumbs, `^` bounce-back |
| **3** | Path Resolution | `@.` workspace, `~.` home, `$.` system prefixes |
| **4** | zBlock Delta | Intra-file navigation, multiple entry points |
| **5** | stop | Exit the demo |

## Files Created

- `foundation_walker.py` - **12 lines** (3-step spark pattern)
- `zUI.foundation_demo.yaml` - Complete declarative UI
- `README.md` - Full documentation
- `QUICKSTART.md` - This file

## Philosophy

**"Seed the Demo, Let It Grow"**

- ✅ Intention precedes implementation (declare in YAML first)
- ✅ Structure guides logic (no imperative loops needed)
- ✅ Evolution over rewrite (add features by adding YAML lines)

## Coverage

**6 Subsystems Tested:**
- zDisplay (all core events)
- zNavigation (~Root*, nested menus, breadcrumbs)
- zDispatch (routing, modifiers)
- zParser (path resolution)
- zLoader (file loading)
- zConfig (workspace detection)

**Time:** ~10 min to run all options  
**Bugs Caught:** Display rendering, navigation state, path resolution

---

✨ **Next:** Level 2 - Data & Logic Layer (zData, zFunc, zWizard, zDialog)

