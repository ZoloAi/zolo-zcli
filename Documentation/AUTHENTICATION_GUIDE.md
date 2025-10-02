# zCLI Authentication System Guide
**Phase 1: Private Git + Runtime Auth**  
**Date**: October 2, 2025

---

## 🎯 Overview

The zCLI authentication system provides two-layer security:
1. **Distribution Control**: Private GitHub repository (requires access to install)
2. **Runtime Authentication**: API key validation against Flask backend

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│   GitHub Private Repo (Distribution Control)        │
│   Only authorized users can access/install          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────┐
│   zCLI Client (Local Installation)                  │
│   • zAuth subsystem                                 │
│   • Credentials stored: ~/.zolo/credentials         │
│   • Commands: auth login, logout, status            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓ (API Key Validation)
┌─────────────────────────────────────────────────────┐
│   Flask API (zCloud/Server)                         │
│   • Endpoint: POST /zAuth                           │
│   • Validates username/password                     │
│   • Returns API key                                 │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────┐
│   Database (zCloud/Data/zDB.db)                     │
│   • zUsers table                                    │
│   • Fields: username, password, role, api_key       │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Implementation

### Files Created:
- `zCLI/subsystems/zAuth.py` - Authentication subsystem

### Files Modified:
- `zCLI/subsystems/__init__.py` - Export ZAuth
- `zCLI/zCore/zCLI.py` - Initialize auth subsystem
- `zCLI/zCore/CommandParser.py` - Parse auth commands
- `zCLI/zCore/CommandExecutor.py` - Execute auth commands
- `zCLI/zCore/Help.py` - Add auth documentation
- `README.md` - Update installation instructions
- `.gitignore` - Ignore credentials directory

---

## 🔐 User Roles

Defined in your schema (`zCloud/schemas/schema.zIndex.yaml`):

```yaml
role:
  type: enum
  options: [zAdmin, zBuilder, zUser]
```

| Role      | Description           | Typical Use Case                    |
|-----------|-----------------------|-------------------------------------|
| zAdmin    | Root/Admin user       | System administration, full access  |
| zBuilder  | Developer user        | Application development             |
| zUser     | Standard user         | End users, limited access           |

---

## 🚀 Usage

### Installation (First Time)

```bash
# Requires GitHub repository access
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git

# Or with personal access token
pip install git+https://TOKEN@github.com/ZoloAi/zolo-zcli.git
```

### Authentication Workflow

```bash
# 1. Start zCLI shell
$ zolo-zcli --shell

# 2. Login with credentials
zCLI> auth login
Username: galnachshon
Password: ********

✅ Logged in as: galnachshon (zAdmin)
   API Key: zAPI_abc123...
   Credentials saved to: /Users/galnachshon/.zolo/credentials

# 3. Check authentication status
zCLI> auth status

🔐 Authentication Status
══════════════════════════════════════════════════════
Username:   galnachshon
Role:       zAdmin
User ID:    zU_xyz789
API Key:    zAPI_abc123...
Server:     http://localhost:5000
══════════════════════════════════════════════════════

# 4. Use zCLI commands (authenticated)
zCLI> crud read zUsers
zCLI> func generate_id zU

# 5. Logout when done
zCLI> auth logout
✅ Logged out successfully
```

### Programmatic Usage

```python
from zCLI import zCLI

# Create zCLI instance
cli = zCLI()

# Login
result = cli.auth.login("username", "password")
if result["status"] == "success":
    print(f"Logged in as: {result['user']['username']}")

# Check authentication
if cli.auth.is_authenticated():
    # Execute commands
    cli.run_command("crud read zUsers")
```

---

## 🔒 Credential Storage

### Location
```
~/.zolo/credentials
```

### Format (JSON)
```json
{
  "username": "galnachshon",
  "api_key": "zAPI_abc123...",
  "role": "zAdmin",
  "user_id": "zU_xyz789",
  "server_url": "http://localhost:5000"
}
```

### Security
- File permissions: `600` (user-only read/write)
- Stored locally, never committed to git
- API key validated on each request
- Can be cleared with `auth logout`

---

## 🌐 Environment Variables

Configure server URL via environment:

```bash
# In .env or shell
export ZOLO_API_URL="http://localhost:5000"

# Or in production
export ZOLO_API_URL="https://api.zolo.dev"
```

Default: `http://localhost:5000`

---

## 🧪 Testing

### Test the Authentication System

```bash
# 1. Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 2. Start Flask API (in separate terminal)
cd /Users/galnachshon/Projects/Zolo/zCloud/Server
python app.py

# 3. Test authentication
zolo-zcli --shell
> auth login
> auth status
> auth logout
```

### Verify API Key Validation

```bash
# Check credentials file
cat ~/.zolo/credentials

# Test with invalid credentials
> auth login
Username: invalid_user
Password: wrong_password
❌ Authentication failed: Invalid credentials
```

---

## 📋 Commands

### `auth login`
Authenticate with Zolo credentials.

**Usage:**
```bash
auth login                          # Interactive prompts
auth login username                 # Prompt for password only
auth login username password        # Non-interactive (not recommended)
```

**Returns:**
- Success: Stores API key locally, updates session
- Failure: Error message, no credentials stored

### `auth logout`
Clear stored credentials and logout.

**Usage:**
```bash
auth logout
```

**Returns:**
- Removes `~/.zolo/credentials`
- Clears session auth data
- Success message

### `auth status`
Show current authentication status.

**Usage:**
```bash
auth status
```

**Returns:**
- If authenticated: Username, role, API key (truncated), server URL
- If not authenticated: Warning message

---

## 🔧 Integration with Existing System

### Flask API Endpoints (Already Exist)

Your Flask API already has the necessary endpoints:

```python
# /zAuth endpoint (zCloud/Server/blueprints/auth.py)
POST /zAuth
Body: {
    "username": "string",
    "password": "string",
    "mode": "Terminal"
}

Response: {
    "status": "success",
    "user": {
        "id": "zU_...",
        "username": "string",
        "role": "zAdmin|zBuilder|zUser",
        "api_key": "zAPI_..."
    }
}
```

### Database Schema (Already Exists)

```yaml
# zCloud/schemas/schema.zIndex.yaml
zUsers:
  id: str (pk)
  username: str (unique)
  email: str (unique)
  password: str (hashed)
  salt: str
  role: enum [zAdmin, zBuilder, zUser]
  api_key: str (unique)
  created_at: datetime
```

---

## 🚦 Future Enhancements (Phase 2)

Optional enhancements for future implementation:

### 1. License Key System
Add installation-time validation:
```python
# setup.py custom hook
ZOLO_LICENSE_KEY=abc123 pip install zolo-zcli
```

### 2. Token Expiration
Add expiration dates to API keys:
```yaml
zUsers:
  api_key_expires: datetime
```

### 3. Device Limits
Track installations per user:
```yaml
zUserDevices:
  user_id: fk -> zUsers.id
  device_id: str
  last_seen: datetime
```

### 4. Private PyPI Server
Professional distribution:
```bash
pip install zolo-zcli --extra-index-url https://pypi.zolo.dev
```

---

## ⚠️ Troubleshooting

### "Not authenticated" Error
```bash
# Solution: Login first
zCLI> auth login
```

### "Error connecting to server"
```bash
# Check Flask API is running
curl http://localhost:5000/

# Check environment variable
echo $ZOLO_API_URL

# Try explicit server URL
zCLI> auth login
(then enter credentials)
```

### "Invalid credentials"
```bash
# Verify user exists in database
# Check password hash matches
# Ensure Flask API is accessible
```

### Credentials file not found
```bash
# Check file exists
ls ~/.zolo/credentials

# If missing, login again
zCLI> auth login
```

---

## 📚 Related Documentation

- [zCore README](./zCore_README.md) - Core functionality
- [ARCHITECTURE.md](./ARCHITECTURE.md) - CRUD architecture
- [VALIDATION_GUIDE.md](./VALIDATION_GUIDE.md) - Data validation

---

## 🎯 Summary

**Phase 1 Complete:**
✅ Authentication subsystem implemented  
✅ Shell commands: `auth login`, `logout`, `status`  
✅ Credential storage in `~/.zolo/credentials`  
✅ Integration with existing Flask API  
✅ Private GitHub distribution  
✅ Documentation complete  

**Next Steps:**
- Test authentication system
- Create initial users in database
- Commit and push changes
- Optional: Add auth check on shell startup

---

**zCLI Authentication** - Secure, simple, and integrated with your existing infrastructure.

