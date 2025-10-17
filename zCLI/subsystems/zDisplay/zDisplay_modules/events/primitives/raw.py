# zCLI/subsystems/zDisplay/zDisplay_modules/events/primitives/raw.py

"""Primitive event handlers for raw, line and block output."""

def handle_raw(obj, output_adapter, logger):
    """Raw output - atomic primitive with no formatting or newlines."""
    content = obj.get("content", "")
    logger.debug("handle_raw: %d chars", len(content))
    output_adapter.write_raw(content)


def handle_line(obj, output_adapter, logger):
    """Single line output with newline (uses raw)."""
    content = obj.get("content", "")
    logger.debug("handle_line: %s", content[:50] if len(content) > 50 else content)
    output_adapter.write_line(content)


def handle_block(obj, output_adapter, logger):
    """Multi-line block output (uses raw)."""
    content = obj.get("content")
    lines = obj.get("lines")

    if lines:
        content = '\n'.join(lines)
    elif content is None:
        content = ""

    logger.debug("handle_block: %d lines", content.count('\n') + 1 if content else 0)
    output_adapter.write_block(content)
