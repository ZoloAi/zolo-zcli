# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/Widgets.py
"""Interactive widgets: progress bars, spinners, and loaders."""

import sys
import time
import threading
import asyncio
import json
import uuid
from contextlib import contextmanager


class Widgets:
    """Interactive widgets for long-running operations.
    
    Provides:
    - progress_bar: Visual progress indicator with percentage and ETA
    - spinner: Animated loading spinner (context manager)
    
    Supports both Terminal mode and zBifrost (WebSocket) mode.
    """

    def __init__(self, display_instance):
        """Initialize Widgets with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get references to other packages for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization
        
        # Spinner styles
        self._spinner_styles = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "line": ["-", "\\", "|", "/"],
            "arc": ["◜", "◠", "◝", "◞", "◡", "◟"],
            "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
            "bouncingBall": ["⠁", "⠂", "⠄", "⠂"],
            "simple": [".", "..", "...", ""],
        }
        
        # Track active progress bars/spinners by ID (for zBifrost mode)
        self._active_progress = {}
        self._active_spinners = {}

    def _is_bifrost_mode(self):
        """Check if running in zBifrost (WebSocket) mode."""
        if not self.display or not hasattr(self.display, 'mode'):
            return False
        return self.display.mode == "zBifrost"
    
    def _emit_websocket_event(self, event_data):
        """Emit a WebSocket event for zBifrost mode."""
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

    def progress_bar(self, current, total=None, label="Processing", 
                     width=50, show_percentage=True, show_eta=False,
                     start_time=None, color=None):
        """
        Display a progress bar (Terminal + zBifrost mode).
        
        Args:
            current: Current progress value (int)
            total: Total value (int) or None for indeterminate spinner
            label: Description text (str)
            width: Bar width in characters (int, default 50)
            show_percentage: Show percentage complete (bool, default True)
            show_eta: Show estimated time to completion (bool, default False)
            start_time: Start timestamp for ETA calculation (float, optional)
            color: Color name for the bar (str, optional)
        
        Returns:
            str: The rendered progress bar
        
        Example:
            Processing files [████████████░░░░░░░] 60% (ETA: 2m 30s)
        """
        # Generate unique ID for this progress bar (use label as key)
        progress_id = f"progress_{label.replace(' ', '_')}"
        
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
                "event": "progress_bar" if current < total else "progress_complete",
                "progressId": progress_id,
                "current": current,
                "total": total,
                "label": label,
                "showPercentage": show_percentage,
                "showETA": show_eta,
                "eta": eta_str,
                "color": color,
                "container": "#app"  # Default container
            }
            self._emit_websocket_event(event_data)
            self._active_progress[progress_id] = event_data
            return f"{label}: {current}/{total}" if total else label
        
        # Terminal mode - render to console
        # Indeterminate mode (spinner)
        if total is None or total == 0:
            spinner_frame = self._spinner_styles["dots"][int(time.time() * 10) % 10]
            output = f"{label} {spinner_frame}"
            self.zPrimitives.write_raw(f"\r{output}", flush=True)
            return output
        
        # Calculate percentage
        percentage = min(100, max(0, int((current / total) * 100)))
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        
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
        output = " ".join(output_parts)
        
        # Use carriage return for live updates
        self.zPrimitives.write_raw(f"\r{output}", flush=True)
        
        # Add newline if complete
        if current >= total:
            self.zPrimitives.write_raw("\n")
        
        return output

    def _format_time(self, seconds):
        """Format seconds into human-readable time string."""
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

    @contextmanager
    def spinner(self, label="Loading", style="dots"):
        """
        Context manager for animated loading spinner (Terminal + zBifrost mode).
        
        Args:
            label: Text to show (str)
            style: Spinner style - 'dots', 'line', 'arc', 'arrow', 'bouncingBall', 'simple'
        
        Usage:
            with display.spinner("Loading data"):
                # long operation
                data = fetch_data()
        
        Example output:
            Loading data ⠋
            Loading data ⠙
            Loading data ⠹
        """
        # Generate unique ID for this spinner
        spinner_id = f"spinner_{label.replace(' ', '_')}_{str(uuid.uuid4())[:8]}"
        
        # zBifrost mode - emit WebSocket events
        if self._is_bifrost_mode():
            # Start spinner
            start_event = {
                "event": "spinner_start",
                "spinnerId": spinner_id,
                "label": label,
                "style": style,
                "container": "#app"  # Default container
            }
            self._emit_websocket_event(start_event)
            self._active_spinners[spinner_id] = start_event
            
            try:
                yield  # Execute the context block
            finally:
                # Stop spinner
                stop_event = {
                    "event": "spinner_stop",
                    "spinnerId": spinner_id
                }
                self._emit_websocket_event(stop_event)
                if spinner_id in self._active_spinners:
                    del self._active_spinners[spinner_id]
            return
        
        # Terminal mode - animated spinner
        # Get spinner frames
        frames = self._spinner_styles.get(style, self._spinner_styles["dots"])
        
        # Spinner state
        stop_event = threading.Event()
        frame_idx = [0]  # Use list for mutable reference in nested function
        
        def animate():
            """Animation loop running in separate thread."""
            while not stop_event.is_set():
                frame = frames[frame_idx[0] % len(frames)]
                self.zPrimitives.write_raw(f"\r{label} {frame}", flush=True)
                frame_idx[0] += 1
                time.sleep(0.1)
        
        # Start animation thread
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
        
        try:
            yield  # Execute the context block
        finally:
            # Stop animation
            stop_event.set()
            animation_thread.join(timeout=0.5)
            
            # Clear the line and show completion
            self.zPrimitives.write_raw(f"\r{label} ✓\n", flush=True)

    def progress_iterator(self, iterable, label="Processing", show_percentage=True, show_eta=True):
        """
        Wrap an iterable with a progress bar.
        
        Args:
            iterable: Any iterable (list, range, etc.)
            label: Description text
            show_percentage: Show percentage complete
            show_eta: Show estimated time
        
        Yields:
            Items from the iterable
        
        Usage:
            for item in display.progress_iterator(items, "Processing items"):
                process(item)
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

    def indeterminate_progress(self, label="Processing"):
        """
        Show an indeterminate progress indicator (when total is unknown).
        
        Args:
            label: Description text
        
        Returns:
            Callable to update the spinner
        
        Usage:
            update = display.indeterminate_progress("Loading")
            while processing:
                update()  # Call to update spinner frame
                do_work()
        """
        frame_idx = [0]
        frames = self._spinner_styles["dots"]
        
        def update():
            """Update the spinner frame."""
            frame = frames[frame_idx[0] % len(frames)]
            self.zPrimitives.write_raw(f"\r{label} {frame}", flush=True)
            frame_idx[0] += 1
        
        return update

