# Local Authentication Setup (Development Mode)
**For zCLI Development & Testing**  
**Date**: October 2, 2025

---

## 🎯 Overview

For local development and testing, zCLI includes **hardcoded backend users** that bypass the Flask API entirely. This allows you to:
- Test authentication flow without running Flask
- Develop zCLI features in isolation
- Debug authentication issues locally

---

## 🔐 Local Test Users

Three hardcoded users are available:

| Username | Password | Role     | Use Case                    |
|----------|----------|----------|-----------------------------|
| `admin`  | `admin`  | zAdmin   | Full admin access (testing) |
| `builder`| `builder`| zBuilder | Developer role (testing)    |
| `user`   | `user`   | zUser    | Standard user (testing)     |

---

## 🚀 Quick Start

```bash
# 1. Start zCLI shell
zolo-zcli --shell

# 2. Login with local admin
zCLI> auth login
Username: admin
Password: admin

✅ Logged in as: admin (zAdmin)
   User ID: zU_local_admin
   API Key: zAPI_local_dev_key_adm...
   Mode: Local (development)
   Credentials saved to: /Users/you/.zolo/credentials

# 3. Check status
zCLI> auth status

🔐 Authentication Status
══════════════════════════════════════════════════════
Username:   admin
Role:       zAdmin
User ID:    zU_local_admin
API Key:    zAPI_local_dev_key_adm...
Server:     local
══════════════════════════════════════════════════════

# 4. Use zCLI commands
zCLI> crud read zUsers
zCLI> func generate_id zU
zCLI> session info

# 5. Test different roles
zCLI> auth logout
zCLI> auth login
Username: builder
Password: builder
```

---

## 🔄 Switching to Remote API

When you're ready to test with the real Flask API:

```bash
# Set environment variable
export ZOLO_USE_REMOTE_API=true
export ZOLO_API_URL=http://localhost:5000

# Start Flask API (separate terminal)
cd /Users/galnachshon/Projects/Zolo/zCloud/Server
python app.py

# Now login will use Flask API
zolo-zcli --shell
zCLI> auth login
# Will authenticate against Flask API
```

---

## 📋 Authentication Flow

### Local Mode (Default)
```
┌─────────────────────┐
│  User enters creds  │
└──────────┬──────────┘
           │
           ↓
┌──────────────────────────┐
│  Check LOCAL_USERS dict  │
│  (hardcoded in zAuth.py) │
└──────────┬───────────────┘
           │
           ↓
    ┌──────┴──────┐
    │   Valid?    │
    └──────┬──────┘
           │
    ┏━━━━━━┻━━━━━━┓
    ▼              ▼
  ✅ YES         ❌ NO
  Store creds    Show error
```

### Remote Mode (When ZOLO_USE_REMOTE_API=true)
```
┌─────────────────────┐
│  User enters creds  │
└──────────┬──────────┘
           │
           ↓
┌──────────────────────────┐
│  Check LOCAL_USERS first │
└──────────┬───────────────┘
           │
           ↓ (if not found)
┌────────────────────────┐
│  POST to Flask /zAuth  │
└──────────┬─────────────┘
           │
           ↓
┌──────────────────────────┐
│  Validate against zDB    │
└──────────┬───────────────┘
           │
    ┏━━━━━━┻━━━━━━┓
    ▼              ▼
  ✅ YES         ❌ NO
  Store creds    Show error
```

---

## 🧪 Testing Scenarios

### Scenario 1: Test All Roles

```bash
# Test admin role
zCLI> auth login
Username: admin
Password: admin
zCLI> auth status
zCLI> auth logout

# Test builder role
zCLI> auth login
Username: builder
Password: builder
zCLI> auth status
zCLI> auth logout

# Test user role
zCLI> auth login
Username: user
Password: user
zCLI> auth status
```

### Scenario 2: Test Invalid Credentials

```bash
zCLI> auth login
Username: invalid
Password: wrong

❌ Authentication failed: Invalid credentials
   Hint: Use admin/admin for local development
```

### Scenario 3: Test Credentials Persistence

```bash
# Login once
zCLI> auth login
Username: admin
Password: admin

# Exit shell
zCLI> exit

# Check credentials file
cat ~/.zolo/credentials
{
  "username": "admin",
  "role": "zAdmin",
  "user_id": "zU_local_admin",
  "api_key": "zAPI_local_dev_key_admin_00000000000000000000",
  "server_url": "local"
}

# Start new shell - credentials still there
zolo-zcli --shell
zCLI> auth status
# Should show logged in as admin
```

---

## 🔧 Implementation Details

### Location
`zCLI/subsystems/zAuth.py`

### Method
`_authenticate_local(username, password)`

### Hardcoded Users Dictionary
```python
LOCAL_USERS = {
    "admin": {
        "password": "admin",
        "role": "zAdmin",
        "user_id": "zU_local_admin",
        "api_key": "zAPI_local_dev_key_admin_" + "0" * 20
    },
    "builder": {
        "password": "builder",
        "role": "zBuilder",
        "user_id": "zU_local_builder",
        "api_key": "zAPI_local_dev_key_builder_" + "0" * 20
    },
    "user": {
        "password": "user",
        "role": "zUser",
        "user_id": "zU_local_user",
        "api_key": "zAPI_local_dev_key_user_" + "0" * 20
    }
}
```

---

## ⚠️ Security Notes

**WARNING:** These hardcoded credentials are for **DEVELOPMENT ONLY**

- ❌ Never use in production
- ❌ Never commit real credentials
- ❌ Never expose to external network
- ✅ Only for local testing
- ✅ Should be disabled in production builds

---

## 🔄 Migration Path

### Phase 1: Local Development (Current)
- Use hardcoded users
- No Flask dependency
- Fast iteration

### Phase 2: Integration Testing
- Set `ZOLO_USE_REMOTE_API=true`
- Test against real Flask API
- Validate full flow

### Phase 3: Production
- Remove local auth code
- Enforce remote API only
- Add production security

---

## 📚 Related Documentation

- [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) - Full auth system
- [zCore_README.md](./zCore_README.md) - Core functionality

---

## 🎯 Summary

✅ **Advantages:**
- No Flask dependency for basic testing
- Instant feedback during development
- Easy to test different roles
- Simple debugging

🔄 **When to Switch to Remote API:**
- Testing database integration
- Validating password hashing
- Testing real user creation flow
- Production deployment prep

---

**zCLI Local Auth** - Fast, simple, perfect for development.

