import os
import importlib.util

from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay, handle_zInput
# Logger instance
logger = Logger.get_logger(__name__)


class ZFunc:
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "session", None)
        if not self.zSession:
            raise ValueError("ZFunc requires a walker with a session")
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle(self, zHorizontal, zContext=None):
        handle_zDisplay({
            "event": "sysmsg",
            "label": f"{zHorizontal}",
            "style": "single",
            "color": "ZFUNC",
            "indent": 0
        })

        logger.debug("handle_zFunc invoked:")
        logger.debug("zHorizontal: %s", zHorizontal)

        if zContext:
            for k, v in zContext.items():
                logger.debug("  %s: %s", k, v)
        else:
            logger.debug("zContext: None")

        try:
            if isinstance(zHorizontal, dict):
                func_path = zHorizontal["zFunc_path"]
                arg_str = zHorizontal["zFunc_args"]
                function_name = os.path.splitext(os.path.basename(func_path))[0]
            else:
                zHorizontal_raw = zHorizontal[len("zFunc("):-1].strip()
                logger.debug("zHorizontal_raw:\n%s", zHorizontal_raw)
                if zContext:
                    model = zContext.get("model")
                    logger.debug("model: %s", model)

                if "," in zHorizontal_raw:
                    path_part, arg_str = zHorizontal_raw.split(",", 1)
                    arg_str = arg_str.strip()
                else:
                    path_part = zHorizontal_raw
                    arg_str = None

                path_parts = path_part.split(".")
                function_name = path_parts[-1]
                file_name = path_parts[-2]
                zPath_unparsed = path_parts[:-2]
                logger.debug("file_name:\n%s", file_name)
                logger.debug("function_name:\n%s", function_name)
                logger.debug("zPath_unparsed:\n%s", zPath_unparsed)

                first = zPath_unparsed[0] if zPath_unparsed else ""
                symbol = first[0] if first.startswith("@") or first.startswith("~") else None
                if symbol:
                    zPath_unparsed[0] = first[1:]
                logger.debug("symbol: %s", symbol)
                if zContext:
                    logger.debug("zContext:\n%s", zContext)

                if symbol == "@":
                    zVaFile_basepath = os.path.join(self.zSession["zWorkspace"], *zPath_unparsed)
                    logger.debug("\nzVaFile path: %s", zVaFile_basepath)
                elif symbol == "~":
                    logger.debug("↪ '~' → absolute path")
                    zVaFile_basepath = os.path.join("/", *zPath_unparsed)
                else:
                    logger.debug("↪ no symbol → treat whole as relative")
                    zVaFile_basepath = os.path.join(*zPath_unparsed) if zPath_unparsed else ""

                func_path = os.path.join(zVaFile_basepath, f"{file_name}.py")
                logger.debug("func_path: %s", func_path)

                logger.debug("Parsed zFunc → func_path: %s, arg_str: %s, function_name: %s", func_path, arg_str, function_name)

            args = self.parse_args(arg_str, zContext)
            logger.debug("Prepared args for zFunc: %s", args)
            if zContext and isinstance(zContext, dict) and "model" in zContext:
                model = zContext["model"]
                if args and isinstance(args[0], dict):
                    args[0]["model"] = model
                else:
                    args.insert(0, {"model": model})
                logger.debug("Args after model merge: %s", args)

            func = self.resolve_callable(func_path, function_name)
            logger.debug("Resolved callable: %s.%s", func.__module__, func.__name__)

            # Auto-inject session parameter if function accepts it and walker has a session
            import inspect
            sig = inspect.signature(func)
            if 'session' in sig.parameters and self.walker and hasattr(self.walker, 'zSession'):
                # Check if session wasn't already provided in args
                # Simple heuristic: if we have args and first arg is a dict with 'session' key, don't inject
                inject_session = True
                if args and isinstance(args[0], dict) and 'session' in args[0]:
                    inject_session = False
                
                if inject_session:
                    logger.debug("Auto-injecting walker's session to function")
                    # Try to pass as keyword argument
                    try:
                        result = func(*args, session=self.walker.zSession)
                    except TypeError:
                        # If that fails, just call normally
                        result = func(*args)
                else:
                    result = func(*args)
            else:
                result = func(*args)

            logger.debug("zFunc '%s' executed with result: %s", func_path, result)
            handle_zDisplay({
                "event": "zJSON",
                "title": "Result",
                "payload": result,
                "color": "CYAN",
                "style": "~",
                "indent": 0,
            })
            handle_zDisplay({
                "event": "sysmsg",
                "label": "",
                "color": "CYAN",
                "style": "~",
                "indent": 0,
            })

            handle_zInput({
                "event": "break"
            })

            handle_zDisplay({
                "event": "sysmsg",
                "label": "zFunction Return",
                "style": "~",
                "color": "ZFUNC",
                "indent": 0
            })

            return result

        except Exception as e:
            logger.error("zFunc execution error: %s", e, exc_info=True)
            raise

    def parse_args(self, arg_str, zContext):
        handle_zDisplay({
            "event": "sysmsg",
            "label": "Parse Arguments",
            "style": "single",
            "color": "ZFUNC",
            "indent": 1
        })

        if not arg_str:
            logger.debug("No argument string provided to parse_args.")
            return []

        try:
            logger.debug("Raw arg string: %s", arg_str)
            args_raw = [arg.strip() for arg in self.split_args(arg_str)]
            logger.debug("🔍 Split args: %s", args_raw)

            parsed_args = []

            for arg in args_raw:
                if arg == "zContext":
                    parsed_args.append(zContext)
                    logger.debug("Injected full zContext into args.")
                elif isinstance(zContext, dict) and arg.startswith("this."):
                    key = arg.replace("this.", "")
                    value = zContext.get(key)
                    parsed_args.append(value)
                    logger.debug("Resolved 'this.%s' → %s", key, value)
                else:
                    evaluated = eval(arg, {}, {})
                    parsed_args.append(evaluated)
                    logger.debug("Evaluated literal '%s' → %s", arg, evaluated)

            logger.debug("Final parsed args: %s", parsed_args)
            return parsed_args

        except Exception as e:
            logger.error("Failed to parse zFunc args: %s", e)
            raise

    def split_args(self, arg_str):
        handle_zDisplay({
            "event": "sysmsg",
            "label": "Split Arguments",
            "style": "single",
            "color": "ZFUNC",
            "indent": 1
        })


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

    def resolve_callable(self, file_path, func_name):
        handle_zDisplay({
            "event": "sysmsg",
            "label": "Resolve Callable",
            "style": "single",
            "color": "ZFUNC",
            "indent": 1
        })

        try:
            logger.debug("File path: %s", file_path)
            logger.debug("Function name: %s", func_name)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No such file: {file_path}")

            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            func = getattr(module, func_name)
            logger.debug("Resolved callable: %s", func)
            return func

        except Exception as e:
            logger.error("Failed to resolve callable from '%s > %s': %s", file_path, func_name, e, exc_info=True)
            raise


def handle_zFunc(zHorizontal, zContext=None, walker=None):
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZFunc(walker).handle(zHorizontal, zContext)
