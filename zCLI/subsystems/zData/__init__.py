# zCLI/subsystems/zData/__init__.py
# ----------------------------------------------------------------
# zData subsystem - Unified data management across multiple backends.
# ----------------------------------------------------------------

from .zData import ZData, load_schema_ref
from .zData_modules.infrastructure import (
    zTables, zDataConnect, zEnsureTables, resolve_source, build_order_clause,
    handle_zData  # Legacy handle_zData with zCRUD_Preped signature
)
from .zData_modules.migration import (
    ZMigrate, auto_migrate_schema, detect_schema_changes
)

# Legacy ZCRUD compatibility
def handle_zCRUD(zRequest, walker=None):
    """
    Legacy handle_zCRUD function - delegates to handle_zData.
    Kept for backward compatibility with existing code.
    """
    from logger import logger
    from zCLI.subsystems.zLoader import handle_zLoader
    from zCLI.subsystems.zDisplay import handle_zDisplay
    
    handle_zDisplay({
        "event": "sysmsg",
        "style": "full",
        "label": "Preping zCRUD Request",
        "color": "ZCRUD",
        "indent": 1
    })

    if not isinstance(zRequest, dict):
        logger.warning("zCRUD input is not a dict: %s", type(zRequest))
        raise TypeError("zCRUD input must be a dict")

    # Allow wrapping the request under a top-level "zCRUD" key
    if "zCRUD" in zRequest and isinstance(zRequest["zCRUD"], dict):
        logger.debug("Unwrapping nested 'zCRUD' request")
        zRequest = zRequest["zCRUD"]

    model_path = zRequest.get("model")
    if not model_path:
        logger.error("zCRUD missing 'model' in request")
        return "error"

    # Load schema
    zForm = handle_zLoader(model_path)
    if zForm == "error":
        logger.error("Failed to load schema from model: %s", model_path)
        return "error"

    logger.info("zForm (parsed). %s", zForm)

    # Delegate to new zData infrastructure
    from .zData_modules.infrastructure import zDataConnect, zEnsureTables
    from .zData_modules.operations import (
        zCreate, zRead, zSearch, zUpdate, zDelete, zTruncate,
        zListTables, zUpsert, zAlterTable
    )
    
    zCRUD_Preped = {"zRequest": zRequest, "zForm": zForm, "walker": walker}
    
    # Call the old handle_zData logic
    meta = zForm.get("Meta", {})
    Data_Type = meta.get("Data_Type")
    Data_Path = meta.get("Data_path")

    zData = zDataConnect(Data_Type, Data_Path, zForm)
    
    if zData["ready"] and zData["conn"]:
        zData["cursor"] = zData["conn"].cursor()
    else:
        logger.error("zData not ready — cannot create cursor.")
        return "error"

    action = zRequest.get("action")
    results = None

    try:
        if action == "list_tables":
            results = zListTables(zForm, zData)
        elif zEnsureTables(zForm, zData, action, zRequest):
            if action == "create":
                results = zCreate(zRequest, zForm, zData, walker=walker)
            elif action in ["read"]:
                results = zRead(zRequest, zForm, zData, walker=walker)
            elif action == "search":
                results = zSearch(zRequest, zForm, zData)
            elif action == "update":
                results = zUpdate(zRequest, zForm, zData)
            elif action == "delete":
                results = zDelete(zRequest, zForm, zData)
            elif action == "upsert":
                results = zUpsert(zRequest, zForm, zData, walker=walker)
            elif action == "alter_table":
                results = zAlterTable(zRequest, zForm, zData, walker=walker)
            elif action == "truncate":
                results = zTruncate(zRequest, zForm, zData)
            else:
                results = None
        else:
            logger.error("Required tables missing for action '%s'", action)
            results = "error"
    finally:
        if zData.get("conn"):
            try:
                zData["conn"].close()
            except Exception as e:
                logger.error("Error closing database connection: %s", e)

    return results


__all__ = [
    "ZData", 
    "handle_zData", 
    "load_schema_ref", 
    "handle_zCRUD",
    "zTables",
    "zDataConnect",
    "zEnsureTables",
    "resolve_source",
    "build_order_clause",
    # Migration functions
    "ZMigrate",
    "auto_migrate_schema",
    "detect_schema_changes",
]