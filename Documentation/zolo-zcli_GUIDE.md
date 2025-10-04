# zolo-zcli Guide

## Introduction

**zolo-zcli** is a YAML-driven CLI framework for interactive applications. It provides a flexible, configuration-based approach to building command-line interfaces with support for both Shell and Walker modes.

---

## Module Structure

### zCLI/__init__.py - Main Module Structure

The main module file (`zCLI/__init__.py`) defines the core architecture and export structure of the zolo-zcli system:

#### Components:

**zCLI Core:**
- The main implementation of the zCLI system
- Provides the core functionality for both Shell and Walker modes
- Handles subsystem initialization and management
- Streamlined, single-purpose interface

**zWalker Integration:**
- Direct integration with the zWalker subsystem for UI mode
- Enables seamless switching between Shell and Walker modes
- Provides the foundation for interactive menu-driven interfaces

**Export Structure:**
- `zCLI`: Main CLI core implementation
- `zWalker`: UI navigation subsystem

---

## zCLI Core Engine

### zCLI/zCore/zCLI.py - Core Engine Implementation

The core engine (`zCLI/zCore/zCLI.py`) is the central hub that manages all subsystems and provides the main entry point for zolo-zcli applications.

#### Core Architecture:

**Single Source of Truth:**
- All subsystems are instantiated once in the zCLI class
- Prevents subsystem duplication and ensures consistent state
- Provides centralized configuration management

**Subsystem Management:**
- **Shared Subsystems:** zUtils, zCRUD, zFunc, zDisplay, zParser (unified parser for paths and commands), zSocket, zDialog, zWizard, zOpen, zAuth, and zLoader
- **Walker Components:** zCrumbs, zDispatch, zMenu, zLink (walker-specific subsystems instantiated by zWalker)
- **Shell Components:** InteractiveShell and CommandExecutor

**Dual Mode Support:**
- **Shell Mode:** Interactive command-line interface via InteractiveShell
- **Walker Mode:** YAML-driven menu navigation via zWalker (lazy-loaded)
- **Automatic Detection:** UI mode determined by presence of `zVaFilename` in configuration

#### Initialization Process:

1. **Configuration Loading:** Accepts optional `zspark_obj` configuration object
2. **Session Creation:** Creates isolated session for multi-user/parallel execution support
3. **Subsystem Initialization:** Instantiates all core subsystems with zCLI instance reference
4. **Plugin Loading:** Loads utility plugins if specified in configuration
5. **Mode Detection:** Determines Shell vs Walker mode based on `zVaFilename` presence
6. **Session Setup:** Initializes minimal session with required defaults

#### Public API Methods:

**`run()`** - Main entry point that automatically chooses Shell or Walker mode
- **UI Mode:** Lazy-loads zWalker and delegates to `walker.run()`
- **Shell Mode:** Delegates to `run_interactive()` for InteractiveShell

**`run_interactive()`** - Explicitly runs in Shell mode via InteractiveShell

**`run_command(command)`** - Execute single command (useful for API/scripting)

#### Configuration Support:

Key configuration values (typically from .env):
- `zWorkspace`: Project workspace path (defaults to current working directory)
- `zVaFile_path`: Path to UI file (optional)
- `zVaFilename`: UI file for Walker mode (triggers UI mode when present)
- `zBlock`: Starting block in UI file (optional)
- `zMode`: Operating mode (defaults to "Terminal" for Shell mode)
- `plugins`: List of plugin paths to load (optional)
- `logger`: Enable debug logging (optional)

#### Usage Examples:

**Basic Shell Mode:**
```python
from zCLI import zCLI

# Simple shell mode - minimal configuration
cli = zCLI()
cli.run()  # Starts interactive shell
```

**Walker Mode (UI Interface):**
```python
from zCLI import zCLI

# Complete Walker mode configuration
cli = zCLI({
    "zWorkspace": "/path/to/my/project",
    "zVaFile_path": "@.menus",
    "zVaFilename": "ui.main",
    "zBlock": "MainMenu",
    "zMode": "UI",
    "plugins": ["plugins.ui_helpers"],
    "logger": "debug"
})
cli.run()  # Starts Walker UI interface
```

---

## zSession Management

### Session Architecture

**zSession** is the central state management system that provides isolated, instance-specific sessions for each zCLI instance. This enables multi-user support, parallel execution, and consistent state management across all subsystems.

#### Key Features:
- **Instance Isolation:** Each `zCLI()` instance gets its own session
- **Minimal Initialization:** Only essential fields populated at startup
- **Progressive Population:** Fields added on-demand as needed by user actions
- **Backward Compatibility:** Global session available for legacy code

#### Session Fields:
- **Core Identity:** `zS_id` (unique identifier), `zMode` (Terminal/UI)
- **Workspace & Navigation:** `zWorkspace`, `zVaFile_path`, `zVaFilename`, `zBlock`
- **Machine Capabilities:** `zMachine` (platform, capabilities, versions)
- **Authentication:** `zAuth` (user credentials, API keys, roles)
- **Navigation State:** `zCrumbs` (breadcrumb trails), `zCache` (session caching)

#### Session Lifecycle:
1. **Creation:** Factory function creates new isolated session
2. **Minimal Initialization:** Sets `zS_id`, `zMachine`, and `zMode` only
3. **Progressive Population:** Fields populated by user actions (auth login, CRUD operations, Walker navigation)
4. **Session Viewing:** `session info` command displays current state

> **Note:** For complete zSession documentation including field descriptions, lifecycle management, and integration examples, see [zSession_GUIDE.md](zSession_GUIDE.md).

