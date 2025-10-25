# zCLI/utils/validation.py

"""Validation utilities for zCLI subsystems."""


def validate_zcli_instance(zcli, subsystem_name, require_session=True):
    """Validate that a zCLI instance is properly initialized for subsystem use.
    
    This validation ensures subsystems receive a valid zCLI instance and helps
    catch initialization order issues early.
    
    Args:
        zcli: The zCLI instance to validate (should never be None)
        subsystem_name: Name of the subsystem for error messages (e.g., "zComm", "zConfig")
        require_session: Whether to require session attribute (default: True)
                        Set to False only for zConfig which creates the session
        
    Raises:
        ValueError: If zcli is None (initialization order issue) or missing required attributes
        
    Note:
        If zcli is None, it indicates a serious initialization order problem.
        Subsystems should always receive a valid zCLI instance.
        
        require_session=False should ONLY be used by zConfig since it's Layer 0
        and is responsible for creating the session. All other subsystems require session.
    """
    if zcli is None:
        raise ValueError(
            f"{subsystem_name} received None for zCLI instance. "
            f"This indicates an initialization order issue - subsystems must be "
            f"initialized with a valid zCLI instance."
        )
    
    if require_session and not hasattr(zcli, 'session'):
        raise ValueError(
            f"{subsystem_name} requires zCLI instance with 'session' attribute. "
            f"Ensure zCLI is fully initialized before creating {subsystem_name}."
        )

