# 🏗️ Foundation Layer Demo

> **Philosophy:** "Seed the Demo, Let It Grow"  
> Start simple, build complexity naturally. Each demo catches bugs and proves patterns.

## Overview

This demo covers **DEMO_PLAN items 1.1-1.4** (Foundation Layer):

| Demo | Name | Subsystems | Time |
|------|------|-----------|------|
| **1.1** | Display Basics | zDisplay, zConfig | 10 min |
| **1.2** | Navigation | zNavigation, zDispatch | 15 min |
| **1.3** | Nested Menus | zNavigation, zDispatch | 15 min |
| **1.4** | Path Resolution | zParser, zLoader, zConfig | 10 min |

**Total Time:** ~50 minutes  
**Coverage:** 6 subsystems tested

---

## What It Demonstrates

### ✅ zDisplay (Demo 1.1)
- All core display events: `text`, `header`, `success`, `error`, `warning`, `info`
- Event styling and indentation
- zTheme CSS integration
- Line separators

### ✅ zNavigation (Demos 1.2, 1.3)
- Declarative menus with `~Root*`
- Automatic numbering (0, 1, 2, ...)
- Nested menu structures
- Breadcrumb tracking (zCrumbs)
- `^` modifier for bounce-back navigation

### ✅ zDispatch (All Demos)
- Command routing
- Modifier handling (`^` for navigation)
- Event dispatching to subsystems

### ✅ zParser (Demo 1.4)
- Path prefix resolution:
  - `@.` - Workspace prefix
  - `~.` - Home/AppSupport prefix
  - `$.` - System prefix
- Automatic file extension handling (`.yaml`)

### ✅ zLinks (Throughout)
- Intra-file navigation jumps
- zBlock delta targeting
- Menu navigation shortcuts

### ✅ zBlock Deltas (Bonus)
- Multiple entry points in one zUI file
- `zVaF` (main entry point)
- `zBlock.AlternatePath` (alternate menu)
- `zBlock.ThemeTest` (style testing)

---

## File Structure

```
01_Foundation/
├── foundation_walker.py          # Main demo launcher (3 steps pattern)
├── zUI.foundation_demo.yaml      # Complete demo zUI (declarative)
└── README.md                     # This file
```

**Philosophy in Action:**
- **1 Python file** (minimal imperative code)
- **1 YAML file** (all logic and structure)
- **0 helper scripts** (pure zKernel patterns)

---

## Usage

### Basic Usage (Terminal Mode)

```bash
# Run the main demo
python foundation_walker.py

# Interactive menu flow:
#   1. Select "1.1 Display Basics" → See all display events
#   2. Select "1.2 Navigation Demo" → Learn about ~Root*
#   3. Select "1.3 Nested Menus" → Navigate through levels
#   4. Select "1.4 Path Resolution" → Understand @. ~. $.
#   5. Select "Jump to zBlock Delta" → See alternate entry point
```

### Alternate Entry Points

```bash
# Jump directly to alternate path
python foundation_walker.py --block AlternatePath

# Jump to theme testing
python foundation_walker.py --block ThemeTest

# Show help
python foundation_walker.py --help
```

### Using zcli CLI

```bash
# If zKernel is installed globally
zcli --file @.zUI.foundation_demo --block zVaF
```

---

## What Each Demo Tests

### 1.1 Display Basics ✅
**Tests:**
- `zDisplay.text()` - Plain text output
- `zDisplay.header()` - Section headers
- `zDisplay.success()` - Success messages
- `zDisplay.error()` - Error messages
- `zDisplay.warning()` - Warning messages
- `zDisplay.info()` - Info messages
- `zDisplay.line()` - Visual separators

**Catches:**
- zTheme CSS loading failures
- Font path issues
- Terminal vs zBifrost rendering differences
- Style application errors

### 1.2 Navigation Demo ✅
**Tests:**
- `~Root*` pattern (declarative menu)
- Automatic menu numbering
- zDispatch command routing
- Selection handling

**Catches:**
- Menu parsing errors
- Navigation state issues
- zDispatch routing failures
- Stop command handling

### 1.3 Nested Menus ✅
**Tests:**
- Multi-level menu hierarchies
- Breadcrumb generation (zCrumbs)
- `^` modifier for bounce-back
- Navigation stack management

**Catches:**
- zCrumbs state corruption
- Deep navigation issues
- Back-button failures
- zLink navigation errors

### 1.4 Path Resolution ✅
**Tests:**
- `@.` workspace prefix
- `~.` home/AppSupport prefix
- `$.` system prefix
- Automatic `.yaml` extension

**Catches:**
- zParser path resolution bugs
- zLoader file loading errors
- zConfig path detection failures
- Cross-platform path issues (macOS/Linux/Windows)

---

## Design Philosophy

### Intention Precedes Implementation

This demo is **declarative-first**:

```yaml
# Traditional Approach (Imperative)
# - Write Python functions
# - Create menu loop
# - Handle input parsing
# - Display formatted output
# Total: ~300 lines of code

# zKernel Approach (Declarative)
~Root*: ["Option 1", "Option 2", "stop"]

Option 1:
  zDisplay:
    event: text
    content: "Hello World!"
# Total: 10 lines of YAML
```

**The YAML *is* the application, not just configuration.**

### Structure Guides Logic

The zUI file structure mirrors the user's mental model:

1. **Root Menu** → Top-level choices
2. **Nested Menus** → Sub-categories
3. **Actions** → What happens when selected

No translation layer needed - what you declare is what runs.

### Evolution Over Rewrite

Need to add a new menu item? Just add one line to the array:

```yaml
# Before
~Root*: ["Option 1", "Option 2", "stop"]

# After (evolutionary change)
~Root*: ["Option 1", "Option 2", "Option 3", "stop"]
```

No code refactoring required.

---

## Expected Output

### Terminal Mode (Sample)

```
════════════════════════════════════════════════════════════════════════════════
🏗️  Foundation Layer Demo - zKernel v1.5.4
════════════════════════════════════════════════════════════════════════════════

Philosophy: 'Seed the Demo, Let It Grow'
Testing: Display, Navigation, Nested Menus, Path Resolution
────────────────────────────────────────────────────────────────────────────────

Select option:

  0) 1.1 Display Basics
  1) 1.2 Navigation Demo
  2) 1.3 Nested Menus
  3) 1.4 Path Resolution
  4) Jump to zBlock Delta
  5) stop

Enter choice (0-5): 0

════════════════════════════════════════════════════════════════════════════════
🎨 Demo 1.1: Display Basics
════════════════════════════════════════════════════════════════════════════════

  Testing core zDisplay events. Each event type has distinct visual styling.
  
  ✅ SUCCESS event: Operation completed successfully
  ❌ ERROR event: Something went wrong (just a demo!)
  ⚠️  WARNING event: Proceed with caution
  ℹ️  INFO event: Informational message

────────────────────────────────────────────────────────────────────────────────
  ✨ All core display events tested! zTheme styling applied.

[Returns to menu...]
```

---

## Success Criteria

### ✅ Demo Passes If:

1. **All display events render correctly** (1.1)
   - Text appears with proper styling
   - Headers are prominent
   - Colors are applied (success=green, error=red, etc.)

2. **Menus are auto-generated** (1.2)
   - Numbers appear (0, 1, 2, ...)
   - Selection works
   - "stop" command exits cleanly

3. **Nested navigation works** (1.3)
   - Can navigate through 3 levels
   - Breadcrumbs show path
   - `^` modifier bounces back
   - zLinks jump correctly

4. **Path resolution is explained** (1.4)
   - All three prefixes documented (@. ~. $.)
   - Examples are clear
   - User understands when to use each

5. **zBlock deltas function** (Bonus)
   - Can jump to alternate entry point
   - Navigation between blocks works
   - Multiple menus in one file

---

## Bugs This Demo Catches

### Known Issues (from previous demos):

1. **Terminal blocking in zBifrost mode** ✅ FIXED
   - Root cause: `display.text()` missing `break_after=False`
   - Fixed in: `dispatch_launcher.py` line 548

2. **zTheme CSS loading failures**
   - Symptoms: No colors, broken formatting
   - Tests: All display events check theme application

3. **zCrumbs state corruption**
   - Symptoms: Wrong breadcrumb path
   - Tests: Multi-level navigation with repeated traversal

4. **zParser path resolution on Windows**
   - Symptoms: Path separators fail (\ vs /)
   - Tests: All three prefix types (@. ~. $.)

---

## Next Steps

After completing the Foundation Layer, proceed to:

**LEVEL 2: Data & Logic Layer**
- Demo 2.1: CRUD Operations (zData)
- Demo 2.2: Plugin Functions (zFunc)
- Demo 2.3: Multi-Step Workflow (zWizard)
- Demo 2.4: Interactive Forms (zDialog)

See `../DEMO_PLAN.html` for full roadmap.

---

## Philosophy Reference

> *"The chair isn't built then used. The chair becomes when you intend to sit."*
> 
> — **zPhilosophy.md**

This demo embodies:
- **Intention first** - Declare what you want (menus, display)
- **Structure guides** - YAML defines the application
- **Evolution** - Add features by adding lines, not rewriting code

**For more:** See `Documentation/zPhilosophy.md`

---

**Version:** 1.5.4  
**Created:** 2025-11-09  
**Status:** ✅ Ready for testing  
**Coverage:** 6 subsystems (zDisplay, zNavigation, zDispatch, zParser, zLoader, zConfig)

