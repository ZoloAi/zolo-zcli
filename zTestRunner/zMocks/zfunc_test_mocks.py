# zMocks/plugins/zfunc_test_mocks.py
"""
Mock functions for zFunc testing.
Stable file used instead of temp files to avoid path resolution issues.
"""

import asyncio
from typing import Any, Dict, Optional

# ============================================================================
# Simple Test Functions
# ============================================================================

def simple_function():
    """Simple function with no parameters."""
    return "success"

def function_with_args(x, y):
    """Function with positional arguments."""
    return x + y

def function_with_kwargs(name=None, value=None):
    """Function with keyword arguments."""
    return {"name": name, "value": value}

def function_returns_dict():
    """Function that returns a dictionary."""
    return {"status": "ok", "data": [1, 2, 3]}

def function_returns_list():
    """Function that returns a list."""
    return [1, 2, 3, 4, 5]

def function_returns_number():
    """Function that returns a number."""
    return 42

def function_returns_boolean():
    """Function that returns a boolean."""
    return True

def function_returns_none():
    """Function that returns None."""
    return None

def function_with_exception():
    """Function that raises an exception."""
    raise ValueError("Test exception")

# ============================================================================
# Async Test Functions
# ============================================================================

async def async_simple():
    """Simple async function."""
    await asyncio.sleep(0.01)
    return "async_success"

async def async_with_args(x, y):
    """Async function with arguments."""
    await asyncio.sleep(0.01)
    return x * y

async def async_returns_dict():
    """Async function that returns a dictionary."""
    await asyncio.sleep(0.01)
    return {"async": True, "result": "ok"}

# ============================================================================
# Auto-Injection Test Functions
# ============================================================================

def function_with_zcli(zcli):
    """Function that expects zcli to be auto-injected."""
    return {"has_zcli": zcli is not None, "type": type(zcli).__name__}

def function_with_session(session):
    """Function that expects session to be auto-injected."""
    return {"has_session": session is not None, "type": type(session).__name__}

def function_with_context(context):
    """Function that expects context to be auto-injected."""
    return {"has_context": context is not None, "type": type(context).__name__}

def function_with_multiple_injection(zcli, session, context):
    """Function that expects multiple parameters to be auto-injected."""
    return {
        "has_zcli": zcli is not None,
        "has_session": session is not None,
        "has_context": context is not None
    }

def function_with_mixed_args(x, y, zcli, session):
    """Function with both regular and auto-injected parameters."""
    return {
        "sum": x + y,
        "has_zcli": zcli is not None,
        "has_session": session is not None
    }

# ============================================================================
# Context Injection Test Functions
# ============================================================================

def function_with_zcontext(zContext):
    """Function that expects zContext special argument."""
    return {"has_zContext": zContext is not None, "keys": list(zContext.keys()) if isinstance(zContext, dict) else []}

def function_with_zhat(zHat):
    """Function that expects zHat special argument."""
    return {"has_zHat": zHat is not None, "type": type(zHat).__name__}

def function_with_zconv(zConv):
    """Function that expects zConv special argument."""
    return {"has_zConv": zConv is not None, "type": type(zConv).__name__}

def function_with_all_special(zContext, zHat, zConv):
    """Function with all special context arguments."""
    return {
        "has_zContext": zContext is not None,
        "has_zHat": zHat is not None,
        "has_zConv": zConv is not None
    }

def function_with_regular_and_special(x, y, zContext):
    """Function with both regular and special arguments."""
    return {
        "sum": x + y,
        "has_context": zContext is not None
    }

