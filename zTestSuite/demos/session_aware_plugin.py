#!/usr/bin/env python3
# zCLI/utils/session_aware_plugin.py

"""
Session-Aware Plugin - Demonstrates CLI session access.

This plugin showcases how plugins can access zCLI subsystems:
- Logger for logging
- Session for workspace, machine info, etc.
- Data subsystem for database operations
- Display for output

The `zcli` variable is automatically injected by zUtils/PluginCache.
"""


def get_workspace():
    """
    Get current workspace path from CLI session.
    
    Returns:
        str: Workspace path or '.' if not set
    """
    if hasattr(zcli, 'session'):
        return zcli.session.get('zSpace', '.')
    return '.'


def get_machine_info():
    """
    Get machine information from CLI session.
    
    Returns:
        dict: Machine information (hostname, username, os, etc.)
    """
    if hasattr(zcli, 'session'):
        machine_data = zcli.session.get('zMachine', {})
        return {
            "hostname": machine_data.get('hostname', 'unknown'),
            "username": machine_data.get('username', 'unknown'),
            "os": machine_data.get('os', 'unknown'),
            "arch": machine_data.get('arch', 'unknown')
        }
    return {}


def log_message(message, level="info"):
    """
    Log a message using CLI logger.
    
    Args:
        message (str): Message to log
        level (str): Log level (debug, info, warning, error)
    """
    if hasattr(zcli, 'logger'):
        log_func = getattr(zcli.logger, level, zcli.logger.info)
        log_func(f"[SessionAwarePlugin] {message}")
        return f"Logged: {message}"
    return "Logger not available"


def get_session_id():
    """
    Get current session ID.
    
    Returns:
        str: Session ID or 'unknown'
    """
    if hasattr(zcli, 'session'):
        return zcli.session.get('zS_id', 'unknown')
    return 'unknown'


def display_message(message, color="INFO"):
    """
    Display a message using CLI display subsystem.
    
    Args:
        message (str): Message to display
        color (str): Color code
        
    Returns:
        str: Confirmation message
    """
    if hasattr(zcli, 'display'):
        zcli.display.zDeclare(message, color=color, indent=1, style="single")
        return f"Displayed: {message}"
    return "Display not available"


def get_plugin_cache_stats():
    """
    Get plugin cache statistics.
    
    Returns:
        dict: Cache statistics
    """
    if hasattr(zcli, 'loader') and hasattr(zcli.loader, 'cache'):
        return zcli.loader.cache.get_stats(cache_type="plugin")
    return {}


def test_all_features():
    """
    Test all plugin features and return results.
    
    Returns:
        dict: Test results
    """
    results = {
        "workspace": get_workspace(),
        "machine_info": get_machine_info(),
        "session_id": get_session_id(),
        "cache_stats": get_plugin_cache_stats(),
        "has_logger": hasattr(zcli, 'logger'),
        "has_display": hasattr(zcli, 'display'),
        "has_data": hasattr(zcli, 'data'),
        "has_session": hasattr(zcli, 'session')
    }
    
    # Log the test
    log_message("Plugin test completed successfully")
    
    return results

