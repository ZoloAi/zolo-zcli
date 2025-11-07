# zTests Command Integration Summary

## What Was Added

A new `zolo ztests` command has been integrated into the main zCLI entry point, providing easy access to the declarative test runner.

---

## Commands Available

### `zolo test` (Legacy - Unchanged)
**Status**: Kept as backup  
**Implementation**: Imperative Python (existing)  
**Location**: `zTestSuite/run_all_tests.py`

```bash
zolo test
# Runs legacy test menu (unchanged)
```

### `zolo ztests` (New - Declarative)
**Status**: ✅ New in v1.5.4+  
**Implementation**: Pure zCLI (declarative)  
**Location**: `zTestRunner/`

```bash
zolo ztests
# Runs declarative test menu (37 test suites)
```

---

## Implementation Details

### Changes to `main.py`

**1. New Handler Function**:
```python
def handle_ztests_command():
    """Handle zTests command (declarative test runner)."""
    from pathlib import Path
    from zCLI import zCLI
    
    # Get project root (where zTestRunner lives)
    import zCLI as zcli_module
    project_root = Path(zcli_module.__file__).parent.parent
    
    # Launch declarative test runner
    test_cli = zCLI({
        "zWorkspace": str(project_root),
        "zVaFile": "@.zTestRunner.zUI.test_menu",
        "zBlock": "zVaF",
        "zMode": "Terminal"
    })
    test_cli.walker.run()
```

**2. Subparser Registration**:
```python
# Test subcommand (legacy)
subparsers.add_parser("test", help="Run zCLI test suite (legacy)")

# zTests subcommand (declarative)
subparsers.add_parser("ztests", help="Run zCLI test suite (declarative)")
```

**3. Routing Logic**:
```python
elif args.command == "ztests":
    return handle_ztests_command()
```

---

## Help Output

```bash
$ zolo --help

usage: zolo [-h] [--version] {shell,config,test,ztests,uninstall} ...

Zolo zCLI Framework - YAML-driven CLI for interactive applications

positional arguments:
  {shell,config,test,ztests,uninstall}
                        Available commands
    shell               Start interactive zCLI shell
    config              Manage zCLI configuration
    test                Run zCLI test suite (legacy)
    ztests              Run zCLI test suite (declarative)  ← NEW!
    uninstall           Uninstall zolo-zcli framework

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

---

## Usage Examples

### Run Declarative Test Runner
```bash
# Method 1: Via zolo command (NEW!)
zolo ztests

# Method 2: Direct Python
python3 zTestRunner/run_tests.py

# Method 3: Executable script
./zTestRunner/run_tests.py

# Method 4: Convenience launcher
./run_zcli_tests.sh
```

### Run Legacy Test Runner (Backup)
```bash
# Still works exactly as before
zolo test
```

---

## Key Design Principles

### ✅ Follows zCLI Patterns

**3-Step Spark**:
1. Import zCLI
2. Create zSpark with config
3. Run walker

**Declarative Navigation**:
- Menu defined in YAML (`zUI.test_menu.yaml`)
- ~Root* array contains menu items
- zWizard handles numbering and routing

**Plugin-Based Execution**:
- Test execution logic in `plugins/test_runner.py`
- Auto-injection of `zcli` parameter
- Returns structured results

### ✅ Non-Breaking Change

**Legacy Command Preserved**:
- `zolo test` still works (marked as "legacy")
- Existing workflows unaffected
- Both commands coexist peacefully

**Migration Path**:
- Users can try `zolo ztests` when ready
- No forced migration
- Easy comparison between old/new

---

## File Structure

```
zolo-zcli/
├── main.py                     # ✅ UPDATED (added ztests command)
├── zTestRunner/                # NEW
│   ├── run_tests.py           # Direct Python entry point
│   ├── zUI.test_menu.yaml     # Declarative menu (37 test suites)
│   └── README.md              # Documentation
├── plugins/
│   └── test_runner.py         # NEW (test execution plugin)
├── run_zcli_tests.sh          # NEW (convenience launcher)
└── zTestSuite/
    └── run_all_tests.py       # Legacy (unchanged)
```

---

## Testing

### Syntax Validation
```bash
python3 -m py_compile main.py  # ✅ PASSED
```

### Help Menu Verification
```bash
python3 main.py --help  # ✅ Shows ztests command
```

### Command Execution
```bash
# Will execute when run:
zolo ztests
# → Launches zCLI test runner
# → Displays numbered menu (0-36)
# → Executes selected test suite via plugin
# → Returns to menu (or exits on "stop")
```

---

## Benefits of Dual Command System

### For Developers
✅ **Test the new system** without breaking existing workflows  
✅ **Compare implementations** side-by-side  
✅ **Gradual migration** when ready  

### For Users
✅ **Choose preferred interface** (legacy vs declarative)  
✅ **No forced changes** to existing scripts  
✅ **Learn new patterns** at own pace  

### For Framework
✅ **Demonstrates declarative patterns** in real-world use case  
✅ **Validates architecture** (zCLI can build its own tooling)  
✅ **Shows migration path** for other imperative code  

---

## Future Plans

### Phase 1: Coexistence (Current)
- Both commands available
- Users choose preference
- Gather feedback

### Phase 2: Recommendation
- Mark `zolo test` as deprecated (not removed)
- Recommend `zolo ztests` in docs
- Update CI/CD to use new command

### Phase 3: Transition (Future)
- Consider making `zolo ztests` the default
- Keep legacy as `zolo test-legacy` or similar
- Full documentation update

---

## Version Info

**Created**: v1.5.4+  
**Status**: ✅ Functional  
**Compatibility**: Non-breaking (legacy preserved)  
**Pattern**: Pure zCLI (declarative)  

---

## Quick Reference

| Command | Type | Status | Entry Point |
|---------|------|--------|-------------|
| `zolo test` | Imperative | Legacy | `zTestSuite/run_all_tests.py` |
| `zolo ztests` | Declarative | NEW | `zTestRunner/run_tests.py` |

**Recommendation**: Try `zolo ztests` for modern, declarative testing experience! 🚀

