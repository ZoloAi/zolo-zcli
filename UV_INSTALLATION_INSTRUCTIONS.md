# 🚀 UV Installation Instructions

Your project is now **configured for `uv`** - the ultra-fast Python package manager!

## ✅ What's Been Done

The following files have been created/updated:

1. **`.python-version`** - Pins project to Python 3.11
2. **`.gitignore`** - Updated to ignore `.venv/` (uv's virtual environment)
3. **`pyproject.toml`** - Added `[tool.uv]` configuration section
4. **`UV_SETUP.md`** - Comprehensive documentation for uv usage
5. **`setup-uv.sh`** - Automated setup script (executable)

## 🎯 Next Steps (Run These Commands)

### Step 1: Install uv

Choose one method:

```bash
# Method 1: Official installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 2: Via pip
pip install uv

# Method 3: Via Homebrew (macOS)
brew install uv
```

After installation, restart your terminal or run:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

### Step 2: Run the Setup Script

```bash
cd /Users/galnachshon/Projects/zolo-zcli
./setup-uv.sh
```

This will:
- Verify uv is installed
- Install Python 3.11 if needed
- Generate `uv.lock` file
- Install all dependencies
- Verify the installation

### Step 3: Commit the Lock File

```bash
git add .python-version uv.lock .gitignore pyproject.toml UV_SETUP.md setup-uv.sh
git commit -m "Add uv dependency management with lock file"
```

## 🎬 Quick Test

After setup, verify everything works:

```bash
# Check uv version
uv --version

# Run tests
uv run pytest

# Start zCLI shell
uv run zolo shell

# Check CLI version
uv run zolo --version
```

## 📊 Before vs After

### Before (pip)
```bash
# Slow dependency resolution
pip install -e .                # ~30-60 seconds
pip install -e .[dev]           # Additional time

# No lock file - versions may drift
# No Python version pinning
```

### After (uv)
```bash
# Lightning fast
uv sync --all-extras            # ~3-5 seconds! ⚡

# Lock file ensures reproducible builds
# Python version pinned to 3.11
# Better dependency conflict resolution
```

## 🎯 New Workflows

### For Development
```bash
# Install everything
uv sync --all-extras

# Add a new dependency
uv add requests

# Update dependencies
uv lock --upgrade
uv sync
```

### For CI/CD
```yaml
# .github/workflows/test.yml
- uses: astral-sh/setup-uv@v1
- run: uv sync --all-extras
- run: uv run pytest
```

### For Users
```bash
# Traditional install (still works!)
pip install zolo-zcli

# Or one-off execution (no install!)
uvx zolo-zcli shell
uvx zolo-zcli migrate app.py
```

## 🔍 What Gets Committed

✅ **Do Commit:**
- `uv.lock` - Lock file for reproducible builds
- `.python-version` - Python version pin
- `pyproject.toml` - Project configuration
- `UV_SETUP.md` - Documentation
- `setup-uv.sh` - Setup script

❌ **Don't Commit:**
- `.venv/` - Virtual environment (ignored)
- `__pycache__/` - Python cache (already ignored)

## 💡 Tips

1. **First time?** Run `./setup-uv.sh` - it handles everything
2. **Updating deps?** Use `uv lock --upgrade` to update lock file
3. **Clean install?** Delete `.venv/` and run `uv sync --all-extras`
4. **CI/CD?** uv is 10-100x faster than pip for CI builds!
5. **Problems?** Check `UV_SETUP.md` for troubleshooting

## 🆘 Troubleshooting

### "uv: command not found"
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then restart terminal or:
export PATH="$HOME/.cargo/bin:$PATH"
```

### Lock file out of sync
```bash
# Regenerate
uv lock
uv sync
```

### Python version issues
```bash
# Install Python 3.11 via uv
uv python install 3.11
uv python pin 3.11
```

## 📚 Resources

- **Full Documentation**: See `UV_SETUP.md`
- **uv Official Docs**: https://docs.astral.sh/uv/
- **GitHub**: https://github.com/astral-sh/uv

---

## ⚡ Quick Summary

**What you need to do:**
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Run setup: `./setup-uv.sh`
3. Commit files: `git add .python-version uv.lock ... && git commit`
4. Enjoy 10-100x faster dependency management! 🚀

See `UV_SETUP.md` for complete documentation.

