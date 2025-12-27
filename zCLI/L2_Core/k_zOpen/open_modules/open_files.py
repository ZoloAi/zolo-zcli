# zCLI/subsystems/zOpen/open_modules/open_files.py

"""
File Opening Module

This module provides local file opening functionality for the zOpen subsystem, handling
various file types based on extension and routing to appropriate handlers (browser, IDE,
or display).

Architecture Position:
    - Tier 1c (Foundation Module) of zOpen's 3-tier architecture
    - Provides file opening services for the facade layer
    - Most complex foundation module (handles multiple file types)

Key Features:
    - Extension-Based Routing: Dispatches to appropriate handler based on file extension
    - HTML Files: Opens in browser (file:// URL)
    - Text Files: Opens in user's preferred IDE
    - IDE Preference: Uses zMachine.ide from session
    - zDialog Integration: Prompts for file creation or IDE selection
    - Fallback Strategy: Displays file content if IDE opening fails
    - Cross-Platform: Works on Windows, macOS, Linux

File Type Support:
    Current:
        - HTML/HTM: Opens in browser
        - Text formats: .txt, .md, .py, .js, .json, .yaml, .yml → IDE
    Future (documented for expansion):
        - Documents: PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
        - Images: PNG, JPG, GIF, SVG (system viewer + Bifrost display)
        - Archives: ZIP, TAR, GZ (list contents, extract options)
        - Media: Audio (MP3, WAV), Video (MP4, AVI)

Integration Points:
    - zConfig: Session access for IDE/workspace preferences
    - zDisplay: File info display, content rendering, status messages
    - zDialog: Interactive prompts (file creation, IDE selection)
    - zOpen facade: Primary entry point via handle()

Dependencies:
    - os: File operations and path manipulation
    - subprocess: Launch IDE applications
    - webbrowser: Open HTML files in browser
    - zConfig constants: SESSION_KEY_ZMACHINE for session dict keys

Usage Example:
    from zCLI.L2_Core.k_zOpen.open_modules.open_files import open_file

    session = {"zMachine": {"ide": "cursor"}}
    display = zcli.display
    dialog = zcli.dialog
    logger = zcli.logger

    result = open_file("/path/to/file.py", session, display, dialog, logger)
    # Returns: "zBack" on success, "stop" on failure

Version History:
    - v1.5.4: Extracted from monolithic zOpen.py, added industry-grade documentation
    - v1.5.4: Added type hints, constants, and session modernization
    - v1.5.4: Enhanced extension routing and defensive zDialog integration
    - v1.5.4: Documented future extension points for additional file types

Author: zCLI Development Team
"""

from zCLI import os, webbrowser, subprocess, Any

# Import centralized session constants
from zCLI.L1_Foundation.a_zConfig.zConfig_modules.config_session import (
    SESSION_KEY_ZMACHINE,
    SESSION_KEY_IDE,
)

# Import platform-specific IDE launch command helper from zConfig
from zCLI.L1_Foundation.a_zConfig.zConfig_modules.helpers import get_ide_launch_command

# ═══════════════════════════════════════════════════════════════
# Module-Level Constants
# ═══════════════════════════════════════════════════════════════

# File Extensions (Supported Types)
EXTENSIONS_HTML = ('.html', '.htm')
EXTENSIONS_TEXT = ('.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml')

# Future Extensions (Documented for Expansion)
# EXTENSIONS_DOCUMENTS = ('.pdf', '.docx', '.xlsx', '.pptx')
# EXTENSIONS_IMAGES = ('.png', '.jpg', '.jpeg', '.gif', '.svg')
# EXTENSIONS_ARCHIVES = ('.zip', '.tar', '.gz', '.rar')
# EXTENSIONS_MEDIA_AUDIO = ('.mp3', '.wav', '.flac')
# EXTENSIONS_MEDIA_VIDEO = ('.mp4', '.avi', '.mkv')

# Return Codes (zCLI standard)
RETURN_ZBACK = "zBack"    # Success, return to previous screen
RETURN_STOP = "stop"       # Failure, stop execution

# Session Keys (zMachine sub-keys)
ZMACHINE_KEY_IDE = "ide"

# Default IDE (fallback if not configured)
DEFAULT_IDE = "nano"
IDE_UNKNOWN = "unknown"

# Available IDEs (for zDialog selection prompt)
AVAILABLE_IDES = ["cursor", "code", "nano", "vim"]

# File Creation Options (zDialog prompt)
FILE_ACTION_CREATE = "Create file"
FILE_ACTION_CANCEL = "Cancel"
FILE_ACTIONS = [FILE_ACTION_CREATE, FILE_ACTION_CANCEL]

# Content Display Limits
CONTENT_TRUNCATE_LIMIT = 1000  # Characters to show before truncation

# Display Colors
COLOR_SUCCESS = "GREEN"
COLOR_ERROR = "RED"
COLOR_INFO = "INFO"

# Display Styles
STYLE_SINGLE = "single"
STYLE_SECTION = "~"

# Display Indents
INDENT_FILE_INFO = 1

# Display Messages
MSG_CREATED_FILE = "Created {path}"
MSG_OPENED_BROWSER = "Opened {filename} in browser"
MSG_OPENED_IDE = "Opened {filename} in {ide}"
MSG_BROWSER_FAILED = "Browser failed to open HTML file"
MSG_BROWSER_ERROR = "Browser error: {error}"
MSG_FAILED_IDE = "Failed to open with {ide}: {error}"
MSG_FILE_CONTENT_TITLE = "File Content: {filename}"
MSG_CONTENT_TRUNCATED = "\n[Content truncated - showing first {limit} of {total} characters]"
MSG_UNSUPPORTED_TYPE = "Unsupported file type: {ext}"

# Error Messages
ERR_FILE_NOT_FOUND = "File not found: %s"
ERR_DIALOG_FAILED = "Dialog fallback failed: %s"
ERR_BROWSER_FAILED = "Browser failed to open HTML file"
ERR_BROWSER_ERROR = "Browser error: %s"
ERR_IDE_FAILED = "Failed to open with IDE %s: %s"
ERR_READ_FAILED = "Failed to read file: %s"
ERR_UNSUPPORTED_TYPE = "Unsupported file type: %s"

# Log Messages
LOG_RESOLVED_PATH = "Resolved path: %s"
LOG_FILE_NOT_FOUND = "File not found: %s"
LOG_PROMPTING_USER = "Prompting user for action on missing file"
LOG_CREATED_FILE = "Created file: %s"
LOG_OPENING_HTML = "Opening HTML file: %s"
LOG_SUCCESS_HTML = "Successfully opened HTML file in browser"
LOG_OPENING_TEXT = "Opening text file: %s"
LOG_USING_IDE = "Using IDE: %s"
LOG_SUCCESS_IDE = "Successfully opened file with %s"
LOG_IDE_SELECTION_FAILED = "IDE selection dialog failed: %s"
LOG_DISPLAYING_CONTENT = "Displaying text file content"

# File Encoding
FILE_ENCODING = 'utf-8'

# zDialog Field Names
DIALOG_FIELD_ACTION = "action"
DIALOG_FIELD_IDE = "ide"

# OS Platform Identifier
OS_WINDOWS = 'nt'


# ═══════════════════════════════════════════════════════════════
# Public API Functions
# ═══════════════════════════════════════════════════════════════

def open_file(
    path: str,
    session: dict[str, Any],
    display: Any,
    dialog: Any,
    logger: Any
) -> str:
    """
    Handle local file opening based on file extension.

    This function is the main entry point for file opening operations. It displays
    file information, handles missing files (with zDialog prompt), and routes to
    appropriate handlers based on file extension.

    Args:
        path: Absolute filesystem path to the file
        session: zCLI session dictionary containing machine configuration
        display: zDisplay instance for output and status messages
        dialog: zDialog instance for interactive prompts (optional, can be None)
        logger: Logger instance for debug/error output

    Returns:
        "zBack" if file opened successfully, "stop" if failed or user cancelled

    Opening Flow:
        1. Display file info (path, size, type) via zDisplay.json_data()
        2. Check if file exists
            - If missing: Prompt user to create file (via zDialog)
            - If user cancels: Return "stop"
        3. Extract file extension
        4. Route to appropriate handler:
            - .html/.htm → _open_html() → browser
            - .txt/.md/.py/etc → _open_text() → IDE
            - Other → Return "stop" (unsupported)

    File Info Display:
        Displays JSON structure via zDisplay.json_data():
        {
            "path": "/path/to/file.py",
            "exists": true,
            "size": "1024 bytes",
            "type": ".py"
        }

    Missing File Handling (zDialog Integration):
        - If file doesn't exist and dialog available:
            - Prompts: "Create file" or "Cancel"
            - If "Create file": Creates empty file, continues opening
            - If "Cancel": Returns "stop"
        - If file doesn't exist and no dialog:
            - Returns "stop" immediately

    Extension Routing:
        HTML/HTM:
            → _open_html(path, display, logger)
            → Opens file:// URL in browser

        Text formats (.txt, .md, .py, .js, .json, .yaml, .yml):
            → _open_text(path, session, display, dialog, logger)
            → Opens in user's preferred IDE
            → Falls back to content display if IDE fails

        Unsupported:
            → Logs warning, displays error message
            → Returns "stop"

    Return Values:
        - "zBack": File opened successfully (browser or IDE launched)
        - "stop": File opening failed or user cancelled

    Error Handling:
        - Missing file: zDialog prompt or immediate stop
        - Unsupported extension: Warning logged, error displayed
        - Handler failures: Propagated from _open_html() or _open_text()
        - All exceptions caught in handlers

    Integration Notes:
        - Called by zOpen facade after path resolution
        - Uses zDisplay for all output (mode-agnostic)
        - Uses centralized SESSION_KEY_ZMACHINE constant
        - Defensive zDialog checks (dialog can be None)
        - Delegates to specialized handlers for each file type

    Example Usage:
        >>> session = {SESSION_KEY_ZMACHINE: {ZMACHINE_KEY_IDE: "cursor"}}
        >>> result = open_file("/path/to/script.py", session, display, dialog, logger)
        "zBack"  # Opened in Cursor IDE

        >>> result = open_file("/path/to/page.html", session, display, None, logger)
        "zBack"  # Opened in browser

        >>> result = open_file("/missing.txt", session, display, dialog, logger)
        # User prompted to create file, then opens in IDE if created

    Future Extensions:
        To add support for new file types, extend the routing logic in this function:
        1. Add extension constant (e.g., EXTENSIONS_DOCUMENTS)
        2. Create handler function (e.g., _open_document())
        3. Add routing condition: if ext in EXTENSIONS_DOCUMENTS: return _open_document(...)
        4. Update module docstring with new supported types

    See Also:
        - _open_html(): HTML file handler (browser)
        - _open_text(): Text file handler (IDE)
        - _display_file_content(): Fallback content display

    Version: v1.5.4
    """
    logger.debug(LOG_RESOLVED_PATH, path)

    # Enhanced display: Show file info as JSON (if file exists)
    if os.path.exists(path):
        file_info = {
            "path": path,
            "exists": True,
            "size": f"{os.path.getsize(path)} bytes",
            "type": os.path.splitext(path)[1]
        }
        display.json_data(file_info, color=True, indent=INDENT_FILE_INFO)

    # Check if file exists
    if not os.path.exists(path):
        logger.error(ERR_FILE_NOT_FOUND, path)

        # zDialog fallback: Offer to create file or cancel (defensive check)
        if dialog:
            logger.info(LOG_PROMPTING_USER)

            try:
                result = dialog.handle({
                    "zDialog": {
                        "model": None,
                        "fields": [{
                            "name": DIALOG_FIELD_ACTION,
                            "type": "enum",
                            "options": FILE_ACTIONS
                        }]
                    }
                })

                if result.get(DIALOG_FIELD_ACTION) == FILE_ACTION_CREATE:
                    # Create empty file
                    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                    with open(path, 'w', encoding=FILE_ENCODING) as f:
                        f.write("")
                    logger.info(LOG_CREATED_FILE, path)
                    display.zDeclare(
                        MSG_CREATED_FILE.format(path=path),
                        color=COLOR_SUCCESS,
                        indent=INDENT_FILE_INFO,
                        style=STYLE_SINGLE
                    )
                    # Continue with opening the newly created file
                else:
                    return RETURN_STOP

            except Exception as e:
                logger.warning(ERR_DIALOG_FAILED, e)
                return RETURN_STOP
        else:
            # No dialog available, can't create file
            return RETURN_STOP

    # Route to appropriate handler based on file extension
    _, ext = os.path.splitext(path.lower())

    if ext in EXTENSIONS_HTML:
        return _open_html(path, display, logger)

    if ext in EXTENSIONS_TEXT:
        return _open_text(path, session, display, dialog, logger)

    # Unsupported file type
    logger.warning(ERR_UNSUPPORTED_TYPE, ext)
    display.zDeclare(
        MSG_UNSUPPORTED_TYPE.format(ext=ext),
        color=COLOR_ERROR,
        indent=INDENT_FILE_INFO,
        style=STYLE_SINGLE
    )
    return RETURN_STOP


# ═══════════════════════════════════════════════════════════════
# Private Helper Functions
# ═══════════════════════════════════════════════════════════════

def _open_html(
    path: str,
    display: Any,
    logger: Any
) -> str:
    """
    Open HTML files in browser.

    Converts filesystem path to file:// URL and opens in system default browser.

    Args:
        path: Absolute path to HTML file
        display: zDisplay instance for status messages
        logger: Logger instance for debug/error output

    Returns:
        "zBack" if opened successfully, "stop" if failed

    Browser Integration:
        - Converts path to file:// URL format
        - Uses webbrowser.open() for system default browser
        - Cross-platform compatible

    Display Integration:
        - Success: "Opened {filename} in browser" (GREEN)
        - Failure: "Browser failed to open HTML file" (RED)
        - Error: "Browser error: {error}" (RED)

    Example:
        >>> _open_html("/path/to/page.html", display, logger)
        "zBack"  # Opened file://path/to/page.html in browser

    Version: v1.5.4
    """
    url = f"file://{path}"
    logger.info(LOG_OPENING_HTML, url)

    try:
        success = webbrowser.open(url)
        if success:
            logger.info(LOG_SUCCESS_HTML)
            display.zDeclare(
                MSG_OPENED_BROWSER.format(filename=os.path.basename(path)),
                color=COLOR_SUCCESS,
                indent=INDENT_FILE_INFO,
                style=STYLE_SINGLE
            )
            return RETURN_ZBACK

        logger.warning(ERR_BROWSER_FAILED)
        display.zDeclare(
            MSG_BROWSER_FAILED,
            color=COLOR_ERROR,
            indent=INDENT_FILE_INFO,
            style=STYLE_SINGLE
        )
        return RETURN_STOP

    except Exception as e:
        logger.warning(ERR_BROWSER_ERROR, e)
        display.zDeclare(
            MSG_BROWSER_ERROR.format(error=str(e)),
            color=COLOR_ERROR,
            indent=INDENT_FILE_INFO,
            style=STYLE_SINGLE
        )
        return RETURN_STOP


def _open_text(
    path: str,
    session: dict[str, Any],
    display: Any,
    dialog: Any,
    logger: Any
) -> str:
    """
    Open text files using user's preferred IDE.

    Retrieves IDE preference from session, optionally prompts user if unknown,
    launches IDE with file, and falls back to content display if IDE fails.

    Args:
        path: Absolute path to text file
        session: zCLI session dictionary containing IDE preference
        display: zDisplay instance for output and status messages
        dialog: zDialog instance for IDE selection prompt (can be None)
        logger: Logger instance for debug/error output

    Returns:
        "zBack" if opened successfully (IDE or content display), rarely "stop"

    IDE Selection Logic:
        1. Get IDE from session[SESSION_KEY_ZMACHINE][ZMACHINE_KEY_IDE]
        2. If IDE is "unknown" and dialog available:
            - Prompt user to select from AVAILABLE_IDES
        3. Default to "nano" if not configured

    IDE Launch:
        Windows (os.name == 'nt'):
            - Try: os.startfile(path)
            - Fallback: subprocess.run([ide, path])

        Unix/Linux/macOS:
            - subprocess.run([ide, path], check=False)

    Fallback Strategy:
        - If IDE launch fails: Call _display_file_content()
        - Content display is the final fallback (always returns "zBack")

    Display Integration:
        - Success: "Opened {filename} in {ide}" (GREEN)
        - Failure: "Failed to open with {ide}: {error}" (RED)
        - Then: Calls _display_file_content() as fallback

    Example:
        >>> session = {SESSION_KEY_ZMACHINE: {ZMACHINE_KEY_IDE: "cursor"}}
        >>> _open_text("/path/to/script.py", session, display, None, logger)
        "zBack"  # Opened in Cursor

    Version: v1.5.4
    """
    logger.info(LOG_OPENING_TEXT, path)

    # Get IDE preference (priority: session["ide"] → session["zMachine"]["ide"] → default)
    editor = session.get(SESSION_KEY_IDE) or session.get(SESSION_KEY_ZMACHINE, {}).get(ZMACHINE_KEY_IDE, DEFAULT_IDE)

    logger.info(LOG_USING_IDE, editor)

    # zDialog: Optionally ask for IDE if unknown (defensive check)
    if dialog and editor == IDE_UNKNOWN:
        try:
            result = dialog.handle({
                "zDialog": {
                    "model": None,
                    "fields": [{
                        "name": DIALOG_FIELD_IDE,
                        "type": "enum",
                        "options": AVAILABLE_IDES
                    }]
                }
            })
            editor = result.get(DIALOG_FIELD_IDE, DEFAULT_IDE)
        except Exception as e:
            logger.warning(LOG_IDE_SELECTION_FAILED, e)

    # Try to open with IDE using platform-specific launch command
    try:
        # Get platform-specific IDE launch command from zConfig
        cmd, args = get_ide_launch_command(editor)
        
        if cmd:
            # Build full command: cmd + args + [path]
            full_cmd = [cmd] + args + [path]
            subprocess.run(full_cmd, check=False, timeout=10)
            logger.info(LOG_SUCCESS_IDE, editor)
        elif os.name == OS_WINDOWS:
            # Windows fallback: try os.startfile for unknown IDEs
            try:
                os.startfile(path)  # type: ignore
                logger.info(LOG_SUCCESS_IDE, "startfile")
            except AttributeError:
                subprocess.run([editor, path], check=False, timeout=10)
                logger.info(LOG_SUCCESS_IDE, editor)
        else:
            # Unix/macOS fallback: try direct command for unknown IDEs
            subprocess.run([editor, path], check=False, timeout=10)
            logger.info(LOG_SUCCESS_IDE, editor)
        display.zDeclare(
            MSG_OPENED_IDE.format(filename=os.path.basename(path), ide=editor),
            color=COLOR_SUCCESS,
            indent=INDENT_FILE_INFO,
            style=STYLE_SINGLE
        )
        return RETURN_ZBACK

    except Exception as e:
        logger.warning(ERR_IDE_FAILED, editor, e)
        display.zDeclare(
            MSG_FAILED_IDE.format(ide=editor, error=str(e)),
            color=COLOR_ERROR,
            indent=INDENT_FILE_INFO,
            style=STYLE_SINGLE
        )

        # Fallback: Display file content
        return _display_file_content(path, display, logger)


def _display_file_content(
    path: str,
    display: Any,
    logger: Any
) -> str:
    """
    Display text file content when IDE opening fails.

    Final fallback for text files. Reads file contents and displays via zDisplay,
    with automatic truncation for large files.

    Args:
        path: Absolute path to text file
        display: zDisplay instance for content output
        logger: Logger instance for error output

    Returns:
        Always returns "zBack" (content displayed or error shown)

    Content Display:
        - Uses display.zDeclare() for section title
        - Uses display.write_block() for content
        - Truncates after CONTENT_TRUNCATE_LIMIT characters (1000)
        - Shows truncation notice if content exceeds limit

    Truncation Logic:
        If len(content) > 1000:
            - Display first 1000 characters + "..."
            - Display: "[Content truncated - showing first 1000 of {total} characters]"
        Else:
            - Display full content

    Error Handling:
        - If file read fails: Log error, return "stop"
        - All exceptions caught and logged

    Example:
        >>> _display_file_content("/path/to/small.txt", display, logger)
        # Displays full content
        "zBack"

        >>> _display_file_content("/path/to/large.log", display, logger)
        # Displays first 1000 chars + truncation notice
        "zBack"

    Version: v1.5.4
    """
    logger.info(LOG_DISPLAYING_CONTENT)

    try:
        with open(path, 'r', encoding=FILE_ENCODING) as f:
            content = f.read()

        display.zDeclare(
            MSG_FILE_CONTENT_TITLE.format(filename=os.path.basename(path)),
            color=COLOR_INFO,
            indent=INDENT_FILE_INFO,
            style=STYLE_SECTION
        )

        # Display content using display.write_block() with truncation
        if len(content) > CONTENT_TRUNCATE_LIMIT:
            display.write_block(content[:CONTENT_TRUNCATE_LIMIT] + "...")
            display.write_line(
                MSG_CONTENT_TRUNCATED.format(
                    limit=CONTENT_TRUNCATE_LIMIT,
                    total=len(content)
                )
            )
        else:
            display.write_block(content)

        return RETURN_ZBACK

    except Exception as e:
        logger.error(ERR_READ_FAILED, e)
        return RETURN_STOP


# ═══════════════════════════════════════════════════════════════
# Module Exports
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "open_file",  # Main file opening function
]

