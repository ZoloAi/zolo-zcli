# zCLI/__init__.py

"""Main zCLI package exposing the `zCLI` core class."""

# Central imports for the entire zCLI system
import os
import sys
import platform
import socket
import shutil
import yaml
import subprocess
import importlib
import secrets
import logging
import requests
import asyncio
import json
import time
import re
import getpass
import uuid
from pathlib import Path

# Import utilities (safe to import early)
from .utils.styled_printer import print_ready
from .utils.colors import Colors

# Import the zCLI Core and Walker
from .zCLI import zCLI

# Export the main interfaces
__all__ = [
    # Core class
    "zCLI",
    
    # System modules
    "os", "sys", "platform", "socket", "shutil", "yaml", "subprocess", "importlib", "secrets", "logging", "requests", "asyncio", "json", "time", "re", "getpass", "uuid", "Path",
    
    # Utils
    "print_ready", "Colors",
]
