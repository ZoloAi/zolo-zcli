# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_media.py

"""
MediaEvents - Media Display Event Package for zDisplay
=====================================================

This event package provides structured media display (images) with
comprehensive formatting options, building on the BasicOutputs foundation.

Composition Architecture
------------------------
MediaEvents builds on BasicOutputs:

Layer 3: display_delegates.py (PRIMARY API)
    ↓
Layer 2: display_events.py (ORCHESTRATOR)
    ↓
Layer 2: events/display_event_media.py (MediaEvents) ← THIS MODULE
    ↓
Layer 2: events/display_event_outputs.py (BasicOutputs) ← FOUNDATION
    ↓
Layer 1: display_primitives.py (FOUNDATION I/O)

Composition Flow:
1. MediaEvents.image() method called
2. If GUI mode (Bifrost):
   a. Send clean JSON event with essential image data (src, alt_text, caption)
   b. Returns immediately (GUI handles async)
3. If terminal mode:
   a. Format image metadata (path, alt text, caption)
   b. Apply styling (indentation, color)
   c. Display via BasicOutputs.text() for consistent I/O
   d. Display button with action="#" (placeholder for future zOpen integration)
4. Return control to caller

Dual-Mode I/O Pattern
----------------------
All methods implement the same dual-mode pattern:

1. **GUI Mode (Bifrost):** Try send_gui_event() first
   - Send clean JSON event with data (src, alt_text, caption)
   - Returns immediately (GUI handles async)
   - GUI frontend will display data

2. **Terminal Mode (Fallback):** Format and display locally
   - Format image metadata (path, alt, caption)
   - Apply styling (indentation, colors)
   - Display via BasicOutputs.text() for consistent I/O
   - Show button with action="#" as placeholder

Terminal-First Philosophy
--------------------------
In terminal mode, images display as:
- 📷 Icon + alt text header
- Path display
- Caption (if provided)
- Button with action="#" (if open_prompt=True)

This ensures terminal users get full metadata even if they can't view the image inline.
"""

from zCLI import Any, Dict, Optional

# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

EVENT_IMAGE = "image"
DEFAULT_IMAGE_ICON = "📷"

class MediaEvents:
    """Event package for displaying media (e.g., images)."""

    display: Any  # Parent zDisplay instance
    zPrimitives: Any  # Primitives instance for I/O operations
    zColors: Any  # Colors instance for terminal styling
    BasicOutputs: Any # BasicOutputs instance for consistent text output
    BasicInputs: Any # BasicInputs instance for button logic

    def __init__(self, display_instance: Any) -> None:
        """Initialize MediaEvents with parent display reference.

        Args:
            display_instance: Parent zDisplay instance providing primitives and colors.
        """
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        self.logger = display_instance.logger # Access logger from display instance

    def image(
        self,
        src: str,
        alt_text: str = "",
        caption: str = "",
        open_prompt: bool = True,
        indent: int = 0,
        color: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Display an image event.

        In Bifrost mode, sends a clean event with src, alt_text, and caption.
        In Terminal mode, displays formatted text with path, alt_text, caption,
        and a button with action="#" (placeholder for future zOpen integration).

        Args:
            src: The source URL or path of the image.
            alt_text: Alternative text for the image (accessibility).
            caption: An optional caption for the image.
            open_prompt: If True (default), displays a button in terminal mode (with action="#").
                        Set to False to disable the prompt.
            indent: Indentation level for terminal output.
            color: Color for terminal output text.
            **kwargs: Additional parameters to pass through to the event.

        Returns:
            Optional[Dict[str, Any]]: The event dictionary if sent to GUI,
                                     or None for terminal mode.
        """
        if not src:
            self.logger.error("[MediaEvents] image() requires 'src' parameter")
            return None

        # Base event for both modes
        base_event = {
            "type": EVENT_IMAGE,
            "src": src,
            "alt_text": alt_text,
            "caption": caption,
            **kwargs
        }

        if self.display.mode == "zBifrost":
            # Bifrost gets clean image data
            return self.zPrimitives.send_gui_event(base_event)
        else:
            # Terminal mode: format and display locally
            indent_str = "  " * indent
            display_color = color if color else self.display.mycolor

            # Display icon + alt text header
            header = f"{indent_str}{DEFAULT_IMAGE_ICON} {alt_text}" if alt_text else f"{indent_str}{DEFAULT_IMAGE_ICON} Image"
            self.BasicOutputs.text(header, indent=0, color=display_color, break_after=False)

            # Display path
            path_line = f"{indent_str}   Path: {src}"
            self.BasicOutputs.text(path_line, indent=0, color="muted", break_after=False)

            # Display caption (if provided)
            if caption:
                caption_line = f"{indent_str}   Caption: {caption}"
                self.BasicOutputs.text(caption_line, indent=0, color="muted", break_after=False)

            # Display button (if open_prompt enabled)
            if open_prompt:
                # Add spacing before button
                self.zPrimitives.write_line("")
                # Use built-in button logic with action="#" (development null)
                confirmed = self.BasicInputs.button("Open image file", action="#", color="info")
                if confirmed:
                    # TODO: Phase 2 - Call zOpen.open_image(src) here
                    self.logger.info(f"[MediaEvents] User confirmed open for: {src}")
            else:
                # Add break after last line if no button
                self.zPrimitives.write_line("")

            return None

