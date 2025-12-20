# zCLI/subsystems/zOpen/zOpen.py

"""
zOpen Subsystem - Main Facade

This module provides the main facade for the zOpen subsystem, handling file and URL
opening operations in a mode-agnostic manner. It serves as the primary entry point,
routing requests to specialized modules and executing optional hooks.

Architecture Position:
    - Tier 2 (Facade) of zOpen's 3-tier architecture
    - Delegates to Tier 1 foundation modules (open_paths, open_urls, open_files)
    - Exposed to zCLI via Tier 3 (package root)

3-Tier Architecture:
    Tier 1: Foundation Modules (open_modules/)
        - open_paths.py: zPath resolution (@ and ~ symbols)
        - open_urls.py: URL opening in browsers
        - open_files.py: File opening by extension (HTML, text)
        - __init__.py: Package aggregator

    Tier 2: Facade (THIS FILE)
        - zOpen class: Main entry point
        - handle() method: Request parsing, routing, and hook execution
        - Delegates all opening logic to Tier 1 modules

    Tier 3: Package Root (__init__.py)
        - Exports zOpen class to zCLI

Key Features:
    - Dual Format Support: Accepts both string ("zOpen(path)") and dict formats
    - Type Detection: Automatically detects URLs, zPaths, and local file paths
    - Modular Routing: Delegates to specialized handlers (paths, URLs, files)
    - Hook Execution: Supports onSuccess/onFail callbacks via zFunc
    - Mode-Agnostic: Works in both Terminal and Bifrost modes
    - Session Integration: Uses zConfig session for preferences

Input Formats:
    String Format (Legacy):
        "zOpen(/path/to/file.txt)"
        "zOpen(https://example.com)"
        "zOpen(@.README.md)"

    Dict Format (Modern):
        {
            "zOpen": {
                "path": "/path/to/file.txt",
                "onSuccess": "callback_function()",  # Optional
                "onFail": "error_handler()"          # Optional
            }
        }

Type Detection & Routing:
    URLs (http:// or https:// or www.):
        → open_url() from open_modules.open_urls
        → Opens in user's preferred or system default browser

    zPaths (@ or ~):
        → resolve_zpath() from open_modules.open_paths
        → Resolves to filesystem path
        → open_file() from open_modules.open_files

    Local Files (everything else):
        → os.path.abspath(os.path.expanduser(path))
        → open_file() from open_modules.open_files
        → Routes by extension (.html → browser, .txt → IDE)

Hook Execution (onSuccess/onFail):
    - Executed after opening attempt completes
    - onSuccess: Triggered if result == "zBack" (success)
    - onFail: Triggered if result == "stop" (failure)
    - Both callbacks executed via zFunc.handle()
    - Hook results replace original result

Integration Points:
    - zCLI.py: Initializes zOpen (line ~210)
    - zDispatch: Routes "zOpen(...)" commands via dispatch_launcher
    - zConfig: Session access for workspace, IDE, browser preferences
    - zDisplay: Output, breadcrumbs, status messages
    - zFunc: Hook callback execution
    - zDialog: Interactive prompts (file creation, IDE selection) via open_files

Dependencies:
    - os: Path operations (abspath, expanduser)
    - urlparse: URL parsing for type detection
    - open_modules: Foundation modules (paths, URLs, files)

Usage Example (from zDispatch):
    # String format
    result = zcli.open.handle("zOpen(/path/to/file.py)")

    # Dict format with hooks
    result = zcli.open.handle({
        "zOpen": {
            "path": "https://github.com",
            "onSuccess": "log_success()",
            "onFail": "log_error()"
        }
    })

    # zPath format
    result = zcli.open.handle("zOpen(@.README.md)")

Return Values:
    - "zBack": Opening successful, return to previous screen
    - "stop": Opening failed or user cancelled
    - Hook result: If hook executes, returns hook's result

Version History:
    - v1.5.4: Refactored from monolithic (369 lines) to modular facade (~150 lines)
    - v1.5.4: Extracted logic to open_modules (paths, URLs, files)
    - v1.5.4: Added industry-grade documentation and type hints
    - v1.5.4: Modernized session key access (SESSION_KEY_* constants)

TODO: Week 6.6 (zDispatch) Integration:
    - dispatch_launcher.py (Line 403): Verify open.handle() signature after refactor ✓
    - dispatch_launcher.py (Line 427): Update open.handle() call after refactor ✓
    - Current signature: handle(zHorizontal: str | dict) → str
    - Status: COMPATIBLE - No changes needed

Author: zCLI Development Team
"""

from zCLI import os, urlparse, Any

# Import from foundation modules (Tier 1)
from .open_modules import resolve_zpath, open_url, open_file

# ═══════════════════════════════════════════════════════════════
# Module-Level Constants
# ═══════════════════════════════════════════════════════════════

# Command Prefix
CMD_PREFIX = "zOpen("

# Dict Keys
DICT_KEY_ZOPEN = "zOpen"
DICT_KEY_PATH = "path"
DICT_KEY_ON_SUCCESS = "onSuccess"
DICT_KEY_ON_FAIL = "onFail"

# URL Schemes (for detection)
URL_SCHEME_HTTP = "http"
URL_SCHEME_HTTPS = "https"
URL_PREFIX_WWW = "www."
URL_SCHEME_HTTPS_DEFAULT = "https://"

# zPath Symbols (for detection)
ZPATH_SYMBOL_WORKSPACE = "@"
ZPATH_SYMBOL_ABSOLUTE = "~"

# Return Codes (zCLI standard)
RETURN_ZBACK = "zBack"
RETURN_STOP = "stop"

# Display Colors
COLOR_ZOPEN = "ZOPEN"
COLOR_INFO = "INFO"

# Display Styles
STYLE_FULL = "full"
STYLE_SINGLE = "single"

# Display Messages
MSG_ZOPEN_READY = "zOpen Ready"
MSG_HANDLE_ZOPEN = "Handle zOpen"
MSG_HOOK_SUCCESS = "[HOOK] onSuccess"
MSG_HOOK_FAIL = "[HOOK] onFail"

# Display Indents
INDENT_INIT = 0
INDENT_HANDLE = 1
INDENT_HOOK = 2

# Log Messages
LOG_INCOMING_REQUEST = "Incoming zOpen request: %s"
LOG_PARSED_PATH = "Parsed path: %s"
LOG_EXEC_SUCCESS_HOOK = "Executing onSuccess hook: %s"
LOG_EXEC_FAIL_HOOK = "Executing onFail hook: %s"


# ═══════════════════════════════════════════════════════════════
# Main Facade Class
# ═══════════════════════════════════════════════════════════════

class zOpen:
    """
    Main facade class for file and URL opening operations.

    This class provides the primary interface for the zOpen subsystem, handling
    initialization, request parsing, type detection, routing to specialized modules,
    and optional hook execution.

    Attributes:
        zcli: Reference to main zCLI instance
        session: zCLI session dictionary (from zcli.session)
        logger: Logger instance (from zcli.logger)
        display: zDisplay instance (from zcli.display)
        zfunc: zFunc instance (from zcli.zfunc) for hook execution
        dialog: zDialog instance (from zcli.dialog) for interactive prompts
        mycolor: Display color identifier ("ZOPEN")

    Public Methods:
        handle(zHorizontal: str | dict) → str:
            Main entry point for opening operations

    Facade Pattern:
        This class delegates all complex logic to specialized modules:
        - zPath resolution → open_modules.open_paths
        - URL opening → open_modules.open_urls
        - File opening → open_modules.open_files

        The facade only handles:
        - Request parsing (string vs dict format)
        - Type detection (URL vs zPath vs file)
        - Routing to appropriate module
        - Hook execution (onSuccess/onFail)

    Integration with zCLI:
        Initialized in zCLI.__init__() (line ~210):
            self.open = zOpen(self)

        Called from zDispatch (dispatch_launcher.py):
            return self.zcli.open.handle(zHorizontal)

    Version: v1.5.4
    """

    def __init__(self, zcli: Any) -> None:
        """
        Initialize zOpen with zCLI instance.

        Args:
            zcli: Main zCLI instance

        Raises:
            ValueError: If zcli is None or missing required attributes

        Initialization Flow:
            1. Validate zcli instance
            2. Store references to required subsystems
            3. Display initialization message via zDisplay

        Required zCLI Attributes:
            - session: Session dictionary
            - logger: Logging instance
            - display: zDisplay instance
            - zfunc: zFunc instance (for hooks)
            - dialog: zDialog instance (for prompts)

        Example:
            >>> zcli = zCLI()
            >>> zopen = zOpen(zcli)
            # Displays: "zOpen Ready"

        Version: v1.5.4
        """
        if zcli is None:
            raise ValueError("zOpen requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Store references to zCLI subsystems
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.zfunc = zcli.zfunc
        self.dialog = zcli.dialog
        self.mycolor = COLOR_ZOPEN

        # Display initialization message
        self.display.zDeclare(
            MSG_ZOPEN_READY,
            color=self.mycolor,
            indent=INDENT_INIT,
            style=STYLE_FULL
        )

    def handle(self, zHorizontal: str | dict[str, Any]) -> str:
        """
        Handle zOpen operations with optional hooks.

        This is the main entry point for all opening operations. It parses the input,
        detects the type (URL/zPath/file), routes to the appropriate handler module,
        and executes optional hooks based on the result.

        Args:
            zHorizontal: Opening request in string or dict format

        Returns:
            "zBack" if successful, "stop" if failed, or hook result if hook executes

        Input Formats:
            String: "zOpen(path_or_url)"
                - Example: "zOpen(/path/to/file.txt)"
                - Example: "zOpen(https://example.com)"
                - No hooks supported in string format

            Dict: {"zOpen": {"path": "...", "onSuccess": "...", "onFail": "..."}}
                - path: Required, path or URL to open
                - onSuccess: Optional, zFunc callback on success
                - onFail: Optional, zFunc callback on failure

        Processing Flow:
            1. Display "Handle zOpen" message and breadcrumbs
            2. Parse input format (string vs dict)
            3. Extract path/URL and optional hooks
            4. Detect type and route:
                - http/https/www → open_url() (open_modules.open_urls)
                - @ or ~ → resolve_zpath() + open_file() (open_modules)
                - Other → open_file() (open_modules.open_files)
            5. Execute hooks if present:
                - onSuccess if result == "zBack"
                - onFail if result == "stop"
            6. Return result or hook result

        Type Detection:
            URLs: parsed.scheme in ("http", "https") or path.startswith("www.")
                → open_url(url, session, display, logger)

            zPaths: path.startswith("@") or path.startswith("~")
                → resolve_zpath(path, session, logger)
                → open_file(resolved_path, session, display, dialog, logger)

            Local Files: Everything else
                → os.path.abspath(os.path.expanduser(path))
                → open_file(path, session, display, dialog, logger)

        Hook Execution:
            onSuccess Hook:
                - Triggered when result == "zBack"
                - Displays: "[HOOK] onSuccess"
                - Executes: self.zfunc.handle(on_success)
                - Returns: Hook result (replaces original result)

            onFail Hook:
                - Triggered when result == "stop"
                - Displays: "[HOOK] onFail"
                - Executes: self.zfunc.handle(on_fail)
                - Returns: Hook result (replaces original result)

        Example Usage:
            # String format (no hooks)
            >>> result = zopen.handle("zOpen(/path/to/file.txt)")
            "zBack"

            # Dict format (with hooks)
            >>> result = zopen.handle({
                "zOpen": {
                    "path": "https://github.com",
                    "onSuccess": "log_success()",
                    "onFail": "log_error()"
                }
            })
            "zBack"  # Or hook result if hook executes

            # zPath format
            >>> result = zopen.handle("zOpen(@.README.md)")
            "zBack"

        Integration Notes:
            - Called by zDispatch.dispatch_launcher (line ~428)
            - Uses zDisplay for output (mode-agnostic)
            - Uses zFunc for hook callbacks
            - Delegates to open_modules for all opening logic
            - Session modernization: Uses constants from zConfig

        See Also:
            - open_modules.open_url(): URL opening
            - open_modules.resolve_zpath(): zPath resolution
            - open_modules.open_file(): File opening by extension

        Version: v1.5.4
        """
        # Display handle message and breadcrumbs
        self.display.zDeclare(
            MSG_HANDLE_ZOPEN,
            color=self.mycolor,
            indent=INDENT_HANDLE,
            style=STYLE_FULL
        )
        self.display.zCrumbs(self.session)

        self.logger.debug(LOG_INCOMING_REQUEST, zHorizontal)

        # Parse input - support both string and dict formats
        if isinstance(zHorizontal, dict):
            # Dict format: {"zOpen": {"path": "...", "onSuccess": "...", "onFail": "..."}}
            zopen_obj = zHorizontal.get(DICT_KEY_ZOPEN, {})
            raw_path = zopen_obj.get(DICT_KEY_PATH, "")
            on_success = zopen_obj.get(DICT_KEY_ON_SUCCESS)
            on_fail = zopen_obj.get(DICT_KEY_ON_FAIL)
        else:
            # String format: "zOpen(path)"
            raw_path = zHorizontal[len(CMD_PREFIX):-1].strip().strip('"').strip("'")
            on_success = None
            on_fail = None

        self.logger.debug(LOG_PARSED_PATH, raw_path)

        # Determine type and route to appropriate handler
        parsed = urlparse(raw_path)

        if parsed.scheme in (URL_SCHEME_HTTP, URL_SCHEME_HTTPS) or raw_path.startswith(URL_PREFIX_WWW):
            # URL handling → open_modules.open_urls
            url = raw_path if parsed.scheme else f"{URL_SCHEME_HTTPS_DEFAULT}{raw_path}"
            result = open_url(url, self.session, self.display, self.logger)

        elif raw_path.startswith(ZPATH_SYMBOL_WORKSPACE) or raw_path.startswith(ZPATH_SYMBOL_ABSOLUTE):
            # zPath handling → open_modules.open_paths + open_modules.open_files
            resolved_path = resolve_zpath(raw_path, self.session, self.logger)
            if not resolved_path:
                # Resolution failed
                result = RETURN_STOP
            else:
                # Open resolved file
                result = open_file(resolved_path, self.session, self.display, self.dialog, self.logger)

        else:
            # Local file handling → open_modules.open_files
            path = os.path.abspath(os.path.expanduser(raw_path))
            result = open_file(path, self.session, self.display, self.dialog, self.logger)

        # Execute hooks based on result
        if result == RETURN_ZBACK and on_success:
            self.logger.info(LOG_EXEC_SUCCESS_HOOK, on_success)
            self.display.zDeclare(
                MSG_HOOK_SUCCESS,
                color=self.mycolor,
                indent=INDENT_HOOK,
                style=STYLE_SINGLE
            )
            return self.zfunc.handle(on_success)

        if result == RETURN_STOP and on_fail:
            self.logger.info(LOG_EXEC_FAIL_HOOK, on_fail)
            self.display.zDeclare(
                MSG_HOOK_FAIL,
                color=self.mycolor,
                indent=INDENT_HOOK,
                style=STYLE_SINGLE
            )
            return self.zfunc.handle(on_fail)

        return result

    def open_image(self, image_path: str) -> str:
        """
        Open an image file in the system's default image viewer or browser (for URLs).
        
        Terminal-First Design:
        - Detects if image_path is a URL (http/https/www)
        - URLs → Opens in browser (correct UX for web images)
        - Local paths → Opens in image viewer app
        
        Uses zMachine's detected image viewer and platform-specific launch commands.
        Falls back gracefully if viewer is not available or headless environment.
        
        Args:
            image_path: Path to the image file (local path or URL)
            
        Returns:
            "zBack" if successfully opened, "stop" if failed
            
        Detection Flow:
            1. Check if image_path is a URL → open in browser
            2. Otherwise, get image_viewer from session[zMachine]
            3. Get platform-specific launch command
            4. Resolve image path (absolute)
            5. Check if file exists
            6. Launch viewer with subprocess
            7. Handle errors gracefully
            
        Examples:
            >>> zcli.open.open_image("screenshot.png")
            # macOS: open -a Preview screenshot.png
            # Linux: eog screenshot.png
            # Windows: start screenshot.png
            
            >>> zcli.open.open_image("https://picsum.photos/200/300")
            # Opens in browser (correct for web images)
            
        Version: v1.5.9 (URL Detection)
        """
        # Detect if it's a URL → open in browser
        parsed = urlparse(image_path)
        if parsed.scheme in (URL_SCHEME_HTTP, URL_SCHEME_HTTPS) or image_path.startswith(URL_PREFIX_WWW):
            self.logger.info(f"Detected web image URL: {image_path}")
            url = image_path if parsed.scheme else f"{URL_SCHEME_HTTPS_DEFAULT}{image_path}"
            return open_url(url, self.session, self.display, self.logger)
        
        # Local file handling (original logic)
        from zCLI import subprocess
        from zCLI.subsystems.zConfig.zConfig_modules.helpers import get_image_viewer_launch_command
        from zCLI.subsystems.zConfig.zConfig_modules.config_session import SESSION_KEY_ZMACHINE
        
        # Get image viewer from session
        zmachine = self.session.get(SESSION_KEY_ZMACHINE, {})
        viewer_name = zmachine.get("image_viewer", "unknown")
        
        # Handle special cases
        if viewer_name in ("none", "unknown"):
            self.logger.warning(f"No image viewer available (viewer: {viewer_name})")
            self.display.warning(
                "No image viewer detected. Cannot open images in this environment.",
                indent=1
            )
            return RETURN_STOP
        
        # Get platform-specific launch command
        cmd, args = get_image_viewer_launch_command(viewer_name)
        
        if cmd is None:
            self.logger.error(f"Failed to get launch command for viewer: {viewer_name}")
            self.display.error(
                f"Image viewer '{viewer_name}' is not supported on this platform.",
                indent=1
            )
            return RETURN_STOP
        
        # Resolve absolute path
        absolute_path = os.path.abspath(os.path.expanduser(image_path))
        
        # Check if file exists
        if not os.path.exists(absolute_path):
            self.logger.error(f"Image file not found: {absolute_path}")
            self.display.error(
                f"Image file not found: {image_path}",
                indent=1
            )
            return RETURN_STOP
        
        # Launch image viewer
        try:
            full_command = [cmd] + args + [absolute_path]
            self.logger.info(f"Launching image viewer: {' '.join(full_command)}")
            
            subprocess.Popen(
                full_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"Successfully opened image in {viewer_name}")
            self.display.success(
                f"Opened image in {viewer_name}",
                indent=1
            )
            return RETURN_ZBACK
            
        except Exception as e:
            self.logger.error(f"Failed to open image with {viewer_name}: {e}")
            self.display.error(
                f"Failed to open image: {e}",
                indent=1
            )
            return RETURN_STOP

    def open_video(self, video_path: str) -> str:
        """
        Open a video file in the system's default video player.
        
        Uses zMachine's detected video player and platform-specific launch commands.
        Falls back gracefully if player is not available or headless environment.
        
        Args:
            video_path: Path to the video file (relative or absolute)
            
        Returns:
            "zBack" if successfully opened, "stop" if failed
            
        Detection Flow:
            1. Get video_player from session[zMachine]
            2. Get platform-specific launch command
            3. Resolve video path (absolute)
            4. Check if file exists
            5. Launch player with subprocess
            6. Handle errors gracefully
            
        Examples:
            >>> zcli.open.open_video("movie.mp4")
            # macOS: open -a "QuickTime Player" movie.mp4
            # Linux: vlc movie.mp4
            # Windows: start movie.mp4
            
        Version: v1.5.8 (Video Support)
        """
        from zCLI import subprocess
        from zCLI.subsystems.zConfig.zConfig_modules.helpers import get_video_player_launch_command
        from zCLI.subsystems.zConfig.zConfig_modules.config_session import SESSION_KEY_ZMACHINE
        
        # Get video player from session
        zmachine = self.session.get(SESSION_KEY_ZMACHINE, {})
        player_name = zmachine.get("video_player", "unknown")
        
        # Handle special cases
        if player_name in ("none", "unknown"):
            self.logger.warning(f"No video player available (player: {player_name})")
            self.display.warning(
                "No video player detected. Cannot play videos in this environment.",
                indent=1
            )
            return RETURN_STOP
        
        # Get platform-specific launch command
        cmd, args = get_video_player_launch_command(player_name)
        
        if cmd is None:
            self.logger.error(f"Failed to get launch command for player: {player_name}")
            self.display.error(
                f"Video player '{player_name}' is not supported on this platform.",
                indent=1
            )
            return RETURN_STOP
        
        # Resolve absolute path
        absolute_path = os.path.abspath(os.path.expanduser(video_path))
        
        # Check if file exists
        if not os.path.exists(absolute_path):
            self.logger.error(f"Video file not found: {absolute_path}")
            self.display.error(
                f"Video file not found: {video_path}",
                indent=1
            )
            return RETURN_STOP
        
        # Launch video player
        try:
            full_command = [cmd] + args + [absolute_path]
            self.logger.info(f"Launching video player: {' '.join(full_command)}")
            
            subprocess.Popen(
                full_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"Successfully opened video in {player_name}")
            self.display.success(
                f"Opened video in {player_name}",
                indent=1
            )
            return RETURN_ZBACK
            
        except Exception as e:
            self.logger.error(f"Failed to open video with {player_name}: {e}")
            self.display.error(
                f"Failed to open video: {e}",
                indent=1
            )
            return RETURN_STOP

    def open_audio(self, audio_path: str) -> str:
        """
        Open an audio file in the system's default audio player.
        
        Uses zMachine's detected audio player and platform-specific launch commands.
        Falls back gracefully if player is not available or headless environment.
        
        Args:
            audio_path: Path to the audio file (relative or absolute)
            
        Returns:
            "zBack" if successfully opened, "stop" if failed
            
        Detection Flow:
            1. Get audio_player from session[zMachine]
            2. Get platform-specific launch command
            3. Resolve audio path (absolute)
            4. Check if file exists
            5. Launch player with subprocess
            6. Handle errors gracefully
            
        Examples:
            >>> zcli.open.open_audio("song.mp3")
            # macOS: open -a Music song.mp3
            # Linux: vlc song.mp3
            # Windows: start song.mp3
            
        Version: v1.5.8 (Audio Support)
        """
        from zCLI import subprocess
        from zCLI.subsystems.zConfig.zConfig_modules.helpers import get_audio_player_launch_command
        from zCLI.subsystems.zConfig.zConfig_modules.config_session import SESSION_KEY_ZMACHINE
        
        # Get audio player from session
        zmachine = self.session.get(SESSION_KEY_ZMACHINE, {})
        player_name = zmachine.get("audio_player", "unknown")
        
        # Handle special cases
        if player_name in ("none", "unknown"):
            self.logger.warning(f"No audio player available (player: {player_name})")
            self.display.warning(
                "No audio player detected. Cannot play audio in this environment.",
                indent=1
            )
            return RETURN_STOP
        
        # Get platform-specific launch command
        cmd, args = get_audio_player_launch_command(player_name)
        
        if cmd is None:
            self.logger.error(f"Failed to get launch command for player: {player_name}")
            self.display.error(
                f"Audio player '{player_name}' is not supported on this platform.",
                indent=1
            )
            return RETURN_STOP
        
        # Resolve absolute path
        absolute_path = os.path.abspath(os.path.expanduser(audio_path))
        
        # Check if file exists
        if not os.path.exists(absolute_path):
            self.logger.error(f"Audio file not found: {absolute_path}")
            self.display.error(
                f"Audio file not found: {audio_path}",
                indent=1
            )
            return RETURN_STOP
        
        # Launch audio player
        try:
            full_command = [cmd] + args + [absolute_path]
            self.logger.info(f"Launching audio player: {' '.join(full_command)}")
            
            subprocess.Popen(
                full_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"Successfully opened audio in {player_name}")
            self.display.success(
                f"Opened audio in {player_name}",
                indent=1
            )
            return RETURN_ZBACK
            
        except Exception as e:
            self.logger.error(f"Failed to open audio with {player_name}: {e}")
            self.display.error(
                f"Failed to open audio: {e}",
                indent=1
            )
            return RETURN_STOP


# ═══════════════════════════════════════════════════════════════
# Module Exports
# ═══════════════════════════════════════════════════════════════

__all__ = ["zOpen"]
