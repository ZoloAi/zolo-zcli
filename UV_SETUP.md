# UV Setup Guide for zCLI

This project uses **`uv`** - the ultra-fast Python package manager from Astral (makers of `ruff`).

## 🚀 Quick Start

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Or via Homebrew (macOS)
brew install uv
```

### First-Time Setup (Developers)

```bash
# 1. Clone the repo
git clone https://github.com/ZoloAi/zolo-zcli
cd zolo-zcli

# 2. Generate lock file (first time only)
uv lock

# 3. Install all dependencies
uv sync

# 4. Install with development tools
uv sync --all-extras

# 5. Verify installation
uv run zolo --version
```

## 📋 Common Commands

### Development Workflow

```bash
# Install dependencies from lock file
uv sync

# Install with dev dependencies
uv sync --all-extras

# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Update all dependencies
uv lock --upgrade

# Run tests
uv run pytest

# Run the CLI
uv run zolo shell
uv run zolo migrate app.py
```

### Installing Optional Dependencies

```bash
# Install with PostgreSQL support
uv sync --extra postgresql

# Install with CSV/Pandas support
uv sync --extra csv

# Install everything
uv sync --all-extras
```

## 🎯 User Installation (Without `uv`)

End users don't need `uv` - they can still use traditional `pip`:

```bash
# Traditional pip install
pip install zolo-zcli

# Or use uvx for one-off execution (no install!)
uvx zolo-zcli shell
uvx zolo-zcli migrate app.py
```

## 📦 Benefits of uv

1. **10-100x Faster** - Dependency resolution and installation
2. **Reproducible** - `uv.lock` ensures identical environments everywhere
3. **Better Resolution** - Smarter conflict handling than pip
4. **Zero-Install UX** - Users can try with `uvx` without installing
5. **Backward Compatible** - Works with existing `pyproject.toml`

## 🔍 Project Structure

```
zolo-zcli/
├── pyproject.toml      # Project metadata & dependencies
├── uv.lock             # Lock file (commit this!)
├── .python-version     # Python version pin (commit this!)
├── .venv/              # Virtual environment (ignored)
└── UV_SETUP.md         # This file
```

## 🆚 uv vs pip

| Task | pip | uv |
|------|-----|-----|
| Install deps | `pip install -e .` | `uv sync` |
| Add dependency | Edit pyproject.toml + `pip install` | `uv add package` |
| Update deps | `pip install --upgrade` | `uv lock --upgrade` |
| Lock versions | ❌ Manual | ✅ Automatic (uv.lock) |
| Speed | 1x | 10-100x |

## 🐛 Troubleshooting

### "uv: command not found"
```bash
# Add to your shell config (~/.bashrc, ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.bashrc  # or source ~/.zshrc
```

### Lock file out of sync
```bash
# Regenerate lock file
uv lock

# Force reinstall
uv sync --reinstall
```

### Python version mismatch
```bash
# Check required Python version
cat .python-version

# Install specific Python version via uv
uv python install 3.11

# Use specific Python version
uv python pin 3.11
```

## 📚 Resources

- **uv Documentation**: https://docs.astral.sh/uv/
- **uv GitHub**: https://github.com/astral-sh/uv
- **Astral Blog**: https://astral.sh/blog

## 🔄 Migration from pip

If you're currently using `pip`:

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Generate lock file from existing pyproject.toml
uv lock

# 3. Create virtual environment and install
uv sync --all-extras

# 4. Test that everything works
uv run pytest

# 5. Commit the lock file
git add uv.lock .python-version
git commit -m "Add uv lock file for reproducible builds"
```

## 🎓 Best Practices

1. **Always commit `uv.lock`** - Ensures reproducible builds
2. **Commit `.python-version`** - Pins Python version for the project
3. **Use `uv sync`** - Respects the lock file (don't use `uv pip install`)
4. **Update regularly** - `uv lock --upgrade` to get latest compatible versions
5. **Test after updates** - Run `uv run pytest` before committing updates

## 💡 Tips

- **Faster CI/CD**: Use `uv sync` in GitHub Actions (10x faster!)
- **Clean installs**: `uv sync --reinstall` for fresh environment
- **Inspect dependencies**: `uv tree` to see dependency tree
- **Check for updates**: `uv lock --upgrade --dry-run` to preview updates

