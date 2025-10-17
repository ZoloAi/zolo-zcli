# zCLI/subsystems/zDisplay/zDisplay_modules/events/walker/menu.py

# zCLI/subsystems/zDisplay_modules/events/walker/menu.py
"""Menu display handler for Walker navigation."""

def handle_menu(obj, output_adapter, logger):
    """Render menu options with numbers for Walker navigation."""
    menu_items = obj.get("menu", [])
    
    if not menu_items:
        logger.warning("zMenu called with empty menu")
        return
    
    logger.debug("Rendering menu with %d items", len(menu_items))
    
    # Use output adapter to print menu
    output_adapter.write_line("")  # Blank line before menu
    for number, option in menu_items:
        output_adapter.write_line(f"  [{number}] {option}")

