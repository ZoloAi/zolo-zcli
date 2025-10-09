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

### Standard Uninstall (Keep Data)

Remove the package but preserve your configuration and data:

```bash
zolo uninstall --keep-data
```

Your data will be preserved at:
- **Config:** `~/.zolo-zcli/` or `~/Library/Application Support/zolo-zcli/`
- **Data:** Databases, CSVs in `Data/` subdirectory
- **Cache:** Temporary files in `Cache/` subdirectory

### Clean Uninstall (Remove Everything)

⚠️ **WARNING:** This removes ALL user data, configuration, and databases!

```bash
zolo uninstall --clean
```

This will:
- Remove the zolo-zcli package
- Delete all configuration files
- Delete all databases and CSVs
- Delete all cached data

**This action CANNOT be undone!**

### Manual Cleanup

If you uninstalled via pip and want to remove user data:

```bash
# Remove user data directories
rm -rf ~/Library/Application\ Support/zolo-zcli  # macOS
rm -rf ~/.config/zolo-zcli                       # Linux
rm -rf ~/Library/Caches/zolo-zcli                # macOS cache
rm -rf ~/.cache/zolo-zcli                        # Linux cache
```

---