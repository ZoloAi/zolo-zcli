# zCLI/subsystems/zComm/__init__.py
"""
Communication & Service Management Subsystem for zCLI.

This package provides comprehensive communication capabilities including HTTP clients,
WebSocket servers (zBifrost), and local service management for zCLI applications.

Architecture:
    zComm is a Layer 0 subsystem (initialized before zDisplay) that provides the
    communication backbone for zCLI. It manages:
    
    - HTTP Communication: Synchronous HTTP requests via HTTPClient
    - WebSocket Server: Real-time bidirectional communication via zBifrost
    - Service Management: Local service lifecycle (PostgreSQL, Redis, MongoDB)
    - Network Utilities: Port checking, availability detection

Main Components:
    - zComm: Primary facade class providing unified interface to all communication
      features. Automatically initializes zBifrost in zBifrost mode.
    - ServiceManager: Manages local database/cache services
    - BifrostManager: Lifecycle management for zBifrost WebSocket server
    - HTTPClient: Synchronous HTTP requests
    - NetworkUtils: Network availability and port checking
    - zBifrost: Full-featured WebSocket bridge with authentication, caching, and
      event-driven architecture

Usage:
    ```python
    from zCLI.subsystems.zComm import zComm
    
    # Initialize zComm (done automatically by zCLI)
    comm = zComm(zcli_instance)
    
    # Access components
    comm.services.start("postgresql")
    comm.bifrost_start()  # Manual start if not auto-started
    response = comm.http_get("https://api.example.com")
    ```

Integration:
    - Depends on: zSession (via zcli.session), zLogger, zConfig
    - Used by: zDisplay, zData, zServer, user applications
    - Auto-starts: zBifrost (if session["zMode"] == "zBifrost")

Exports:
    - zComm: Main subsystem facade (recommended entry point)

See Also:
    - Documentation/zComm_GUIDE.md: Complete usage guide
    - zComm_modules/: Individual module implementations
"""

from .zComm import zComm

__all__ = ['zComm']
