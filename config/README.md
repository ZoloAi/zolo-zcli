# zolo-zcli Configuration Files

This directory contains default configuration files that are included in the zolo-zcli package.

## Files

- **zConfig.default.yaml** - Base configuration with all default values
- **zConfig.dev.yaml** - Development environment overrides
- **zConfig.prod.yaml** - Production environment overrides
- **zConfig.machine.yaml** - Machine configuration template (auto-generated to `~/.zolo-zcli/machine.yaml`)

## Security Notice

⚠️ **These files contain NO secrets!**

These configuration files only contain:
- ✅ Network settings (host, port)
- ✅ Resource limits (max connections, rate limits)
- ✅ Feature flags (require_auth, ssl_enabled)
- ✅ Schema paths (references like `@.schemas.auth.users`)
- ✅ Timeouts and intervals

**Secrets (passwords, API keys, tokens) MUST be provided via environment variables!**

## Environment Variables for Secrets

```bash
# Database credentials
ZOLO_DB_USERNAME="your_db_user"
ZOLO_DB_PASSWORD="your_db_password"

# Security
ZOLO_JWT_SECRET="your_jwt_secret"
ZOLO_API_MASTER_KEY="your_master_key"

# SSL (if not using reverse proxy)
ZOLO_SSL_CERT_PATH="/path/to/cert.pem"
ZOLO_SSL_KEY_PATH="/path/to/key.pem"
```

## Usage

### Select environment:
```bash
# Development (default)
zolo shell

# Production
ZOLO_ENV=prod zolo shell
```

### Override with user config:

**Linux/macOS:**
```bash
mkdir -p ~/.zolo-zcli
nano ~/.zolo-zcli/config.yaml
```

**Windows:**
```powershell
New-Item -Path "$env:APPDATA\zolo-zcli" -ItemType Directory
notepad "$env:APPDATA\zolo-zcli\config.yaml"
```

### Override with project config:
```bash
cd /your/project
nano config.yaml
```

## Configuration Hierarchy

Priority (highest to lowest):
1. Environment variables (runtime)
2. Project config (`./config.yaml`)
3. User config (OS-specific location)
4. System config (OS-specific location)
5. Package environment config (`zConfig.{env}.yaml`)
6. Package defaults (`zConfig.default.yaml`)

