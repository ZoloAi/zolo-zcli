# zCLI Framework Cleanup & Modernization - Game Plan

**Mission**: Regain control, clean up, and systematically test the zCLI codebase layer by layer, achieving industry-grade architecture and maintainability.

**Strategy**: Bottom-up audit and cleanup (Layer 0 → 4), testing each layer before moving to the next.

**Status**: 🟡 Phase 0 (Entry Point Audit) - IN PROGRESS

---

## 📋 Table of Contents

- [Phase 0: Entry Point & Root Audit](#phase-0-entry-point--root-audit) ⬅️ **CURRENT**
- [Phase 1: Layer 0 - System Foundation](#phase-1-layer-0---system-foundation)
- [Phase 2: Layer 1 - Core Infrastructure](#phase-2-layer-1---core-infrastructure)
- [Phase 3: Layer 2 - Business Logic](#phase-3-layer-2---business-logic)
- [Phase 4: Layer 3 - Abstraction & Integration](#phase-4-layer-3---abstraction--integration)
- [Phase 5: Layer 4 - Orchestration](#phase-5-layer-4---orchestration)
- [Phase 6: Documentation & Examples](#phase-6-documentation--examples)
- [Phase 7: Testing Infrastructure](#phase-7-testing-infrastructure)
- [Phase 8: Demo & Sample Apps](#phase-8-demo--sample-apps)

---

## Phase 0: Entry Point & Root Audit

**Goal**: Clean up CLI entry points and root-level project organization before diving into subsystems.

**Status**: 🟡 IN PROGRESS (0.1 → 0.5)

**Sub-Phases**:
- [Phase 0.1: Root Documentation Cleanup](#phase-01-root-documentation-cleanup) - ✅ **COMPLETE**
- [Phase 0.2: Directory Structure Documentation](#phase-02-directory-structure-documentation) - 🔴 Not Started
- [Phase 0.3: zSys Migration (Layer 0)](#phase-03-zsys-migration-layer-0) - 🟡 Planning Complete
- [Phase 0.4: Empty Directory Cleanup](#phase-04-empty-directory-cleanup) - 🔴 Not Started
- [Phase 0.5: Package Configuration](#phase-05-package-configuration) - 🔴 Not Started

**Progress**: 1/5 sub-phases complete (0.1 done, 0.2 revised)

### 📁 Root Directory Structure Audit

#### Current State
```
/
├── main.py                          # ✅ Clean (orchestrator only)
├── version.py                       # ✅ Clean (recently moved to root)
├── pyproject.toml                   # 🟡 Review dependencies
├── README.md                        # 🟡 Needs update
├── LICENSE                          # ✅ Clean
├── MANIFEST.in                      # 🟡 Review includes
├── mypy.ini                         # ✅ Clean
├── uv.lock                          # ✅ Auto-generated
├── setup-uv.sh                      # 🟡 Review necessity
├── UV_*.md (3 files)                # 🔴 Consolidate docs
├── AGENT.md                         # 🟡 Review relevance
├── IMPLEMENTATION_SUMMARY_*.md      # 🔴 Move to local_planning/
├── zSys/                            # 🟡 System utilities (Layer 0) - NEW LOCATION
├── zCLI/                            # 🟡 See Layer Audits
├── zCloud/                          # 🟡 Sample app - needs isolation
├── zTestRunner/                     # 🟡 Testing - needs review
├── Demos/                           # 🔴 Outdated - needs cleanup
├── Documentation/                   # 🟡 Needs consolidation
├── bifrost/                         # 🟡 Should be in zCLI/subsystems/zBifrost/?
├── local_planning/                  # 🟢 Keep as-is
└── zolo_zcli.egg-info/              # ✅ Auto-generated
```

### 🔍 main.py Detailed Audit

#### Current Structure (267 lines)
**Status**: ✅ **EXCELLENT** - Pure orchestrator, minimal logic

**Architecture Score**: A+ (Industry-grade)

**What's Right**:
1. ✅ Pure orchestration - delegates to subsystems
2. ✅ Clean separation: CLI parsing → handler delegation
3. ✅ Type hints on public functions
4. ✅ Docstrings on all functions
5. ✅ Entry point handlers grouped logically
6. ✅ Centralized imports via `zCLI` package
7. ✅ No business logic in CLI layer
8. ✅ Consistent error handling patterns

**Function Inventory**:
```python
✅ main()                      # Pure argparse orchestration
✅ handle_shell_command()      # Delegate to zCLI.run_shell()
✅ shell_main()                # Entry point for `zShell` command
✅ ztests_main()               # Entry point for `zTests` command
✅ handle_config_command()     # Delegate to zConfig.persistence
✅ handle_ztests_command()     # Declarative test runner launcher
✅ handle_migrate_command()    # Delegate to zData.migrate_app()
✅ handle_uninstall_command()  # Delegate to walker + uninstall UI
```

**Suggestions**:
1. 🟡 **Consider**: Extract handler functions to `/zSys/entry_points.py`
   - Would make `main.py` even thinner (just argparse + routing)
   - Handlers are currently 7 functions (~180 lines)
   - Would leave `main.py` at ~90 lines (pure CLI definition)
   - ✅ **DECIDED**: Using `/zSys/` at root (shared by main.py and zCLI)

2. 🟡 **Optional**: Add `handle_version_command()` for consistency
   - Currently: `parser.add_argument("--version", action="version", ...)`
   - Could show: version + install type + Python version + OS

3. 🟢 **Keep**: Path resolution in handlers (lines 52, 95, 192)
   - These are acceptable CLI-layer concerns (not business logic)
   - Need to happen before zCLI initialization

**Decision**: 
- [ ] Keep as-is (already excellent)
- [x] **DECIDED**: `/zSys/` at root level (shared foundation)
- [ ] Extract handlers to `/zSys/entry_points.py` (optional refinement)

---

### 📦 Root Files Detailed Audit

#### ✅ `version.py` (Recently Moved)
**Status**: CLEAN - No action needed
- ✅ Correct location (root for package metadata)
- ✅ Clean implementation
- ✅ Installation type detection working

#### 🟡 `pyproject.toml`
**Issues**:
1. Review dependency versions (are they pinned correctly?)
2. Check for unused dependencies
3. Verify entry points are up-to-date

**Actions**:
- [ ] Audit dependencies
- [ ] Update project description/metadata
- [ ] Verify all entry points work

#### 🟡 `README.md`
**Issues**:
1. Likely outdated (framework has evolved significantly)
2. May reference deprecated features
3. Installation instructions need updating for `uv` workflow

**Actions**:
- [ ] Rewrite to reflect current v1.5+ architecture
- [ ] Update installation section (pip vs uv)
- [ ] Add quick start examples
- [ ] Link to Documentation/ folder

#### 🔴 `UV_*.md` Files (3 files)
**Files**:
- `UV_INSTALLATION_INSTRUCTIONS.md`
- `UV_SETUP.md`
- `setup-uv.sh`

**Issue**: Fragmented UV documentation

**Action**:
- [ ] Consolidate into single `INSTALLATION.md`
- [ ] Sections: pip, pip-editable, uv, uv-editable
- [ ] Remove redundant files

#### 🔴 `IMPLEMENTATION_SUMMARY_*.md`
**Issue**: Implementation notes in root (should be in `local_planning/`)

**Action**:
- [ ] Move to `local_planning/implementations/`
- [ ] Keep root clean (only user-facing docs)

#### 🟡 `AGENT.md`
**Issue**: Purpose unclear - is this for AI agents or developers?

**Action**:
- [ ] Review content
- [ ] Rename if needed (e.g., `AI_DEVELOPMENT_GUIDE.md`)
- [ ] Or move to `Documentation/`

#### 🟡 `MANIFEST.in`
**Action**:
- [ ] Verify all package data is included
- [ ] Check for missing UI files, schemas, etc.

---

### 🗂️ Directory Organization Issues

#### 🔴 `bifrost/` in Root
**Issue**: Client-side code at root level

**Current**:
```
/bifrost/           # WebSocket client (JS)
/zCLI/subsystems/zBifrost/  # WebSocket server (Python)
```

**Suggested**:
1. Keep separate (client vs server)
2. Rename `/bifrost/` → `/bifrost-client/` (clarity)
3. Or move to `/zCLI/subsystems/zBifrost/client/`

**Decision Needed**: 
- [ ] Keep separate as `/bifrost-client/`
- [ ] Move inside zBifrost subsystem
- [ ] Keep as-is (current)

#### 🟡 `zCloud/` Sample App
**Issue**: Sample app mixed with framework code

**Current**: Sample app at root level

**Suggested**:
- Keep at root (it's a demo, not part of framework)
- Ensure it doesn't import from framework in problematic ways
- Add `zCloud/README.md` clarifying it's a sample

**Actions**:
- [ ] Add `zCloud/README.md` ("Sample Application")
- [ ] Ensure clean separation from framework internals
- [ ] Document as reference implementation

#### 🔴 `Demos/` Directory
**Issue**: 41 subdirectories with outdated demos

**Current State**:
- Mix of old demos, new demos, archived demos
- Inconsistent organization (some by feature, some by layer)
- Many likely outdated

**Suggested Structure**:
```
Demos/
├── 00_Quick_Start/          # New user onboarding
├── 01_Foundation/           # Layer 0-1 demos
├── 02_Core/                 # Layer 2 demos
├── 03_Advanced/             # Layer 3-4 demos
├── 04_Full_Apps/            # Complete applications
└── _Archive/                # Deprecated demos
```

**Actions**:
- [ ] Audit each demo (does it work?)
- [ ] Categorize by layer/complexity
- [ ] Archive broken/outdated demos
- [ ] Create quick-start demo (5 min to "Hello World")

#### 🟡 `Documentation/` Directory
**Current**: 28 guide files (one per subsystem + general)

**Issues**:
1. No index/navigation structure
2. Unclear which guides are up-to-date
3. No quick reference (cheat sheet)

**Suggested**:
```
Documentation/
├── 00_INDEX.md              # Navigation hub
├── 01_Getting_Started/      # Installation, quick start
├── 02_Core_Concepts/        # Architecture, philosophy
├── 03_Subsystem_Guides/     # Current guides (organized)
├── 04_Advanced_Topics/      # Patterns, best practices
└── 05_API_Reference/        # Auto-generated?
```

**Actions**:
- [ ] Create `00_INDEX.md` (navigation hub)
- [ ] Group guides by category
- [ ] Add "last updated" dates
- [ ] Create quick reference card

---

---

## Phase 0.1: Root Documentation Cleanup

**Goal**: Consolidate and organize root-level documentation files

**Status**: 🔴 NOT STARTED

**Scope**: Only documentation files - no code, no directories

### Tasks

#### 0.1.1: Consolidate UV Installation Docs
**Single Source of Truth**: `Documentation/zInstall_GUIDE.md` (already exists ✅)

**Files to Review & Merge**:
- `UV_INSTALLATION_INSTRUCTIONS.md` (root)
- `UV_SETUP.md` (root)
- `setup-uv.sh` (root)

**Actions**:
- [ ] Read all 3 root UV files to extract unique content
- [ ] Update `Documentation/zInstall_GUIDE.md` to add:
  - Section 3e: "UV Workflow (Modern Package Management)"
    - What is UV and why use it?
    - Installing UV
    - `uv run zolo` (isolated execution)
    - `uv pip install` (with virtual env)
  - Section 3f: "UV + Editable Install (Contributors)"
    - `uv pip install -e .` for development
- [ ] Verify existing sections are current (pip, pip -e)
- [ ] Delete redundant root files after merge
- [ ] Update `README.md` to reference `Documentation/zInstall_GUIDE.md`
- [ ] Optional: Create `INSTALL.md` symlink at root → `Documentation/zInstall_GUIDE.md`

**Why This Approach**:
- ✅ Documentation/ is the proper home for guides
- ✅ zInstall_GUIDE.md already comprehensive (287 lines)
- ✅ Avoids duplication (one source of truth)
- ✅ Keeps root directory clean

**Estimated Time**: 45 minutes

---

#### 0.1.2: Move Implementation Notes
**Files Affected**:
- `IMPLEMENTATION_SUMMARY_*.md` (any in root)

**Actions**:
- [ ] Create `local_planning/implementations/` if needed
- [ ] Move all `IMPLEMENTATION_SUMMARY_*.md` → `local_planning/implementations/`
- [ ] Keep root clean (user-facing docs only)

**Estimated Time**: 5 minutes

---

#### 0.1.3: Review/Relocate AGENT.md
**File Affected**:
- `AGENT.md`

**Actions**:
- [ ] Read content to determine purpose
- [ ] **Decision**: Rename? Move to Documentation/? Keep as-is?
- [ ] Execute decision

**Estimated Time**: 10 minutes

---

#### 0.1.4: Update README.md
**File Affected**:
- `README.md`

**Actions**:
- [ ] Update to reflect v1.5+ architecture
- [ ] Add 5-layer architecture diagram (or link to zPhilosophy.md)
- [ ] Update installation section:
  - Quick start: `pip install git+https://github.com/ZoloAi/zolo-zcli.git`
  - Link to: `Documentation/zInstall_GUIDE.md` (detailed instructions)
- [ ] Add quick start example (3-5 lines to "Hello World")
- [ ] Add prominent link to `Documentation/` folder
- [ ] Add `/zSys/` mention in architecture section
- [ ] Add badges (if applicable): version, license, Python version

**Estimated Time**: 45 minutes

---

**Phase 0.1 Completion Criteria**:
- ✅ `Documentation/zInstall_GUIDE.md` updated with UV sections (3e & 3f)
- ✅ Root UV files deleted (UV_INSTALLATION_INSTRUCTIONS.md, UV_SETUP.md, setup-uv.sh)
- ✅ No IMPLEMENTATION_SUMMARY_*.md in root (moved to local_planning/implementations/)
- ✅ AGENT.md relocated → `Documentation/AI_AGENT_GUIDE.md`
- ✅ README.md reflects v1.5+ architecture with /zSys/ and links to guides
- ⏭️ Optional: INSTALL.md symlink at root (skipped - not needed)

**Status**: ✅ **COMPLETE** (All 4 tasks done, ~1.5 hours)

---

## Phase 0.2: Directory Structure Documentation

**Goal**: Document intentional directory choices with clarifying READMEs (no moves!)

**Status**: 🔴 NOT STARTED

**Scope**: Documentation only - explain the "why" behind current structure

**Key Insight**: Current structure is **intentional**, not problematic:
- `/bifrost/` - Co-located with zBifrost for development (will extract later)
- `/zCloud/` - Reference implementation + live app (dual purpose)
- `/Demos/` - Valuable learning resources (stay organized by layer)

### Tasks

#### 0.2.1: Document bifrost/ Development Pattern
**Current**: `/bifrost/` at root (WebSocket client JS)

**User Context**:
- Bifrost client will be its own repo eventually
- Co-located here for **context** (near zBifrost backend) and **debugging**
- Mounted to zCloud's zServer for testing
- Future: Imported via CDN

**Decision**: ✅ **Keep at root as-is**

**Actions**:
- [ ] Create `/bifrost/README.md` explaining:
  - Temporary co-location for development velocity
  - Will be extracted to `bifrost-client` repo when mature
  - Currently mounted to zCloud's zServer for testing
  - Future distribution: CDN import

**Estimated Time**: 5 minutes

---

#### 0.2.2: Verify zCloud/ README Clarity
**Current**: `/zCloud/` at root (reference implementation + live website)

**User Context**:
- User's actual website repository
- Developed here similar to bifrost pattern
- Serves as authentic reference implementation
- Real-world application using all major subsystems

**Decision**: ✅ **Keep at root as-is**

**Actions**:
- [ ] Check if `/zCloud/README.md` exists
- [ ] Verify it explains:
  - Dual purpose: reference implementation + live application
  - Demonstrates zCLI framework capabilities in real-world context
  - Uses all major subsystems (zServer, zBifrost, zData, zAuth, etc.)
- [ ] Update if clarity improvements needed

**Estimated Time**: 3 minutes

---

#### 0.2.3: Optional Demos/ README
**Current**: `/Demos/` with organized subdirectories (Archive/, Layer_0/, Layer_1/, Layer_2/)

**User Context**:
- Demos stay! Valuable learning resources
- Git accessible for cloning
- Will be zipped for easier download (non-cloning users)
- Current organization (by layer) is good

**Decision**: ✅ **Keep structure as-is**

**Actions**:
- [ ] Optional: Create `/Demos/README.md` explaining:
  - Organization by layer (Layer_0, Layer_1, Layer_2)
  - Archive/ for deprecated demos
  - How to run demos
  - Future: Zipped download option
- [ ] Or skip if existing structure is self-explanatory

**Estimated Time**: 5 minutes (if created)

---

#### 0.2.4: Create Documentation Index
**Current**: Flat 28 guide files in `/Documentation/`

**Analysis**: 28 files is manageable in flat structure

**Decision**: ✅ **Keep flat + add INDEX.md**

**Rationale**:
- Subdirectories add navigation friction
- INDEX.md provides logical grouping without file moves
- Less disruption to existing links
- Easier to maintain

**Actions**:
- [ ] Create `Documentation/00_INDEX.md`:
  - Welcome section with quick links
  - Group guides by category:
    - Getting Started (zPhilosophy, zInstall, Basics)
    - Core Infrastructure (zConfig, zComm, zDisplay, etc.)
    - Business Logic (zData, zAuth, zFunc, etc.)
    - Orchestration (zWalker, zShell, zBifrost, zServer)
    - Advanced Topics (AI_AGENT_GUIDE)
  - Link to zPhilosophy as starting point
  - Note: Individual guides remain in Documentation/ root

**Estimated Time**: 10 minutes

---

**Phase 0.2 Completion Criteria**:
- ✅ `/bifrost/README.md` explains temporary co-location
- ✅ `/zCloud/README.md` verified/updated for clarity
- ✅ `/Demos/README.md` created (optional)
- ✅ `Documentation/00_INDEX.md` provides navigation
- ✅ No file moves (documentation only)

**Total Estimated Time**: 15-25 minutes (was 30 in original plan)

**What Changed**:
- ❌ No directory moves (bifrost, zCloud, Demos all stay)
- ❌ No restructuring decisions needed
- ✅ Only adding clarifying documentation
- ✅ Respects intentional development workflow

---

## Phase 0.3: zSys Migration (Layer 0)

**Goal**: Move system utilities from `zCLI/0_System/` to root `/zSys/`

**Status**: 🟡 PLANNING COMPLETE - Ready to Execute

**Scope**: System layer only - no other subsystems

### Architecture

**From**:
```
zCLI/
└── 0_System/
    ├── bootstrap_logger.py
    ├── cli_parser.py
    ├── colors.py
    ├── constants.py
    ├── entry_point_handler.py
    ├── system.py
    ├── validation.py
    ├── zExceptions.py
    └── zTraceback.py
```

**To**:
```
zSys/
├── __init__.py
├── bootstrap_logger.py
├── cli_parser.py
├── colors.py
├── constants.py
├── entry_points.py          # renamed from entry_point_handler
├── system.py
├── validation.py
├── exceptions.py            # renamed from zExceptions
└── traceback.py             # renamed from zTraceback
```

### Migration Steps

#### 0.3.1: Create zSys Structure
- [x] Create `/zSys/` directory ✅ (Already exists - user created)
- [ ] Verify directory contents
- [ ] Create `/zSys/__init__.py` with exports (if missing)
- [ ] Test import: `from zSys import colors`

**Estimated Time**: 5 minutes (reduced - dir exists)

---

#### 0.3.2: Move & Rename Files
- [ ] Move all files from `zCLI/0_System/` to `/zSys/`
- [ ] Rename: `entry_point_handler.py` → `entry_points.py`
- [ ] Rename: `zExceptions.py` → `exceptions.py`
- [ ] Rename: `zTraceback.py` → `traceback.py`

**Estimated Time**: 5 minutes

---

#### 0.3.3: Update zSys Imports
- [ ] Update `/zSys/__init__.py` to export all public APIs
- [ ] Ensure no internal cross-imports broken

**Estimated Time**: 10 minutes

---

#### 0.3.4: Update main.py
- [ ] Change: `from zCLI.0_System` → `from zSys`
- [ ] Test: `python main.py --version`

**Estimated Time**: 5 minutes

---

#### 0.3.5: Update zCLI/__init__.py
- [ ] Change: `from zCLI.0_System` → `from zSys`
- [ ] Re-export for backward compatibility if needed
- [ ] Test imports work

**Estimated Time**: 10 minutes

---

#### 0.3.6: Update All Subsystem Imports
- [ ] Find all: `grep -r "from zCLI.0_System" zCLI/subsystems/`
- [ ] Replace with: `from zSys`
- [ ] Find all: `grep -r "from zCLI.utils import" zCLI/subsystems/`
- [ ] Review if any should import from zSys directly

**Estimated Time**: 20 minutes

---

#### 0.3.7: Update pyproject.toml
- [ ] Add `zSys` to packages list
- [ ] Verify package discovery

**Estimated Time**: 5 minutes

---

#### 0.3.8: Test Migration
- [ ] Run: `python -c "from zSys import colors; print('OK')"`
- [ ] Run: `python main.py --version`
- [ ] Run: `python main.py shell` (check startup)
- [ ] Run existing tests
- [ ] Check for import errors

**Estimated Time**: 15 minutes

---

**Phase 0.3 Completion Criteria**:
- ✅ `/zSys/` exists at root with all files
- ✅ All imports updated (main.py, zCLI, subsystems)
- ✅ No import errors
- ✅ `zolo --version` works
- ✅ `zolo shell` starts without errors

**Total Estimated Time**: 1.5 hours

---

## Phase 0.4: Subsystem Layer Organization

**Goal**: Reorganize 17 subsystems from flat `zCLI/subsystems/` into layered architecture

**Status**: 🔴 NOT STARTED

**Scope**: Subsystem migration only - one at a time for safety

**Why**: Currently all 17 subsystems live in a flat `zCLI/subsystems/` directory. Organizing them by layer (per README architecture) improves:
- **Discoverability**: Clear layer boundaries
- **Dependency Management**: Lower layers can't depend on higher ones
- **UX**: Numbered layers show initialization order
- **Maintainability**: Easier to reason about subsystem relationships

### Architecture Mapping (from README.md)

**Target Structure**:
```
zCLI/
├── 1_Foundation/
│   ├── zConfig/      # Self-aware config (machine → env → session)
│   └── zComm/        # HTTP client + service orchestration
├── 2_Core/
│   ├── zDisplay/     # Render everywhere (Terminal/GUI)
│   ├── zAuth/        # Three-tier auth (bcrypt + SQLite + RBAC)
│   ├── zDispatch/    # Universal command router
│   ├── zNavigation/  # Unified navigation (menus + breadcrumbs)
│   ├── zParser/      # Declarative path parsing
│   ├── zLoader/      # 4-tier cache system
│   └── zUtils/       # Plugin engine
├── 3_Abstraction/
│   ├── zFunc/        # Dynamic Python executor
│   ├── zDialog/      # Declarative form engine
│   ├── zOpen/        # Universal opener (URLs/files/zPaths)
│   ├── zWizard/      # Multi-step orchestrator
│   └── zData/        # Database abstraction
└── 4_Orchestration/
    ├── zBifrost/     # WebSocket bridge
    ├── zShell/       # Interactive command center
    ├── zWalker/      # Declarative UI orchestrator
    └── zServer/      # HTTP file server
```

**Current State**: All in `zCLI/subsystems/` (flat, unsorted)

---

### Migration Strategy

**One subsystem at a time** to minimize risk:
1. Move subsystem directory
2. Update imports in moved subsystem
3. Update imports in zCLI/__init__.py
4. Update imports in other subsystems (if any)
5. Test: `zolo --version` and `zolo shell`
6. Commit before moving to next subsystem

**Order**: Foundation → Core → Abstraction → Orchestration (bottom-up)

---

### Tasks

#### 0.4.1: Move zConfig (Foundation Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zConfig/`  
**To**: `zCLI/L1_Foundation/zConfig/`

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zConfig zCLI/L1_Foundation/`
- [x] Update imports in `zCLI/__init__.py`:
  - `from .subsystems.zConfig` → `from .L1_Foundation.zConfig`
- [x] Update imports in `zCLI/zCLI.py`
- [x] Update 147 imports across 57 files (4 patterns)
- [x] Test: `zolo --version`, `zolo --help`

**Key Decision**: Renamed directories with 'L' prefix (Python doesn't allow module names starting with digits)

**Actual Time**: 10 minutes

---

#### 0.4.2: Move zComm (Foundation Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zComm/`  
**To**: `zCLI/L1_Foundation/zComm/`

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zComm zCLI/L1_Foundation/`
- [x] Update 11 imports across 10 Python files (5 patterns)
- [x] Test: `zolo --version`, full instantiation

**L1_Foundation Layer**: ✅ **COMPLETE** (2/2 subsystems: zConfig + zComm)

**Actual Time**: 5 minutes

---

#### 0.4.3: Move zDisplay (Core Layer)
**From**: `zCLI/subsystems/zDisplay/`  
**To**: `zCLI/L2_Core/c_zDisplay/` ← Global position 3

**Actions**:
- [ ] Move directory: `mv zCLI/subsystems/zDisplay zCLI/L2_Core/c_zDisplay`
- [ ] Update imports (absolute + relative patterns)
- [ ] Update `zCLI/zCLI.py`
- [ ] Test: `zolo --version`, full instantiation

**Note**: zDisplay is used by many subsystems - expect more imports than zComm

**Estimated Time**: 10 minutes

---

#### 0.4.4: Move zAuth (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zAuth/`  
**To**: `zCLI/L2_Core/d_zAuth/` ← Global position 4

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zAuth zCLI/L2_Core/d_zAuth`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 239
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.d_zAuth`)
- `zCLI/subsystems/zBifrost/...bridge_messages.py` (1 import)
- `zCLI/subsystems/zDispatch/...dispatch_launcher.py` (2 imports)
- Internal docstrings in `d_zAuth` module (4 files)

**Note**: zAuth has RBAC dependencies in multiple subsystems

**Actual Time**: 8 minutes

---

#### 0.4.5: Move zDispatch (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zDispatch/`  
**To**: `zCLI/L2_Core/e_zDispatch/` ← Global position 5

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zDispatch zCLI/L2_Core/e_zDispatch`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 243
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.e_zDispatch`)
- `zCLI/subsystems/zBifrost/...bridge_messages.py` (4 imports)
- `zCLI/subsystems/zBifrost/...bridge_event_dispatch.py` (1 import)
- `zCLI/subsystems/zDialog/...dialog_submit.py` (1 import)
- Internal `e_zDispatch` files (4 imports)

**Note**: zDispatch is the command router - critical to shell functionality

**Actual Time**: 8 minutes

---

#### 0.4.6: Move zNavigation (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zNavigation/`  
**To**: `zCLI/L2_Core/f_zNavigation/` ← Global position 6

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zNavigation zCLI/L2_Core/f_zNavigation`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 247
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.f_zNavigation`)
- Internal `f_zNavigation/zNavigation.py` (3 imports)
- Internal `f_zNavigation/navigation_modules/__init__.py` (2 imports)
- Internal `f_zNavigation/__init__.py` (1 import)

**Note**: zNavigation handles menus, breadcrumbs, navbar (recently debugged!)

**Actual Time**: 7 minutes

---

#### 0.4.7: Move zParser (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zParser/`  
**To**: `zCLI/L2_Core/g_zParser/` ← Global position 7

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zParser zCLI/L2_Core/g_zParser`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 251
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.g_zParser`)
- `zBifrost/bridge_messages.py` (1 import)
- `c_zDisplay/events/display_event_outputs.py` (4 imports)
- `c_zDisplay/events/display_event_media.py` (3 imports)
- `c_zDisplay/events/display_event_data.py` (1 import)
- `subsystems/zServer/zServer.py` (2 imports)
- `subsystems/zData/validator.py` (1 import)
- `f_zNavigation/navigation_linking.py` (1 import)
- Internal `g_zParser` docstrings (8 imports)

**Note**: zParser has zMachine path references and is widely used

**Actual Time**: 10 minutes

---

#### 0.4.8: Move zLoader (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zLoader/`  
**To**: `zCLI/L2_Core/h_zLoader/` ← Global position 8

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zLoader zCLI/L2_Core/h_zLoader`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 255
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.h_zLoader`)
- `subsystems/zServer/zServer.py` (2 imports)
- `zBifrost/bridge_messages.py` (1 import)
- Internal `h_zLoader` docstrings (4 imports)

**Note**: zLoader manages 4-tier cache system

**Actual Time**: 8 minutes

---

#### 0.4.9: Move zFunc (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zFunc/`  
**To**: `zCLI/L2_Core/i_zFunc/` ← Global position 9

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zFunc zCLI/L2_Core/i_zFunc`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 259
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.i_zFunc`)
- Internal `i_zFunc/zFunc_modules/__init__.py` (5 docstring imports)

**Note**: zFunc is the dynamic Python executor

**Actual Time**: 7 minutes

---

#### 0.4.10: Move zDialog (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zDialog/`  
**To**: `zCLI/L2_Core/j_zDialog/` ← Global position 10

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zDialog zCLI/L2_Core/j_zDialog`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 263
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.j_zDialog`)
- `zBifrost/bridge_messages.py` (2 imports)
- `zBifrost/bifrost_bridge.py` (1 import)
- `zServer/form_utils.py` (1 import)
- Internal `j_zDialog` docstrings (6 imports)

**Note**: zDialog is the declarative form engine

**Actual Time**: 8 minutes

---

#### 0.4.11: Move zOpen (Core Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zOpen/`  
**To**: `zCLI/L2_Core/k_zOpen/` ← Global position 11

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zOpen zCLI/L2_Core/k_zOpen`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 267
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L2_Core.k_zOpen`)
- `c_zDisplay/display_event_inputs.py` (1 import)
- Internal `k_zOpen` docstrings (8 imports)

**Note**: zOpen is the universal opener (URLs/files/zPaths)

**Actual Time**: 7 minutes

---

🎉 **MAJOR MILESTONE: L2_Core Layer COMPLETE!**
All 9 Core subsystems (positions 3-11) successfully migrated!

---

#### 0.4.12: Move zUtils (Abstraction Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zUtils/`  
**To**: `zCLI/L3_Abstraction/l_zUtils/` ← Global position 12

**Actions**:
- [x] Create `L3_Abstraction` directory
- [x] Move directory: `mv zCLI/subsystems/zUtils zCLI/L3_Abstraction/l_zUtils`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 275
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L3_Abstraction.l_zUtils`)

**Note**: zUtils is the plugin engine (minimal dependencies!)

**Actual Time**: 5 minutes

---

#### 0.4.13: Move zWizard (Abstraction Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zWizard/`  
**To**: `zCLI/L3_Abstraction/m_zWizard/` ← Global position 13

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zWizard zCLI/L3_Abstraction/m_zWizard`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 280
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L3_Abstraction.m_zWizard`)
- `c_zDisplay/display_event_system.py` (1 import - RBAC)
- `subsystems/zWalker/zWalker.py` (1 import - extends zWizard)
- Internal `m_zWizard` docstrings (10 imports)

**Note**: zWizard is the multi-step orchestrator (core loop engine)

**Actual Time**: 8 minutes

---

#### 0.4.14: Move zData (Abstraction Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zData/`  
**To**: `zCLI/L3_Abstraction/n_zData/` ← Global position 14

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zData zCLI/L3_Abstraction/n_zData`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 284
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L3_Abstraction.n_zData`)
- `c_zDisplay/display_event_system.py` (1 import)
- `j_zDialog/zDialog.py` (2 imports)
- `zBifrost/bridge_messages.py` (1 import)
- Internal `n_zData` files (37 imports across 15 files)

**Note**: zData is the database abstraction layer (large subsystem!)

**Actual Time**: 10 minutes

---

#### 0.4.15: Move zBifrost (Abstraction Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zBifrost/`  
**To**: `zCLI/L3_Abstraction/o_zBifrost/` ← Global position 15

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zBifrost zCLI/L3_Abstraction/o_zBifrost`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 289
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L3_Abstraction.o_zBifrost`)

**Note**: zBifrost is the WebSocket bridge (minimal external dependencies!)

**Actual Time**: 4 minutes

---

#### 0.4.16: Move zShell (Abstraction Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zShell/`  
**To**: `zCLI/L3_Abstraction/p_zShell/` ← Global position 16

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zShell zCLI/L3_Abstraction/p_zShell`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 293
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L3_Abstraction.p_zShell`)
- Internal `p_zShell` docstrings (7 imports)

**Note**: zShell is the interactive command center

**Actual Time**: 6 minutes

---

🎉 **MAJOR MILESTONE: L3_Abstraction Layer COMPLETE!**
All 5 Abstraction subsystems (positions 12-16) successfully migrated!

---

#### 0.4.17: Move zWalker (Orchestration Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zWalker/`  
**To**: `zCLI/L4_Orchestration/q_zWalker/` ← Global position 17

**Actions**:
- [x] Create `L4_Orchestration` directory
- [x] Move directory: `mv zCLI/subsystems/zWalker zCLI/L4_Orchestration/q_zWalker`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 298
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L4_Orchestration.q_zWalker`)
- `p_zShell/shell_cmd_walker.py` (1 import)
- Internal `q_zWalker` docstrings (3 imports)

**Note**: zWalker is the declarative UI orchestrator (extends zWizard)

**Actual Time**: 6 minutes

---

#### 0.4.18: Move zServer (Orchestration Layer) ✅ COMPLETE
**From**: `zCLI/subsystems/zServer/`  
**To**: `zCLI/L4_Orchestration/r_zServer/` ← Global position 18

**Actions**:
- [x] Move directory: `mv zCLI/subsystems/zServer zCLI/L4_Orchestration/r_zServer`
- [x] Update imports (absolute + relative patterns)
- [x] Update `zCLI/zCLI.py` line 303
- [x] Test: `zolo --version`, full instantiation

**Files Updated**:
- `zCLI/zCLI.py` (import from `.L4_Orchestration.r_zServer`)
- `zCLI/__init__.py` (json_utils export)
- Internal `r_zServer/zServer.py` (2 imports)

**Note**: zServer is the HTTP file server (FINAL subsystem!)

**Actual Time**: 5 minutes

---

🎉🎉🎉 **MIGRATION COMPLETE: ALL 18 SUBSYSTEMS SUCCESSFULLY REORGANIZED!** 🎉🎉🎉

---

#### 0.4.19: Cleanup & Final Testing
**Actions**:
- [ ] Remove empty `zCLI/subsystems/` directory
- [ ] Remove empty `zCLI/subsystems/zSys/` (if exists)
- [ ] Update `zCLI/__init__.py` docstring to reflect new structure
- [ ] Full integration test:
  - `zolo --version`
  - `zolo --help`
  - `zolo shell` (test all subsystems)
  - `zTest.py` (run test suite)
- [ ] Verify no broken imports: `python -c "from zCLI import zCLI; z = zCLI()"`

**Estimated Time**: 15 minutes

---

**Phase 0.4 Completion Criteria**:
- ✅ All 17 subsystems moved to layered directories
- ✅ `zCLI/1_Foundation/` contains: zConfig, zComm (2 subsystems)
- ✅ `zCLI/2_Core/` contains: zDisplay, zAuth, zDispatch, zNavigation, zParser, zLoader, zUtils (7 subsystems)
- ✅ `zCLI/3_Abstraction/` contains: zFunc, zDialog, zOpen, zWizard, zData (5 subsystems)
- ✅ `zCLI/4_Orchestration/` contains: zBifrost, zShell, zWalker, zServer (4 subsystems)
- ✅ `zCLI/subsystems/` directory removed (empty)
- ✅ All imports updated and working
- ✅ Full test suite passes

**Total Estimated Time**: ~3 hours (18 subsystems × 10 min each)

**Risk Mitigation**:
- One subsystem at a time (easy rollback)
- Test after each move (catch issues early)
- Bottom-up order (dependencies flow downward)
- Keep `zCLI/utils/` as backward compatibility shim

---

## Phase 0.5: Package Configuration

**Goal**: Audit and update package configuration files

**Status**: 🔴 NOT STARTED

**Scope**: Configuration files only

### Tasks

#### 0.5.1: Audit pyproject.toml
**File**: `pyproject.toml`

**Actions**:
- [ ] Review dependencies (are they all needed?)
- [ ] Check for unused dependencies
- [ ] Verify version pins (security vs flexibility)
- [ ] Update project description/metadata
- [ ] Verify entry points work
- [ ] Ensure `zSys` is included in packages

**Estimated Time**: 30 minutes

---

#### 0.5.2: Audit MANIFEST.in
**File**: `MANIFEST.in`

**Actions**:
- [ ] Verify all package data included:
  - UI files (*.yaml)
  - Schemas (*.yaml)
  - Static assets
  - Templates
- [ ] Check for missing includes
- [ ] Test: `python -m build` (does it include everything?)

**Estimated Time**: 20 minutes

---

#### 0.5.3: Review setup-uv.sh
**File**: `setup-uv.sh`

**Actions**:
- [ ] Test script works
- [ ] Update if needed
- [ ] Or remove if redundant (after INSTALLATION.md created)

**Estimated Time**: 10 minutes

---

**Phase 0.5 Completion Criteria**:
- ✅ pyproject.toml reviewed and updated
- ✅ MANIFEST.in verified complete
- ✅ setup-uv.sh decision made

**Total Estimated Time**: 1 hour

---

### Phase 0 Summary: Completion Checklist

**Sub-Phase Status**:
- [ ] 0.1: Root Documentation Cleanup (4 tasks)
- [ ] 0.2: Directory Structure Decisions (3 decisions)
- [x] 0.3: zSys Migration (8 steps) - **READY TO START**
- [ ] 0.4: Empty Directory Cleanup (2 tasks)
- [ ] 0.5: Package Configuration (3 tasks)

**Recommended Order**:
1. ✅ **0.1 Complete** - Documentation cleanup (user-facing) - DONE
2. **0.3 Next** - zSys migration (unblocks development) ⬅️ **RECOMMENDED**
3. **0.2 Quick** - Add directory READMEs (~15 min, optional)
4. **0.4 Quick** - Remove empty dirs (~5 min)
5. **0.5 Last** - Package config (polish)

**Total Estimated Time**: ~3.5 hours (reduced from 4 - Phase 0.2 simplified)

---

## Phase 1: Layer 0 - System Foundation (`/zSys/`)

**Goal**: Audit and clean up pre-boot system layer - NOW AT ROOT LEVEL

**Status**: 🟡 ARCHITECTURAL REFACTORING IN PROGRESS

### 🔄 Architectural Decision: `/zSys/` at Root

**Rationale**:
- Both `main.py` (entry point) and `zCLI/` (framework) depend on system utilities
- System utilities should be shared foundation, not nested in framework package
- Consistent with z* naming convention (zCLI, zCloud, zConfig, etc.)

**Structure**:
```
/zSys/                          # System utilities (Layer 0)
├── __init__.py                 # Export zSys API
├── cli_parser.py               # Argparse setup (used by main.py)
├── bootstrap_logger.py         # Pre-boot logging
├── entry_points.py             # Entry point handlers
├── colors.py                   # Terminal colors
├── validation.py               # Defensive checks
├── constants.py                # System-wide constants
├── exceptions.py               # Base exception classes
└── traceback.py                # Error formatting
```

**Import Pattern**:
```python
# main.py (entry point)
from zSys import cli_parser, bootstrap_logger
from zCLI import zCLI

# zCLI/__init__.py (framework)
from zSys import colors, validation, constants, exceptions
```

### Migration Tasks
- [ ] Move `zCLI/0_System/*` → `/zSys/`
- [ ] Update imports in `main.py`
- [ ] Update imports in `zCLI/__init__.py`
- [ ] Update imports in all subsystems
- [ ] Remove empty `zCLI/0_System/` directory
- [ ] Remove empty layer folders (1_Foundation, 2_Core, etc.)
- [ ] Update `pyproject.toml` to include `zSys` package
- [ ] Run tests to verify no breakage

### Modules to Audit (Post-Migration)
- [ ] `bootstrap_logger.py` - Pre-boot logging
- [ ] `cli_parser.py` - Argparse setup
- [ ] `entry_points.py` - Entry point handlers (from main.py)
- [ ] `colors.py` - Terminal colors
- [ ] `validation.py` - Defensive checks
- [ ] `constants.py` - System-wide constants
- [ ] `exceptions.py` - Exception classes
- [ ] `traceback.py` - Error formatting

### Audit Checklist (per file)
- [ ] No circular dependencies
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] Unit tests exist
- [ ] No business logic (foundation only)
- [ ] Proper logging
- [ ] Error handling

---

## Phase 2: Layer 1 - Core Infrastructure

**Goal**: Audit foundational subsystems that other layers depend on

**Status**: 🔴 NOT STARTED

### Subsystems to Audit
- `zConfig` - Configuration management
  - `config_zenv.py` - YAML environment loading
  - `config_paths.py` - Path resolution
  - `config_session.py` - Session management
  - `config_logger.py` - Logging setup
  - Others...
- `zComm` - Communication (HTTP/WebSocket)
- `zDisplay` - Output primitives
- `zParser` - YAML/path parsing
- `zLoader` - Resource loading & caching

---

## Phase 3: Layer 2 - Business Logic

**Goal**: Audit core business logic subsystems

**Status**: 🔴 NOT STARTED

### Subsystems to Audit
- `zData` - Data operations (CRUD, migrations)
- `zAuth` - Authentication & RBAC
- `zFunc` - Function execution
- `zOpen` - File/URL operations
- `zDialog` - User input dialogs
- `zUtils` - Utilities & plugins

---

## Phase 4: Layer 3 - Abstraction & Integration

**Goal**: Audit integration layers

**Status**: 🔴 NOT STARTED

### Subsystems to Audit
- `zDispatch` - Command routing
- `zNavigation` - Breadcrumbs, menus, linking
- `zWizard` - Loop engine (recently cleaned ✅)
- `zServer` - HTTP server

---

## Phase 5: Layer 4 - Orchestration

**Goal**: Audit top-level orchestrators

**Status**: 🔴 NOT STARTED

### Subsystems to Audit
- `zCLI.py` - Main engine orchestrator
- `zWalker` - Menu navigation (recently cleaned ✅)
- `zShell` - Interactive shell
- `zBifrost` - WebSocket orchestration

---

## Phase 6: Documentation & Examples

**Goal**: Ensure all code is documented and demonstrated

**Status**: 🔴 NOT STARTED

### Tasks
- [ ] Subsystem guides up-to-date
- [ ] Architecture diagrams current
- [ ] API reference complete
- [ ] Tutorial path for new users
- [ ] Migration guides (breaking changes)

---

## Phase 7: Testing Infrastructure

**Goal**: Comprehensive test coverage

**Status**: 🔴 NOT STARTED

### Tasks
- [ ] `zTestRunner/` organization
- [ ] Unit tests per subsystem
- [ ] Integration tests
- [ ] RBAC tests
- [ ] WebSocket tests (zBifrost)
- [ ] Performance benchmarks

---

## Phase 8: Demo & Sample Apps

**Goal**: Validate framework via real applications

**Status**: 🔴 NOT STARTED

### Tasks
- [ ] Quick start demo (5 min)
- [ ] Layer-specific demos
- [ ] zCloud as reference app
- [ ] Community examples

---

## 📊 Progress Tracking

### Overall Status
- 🟢 **Complete**: 0/8 phases
- 🟡 **In Progress**: 1/8 phases (Phase 0)
- 🔴 **Not Started**: 7/8 phases

### Phase 0 Progress
- 🟢 **main.py audit**: Complete
- 🟢 **Root files inventory**: Complete
- 🟢 **/zSys/ decision**: Complete (use root-level zSys)
- 🟡 **Phase 0.3 planning**: Complete (ready to execute)
- 🔴 **Sub-phases completed**: 0/5
- 🔴 **Total tasks completed**: 0/20

---

## 🎯 Next Actions (Micro-Steps)

### Immediate (This Session)
1. ✅ **Plan approved** - Using `/zSys/` at root
2. 🟡 **Execute Phase 0.3** - zSys Migration (8 micro-steps, ~1.5 hours)
   - Start: 0.3.1 Create zSys structure
   - End: 0.3.8 Test migration
3. 🔴 **Execute Phase 0.1** - Root Documentation Cleanup (4 tasks, ~1.5 hours)

### Short Term (Next Session)
4. 🔴 **Execute Phase 0.2** - Directory Decisions (3 decisions, ~30 min)
5. 🔴 **Execute Phase 0.4** - Empty Directory Cleanup (2 tasks, ~5 min)
6. 🔴 **Execute Phase 0.5** - Package Configuration (3 tasks, ~1 hour)

### Medium Term
7. 🔴 **Begin Phase 1** - Audit `/zSys/` modules (post-migration)
8. 🔴 **Establish testing pattern** - Define test structure per phase

**Current Focus**: Phase 0.3 (zSys Migration) - Step 0.3.1

---

## 🔧 Methodology

### Per-File Audit Template
```markdown
## File: {path}
**Lines**: {count}
**Complexity**: {Low|Medium|High}
**Dependencies**: {list}

### Issues Found
1. {issue} - Priority: {🔴|🟡|🟢}
2. ...

### Recommendations
1. {action}
2. ...

### Test Coverage
- [ ] Unit tests exist
- [ ] Integration tests exist
- [ ] Edge cases covered
```

### Per-Subsystem Audit Template
```markdown
## Subsystem: {name}
**Layer**: {0-4}
**Status**: {🔴|🟡|🟢}

### Module Inventory
- `file1.py` - {status} - {brief description}
- ...

### Architecture
- Responsibilities: {clear?}
- Dependencies: {appropriate?}
- Circular imports: {none?}

### Code Quality
- Documentation: {score}
- Type hints: {score}
- Error handling: {score}
- Test coverage: {score}

### Action Items
- [ ] {action}
- ...
```

---

## 📖 Definitions

- 🔴 **Critical**: Must fix before phase completion
- 🟡 **Important**: Should fix soon
- 🟢 **Optional**: Nice to have

- **Layer 0**: Pre-boot system (no dependencies)
- **Layer 1**: Foundation (config, I/O, display)
- **Layer 2**: Business logic (data, auth, functions)
- **Layer 3**: Integration (dispatch, navigation, wizards)
- **Layer 4**: Orchestration (CLI, walker, shell, bifrost)

---

*Last Updated: 2025-12-27*
*Version: 1.3*
*Status: Phase 0 - In Progress (0.1 Complete, 0.2 Revised)*
*Current Focus: Phase 0.3 - zSys Migration (Ready to Execute)*
*Architecture Decisions:*
- *`/zSys/` at root level (shared foundation)*
- *`/bifrost/` stays at root (intentional co-location for development)*
- *`/zCloud/` stays at root (reference implementation + live app)*
- *`/Demos/` stays organized by layer (valuable learning resources)*

