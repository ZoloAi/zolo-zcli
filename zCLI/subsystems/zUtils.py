# zCLI/subsystems/zUtils.py — Core Utility Functions for zCLI
# ───────────────────────────────────────────────────────────────
"""Core utility functions for zCLI package - only essential functionality."""

import uuid
import importlib
import importlib.util
import os
import platform
import subprocess
import sys


class ZUtils:
    """
    Core utilities for zCLI package.
    
    Contains only essential functionality:
    - generate_id: Generate unique identifiers
    - detect_machine_type: Detect system environment and capabilities
    - load_plugins: Load external plugin modules
    
    All other utilities (generate_API, hex_password, etc.) should be
    loaded as plugins from external modules like zCloud.
    """
    
    def __init__(self, walker=None):
        self.walker = walker
        self.plugins = {}

    def generate_id(self, prefix: str) -> str:
        """
        Generate a short hex-based ID with a given prefix.
        
        Args:
            prefix: Prefix for the ID (e.g., "zS", "zP")
            
        Returns:
            str: Generated ID in format "prefix_xxxxxxxx"
            
        Example:
            generate_id("zS") → "zS_a1b2c3d4"
        """
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def detect_machine_type(self) -> dict:
        """
        Detect system environment and machine capabilities.
        
        Returns:
            dict: Machine type information including:
                - platform: Operating system (Linux, Darwin, Windows)
                - environment: GUI/Headless detection
                - capabilities: Streamlined capability detection:
                    - default_IDE: GUI IDE (VS Code, Atom, Sublime) or vim
                    - default_text_editor: GUI editor (gedit, kate, notepad) or less
                    - imports: git AND (curl OR wget) for downloading/cloning
                    - browser: Web browser (requires GUI on Unix systems)
                - architecture: System architecture
                - python_version: Python version
                - zcli_version: zolo-zcli framework version
        """
        # Get zolo-zcli version
        try:
            from zCLI.version import get_version
            zcli_version = get_version()
        except ImportError:
            zcli_version = "unknown"
        
        machine_info = {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "zcli_version": zcli_version,
            "environment": "unknown",
            "capabilities": {
                "default_IDE": False,
                "default_text_editor": False,
                "imports": False,
                "browser": False
            }
        }
        
        # Detect environment (GUI vs Headless)
        gui_available = False
        if machine_info["platform"] == "Linux":
            # Check for DISPLAY environment variable (X11)
            if os.environ.get('DISPLAY'):
                machine_info["environment"] = "gui"
                gui_available = True
            else:
                machine_info["environment"] = "headless"
        elif machine_info["platform"] == "Darwin":  # macOS
            machine_info["environment"] = "gui"  # macOS typically has GUI
            gui_available = True
        elif machine_info["platform"] == "Windows":
            machine_info["environment"] = "gui"  # Windows typically has GUI
            gui_available = True
        
        # 1. Detect default_IDE (GUI IDE or vim)
        if gui_available:
            # Check for GUI IDEs
            gui_ide_found = False
            for ide in ['code', 'code-insiders', 'atom', 'sublime_text']:
                try:
                    subprocess.run([ide, '--version'], 
                                 capture_output=True, check=True, timeout=2)
                    gui_ide_found = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    pass
            
            if gui_ide_found:
                machine_info["capabilities"]["default_IDE"] = True
        
        # Check for vim (universal IDE)
        if not machine_info["capabilities"]["default_IDE"]:
            try:
                subprocess.run(['vim', '--version'], 
                             capture_output=True, check=True, timeout=2)
                machine_info["capabilities"]["default_IDE"] = True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                # Fallback to checking EDITOR environment variable
                editor = os.environ.get('EDITOR', '').lower()
                if editor and any(name in editor for name in ['vim', 'nano', 'emacs', 'code']):
                    machine_info["capabilities"]["default_IDE"] = True
        
        # 2. Detect default_text_editor (GUI editor or less)
        if gui_available:
            # Check for GUI text editors
            gui_editor_found = False
            for editor in ['gedit', 'kate', 'notepad', 'textedit']:
                try:
                    subprocess.run([editor, '--version'], 
                                 capture_output=True, check=True, timeout=2)
                    gui_editor_found = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    pass
            
            if gui_editor_found:
                machine_info["capabilities"]["default_text_editor"] = True
        
        # Check for less (universal text viewer/editor)
        if not machine_info["capabilities"]["default_text_editor"]:
            try:
                subprocess.run(['less', '--version'], 
                             capture_output=True, check=True, timeout=2)
                machine_info["capabilities"]["default_text_editor"] = True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        # 3. Detect imports capability (git AND curl OR wget)
        git_available = False
        download_available = False
        
        # Check for git
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, check=True, timeout=2)
            git_available = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Check for curl or wget
        for tool in ['curl', 'wget']:
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, check=True, timeout=2)
                download_available = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        if git_available and download_available:
            machine_info["capabilities"]["imports"] = True
        
        # 4. Detect browser (must have GUI on Unix systems)
        if gui_available:
            try:
                import webbrowser
                browser = webbrowser.get()
                if browser and hasattr(browser, 'name') and browser.name:
                    machine_info["capabilities"]["browser"] = True
            except Exception:
                pass
        
        return machine_info

    def load_plugins(self, plugin_paths):
        """
        Load plugin modules and expose their callables on this instance.
        
        This is the core plugin system for zCLI. External modules can be
        loaded to extend functionality (e.g., zCloud utilities).
        
        Args:
            plugin_paths: iterable of strings. Each can be either:
                - a Python import path (e.g., 'zCloud.Logic.zCloudUtils')
                - an absolute path to a .py file
        """
        if not plugin_paths:
            return
            
        for path in plugin_paths:
            try:
                mod = None
                if isinstance(path, str) and path.endswith('.py') and os.path.isabs(path):
                    # Load from file path
                    name = os.path.splitext(os.path.basename(path))[0]
                    spec = importlib.util.spec_from_file_location(name, path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                else:
                    # Load from import path
                    mod = importlib.import_module(path)

                if not mod:
                    continue

                self.plugins[path] = mod

                # Expose top-level callables as methods on this instance if not colliding
                for attr_name in dir(mod):
                    if attr_name.startswith('_'):
                        continue
                    func = getattr(mod, attr_name)
                    if callable(func) and not hasattr(self, attr_name):
                        setattr(self, attr_name, func)

            except Exception:  # best-effort: do not fail boot on plugin issues
                # keep silent to avoid noisy boot; callers can inspect self.plugins
                pass


# Backward-compatible function wrapper (for legacy code)
def generate_id(prefix):
    """Backward-compatible wrapper for generate_id."""
    return ZUtils().generate_id(prefix)
