# zCLI/subsystems/zDisplay/zDisplay_modules/events/__init__.py
"""
zDisplay Event Packages - Modular UI Event Architecture (v1.5.4+)

This package contains 8 specialized event modules that provide structured, category-based
UI event handling for the zDisplay subsystem. All events support dual-mode I/O (Terminal
+ Bifrost WebSocket) and are orchestrated by `display_events.py` (zEvents class).

═══════════════════════════════════════════════════════════════════════════
PACKAGE ARCHITECTURE - 8 EVENT CATEGORIES
═══════════════════════════════════════════════════════════════════════════

The event packages are organized into three architectural tiers based on dependencies:

**Tier 1 - FOUNDATION (No Dependencies):**
    display_event_outputs.py (BasicOutputs)
        • Provides: header(), text()
        • Role: Foundation for all formatted output
        • Used by: ALL 7 other event packages (most critical!)
        • Dependencies: None (foundation layer)

**Tier 2 - COMPLEX (Compose BasicOutputs):**
    display_event_signals.py (Signals)
        • Provides: error(), warning(), success(), info(), zMarker()
        • Role: Colored feedback messages with semantic meaning
        • Dependencies: BasicOutputs
    
    display_event_inputs.py (BasicInputs)
        • Provides: selection() for interactive user choices
        • Role: Fundamental input collection
        • Dependencies: BasicOutputs
    
    display_event_data.py (BasicData)
        • Provides: list(), json_data() for structured data display
        • Role: Data presentation (lists, JSON)
        • Dependencies: BasicOutputs

**Tier 3 - LEAF (Compose Multiple Packages):**
    display_event_timebased.py (TimeBased)
        • Provides: progress_bar(), spinner(), swiper()
        • Role: Temporal, non-blocking UI feedback
        • Dependencies: BasicOutputs
    
    display_event_advanced.py (AdvancedData)
        • Provides: zTable() with pagination support
        • Role: Complex data display with navigation
        • Dependencies: BasicOutputs
    
    [REMOVED] display_event_auth.py (zAuthEvents)
        • Reason: Violated separation of concerns
        • Auth UI now composed in zAuth subsystem using generic display events
        • zDisplay remains domain-agnostic (no auth-specific knowledge)
    
    display_event_system.py (zSystem)
        • Provides: zSession(), zCrumbs(), zMenu(), zDialog(), zDeclare()
        • Role: System-level introspection & navigation
        • Dependencies: BasicOutputs + Signals + BasicInputs (most dependencies!)


═══════════════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (Bottom-Up)
═══════════════════════════════════════════════════════════════════════════

    BasicOutputs (Foundation - Tier 1)
           ↑
           ├─────────────────────────────────────────────────────┐
           │                                                       │
      Signals (Tier 2)    BasicInputs (Tier 2)    BasicData (Tier 2)
           ↑                     ↑                        ↑
           │                     │                        │
           ├─────────────────────────────────────┐           │
           │                                             │           │
        zSystem (Tier 3)                                 │           │
                                                           │
    TimeBased (Tier 3)              AdvancedData (Tier 3)───────────┘


═══════════════════════════════════════════════════════════════════════════
ORCHESTRATION PATTERN
═══════════════════════════════════════════════════════════════════════════

All event packages are instantiated and cross-wired by `display_events.py` (zEvents),
which acts as the **orchestrator** and **composition layer**:

    display_events.py (zEvents class)
        ├─ Instantiates: All 8 event package classes
        ├─ Cross-wires: Sets BasicOutputs/Signals/BasicInputs refs on dependent packages
        ├─ Exposes: Convenience delegate methods (e.g., error(), success(), selection())
        └─ Coordinates: Cross-package communication and dependency injection

Usage Flow:
    zDisplay → zEvents → Event Packages → zPrimitives → Terminal/Bifrost

Example:
    # Via zEvents orchestrator
    display.zEvents.Signals.error("Error occurred")
    
    # Via zEvents delegate (convenience)
    display.zEvents.error("Error occurred")


═══════════════════════════════════════════════════════════════════════════
USAGE EXAMPLES
═══════════════════════════════════════════════════════════════════════════

1. Direct Import (Advanced Use):
    ```python
    from zCLI.subsystems.zDisplay.zDisplay_modules.events import display_event_outputs
    from zCLI.subsystems.zDisplay.zDisplay_modules.events import display_event_signals
    
    # Access classes directly (requires manual wiring)
    BasicOutputs = display_event_outputs.BasicOutputs(display_instance)
    Signals = display_event_signals.Signals(display_instance)
    ```

2. Via zEvents Orchestrator (Recommended):
    ```python
    # Access via zDisplay.zEvents (automatically wired)
    display.zEvents.BasicOutputs.text("Hello World")
    display.zEvents.Signals.success("Operation complete")
    display.zEvents.BasicInputs.selection(prompt="Choose:", options=["A", "B"])
    display.zEvents.zSystem.zSession(session_data)
    ```

3. Via zEvents Delegates (Convenience):
    ```python
    # Shorthand convenience methods
    display.zEvents.text("Hello World")          # → BasicOutputs.text()
    display.zEvents.success("Complete")          # → Signals.success()
    display.zEvents.selection(...)               # → BasicInputs.selection()
    ```

4. Via zDisplay Delegates (Primary API):
    ```python
    # Most convenient user-facing API
    display.text("Hello World")
    display.success("Complete")
    display.selection(...)
    display.zSession(session_data)
    ```


═══════════════════════════════════════════════════════════════════════════
IMPORT ORDER RATIONALE
═══════════════════════════════════════════════════════════════════════════

Imports are organized by dependency tier (foundation → complex → leaf) to make the
architecture immediately clear and to facilitate dependency-aware refactoring.

This ordering mirrors the audit/implementation sequence used during Week 6.4 refactoring,
ensuring each package's dependencies were already A+ grade before auditing it.


═══════════════════════════════════════════════════════════════════════════
CROSS-REFERENCE
═══════════════════════════════════════════════════════════════════════════

Primary Files:
    display_events.py       - Orchestrator (instantiates & cross-wires all event packages)
    display_primitives.py   - I/O layer (Terminal/Bifrost dual-mode switching)
    display_delegates.py    - User-facing API (convenience methods)
    zDisplay.py             - Main facade (entry point)

Week 6.4 Refactoring:
    All 8 event packages were refactored to A+ grade during Week 6.4 (v1.5.4+):
    - 100% type hint coverage
    - Comprehensive docstrings (80-340 lines)
    - Constants-based (0 magic strings)
    - DRY refactoring (helper methods)
    - zSession/zAuth/zConfig integration


═══════════════════════════════════════════════════════════════════════════
PACKAGE METADATA
═══════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.5.4"
__author__ = "zCLI Team"
__description__ = "zDisplay Event Packages - Modular UI Event Architecture"


# ═══════════════════════════════════════════════════════════════════════════
# TIER 1 - FOUNDATION (No Dependencies)
# ═══════════════════════════════════════════════════════════════════════════

from . import display_event_outputs      # BasicOutputs - header(), text() [FOUNDATION]


# ═══════════════════════════════════════════════════════════════════════════
# TIER 2 - COMPLEX (Compose BasicOutputs)
# ═══════════════════════════════════════════════════════════════════════════

from . import display_event_signals      # Signals - error(), warning(), success(), info(), zMarker()
from . import display_event_inputs       # BasicInputs - selection() for interactive choices
from . import display_event_data         # BasicData - list(), json_data() for structured data


# ═══════════════════════════════════════════════════════════════════════════
# TIER 3 - LEAF (Compose Multiple Packages)
# ═══════════════════════════════════════════════════════════════════════════

from . import display_event_timebased    # TimeBased - progress_bar(), spinner(), swiper()
from . import display_event_advanced     # AdvancedData - zTable() with pagination
from . import display_event_system       # zSystem - zSession(), zCrumbs(), zMenu(), zDialog(), zDeclare()


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'display_event_outputs',      # Tier 1 - Foundation (header, text)
    'display_event_signals',      # Tier 2 - Colored feedback (error, warning, success, info, zMarker)
    'display_event_inputs',       # Tier 2 - User input (selection)
    'display_event_data',         # Tier 2 - Data display (list, json_data)
    'display_event_timebased',    # Tier 3 - Temporal UI (progress_bar, spinner, swiper)
    'display_event_advanced',     # Tier 3 - Complex data (zTable with pagination)
    'display_event_system'        # Tier 3 - System introspection (zSession, zCrumbs, zMenu, zDialog, zDeclare)
]
