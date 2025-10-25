# zCLI/subsystems/zComm/zComm_modules/network_utils.py

"""Network utility functions for zComm."""
import socket

class NetworkUtils:
    """Network utility functions."""

    def __init__(self, logger):
        """Initialize network utilities.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger

    def check_port(self, port):
        """Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            bool: True if port is available, False if in use
        """
        self.logger.debug("Checking port availability: %d", port)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            is_available = result != 0  # True if available, False if in use

            if is_available:
                self.logger.debug("Port %d is available", port)
            else:
                self.logger.debug("Port %d is in use", port)

            return is_available

        except Exception as e:
            self.logger.error("Error checking port %d: %s", port, e)
            return False

