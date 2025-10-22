# zCLI/subsystems/zFunc/zFunc_modules/func_args.py

"""Function argument parsing utilities."""

def parse_arguments(arg_str, zContext, split_fn, logger_instance, zparser=None):
    """Parse function arguments from string."""
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
            elif arg == "zConv":
                # Handle zConv placeholder (from dialog context)
                zconv_value = zContext.get("zConv") if isinstance(zContext, dict) else None
                parsed_args.append(zconv_value)
                logger_instance.debug("Injected zConv from context: %s", zconv_value)
            elif isinstance(zContext, dict) and arg.startswith("zConv."):
                # Handle zConv.field notation
                field = arg.replace("zConv.", "")
                zconv_data = zContext.get("zConv", {})
                value = zconv_data.get(field) if isinstance(zconv_data, dict) else None
                parsed_args.append(value)
                logger_instance.debug("Resolved 'zConv.%s' => %s", field, value)
            elif isinstance(zContext, dict) and arg.startswith("this."):
                key = arg.replace("this.", "")
                value = zContext.get(key)
                parsed_args.append(value)
                logger_instance.debug("Resolved 'this.%s' => %s", key, value)
            else:
                # Use zParser for safe evaluation
                if zparser:
                    evaluated = zparser.parse_json_expr(arg)
                    logger_instance.debug("Evaluated via zParser '%s' => %s", arg, evaluated)
                else:
                    # No zParser available - treat as string literal
                    evaluated = arg
                    logger_instance.debug("No zParser - using literal '%s'", arg)
                parsed_args.append(evaluated)

        logger_instance.debug("Final parsed args: %s", parsed_args)
        return parsed_args

    except Exception as e:
        logger_instance.error("Failed to parse args: %s", e)
        raise


def split_arguments(arg_str):
    """Split argument string while respecting nested brackets."""
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
