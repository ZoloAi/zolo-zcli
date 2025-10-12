# zCLI/subsystems/zShell_modules/executor_commands/alias_utils.py
# ───────────────────────────────────────────────────────────────
"""Alias resolution utilities for zCLI commands."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def resolve_alias(value, pinned_cache, raise_on_missing=True):
    """
    Resolve $alias to cached content from PinnedCache.
    
    This function checks if a value is an alias reference (starts with $)
    and looks it up in the PinnedCache. If found, returns the cached content.
    
    Args:
        value: Option value (e.g., "$sqlite_demo" or "normal_value")
        pinned_cache: PinnedCache instance from CacheOrchestrator
        raise_on_missing: If True, raises ValueError when alias not found.
                         If False, returns original value.
        
    Returns:
        Tuple: (resolved_value, is_alias)
               - If alias found: (parsed_content, True)
               - If not alias: (original_value, False)
               - If alias not found and raise_on_missing: raises ValueError
               - If alias not found and not raise_on_missing: (original_value, False)
    
    Examples:
        >>> resolve_alias("$sqlite_demo", pinned_cache)
        ({'users': {...}, 'posts': {...}}, True)
        
        >>> resolve_alias("@.zCLI.Schemas.zSchema.test", pinned_cache)
        ("@.zCLI.Schemas.zSchema.test", False)
    """
    # Not a string or doesn't start with $ - not an alias
    if not isinstance(value, str) or not value.startswith("$"):
        return value, False
    
    # Extract alias name (remove $ prefix)
    alias_name = value[1:]
    
    # Look up in pinned cache
    cached = pinned_cache.get_alias(alias_name)
    
    if cached is not None:
        logger.debug("[ALIAS] Resolved $%s from PinnedCache", alias_name)
        return cached, True
    
    # Alias not found
    if raise_on_missing:
        error_msg = (
            f"Alias not found: ${alias_name}\n"
            f"Use 'load <zPath> --as {alias_name}' to create this alias.\n"
            f"Example: load @.zCLI.Schemas.zSchema.{alias_name} --as {alias_name}"
        )
        logger.error("[ALIAS] %s", error_msg)
        raise ValueError(error_msg)
    else:
        logger.warning("[ALIAS] Alias $%s not found, using original value", alias_name)
        return value, False


def get_alias_name(alias_ref):
    """
    Extract the alias name from an alias reference.
    
    Args:
        alias_ref: Alias reference (e.g., "$sqlite_demo")
        
    Returns:
        Alias name without $ prefix, or None if not an alias
        
    Examples:
        >>> get_alias_name("$sqlite_demo")
        "sqlite_demo"
        
        >>> get_alias_name("normal_value")
        None
    """
    if isinstance(alias_ref, str) and alias_ref.startswith("$"):
        return alias_ref[1:]
    return None


def is_alias(value):
    """
    Check if a value is an alias reference.
    
    Args:
        value: Value to check
        
    Returns:
        bool: True if value starts with $, False otherwise
        
    Examples:
        >>> is_alias("$sqlite_demo")
        True
        
        >>> is_alias("@.zCLI.Schemas.zSchema.test")
        False
    """
    return isinstance(value, str) and value.startswith("$")


def resolve_option_aliases(options, loaded_cache, option_keys=None):
    """
    Resolve all alias references in an options dictionary.
    
    This is useful for commands that accept multiple options that could
    contain alias references (e.g., --model, --schema, --config).
    
    Args:
        options: Options dictionary from parsed command
        loaded_cache: LoadedCache instance from zLoader
        option_keys: List of option keys to check for aliases.
                    If None, checks all string values in options.
        
    Returns:
        dict: New options dict with resolved aliases
        
    Examples:
        >>> options = {"model": "$sqlite_demo", "limit": 10}
        >>> resolve_option_aliases(options, loaded_cache, ["model"])
        {"model": {...parsed_schema...}, "limit": 10, "_alias_resolved": {"model": "sqlite_demo"}}
    """
    resolved_options = options.copy()
    resolved_info = {}
    
    # Determine which keys to check
    keys_to_check = option_keys if option_keys else options.keys()
    
    for key in keys_to_check:
        if key not in options:
            continue
            
        value = options[key]
        
        # Try to resolve if it's an alias
        if is_alias(value):
            try:
                resolved_value, was_alias = resolve_alias(value, loaded_cache)
                if was_alias:
                    resolved_options[key] = resolved_value
                    resolved_info[key] = get_alias_name(value)
                    logger.debug("[ALIAS] Resolved option --%s: %s", key, value)
            except ValueError as e:
                # Re-raise with context
                raise ValueError(f"Failed to resolve --{key} alias: {e}") from e
    
    # Add metadata about resolved aliases
    if resolved_info:
        resolved_options["_alias_resolved"] = resolved_info
    
    return resolved_options

