# zCLI/__init__.py

"""Main zCLI package exposing the `zCLI` core class."""

# Central imports for the entire zCLI system
# Standard library imports
import asyncio
import getpass
import importlib
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
import uuid
import webbrowser
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Third-party imports
import platformdirs  # pylint: disable=import-error
import requests  # pylint: disable=import-error
import yaml  # pylint: disable=import-error

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
    "uuid", "webbrowser", "yaml", "OrderedDict", "Path", "urlparse",

    # Utils
    "Colors",
]
