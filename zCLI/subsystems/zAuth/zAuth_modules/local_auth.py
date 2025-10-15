"""
zAuth/zAuth_modules/local_auth.py
Local authentication (development/testing)
"""


def authenticate_local(username, password, logger=None):  # pylint: disable=unused-argument
    """
    Authenticate against local backend (disabled - no hardcoded users).
    
    Security: Hardcoded users have been removed.
    Authentication must go through proper backend systems.
    """
    if logger:
        logger.debug("Local authentication disabled - no hardcoded users available")
    return None

