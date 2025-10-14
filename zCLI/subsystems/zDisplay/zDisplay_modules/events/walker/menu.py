# zCLI/subsystems/zDisplay_modules/events/walker/menu.py
"""Menu display handler for Walker navigation."""

from logger import Logger

logger = Logger.get_logger(__name__)


def handle_menu(obj, output_adapter):
    """
    Render menu options with numbers.
    
    Used by Walker for vertical navigation - displays numbered menu items
    that the user can select from.
    
    Args:
        obj: Display object with 'menu' key containing list of (number, option) tuples
        output_adapter: Output adapter for rendering
        
    Example obj:
        {
            "event": "zMenu",
            "menu": [(0, "Option A"), (1, "Option B"), (2, "zBack")]
        }
    """
    menu_items = obj.get("menu", [])
    
    if not menu_items:
        logger.warning("zMenu called with empty menu")
        return
    
    logger.debug("Rendering menu with %d items", len(menu_items))
    
    # Use output adapter to print menu
    output_adapter.write_line("")  # Blank line before menu
    for number, option in menu_items:
        output_adapter.write_line(f"  [{number}] {option}")

