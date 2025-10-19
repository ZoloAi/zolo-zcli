# zCLI Installation Guide

## 📋 Prerequisites

- **Python 3.8 or higher**
- **GitHub Account** with access to the private `ZoloAi/zolo-zcli` repository
- **SSH Key configured** on GitHub (for private repo access)

---

## 🔐 Access Control

**GitHub repository access** controls who can install and use zCLI. Once you have access to the private repository, you have full access to zCLI.

**Note**: zCLI includes a built-in authentication subsystem (`zAuth`) for apps and tools that extend beyond zCLI (like zCloud). This is a **feature**, not a security requirement for using zCLI itself.

### SSH Key Setup (Required)

**1. Generate SSH Key** (skip if you already have one):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for all prompts (uses defaults)
```

**2. Copy Your Public Key**:
```bash
# macOS
cat ~/.ssh/id_ed25519.pub | pbcopy

# Linux
cat ~/.ssh/id_ed25519.pub

# Windows Git Bash
cat ~/.ssh/id_ed25519.pub | clip
```

**3. Add to GitHub**:
- Go to: https://github.com/settings/keys
- Click **"New SSH key"**
- **Title**: `zCLI` (or any name)
- **Key type**: **Authentication Key**
- **Key**: Paste your public key
- Click **"Add SSH key"**

**4. Test Connection**:
```bash
ssh -T git@github.com
# Should see: "Hi YourUsername! You've successfully authenticated..."
```

**Troubleshooting**: If "Permission denied", verify the key was added correctly at https://github.com/settings/keys

### GitHub Repository Access

**Important**: This is a **private repository**. To install zCLI, you must be added as a collaborator.

#### For Users Requesting Access

If you get a "Permission denied" error when installing:

1. Contact your admin (gal@zolo.media) to be added to the repository
2. Accept the GitHub invitation email
3. Verify access: `ssh -T git@github.com`
4. Try installation again

---

## 📦 Installation Methods

### Method 1: Direct Install (Recommended)

Install the latest version from the main branch:

```bash
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git
```

### Method 2: Install Specific Version

Install a tagged release (safer for production):

```bash
# Install a specific version
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.0.0

# Or install a specific commit
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@abc1234
```

### Method 3: HTTPS Install (if SSH is not available)

If you can't use SSH, you can use HTTPS with a GitHub Personal Access Token:

```bash
# First, create a GitHub Personal Access Token with 'repo' scope
# Then install using:
pip install git+https://<YOUR_TOKEN>@github.com/ZoloAi/zolo-zcli.git
```

### Method 4: Editable/Development Install

For contributors or active development:

```bash
# Clone the repository
git clone git@github.com:ZoloAi/zolo-zcli.git
cd zolo-zcli

# Install in editable mode
pip install -e .

# Now any changes to the source code are immediately reflected
```

---

## ✅ Verify Installation

After installation, verify that zCLI is working:

```bash
# Check if the command is available
zolo-zcli --version

# Start the interactive shell
zolo shell
```

You should see:

```
╔═══════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                 ║
╚═══════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'exit' or 'quit' to leave

zCLI>
```

---


## 🔄 Updating zCLI

### Update to Latest Version

```bash
pip install --upgrade git+ssh://git@github.com/ZoloAi/zolo-zcli.git
```

### Update to Specific Version

```bash
pip install --upgrade git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.0.1
```

### Check Current Version

```bash
python3 -c "from zCLI.version import get_version; print(get_version())"
```

---

## 🗑️ Uninstalling

zCLI provides flexible uninstall options to suit your needs.

---

### Option 1: Framework Only (Keep Data) - DEFAULT

Remove the package but preserve your configuration and data:

```bash
zolo uninstall
```

**What gets removed:**
- ❌ zolo-zcli Python package

**What gets preserved:**
- ✅ All configuration files
- ✅ All databases and CSVs
- ✅ All cached data
- ✅ zMachine directories (user data)
- ✅ Optional dependencies (pandas, psycopg2)

**Your data will be preserved at:**
- **Config:** `~/Library/Application Support/zolo-zcli/` (macOS) or `~/.config/zolo-zcli/` (Linux)
- **Data:** `~/Library/Application Support/zolo-zcli/` (macOS) or `~/.local/share/zolo-zcli/` (Linux)
- **Cache:** `~/Library/Caches/zolo-zcli/` (macOS) or `~/.cache/zolo-zcli/` (Linux)

---

### Option 2: Clean Uninstall (Remove Package + Data)

⚠️ **WARNING:** This removes ALL user data, configuration, and databases!

```bash
zolo uninstall --clean
```

**What gets removed:**
- ❌ zolo-zcli Python package
- ❌ All configuration files (zConfigs)
- ❌ All user data (databases, CSVs)
- ❌ All zMachine directories (`zMachine.*` paths)
- ❌ All cached data

**What gets preserved:**
- ✅ Optional dependencies (pandas, psycopg2) - may be used by other tools

**This action CANNOT be undone!**

---

### Option 3: Dependencies Only

Remove optional dependencies but keep zCLI and your data:

```bash
zolo uninstall --dependencies
```

**What gets removed:**
- ❌ pandas (CSV backend support)
- ❌ psycopg2-binary (PostgreSQL backend support)

**What gets preserved:**
- ✅ zolo-zcli Python package
- ✅ All configuration and data
- ✅ Core dependencies (PyYAML, websockets, etc.)

⚠️ **WARNING:** CSV and PostgreSQL backends will stop working!

To restore: `pip install zolo-zcli[csv,postgresql]`

---

### Option 4: Complete Removal (Everything)

For a truly clean slate, remove package, data, AND dependencies:

```bash
# Step 1: Remove package and data
zolo uninstall --clean

# Step 2: Remove dependencies
pip uninstall pandas psycopg2-binary -y
```

This removes **everything** related to zCLI from your system.

---

### Manual Cleanup

If you uninstalled via `pip uninstall zolo-zcli` and want to manually remove user data:

```bash
# macOS
rm -rf ~/Library/Application\ Support/zolo-zcli  # Config & Data (includes zMachine folders)
rm -rf ~/Library/Caches/zolo-zcli                # Cache

# Linux
rm -rf ~/.config/zolo-zcli                       # Config
rm -rf ~/.local/share/zolo-zcli                  # Data (includes zMachine folders)
rm -rf ~/.cache/zolo-zcli                        # Cache

# Windows (PowerShell)
Remove-Item -Recurse -Force $env:APPDATA\zolo-zcli       # Config
Remove-Item -Recurse -Force $env:LOCALAPPDATA\zolo-zcli  # Data & Cache
```

**What's in these directories:**

- **Config**: `zConfig.yaml`, `zConfig.machine.yaml`, session data
- **Data**: All files created via `zMachine.*` paths (databases, CSVs, test files, etc.)
- **Cache**: Temporary files, pinned schema cache, plugin cache

---

### Uninstall Decision Guide

| Scenario | Command | Package | Data | Dependencies |
|----------|---------|---------|------|--------------|
| **Upgrade zCLI** | `zolo uninstall` | ❌ | ✅ | ✅ |
| **Start fresh** | `zolo uninstall --clean` | ❌ | ❌ | ✅ |
| **Free disk space** | `zolo uninstall --clean` + manual deps | ❌ | ❌ | ❌ |
| **Remove CSV support** | `zolo uninstall --dependencies` | ✅ | ✅ | ❌ |

---

### What is a zMachine Directory?

When you use paths like `zMachine.zDataTests` or `zMachine.MyProject`, zCLI creates folders in your **user data directory** to store files in a machine-agnostic way.

**Example:**
- `zMachine.zDataTests` → `~/Library/Application Support/zolo-zcli/zDataTests/` (macOS)
- `zMachine.zDataTests` → `~/.local/share/zolo-zcli/zDataTests/` (Linux)

All these folders are removed when you use `zolo uninstall --clean`.

---