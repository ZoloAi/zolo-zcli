# Level 3: Get - Reading Configuration Values

**Goal:** Access machine, environment, workspace, and session configuration values.

## What You'll Learn

1. **zMachine** - Hardware and OS detection (CPU, memory, Python version)
2. **zEnvironment** - Deployment context and persistent settings
3. **Dotenv (.env/.zEnv)** - Workspace variables (CS convention, auto-loaded)
4. **zSession** - Runtime state (zMode, zSpace, zAuth)

## Demos

### 1. Machine Configuration (`1_zmachine.py`)
Read hardware and OS information auto-detected by zCLI.

```python
machine = z.config.get_machine()

print(f"OS: {machine.get('os')}")
print(f"CPU cores: {machine.get('cpu_cores')}")
print(f"Memory: {machine.get('memory_gb')}GB")
print(f"Python: {machine.get('python_version')}")
```

### 2. Environment Configuration (`2_environment.py`)
Access deployment context and persistent environment settings.

```python
env = z.config.get_environment()

print(f"Deployment: {env.get('deployment')}")
print(f"Role: {env.get('role')}")
print(f"Datacenter: {env.get('datacenter')}")
```

### 3. Workspace Variables (`3_dotenv.py`)
Access workspace-specific variables from auto-loaded dotenv files (.env / .zEnv).

```python
# Dotenv files are automatically loaded from workspace
app_name = z.config.environment.get_env_var("APP_NAME", "Unknown")
api_key = z.config.environment.get_env_var("API_KEY")
debug_mode = z.config.environment.get_env_var("DEBUG", "false") == "true"
```

### 4. Session State (`4_zsession.py`)
Read ephemeral runtime session values created during initialization.

```python
session = z.session

print(f"zS_id: {session.get('zS_id')}")
print(f"title: {session.get('title')}")
print(f"zMode: {session.get('zMode')}")
print(f"zLogger: {session.get('zLogger')}")
print(f"zTraceback: {session.get('zTraceback')}")
```

## Key Concepts

- **get_machine()** - Hardware/OS (auto-detected, persistent)
- **get_environment()** - Deployment context (user-configured, persistent)
- **get_env_var()** - Dotenv variables from .env/.zEnv (CS convention, auto-loaded)
- **z.session** - Runtime state (ephemeral, in-memory only)
- **Consistent zSpark pattern** - All demos use Production deployment
- **Copy-paste ready** - All demos show working accessor patterns

## What's Next?

**→ Level 4:** See all 5 layers working together in a real-world app (System Requirements Checker)

