# zCLI/subsystems/zComm/zComm_modules/comm_http.py
"""
HTTP client for zComm subsystem.

Provides a simple HTTP POST client for making web requests. This is a pure
communication layer with no authentication logic - auth should be handled by
the caller (e.g., zAuth subsystem).

Note: Currently only implements POST method as that's the primary use case
for zComm. Additional HTTP methods (GET, PUT, DELETE, PATCH) can be added
as needed.
"""

from zCLI import Any, Dict, Optional, requests

# ═══════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[HTTPClient]"

# Network Configuration
DEFAULT_TIMEOUT = 10  # seconds

# Log Messages
LOG_POST_REQUEST = "Making HTTP POST request to {url}"
LOG_REQUEST_PAYLOAD = "Request payload: {data}"
LOG_RESPONSE_RECEIVED = "Response received [status={status}]"

# Error Messages
ERROR_REQUEST_FAILED = "HTTP POST request failed to {url}: {error}"
ERROR_INVALID_URL = "Invalid URL provided: {url}"
ERROR_INVALID_TIMEOUT = "Timeout must be positive, got: {timeout}"


class HTTPClient:
    """
    HTTP client for making web requests (POST method).
    
    This is a pure communication layer with no authentication logic.
    Authentication should be handled by the caller (e.g., zAuth subsystem).
    
    Example:
        >>> client = HTTPClient(logger)
        >>> response = client.post("https://api.example.com/endpoint", 
        ...                        data={"key": "value"}, 
        ...                        timeout=5)
        >>> if response:
        ...     print(f"Status: {response.status_code}")
    """

    def __init__(self, logger: Any) -> None:
        """
        Initialize HTTP client.
        
        Args:
            logger: Logger instance for debug/error output
        """
        self.logger = logger

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             timeout: int = DEFAULT_TIMEOUT) -> Optional[Any]:
        """
        Make HTTP POST request - pure communication, no auth logic.
        
        Args:
            url: Target URL (must start with http:// or https://)
            data: Optional JSON data payload (dict will be serialized to JSON)
            timeout: Request timeout in seconds (must be positive, default: 10)
            
        Returns:
            Response object on success, None on failure
            
        Raises:
            ValueError: If url is empty/invalid or timeout is not positive
            
        Example:
            >>> response = client.post(
            ...     "https://api.example.com/data",
            ...     data={"user_id": 123, "action": "update"},
            ...     timeout=5
            ... )
            >>> if response and response.status_code == 200:
            ...     result = response.json()
        """
        # Validate URL
        if not url or not isinstance(url, str):
            error_msg = ERROR_INVALID_URL.format(url=url)
            self.logger.error(f"{LOG_PREFIX} {error_msg}")
            raise ValueError(error_msg)

        if not url.startswith(("http://", "https://")):
            error_msg = ERROR_INVALID_URL.format(url=url)
            self.logger.error(f"{LOG_PREFIX} {error_msg}")
            raise ValueError(error_msg)

        # Validate timeout
        if not isinstance(timeout, int) or timeout <= 0:
            error_msg = ERROR_INVALID_TIMEOUT.format(timeout=timeout)
            self.logger.error(f"{LOG_PREFIX} {error_msg}")
            raise ValueError(error_msg)

        # Log request
        self.logger.debug(f"{LOG_PREFIX} {LOG_POST_REQUEST.format(url=url)}")
        if data:
            self.logger.debug(f"{LOG_PREFIX} {LOG_REQUEST_PAYLOAD.format(data=data)}")

        try:
            response = requests.post(url, json=data, timeout=timeout)
            self.logger.debug(
                f"{LOG_PREFIX} {LOG_RESPONSE_RECEIVED.format(status=response.status_code)}"
            )
            return response

        except requests.Timeout:
            # Specific timeout error
            error_msg = ERROR_REQUEST_FAILED.format(url=url, error=f"Timeout after {timeout}s")
            self.logger.error(f"{LOG_PREFIX} {error_msg}")
            return None

        except requests.RequestException as e:
            # Other request-related errors (connection, DNS, etc.)
            error_msg = ERROR_REQUEST_FAILED.format(url=url, error=str(e))
            self.logger.error(f"{LOG_PREFIX} {error_msg}")
            return None
