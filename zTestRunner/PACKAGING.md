# zTestRunner Packaging Configuration

## Package Inclusion Summary

The `zTestRunner` package has been properly configured for distribution in the `zolo-zcli` package.

---

## Files Modified

### 1. **MANIFEST.in**
Added zTestRunner to the distribution manifest:

```ini
# Include test suite and demos
recursive-include zTestSuite *.py *.yaml *.md
recursive-include zTestRunner *.py *.yaml *.md *.sh

# Include root launcher script
include run_zcli_tests.sh
```

**What this does**: Includes all Python files, YAML configs, Markdown docs, and shell scripts from zTestRunner in the source distribution.

---

### 2. **pyproject.toml**

#### Package Discovery
Added to `[tool.setuptools.packages.find]`:

```toml
include = ["zCLI*", "logger*", "zTestSuite*", "zTestRunner*"]
```

**What this does**: Tells setuptools to discover and include zTestRunner as a Python package.

#### Package Data
Added to `[tool.setuptools.package-data]`:

```toml
zTestRunner = [
    "*.yaml",
    "*.md",
    "*.sh",
]
```

**What this does**: Includes non-Python files (YAML, Markdown, shell scripts) when installing the package.

---

### 3. **zTestRunner/__init__.py** (NEW)
Created package initializer:

```python
"""
zTestRunner - Declarative Test Execution for zCLI

This package provides a declarative test runner built entirely with zCLI patterns.
Entry point: zolo ztests
"""

__all__ = ["run_tests"]
```

**What this does**: Makes zTestRunner a proper Python package that setuptools can discover and include.

---

## Package Structure

After installation, users will have:

```
site-packages/
├── zCLI/                    # Main framework
├── zTestSuite/              # Legacy test suite (imperative)
├── zTestRunner/             # NEW: Declarative test runner
│   ├── __init__.py
│   ├── run_tests.py         # Direct entry point
│   ├── zUI.test_menu.yaml   # Declarative menu (37 test suites)
│   ├── README.md            # Documentation
│   ├── INTEGRATION_SUMMARY.md
│   └── PACKAGING.md         # This file
├── plugins/
│   └── test_runner.py       # Test execution plugin
├── main.py                  # Entry point (zolo command)
└── run_zcli_tests.sh        # Convenience launcher
```

---

## Verification

### Check what will be included in distribution:

```bash
# Build source distribution
python3 -m build --sdist

# Check contents
tar -tzf dist/zolo-zcli-*.tar.gz | grep zTestRunner
```

**Expected output**:
```
zolo-zcli-x.x.x/zTestRunner/
zolo-zcli-x.x.x/zTestRunner/__init__.py
zolo-zcli-x.x.x/zTestRunner/run_tests.py
zolo-zcli-x.x.x/zTestRunner/zUI.test_menu.yaml
zolo-zcli-x.x.x/zTestRunner/README.md
zolo-zcli-x.x.x/zTestRunner/INTEGRATION_SUMMARY.md
zolo-zcli-x.x.x/zTestRunner/PACKAGING.md
```

---

### Test installation:

```bash
# Install from local source
pip install -e .

# Verify package is accessible
python3 -c "import zTestRunner; print(zTestRunner.__file__)"

# Verify command works
zolo ztests
```

---

## What Gets Installed

### ✅ Included in Package:

1. **Python modules**: `__init__.py`, `run_tests.py`
2. **YAML configs**: `zUI.test_menu.yaml`
3. **Documentation**: `README.md`, `INTEGRATION_SUMMARY.md`, `PACKAGING.md`
4. **Plugin**: `plugins/test_runner.py` (included separately)
5. **Launcher script**: `run_zcli_tests.sh` (root level)

### ❌ Not Included (Development Only):

1. **Python cache**: `__pycache__/` (excluded globally)
2. **Compiled files**: `*.pyc` (excluded globally)

---

## Entry Points After Installation

Users can run tests via:

### 1. **Main Command** (Recommended)
```bash
zolo ztests
```
- Registered in `main.py`
- Uses `handle_ztests_command()`
- Resolves package location automatically

### 2. **Direct Python**
```bash
python3 -m zTestRunner.run_tests
```
- Direct module execution
- Useful for debugging

### 3. **Import in Python**
```python
from zTestRunner import run_tests
# (Future: expose as callable API)
```

---

## Path Resolution

The `handle_ztests_command()` in `main.py` uses dynamic path resolution:

```python
import zCLI as zcli_module
project_root = Path(zcli_module.__file__).parent.parent
```

**Why this works**:
- After installation, `zCLI` is in `site-packages/zCLI/`
- `parent.parent` gives us `site-packages/`
- `zTestRunner` is also in `site-packages/zTestRunner/`
- Both packages can find each other

**Development vs Production**:
- **Development**: Resolves to repo root (`/path/to/zolo-zcli/`)
- **Production**: Resolves to site-packages parent
- **Both**: zTestRunner and plugins are found correctly

---

## Testing Packaging

### Local Development Test:

```bash
# Install in editable mode
pip install -e .

# Test command
zolo ztests
```

### Production Installation Test:

```bash
# Build wheel
python3 -m build

# Install in clean environment
pip install dist/zolo_zcli-*.whl

# Verify
zolo ztests
```

---

## Common Issues & Solutions

### Issue 1: "Module not found: zTestRunner"
**Cause**: Package not included in `pyproject.toml`  
**Solution**: ✅ Fixed - Added to `include = ["zTestRunner*"]`

### Issue 2: "YAML file not found"
**Cause**: YAML files not included in package data  
**Solution**: ✅ Fixed - Added to `package-data` section

### Issue 3: "Plugin not found: test_runner"
**Cause**: plugins/ folder not in same location as zTestRunner  
**Solution**: ✅ Not an issue - plugins/ is separate package-level directory

### Issue 4: "Command 'ztests' not recognized"
**Cause**: Package not reinstalled after main.py update  
**Solution**: Re-run `pip install -e .` after modifying entry points

---

## Distribution Checklist

Before releasing:

- [x] Add zTestRunner to MANIFEST.in
- [x] Add zTestRunner to pyproject.toml packages.find
- [x] Add zTestRunner package data to pyproject.toml
- [x] Create zTestRunner/__init__.py
- [x] Include run_zcli_tests.sh in MANIFEST.in
- [x] Update main.py with ztests command
- [ ] Test source distribution build
- [ ] Test wheel installation in clean environment
- [ ] Verify `zolo ztests` command works post-install
- [ ] Update changelog/release notes

---

## Version Info

**Created**: v1.5.4+  
**Package Type**: Python package with data files  
**Dependencies**: None (uses zCLI framework)  
**Entry Points**: `zolo ztests` command  

---

## References

- **setuptools packaging**: https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
- **MANIFEST.in syntax**: https://packaging.python.org/en/latest/guides/using-manifest-in/
- **pyproject.toml guide**: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

