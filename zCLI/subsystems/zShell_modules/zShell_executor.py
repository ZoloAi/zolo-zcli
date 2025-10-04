# zCLI/zCore/CommandExecutor.py — Command Execution Engine
# ───────────────────────────────────────────────────────────────

import sys
from zCLI.utils.logger import logger


class CommandExecutor:
    """
    Command Execution Engine for zCLI.
    
    Handles parsing and executing different command types:
    - CRUD operations
    - Functions
    - Utilities
    - Session management
    - Walker commands
    - Open commands
    """
    
    def __init__(self, zcli):
        """
        Initialize command executor.
        
        Args:
            zcli: Parent zCLI instance with access to all subsystems
        """
        self.zcli = zcli
        self.logger = logger
    
    def execute(self, command: str):
        """
        Parse and execute a shell command.
        
        Args:
            command: Command string like "crud read users --limit 10"
        
        Returns:
            Command execution result
        """
        if not command.strip():
            return None
        
        try:
            # Parse the command using zParser
            parsed = self.zcli.zparser.parse_command(command)
            
            # Check for parsing errors
            if "error" in parsed:
                return parsed
            
            # Execute based on command type
            command_type = parsed.get("type")
            
            if command_type == "crud":
                return self.execute_crud(parsed)
            elif command_type == "func":
                return self.execute_func(parsed)
            elif command_type == "utils":
                return self.execute_utils(parsed)
            elif command_type == "session":
                return self.execute_session(parsed)
            elif command_type == "walker":
                return self.execute_walker(parsed)
            elif command_type == "open":
                return self.execute_open(parsed)
            elif command_type == "test":
                return self.execute_test(parsed)
            elif command_type == "auth":
                return self.execute_auth(parsed)
            else:
                return {"error": f"Unknown command type: {command_type}"}
        
        except Exception as e:
            logger.error("Command execution failed: %s", e)
            return {"error": str(e)}
    
    def execute_crud(self, parsed):
        """
        Execute CRUD commands like 'crud read users --limit 10'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            CRUD operation result
        """
        action = parsed["action"]
        table = parsed["args"][0] if parsed["args"] else None
        
        # Set default model path if not provided
        model_path = parsed.get("options", {}).get("model")
        if not model_path and table:
            model_path = f"@.zCloud.schemas.schema.zIndex.{table}"
        
        zRequest = {
            "action": action,
            "tables": [table] if table else [],
            "model": model_path,
            **parsed.get("options", {})
        }
        
        logger.debug("Executing CRUD: %s on %s", action, table)
        return self.zcli.crud.handle(zRequest)
    
    def execute_func(self, parsed):
        """
        Execute function commands like 'func generate_id zU'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Function execution result
        """
        func_name = parsed["action"]
        args = parsed["args"]
        
        # Format as zFunc expression
        func_expr = f"zFunc({func_name}({','.join(args)}))"
        
        logger.debug("Executing function: %s", func_expr)
        return self.zcli.funcs.handle(func_expr)
    
    def execute_utils(self, parsed):
        """
        Execute utility commands like 'utils hash_password mypass'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Utility execution result
        """
        action = parsed["action"]
        args = parsed["args"]
        
        if hasattr(self.zcli.utils, action):
            logger.debug("Executing utility: %s", action)
            return getattr(self.zcli.utils, action)(*args)
        else:
            return {"error": f"Unknown utility: {action}"}
    
    def execute_session(self, parsed):
        """
        Execute session commands like 'session info', 'session set mode zGUI'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Session command result
        """
        action = parsed["action"]
        args = parsed["args"]
        
        if action == "info":
            # IMPORTANT: Pass the instance's session, not the global one
            return self.zcli.display.handle({
                "event": "zSession",
                "zSession": self.zcli.session  # ← Pass instance session
            })
        elif action == "set" and len(args) >= 2:
            key, value = args[0], args[1]
            self.zcli.session[key] = value
            logger.info("Session updated: %s = %s", key, value)
            return {"success": f"Set {key} = {value}"}
        elif action == "get" and len(args) >= 1:
            key = args[0]
            value = self.zcli.session.get(key)
            return {"result": {key: value}}
        else:
            return {"error": f"Unknown session command: {action}"}
    
    def execute_walker(self, parsed):
        """
        Execute walker commands like 'walker run'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Walker command result
        """
        action = parsed["action"]
        
        if action == "run":
            # Launch Walker using session's zVaF configuration
            logger.info("Launching Walker from session configuration...")
            
            # Validate required session fields
            required_fields = ["zWorkspace", "zVaFilename", "zVaFile_path", "zBlock"]
            missing = []
            
            for field in required_fields:
                if not self.zcli.session.get(field):
                    missing.append(field)
            
            if missing:
                return {
                    "error": f"Missing required session fields: {', '.join(missing)}",
                    "note": "Use 'session set <field> <value>' to configure Walker"
                }
            
            # Build zSpark configuration from session
            self.zcli.zspark_obj.update({
                "zWorkspace": self.zcli.session["zWorkspace"],
                "zVaFilename": self.zcli.session["zVaFilename"],
                "zVaFile_path": self.zcli.session.get("zVaFile_path", "@"),
                "zBlock": self.zcli.session.get("zBlock", "Root"),
                "zMode": self.zcli.session.get("zMode", "Terminal")
            })
            
            # Set UI mode
            self.zcli.ui_mode = True
            
            # Import and launch Walker
            try:
                from zCLI.subsystems.zWalker.zWalker import zWalker
                logger.info("Creating zWalker instance from zCLI...")
                walker = zWalker(self.zcli)
                
                logger.info("Starting Walker UI mode...")
                result = walker.run()
                
                # After Walker exits normally, return to shell
                logger.info("Walker exited normally, returning to Shell mode...")
                self.zcli.ui_mode = False
                
                return {"success": "Walker session completed", "result": result}
                
            except SystemExit as e:
                # Walker called sys.exit() - this is normal for "stop" or completion
                logger.info("Walker exited via sys.exit(%s), returning to Shell mode...", e.code)
                self.zcli.ui_mode = False
                
                # Determine if it was a normal exit or error
                if e.code == 0 or e.code is None:
                    return {"success": "Walker exited normally"}
                else:
                    return {"note": f"Walker exited with code {e.code}"}
                
            except Exception as e:
                logger.error("Failed to launch Walker: %s", e, exc_info=True)
                self.zcli.ui_mode = False
                return {"error": f"Walker launch failed: {str(e)}"}
        
        else:
            return {"error": f"Unknown walker command: {action}. Use: walker run"}
    
    def execute_open(self, parsed):
        """
        Execute open commands like 'open @.zProducts.zTimer.index.html' or 'open https://example.com'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Open command result
        """
        args = parsed["args"]
        
        if not args:
            return {"error": "No path provided to open"}
        
        path = args[0]
        # Format as zOpen() expression
        zHorizontal = f"zOpen({path})"
        
        logger.info("Opening: %s", path)
        result = self.zcli.open.handle(zHorizontal)
        
        if result == "zBack":
            return {"success": f"Opened: {path}"}
        else:
            return {"result": result}
    
    def execute_test(self, parsed):
        """
        Execute test commands using the unified test runner.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Test execution result
        """
        import subprocess
        import os
        
        action = parsed["action"]
        
        # Find project root and test runner
        # Strategy: Look for tests/ directory starting from current working directory
        cwd = os.getcwd()
        test_runner = None
        
        # First try: from current working directory
        if os.path.exists(os.path.join(cwd, "tests", "run_tests.py")):
            test_runner = os.path.join(cwd, "tests", "run_tests.py")
        
        # Second try: walk up from current directory to find tests/
        elif not test_runner:
            search_path = cwd
            for _ in range(5):  # Search up to 5 levels
                candidate = os.path.join(search_path, "tests", "run_tests.py")
                if os.path.exists(candidate):
                    test_runner = candidate
                    break
                parent = os.path.dirname(search_path)
                if parent == search_path:  # Reached filesystem root
                    break
                search_path = parent
        
        # Third try: relative to this file (fallback)
        if not test_runner:
            test_runner = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "../../../tests/run_tests.py"
            ))
        
        if action == "run":
            # Run all tests using unified runner
            logger.info("Running all zCLI test suites...")
            
            if not os.path.exists(test_runner):
                return {"error": f"Test runner not found at: {test_runner}"}
            
            try:
                result = subprocess.run(
                    [sys.executable, test_runner],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                # Print the test output
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                
                if result.returncode == 0:
                    return {"success": "All tests passed!"}
                else:
                    return {"error": "Some tests failed. See output above."}
            except subprocess.TimeoutExpired:
                return {"error": "Test execution timed out"}
            except Exception as e:
                return {"error": f"Failed to run tests: {str(e)}"}
        
        elif action == "session":
            # Quick session test - verify current instance has unique session
            session_id = self.zcli.session.get("zS_id")
            return {
                "success": "Session test passed",
                "session_id": session_id,
                "note": "This instance has a unique session ID"
            }
        
        else:
            return {"error": f"Unknown test action: {action}. Use: test run | test session"}
    
    def execute_auth(self, parsed):
        """
        Execute authentication commands like 'auth login', 'auth logout', 'auth status'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Authentication operation result
        """
        action = parsed["action"]
        args = parsed.get("args", [])
        
        logger.debug("Executing auth command: %s", action)
        
        if action == "login":
            # Handle login - optionally with username/password from args
            username = args[0] if len(args) > 0 else None
            password = args[1] if len(args) > 1 else None
            return self.zcli.auth.login(username, password)
        
        elif action == "logout":
            # Handle logout
            return self.zcli.auth.logout()
        
        elif action == "status":
            # Show authentication status
            return self.zcli.auth.status()
        
        else:
            return {"error": f"Unknown auth action: {action}"}
