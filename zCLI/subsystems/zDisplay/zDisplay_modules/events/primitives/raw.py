# zCLI/subsystems/zDisplay_modules/events/primitives/raw.py
"""
Primitive event handlers - atomic output operations.

These are the most basic operations that cannot be decomposed further:
- raw: Direct output with no formatting
- line: Single line output (adds newline)
- block: Multi-line block output
"""

from logger import Logger

logger = Logger.get_logger(__name__)


def handle_raw(obj, output_adapter):
    """Raw output - atomic primitive with no formatting or newlines."""
    content = obj.get("content", "")
    output_adapter.write_raw(content)


def handle_line(obj, output_adapter):
    """Single line output with newline (uses raw)."""
    content = obj.get("content", "")
    output_adapter.write_line(content)


def handle_block(obj, output_adapter):
    """Multi-line block output (uses raw)."""
    content = obj.get("content")
    lines = obj.get("lines")
    
    if lines:
        content = '\n'.join(lines)
    elif content is None:
        content = ""
    
    output_adapter.write_block(content)

