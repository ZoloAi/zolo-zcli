# zCLI/subsystems/zShell/zShell_modules/executor_commands/load_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/load_executor.py
# ───────────────────────────────────────────────────────────────
"""Load command execution for zCLI."""

def execute_load(zcli, parsed):
    """Execute load command to pin resources to cache."""
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Check if first arg is a subcommand (show/clear)
    if args and args[0] in ["show", "clear"]:
        subcommand = args[0]
        remaining_args = args[1:]
        
        if subcommand == "show":
            # Handle show variants
            if not remaining_args:
                # load show - show all tiers
                return show_all_cache_tiers(zcli)
            elif remaining_args[0] == "pinned":
                # load show pinned - show Tier 1 only
                return show_pinned_resources(zcli)
            elif remaining_args[0] == "cached":
                # load show cached - show Tier 2 only
                return show_cached_stats(zcli)
            elif remaining_args[0] == "aliases":
                # load show aliases - show all aliases
                return show_aliases(zcli)
            elif remaining_args[0] in ["schemas", "ui", "config"]:
                # load show schemas/ui/config - filter by type
                return show_resources_by_type(zcli, remaining_args[0])
            else:
                return {"error": f"Unknown show option: {remaining_args[0]}"}
        elif subcommand == "clear":
            pattern = remaining_args[0] if remaining_args else None
            return clear_loaded_resources(zcli, pattern)
    
    # Load resource
    if not args:
        return {"error": "Usage: load <zPath> [--as <alias>] | load show | load clear [pattern]"}
    
    zPath = args[0]
    alias = options.get("as")
    
    try:
        # For aliases, we want to bypass the "no schema caching" rule
        # Load directly without going through handle() to ensure schemas are cached
        if alias:
            # Load raw file
            from zCLI.subsystems.zLoader.zLoader_modules.loader_io import load_file_raw
            
            # Get resolved filepath from zParser
            zVaFile_fullpath, zVaFilename = zcli.zparser.zPath_decoder(zPath, None)
            zFilePath_identified, zFile_extension = zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
            
            # Read raw content
            zFile_raw = load_file_raw(zFilePath_identified, zcli.logger, zcli.display)
            
            # Parse content
            result = zcli.zparser.parse_file_content(zFile_raw, zFile_extension)
            
            if result == "error" or result is None:
                return {"error": f"Failed to load: {zPath}"}
        else:
            # Traditional load via zLoader (uses SmartCache)
            result = zcli.loader.handle(zPath)
            
            if result == "error" or result is None:
                return {"error": f"Failed to load: {zPath}"}
            
            # Get resolved filepath from zParser
            zVaFile_fullpath, zVaFilename = zcli.zparser.zPath_decoder(zPath, None)
            zFilePath_identified, _ = zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        
        # Determine resource type using proper zVaFile detection
        if "zSchema." in zPath:
            resource_type = "schema"
        elif "zUI." in zPath:
            resource_type = "ui"
        elif "zConfig." in zPath:
            resource_type = "config"
        else:
            resource_type = "other"
        
        # Pin to cache (pinned_cache for aliases, system_cache for regular loads)
        if alias:
            # Store in pinned_cache with alias
            zcli.loader.cache.pinned_cache.load_alias(
                alias_name=alias,
                parsed_schema=result,
                zpath=zPath
            )
            display_name = f"${alias}"
        else:
            # Store in system_cache (not pinned_cache)
            # This is for 'load <path>' without --as
            display_name = zPath
        
        # Count tables/blocks
        if resource_type == "schema":
            items = [k for k in result.keys() if k != "Meta"]
            item_type = "tables"
        else:
            items = list(result.keys())
            item_type = "blocks"
        
        if alias:
            zcli.logger.info("✅ Loaded and aliased %s: %s → %s (%d %s)", 
                       resource_type, zPath, display_name, len(items), item_type)
        else:
            zcli.logger.info("✅ Loaded %s: %s (%d %s)", resource_type, zPath, len(items), item_type)
        
        return {
            "status": "success",
            "type": resource_type,
            "path": zPath,
            "alias": alias,
            "items": items,
            "count": len(items)
        }
        
    except Exception as e:  # pylint: disable=broad-except
        zcli.logger.error("Failed to load %s: %s", zPath, e)
        return {"error": str(e)}


def show_all_cache_tiers(zcli):
    """Show all three cache tiers."""
    print("\n" + "=" * 70)
    print("Cache System - Three Tiers")
    print("=" * 70)
    
    total_items = 0
    
    # ═══════════════════════════════════════════════════════════
    # TIER 1: Pinned Cache (User-Loaded Aliases)
    # ═══════════════════════════════════════════════════════════
    print("\n╔═══ Tier 1: Pinned Cache (User-Loaded Aliases) ═══╗")
    
    loaded_resources = zcli.loader.cache.pinned_cache.list_aliases()
    
    if loaded_resources:
        # Group by type
        by_type = {}
        for res in loaded_resources:
            res_type = res.get("type", "unknown")
            if res_type not in by_type:
                by_type[res_type] = []
            by_type[res_type].append(res)
        
        for res_type, items in by_type.items():
            print(f"\n{res_type.upper()}:")
            
            for item in items:
                age_mins = int(item["age"] / 60)
                print(f"  • ${item['name']}")
                print(f"    Path: {item.get('zpath', 'N/A')}")
                print(f"    Age: {age_mins} minutes")
        
        total_items += len(loaded_resources)
        print(f"\nTotal: {len(loaded_resources)} pinned resources")
    else:
        print("  (empty - use 'load <zPath>' to pin resources)")
    
    # ═══════════════════════════════════════════════════════════
    # TIER 2: System Cache (Auto-Cached Files)
    # ═══════════════════════════════════════════════════════════
    print("\n╔═══ Tier 2: System Cache (Auto-Cached Files) ═══╗")
    
    # Get system cache statistics
    system_stats = zcli.loader.cache.system_cache.get_stats()
    
    print(f"  Size: {system_stats.get('size', 0)}/{system_stats.get('max_size', 0)}")
    print(f"  Hit Rate: {system_stats.get('hit_rate', '0%')}")
    print(f"  Hits: {system_stats.get('hits', 0)} | Misses: {system_stats.get('misses', 0)}")
    print(f"  Evictions: {system_stats.get('evictions', 0)} | Invalidations: {system_stats.get('invalidations', 0)}")
    
    total_items += system_stats.get('size', 0)
    
    # ═══════════════════════════════════════════════════════════
    # TIER 3: Disk I/O
    # ═══════════════════════════════════════════════════════════
    print("\n╔═══ Tier 3: Disk I/O (Fallback) ═══╗")
    print("  Loads directly from filesystem when not cached")
    print("  No eviction - always available")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Total Cached Items: {total_items}")
    print("=" * 70 + "\n")
    
    return {
        "status": "success",
        "tier1_count": len(loaded_resources),
        "tier2_count": system_stats.get('size', 0),
        "total": total_items
    }


def show_pinned_resources(zcli):
    """Show only Tier 1 (pinned/loaded) resources."""
    print("\n" + "=" * 70)
    print("Tier 1: Pinned Cache (User-Loaded Aliases)")
    print("=" * 70)
    
    loaded_resources = zcli.loader.cache.pinned_cache.list_aliases()
    
    if not loaded_resources:
        print("\nNo pinned resources.")
        print("Use 'load <zPath>' to pin resources to cache.")
        return {"status": "empty"}
    
    # Group by type
    by_type = {}
    for res in loaded_resources:
        res_type = res.get("type", "unknown")
        if res_type not in by_type:
            by_type[res_type] = []
        by_type[res_type].append(res)
    
    for res_type, items in by_type.items():
        print(f"\n{res_type.upper()}:")
        for item in items:
            age_mins = int(item["age"] / 60)
            print(f"  • ${item['name']}")
            print(f"    Path: {item.get('zpath', 'N/A')}")
            print(f"    Age: {age_mins} minutes")
    
    print(f"\n{'=' * 70}")
    print(f"Total: {len(loaded_resources)} pinned resources")
    print("=" * 70 + "\n")
    
    return {"status": "success", "count": len(loaded_resources)}


def show_cached_stats(zcli):
    """Show only Tier 2 (system cache) statistics."""
    print("\n" + "=" * 70)
    print("Tier 2: System Cache (Auto-Cached Files)")
    print("=" * 70)
    
    system_stats = zcli.loader.cache.system_cache.get_stats()
    
    print(f"\nNamespace: {system_stats.get('namespace', 'N/A')}")
    print(f"Size: {system_stats.get('size', 0)}/{system_stats.get('max_size', 0)} entries")
    print("\nPerformance:")
    print(f"  Hit Rate: {system_stats.get('hit_rate', '0%')}")
    print(f"  Hits: {system_stats.get('hits', 0)}")
    print(f"  Misses: {system_stats.get('misses', 0)}")
    print("\nMaintenance:")
    print(f"  Evictions: {system_stats.get('evictions', 0)} (LRU)")
    print(f"  Invalidations: {system_stats.get('invalidations', 0)} (mtime)")
    
    print("\n" + "=" * 70 + "\n")
    
    return {"status": "success", "stats": system_stats}


def show_resources_by_type(zcli, resource_type):
    """Show resources filtered by type (schemas, ui, config)."""
    # Normalize type name
    type_map = {
        "schemas": "schema",
        "ui": "ui", 
        "config": "config"
    }
    filter_type = type_map.get(resource_type, resource_type)
    
    print("\n" + "=" * 70)
    print(f"Resources: {filter_type.upper()}")
    print("=" * 70)
    
    loaded_resources = zcli.loader.cache.pinned_cache.list_aliases()
    filtered = [r for r in loaded_resources if r.get("type") == filter_type]
    
    if not filtered:
        print(f"\nNo {filter_type} resources loaded.")
        print(f"Use 'load @.{filter_type}s.{filter_type}' to load {filter_type} resources.")
        return {"status": "empty"}
    
    print(f"\nFound {len(filtered)} {filter_type} resource(s):\n")
    for item in filtered:
        age_mins = int(item["age"] / 60)
        print(f"  • ${item['name']}")
        print(f"    Path: {item.get('zpath', 'N/A')}")
        print(f"    Age: {age_mins} minutes")
    
    print("\n" + "=" * 70 + "\n")
    
    return {"status": "success", "type": filter_type, "count": len(filtered)}


def show_aliases(zcli):
    """Show all defined aliases (resources loaded with --as flag)."""
    print("\n" + "=" * 70)
    print("Defined Aliases")
    print("=" * 70)
    
    aliases = zcli.loader.cache.pinned_cache.list_aliases()
    
    if not aliases:
        print("\nNo aliases defined.")
        print("Use 'load <zPath> --as <alias>' to create an alias.")
        print("\nExample:")
        print("  load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo")
        print("  data read users --model $sqlite_demo")
        return {"status": "empty"}
    
    # Group by type
    by_type = {}
    for alias_res in aliases:
        res_type = alias_res.get("type", "unknown")
        if res_type not in by_type:
            by_type[res_type] = []
        by_type[res_type].append(alias_res)
    
    for res_type, items in by_type.items():
        print(f"\n{res_type.upper()}:")
        for item in items:
            age_mins = int(item["age"] / 60)
            print(f"  ${item['name']}")
            print(f"    → {item.get('zpath', 'N/A')}")
            print(f"    Age: {age_mins} minutes")
    
    print(f"\n{'=' * 70}")
    print(f"Total: {len(aliases)} alias(es)")
    print("=" * 70 + "\n")
    
    return {"status": "success", "count": len(aliases), "aliases": aliases}


def clear_loaded_resources(zcli, pattern=None):
    """Clear loaded resources."""
    count = zcli.loader.cache.pinned_cache.clear(pattern)
    
    if pattern:
        print(f"\n✅ Cleared {count} loaded resources matching '{pattern}'")
    else:
        print(f"\n✅ Cleared all {count} loaded resources")
    
    return {"status": "success", "cleared": count}
