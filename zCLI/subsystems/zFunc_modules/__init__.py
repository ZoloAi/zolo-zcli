# zCLI/subsystems/zFunc_modules/__init__.py
"""zFunc module registry - function loading and execution helpers."""

# Import modules for use by zFunc
from .func_args import parse_arguments, split_arguments
from .func_resolver import resolve_callable

__all__ = [
    "parse_arguments",
    "split_arguments",
    "resolve_callable",
]

