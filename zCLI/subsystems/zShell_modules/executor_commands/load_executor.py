# zCLI/subsystems/zShell_modules/executor_commands/load_executor.py
# ───────────────────────────────────────────────────────────────
"""Load command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_load(zcli, parsed):
    """
    Execute load command to pin resources to cache.
    
    Commands:
      load @.schemas.schema          - Load and pin schema
      load @.ui.admin                - Load and pin UI file
      load --show                    - Show loaded resources
      load --clear [pattern]         - Clear loaded resources
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Load operation result
    """
    action = parsed.get("action")
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Handle --show flag
    if options.get("show") or action == "show":
        return show_loaded_resources(zcli)
    
    # Handle --clear flag
    if options.get("clear") or action == "clear":
        pattern = args[0] if args else None
        return clear_loaded_resources(zcli, pattern)
    
    # Load resource
    if not args:
        return {"error": "Usage: load <zPath> or load --show or load --clear"}
    
    zPath = args[0]
    
    try:
        # Load via zLoader (uses SmartCache)
        result = zcli.loader.handle(zPath)
        
        if result == "error" or result is None:
            return {"error": f"Failed to load: {zPath}"}
        
        # Determine resource type from zPath
        if "schema" in zPath:
            resource_type = "schema"
            key_prefix = "schema"
        elif "ui" in zPath:
            resource_type = "ui"
            key_prefix = "ui"
        else:
            resource_type = "config"
            key_prefix = "config"
        
        # Get resolved filepath from zParser
        if hasattr(zcli, 'zparser'):
            zVaFile_fullpath, zVaFilename = zcli.zparser.zPath_decoder(zPath, None)
            zFilePath_identified, _ = zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        else:
            zFilePath_identified = zPath
        
        # Pin to loaded cache
        loaded_key = f"parsed:{zFilePath_identified}"
        zcli.loader.loaded_cache.load(
            loaded_key,
            result,
            filepath=zFilePath_identified,
            resource_type=resource_type
        )
        
        # Count tables/blocks
        if resource_type == "schema":
            items = [k for k in result.keys() if k != "Meta"]
            item_type = "tables"
        else:
            items = list(result.keys())
            item_type = "blocks"
        
        logger.info("✅ Loaded %s: %s (%d %s)", resource_type, zPath, len(items), item_type)
        
        return {
            "status": "success",
            "type": resource_type,
            "path": zPath,
            "items": items,
            "count": len(items)
        }
        
    except Exception as e:
        logger.error("Failed to load %s: %s", zPath, e)
        return {"error": str(e)}


def show_loaded_resources(zcli):
    """Show all loaded resources."""
    resources = zcli.loader.loaded_cache.list_loaded()
    
    if not resources:
        print("\nNo resources currently loaded.")
        print("Use 'load <zPath>' to pin resources to cache.")
        return {"status": "empty"}
    
    print("\n" + "=" * 70)
    print("Loaded Resources (Pinned in Cache)")
    print("=" * 70)
    
    # Group by type
    by_type = {}
    for res in resources:
        res_type = res["type"]
        if res_type not in by_type:
            by_type[res_type] = []
        by_type[res_type].append(res)
    
    for res_type, items in by_type.items():
        print(f"\n{res_type.upper()}:")
        for item in items:
            age_mins = int(item["age"] / 60)
            print(f"  • {item['key']}")
            print(f"    Path: {item.get('filepath', 'N/A')}")
            print(f"    Loaded: {age_mins} minutes ago")
    
    print("\n" + "=" * 70)
    print(f"Total: {len(resources)} pinned resources")
    print("Use 'load --clear [pattern]' to remove")
    print("=" * 70)
    
    return {"status": "success", "count": len(resources), "resources": resources}


def clear_loaded_resources(zcli, pattern=None):
    """Clear loaded resources."""
    count = zcli.loader.loaded_cache.clear(pattern)
    
    if pattern:
        print(f"\n✅ Cleared {count} loaded resources matching '{pattern}'")
    else:
        print(f"\n✅ Cleared all {count} loaded resources")
    
    return {"status": "success", "cleared": count}
