# zCLI/subsystems/zComm/zComm_modules/zBifrost/__init__.py

"""
zBifrost WebSocket Bridge Module
Secure WebSocket server with authentication and origin validation.
"""

from .bifrost_bridge import zBifrost, broadcast, start_socket_server

__all__ = ['zBifrost', 'broadcast', 'start_socket_server']
