# zCLI/subsystems/zComm/zComm_modules/zBifrost/__init__.py

"""
zBifrost WebSocket Bridge Module
Secure WebSocket server with event-driven architecture.
"""

# Use modular implementation (v1.5.4+)
from .bifrost_bridge_modular import zBifrost, broadcast, start_socket_server

__all__ = ['zBifrost', 'broadcast', 'start_socket_server']
