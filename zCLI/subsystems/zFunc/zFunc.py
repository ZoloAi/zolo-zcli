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
            self.logger.debug("Parsed => func_path: %s, arg_str: %s, function_name: %s", 
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

            # Step 4: Execute function with optional session/context injection
            result = self._execute_function(func, args, zContext)
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

    def _execute_function(self, func, args, zContext=None):
        """Execute function with optional session/zcli/context injection."""
        import asyncio
        
        sig = inspect.signature(func)
        kwargs = {}

        # Auto-inject zcli if function accepts it
        if 'zcli' in sig.parameters:
            self.logger.debug("Auto-injecting zcli instance to function")
            kwargs['zcli'] = self.zcli

        # Auto-inject session if function accepts it
        if 'session' in sig.parameters:
            inject_session = True
            if args and isinstance(args[0], dict) and 'session' in args[0]:
                inject_session = False

            if inject_session:
                self.logger.debug("Auto-injecting session to function")
                kwargs['session'] = self.session
        
        # Auto-inject context if function accepts it (for zWizard/zHat access)
        if 'context' in sig.parameters and zContext:
            self.logger.debug("Auto-injecting context to function")
            kwargs['context'] = zContext

        # Execute with injected kwargs
        if kwargs:
            try:
                result = func(*args, **kwargs)
            except TypeError as e:
                self.logger.warning("Failed to inject parameters: %s", e)
                result = func(*args)
        else:
            result = func(*args)
        
        # Handle async functions (coroutines)
        if asyncio.iscoroutine(result):
            self.logger.debug("Function returned coroutine - awaiting in event loop")
            try:
                # Check if event loop is already running (zBifrost mode)
                loop = asyncio.get_running_loop()
                self.logger.debug("Event loop is running - using run_coroutine_threadsafe")
                
                # Use run_coroutine_threadsafe to execute coroutine from sync context
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(result, loop)
                return future.result(timeout=300)  # 5 min timeout
                
            except RuntimeError:
                # No event loop running - use asyncio.run (Terminal mode)
                self.logger.debug("No running event loop - using asyncio.run()")
                return asyncio.run(result)
        
        return result

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
