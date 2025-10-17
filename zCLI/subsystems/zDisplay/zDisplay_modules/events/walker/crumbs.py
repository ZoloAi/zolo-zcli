# zCLI/subsystems/zDisplay/zDisplay_modules/events/walker/crumbs.py

# zCLI/subsystems/zDisplay_modules/events/walker/crumbs.py
"""Breadcrumb trail display handler."""

def handle_crumbs(obj, output_adapter, logger):
    """Render breadcrumb trail showing navigation path."""

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

