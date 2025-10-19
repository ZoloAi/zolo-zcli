# zCLI/subsystems/zFunc/zFunc.py

"""External Python function loader and executor."""

from zCLI import inspect


class zFunc:
    """Function loading and execution subsystem."""

    def __init__(self, zcli):
        """Initialize zFunc with zCLI instance."""
        self.zcli = zcli
        self.logger = zcli.logger
        self.session = zcli.session
        self.display = zcli.display
        self.zparser = zcli.zparser
        self.mycolor = "ZFUNC"
        self.display.zDeclare("zFunc Ready", color=self.mycolor, indent=0, style="full")

    def handle(self, zHorizontal, zContext=None):
        """Execute external Python function with given spec and context."""
        self.display.zDeclare(f"{zHorizontal}", color=self.mycolor, indent=1, style="single")

        self.logger.debug("zFunc.handle() invoked:")
        self.logger.debug("zHorizontal: %s", zHorizontal)

        if zContext:
            for k, v in zContext.items():
                self.logger.debug("  %s: %s", k, v)
        else:
            self.logger.debug("zContext: None")

        try:
            # Step 1: Parse function path using zParser (reuses symbol resolution)
            func_path, arg_str, function_name = self.zparser.parse_function_path(
                zHorizontal, 
                zContext
            )
            self.logger.debug("Parsed → func_path: %s, arg_str: %s, function_name: %s", 
                            func_path, arg_str, function_name)

            # Step 2: Parse arguments
            args = self._parse_args_with_display(arg_str, zContext)
            self.logger.debug("Prepared args: %s", args)

            # Merge model if present in context
            if zContext and isinstance(zContext, dict) and "model" in zContext:
                model = zContext["model"]
                if args and isinstance(args[0], dict):
                    args[0]["model"] = model
                else:
                    args.insert(0, {"model": model})
                self.logger.debug("Args after model merge: %s", args)

            # Step 3: Resolve callable
            func = self._resolve_callable_with_display(func_path, function_name)
            self.logger.debug("Resolved: %s.%s", func.__module__, func.__name__)

            # Step 4: Execute function with optional session injection
            result = self._execute_function(func, args)
            self.logger.debug("Execution result: %s", result)

            # Step 5: Display result
            self._display_result(result)

            return result

        except Exception as e:
            self.logger.error("zFunc execution error: %s", e, exc_info=True)
            raise

    def _parse_args_with_display(self, arg_str, zContext):
        """Parse arguments with display header."""
        self.display.zDeclare("Parse Arguments", color=self.mycolor, indent=1, style="single")
        from .zFunc_modules.func_args import parse_arguments, split_arguments
        return parse_arguments(arg_str, zContext, split_arguments, self.logger, self.zparser)

    def _resolve_callable_with_display(self, func_path, function_name):
        """Resolve callable with display header."""
        self.display.zDeclare("Resolve Callable", color=self.mycolor, indent=1, style="single")
        from .zFunc_modules.func_resolver import resolve_callable
        return resolve_callable(func_path, function_name, self.logger)

    def _execute_function(self, func, args):
        """Execute function with optional session injection."""
        sig = inspect.signature(func)

        # Auto-inject session if function accepts it
        if 'session' in sig.parameters:
            inject_session = True
            if args and isinstance(args[0], dict) and 'session' in args[0]:
                inject_session = False

            if inject_session:
                self.logger.debug("Auto-injecting session to function")
                try:
                    return func(*args, session=self.session)
                except TypeError:
                    return func(*args)

        return func(*args)

    def _display_result(self, result):
        """Display function result with styling."""
        # Display result as JSON
        self.display.json_data(result, color=True, indent=0)

        # Separator
        self.display.zDeclare("", color="CYAN", indent=0, style="~")

        # Break for user to review (use text with newline)
        self.display.text("")

        # Return header
        self.display.zDeclare("zFunction Return", color=self.mycolor, indent=1, style="single")
