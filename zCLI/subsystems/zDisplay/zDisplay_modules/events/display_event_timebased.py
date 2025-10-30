# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_timebased.py
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    zDisplay TimeBased Events Package                      ║
║                 Progress, Spinners, and Temporal Feedback                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

ARCHITECTURE OVERVIEW
─────────────────────────────────────────────────────────────────────────────

What Makes This "TimeBased"?
    The "TimeBased" naming was chosen over "Widgets" to reflect the
    distinguishing characteristic of these UI elements: they provide temporal,
    non-blocking feedback for operations that take TIME to complete.
    
    Unlike BasicOutputs (instant display) or BasicInputs (wait for user),
    TimeBased events are ANIMATED and update over time while work happens in
    the background.

Temporal UI Elements Provided:
    1. progress_bar()         - Visual progress indicator with percentage/ETA
    2. spinner()              - Animated loading spinner (context manager)
    3. progress_iterator()    - Wrap iterable with auto-updating progress bar
    4. indeterminate_progress() - Spinner for unknown-duration operations
    5. swiper()               - Interactive content carousel with auto-advance

DUAL-MODE PATTERN (Terminal + Bifrost)
─────────────────────────────────────────────────────────────────────────────

Terminal Mode (Synchronous):
    - ANSI escape sequences: Carriage returns (\r), clear screen (\033[2J)
    - Box-drawing characters: ╔═╗║╠╣╚═╝ (Unicode)
    - Animation via threading: Background threads update display
    - Non-blocking input: termios + select for keyboard navigation
    - Live updates: Overwrite same line with \r for progress bars
    - Context managers: Automatic cleanup with try/finally

Bifrost Mode (Asynchronous WebSocket):
    - WebSocket events: progress_bar, spinner_start, swiper_init, etc.
    - Frontend handles rendering: React components receive events
    - Async-safe: asyncio.run_coroutine_threadsafe for event loop
    - Touch gestures: Swipe left/right for swiper navigation
    - Auto-advance: Configurable delays for automatic progression
    - State tracking: _active_progress, _active_spinners, _active_swipers

LAYER POSITION (Event Package Layer - Depends on BasicOutputs)
─────────────────────────────────────────────────────────────────────────────

    Layer 1: zDisplay.py (Facade)
            ↓
    Layer 2: display_events.py (Composition)
            ↓
    Layer 3: display_event_timebased.py ← YOU ARE HERE
            ↓
    Layer 4: display_event_outputs.py (BasicOutputs fallback)
            ↓
    Foundation: display_primitives.py (Dual-mode I/O)

    Dependencies:
        - display_primitives.py (zPrimitives): Terminal I/O (write_raw, write_line)
        - zColors: ANSI color codes
        - BasicOutputs: Fallback for non-critical output (header, text)
        - zComm: WebSocket broadcast for Bifrost mode

    Used by:
        - display_events.py (delegates to all 5 methods)
        - End-user code (via display.progress_bar, etc.)

TERMINAL PARADIGM (How Time-Based Events Work in Console)
─────────────────────────────────────────────────────────────────────────────

Challenge: Terminals are line-based and synchronous by default
Solution:  Multi-threading + ANSI escape codes for animation

Progress Bars:
    1. Use \r (carriage return) to overwrite same line
    2. Caller updates in loop: for i in range(100): progress_bar(i, 100)
    3. No thread needed - caller controls update frequency

Spinners:
    1. Context manager: with spinner("Loading"): do_work()
    2. Background thread animates frames while do_work() runs
    3. Automatic cleanup: stop thread + print checkmark

Swiper (Interactive Carousel):
    1. Background thread: auto-advances slides every N seconds
    2. Foreground thread: non-blocking keyboard input (termios + select)
    3. Navigation: Arrow keys (◀▶), Number keys (1-9), Pause (p), Quit (q)
    4. Box-drawing UI: Beautiful bordered display with live status
    5. Windows fallback: Basic Enter/q navigation (no termios)

BIFROST PROTOCOL (WebSocket Event Structure)
─────────────────────────────────────────────────────────────────────────────

Progress Bar Events:
    {
        "event": "progress_bar" | "progress_complete",
        "progressId": "progress_Processing_Files",
        "current": 60,
        "total": 100,
        "label": "Processing Files",
        "showPercentage": true,
        "showETA": true,
        "eta": "2m 30s",
        "color": "GREEN",
        "container": "#app"
    }

Spinner Events:
    {
        "event": "spinner_start" | "spinner_stop",
        "spinnerId": "spinner_Loading_abc123",
        "label": "Loading data",
        "style": "dots",
        "container": "#app"
    }

Swiper Events:
    {
        "event": "swiper_init" | "swiper_update" | "swiper_complete",
        "swiperId": "swiper_Tutorial_xyz789",
        "label": "Tutorial",
        "slides": ["Slide 1", "Slide 2", "Slide 3"],
        "currentSlide": 0,
        "totalSlides": 3,
        "autoAdvance": true,
        "delay": 3,
        "loop": false,
        "container": "#app"
    }

THREAD SAFETY
─────────────────────────────────────────────────────────────────────────────

    Threading Usage:
        - spinner(): Background thread animates frames
        - swiper(): Background thread for auto-advance
        - threading.Event(): Clean shutdown coordination
        - daemon=True: Threads exit when main thread exits
        - join(timeout=0.5): Max 500ms wait on cleanup

    Asyncio Integration (Bifrost):
        - asyncio.get_running_loop(): Check for active event loop
        - asyncio.run_coroutine_threadsafe(): Thread-safe event loop access
        - Graceful fallback: Silent failure if no event loop

    State Tracking:
        - _active_progress: Dict[str, Dict] (progress bars by ID)
        - _active_spinners: Dict[str, Dict] (spinners by ID)
        - _active_swipers: Dict[str, Dict] (swipers by ID)
        - Cleanup: Delete from dict when complete

FUTURE EXTENSIONS (Time-Based Event Ideas)
─────────────────────────────────────────────────────────────────────────────

    1. typing_indicator(): "User is typing..." with animated dots
    2. countdown_timer(): Countdown from N seconds to 0
    3. marquee(): Scrolling text banner (left-to-right)
    4. toast(): Auto-dismissing notification (5-second display)
    5. pulse_indicator(): Breathing/pulsing dot for "waiting"
    6. slide_transition(): Animated slide-in/slide-out for content

USAGE EXAMPLES
─────────────────────────────────────────────────────────────────────────────

Progress Bar (Manual Updates):
    ```python
    import time
    total = 100
    start = time.time()
    for i in range(total + 1):
        display.progress_bar(
            current=i,
            total=total,
            label="Processing files",
            show_percentage=True,
            show_eta=True,
            start_time=start,
            color="GREEN"
        )
        time.sleep(0.05)
    ```

Spinner (Context Manager):
    ```python
    with display.spinner("Loading data", style="dots"):
        data = fetch_large_dataset()
        process_data(data)
    # Automatically prints "Loading data ✓" on exit
    ```

Progress Iterator (Automatic):
    ```python
    items = ["file1.txt", "file2.txt", "file3.txt"]
    for item in display.progress_iterator(items, "Processing files"):
        process_file(item)
    # Progress updates automatically for each iteration
    ```

Swiper (Interactive Carousel):
    ```python
    slides = [
        "Welcome to zCLI!",
        "Feature 1: Progress Bars",
        "Feature 2: Spinners",
        "Thank you!"
    ]
    display.swiper(
        slides,
        label="Getting Started",
        auto_advance=True,
        delay=3,
        loop=True
    )
    # Auto-advances every 3s, user can navigate with arrow keys
    ```

MODULE CONSTANTS
─────────────────────────────────────────────────────────────────────────────
See constants section below for all 45+ defined constants used throughout.

VERSION INFO
─────────────────────────────────────────────────────────────────────────────
Created:  Week 6.4 (zDisplay subsystem refactoring)
Upgraded: Week 6.4.11c (Industry-grade: type hints, constants, docstrings)
Line Count: 554 → ~700 lines (documentation & constants)
"""

import sys
import time
import threading
import asyncio
import json
import uuid
from contextlib import contextmanager
from typing import Any, Optional, List, Dict, Callable, Iterator

# ═══════════════════════════════════════════════════════════════════════════
#                              MODULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Mode Constants
MODE_BIFROST = "zBifrost"

# WebSocket Event Names
EVENT_PROGRESS_BAR = "progress_bar"
EVENT_PROGRESS_COMPLETE = "progress_complete"
EVENT_SPINNER_START = "spinner_start"
EVENT_SPINNER_STOP = "spinner_stop"
EVENT_SWIPER_INIT = "swiper_init"
EVENT_SWIPER_UPDATE = "swiper_update"
EVENT_SWIPER_COMPLETE = "swiper_complete"

# WebSocket Event Dictionary Keys
KEY_EVENT = "event"
KEY_PROGRESS_ID = "progressId"
KEY_CURRENT = "current"
KEY_TOTAL = "total"
KEY_LABEL = "label"
KEY_SHOW_PERCENTAGE = "showPercentage"
KEY_SHOW_ETA = "showETA"
KEY_ETA = "eta"
KEY_COLOR = "color"
KEY_CONTAINER = "container"
KEY_SPINNER_ID = "spinnerId"
KEY_STYLE = "style"
KEY_SWIPER_ID = "swiperId"
KEY_SLIDES = "slides"
KEY_CURRENT_SLIDE = "currentSlide"
KEY_TOTAL_SLIDES = "totalSlides"
KEY_AUTO_ADVANCE = "autoAdvance"
KEY_DELAY = "delay"
KEY_LOOP = "loop"

# Default Values
DEFAULT_LABEL_PROCESSING = "Processing"
DEFAULT_LABEL_LOADING = "Loading"
DEFAULT_LABEL_SLIDES = "Slides"
DEFAULT_CONTAINER = "#app"
DEFAULT_WIDTH = 50
DEFAULT_SWIPER_DELAY = 3
DEFAULT_SHOW_PERCENTAGE = True
DEFAULT_SHOW_ETA = False
DEFAULT_AUTO_ADVANCE = True
DEFAULT_LOOP = False
DEFAULT_SWIPER_WIDTH = 80
DEFAULT_THREAD_JOIN_TIMEOUT = 0.5
DEFAULT_ANIMATION_DELAY = 0.1
DEFAULT_SPINNER_STYLE = "dots"

# Progress Bar Characters
CHAR_FILLED = "█"
CHAR_EMPTY = "░"
CHAR_CHECKMARK = "✓"
CHAR_SPACE = " "

# Box Drawing Characters (Unicode)
BOX_TOP_LEFT = "╔"
BOX_TOP_RIGHT = "╗"
BOX_BOTTOM_LEFT = "╚"
BOX_BOTTOM_RIGHT = "╝"
BOX_HORIZONTAL = "═"
BOX_VERTICAL = "║"
BOX_LEFT_T = "╠"
BOX_RIGHT_T = "╣"

# ANSI Escape Sequences
ANSI_CLEAR_SCREEN = "\033[2J"
ANSI_HOME = "\033[H"
ANSI_CARRIAGE_RETURN = "\r"

# Swiper Navigation Commands
SWIPER_CMD_PREV = "p"
SWIPER_CMD_NEXT = "n"
SWIPER_CMD_PAUSE = "p"
SWIPER_CMD_QUIT = "q"

# Swiper Escape Sequences
ESC_KEY = "\x1b"
ARROW_RIGHT = "[C"
ARROW_LEFT = "[D"

# Swiper Status Messages
SWIPER_STATUS_PAUSED = "[PAUSED]"
SWIPER_STATUS_AUTO = "[AUTO-ADVANCE: {}s]"
SWIPER_STATUS_MANUAL = "[MANUAL]"

# Messages
MSG_SWIPER_FALLBACK = "\nPress Enter to advance, 'q' to quit..."
MSG_BIFROST_INITIALIZED = "Navigate using touch gestures on the web interface.\n"
MSG_SWIPER_COMPLETED = "\n✓ {} completed!\n"

# Spinner Style Names
STYLE_DOTS = "dots"
STYLE_LINE = "line"
STYLE_ARC = "arc"
STYLE_ARROW = "arrow"
STYLE_BOUNCING_BALL = "bouncingBall"
STYLE_SIMPLE = "simple"


class TimeBased:
    """
    Time-based events for long-running operations with dual-mode support.
    
    COMPOSITION PATTERN
    ───────────────────────────────────────────────────────────────────────
    This class composes BasicOutputs (for fallback text display) and depends
    on zPrimitives (for low-level Terminal/Bifrost I/O). It provides temporal,
    animated UI feedback that updates over time while work happens in background.
    
    METHODS PROVIDED
    ───────────────────────────────────────────────────────────────────────
    1. progress_bar()          - Visual progress indicator with % and ETA
    2. spinner()               - Animated loading spinner (context manager)
    3. progress_iterator()     - Wrap iterable with auto-updating progress bar
    4. indeterminate_progress()- Spinner for unknown-duration operations
    5. swiper()                - Interactive content carousel with navigation
    
    DUAL-MODE SUPPORT
    ───────────────────────────────────────────────────────────────────────
    - Terminal: ANSI escape sequences, threading, non-blocking keyboard input
    - Bifrost: WebSocket events for React frontend, asyncio-safe broadcasts
    
    THREAD SAFETY
    ───────────────────────────────────────────────────────────────────────
    - Background threads for animation (spinner, swiper auto-advance)
    - threading.Event() for clean shutdown coordination
    - asyncio.run_coroutine_threadsafe() for event loop integration
    
    STATE TRACKING
    ───────────────────────────────────────────────────────────────────────
    - _active_progress: Dict[str, Dict] (progress bars by ID)
    - _active_spinners: Dict[str, Dict] (spinners by ID)
    - _active_swipers: Dict[str, Dict] (swipers by ID)
    
    Dependencies: zPrimitives, zColors, BasicOutputs (optional), zComm (Bifrost)
    """
    
    # Type declarations for class-level attributes
    display: Any  # Parent zDisplay instance
    zPrimitives: Any  # display_primitives.zPrimitives instance
    zColors: Any  # zColors module reference
    BasicOutputs: Optional[Any]  # display_event_outputs.BasicOutputs (set after init)
    _spinner_styles: Dict[str, List[str]]  # Spinner animation frames by style name
    _active_progress: Dict[str, Dict[str, Any]]  # Active progress bars (Bifrost)
    _active_spinners: Dict[str, Dict[str, Any]]  # Active spinners (Bifrost)
    _active_swipers: Dict[str, Dict[str, Any]]  # Active swipers (Bifrost)

    def __init__(self, display_instance: Any) -> None:
        """
        Initialize TimeBased with reference to parent display instance.
        
        Args:
            display_instance: Parent zDisplay instance (provides mode, zcli, etc.)
        
        Returns:
            None
        
        Sets up:
            - display: Parent reference
            - zPrimitives: Low-level I/O (write_raw, write_line)
            - zColors: ANSI color codes
            - BasicOutputs: None initially (set by display_events.py after init)
            - _spinner_styles: Dict of animation frames for 6 spinner styles
            - _active_*: Empty dicts for tracking Bifrost state
        """
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get references to other packages for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization
        
        # Spinner styles - animation frames for each style
        self._spinner_styles = {
            STYLE_DOTS: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            STYLE_LINE: ["-", "\\", "|", "/"],
            STYLE_ARC: ["◜", "◠", "◝", "◞", "◡", "◟"],
            STYLE_ARROW: ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
            STYLE_BOUNCING_BALL: ["⠁", "⠂", "⠄", "⠂"],
            STYLE_SIMPLE: [".", "..", "...", ""],
        }
        
        # Track active progress bars/spinners/swipers by ID (for zBifrost mode)
        self._active_progress = {}
        self._active_spinners = {}
        self._active_swipers = {}

    # ═══════════════════════════════════════════════════════════════════════
    #                              HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _is_bifrost_mode(self) -> bool:
        """
        Check if running in zBifrost (WebSocket) mode.
        
        Returns:
            bool: True if display.mode == "zBifrost", False otherwise
        
        Notes:
            - Gracefully handles missing display or mode attribute
            - Used to determine Terminal vs. Bifrost rendering path
        """
        if not self.display or not hasattr(self.display, 'mode'):
            return False
        return self.display.mode == MODE_BIFROST
    
    def _emit_websocket_event(self, event_data: Dict[str, Any]) -> None:
        """
        Emit a WebSocket event for zBifrost mode.
        
        Args:
            event_data: Event dictionary with 'event' key and payload
        
        Returns:
            None
        
        Notes:
            - Only sends if in Bifrost mode (_is_bifrost_mode() == True)
            - Uses zComm.broadcast_websocket() for async event loop
            - Thread-safe: asyncio.run_coroutine_threadsafe()
            - Graceful failure: Silent return if no event loop or zComm missing
        
        Example event_data:
            {
                "event": "progress_bar",
                "progressId": "progress_Processing_Files",
                "current": 60,
                "total": 100,
                "label": "Processing Files"
            }
        """
        if not self._is_bifrost_mode():
            return
        
        try:
            zcli = self.display.zcli
            if not zcli or not hasattr(zcli, 'comm'):
                return
            
            # Send via zComm's WebSocket broadcast
            if hasattr(zcli.comm, 'broadcast_websocket'):
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.run_coroutine_threadsafe(
                        zcli.comm.broadcast_websocket(json.dumps(event_data)),
                        loop
                    )
                except RuntimeError:
                    # No running event loop - skip broadcast
                    pass
        except Exception:
            # Silently fail in case of WebSocket issues
            pass
    
    def _format_time(self, seconds: float) -> str:
        """
        Format seconds into human-readable time string.
        
        Args:
            seconds: Duration in seconds (float)
        
        Returns:
            str: Formatted time string (e.g., "5s", "2m 30s", "1h 15m")
        
        Examples:
            - _format_time(45.2) → "45s"
            - _format_time(150) → "2m 30s"
            - _format_time(3720) → "1h 2m"
        
        Notes:
            - Used for ETA display in progress_bar()
            - Automatically chooses appropriate unit (s/m/h)
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"
    
    # ═══════════════════════════════════════════════════════════════════════
    #                           PUBLIC METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def progress_bar(
        self,
        current: int,
        total: Optional[int] = None,
        label: str = DEFAULT_LABEL_PROCESSING,
        width: int = DEFAULT_WIDTH,
        show_percentage: bool = DEFAULT_SHOW_PERCENTAGE,
        show_eta: bool = DEFAULT_SHOW_ETA,
        start_time: Optional[float] = None,
        color: Optional[str] = None
    ) -> str:
        """
        Display a progress bar (Terminal + zBifrost mode).
        
        Args:
            current: Current progress value (int)
            total: Total value (int) or None for indeterminate spinner
            label: Description text (str, default "Processing")
            width: Bar width in characters (int, default 50)
            show_percentage: Show percentage complete (bool, default True)
            show_eta: Show estimated time to completion (bool, default False)
            start_time: Start timestamp for ETA calculation (float, optional)
            color: Color name for the bar (str, optional)
        
        Returns:
            str: The rendered progress bar string
        
        Terminal Example:
            Processing files [████████████░░░░░░░] 60% (ETA: 2m 30s)
        
        Bifrost Example:
            Emits WebSocket event → React renders progress component
        
        Notes:
            - Terminal: Uses \r (carriage return) to overwrite same line
            - Bifrost: Emits 'progress_bar' or 'progress_complete' event
            - Indeterminate mode: If total=None, shows spinner instead of bar
            - ETA calculation: Requires start_time parameter
        """
        # Generate unique ID for this progress bar (use label as key)
        progress_id = f"progress_{label.replace(CHAR_SPACE, '_')}"
        
        # Calculate ETA string if requested
        eta_str = None
        if show_eta and start_time and current > 0 and total and total > 0:
            elapsed = time.time() - start_time
            rate = current / elapsed
            remaining = (total - current) / rate if rate > 0 else 0
            eta_str = self._format_time(remaining)
        
        # zBifrost mode - emit WebSocket event
        if self._is_bifrost_mode():
            event_data = {
                KEY_EVENT: EVENT_PROGRESS_BAR if current < total else EVENT_PROGRESS_COMPLETE,
                KEY_PROGRESS_ID: progress_id,
                KEY_CURRENT: current,
                KEY_TOTAL: total,
                KEY_LABEL: label,
                KEY_SHOW_PERCENTAGE: show_percentage,
                KEY_SHOW_ETA: show_eta,
                KEY_ETA: eta_str,
                KEY_COLOR: color,
                KEY_CONTAINER: DEFAULT_CONTAINER
            }
            self._emit_websocket_event(event_data)
            self._active_progress[progress_id] = event_data
            return f"{label}: {current}/{total}" if total else label
        
        # Terminal mode - render to console
        # Indeterminate mode (spinner)
        if total is None or total == 0:
            spinner_frame = self._spinner_styles[STYLE_DOTS][int(time.time() * 10) % 10]
            output = f"{label} {spinner_frame}"
            self.zPrimitives.write_raw(f"{ANSI_CARRIAGE_RETURN}{output}", flush=True)
            return output
        
        # Calculate percentage
        percentage = min(100, max(0, int((current / total) * 100)))
        filled = int((current / total) * width)
        bar = CHAR_FILLED * filled + CHAR_EMPTY * (width - filled)
        
        # Build output components
        output_parts = [label]
        
        # Add the bar
        if color:
            color_code = getattr(self.zColors, color, self.zColors.RESET)
            colored_bar = f"{color_code}{bar}{self.zColors.RESET}"
            output_parts.append(f"[{colored_bar}]")
        else:
            output_parts.append(f"[{bar}]")
        
        # Add percentage
        if show_percentage:
            output_parts.append(f"{percentage}%")
        
        # Add ETA
        if eta_str:
            output_parts.append(f"(ETA: {eta_str})")
        
        # Join and render
        output = CHAR_SPACE.join(output_parts)
        
        # Use carriage return for live updates
        self.zPrimitives.write_raw(f"{ANSI_CARRIAGE_RETURN}{output}", flush=True)
        
        # Add newline if complete
        if current >= total:
            self.zPrimitives.write_raw("\n")
        
        return output

    @contextmanager
    def spinner(
        self,
        label: str = DEFAULT_LABEL_LOADING,
        style: str = DEFAULT_SPINNER_STYLE
    ) -> Iterator[None]:
        """
        Context manager for animated loading spinner (Terminal + zBifrost mode).
        
        Args:
            label: Text to show (str, default "Loading")
            style: Spinner style (str, default "dots")
                   Options: 'dots', 'line', 'arc', 'arrow', 'bouncingBall', 'simple'
        
        Returns:
            Iterator[None]: Context manager (use with 'with' statement)
        
        Terminal Example:
            Loading data ⠋  (animates through 10 frames)
            Loading data ⠙
            Loading data ⠹
            Loading data ✓  (on completion)
        
        Bifrost Example:
            Emits 'spinner_start' → React shows spinner component
            Emits 'spinner_stop' → React removes spinner
        
        Usage:
            with display.spinner("Loading data", style="dots"):
                data = fetch_large_dataset()
                process_data(data)
            # Automatically prints "Loading data ✓" on exit
        
        Notes:
            - Terminal: Background thread animates frames at 10 FPS
            - Bifrost: WebSocket events, no animation thread needed
            - Context manager ensures cleanup (stop thread + show checkmark)
            - Thread-safe: threading.Event() for coordination
        """
        # Generate unique ID for this spinner
        spinner_id = f"spinner_{label.replace(CHAR_SPACE, '_')}_{str(uuid.uuid4())[:8]}"
        
        # zBifrost mode - emit WebSocket events
        if self._is_bifrost_mode():
            # Start spinner
            start_event = {
                KEY_EVENT: EVENT_SPINNER_START,
                KEY_SPINNER_ID: spinner_id,
                KEY_LABEL: label,
                KEY_STYLE: style,
                KEY_CONTAINER: DEFAULT_CONTAINER
            }
            self._emit_websocket_event(start_event)
            self._active_spinners[spinner_id] = start_event
            
            try:
                yield  # Execute the context block
            finally:
                # Stop spinner
                stop_event = {
                    KEY_EVENT: EVENT_SPINNER_STOP,
                    KEY_SPINNER_ID: spinner_id
                }
                self._emit_websocket_event(stop_event)
                if spinner_id in self._active_spinners:
                    del self._active_spinners[spinner_id]
            return
        
        # Terminal mode - animated spinner
        # Get spinner frames
        frames = self._spinner_styles.get(style, self._spinner_styles[STYLE_DOTS])
        
        # Spinner state
        stop_event_flag = threading.Event()
        frame_idx = [0]  # Use list for mutable reference in nested function
        
        def animate():
            """Animation loop running in separate thread."""
            while not stop_event_flag.is_set():
                frame = frames[frame_idx[0] % len(frames)]
                self.zPrimitives.write_raw(
                    f"{ANSI_CARRIAGE_RETURN}{label} {frame}",
                    flush=True
                )
                frame_idx[0] += 1
                time.sleep(DEFAULT_ANIMATION_DELAY)
        
        # Start animation thread
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
        
        try:
            yield  # Execute the context block
        finally:
            # Stop animation
            stop_event_flag.set()
            animation_thread.join(timeout=DEFAULT_THREAD_JOIN_TIMEOUT)
            
            # Clear the line and show completion
            self.zPrimitives.write_raw(
                f"{ANSI_CARRIAGE_RETURN}{label} {CHAR_CHECKMARK}\n",
                flush=True
            )

    def progress_iterator(
        self,
        iterable: Any,
        label: str = DEFAULT_LABEL_PROCESSING,
        show_percentage: bool = DEFAULT_SHOW_PERCENTAGE,
        show_eta: bool = True
    ) -> Iterator[Any]:
        """
        Wrap an iterable with a progress bar that auto-updates on each iteration.
        
        Args:
            iterable: Any iterable (list, range, generator, etc.)
            label: Description text (str, default "Processing")
            show_percentage: Show percentage complete (bool, default True)
            show_eta: Show estimated time to completion (bool, default True)
        
        Yields:
            Any: Items from the iterable, one at a time
        
        Terminal Example:
            Processing items [████████░░] 80% (ETA: 30s)
        
        Usage:
            items = ["file1.txt", "file2.txt", "file3.txt"]
            for item in display.progress_iterator(items, "Processing files"):
                process_file(item)
                # Progress bar updates automatically after each iteration
        
        Notes:
            - Converts iterable to list to get total count
            - Automatically tracks start_time for ETA calculation
            - Updates progress bar after yielding each item
        """
        items = list(iterable)
        total = len(items)
        start_time = time.time()
        
        for idx, item in enumerate(items, 1):
            self.progress_bar(
                current=idx,
                total=total,
                label=label,
                show_percentage=show_percentage,
                show_eta=show_eta,
                start_time=start_time
            )
            yield item

    def indeterminate_progress(
        self,
        label: str = DEFAULT_LABEL_PROCESSING
    ) -> Callable[[], None]:
        """
        Show an indeterminate progress indicator (when total count is unknown).
        
        Args:
            label: Description text (str, default "Processing")
        
        Returns:
            Callable[[], None]: update() function to call for each frame update
        
        Terminal Example:
            Processing ⠋  (call update() to advance frame)
            Processing ⠙
            Processing ⠹
        
        Usage:
            update = display.indeterminate_progress("Loading data")
            while processing:
                update()  # Call to update spinner frame
                do_some_work()
                time.sleep(0.1)
        
        Notes:
            - Returns a closure that maintains frame state
            - Caller controls update frequency (call update() in loop)
            - Use spinner() context manager for automatic animation
        """
        frame_idx = [0]
        frames = self._spinner_styles[STYLE_DOTS]
        
        def update() -> None:
            """Update the spinner frame (caller controls frequency)."""
            frame = frames[frame_idx[0] % len(frames)]
            self.zPrimitives.write_raw(
                f"{ANSI_CARRIAGE_RETURN}{label} {frame}",
                flush=True
            )
            frame_idx[0] += 1
        
        return update

    def swiper(
        self,
        slides: List[str],
        label: str = DEFAULT_LABEL_SLIDES,
        auto_advance: bool = DEFAULT_AUTO_ADVANCE,
        delay: int = DEFAULT_SWIPER_DELAY,
        loop: bool = DEFAULT_LOOP,
        container: str = DEFAULT_CONTAINER
    ) -> None:
        """
        Display a content carousel/swiper with navigation (Terminal + zBifrost mode).
        
        Args:
            slides: List of slide content strings (list of str)
            label: Title for the swiper (str, default "Slides")
            auto_advance: Auto-cycle through slides (bool, default True)
            delay: Seconds between auto-advance (int, default 3)
            loop: Wrap around to start after last slide (bool, default False)
            container: Bifrost DOM container (str, default "#app")
        
        Returns:
            None
        
        Terminal Mode (Hybrid B+C):
            - Auto-cycle: Slides advance every N seconds (if auto_advance=True)
            - Manual control: Arrow keys (◀ prev, ▶ next), Number keys (1-N jump)
            - Pause/Resume: 'p' key toggles auto-advance
            - Quit: 'q' key exits swiper
            
        Bifrost Mode:
            - Touch gestures: Swipe left/right for navigation
            - Auto-advance: Same as Terminal (configurable)
            - Slide indicators: Dots showing position (1/N, 2/N, etc.)
            - Loop mode: Optional wrap around to start
        
        Usage:
            slides = [
                "Welcome to zCLI!",
                "Feature 1: Progress Bars",
                "Feature 2: Spinners",
                "Feature 3: Swipers",
                "Thank you!"
            ]
            display.swiper(slides, "Getting Started", auto_advance=True, delay=3)
        
        Example output (Terminal):
            ╔═══════════════════════════════════════════════╗
            ║  Getting Started (Slide 2/5)                 ║
            ╠═══════════════════════════════════════════════╣
            ║                                               ║
            ║  Feature 1: Progress Bars                    ║
            ║                                               ║
            ╠═══════════════════════════════════════════════╣
            ║  ◀ Prev  ▶ Next  1-5 Jump  P Pause  Q Quit   ║
            ╚═══════════════════════════════════════════════╝
        """
        if not slides:
            return
        
        # Generate unique ID for this swiper
        swiper_id = f"swiper_{label.replace(CHAR_SPACE, '_')}_{str(uuid.uuid4())[:8]}"
        
        # zBifrost mode - emit WebSocket events
        if self._is_bifrost_mode():
            # Initialize swiper
            init_event = {
                KEY_EVENT: EVENT_SWIPER_INIT,
                KEY_SWIPER_ID: swiper_id,
                KEY_LABEL: label,
                KEY_SLIDES: slides,
                KEY_CURRENT_SLIDE: 0,
                KEY_TOTAL_SLIDES: len(slides),
                KEY_AUTO_ADVANCE: auto_advance,
                KEY_DELAY: delay,
                KEY_LOOP: loop,
                KEY_CONTAINER: container
            }
            self._emit_websocket_event(init_event)
            self._active_swipers[swiper_id] = init_event
            
            # Bifrost mode is async - frontend handles navigation
            # For now, just display a simple confirmation in terminal fallback
            self.zPrimitives.write_line(f"\n{label}: Swiper initialized with {len(slides)} slides (Bifrost mode)")
            self.zPrimitives.write_line(MSG_BIFROST_INITIALIZED)
            return
        
        # Terminal mode - interactive swiper with auto-cycle + manual control
        current_slide = [0]  # Mutable reference for nested function
        is_paused = [False]  # Pause state
        stop_event = threading.Event()
        
        def display_slide(idx: int) -> None:
            """Render a single slide in terminal with box-drawing UI."""
            # Clear screen (ANSI escape codes)
            self.zPrimitives.write_raw(f"{ANSI_CLEAR_SCREEN}{ANSI_HOME}", flush=True)
            
            # Calculate box width
            width = DEFAULT_SWIPER_WIDTH
            inner_width = width - 4
            
            # Build slide display
            slide_content = slides[idx]
            slide_num = f"Slide {idx + 1}/{len(slides)}"
            
            # Header
            header_text = f"  {label} ({slide_num})"
            header_padding = CHAR_SPACE * (width - len(header_text) - 2)
            self.zPrimitives.write_line(
                f"{BOX_TOP_LEFT}{BOX_HORIZONTAL * (width - 2)}{BOX_TOP_RIGHT}"
            )
            self.zPrimitives.write_line(
                f"{BOX_VERTICAL}{header_text}{header_padding}{BOX_VERTICAL}"
            )
            self.zPrimitives.write_line(
                f"{BOX_LEFT_T}{BOX_HORIZONTAL * (width - 2)}{BOX_RIGHT_T}"
            )
            
            # Content (centered)
            self.zPrimitives.write_line(
                f"{BOX_VERTICAL}{CHAR_SPACE * (width - 2)}{BOX_VERTICAL}"
            )
            content_padding = (inner_width - len(slide_content)) // 2
            content_line = (
                f"{BOX_VERTICAL}  {CHAR_SPACE * content_padding}{slide_content}"
                f"{CHAR_SPACE * (inner_width - len(slide_content) - content_padding)}  "
                f"{BOX_VERTICAL}"
            )
            self.zPrimitives.write_line(content_line)
            self.zPrimitives.write_line(
                f"{BOX_VERTICAL}{CHAR_SPACE * (width - 2)}{BOX_VERTICAL}"
            )
            
            # Controls
            if is_paused[0]:
                status = SWIPER_STATUS_PAUSED
            elif auto_advance:
                status = SWIPER_STATUS_AUTO.format(delay)
            else:
                status = SWIPER_STATUS_MANUAL
            
            self.zPrimitives.write_line(
                f"{BOX_LEFT_T}{BOX_HORIZONTAL * (width - 2)}{BOX_RIGHT_T}"
            )
            controls = f"  ◀ Prev  ▶ Next  1-{len(slides)} Jump  P Pause  Q Quit  {status}"
            controls_padding = CHAR_SPACE * max(0, width - len(controls) - 2)
            self.zPrimitives.write_line(
                f"{BOX_VERTICAL}{controls}{controls_padding}{BOX_VERTICAL}"
            )
            self.zPrimitives.write_line(
                f"{BOX_BOTTOM_LEFT}{BOX_HORIZONTAL * (width - 2)}{BOX_BOTTOM_RIGHT}"
            )
        
        def auto_advance_loop():
            """Auto-advance slides in background thread."""
            while not stop_event.is_set():
                if auto_advance and not is_paused[0]:
                    time.sleep(delay)
                    if not stop_event.is_set():
                        # Move to next slide
                        if loop or current_slide[0] < len(slides) - 1:
                            current_slide[0] = (current_slide[0] + 1) % len(slides)
                            display_slide(current_slide[0])
                        else:
                            # Reached end without loop - stop
                            stop_event.set()
                else:
                    time.sleep(0.1)
        
        # Start auto-advance thread if enabled
        if auto_advance:
            advance_thread = threading.Thread(target=auto_advance_loop, daemon=True)
            advance_thread.start()
        
        # Display first slide
        display_slide(current_slide[0])
        
        # Handle keyboard input (non-blocking)
        try:
            import termios
            import tty
            import select
            
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            
            while not stop_event.is_set():
                # Check for keyboard input (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    # Handle arrow keys (escape sequences)
                    if key == ESC_KEY:  # ESC
                        next_keys = sys.stdin.read(2)
                        if next_keys == ARROW_RIGHT:  # Right arrow
                            if loop or current_slide[0] < len(slides) - 1:
                                current_slide[0] = (current_slide[0] + 1) % len(slides)
                                display_slide(current_slide[0])
                        elif next_keys == ARROW_LEFT:  # Left arrow
                            if loop or current_slide[0] > 0:
                                current_slide[0] = (current_slide[0] - 1) % len(slides)
                                display_slide(current_slide[0])
                    # Handle number keys (1-9)
                    elif key.isdigit():
                        target_idx = int(key) - 1
                        if 0 <= target_idx < len(slides):
                            current_slide[0] = target_idx
                            display_slide(current_slide[0])
                    # Handle pause toggle
                    elif key.lower() == SWIPER_CMD_PAUSE:
                        is_paused[0] = not is_paused[0]
                        display_slide(current_slide[0])
                    # Handle quit
                    elif key.lower() == SWIPER_CMD_QUIT:
                        stop_event.set()
                        break
        
        except (ImportError, AttributeError, termios.error):
            # Fallback for systems without termios (Windows)
            # Just display slides sequentially with basic input
            self.zPrimitives.write_line(MSG_SWIPER_FALLBACK)
            for idx in range(len(slides)):
                if stop_event.is_set():
                    break
                display_slide(idx)
                user_input = input()
                if user_input.lower() == SWIPER_CMD_QUIT:
                    break
        
        finally:
            # Restore terminal settings
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except (OSError, AttributeError):
                pass
            
            # Stop auto-advance thread
            stop_event.set()
            if auto_advance:
                advance_thread.join(timeout=DEFAULT_THREAD_JOIN_TIMEOUT)
            
            # Clear screen and show completion
            self.zPrimitives.write_raw(f"{ANSI_CLEAR_SCREEN}{ANSI_HOME}", flush=True)
            self.zPrimitives.write_line(MSG_SWIPER_COMPLETED.format(label))
            
            # Emit completion event for Bifrost
            if swiper_id in self._active_swipers:
                complete_event = {
                    KEY_EVENT: EVENT_SWIPER_COMPLETE,
                    KEY_SWIPER_ID: swiper_id
                }
                self._emit_websocket_event(complete_event)
                del self._active_swipers[swiper_id]


