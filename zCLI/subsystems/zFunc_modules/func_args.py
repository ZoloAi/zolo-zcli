# zCLI/subsystems/zFunc_modules/func_args.py
"""Function argument parsing utilities."""

from logger import Logger

logger = Logger.get_logger(__name__)


def parse_arguments(arg_str, zContext, split_fn, logger_instance, zparser=None):
    """
    Parse function arguments from string.
    
    Args:
        arg_str: Argument string to parse
        zContext: Context for variable resolution
        split_fn: Function to split arguments
        logger_instance: Logger instance
        zparser: Optional zParser instance for safer evaluation
        
    Returns:
        list: Parsed arguments
    """
    if not arg_str:
        logger_instance.debug("No arguments to parse")
        return []

    try:
        logger_instance.debug("Raw arg string: %s", arg_str)
        args_raw = [arg.strip() for arg in split_fn(arg_str)]
        logger_instance.debug("Split args: %s", args_raw)

        parsed_args = []

        for arg in args_raw:
            if arg == "zContext":
                parsed_args.append(zContext)
                logger_instance.debug("Injected full zContext")
            elif isinstance(zContext, dict) and arg.startswith("this."):
                key = arg.replace("this.", "")
                value = zContext.get(key)
                parsed_args.append(value)
                logger_instance.debug("Resolved 'this.%s' → %s", key, value)
            else:
                # Use zParser for safer evaluation if available
                if zparser:
                    try:
                        evaluated = zparser.parse_json_expr(arg)
                        logger_instance.debug("Evaluated via zParser '%s' → %s", arg, evaluated)
                    except Exception:
                        # Fallback to eval for non-JSON expressions
                        evaluated = eval(arg, {}, {})
                        logger_instance.debug("Evaluated via eval '%s' → %s", arg, evaluated)
                else:
                    evaluated = eval(arg, {}, {})
                    logger_instance.debug("Evaluated literal '%s' → %s", arg, evaluated)
                parsed_args.append(evaluated)

        logger_instance.debug("Final parsed args: %s", parsed_args)
        return parsed_args

    except Exception as e:
        logger_instance.error("Failed to parse args: %s", e)
        raise


def split_arguments(arg_str):
    """
    Split argument string while respecting nested brackets.
    
    Args:
        arg_str: Argument string to split
        
    Returns:
        list: Split arguments
    """
    args = []
    buf = ''
    depth = 0

    for char in arg_str:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        
        if char == ',' and depth == 0:
            args.append(buf)
            buf = ''
        else:
            buf += char

    if buf:
        args.append(buf)

    return args

