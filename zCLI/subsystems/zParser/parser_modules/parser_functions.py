# zCLI/subsystems/zParser/parser_modules/parser_functions.py
"""
Function call resolution for zParser.

Handles parsing and resolution of &function calls in zUI content (declarative YAML).
This enables calling built-in functions like &zNow directly from YAML configuration.
"""

import re
from zCLI import Any


def resolve_function_call(value: str, zcli: Any) -> str:
    """
    Resolve &function calls in zUI content.
    
    Syntax:
        &zNow → zNow()
        &zNow('date') → zNow('date')
        &zNow(custom_format='yyyy-mm-dd') → zNow(custom_format='yyyy-mm-dd')
    
    Args:
        value: String potentially containing &function calls
        zcli: zCLI instance for function execution
        
    Returns:
        String with function calls resolved to their values
        
    Examples:
        >>> resolve_function_call("Today is &zNow('date')", zcli)
        "Today is 19122025"
        
        >>> resolve_function_call("Report: &zNow", zcli)
        "Report: 19122025 14:30:00"
    """
    # Pattern: &functionName or &functionName(...args...)
    pattern = r'&(\w+)(?:\((.*?)\))?'
    
    def replace_function(match):
        func_name = match.group(1)
        args_str = match.group(2) if match.group(2) else ""
        
        # Handle zNow
        if func_name == "zNow":
            if not args_str:
                return zcli.zfunc.zNow()
            else:
                # Parse simple arg: 'date', 'time', or custom_format='...'
                args_str = args_str.strip().strip("'\"")
                if args_str in ["date", "time", "datetime"]:
                    return zcli.zfunc.zNow(format_type=args_str)
                elif args_str.startswith("custom_format="):
                    custom_fmt = args_str.split("=", 1)[1].strip("'\"")
                    return zcli.zfunc.zNow(custom_format=custom_fmt)
                else:
                    # Default: treat as format_type
                    return zcli.zfunc.zNow(format_type=args_str)
        
        # Unknown function - return as-is (no modification)
        return match.group(0)
    
    return re.sub(pattern, replace_function, value)

