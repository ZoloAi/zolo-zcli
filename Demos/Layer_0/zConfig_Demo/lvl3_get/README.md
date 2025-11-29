# Level 3: Get - Reading Configuration Values

**Goal:** Access machine, environment, and session configuration values.

## What You'll Learn

1. **zMachine** - Hardware and OS detection (CPU, memory, Python version)
2. **zEnvironment** - Deployment context and persistent settings
3. **zSession** - Runtime state (zMode, zSpace, zAuth)

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

### 3. Session State (`3_zsession.py`)
Read runtime session values set during initialization.

```python
session = z.session

print(f"zMode: {session.get('zMode')}")
print(f"zSpace: {session.get('zSpace')}")
print(f"zS_id: {session.get('zS_id')}")
```

## Key Concepts

- **get_machine()** - Static hardware/OS configuration
- **get_environment()** - Deployment context (persistent)
- **z.session** - Runtime state (ephemeral)
- **Copy-paste ready** - All demos show accessor patterns

## What's Next?

**→ Level 4:** Understand the configuration hierarchy and persistence

