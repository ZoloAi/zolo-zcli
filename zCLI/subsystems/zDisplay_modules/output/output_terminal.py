# zCLI/subsystems/zDisplay_modules/output/output_terminal.py
"""
Terminal output adapter - Print to stdout (current implementation)
"""

from .output_adapter import OutputAdapter
from ..display_colors import Colors, print_line
from ..display_render import (
    render_marker as _render_marker,
    render_header as _render_header,
    render_menu as _render_menu,
    render_session as _render_session,
    render_json as _render_json,
    render_table as _render_table,
    print_crumbs as _print_crumbs
)
from ..display_forms import render_zConv as _render_zConv


class TerminalOutput(OutputAdapter):
    """
    Terminal output adapter.
    
    Renders to stdout using print() and ANSI colors.
    This is the current, fully-functional implementation.
    """
    
    def render_header(self, obj):
        """Render section header to terminal."""
        _render_header(obj)
    
    def render_menu(self, obj):
        """Render menu options to terminal."""
        _render_menu(obj)
    
    def render_table(self, obj):
        """Render data table to terminal."""
        _render_table(obj)
    
    def render_form(self, obj):
        """Render interactive form to terminal."""
        return _render_zConv(obj)
    
    def render_pause(self, obj):
        """Handle pause in terminal (blocking input)."""
        message = obj.get("message", "Press Enter to continue...")
        indent = obj.get("indent", 0)
        pagination = obj.get("pagination", {})
        
        indent_str = "  " * indent
        print(f"{indent_str}[||] {message}")
        
        # Check if we have pagination
        if pagination:
            current_page = pagination.get("current_page", 1)
            total_pages = pagination.get("total_pages", 1)
            
            if total_pages > 1:
                print(f"{indent_str}    Page {current_page} of {total_pages}")
                print(f"{indent_str}    [n] Next page | [p] Previous page | [Enter] Continue")
                
                user_input = input(f"{indent_str}>>> ").strip().lower()
                
                if user_input == 'n' and current_page < total_pages:
                    return {"action": "next_page"}
                elif user_input == 'p' and current_page > 1:
                    return {"action": "prev_page"}
        
        # Default: just wait for Enter
        input()
        return {"action": "continue"}
    
    def render_json(self, obj):
        """Render JSON data to terminal."""
        _render_json(obj)
    
    def render_session(self, obj):
        """Render session information to terminal."""
        _render_session(obj)
    
    def render_marker(self, obj):
        """Render flow marker to terminal."""
        _render_marker(obj)
    
    def render_crumbs(self, obj):
        """Render breadcrumb trail to terminal."""
        session = obj.get("zSession") if isinstance(obj, dict) else None
        _print_crumbs(session)
