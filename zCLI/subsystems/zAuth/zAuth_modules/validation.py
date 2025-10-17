# zCLI/subsystems/zAuth/zAuth_modules/validation.py

"""
zAuth/zAuth_modules/validation.py
API key validation
"""


def validate_api_key(zcli, api_key, server_url=None):  # pylint: disable=unused-argument
    """
    Validate API key against server using zData.
    
    Args:
        zcli: zCLI instance
        api_key: API key to validate
        server_url: Server URL (unused - for future use)
    
    Returns:
        dict: Validation result with 'valid' and optional 'user'
    """
    logger = zcli.logger
    
    if not zcli:
        logger.error("Cannot validate API key: No zCLI instance available")
        return {"valid": False, "reason": "No zCLI instance"}
    
    try:
        # Validate via zData subsystem
        result = zcli.data.handle_request({
            "action": "read",
            "model": "@.zCloud.schemas.schema.zIndex.zUsers",
            "fields": ["id", "username", "role"],
            "filters": {"api_key": api_key},
            "limit": 1
        })
        
        if result and len(result) > 0:
            user = result[0]
            logger.info("[OK] API key validated for: %s", user.get("username"))
            return {"valid": True, "user": user}
        else:
            logger.warning("[FAIL] Invalid API key")
            return {"valid": False, "reason": "Invalid API key"}
    
    except Exception as e:
        logger.error("Error validating API key: %s", e)
        return {"valid": False, "reason": str(e)}

