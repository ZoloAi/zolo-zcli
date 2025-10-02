# zCLI Installation Guide

## 📋 Prerequisites

- **Python 3.8 or higher**
- **GitHub Account** with access to the private `ZoloAi/zolo-zcli` repository
- **SSH Key configured** on GitHub (for private repo access)

---

## 🔐 Authentication Setup

zCLI uses a **two-layer security model**:

1. **GitHub Access** → Controls who can install the package
2. **Runtime Authentication** → Controls who can use the installed CLI

### Verify GitHub SSH Access

```bash
# Test your SSH connection to GitHub
ssh -T git@github.com

# You should see:
# Hi username! You've successfully authenticated...
```

If you don't have SSH keys set up, follow [GitHub's SSH key guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

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
zolo-zcli --help

# Start the interactive shell
zolo-zcli --shell
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

## 🔑 First-Time Authentication

After installing zCLI, you must authenticate to use it:

### 1. Start zCLI Shell

```bash
zolo-zcli --shell
```

### 2. Login with Your Credentials

```bash
zCLI> auth login
```

You'll be prompted for:
- **Username**: Your zCLI username
- **Password**: Your zCLI password
- **Server URL** (optional): Defaults to `http://localhost:5000`

### 3. Verify Authentication Status

```bash
zCLI> auth status
```

### Local Development Mode

If you're developing locally without a backend server, zCLI supports **local authentication** with predefined test users:

```bash
# In your terminal, set this environment variable:
export ZOLO_USE_LOCAL_AUTH=true

# Then login with test credentials:
# Username: admin, Password: admin
# Username: builder, Password: builder
# Username: user, Password: user
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

```bash
pip uninstall zolo-zcli
```

Your authentication credentials will remain in `~/.zolo/credentials` unless you delete them manually:

```bash
rm -rf ~/.zolo
```

---

## 🐛 Troubleshooting

### Issue: "Permission denied (publickey)"

**Problem**: Can't access the private GitHub repository.

**Solution**:
1. Verify your SSH key is added to GitHub
2. Test: `ssh -T git@github.com`
3. Check that you're added as a collaborator on the repo

### Issue: "command not found: zolo-zcli"

**Problem**: The CLI command is not in your PATH.

**Solution**:
```bash
# Find where pip installed the command
python3 -m pip show zolo-zcli

# Add pip's bin directory to your PATH
export PATH="$PATH:$(python3 -m site --user-base)/bin"

# Or reinstall with:
python3 -m pip install --user git+ssh://git@github.com/ZoloAi/zolo-zcli.git
```

### Issue: "Authentication failed"

**Problem**: Can't login to zCLI after installation.

**Solution**:
1. Verify backend server is running (if using remote auth)
2. For local development, set `ZOLO_USE_LOCAL_AUTH=true`
3. Check your credentials: `zCLI> auth status`
4. Try logout and login again: `auth logout` then `auth login`

### Issue: Module import errors

**Problem**: `ModuleNotFoundError` when running zCLI.

**Solution**:
```bash
# Ensure all dependencies are installed
pip install --upgrade pip
pip uninstall zolo-zcli
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git
```

---

## 🎯 Quick Start After Installation

1. **Install zCLI**:
   ```bash
   pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git
   ```

2. **Start Shell**:
   ```bash
   zolo-zcli --shell
   ```

3. **Authenticate**:
   ```bash
   zCLI> auth login
   ```

4. **Test**:
   ```bash
   zCLI> test run
   ```

5. **Get Help**:
   ```bash
   zCLI> help
   ```

---

## 📚 Additional Resources

- **Main README**: [README.md](README.md)
- **Authentication Guide**: [Documentation/AUTHENTICATION_GUIDE.md](Documentation/AUTHENTICATION_GUIDE.md)
- **Architecture**: [Documentation/ARCHITECTURE.md](Documentation/ARCHITECTURE.md)
- **Testing**: [Documentation/TESTING_COMMANDS.md](Documentation/TESTING_COMMANDS.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Run tests: `zCLI> test all`
3. Check logs for error details
4. Open an issue on GitHub (if you have access)
5. Contact the maintainer: gal@zolo.dev

---

**Version**: 1.0.0  
**Last Updated**: October 2025

