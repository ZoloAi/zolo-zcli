# zCLI/subsystems/zComm/zComm_modules/__init__.py
"""
Communication Module Implementations for zComm Subsystem.

This package contains the core implementation modules for zCLI's communication
infrastructure. Each module is focused on a specific communication domain and
follows the zCLI architectural patterns for consistency and maintainability.

Module Organization:
    - Core Modules: HTTP, Services, Bifrost (in zComm_modules/)
    - Bifrost Implementation: WebSocket bridge (in bifrost/)
    - Service Implementations: Database services (in services/)
    - Helper Utilities: Network utilities (in helpers/)

Exported Components:
    ServiceManager: Local service lifecycle management (PostgreSQL, Redis, MongoDB)
        - Start/stop/status operations for local database services
        - Cross-platform support (macOS, Linux, Windows)
        - Integration with system package managers (Homebrew, apt, etc.)
    
    BifrostManager: zBifrost WebSocket server lifecycle facade
        - Auto-start in zBifrost mode (from session["zMode"])
        - Manual start/stop/status control
        - Connection to main zBifrost bridge implementation
    
    HTTPClient: Synchronous HTTP request handler
        - GET/POST/PUT/DELETE operations
        - Session-aware headers
        - Error handling and logging
    
    NetworkUtils: Network availability and port checking utilities
        - Port availability detection
        - Service readiness validation
        - Cross-platform network checks
    
    zBifrost: Full WebSocket bridge implementation
        - Real-time bidirectional communication
        - Three-tier authentication (zSession, application, dual)
        - Schema caching and query optimization
        - Event-driven architecture with modular handlers

Architecture Patterns:
    - Dependency Injection: All components accept logger/zcli in __init__
    - Delegation: Managers delegate to implementation classes
    - Encapsulation: Internal implementation in submodules
    - Layer 0 Design: No zDisplay dependency (uses print_ready_message)

Usage:
    ```python
    from zCLI.subsystems.zComm.zComm_modules import (
        ServiceManager,
        BifrostManager,
        HTTPClient,
        NetworkUtils,
        zBifrost
    )
    
    # Typically accessed via zComm facade
    services = ServiceManager(logger)
    services.start("postgresql")
    
    # Direct access to Bifrost (advanced usage)
    bridge = zBifrost(zcli, walker)
    ```

See Also:
    - comm_services.py: ServiceManager implementation
    - comm_bifrost.py: BifrostManager implementation
    - comm_http.py: HTTPClient implementation
    - helpers/network_utils.py: NetworkUtils implementation
    - bifrost/: Full zBifrost WebSocket bridge
"""

from .comm_services import ServiceManager
from .comm_bifrost import BifrostManager
from .comm_http import HTTPClient
from .helpers.network_utils import NetworkUtils
from .bifrost import zBifrost

__all__ = ['ServiceManager', 'BifrostManager', 'HTTPClient', 'NetworkUtils', 'zBifrost']
