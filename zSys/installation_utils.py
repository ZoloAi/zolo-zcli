# zSys/installation_utils.py
"""
Installation detection utilities (Layer 0 - System Foundation).

Provides portable installation type detection for zCLI without any
framework dependencies. Used by main.py bootstrap logger and info banner.
"""

from pathlib import Path
import os


def detect_installation_type(zcli_package, detailed: bool = False) -> str:
    """
    Detect zCLI installation type in a portable way.
    
    Args:
        zcli_package: The imported zCLI package (for __file__ access)
        detailed: If True, return detailed path info; if False, return simple type string
    
    Returns:
        str: Installation type ("editable", "standard", "uv", etc.)
    
    Examples:
        >>> import zCLI as zcli_package
        >>> detect_installation_type(zcli_package, detailed=False)
        'editable'
        >>> detect_installation_type(zcli_package, detailed=True)
        'editable (pip -e) at /Users/you/Projects/zolo-zcli/zCLI'
    
    Detection Logic:
        1. Not in site-packages → editable install (pip install -e .)
        2. VIRTUAL_ENV with 'uv' → uv environment
        3. VIRTUAL_ENV set → virtual environment
        4. Otherwise → standard (site-packages)
    
    Notes:
        - Portable across Windows, Mac, Linux
        - Based on Python packaging standards
        - No hardcoded paths or system assumptions
    """
    try:
        zcli_path = Path(zcli_package.__file__).resolve()
        
        # Check if in site-packages (standard install)
        is_site_packages = 'site-packages' in str(zcli_path)
        
        # Check for virtual environment
        venv_path = os.getenv('VIRTUAL_ENV')
        in_venv = venv_path is not None
        
        # Determine installation type
        if not is_site_packages:
            # Editable install (pip install -e .)
            if detailed:
                return f"editable (pip -e) at {zcli_path.parent}"
            return "editable"
        
        elif in_venv:
            # Check if uv environment
            if 'uv' in venv_path.lower():
                if detailed:
                    return f"uv environment at {venv_path}"
                return "uv"
            else:
                if detailed:
                    return f"venv at {venv_path}"
                return "venv"
        
        else:
            # Standard system-wide install
            if detailed:
                return f"standard (site-packages) at {zcli_path.parent}"
            return "standard"
            
    except Exception as e:
        if detailed:
            return f"unknown (detection failed: {e})"
        return "unknown"

