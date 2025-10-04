import requests
from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay

def create_session():
    """
    Factory function to create a new session instance.
    
    This allows each zCLI instance to have its own isolated session,
    enabling multi-user support and parallel execution.
    
    Returns:
        dict: A new session dictionary with default values
    """
    return {
        "zS_id": None,
        "zWorkspace": None,
        "zVaFile_path": None,
        "zVaFilename": None,
        "zBlock": None,
        "zMode": None,
        "zAuth": {
            "id": None,
            "username": None,
            "role": None,
            "API_Key": None
        },
        "zCrumbs": {},
        "zCache": {},
    }

# Global session for backward compatibility
# Legacy code can still import and use this global zSession
zSession = create_session()

def View_zSession(session=None):
    """
    Display the current session information.
    
    Args:
        session: Session dict to display (optional, defaults to global zSession)
    """
    # Use provided session or fall back to global for backward compatibility
    target_session = session if session is not None else zSession
    
    handle_zDisplay({
        "event": "zSession",
        "zSession": target_session
    })

def zSession_Login(data, url=None, session=None):
    """
    Authenticate and update session with user credentials.
    
    Args:
        data: Authentication data (username, password, etc.)
        url: Authentication endpoint URL (optional)
        session: Session instance to update (optional, defaults to global zSession)
    
    Returns:
        dict: Authentication result or None on failure
    """
    # Use provided session or fall back to global for backward compatibility
    target_session = session if session is not None else zSession
    
    handle_zDisplay({
        "event": "header",
        "label": "send_to_server",
        "style": "~",
        "color": "EXTERNAL",
        "indent": 0
    })

    if not url:
        url = "http://127.0.0.1:5000/zAuth"
        logger.debug("[Web] No URL provided — defaulting to %s", url)

    # Include current session mode so server can distinguish CLI vs Web
    data.setdefault("mode", target_session.get("zMode"))

    logger.info("[>>] Sending request to %s", url)
    logger.debug("└── Payload: %s", data)

    try:
        response = requests.post(url, json=data, timeout=10)

        logger.info("[<<] Response received [status=%s]", response.status_code)
        logger.debug("└── Body: %s", response.text)

        result = response.json()

        if result.get("status") == "success" and "user" in result:
            user = result["user"]
            target_session["zAuth"].update({
                "username": user.get("username"),
                "role": user.get("role"),
                "id": user.get("id", None),
                "API_Key": user.get("api_key", None)
            })

            logger.info("[*] Authenticated user: %s (role=%s)", user.get("username"), user.get("role"))
            logger.debug(
                "└── Updated zSession['zAuth']: id=%s, API_Key=%s",
                user.get("id", None),
                user.get("api_key", None)
            )

            return result

        logger.warning("[FAIL] Login failed or missing user data in response: %s", result)
        return None

    except Exception as e:
        logger.error("[ERROR] Exception during request to %s: %s", url, e)
        return None
