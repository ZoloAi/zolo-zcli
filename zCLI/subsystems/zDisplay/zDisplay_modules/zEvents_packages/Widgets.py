# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/Widgets.py
"""Interactive widgets: progress bars, spinners, and loaders."""

import sys
import time
import threading
from contextlib import contextmanager


class Widgets:
    """Interactive widgets for long-running operations.
    
    Provides:
    - progress_bar: Visual progress indicator with percentage and ETA
    - spinner: Animated loading spinner (context manager)
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

    def progress_bar(self, current, total=None, label="Processing", 
                     width=50, show_percentage=True, show_eta=False,
                     start_time=None, color=None):
        """
        Display a progress bar for Terminal mode.
        
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
        if show_eta and start_time and current > 0:
            elapsed = time.time() - start_time
            rate = current / elapsed
            remaining = (total - current) / rate if rate > 0 else 0
            eta_str = self._format_time(remaining)
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
        Context manager for animated loading spinner.
        
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

