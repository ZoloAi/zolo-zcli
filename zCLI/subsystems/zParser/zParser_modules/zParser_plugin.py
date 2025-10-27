# zCLI/subsystems/zParser/zParser_modules/zParser_plugin.py

"""
Plugin invocation parser with unified filename-based syntax.

Unified Syntax:
    &PluginName.function_name(args)

Architecture:
    1. Check cache by filename first (fast!)
    2. If not cached → search standard locations
    3. Load, cache by filename, execute
    4. Collision detection prevents duplicate filenames

Standard Search Paths:
    - @.utils
    - @.zCLI.utils
    - @.plugins

Examples:
    &test_plugin.hello_world("Alice")     # Checks cache → loads if needed
    &IDGenerator.generate_uuid()          # Simple, clean syntax
    &DateUtils.get_timestamp()            # No path complexity!
"""

import re
from pathlib import Path


# Standard search paths for plugin discovery
PLUGIN_SEARCH_PATHS = [
    "@",                   # Primary: Workspace root (for demo/test plugins)
    "@.zTestSuite.demos",  # Secondary: Test/demo plugins
    "@.utils",             # Tertiary: Workspace utilities
    "@.plugins",           # Quaternary: Workspace plugins directory
]


def is_plugin_invocation(value):
    """
    Check if value is a plugin invocation.
    
    Args:
        value: Value to check
        
    Returns:
        bool: True if value starts with & and looks like a plugin call
        
    Examples:
        >>> is_plugin_invocation("&test_plugin.hello()")
        True
        >>> is_plugin_invocation("regular_string")
        False
    """
    if not isinstance(value, str):
        return False
    
    # Must start with & and contain a dot (plugin.function)
    return value.startswith('&') and '.' in value


def resolve_plugin_invocation(value, zcli):
    """
    Resolve plugin function invocation with unified filename-based syntax.
    
    Syntax:
        &PluginName.function_name(args)
    
    Process:
        1. Parse: &PluginName.function_name(args)
        2. Check cache for "PluginName"
        3. If cached → get function → execute
        4. If not cached → search paths → load → cache → execute
    
    Args:
        value (str): Plugin invocation string
        zcli: zCLI instance with plugin cache
        
    Returns:
        Result of plugin function execution
        
    Raises:
        ValueError: If syntax invalid, plugin not found, or function not found
        
    Examples:
        >>> resolve_plugin_invocation("&test_plugin.hello_world('Alice')", zcli)
        "Hello, Alice!"
        
        >>> resolve_plugin_invocation("&IDGenerator.generate_uuid()", zcli)
        "550e8400-e29b-41d4-a716-446655440000"
    """
    if not isinstance(value, str) or not value.startswith('&'):
        return value
    
    # Step 1: Parse invocation
    plugin_name, function_name, args_str = _parse_invocation(value)
    
    # Step 2: Check cache first
    cached_module = zcli.loader.cache.get(plugin_name, cache_type="plugin")
    
    if cached_module:
        # Cache hit!
        zcli.logger.debug("Plugin cache HIT: %s", plugin_name)
        func = _get_function_from_module(cached_module, function_name, plugin_name)
        args, kwargs = _parse_arguments(args_str)
        return _execute_function(func, args, kwargs, value, zcli)
    
    # Step 3: Cache miss - search and load
    zcli.logger.debug("Plugin cache MISS: %s (searching...)", plugin_name)
    
    for search_path in PLUGIN_SEARCH_PATHS:
        try:
            # Construct full zPath
            zpath = f"{search_path}.{plugin_name}"
            
            # Resolve to absolute file path
            file_path = _resolve_zpath(zpath, zcli)
            
            if not file_path.endswith('.py'):
                file_path = f"{file_path}.py"
            
            # Check if file exists
            if not Path(file_path).is_file():
                continue
            
            # Load and cache (by filename)
            zcli.logger.debug("Loading plugin: %s from %s", plugin_name, file_path)
            module = zcli.loader.cache.plugin_cache.load_and_cache(file_path, plugin_name)
            
            # Execute function
            func = _get_function_from_module(module, function_name, plugin_name)
            args, kwargs = _parse_arguments(args_str)
            return _execute_function(func, args, kwargs, value, zcli)
            
        except FileNotFoundError:
            continue
        except Exception as e:
            if "collision" in str(e).lower():
                raise  # Re-raise collision errors
            zcli.logger.debug("Failed to load from %s: %s", search_path, e)
            continue
    
    # Step 4: Not found anywhere
    raise ValueError(
        f"Plugin not found: {plugin_name}\n"
        f"Searched in: {', '.join(PLUGIN_SEARCH_PATHS)}\n"
        f"Hint: Use 'plugin load <zPath>' to load from custom location"
    )


def _parse_invocation(value):
    """
    Parse &PluginName.function_name(args) into components.
    
    Args:
        value (str): Plugin invocation string
        
    Returns:
        tuple: (plugin_name, function_name, args_str)
        
    Raises:
        ValueError: If syntax is invalid
        
    Examples:
        >>> _parse_invocation("&test_plugin.hello('Alice')")
        ('test_plugin', 'hello', "'Alice'")
    """
    # Pattern: &PluginName.function_name(args)
    pattern = r'^&([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)$'
    match = re.match(pattern, value)
    
    if not match:
        raise ValueError(
            f"Invalid plugin invocation syntax: {value}\n"
            f"Expected format: &PluginName.function_name(args)\n"
            f"Examples:\n"
            f"  &test_plugin.hello_world('Alice')\n"
            f"  &IDGenerator.generate_uuid()\n"
            f"  &DateUtils.get_timestamp()"
        )
    
    plugin_name, function_name, args_str = match.groups()
    return plugin_name, function_name, args_str


def _resolve_zpath(zpath, zcli):
    """
    Resolve zPath to absolute file path.
    
    Args:
        zpath (str): zPath string (e.g., "@.utils.test_plugin")
        zcli: zCLI instance
        
    Returns:
        str: Absolute file path
    """
    # Parse zPath
    parts = zpath.split('.')
    symbol = parts[0]
    path_parts = parts[1:]
    
    # Resolve using zParser
    return zcli.zparser.resolve_symbol_path(symbol, [symbol] + path_parts)


def _get_function_from_module(module, function_name, plugin_name):
    """
    Get callable function from loaded module.
    
    Args:
        module: Loaded Python module
        function_name (str): Name of function to retrieve
        plugin_name (str): Plugin name for error messages
        
    Returns:
        callable: Function from module
        
    Raises:
        ValueError: If function not found or not callable
    """
    if not hasattr(module, function_name):
        available_funcs = [name for name in dir(module) 
                          if not name.startswith('_') and callable(getattr(module, name))]
        raise ValueError(
            f"Function not found in plugin '{plugin_name}': {function_name}\n"
            f"Available functions: {', '.join(available_funcs) if available_funcs else 'none'}"
        )
    
    func = getattr(module, function_name)
    
    if not callable(func):
        raise ValueError(
            f"'{function_name}' in plugin '{plugin_name}' is not callable"
        )
    
    return func


def _execute_function(func, args, kwargs, original_value, zcli):
    """
    Execute plugin function with error handling, zcli injection, and async support.
    
    Args:
        func: Callable function
        args: Positional arguments
        kwargs: Keyword arguments
        original_value: Original invocation string for error messages
        zcli: zCLI instance for dependency injection
        
    Returns:
        Result of function execution
        
    Raises:
        ValueError: If execution fails
    """
    import inspect
    import asyncio
    
    try:
        # Auto-inject zcli if function accepts it
        sig = inspect.signature(func)
        if 'zcli' in sig.parameters:
            zcli.logger.debug("Auto-injecting zcli instance to plugin function")
            kwargs['zcli'] = zcli
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Handle async functions (coroutines)
        if asyncio.iscoroutine(result):
            zcli.logger.debug("Plugin function returned coroutine - awaiting in event loop")
            try:
                # Check if event loop is already running (zBifrost mode)
                loop = asyncio.get_running_loop()
                zcli.logger.debug("Event loop is running - using run_coroutine_threadsafe")
                
                # Use run_coroutine_threadsafe to execute coroutine from sync context
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(result, loop)
                return future.result(timeout=300)  # 5 min timeout
                
            except RuntimeError:
                # No event loop running - use asyncio.run (Terminal mode)
                zcli.logger.debug("No running event loop - using asyncio.run()")
                return asyncio.run(result)
        
        return result
        
    except TypeError as e:
        raise ValueError(
            f"Plugin function call failed: {original_value}\n"
            f"Error: {e}\n"
            f"Check function signature and arguments"
        ) from e
    except Exception as e:
        raise ValueError(
            f"Plugin function execution failed: {original_value}\n"
            f"Error: {e}"
        ) from e


def _parse_arguments(args_str):
    """
    Parse function arguments from string.
    
    Supports:
        - Strings: "text", 'text'
        - Integers: 42
        - Floats: 3.14
        - Booleans: True, False
        - None: None
        - Keyword args: key=value
    
    Args:
        args_str (str): Arguments string from function call
        
    Returns:
        tuple: (args list, kwargs dict)
        
    Examples:
        >>> _parse_arguments("")
        ([], {})
        
        >>> _parse_arguments("'Alice', 30")
        (['Alice', 30], {})
        
        >>> _parse_arguments("name='Bob', age=25")
        ([], {'name': 'Bob', 'age': 25})
    """
    args = []
    kwargs = {}
    
    if not args_str or not args_str.strip():
        return args, kwargs
    
    # Split by comma, but respect quotes
    parts = _smart_split(args_str)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check for keyword argument (key=value)
        if '=' in part and not _is_quoted(part):
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            kwargs[key] = _parse_value(value)
        else:
            # Positional argument
            args.append(_parse_value(part))
    
    return args, kwargs


def _smart_split(text):
    """
    Split text by comma, respecting quotes.
    
    Args:
        text (str): Text to split
        
    Returns:
        list: Split parts
    """
    parts = []
    current = []
    in_quotes = False
    quote_char = None
    
    for char in text:
        if char in ('"', "'") and (not in_quotes or char == quote_char):
            in_quotes = not in_quotes
            quote_char = char if in_quotes else None
            current.append(char)
        elif char == ',' and not in_quotes:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    
    if current:
        parts.append(''.join(current))
    
    return parts


def _is_quoted(text):
    """Check if text is quoted."""
    text = text.strip()
    return ((text.startswith('"') and text.endswith('"')) or
            (text.startswith("'") and text.endswith("'")))


def _parse_value(value):
    """
    Parse a single value from string.
    
    Args:
        value (str): Value string
        
    Returns:
        Parsed value (str, int, float, bool, or None)
    """
    value = value.strip()
    
    # Handle quoted strings
    if _is_quoted(value):
        return value[1:-1]  # Remove quotes
    
    # Handle boolean
    if value == 'True':
        return True
    if value == 'False':
        return False
    
    # Handle None
    if value == 'None':
        return None
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string (unquoted)
    return value
