# zCLI/subsystems/zComm/zComm_modules/http_client.py

"""HTTP client for zComm - pure communication layer."""
from zCLI import requests

class HTTPClient:
    """HTTP client for making web requests."""

    def __init__(self, logger):
        """Initialize HTTP client.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger

    def post(self, url, data=None, timeout=10):
        """Make HTTP POST request - pure communication, no auth logic.
        
        Args:
            url: Target URL
            data: Optional JSON data payload
            timeout: Request timeout in seconds (default: 10)
            
        Returns:
            Response object or None on failure
        """
        self.logger.debug("Making HTTP POST request to %s", url)
        self.logger.debug("Request payload: %s", data)

        try:
            response = requests.post(url, json=data, timeout=timeout)
            self.logger.debug("Response received [status=%s]", response.status_code)
            return response
        except Exception as e:
            self.logger.error("HTTP POST request failed to %s: %s", url, e)
            return None

