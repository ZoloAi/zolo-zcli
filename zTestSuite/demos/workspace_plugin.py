#!/usr/bin/env python3
# zCLI/utils/workspace_plugin.py

"""
Workspace Test Plugin - For testing & invocations with workspace-relative paths.

This plugin is used to test the & and &@ path modifiers.
"""


def workspace_greeting(name="Workspace"):
    """
    Return a workspace-specific greeting.
    
    Args:
        name (str): Name to greet
        
    Returns:
        str: Greeting message
    """
    return f"Hello from workspace, {name}!"


def workspace_multiply(a, b):
    """
    Multiply two numbers.
    
    Args:
        a (int/float): First number
        b (int/float): Second number
        
    Returns:
        int/float: Product of a and b
    """
    return a * b


def get_workspace_info():
    """
    Get workspace plugin info.
    
    Returns:
        dict: Plugin metadata
    """
    return {
        "name": "Workspace Plugin",
        "location": "workspace-relative",
        "path_modifier": "&"
    }

