# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_links.py

"""
LinkEvents - Semantic Link Rendering for zDisplay
==================================================

Handles semantic link rendering with support for:
- Internal navigation (delta $ and zPath @)
- External URLs (http/https)
- Anchor links (#section)
- Target behavior (_blank, _self, etc.)
- Window features (width, height, etc.)

Terminal Mode:
- Internal links: Auto-navigate or prompt based on link type
- External links: Show URL, prompt to open in browser
- Anchor links: Display with icon (no scroll in Terminal)
- Target: Limited support (new terminal window if possible)

Bifrost Mode:
- Internal links: Client-side routing via BifrostClient
- External links: Native <a> tag behavior with proper security
- Anchor links: Smooth scroll to target element
- Target: Full HTML5 support including window.open()

Architecture Position:
    Layer 2: Event Handlers (this module)
    Uses: display_primitives for output, zOpen for external links
    Called by: display_events.py orchestrator

Version: v1.6.0 (Link Event Support)
"""

from typing import Dict, Any, Optional

# Event type constant
EVENT_LINK = "link"

# Target constants
TARGET_SELF = "_self"
TARGET_BLANK = "_blank"
TARGET_PARENT = "_parent"
TARGET_TOP = "_top"
DEFAULT_TARGET = TARGET_SELF

# Link type detection constants
LINK_TYPE_INTERNAL_DELTA = "delta"  # $zAbout
LINK_TYPE_INTERNAL_ZPATH = "zpath"  # @.UI.zUI.zAbout
LINK_TYPE_EXTERNAL = "external"  # https://...
LINK_TYPE_ANCHOR = "anchor"  # #section
LINK_TYPE_PLACEHOLDER = "placeholder"  # # (empty anchor)

# Button-style prompt constant (reused from button primitive for consistency)
PROMPT_LINK_TEMPLATE = "Click [{label}]? (y/n): "

# Log prefix
LOG_PREFIX = "[LinkEvents]"


class LinkEvents:
    """
    Handle link event rendering for Terminal and Bifrost modes.
    
    Provides semantic link rendering with mode-aware behavior, supporting
    internal navigation, external URLs, and anchor links with full target
    and window feature control.
    
    Attributes:
        display: Parent zDisplay instance
        zcli: Root zCLI instance
        logger: Logger instance
    
    Methods:
        handle_link(): Main entry point for link rendering
    """
    
    def __init__(self, display: Any) -> None:
        """
        Initialize LinkEvents handler.
        
        Args:
            display: Parent zDisplay instance
        """
        self.display = display
        self.zcli = display.zcli
        self.logger = display.logger
        self.primitives = display.zPrimitives
        self.zColors = display.zColors  # For Terminal color support
        # Cross-references (set by zEvents)
        self.BasicOutputs = None  # Will be wired by zEvents.__init__
        self.BasicInputs = None   # Will be wired by zEvents.__init__
    
    def handle_link(self, link_data: Dict[str, Any]) -> Optional[Any]:
        """
        Main entry point for link event handling.
        
        Renders links based on mode (Terminal vs Bifrost) and link type
        (internal, external, anchor). Handles target behavior and window
        features for advanced use cases.
        
        Args:
            link_data: Dict with keys:
                - label: Link text (required)
                - href: Link destination (required)
                - target: Target behavior (_self, _blank, etc.)
                - rel: Link relationship (security)
                - window: Window features for window.open()
                - _zClass: CSS classes for styling
                - color: Color theme
        
        Returns:
            Navigation result (for internal links) or None
        
        Examples:
            # Internal link
            handle_link({"label": "About", "href": "$zAbout"})
            
            # External link with new tab
            handle_link({
                "label": "GitHub",
                "href": "https://github.com",
                "target": "_blank"
            })
            
            # Anchor link
            handle_link({"label": "Features", "href": "#features"})
        """
        href = link_data.get('href', '#')
        label = link_data.get('label', href)
        target = link_data.get('target', DEFAULT_TARGET)
        
        # Detect link type
        link_type = self._detect_link_type(href)
        
        # Route to mode-specific handler
        mode = self.zcli.session.get('zMode', 'Terminal')
        
        if mode == 'Terminal':
            return self._render_terminal(link_data, link_type)
        else:  # zBifrost
            return self._render_bifrost(link_data, link_type)
    
    def _detect_link_type(self, href: str) -> str:
        """
        Detect link type from href value.
        
        Args:
            href: Link destination
        
        Returns:
            Link type constant (delta, zpath, external, anchor, placeholder)
        
        Examples:
            _detect_link_type("$zAbout") → "delta"
            _detect_link_type("@.UI.zUI.zAbout") → "zpath"
            _detect_link_type("https://example.com") → "external"
            _detect_link_type("#features") → "anchor"
            _detect_link_type("#") → "placeholder"
        """
        if not href or href == '#':
            return LINK_TYPE_PLACEHOLDER
        elif href.startswith('$'):
            return LINK_TYPE_INTERNAL_DELTA
        elif href.startswith('@'):
            return LINK_TYPE_INTERNAL_ZPATH
        elif href.startswith(('http://', 'https://')):
            return LINK_TYPE_EXTERNAL
        elif href.startswith('#'):
            return LINK_TYPE_ANCHOR
        else:
            # Assume internal delta if unclear
            return LINK_TYPE_INTERNAL_DELTA
    
    def _render_terminal(self, link_data: Dict[str, Any], link_type: str) -> Optional[Any]:
        """
        Render link in Terminal mode using button-style y/n prompts.
        
        Terminal-First Design:
        - Color is the source of truth (semantic intent)
        - ANSI colors applied based on color parameter
        - Consistent with button primitive pattern for ALL link types
        
        Display Pattern:
        - Display: [{label}] with semantic color
        - Prompt: Click [{label}]? (y/n):
        - Action: Based on link type and user response
        
        Args:
            link_data: Link configuration dict
            link_type: Detected link type
        
        Returns:
            Navigation dict (for internal links) or None
        """
        href = link_data.get('href', '#')
        label = link_data.get('label', href)
        target = link_data.get('target', DEFAULT_TARGET)
        color = link_data.get('color', 'PRIMARY')
        
        # STEP 1: Display the link label (button-style, plain text)
        self.BasicOutputs.text(
            f"  [{label}]",
            indent=1,
            break_after=False
        )
        
        # STEP 2: Prompt with y/n - Apply SEMANTIC COLOR to prompt (Terminal-first pattern)
        # Use centralized color mapping from colors.py (single source of truth)
        terminal_color = self.zColors.get_semantic_color(color)
        prompt_text = PROMPT_LINK_TEMPLATE.format(label=label)
        
        # Apply semantic color to PROMPT (not label) - terminal-first visual feedback
        if terminal_color:
            colored_prompt = f"{terminal_color}{prompt_text}{self.zColors.RESET}"
        else:
            colored_prompt = prompt_text
        
        try:
            response = self.primitives.read_string(colored_prompt).strip().lower()
            
            # STEP 3: Handle response based on link type
            if response not in ('y', 'yes'):
                # User cancelled
                self.BasicOutputs.text(
                    f"  {label} cancelled.",
                    indent=1,
                    break_after=False
                )
                self.logger.debug(f"{LOG_PREFIX} Link cancelled by user: {label}")
                return "stop"
            
            # User confirmed - proceed based on link type
            if link_type == LINK_TYPE_PLACEHOLDER:
                # Placeholder - just acknowledge, no action
                self.BasicOutputs.text(
                    f"  {label} is a placeholder (no action).",
                    indent=1,
                    break_after=False
                )
                self.logger.debug(f"{LOG_PREFIX} Placeholder link clicked (no action): {label}")
                return None
            
            elif link_type == LINK_TYPE_INTERNAL_DELTA:
                # Delta link - navigate
                self.BasicOutputs.text(
                    f"  Navigating to {label}...",
                    indent=1,
                    break_after=False
                )
                self.logger.info(f"{LOG_PREFIX} Delta navigation confirmed: {href}")
                return {"zLink": href}
            
            elif link_type == LINK_TYPE_INTERNAL_ZPATH:
                # zPath link - navigate
                self.BasicOutputs.text(
                    f"  Navigating to {label}...",
                    indent=1,
                    break_after=False
                )
                self.logger.info(f"{LOG_PREFIX} zPath navigation confirmed: {href}")
                return {"zLink": href}
            
            elif link_type == LINK_TYPE_EXTERNAL:
                # External link - show URL then open
                self.BasicOutputs.text(
                    f"     → {href}",  # Show URL for transparency
                    indent=1,
                    color="MUTED"
                )
                self.BasicOutputs.text(
                    f"  Opening {label} in browser...",
                    indent=1,
                    break_after=False
                )
                self.logger.info(f"{LOG_PREFIX} External link confirmed: {href}")
                
                # Handle target for external links
                if target == TARGET_BLANK:
                    self.logger.info(f"{LOG_PREFIX} Opening in new window/tab (target: _blank)")
                
                # Open via zOpen subsystem (reusing primitive)
                return self.zcli.open.handle(f"zOpen({href})")
            
            elif link_type == LINK_TYPE_ANCHOR:
                # Anchor link - acknowledge but no scroll action (Terminal limitation)
                self.BasicOutputs.text(
                    f"     ⚓ {href}",  # Show anchor target
                    indent=1,
                    color="MUTED"
                )
                self.BasicOutputs.text(
                    f"  {label} is an anchor link (Terminal has no scroll).",
                    indent=1,
                    break_after=False
                )
                self.logger.debug(f"{LOG_PREFIX} Anchor link (Terminal limitation): {href}")
                return None
            
            return None
            
        except KeyboardInterrupt:
            self.BasicOutputs.text(
                f"  {label} cancelled.",
                indent=1,
                break_after=False
            )
            self.logger.debug(f"{LOG_PREFIX} Link cancelled (KeyboardInterrupt): {label}")
            return "stop"
    
    def _render_bifrost(self, link_data: Dict[str, Any], link_type: str) -> None:
        """
        Render link in Bifrost mode (send to frontend).
        
        Sends structured link event to frontend for semantic HTML rendering
        with proper <a> tags, target behavior, and security attributes.
        
        Args:
            link_data: Link configuration dict
            link_type: Detected link type
        
        Notes:
            - Frontend handles client-side routing for internal links
            - Security: rel="noopener noreferrer" auto-added for _blank
            - Window features: Supports custom width, height, and features
        """
        # Emit link event to frontend with all metadata
        event_data = {
            'event': EVENT_LINK,
            'label': link_data.get('label', ''),
            'href': link_data.get('href', '#'),
            'target': link_data.get('target', DEFAULT_TARGET),
            'rel': link_data.get('rel', ''),
            'link_type': link_type,
            '_zClass': link_data.get('_zClass', ''),
            'color': link_data.get('color', ''),
            'window': link_data.get('window', {})  # For window.open() features
        }
        
        # Auto-add security for external _blank links
        if (link_type == LINK_TYPE_EXTERNAL and 
            event_data['target'] == TARGET_BLANK and 
            not event_data['rel']):
            event_data['rel'] = 'noopener noreferrer'
            self.logger.debug(f"{LOG_PREFIX} Auto-added rel='noopener noreferrer' for external _blank link")
        
        # Send to frontend via primitives
        self.primitives.send_gui_event('link', event_data)
        self.logger.info(f"{LOG_PREFIX} Link event sent to Bifrost: {link_data.get('label')}")

