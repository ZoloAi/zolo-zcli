# zCLI/subsystems/zUtils_modules/utils_machine.py
# ───────────────────────────────────────────────────────────────
"""Machine detection utilities for zCLI."""

import platform
import socket
import sys
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def detect_machine_type() -> dict:
    """
    Get machine information from zConfig.
    
    This method now returns machine config from machine.yaml
    instead of re-detecting on every call.
    
    Returns:
        dict: Machine information from machine.yaml
    """
    try:
        # Get machine config from zConfig
        from zCLI.subsystems.zConfig import get_config
        config = get_config()
        machine = config.get_machine()
        
        # Add zcli version
        try:
            from zCLI.version import get_version
            machine['zcli_version'] = get_version()
        except ImportError:
            machine['zcli_version'] = "unknown"
        
        return machine
    
    except Exception as e:
        # Fallback if zConfig not available
        logger.warning("[zUtils] zConfig not available, using minimal fallback: %s", e)
        
        try:
            from zCLI.version import get_version
            zcli_version = get_version()
        except ImportError:
            zcli_version = "unknown"
        
        return {
            "os": platform.system(),
            "hostname": socket.gethostname(),
            "architecture": platform.machine(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "zcli_version": zcli_version,
            "deployment": "dev",
            "text_editor": "nano",
            "browser": "unknown",
        }
