# zCLI/subsystems/zShell/zShell_modules/executor_commands/plugin_executor.py

"""Plugin command execution for zCLI shell."""


def execute_plugin(zcli, parsed):
    """
    Execute plugin command for loading/managing plugins.
    
    Commands:
        plugin load <zPath>          - Load plugin from zPath
        plugin show                  - Show loaded plugins
        plugin show cache            - Show plugin cache stats
        plugin clear [pattern]       - Clear plugin cache
        plugin reload <zPath>        - Reload plugin (clear + load)
    
    Examples:
        plugin load @.zCLI.utils.my_plugin
        plugin load ~/plugins/custom.py
        plugin load zMachine.plugins.helper
        plugin show
        plugin clear test_plugin
    """
    # Get action from parsed command (set by _parse_plugin_command)
    action = parsed.get("action")
    args = parsed.get("args", [])
    
    if not action:
        return {
            "error": "Usage: plugin <command> [args]\n"
                    "Commands: load, show, clear, reload"
        }
    
    if action == "load":
        return load_plugin(zcli, args)
    elif action == "show":
        return show_plugins(zcli, args)
    elif action == "clear":
        return clear_plugins(zcli, args)
    elif action == "reload":
        return reload_plugin(zcli, args)
    else:
        return {"error": f"Unknown plugin command: {action}"}


def load_plugin(zcli, args):
    """Load a plugin from zPath."""
    if not args:
        return {"error": "Usage: plugin load <zPath>"}
    
    zpath = args[0]
    
    try:
        # Resolve zPath to absolute file path
        # Support @, ~, and zMachine paths
        if zpath.startswith("zMachine."):
            file_path = zcli.zparser.resolve_zmachine_path(zpath)
        else:
            # Parse zPath (@ or ~ or relative)
            symbol = '@' if zpath.startswith('@') else ('~' if zpath.startswith('~') else '@')
            path_str = zpath[1:] if zpath.startswith(('@', '~')) else zpath
            path_parts = path_str.split('.')
            
            # Prepend symbol for resolve_symbol_path
            zRelPath_parts = [symbol] + path_parts
            file_path = zcli.zparser.resolve_symbol_path(symbol, zRelPath_parts)
        
        # Add .py extension if not present
        if not file_path.endswith('.py'):
            file_path = f"{file_path}.py"
        
        # Check if file exists
        import os
        if not os.path.isfile(file_path):
            return {"error": f"Plugin file not found: {file_path}"}
        
        # Load via PluginCache (handles caching and session injection)
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        module = zcli.loader.cache.plugin_cache.load_and_cache(file_path, module_name)
        
        # Get available functions
        functions = [name for name in dir(module) 
                    if not name.startswith('_') and callable(getattr(module, name))]
        
        zcli.display.success(f"[OK] Loaded plugin: {module_name}")
        zcli.display.info(f"  Path: {file_path}")
        zcli.display.info(f"  Functions: {', '.join(functions) if functions else 'none'}")
        
        return {
            "success": True,
            "module_name": module_name,
            "file_path": file_path,
            "functions": functions
        }
        
    except Exception as e:
        return {"error": f"Failed to load plugin: {e}"}


def show_plugins(zcli, args):
    """Show loaded plugins or cache stats."""
    if args and args[0] == "cache":
        # Show cache statistics
        stats = zcli.loader.cache.get_stats(cache_type="plugin")
        plugin_cache_stats = stats.get("plugin_cache", {})
        
        zcli.display.header("Plugin Cache Statistics")
        zcli.display.text(f"Size: {plugin_cache_stats.get('size', 0)}/{plugin_cache_stats.get('max_size', 0)}")
        zcli.display.text(f"Hits: {plugin_cache_stats.get('hits', 0)}")
        zcli.display.text(f"Misses: {plugin_cache_stats.get('misses', 0)}")
        zcli.display.text(f"Hit Rate: {plugin_cache_stats.get('hit_rate', '0%')}")
        zcli.display.text(f"Loads: {plugin_cache_stats.get('loads', 0)}")
        zcli.display.text(f"Evictions: {plugin_cache_stats.get('evictions', 0)}")
        zcli.display.text(f"Invalidations: {plugin_cache_stats.get('invalidations', 0)}")
        zcli.display.text(f"Collisions: {plugin_cache_stats.get('collisions', 0)}")
        
        return {"success": True, "stats": plugin_cache_stats}
    
    # Show loaded plugins from PluginCache (filename-based)
    cached_plugins = zcli.loader.cache.plugin_cache.list_plugins()
    
    zcli.display.header("Loaded Plugins")
    
    if cached_plugins:
        for plugin_info in cached_plugins:
            name = plugin_info.get("name", "unknown")
            filepath = plugin_info.get("filepath", "unknown")
            hits = plugin_info.get("hits", 0)
            
            zcli.display.text(f"\n[BULLET] {name}")
            zcli.display.text(f"  Path: {filepath}")
            zcli.display.text(f"  Cache hits: {hits}")
    else:
        zcli.display.warning("No plugins loaded")
        zcli.display.info("Use 'plugin load <zPath>' to load a plugin")
        zcli.display.info("Or use '&PluginName.function()' - auto-loads from standard paths")
    
    total = len(cached_plugins)
    zcli.display.text(f"\nTotal: {total} plugins")
    
    return {
        "success": True,
        "plugins": cached_plugins,
        "total": total
    }


def clear_plugins(zcli, args):
    """Clear plugin cache."""
    pattern = args[0] if args else None
    
    if pattern:
        zcli.loader.cache.clear(cache_type="plugin", pattern=pattern)
        zcli.display.success(f"[OK] Cleared plugins matching: {pattern}")
    else:
        zcli.loader.cache.clear(cache_type="plugin")
        zcli.display.success("[OK] Cleared all cached plugins")
    
    return {"success": True, "pattern": pattern}


def reload_plugin(zcli, args):
    """Reload a plugin (clear + load)."""
    if not args:
        return {"error": "Usage: plugin reload <zPath>"}
    
    zpath = args[0]
    
    # Extract module name for clearing
    path_parts = zpath.replace('@.', '').replace('~.', '').replace('zMachine.', '').split('.')
    module_name = path_parts[-1]
    
    # Clear from cache
    clear_result = clear_plugins(zcli, [module_name])
    if "error" in clear_result:
        return clear_result
    
    # Load fresh
    load_result = load_plugin(zcli, [zpath])
    if "error" in load_result:
        return load_result
    
    zcli.display.success(f"[OK] Reloaded plugin: {module_name}")
    
    return {
        "success": True,
        "module_name": module_name,
        "reloaded": True
    }

