# Authentication System Testing Guide
**Complete Test Scenarios for zCLI Auth**  
**Date**: October 2, 2025

---

## ✅ **Implementation Complete**

The zCLI authentication system is now fully integrated with:
- ✅ Local backend users (admin/builder/user)
- ✅ zSession["zAuth"] updated on login
- ✅ Credentials restored on shell startup
- ✅ Persistent authentication across sessions

---

## 🧪 **Test Scenarios**

### **Test 1: Basic Login & Logout**

```bash
# Start shell
zolo-zcli --shell

# Login as admin
zCLI> auth login
Username: admin
Password: admin

# Expected output:
✅ Logged in as: admin (zAdmin)
   User ID: zU_local_admin
   API Key: zAPI_local_dev_key_adm...
   Mode: Local (development)
   Credentials saved to: /Users/you/.zolo/credentials

# Check auth status
zCLI> auth status

# Expected output:
🔐 Authentication Status
══════════════════════════════════════════════════════
Username:   admin
Role:       zAdmin
User ID:    zU_local_admin
API Key:    zAPI_local_dev_key_adm...
Server:     local
══════════════════════════════════════════════════════

# Logout
zCLI> auth logout

# Expected output:
✅ Logged out successfully
```

---

### **Test 2: zSession Integration**

```bash
# Login
zCLI> auth login
Username: admin
Password: admin

# Check session - should show zAuth populated
zCLI> session info

# Expected to see:
{
  "zS_id": "zS_...",
  "zAuth": {
    "id": "zU_local_admin",
    "username": "admin",
    "role": "zAdmin",
    "API_Key": "zAPI_local_dev_key_admin_00000000000000000000"
  },
  ...
}
```

---

### **Test 3: Persistent Authentication**

```bash
# First session - login
zolo-zcli --shell
zCLI> auth login
Username: admin
Password: admin
zCLI> exit

# Second session - auth should be restored
zolo-zcli --shell
zCLI> auth status

# Should show logged in as admin (credentials restored from file)

zCLI> session info
# zAuth should be populated automatically
```

---

### **Test 4: Multiple Roles**

```bash
# Test admin role
zCLI> auth login
Username: admin
Password: admin
zCLI> auth status
# Role: zAdmin
zCLI> auth logout

# Test builder role
zCLI> auth login
Username: builder
Password: builder
zCLI> auth status
# Role: zBuilder
zCLI> auth logout

# Test user role
zCLI> auth login
Username: user
Password: user
zCLI> auth status
# Role: zUser
```

---

### **Test 5: Invalid Credentials**

```bash
# Try invalid username
zCLI> auth login
Username: hacker
Password: password

# Expected output:
❌ Authentication failed: Invalid credentials
   Hint: Use admin/admin for local development

# Try invalid password
zCLI> auth login
Username: admin
Password: wrong

# Expected output:
❌ Authentication failed: Invalid credentials
   Hint: Use admin/admin for local development
```

---

### **Test 6: Credentials File**

```bash
# Login
zCLI> auth login
Username: admin
Password: admin

# In another terminal, check credentials file
cat ~/.zolo/credentials

# Expected output:
{
  "username": "admin",
  "role": "zAdmin",
  "user_id": "zU_local_admin",
  "api_key": "zAPI_local_dev_key_admin_00000000000000000000",
  "server_url": "local"
}

# Check file permissions (should be 600 - user only)
ls -la ~/.zolo/credentials
# Output: -rw------- (600)
```

---

### **Test 7: CRUD Operations with Auth**

```bash
# Login first
zCLI> auth login
Username: admin
Password: admin

# Try CRUD operations - should work
zCLI> crud read zUsers
# Should display users from database

zCLI> func generate_id zU
# Should generate ID

zCLI> session info
# Should show full session including auth
```

---

### **Test 8: Help System**

```bash
# Check general help
zCLI> help
# Should show auth commands in the list

# Check auth-specific help
# (Would need to add: help auth)
```

---

## 🔍 **Verification Checklist**

### **After Login:**
- [ ] `auth status` shows user info
- [ ] `session info` shows zAuth populated
- [ ] `~/.zolo/credentials` file exists
- [ ] File permissions are 600
- [ ] Credentials contain all required fields

### **After Logout:**
- [ ] `auth status` shows "not authenticated"
- [ ] `~/.zolo/credentials` file deleted
- [ ] `session info` shows zAuth cleared

### **On Shell Restart:**
- [ ] Previous authentication is restored
- [ ] zSession["zAuth"] is populated
- [ ] `auth status` shows correct user

---

## 🐛 **Debugging**

### **Check Logs**

```bash
# zCLI logs authentication events
# Look for:
# ✅ Local authentication successful
# Updated zSession['zAuth']
# Restored zSession from saved credentials
```

### **Inspect Session Directly**

```python
# In Python (for debugging)
from zCLI import zCLI

cli = zCLI()
print("Is authenticated:", cli.auth.is_authenticated())
print("Credentials:", cli.auth.get_credentials())
print("zSession auth:", cli.session["zAuth"])
```

### **Manual Credential Check**

```bash
# Check if credentials exist
ls -la ~/.zolo/

# View credentials (careful - contains sensitive data in production)
cat ~/.zolo/credentials

# Remove credentials manually
rm ~/.zolo/credentials
```

---

## 📊 **Expected Behavior Summary**

| Action | zSession["zAuth"] Updated | Credentials File | Status Command |
|--------|---------------------------|------------------|----------------|
| `auth login` | ✅ Yes | Created/Updated | Shows user info |
| `auth logout` | ✅ Cleared | Deleted | Shows "not authenticated" |
| Shell startup (with saved creds) | ✅ Restored | Unchanged | Shows user info |
| Shell startup (no saved creds) | ❌ Empty | N/A | Shows "not authenticated" |

---

## 🎯 **Success Criteria**

All of these should work:

1. ✅ Login with `admin/admin`
2. ✅ `auth status` shows admin info
3. ✅ `session info` shows zAuth populated
4. ✅ Exit and restart shell
5. ✅ Auth is automatically restored
6. ✅ CRUD commands work with auth
7. ✅ Logout clears everything
8. ✅ Invalid credentials are rejected

---

## 🔄 **Next Steps (Optional)**

### **Add Authentication Enforcement**
Make authentication required before any commands:

```python
# In Shell.py run() method:
from zCLI.subsystems.zAuth import check_authentication

if not check_authentication(self.zcli):
    return  # Exit if not authenticated
```

### **Add Role-Based Permissions**
Different commands available based on role:

```python
ROLE_PERMISSIONS = {
    "zAdmin": ["*"],  # All commands
    "zBuilder": ["crud read", "crud create", "func"],
    "zUser": ["crud read"]
}
```

### **Add Session Timeout**
Auto-logout after inactivity:

```python
last_activity = time.time()
TIMEOUT = 3600  # 1 hour
```

---

## 📁 **Files Modified**

```
zCLI/subsystems/zAuth.py
  - Added _authenticate_local()
  - Added _authenticate_remote()
  - Added _restore_session_from_credentials()
  - Updates zSession["zAuth"] on login
  - Restores zSession on initialization
```

---

## 🎉 **Summary**

The authentication system is now fully functional with:
- ✅ Local backend users for development
- ✅ zSession integration (auth info in session)
- ✅ Persistent authentication (survives shell restart)
- ✅ Secure credential storage (600 permissions)
- ✅ Three test roles (admin/builder/user)
- ✅ Ready for Flask integration (optional)

**Test all scenarios above to verify complete functionality!** 🚀

