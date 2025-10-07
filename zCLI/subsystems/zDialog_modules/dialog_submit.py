# zCLI/subsystems/zDialog_modules/dialog_submit.py
"""
Submission handling for zDialog - Processes onSubmit expressions
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay
from .dialog_context import inject_placeholders


def handle_submit(submit_expr, zContext, walker=None):
    """
    Handle the zDialog onSubmit expression.
    
    Supports:
    - Dict-based syntax (dispatched through zDispatch/zCRUD)
    - Legacy string-based expressions (evaluated via zFunc)
    
    Args:
        submit_expr: Submit expression (dict or string)
        zContext: Dialog context with model, fields, zConv
        walker: Optional walker instance
        
    Returns:
        Result of submission (varies by handler)
    """
    handle_zDisplay({
        "event": "sysmsg",
        "label": "zSubmit",
        "style": "single",
        "color": "ZDIALOG",
        "indent": 2
    })

    logger.debug("zSubmit_expr: %s", submit_expr)
    logger.debug("zContext keys: %s | zConv: %s", list(zContext.keys()), zContext.get("zConv"))

    # ── Dict-based submission → dispatch via zLauncher ──
    if isinstance(submit_expr, dict):
        return handle_dict_submit(submit_expr, zContext, walker)
    
    # ── Legacy string-based submission → via zFunc ──
    if isinstance(submit_expr, str):
        return handle_string_submit(submit_expr, zContext, walker)
    
    logger.error("zSubmit expression must be a string or dict, got: %s", type(submit_expr))
    return False


def handle_dict_submit(submit_dict, zContext, walker=None):
    """
    Handle dict-based onSubmit (new syntax).
    
    Example:
        onSubmit:
          zCRUD:
            action: create
            tables: [zUsers]
            fields: [username, email]
            values: zConv
    
    Args:
        submit_dict: Dict with zCRUD/zFunc/etc.
        zContext: Dialog context
        walker: Optional walker instance
        
    Returns:
        Result from zDispatch
    """
    logger.debug("zSubmit detected dict payload; preparing for zLaunch")

    # Inject placeholders (zConv → actual values)
    submit_dict = inject_placeholders(submit_dict, zContext)
    
    # Ensure model is passed to zCRUD
    if "zCRUD" in submit_dict and isinstance(submit_dict["zCRUD"], dict):
        if "model" not in submit_dict["zCRUD"]:
            submit_dict["zCRUD"]["model"] = zContext.get("model")
    elif "model" not in submit_dict:
        submit_dict["model"] = zContext.get("model")

    # Dispatch via zLauncher
    from zCLI.subsystems.zWalker.zWalker_modules.zDispatch import zLauncher
    logger.info("Dispatching dict onSubmit via zLauncher: %s", submit_dict)
    result = zLauncher(submit_dict, walker=walker)

    handle_zDisplay({
        "event": "sysmsg",
        "label": "zSubmit Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 3
    })

    handle_zDisplay({
        "event": "sysmsg",
        "label": "zDialog Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 2
    })

    return result


def handle_string_submit(submit_expr, zContext, walker=None):
    """
    Handle string-based onSubmit (legacy syntax).
    
    Example:
        onSubmit: "zFunc(create_user(zConv))"
    
    Args:
        submit_expr: String expression with zFunc
        zContext: Dialog context
        walker: Optional walker instance
        
    Returns:
        Result from zFunc
    """
    logger.debug("zSubmit detected string payload (legacy)")
    
    # Inject zConv placeholder
    if "zConv" in submit_expr:
        logger.debug("Detected 'zConv' in submit_expr — injecting...")
        try:
            injected_value = repr(zContext.get("zConv", {}))
            logger.debug("Injected zConv value: %s", injected_value)
            submit_expr = submit_expr.replace("zConv", injected_value)
        except Exception as e:
            logger.error("Failed to inject zConv: %s", e)
            return False

    # Execute via zFunc
    from zCLI.subsystems.zFunc import handle_zFunc
    logger.info("Final zSubmit to execute: %s", submit_expr)
    
    handle_zDisplay({
        "event": "sysmsg",
        "label": " → Handle zFunc",
        "style": "single",
        "color": "DISPATCH",
        "indent": 5
    })
    
    result = handle_zFunc(submit_expr, zContext=zContext, walker=walker)
    logger.debug("zSubmit result: %s", result)
    
    handle_zDisplay({
        "event": "sysmsg",
        "label": "zSubmit Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 3
    })

    handle_zDisplay({
        "event": "sysmsg",
        "label": "zDialog Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 2
    })

    return result
