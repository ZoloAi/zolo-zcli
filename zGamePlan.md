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
- [Phase 0.3: zSys Migration (Layer 0)](#phase-03-zsys-migration-layer-0) - ✅ Complete
- [Phase 0.4: Subsystem Layer Organization](#phase-04-subsystem-layer-organization) - ✅ Complete
- [Phase 0.5: Package Configuration](#phase-05-package-configuration) - 🟡 In Progress (1/3 tasks complete)
- [Phase 0.6: Argparser Audit & Cleanup](#phase-06-argparser-audit--cleanup) - ✅ Complete (Core Objectives Achieved)

**Progress**: 4.5/6 sub-phases complete (0.1, 0.3, 0.4, 0.6 done; 0.5 partial; 0.2 optional)

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

**Goal**: Clean up package metadata and configuration files

**Status**: 🟡 IN PROGRESS

**Scope**: Package metadata and configuration files

### Tasks

#### 0.5.1: Move version.py to Root ✅ COMPLETE
**From**: `zCLI/version.py`  
**To**: `version.py` (root)

**Rationale**: Package version metadata belongs at root level with `pyproject.toml`

**Actions**:
- [x] Move `zCLI/version.py` → `version.py`
- [x] Update `pyproject.toml` version reference (`version.__version__`)
- [x] Update `pyproject.toml` py-modules to include `version`
- [x] Update imports in `main.py`
- [x] Update imports in `o_zBifrost/bridge_connection.py`
- [x] Reinstall package: `pip install -e .`
- [x] Test: `zolo --version` works correctly ✓

**Files Updated**:
- `version.py` (moved to root)
- `pyproject.toml` (version attr + py-modules)
- `main.py` (import from `version`)
- `o_zBifrost/bridge_connection.py` (import from `version`)

**Actual Time**: 10 minutes

---

#### 0.5.2: Audit pyproject.toml
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

## Phase 0.6: Argparser Audit & Cleanup

**Goal**: Audit and streamline main.py argparser logic for clarity, consistency, and maintainability

**Status**: 🟢 SUBSTANTIAL PROGRESS - Major Improvements Complete

**Scope**: CLI argument parsing in `main.py` only

---

### ✅ Completed Changes (Surgical Approach)

#### 0.6.1: Default Behavior - Info Banner ✅ COMPLETE
**Changes Applied**:
- [x] Added `display_info()` function - Shows version, install type, tagline, author, license
- [x] Changed `zolo` default behavior - No longer opens shell, displays info banner instead
- [x] Simplified installation type display - Shows "editable", "uv", or "standard" (clean, no double parens)

**Result**:
```bash
$ zolo
zolo-zcli 1.5.8 (editable)
A declarative based Framework
By Gal Nachshon
License: MIT
```

**Time**: 10 minutes

---

#### 0.6.2: Remove zShell Standalone ✅ COMPLETE
**Changes Applied**:
- [x] Removed `zShell` standalone command - Removed entry point from `pyproject.toml`
- [x] Removed `shell_main()` function - Eliminated duplicate code
- [x] Consolidated shell entry points - Only `zolo shell` works now

**Result**:
```bash
$ zShell  # Now removed
command not found: zShell

$ zolo shell  # Must use this explicitly
[enters shell]
```

**Time**: 5 minutes

---

#### 0.6.3: Simplify Config Command ✅ COMPLETE
**Changes Applied**:
- [x] Removed all nested subparsers (machine/environment)
- [x] Removed all flags (--show, --reset)
- [x] Removed all arguments (key, value)
- [x] Simplified handler - No args parameter, read-only display only
- [x] Single line argparser definition

**Before** (Complex - 33+ lines):
```python
def handle_config_command(args):
    if args.config_type == "machine":
        if args.show: ...
        elif args.reset and args.key: ...
        elif args.key and args.value: ...
    elif args.config_type == "environment": ...
```

**After** (Simple - 4 lines):
```python
def handle_config_command():
    """Handle config command - display only (read-only)."""
    cli = zCLI({'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'})
    cli.config.persistence.show_machine_config()
    cli.config.persistence.show_environment_config()
```

**Design Achieved**:
- **CLI Level (Read-Only)**: `zolo config` → Shows zMachine + zEnvironment
- **Shell Level (Interactive)**: `config check/show/get/set/reset` → All modifications

**Time**: 15 minutes

---

#### 0.6.4: Production Mode for Config ✅ COMPLETE
**Changes Applied**:
- [x] Config command runs in Production mode with PROD logger
- [x] Suppresses all "[Ready]" messages and initialization logs
- [x] Clean output - only config data displayed

**Before**: 200+ lines of verbose output (all subsystem init messages, schema loading)

**After**: Clean config display only

**zSpark Config**:
```python
{'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'}
```

**Time**: 10 minutes

---

#### 0.6.5: Refactor Migration Command to zData ✅ COMPLETE
**Goal**: Move migration display/UX logic from main.py to zData (single source of truth)

**Changes Applied**:
- [x] Created `zData.cli_migrate()` method - Full CLI migration experience (140 lines)
- [x] Simplified `handle_migrate_command()` - From 109 lines to 18 lines (83% reduction!)
- [x] Maintained file validation in main.py - CLI layer concern
- [x] Delegated all display/UX to zData - Subsystem layer concern

**Before**:
```python
def handle_migrate_command(args):  # 109 lines in main.py
    # File validation
    # Banner display (70 lines)
    # Schema discovery display
    # Migration execution
    # Results display (40 lines)
```

**After**:
```python
# main.py - 18 lines
def handle_migrate_command(args):
    # File validation (CLI layer)
    # Delegate to z.data.cli_migrate()

# zData.py - 140 lines
def cli_migrate(self, ...):
    # All display & UX logic
    # Delegates to self.migrate_app()
    # Returns exit code
```

**Benefits**:
- ✅ Single source of truth (all migration UX in zData)
- ✅ Reusable (other code can call `z.data.cli_migrate()`)
- ✅ Testable (migration UX testable independently)
- ✅ Consistent (matches `z.run_shell()`, `z.config.show_*()`)
- ✅ Clean main.py (reduced by 91 lines)
- ✅ Maintainable (changes in one place)

**Design Philosophy**:
- **CLI layer** (main.py): Argparse + validation + delegation
- **Subsystem layer** (zData): Full feature + UX + business logic

**Files Modified**:
- `zCLI/L3_Abstraction/n_zData/zData.py` - Added `cli_migrate()` method
- `main.py` - Simplified `handle_migrate_command()`

**Total Lines**:
- main.py: 264 → 178 lines (86 lines removed)
- zData.py: +140 lines (new method)
- Net: Better organization, single source of truth achieved

**Testing**:
- ✅ `zolo migrate --help` - Works
- ✅ `zolo migrate zTest.py --dry-run` - Works
- ✅ Display banners - ✓
- ✅ Schema discovery - ✓
- ✅ Migration execution - ✓
- ✅ Results display - ✓
- ✅ Exit codes - ✓

**Time**: 20 minutes

---

#### 0.6.6: Bootstrap Logger Implementation ✅ COMPLETE
**Goal**: Implement robust pre-boot logging system with buffer injection and --verbose support

**Changes Applied**:
- [x] Created `zSys/bootstrap_logger.py` - Complete bootstrap logger class (212 lines)
- [x] Updated `zSys/__init__.py` - Exports BootstrapLogger
- [x] Updated `main.py` - Bootstrap logger integration throughout
- [x] Added `--verbose` flag to ALL commands - Shows bootstrap process on stdout
- [x] Buffer injection to `zcli-framework.log` - Complete audit trail
- [x] Emergency dump on init failure - stderr + temp file fallback
- [x] Exception handling - try/except wrapper in main()

**Bootstrap Logger Features**:
```python
class BootstrapLogger:
    • In-memory log buffer (pre-boot)
    • flush_to_framework() - Inject to zcli-framework.log
    • emergency_dump() - Fallback on critical errors
    • --verbose support - Colored stdout display
    • Zero dependencies - Pure Python stdlib
```

**Integration**:
```python
# main.py - ALWAYS FIRST
boot_logger = BootstrapLogger()
boot_logger.info("zolo-zcli entry point started")
boot_logger.debug("Python: %s", sys.version)

# ... imports, args parsing ...

cli = zCLI()
boot_logger.flush_to_framework(cli.logger.framework, verbose=args.verbose)
```

**--verbose Flag**:
```bash
# Shows bootstrap process on stdout (colored + timestamped)
$ zolo config --verbose
[17:34:01] [Bootstrap] zolo-zcli entry point started
[17:34:01] [Bootstrap] Python: 3.12.4
[17:34:01] [Bootstrap] Core imports completed
[17:34:01] [Bootstrap] Parsing command-line arguments
[17:34:01] [Bootstrap] Loading config display...
[Bootstrap] ✓ Initialized in 1.199s

[Config display follows...]

# Without --verbose: silent (but logs still go to framework.log)
$ zolo config
[Config display only - no bootstrap messages]
```

**zcli-framework.log Injection**:
```
2025-12-27 17:34:02 - bootstrap_logger - INFO - ======================================
2025-12-27 17:34:02 - bootstrap_logger - INFO - [Bootstrap] Pre-boot log injection (7 messages, 1.199s)
2025-12-27 17:34:02 - bootstrap_logger - INFO - ======================================
2025-12-27 17:34:02 - bootstrap_logger - INFO - [Bootstrap:17:34:01.083] zolo-zcli entry point started
2025-12-27 17:34:02 - bootstrap_logger - DEBUG - [Bootstrap:17:34:01.083] Python: 3.12.4
2025-12-27 17:34:02 - bootstrap_logger - DEBUG - [Bootstrap:17:34:01.243] Core imports completed
...
2025-12-27 17:34:02 - bootstrap_logger - INFO - ======================================
2025-12-27 17:34:02 - bootstrap_logger - INFO - [Bootstrap] Injection complete (1.199s total)
2025-12-27 17:34:02 - bootstrap_logger - INFO - ======================================
```

**Benefits**:
- ✅ Complete audit trail (entry → init → execution)
- ✅ Debug-friendly (see exact failure point before crash)
- ✅ Performance tracking (timestamps show bottlenecks)
- ✅ Clean UX (verbose only when requested)
- ✅ Emergency fallback (never lose diagnostic info)

**Files Modified**:
- `zSys/bootstrap_logger.py` - New file (+212 lines)
- `zSys/__init__.py` - Added BootstrapLogger export
- `main.py` - Bootstrap logger integration (+10 lines setup)

**Testing**:
- ✅ `zolo config --verbose` - Shows bootstrap process
- ✅ `zolo config` - Silent (no bootstrap output)
- ✅ `zcli-framework.log` - Bootstrap logs injected properly
- ✅ All commands support --verbose flag

**Time**: 30 minutes

---

### 📊 Summary of Completed Work

**Total Changes**:
- ✅ 6 major improvements implemented
- ✅ 10 specific actions completed
- ✅ ~86 lines simplified/removed from main.py (migration refactor)
- ✅ 2 entry points consolidated
- ✅ Clean CLI UX achieved
- ✅ Separation of concerns enforced (CLI vs Subsystem layers)
- ✅ Complete pre-boot logging with --verbose support
- ✅ Bootstrap logger with framework.log injection

**Files Modified**:
- `main.py` - Added `display_info()`, removed `shell_main()`, simplified `handle_config_command()`, changed default routing, refactored `handle_migrate_command()`, integrated bootstrap logger (264 → 222 lines including bootstrap setup)
- `pyproject.toml` - Removed `zShell` entry point
- `zCLI/L3_Abstraction/n_zData/zData.py` - Added `cli_migrate()` method (+140 lines)
- `zSys/bootstrap_logger.py` - New bootstrap logger (+212 lines)
- `zSys/__init__.py` - Added BootstrapLogger export

**Time Spent**: ~90 minutes

**Lines Removed from main.py**: ~86 lines (migration refactor)

**Lines Added**:
- zData: ~140 lines (properly organized in subsystem)
- zSys: ~212 lines (bootstrap logger - Layer 0 utility)

---

### 🎯 Current CLI Structure (Clean & Minimal)

```bash
$ zolo                    # Info banner (version, author, license)
$ zolo --version          # Version only
$ zolo --help             # Full help

$ zolo shell [--verbose]          # Interactive shell (all modifications here)
$ zolo config [--verbose]         # Quick config inspection (read-only)
$ zolo ztests [--verbose]         # Test runner
$ zolo migrate <app> [--verbose]  # Schema migrations (delegated to zData.cli_migrate)
$ zolo uninstall [--verbose]      # Uninstall wizard
```

**--verbose flag**: Shows bootstrap process on stdout (colored, timestamped)

**Design Philosophy Achieved**: 
- ✅ CLI = Read-only operations + Orchestration + Delegation
- ✅ Shell = Interactive modifications
- ✅ Clean separation of concerns
- ✅ Subsystems own their UX (e.g., zData.cli_migrate, zShell.run_shell, zConfig.show_*)
- ✅ Complete logging (pre-boot → init → execution in zcli-framework.log)
- ✅ Debug-friendly (--verbose shows bootstrap process)

---

### 📊 Original Audit (For Reference)

#### File Structure
**File**: `main.py` (267 lines)

**Argparser Section**: Lines 203-262 (60 lines)

**Handler Functions** (BEFORE refactor):
- `handle_shell_command()` - Lines 7-10 → ✅ Kept (already clean)
- `handle_config_command(args)` - Lines 24-45 → ✅ Simplified (removed 22 lines)
- `handle_ztests_command()` - Lines 48-74 → 🟡 Keep as-is (tests review in Phase 1)
- `handle_migrate_command(args)` - Lines 77-185 → ✅ Refactored (109 → 18 lines)
- `handle_uninstall_command()` - Lines 188-200 → 🟡 Review later
- `main()` - Lines 203-266 → ✅ Updated (info banner, routing)

---

### 🔍 Issues Found

#### 🔴 **CRITICAL: Inconsistent Patterns**

1. **Mixed Handler Signatures**:
   ```python
   handle_shell_command()           # No args
   handle_config_command(args)      # Takes args
   handle_ztests_command()          # No args
   handle_migrate_command(args)     # Takes args
   handle_uninstall_command()       # No args (but parser has options!)
   ```
   **Problem**: Some handlers take `args`, some don't. Confusing and inconsistent.

2. **Unused Parser Arguments**:
   - `shell --config` - Defined but NEVER used in `handle_shell_command()`
   - `uninstall --clean` - Defined but NEVER used in `handle_uninstall_command()`
   - `uninstall --dependencies` - Defined but NEVER used in `handle_uninstall_command()`
   **Problem**: Dead code creates confusion about what CLI actually supports.

3. **Duplicate Shell Entry Points**:
   - `handle_shell_command()` - Called from `main()` (line 252, 262)
   - `shell_main()` - Entry point for `zShell` command (line 13-16)
   **Problem**: Identical code duplicated. Should call same function.

#### 🟡 **MEDIUM: Clarity & Maintainability**

4. **Giant `handle_migrate_command()` Function**:
   - **Lines**: 109 lines (77-185)
   - **Complexity**: Too high for a CLI handler
   - **Responsibility**: Mixing CLI validation, display banners, schema discovery display, AND business logic
   **Recommendation**: Extract display/formatting logic to helper functions.

5. **Inconsistent Error Handling**:
   - `handle_ztests_command()`: Creates temp `zCLI` instance for errors (lines 59-61)
   - `handle_migrate_command()`: Creates temp `zCLI` instance for errors (lines 91-93)
   - Others: No explicit error handling
   **Problem**: Inconsistent approach to error display.

6. **Return Value Inconsistency**:
   - Most handlers: Return `None` implicitly
   - `handle_ztests_command()`: Returns `1` on error (line 61)
   - `handle_migrate_command()`: Returns `0` or `1` (line 185)
   - `main()`: Sometimes returns values, sometimes doesn't (lines 256, 258)
   **Problem**: Unclear exit code behavior.

7. **Subparser Structure**:
   ```python
   # Flat subparsers
   shell_parser = subparsers.add_parser("shell", ...)
   config_parser = subparsers.add_parser("config", ...)
   
   # But config has NESTED subparsers
   config_subparsers = config_parser.add_subparsers(dest="config_type")
   machine_parser = config_subparsers.add_parser("machine", ...)
   env_parser = config_subparsers.add_parser("environment", ...)
   ```
   **Problem**: Mixed one-level and two-level command structures. Could be cleaner.

#### 🟢 **LOW: Style & Polish**

8. **Help Text Consistency**:
   - Some: `"Start interactive zCLI shell"` (descriptive)
   - Some: `"Run schema migrations for an application"` (longer)
   - Some: `"Uninstall zolo-zcli framework"` (terse)
   **Recommendation**: Standardize help text style (imperative vs descriptive).

9. **Missing Help Text**:
   - `migrate --history` flag defined but NOT implemented
   **Problem**: Misleading to users.

---

### 💡 Recommendations

#### Quick Wins (< 1 hour)

**A. Fix Handler Signatures - Make Consistent**
```python
# Option 1: All handlers take args (recommended)
def handle_shell_command(args):
def handle_ztests_command(args):
def handle_uninstall_command(args):

# Then call: handle_shell_command(args)
```
**Benefits**: Consistent, extensible, less surprising.

**B. Remove Dead Code**
- Remove `shell --config` argument (not used)
- Remove `uninstall --clean` and `--dependencies` (not used, launcher handles interactively)
- Remove `migrate --history` (not implemented)

**C. Consolidate Shell Entry Points**
```python
def shell_main() -> None:
    """Direct entry point for zShell command."""
    cli = zCLI()
    cli.run_shell()

def handle_shell_command(args):
    """Handle shell command from main CLI."""
    shell_main()  # Reuse!
```

**D. Standardize Return Values**
- `main()` should ALWAYS return `int` or `None` consistently
- All handlers should return `Optional[int]` (0=success, 1=error, None=success)
- Update type hints: `def main() -> None:` should be `def main() -> int:`

**E. Extract Banner/Display Logic from `handle_migrate_command()`**
```python
# Current: 109 lines with mixed concerns
def handle_migrate_command(args): ...

# Better: Extract display helpers
def _display_migration_banner(z, app_file): ...
def _display_schemas(z, schemas): ...
def _display_migration_results(z, result): ...

def handle_migrate_command(args):
    # Now < 40 lines of pure orchestration
```

#### Medium Refactors (1-2 hours)

**F. Consider Extracting Argparser Setup**
- Current: All parser definition in `main()`
- Better: Extract to function for testability
```python
def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(...)
    # ... all subparser logic ...
    return parser

def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    # ... routing logic ...
```
**Benefits**: Can test parser in isolation, cleaner main().

**G. Unified Error Display Helper**
```python
def _display_cli_error(message: str) -> int:
    """Display CLI error and return error code."""
    temp_z = zCLI({'zMode': 'Terminal'})
    temp_z.display.text(f"❌ {message}")
    return 1

# Then use everywhere:
if not Path(app_file).exists():
    return _display_cli_error(f"App file not found: {app_file}")
```

**H. Flatten or Clarify Config Subcommands**
- Current: `zolo config machine key value`
- Consider: `zolo machine key value` (simpler) OR keep but document rationale
- Issue: Only `config` has nested structure, makes it feel "special"

---

### ✅ What's Actually Good

**Strengths to Preserve**:
1. ✅ **Thin Orchestration**: Handlers delegate to `zCLI` methods (good!)
2. ✅ **Docstrings**: Every function documented
3. ✅ **Type Hints**: Using `-> None`, `-> int` (partially)
4. ✅ **Separation**: Handlers separated from parser definition
5. ✅ **Centralized Routing**: Single `if/elif` chain in `main()` (lines 251-262)

---

### 🎯 Remaining Tasks (Optional - From Original Audit)

These are **optional refinements** from the original audit. The core issues are resolved!

#### Optional 0.6.5: Additional Quick Fixes (~10 min)
- [x] ~~Consolidate `shell_main()` and `handle_shell_command()`~~ ✅ DONE
- [x] ~~Simplify config command~~ ✅ DONE (beyond original scope!)
- [ ] Standardize handler signatures (all take `args`) - **Optional**
- [ ] Remove unused CLI arguments (`shell --config`, `uninstall` flags, `migrate --history`) - **Optional**
- [ ] Fix return value consistency in `main()` - **Optional**

**Status**: Major issues resolved. Remaining items are polish.

---

#### Optional 0.6.6: Extract Migration Display Logic (~30 min) 🟡 OPTIONAL
- [ ] Create `_display_migration_banner(z, app_file)`
- [ ] Create `_display_schemas(z, schemas)`
- [ ] Create `_display_migration_results(z, result)`
- [ ] Refactor `handle_migrate_command()` to use helpers (reduce from 109 lines to ~40 lines)

**Rationale**: Would improve readability, but `handle_migrate_command()` works fine as-is

**Priority**: Low (Nice to have, not critical)

---

#### Optional 0.6.7: Error Handling (~20 min) 🟡 OPTIONAL
- [ ] Create `_display_cli_error()` helper
- [ ] Standardize error handling across all handlers
- [ ] Update all handlers to return proper exit codes

**Rationale**: Current error handling works, standardization would be polish

**Priority**: Low (Consistency improvement)

---

#### Optional 0.6.8: Parser Extraction (~20 min) 🟡 OPTIONAL
- [ ] Extract parser definition to `_build_parser()`
- [ ] Add docstring explaining structure
- [ ] Consider future: Move to `zSys/cli_parser.py` if it grows

**Rationale**: Testability improvement, but current structure is maintainable

**Priority**: Low (Future enhancement)

---

### 📏 Complexity Metrics

**Current**:
- `main()`: 60 lines (parser def + routing)
- `handle_migrate_command()`: 109 lines (TOO LONG)
- Total argparser code: ~180 lines across 7 functions

**After Cleanup** (estimated):
- `main()`: 40 lines (extracted parser + cleaner routing)
- `handle_migrate_command()`: 40 lines (extracted display helpers)
- `_build_parser()`: 60 lines (extracted)
- Helper functions: 3-4 small functions (~10 lines each)
- Total: ~200 lines but MUCH more readable/testable

---

### 🧪 Testing Considerations

**Current Testing**:
- No explicit tests for argparser
- Manual testing via `zolo` commands

**After Refactor**:
- Can test `_build_parser()` in isolation
- Can test handlers with mock `args` objects
- Can test display helpers independently

---

---

### ✅ 0.6.7: Unified Logging System ⭐ **COMPLETE**

**Problem**: Three different logging systems with inconsistent formats:
- Bootstrap logger: Custom format with colors
- Framework logger: Detailed format with custom `FileNameFormatter`
- App logger: Simple format with custom formatter
- ConsoleLogger: Basic `[LEVEL] message` format

**Inspiration**: Israel Levin's [mkma](https://github.com/israellevin/mkma/blob/master/initramfs_init.sh) logging pattern
```bash
_log() {
    level=$1
    shift
    message="$(date) [mkma.sh init]: $*"
    echo "<$level>$message" > /dev/kmsg
}
```

**Key Pattern**: Single `_log()` function = single source of truth for format

---

#### Implementation

**Created**: `zSys/logger_formats.py` - Single Source of Truth

```python
def format_log_message(
    timestamp: datetime,
    level: str,
    context: str,
    message: str,
    include_details: bool = False,
    filename: Optional[str] = None,
    lineno: Optional[int] = None
) -> str:
    """
    Single format function for ALL zCLI logging.
    
    Format: TIMESTAMP [CONTEXT] LEVEL: MESSAGE
    Format (detailed): TIMESTAMP [CONTEXT] LEVEL [FILE:LINE]: MESSAGE
    """
```

**Updated**:
1. ✅ `bootstrap_logger.py` - Uses `format_log_message()` and `format_bootstrap_verbose()`
2. ✅ `config_logger.py` - Uses `UnifiedFormatter` (replaced `FileNameFormatter`)
3. ✅ `logger.py` (ConsoleLogger) - Enhanced to use `format_log_message()`

---

#### Results - Consistent Output Everywhere

**Bootstrap Logger** (console, --verbose):
```
[18:14:55] [Bootstrap] zolo-zcli entry point started
[18:14:55] [Bootstrap] Python: 3.12.4
```

**Framework Logger** (file: zcli-framework.log):
```
2025-12-27 18:15:40 [Framework] DEBUG [zCLI.py:359]: Session initialized
2025-12-27 18:15:40 [Framework] INFO [bootstrap_logger.py:110]: Pre-boot log injection
```

**App Logger** (file: zolo.log):
```
2025-12-27 18:15:40 [App] DEBUG [config_logger.py:508]: No models/ folder found
2025-12-27 18:15:40 [App] INFO [config_logger.py:519]: Initialized
```

**ConsoleLogger** (WSGI workers):
```
2025-12-27 18:16:00 [WSGI] INFO: Server started
2025-12-27 18:16:00 [WSGI] ERROR: Connection failed
```

---

#### Benefits (Israel's Pattern Applied)

1. ✅ **Single Source of Truth** - One `format_log_message()` function
2. ✅ **Consistency** - All logs use same format: `TIMESTAMP [CONTEXT] LEVEL: MESSAGE`
3. ✅ **Machine-Parseable** - Easy to grep/awk/parse
4. ✅ **Context Clear** - `[Bootstrap]`, `[Framework]`, `[App]`, `[WSGI]` immediately visible
5. ✅ **Simple** - No complex formatter classes, just a function
6. ✅ **Maintainable** - Change format once, affects all loggers

---

#### Code Quality Impact

**Before** (3 different formats):
- `bootstrap_logger.py`: Custom color formatting (170 lines)
- `config_logger.py`: `FileNameFormatter` class + format strings (665 lines)
- `logger.py`: Basic `[LEVEL] message` (39 lines)

**After** (1 unified format):
- `logger_formats.py`: Single format function + `UnifiedFormatter` class (196 lines)
- `bootstrap_logger.py`: Calls `format_log_message()` (simplified)
- `config_logger.py`: Uses `UnifiedFormatter` (removed 50+ lines of formatter logic)
- `logger.py`: Enhanced to use `format_log_message()` (better output)

**Net Result**: More consistent, more maintainable, easier to understand

---

#### Files Changed
- ✅ Created: `zSys/logger_formats.py` (196 lines)
- ✅ Updated: `zSys/bootstrap_logger.py` (now uses unified format)
- ✅ Updated: `zSys/logger.py` (ConsoleLogger enhanced)
- ✅ Updated: `zCLI/L1_Foundation/a_zConfig/zConfig_modules/config_logger.py` (uses UnifiedFormatter)
- ✅ Updated: `zSys/__init__.py` (exports new logger_formats module)

**Testing**:
- ✅ `zolo --verbose` - Bootstrap logger works with unified format
- ✅ `zolo config --verbose` - Framework logger uses unified format
- ✅ Framework log file (`zcli-framework.log`) - Consistent format
- ✅ App log file (`zolo.log`) - Consistent format
- ✅ ConsoleLogger - Tested with python3 script

**Time Spent**: ~1.5 hours | **Impact**: High (architectural improvement)

---

### 📊 Phase 0.6 Progress Summary

**Completed** (6 major improvements):
- ✅ Info banner on `zolo` (no shell auto-launch)
- ✅ Simplified installation type display ("editable", "uv", "standard")
- ✅ Removed `zShell` standalone command (consolidated entry points)
- ✅ Simplified `config` command (removed 33+ lines, now read-only)
- ✅ Production mode for config (clean output, no verbose logs)
- ✅ **Unified Logging System** (centralized format, Israel's mkma-inspired pattern)

**Remaining** (Optional polish items):
- 🟡 Optional 0.6.5: Additional Quick Fixes (~10 min) - **OPTIONAL**
- 🟡 Optional 0.6.6: Extract Migration Display Logic (~30 min) - **OPTIONAL**
- 🟡 Optional 0.6.7: Error Handling Standardization (~20 min) - **OPTIONAL**
- 🟡 Optional 0.6.8: Parser Extraction (~20 min) - **OPTIONAL**

**Time Spent**: ~2 hours | **Remaining** (if pursuing polish): ~1-1.5 hours

**Status**: ✅ **CORE OBJECTIVES ACHIEVED** - Remaining items are optional refinements

---

### 🎯 Next Action Options

**RECOMMENDED: Option E - Move to Next Phase**
Phase 0.6 core objectives are complete! Time to move forward.

**Option E: Move to Next Phase** ⭐ **RECOMMENDED**
- Phase 0.5.2: Audit pyproject.toml (~30 min)
- Phase 1: Start layer audits (major work)
- Or: Close out Phase 0 entirely and celebrate! 🎉

**Option A-D: Optional Polish (if desired)**
Only pursue if you want extra refinement:

**Option A: Additional Quick Fixes (Optional 0.6.5)** 🟡
- Remove unused CLI args
- Standardize handler signatures
- Fix return value consistency
**Time**: 10 minutes | **Impact**: Low (polish)

**Option B: Extract Migration Display (Optional 0.6.6)** 🟡
- Break down `handle_migrate_command()` (109 lines → ~40 lines)
**Time**: 30 minutes | **Impact**: Medium (readability, not critical)

**Option C: Standardize Error Handling (Optional 0.6.7)** 🟡
- Create unified error display helper
**Time**: 20 minutes | **Impact**: Low (consistency)

**Option D: Extract Parser (Optional 0.6.8)** 🟡
- Move parser setup to `_build_parser()`
**Time**: 20 minutes | **Impact**: Low (testability)

---

**Phase 0.6 Completion Criteria**:

**Core Objectives** (All Achieved ✅):
- ✅ `zolo` default behavior improved (info banner, not shell)
- ✅ Installation type display simplified
- ✅ Duplicate entry points removed (`zShell` consolidated)
- ✅ Config command simplified (read-only, clean output)
- ✅ **Unified logging system** (single source of truth, mkma-inspired)
- ✅ Testing: `zolo --help` works ✓
- ✅ Testing: `zolo` works ✓
- ✅ Testing: `zolo shell` works ✓
- ✅ Testing: `zolo config` works ✓ (clean output)
- ✅ Testing: All loggers use consistent format ✓

**Optional Refinements** (Not Critical):
- 🟡 Handler signature consistency (optional polish)
- 🟡 Dead CLI arguments removal (optional cleanup)
- 🟡 `handle_migrate_command()` extraction (optional refactor)
- 🟡 Error handling standardization (optional consistency)
- 🟡 Return value consistency (optional polish)
- 🟡 Parser extraction (optional testability)

**Result**: ✅ **PHASE 0.6 CORE OBJECTIVES COMPLETE**

**Time Spent**: ~2 hours | **Estimated for Optional Polish**: 1-1.5 hours (if desired)

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

