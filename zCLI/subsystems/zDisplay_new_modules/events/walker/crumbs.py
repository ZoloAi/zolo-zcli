# zCLI/subsystems/zDisplay_new_modules/events/walker/crumbs.py
"""Breadcrumb trail display handler."""

from logger import Logger

logger = Logger.get_logger(__name__)


def handle_crumbs(obj, output_adapter):
    """
    Render breadcrumb trail showing navigation path.
    
    Displays the current navigation trail for each scope in the session's zCrumbs.
    Shows where the user has navigated within the Walker UI.
    
    Args:
        obj: Display object with optional 'zSession' key containing zCrumbs
        output_adapter: Output adapter for rendering
        
    Example obj:
        {
            "event": "zCrumbs",
            "zSession": {
                "zCrumbs": {
                    "@.UI.zUI.zVaF": ["menu1", "submenu2"],
                    "@.UI.zUI.zVaF.submenu2": []
                }
            }
        }
        
    Output example:
        zCrumbs:
          @.UI.zUI.zVaF[menu1 > submenu2]
          @.UI.zUI.zVaF.submenu2[]
    """
    # Extract session from object or use empty dict
    session = obj.get("zSession", {})
    z_crumbs = session.get("zCrumbs", {})
    
    if not z_crumbs:
        logger.debug("No breadcrumbs in session")
        return
    
    logger.debug("Rendering breadcrumbs for %d scopes", len(z_crumbs))
    
    # Build formatted breadcrumb display
    crumbs_display = {}
    for scope, trail in z_crumbs.items():
        # Join trail with " > " separator, or show empty
        path = " > ".join(trail) if trail else ""
        crumbs_display[scope] = path
    
    # Display breadcrumbs
    output_adapter.write_line("\nzCrumbs:")
    for scope, path in crumbs_display.items():
        output_adapter.write_line(f"  {scope}[{path}]")

