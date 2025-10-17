# zCLI/subsystems/zParser/zParser_modules/zParser_zFunc.py

"""Function path parsing for zFunc subsystem."""

from zCLI import os
from .zParser_zPath import _resolve_symbol_path

def parse_function_spec(zFunc_spec, session, logger, zContext=None):
    """Parse zFunc specification into (func_path, arg_str, function_name) tuple."""
    # Handle dict format
    if isinstance(zFunc_spec, dict):
        func_path = zFunc_spec["zFunc_path"]
        arg_str = zFunc_spec.get("zFunc_args")
        function_name = os.path.splitext(os.path.basename(func_path))[0]
        return func_path, arg_str, function_name

    # Handle string format: "zFunc(path.to.file.function_name, args)"
    zFunc_raw = zFunc_spec[len("zFunc("):-1].strip()
    
    logger.debug("Parsing zFunc spec: %s", zFunc_raw)
    if zContext:
        logger.debug("Context model: %s", zContext.get("model"))

    # Split path and arguments
    if "," in zFunc_raw:
        path_part, arg_str = zFunc_raw.split(",", 1)
        arg_str = arg_str.strip()
    else:
        path_part = zFunc_raw
        arg_str = None

    # Parse path components: @utils.myfile.my_function
    path_parts = path_part.split(".")
    function_name = path_parts[-1]  # "my_function"
    file_name = path_parts[-2]      # "myfile"
    path_prefix = path_parts[:-2]   # ["@utils"] or ["utils"]
    
    logger.debug("file_name: %s", file_name)
    logger.debug("function_name: %s", function_name)
    logger.debug("path_prefix: %s", path_prefix)

    # Extract symbol from first part
    first_part = path_prefix[0] if path_prefix else ""
    symbol = None
    
    if first_part and (first_part.startswith("@") or first_part.startswith("~")):
        symbol = first_part[0]
        # Remove symbol from first part
        path_prefix[0] = first_part[1:]
    
    logger.debug("symbol: %s", symbol)

    # Reuse zParser's symbol resolution logic
    zWorkspace = session.get("zWorkspace", os.getcwd())
    
    # Build path_parts list for _resolve_symbol_path
    if symbol:
        symbol_parts = [symbol] + path_prefix
    else:
        symbol_parts = path_prefix
    
    base_path = _resolve_symbol_path(symbol, symbol_parts, zWorkspace, session, logger)
    func_path = os.path.join(base_path, f"{file_name}.py")
    
    logger.debug("Resolved func_path: %s", func_path)

    return func_path, arg_str, function_name

