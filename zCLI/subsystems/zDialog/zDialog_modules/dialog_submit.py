# zCLI/subsystems/zDialog/zDialog_modules/dialog_submit.py

"""Submission handling for zDialog - Processes onSubmit expressions."""

from .dialog_context import inject_placeholders


def handle_submit(submit_expr, zContext, logger, walker=None):
    """Handle the zDialog onSubmit expression (dict or string) and return submission result."""
    if walker is None:
        raise ValueError("handle_submit requires a walker instance")
    
    walker.display.handle({
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
        return handle_dict_submit(submit_expr, zContext, logger, walker)
    
    # ── Legacy string-based submission → via zFunc ──
    if isinstance(submit_expr, str):
        return handle_string_submit(submit_expr, zContext, logger, walker)
    
    logger.error("zSubmit expression must be a string or dict, got: %s", type(submit_expr))
    return False


def handle_dict_submit(submit_dict, zContext, logger, walker=None):
    """Handle dict-based onSubmit expression and dispatch via zLauncher."""
    logger.debug("zSubmit detected dict payload; preparing for zLaunch")

    # Inject placeholders (zConv → actual values)
    submit_dict = inject_placeholders(submit_dict, zContext, logger)
    
    # Ensure model is passed to zCRUD
    if "zCRUD" in submit_dict and isinstance(submit_dict["zCRUD"], dict):
        if "model" not in submit_dict["zCRUD"]:
            submit_dict["zCRUD"]["model"] = zContext.get("model")
    elif "model" not in submit_dict:
        submit_dict["model"] = zContext.get("model")

    # Dispatch via core zDispatch
    from zCLI.subsystems.zDispatch import handle_zDispatch
    logger.info("Dispatching dict onSubmit via zDispatch: %s", submit_dict)
    result = handle_zDispatch("submit", submit_dict, zcli=walker.zcli, walker=walker)

    walker.display.handle({
        "event": "sysmsg",
        "label": "zSubmit Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 3
    })

    walker.display.handle({
        "event": "sysmsg",
        "label": "zDialog Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 2
    })

    return result


def handle_string_submit(submit_expr, zContext, logger, walker=None):
    """Handle legacy string-based onSubmit via zFunc."""
    logger.debug("zSubmit detected string payload (legacy)")
    logger.info("Executing zFunc expression: %s", submit_expr)
    
    walker.display.handle({
        "event": "sysmsg",
        "label": " → Handle zFunc",
        "style": "single",
        "color": "DISPATCH",
        "indent": 5
    })
    
    # Let zFunc handle all placeholder resolution (zConv, zConv.field, etc.)
    # zFunc's parse_arguments now natively supports these placeholders
    result = walker.zcli.zfunc.handle(submit_expr, zContext)
    logger.debug("zSubmit result: %s", result)
    
    walker.display.handle({
        "event": "sysmsg",
        "label": "zSubmit Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 3
    })

    walker.display.handle({
        "event": "sysmsg",
        "label": "zDialog Return",
        "style": "~",
        "color": "ZDIALOG",
        "indent": 2
    })

    return result
