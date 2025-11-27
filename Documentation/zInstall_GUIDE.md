**[← Back to README](../README.md) | [Home](../README.md) | [Next: zPhilosophy →](zPhilosophy_GUIDE.md)**

---

# zCLI Installation Guide

Everything you need to go from zero to a working zCLI install—Python setup, pip commands, verification, updates, and cleanup.


## 1. Quick Checklist

- [ ] Python **3.8+** installed (macOS, Windows, or Linux)
- [ ] `git` installed (`git --version` works)
- [ ] `pip` or `pip3` available

## 2. Install Python (macOS & Windows)

### macOS

```bash
# Install Homebrew (if missing)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python@3.11

# Verify
python3 --version
pip3 --version
```

### Windows

1. Download from https://www.python.org/downloads/windows/
2. **Important:** enable "Add Python to PATH" during installation
3. Verify in PowerShell:
   ```powershell
   python --version
   py --version
   ```
4. If `python` fails but `py` works, use `py -m pip install ...`

--- 

### Troubleshoot: Which Python command should I use?

**Common confusion: `python`, `python3`, or `py`**

It depends on your OS and Python installation:

- **macOS/Linux**: Usually `python3` and `pip3`
- **Windows**: Usually `python` or `py` and `pip`
- **Test yours**: Run each command with `--version` and use whichever reports Python 3.8+

**Best practice (works everywhere):**
```bash
# Instead of: pip install ...
# Use this:
python3 -m pip install ...

# This ensures pip matches your Python interpreter
```

> **Note:** For simplicity, the rest of this guide uses `pip` in examples. If you encounter issues, substitute with `python3 -m pip` or `py -m pip` as needed.

## 3. Install zCLI

### 3.1 Pick your package

- **Basic** – SQLite only (fastest install)
- **+CSV** – Adds CSV tooling (`pandas`)
- **+PostgreSQL** – Adds PostgreSQL tooling (`psycopg2-binary`)
- **Full** – Installs every backend (`[all]`)

### 3.2 Install from GitHub (HTTPS)

**Open your terminal** (macOS/Linux) or **Command Prompt/PowerShell** (Windows), then run your desired **zCLI** install command:

```bash
# Basic (SQLite only)
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# CSV support
pip install "zolo-zcli[csv] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# PostgreSQL support
pip install "zolo-zcli[postgresql] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Full install (all backends)
pip install "zolo-zcli[all] @ git+https://github.com/ZoloAi/zolo-zcli.git"
```

### 3.3 Install specific version

```bash
# Install a tagged release
pip install git+https://github.com/ZoloAi/zolo-zcli.git@v1.5.6

# Install a specific commit
pip install git+https://github.com/ZoloAi/zolo-zcli.git@abc1234
```

### 3.4 Editable install (contributors)

**zCLI is open source!** You can clone the entire repository, modify the code, and contribute back to the project.

An **editable install** (`-e`) means changes you make to the source code are immediately reflected without reinstalling. Perfect for:
- Contributing new features or bug fixes
- Experimenting with subsystem modifications
- Learning how zCLI works under the hood

```bash
git clone https://github.com/ZoloAi/zolo-zcli.git
cd zolo-zcli
pip install -e .
```

Now any edits to the `zCLI/` source folder take effect immediately.

## 4. Verify installation

After installation completes, **test that zCLI is working** by running these commands in your terminal:

```bash
zolo --version
```

You should see the version number (e.g., `v1.5.6`). This confirms zCLI is installed and accessible.


## 5. Updating

To update zCLI to a newer version, run the install command again with `--upgrade`:

```bash
# Update to latest version
pip install --upgrade git+https://github.com/ZoloAi/zolo-zcli.git

# Or update to a specific version
pip install --upgrade git+https://github.com/ZoloAi/zolo-zcli.git@v1.5.6
```

**Check your current version:**

```bash
zolo --version
```

## 6. Uninstall & cleanup

### Option 1: Interactive uninstall (recommended)

Run this command in your terminal:

```bash
zolo uninstall
```

This launches an **interactive menu** where you can choose:

1. **Framework Only** (default) - Removes the package, keeps your data and optional dependencies
2. **Clean Uninstall** - Removes package AND all user data (configs, databases, cache)
3. **Dependencies Only** - Removes optional dependencies (pandas, psycopg2) but keeps zCLI

Each option shows you exactly what will be removed and asks for confirmation before proceeding.

### Option 2: Traditional pip uninstall

If you prefer the standard approach:

```bash
pip uninstall zolo-zcli
```

This removes the package only. Your data (configs, databases, cache) will remain on disk. See "Manual cleanup paths" below if you want to remove that data too.

### Manual cleanup paths

If you want to manually remove user data (or if you uninstalled via `pip uninstall zolo-zcli`):

> **Note:** Everything is stored in a single directory per platform for simplicity. No scattered files across multiple OS directories.

```bash
# macOS
rm -rf ~/Library/Application\ Support/zolo-zcli

# Linux
rm -rf ~/.local/share/zolo-zcli

# Windows (PowerShell)
Remove-Item -Recurse -Force $env:LOCALAPPDATA\zolo-zcli
```

This removes all zCLI data including:
- **Configuration files**: `zConfig.machine.yaml`, `zConfig.environment.yaml` (in `zConfigs/`)
- **UI customizations**: User-defined UI files (in `zUIs/`)
- **Application logs**: All log files (in `logs/`)
- **User data**: All `zMachine.*` folders containing databases, CSVs, test files, etc.

> **What are zMachine directories?** See [zConfig Guide](zConfig_GUIDE.md) for details on how zCLI manages cross-platform paths.

## What's next?

Now that **zCLI** is installed, you have three paths forward:

**1. New to Zolo?**  
Start with **[The zPhilosophy](zPhilosophy_GUIDE.md)**. It introduces the core concepts of **zCLI** and smoothly leads into the layer-by-layer guides with ready-made demos.

**2. Need a specific capability?**  
Return to the **[README Architecture table](../README.md#architecture)** and jump directly to the subsystem guide you need (zConfig, zComm, zData, etc.).

---

[← Back to README](../README.md) | [Home](../README.md) | [Next: zPhilosophy →](zPhilosophy_GUIDE.md)
