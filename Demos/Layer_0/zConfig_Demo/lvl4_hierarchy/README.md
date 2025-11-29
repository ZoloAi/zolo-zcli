## Level 3 Demos: Configuration Hierarchy

This level shows how zConfig resolves settings through **5 layers**, from system defaults to runtime overrides.

**Micro-step demos:**

1. **`zenv_demo.py`** - Read workspace secrets from .zEnv (Layer 4)
2. **`zenv_persistence_demo.py`** - Read persistent environment config (Layer 3)

**Run them:**
```bash
python3 Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_demo.py
python3 Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_persistence_demo.py
```

**Shared `.zEnv` file:**

All demos use the same `.zEnv` file with workspace-specific settings:
```bash
APP_THRESHOLD=4
APP_REGION=us-east-1
APP_REPORT_NAME=low_stock_report
```

---

### <span style="color:#8FBE6D">Demo 1: Read from .zEnv</span>

**The simplest layer to understand** - workspace-specific secrets that travel with your project.

```python
z = zCLI({"logger": "PROD"})  # Clean output

# Read values auto-loaded from .zEnv
threshold = z.config.environment.get_env_var("APP_THRESHOLD")
region = z.config.environment.get_env_var("APP_REGION")
```

**How it works:**
1. zConfig detects workspace root on initialization
2. Looks for `.zEnv` (preferred) or `.env` file
3. Loads variables into environment automatically
4. Access via `get_env_var()`

**No python-dotenv needed!** This is built into zConfig.

**When to use .zEnv:**
- API keys and secrets (add to .gitignore!)
- Database connection strings
- Deployment-specific thresholds
- Region/environment settings
- Any value that changes between dev/staging/prod

---

### <span style="color:#8FBE6D">Demo 2: Read Persistent Environment Config</span>

**System-wide environment config** that persists across ALL projects.

```python
z = zCLI({"logger": "PROD"})

# Environment config (Layer 3)
deployment = z.config.get_environment("deployment")
role = z.config.get_environment("role")

# Custom fields (Layer 3) - built into the template!
custom_1 = z.config.get_environment("custom_field_1")
custom_2 = z.config.get_environment("custom_field_2")
custom_3 = z.config.get_environment("custom_field_3")
```

**Where is this stored?**
- `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml`

**Custom fields are built in!** Use them for:
- Application defaults
- User preferences
- Feature flags
- API endpoints
- Any persistent data your app needs

**How to edit:**
- Via zShell: `config environment deployment Production`
- Via code: `z.config.persistence.persist_environment('deployment', 'Production')`
- Manually: Edit the YAML files directly

**vs .zEnv:**
- .zEnv = workspace-specific (travels with project)
- Persistent config = system-wide (available to all projects)

---

### <span style="color:#8FBE6D">The 5-Layer Hierarchy</span>

zConfig resolves settings in this order (highest priority wins):

```
5. Runtime Session (zSpark)      ← Highest priority
4. Workspace Secrets (.zEnv)     ← This demo!
3. Environment Config (zEnvironment)
2. Machine Config (zMachine)
1. System Defaults               ← Lowest priority
```

This demo focuses on **Layer 4** - the workspace-specific layer that's perfect for project secrets.

---

### <span style="color:#8FBE6D">Next Steps</span>

More hierarchy demos coming soon:
- **Demo 3:** Machine config (Layer 2)
- **Demo 4:** zSpark overrides (Layer 5)
- **Demo 5:** Complete hierarchy resolution

Each demo focuses on one layer to keep concepts clean and simple.

