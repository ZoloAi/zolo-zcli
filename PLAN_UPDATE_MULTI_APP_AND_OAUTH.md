# HTML Plan Updated: Multi-App Support + OAuth Integration ✅

**Date:** 2025-10-29
**Changes:** Updated `v1.5.4_plan.html` to reflect multi-app architecture and OAuth as deferred feature

---

## 🎯 **What Changed**

### **1. Week 6.3.6.6a: Session Structure Redesign** (REVISED)

**OLD Structure (Single-App):**
```python
session["zAuth"] = {
    "zSession": {...},
    "application": {...},  # ❌ Single app only!
    "active_context": None
}
```

**NEW Structure (Multi-App):**
```python
session["zAuth"] = {
    "zSession": {...},
    "applications": {  # ✅ Multiple apps simultaneously!
        "ecommerce_store": {...},
        "analytics_dashboard": {...},
        "support_chat": {...}
    },
    "active_app": None,  # ✅ Track which app is focused
    "active_context": None,
    "dual_mode": False
}
```

**New Constants Added:**
- `ZAUTH_KEY_APPLICATIONS = "applications"` (plural!)
- `ZAUTH_KEY_ACTIVE_APP = "active_app"` (NEW!)

**Use Cases Enabled:**
- ✅ User logs into Store A as `customer_bob` → opens Analytics as `analyst_alice`
- ✅ Both authentications persist simultaneously
- ✅ Switching between apps doesn't lose authentication
- ✅ `active_app` tracks which app is currently focused

---

### **2. Week 6.3.6.6b: zAuth Module Enhancement** (UPDATED)

**New Methods Added:**

#### **`authenticate_app_user(app_name, token, config)`**
- Now requires `app_name` parameter
- Populates `session["zAuth"]["applications"][app_name]`
- Sets `active_app = app_name`
- Supports multiple simultaneous app authentications

#### **`switch_app(app_name)`** (NEW!)
- Switch focus between authenticated applications
- Validates app exists before switching
- Updates `active_app` state

#### **`get_app_user(app_name)`** (NEW!)
- Retrieve auth info for specific application
- Returns user dict for requested app
- Returns None if app not authenticated

#### **`logout(context, app_name)`** (UPDATED)
- Now supports `context` parameter:
  - `"zSession"`: Clear zSession only
  - `"application"`: Clear specific app (requires `app_name`)
  - `"all_apps"`: Clear all applications
  - `"all"`: Clear everything (zSession + all apps)

#### **`get_active_user()`** (UPDATED)
- Multi-app aware
- Returns `applications[active_app]` when in application context
- Returns both zSession + active_app when in dual mode

---

### **3. Week 8: OAuth & Third-Party Authentication** (NEW - DEFERRED ⏸️)

**Status:** Lower priority, deferred until after three-tier auth is stable

**Scope:**
- New module: `zAuth/zAuth_modules/oauth_provider.py` (~500 lines)
- OAuth 2.0 flows: authorization code, implicit, client credentials
- OpenID Connect support
- Built-in providers: Google, Facebook, GitHub, Spotify, Instagram, Twitter
- Custom provider support

**OAuth Methods:**
- `get_authorization_url(provider, scopes)`: Generate OAuth URL
- `exchange_code_for_token(provider, code)`: Exchange code for token
- `get_user_info(provider, access_token)`: Fetch user profile
- `refresh_token(provider, refresh_token)`: Refresh expired token
- `revoke_token(provider, token)`: Revoke access

**Session Structure with OAuth:**
```python
session["zAuth"]["applications"]["my_app"] = {
    "authenticated": True,
    "auth_method": "oauth",  # NEW!
    "oauth_provider": "google",  # NEW!
    "access_token": "ya29.a0AfH6...",
    "refresh_token": "1//0gH...",
    "token_expires_at": "2025-10-30T12:00:00Z",
    "scopes": ["email", "profile"]
}
```

**Dependencies:**
- `authlib>=1.3.0` or `requests-oauthlib`
- `cryptography` for JWT validation

**Target Use Cases:**
1. Users building apps that integrate with Google/Spotify/Instagram APIs
2. "Sign in with Google/Facebook" for zCLI applications
3. Enterprise SSO via OAuth 2.0/OpenID Connect

**Why Deferred:**
- Three-tier auth + multi-app support is more critical
- Requires external dependencies
- Need stable zCLI architecture first
- Lower user priority (nice-to-have vs must-have)

**Effort:** 3-5 days when implemented

---

## 📊 **Impact Summary**

### **Session Architecture:**
- **Before:** Single zSession + single application
- **After:** Single zSession + multiple applications simultaneously

### **New Capabilities:**
- ✅ Multiple apps logged in at once (e.g., Store + Analytics + Chat)
- ✅ Switch between apps without losing authentication
- ✅ Per-app logout (don't log out of everything)
- ✅ OAuth support (deferred but planned)

### **Breaking Changes (Week 6.3.6.6a):**
```python
# OLD ❌
session["zAuth"]["application"]

# NEW ✅
session["zAuth"]["applications"][app_name]
```

### **New Session Constants:**
- `ZAUTH_KEY_APPLICATIONS` (plural)
- `ZAUTH_KEY_ACTIVE_APP`
- (OAuth fields deferred to Week 8)

---

## 🎯 **Next Steps**

### **Immediate (Week 6.3.6.6a - NOW):**
- Need to revise our just-completed implementation
- Change `"application"` → `"applications": {}`
- Add `"active_app"` tracking
- Update all 6 occurrences in zAuth files

### **After Week 6.3.6.6a:**
- Week 6.3.6.6b: Implement multi-app methods
- Week 6.3.6.6c: Update bridge_auth.py for multi-app
- Week 6.3.6.6d: Test all scenarios

### **Future (Week 8 - Deferred):**
- OAuth integration when architecture is stable
- All 3 use cases supported (single app, multi-app, OAuth)

---

## ✅ **Plan Status**

- ✅ **Week 6.3.6.6a**: Updated to multi-app architecture
- ✅ **Week 6.3.6.6b**: Updated with multi-app methods
- ✅ **Week 6.3.6.6c**: Ready for multi-app implementation
- ✅ **Week 6.3.6.6d**: Testing updated for multi-app
- ✅ **Week 8**: OAuth added as comprehensive deferred feature
- ✅ **Layer 2**: Updated to Weeks 9-12 (was 8-11)

---

## 💡 **User's Vision Captured:**

> "All three use cases are important for my users, but third-party OAuth is on lower priority - got to get zCLI stable first anyways."

**Plan reflects this priority:**
1. ✅ Multi-app support (Week 6.3.6.6) - HIGH PRIORITY ⚡
2. ✅ Application auth flexibility (Week 6.3.6.6) - HIGH PRIORITY ⚡
3. ⏸️ OAuth integration (Week 8) - LOWER PRIORITY (deferred) 📌

---

**HTML Plan File:** `v1.5.4_plan.html` (updated and ready for review)
**Status:** Ready to implement Week 6.3.6.6a with multi-app architecture! 🚀

