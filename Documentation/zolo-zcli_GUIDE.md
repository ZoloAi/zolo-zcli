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
- **Core Subsystems:** utils, crud, funcs, display, zparser, socket, dialog, wizard, open, auth, loader
- **Walker Components:** crumbs, dispatch, menu, link (walker-specific subsystems instantiated by zWalker)
- **Shell Components:** parser, shell, executor

**Dual Mode Support:**
- **Shell Mode:** Interactive command-line interface via InteractiveShell
- **Walker Mode:** YAML-driven menu navigation via zWalker
- **Automatic Detection:** UI mode determined by presence of `zVaFilename` in configuration

#### Initialization Process:

1. **Configuration Loading:** Accepts optional `zSpark_obj` configuration object
2. **Session Creation:** Creates isolated session for multi-user/parallel execution support
3. **Subsystem Initialization:** Instantiates all core subsystems with zCLI instance reference
4. **Plugin Loading:** Loads utility plugins if specified in configuration
5. **Mode Detection:** Determines Shell vs Walker mode based on configuration
6. **Session Setup:** Initializes minimal session with required defaults

#### Public API Methods:

**`run()`** - Main entry point that automatically chooses Shell or Walker mode
**`run_interactive()`** - Explicitly runs in Shell mode
**`run_command(command)`** - Execute single command (useful for API/scripting)

#### Configuration Support:

Key configuration values (typically from .env):
- `zWorkspace`: Project workspace path (defaults to current working directory)
- `zMode`: Operating mode (defaults to "Terminal" for Shell mode)
- `zVaFilename`: UI file for Walker mode (optional)
- `zVaFile_path`: Path to UI file (optional)
- `zBlock`: Starting block in UI file (optional)
- `plugins`: List of plugin paths to load (optional)

#### Architecture Benefits:
- **Centralized Management:** All subsystems managed from single location
- **Instance Isolation:** Each zCLI instance has isolated session and state
- **Flexible Configuration:** Supports both minimal and full configuration scenarios
- **Clean Separation:** Clear distinction between Shell and Walker modes
- **Plugin Support:** Extensible architecture through plugin system

