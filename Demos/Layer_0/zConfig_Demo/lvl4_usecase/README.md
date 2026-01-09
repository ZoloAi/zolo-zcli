# Level 4: Use Case - The 5-Layer System

**Goal:** Apply everything you've learned with a practical real-world app.

## What You'll Learn

The **5-layer configuration hierarchy** where higher layers override lower ones:

| Priority | Source | What | Where | Example |
|----------|--------|------|-------|---------|
| **5 (highest)** | **zSpark** | Runtime overrides | Your code | `zKernel({"deployment": "Production"})` |
| **4** | **.zEnv** | Workspace secrets | Project folder | `MIN_CPU_CORES=4` |
| **3** | **zEnvironment** | Global settings | Config file | `deployment: Development` |
| **2** | **zMachine** | Hardware specs | Config file | `cpu_cores: 8` (auto-detected) |
| **1 (lowest)** | **Defaults** | Fallback values | Package | `deployment: Development` |

## Demo: System Requirements Checker

A practical app that checks if your machine meets project requirements.

### How It Works

1. **Requirements** defined in `.zEnv` (Layer 4 - workspace-specific)
2. **Hardware specs** from zMachine (Layer 2 - auto-detected)
3. **Deployment mode** from zSpark (Layer 5 - runtime override)
4. **Comparison** shows if system meets requirements

### Run the Demo

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl4_usecase/1_system_checker.py
```

### What You'll See

```
SYSTEM REQUIREMENTS CHECKER
============================

Checking requirements for: ML Training Pipeline v2.1.0
Environment: staging

REQUIREMENTS CHECK
------------------

# CPU Cores:
  Required : 4 cores
  Actual   : 8 cores
  Status   : ✅ PASS

# Memory:
  Required : 8 GB
  Actual   : 16 GB
  Status   : ✅ PASS

# Python Version:
  Required : 3.11+
  Actual   : 3.12.4
  Status   : ✅ PASS

# GPU:
  Required : Yes
  Available: Yes
  Type     : Apple M1
  Status   : ✅ PASS

✅ SYSTEM READY - All requirements met!
```

## The `.zEnv` File

Workspace-specific requirements that travel with your project:

```bash
# Project: ML Training Pipeline
PROJECT_NAME=ML Training Pipeline
PROJECT_VERSION=2.1.0

# Hardware Requirements
MIN_CPU_CORES=4
MIN_MEMORY_GB=8
REQUIRED_GPU=true

# Software Requirements
MIN_PYTHON_VERSION=3.11

# Deployment Context
DEPLOYMENT_ENV=staging
```

### Key Concepts

- **Workspace-specific**: Each project has its own `.zEnv`
- **Auto-loaded**: zConfig loads it automatically (no python-dotenv!)
- **Gitignore-ready**: Perfect for secrets, API keys, tokens
- **Layer 4**: Overrides global config, overridden by zSpark

## Try This

1. **Change requirements**: Edit `.zEnv`, set `MIN_CPU_CORES=16`, run again
2. **Different project**: Copy this `.zEnv` to your own project, customize values
3. **Add secrets**: Add `API_KEY=your_key` to `.zEnv` (remember .gitignore!)

## Hierarchy in Action

This demo shows all 5 layers working together:

```python
# Layer 5: zSpark (highest priority)
zSpark = {"deployment": "Production"}  # Overrides everything
z = zKernel(zSpark)

# Layer 4: .zEnv (workspace)
min_cores = z.config.environment.get_env_var("MIN_CPU_CORES")

# Layer 3: zEnvironment (global config file)
global_deployment = z.config.get_environment("deployment")

# Layer 2: zMachine (auto-detected)
actual_cores = z.config.get_machine("cpu_cores")

# Layer 1: Defaults (fallback)
# If nothing is set, system defaults apply
```

## Real-World Use Cases

1. **System requirements**: Check if machine can run your app
2. **Environment detection**: Different configs for dev/staging/prod
3. **Secrets management**: API keys, tokens in `.zEnv` (gitignored)
4. **Team coordination**: Share `.zEnv.example`, customize per developer
5. **CI/CD pipelines**: Different `.zEnv` per deployment stage

## What's Next?

You've completed the core zConfig tutorials! You now understand:
- ✅ Initialization (Level 1)
- ✅ Settings - logging & traceback (Level 2)
- ✅ Reading configuration (Level 3)
- ✅ The 5-layer hierarchy (Level 4)

For advanced topics, see the guide's appendix:
- Configuration persistence
- Programmatic config changes
- Custom fields and extensions

