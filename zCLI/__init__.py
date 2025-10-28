# zCLI/__init__.py

"""Main zCLI package exposing the `zCLI` core class."""

# Central imports for the entire zCLI system
# Standard library imports
import asyncio
import getpass
import importlib
import importlib.util
import inspect
import json
import logging
import os
import platform
import re
import secrets
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import traceback
import typing
import uuid
import webbrowser
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

# Third-party imports
import platformdirs  # pylint: disable=import-error
import requests  # pylint: disable=import-error
import yaml  # pylint: disable=import-error

# Optional third-party helper (fallback implementation if python-dotenv missing)
if importlib.util.find_spec("dotenv") is not None:
    from dotenv import load_dotenv  # pylint: disable=import-error
else:  # pragma: no cover - exercised when python-dotenv is unavailable
    def load_dotenv(dotenv_path=None, override=True):
        """Minimal fallback dotenv loader when python-dotenv is unavailable."""
        path = Path(dotenv_path) if dotenv_path else Path.cwd() / ".env"
        if not path.exists():
            return False

        loaded_any = False
        with path.open("r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                key, sep, value = line.partition("=")
                if not sep:
                    continue

                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if override or key not in os.environ:
                    os.environ[key] = value
                loaded_any = True

        return loaded_any

# Import utilities (safe to import early)
from .utils.colors import Colors

# Import the zCLI Core and Walker
from .zCLI import zCLI

# Export the main interfaces
__all__ = [
    # Core class
    "zCLI",

    # System modules
    "asyncio", "datetime", "getpass", "importlib", "inspect", "json", 
    "logging", "os", "platform", "platformdirs", "re", "requests", "secrets",
    "shutil", "socket", "sqlite3", "subprocess", "sys", "time", "traceback",
    "typing", "uuid", "webbrowser", "yaml", "OrderedDict", "Path", "urlparse",

    # Typing helpers
    "Any", "Callable", "Dict", "List", "Optional", "Tuple", "Union",

    # Third-party helpers
    "load_dotenv",

    # Utils
    "Colors",
]
