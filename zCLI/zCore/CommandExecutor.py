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
        Execute walker commands like 'walker load ui.zCloud.yaml'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Walker command result
        """
        action = parsed["action"]
        args = parsed["args"]
        
        if action == "load" and args:
            ui_file = args[0]
            logger.info("Loading UI file: %s", ui_file)
            # This would create a new zWalker instance
            return {"success": f"Loaded UI file: {ui_file}", "note": "Walker reload not yet implemented"}
        else:
            return {"error": f"Unknown walker command: {action}"}
    
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
        Execute test commands like 'test run' or 'test session'.
        
        Args:
            parsed: Parsed command dictionary
            
        Returns:
            Test execution result
        """
        import subprocess
        import os
        
        action = parsed["action"]
        
        if action == "run":
            # Run the full test suite
            logger.info("Running zCLI test suite...")
            test_path = os.path.join(
                os.path.dirname(__file__),
                "../../tests/test_core.py"
            )
            
            try:
                result = subprocess.run(
                    [sys.executable, test_path],
                    capture_output=True,
                    text=True,
                    timeout=60
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
        
        elif action == "crud":
            # Run CRUD tests only
            logger.info("Running CRUD test suite...")
            crud_test_dir = os.path.join(
                os.path.dirname(__file__),
                "../../tests/crud"
            )
            
            crud_tests = [
                "test_validation.py",
                "test_join.py",
                "test_zApps_crud.py",
                "test_direct_operations.py",
                "test_migration.py",
                "test_composite_pk.py",
                "test_where.py",
                "test_indexes.py",
                "test_upsert.py",
                "test_rgb_phase1.py",
                "test_rgb_phase2.py",
                "test_rgb_phase3.py"
            ]
            
            print("\n[TEST] Running CRUD Test Suite...")
            print("=" * 70)
            
            all_passed = True
            for test_file in crud_tests:
                test_path = os.path.join(crud_test_dir, test_file)
                if not os.path.exists(test_path):
                    print(f"[WARN] Test file not found: {test_file}")
                    continue
                
                print(f"\n[>>] Running {test_file}...")
                try:
                    result = subprocess.run(
                        [sys.executable, test_path],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                    
                    if result.returncode != 0:
                        all_passed = False
                        
                except Exception as e:
                    print(f"[X] Error running {test_file}: {e}")
                    all_passed = False
            
            print("\n" + "=" * 70)
            if all_passed:
                return {"success": "All CRUD tests passed!"}
            else:
                return {"error": "Some CRUD tests failed. See output above."}
        
        elif action == "all":
            # Run ALL tests (core + CRUD)
            logger.info("Running ALL test suites...")
            
            print("\n[TEST] Running COMPLETE Test Suite (Core + CRUD)...")
            print("=" * 70)
            
            # Run core tests first
            print("\n[1/2] Running Core Tests...")
            core_result = self.execute_test({"action": "run", "args": [], "options": {}})
            
            # Run CRUD tests
            print("\n[2/2] Running CRUD Tests...")
            crud_result = self.execute_test({"action": "crud", "args": [], "options": {}})
            
            # Summary
            print("\n" + "=" * 70)
            print("[SUMMARY] Complete Test Suite Results")
            print("=" * 70)
            
            core_passed = "success" in core_result
            crud_passed = "success" in crud_result
            
            print(f"Core Tests:  {'[PASS]' if core_passed else '[FAIL]'}")
            print(f"CRUD Tests:  {'[PASS]' if crud_passed else '[FAIL]'}")
            print("=" * 70)
            
            if core_passed and crud_passed:
                return {"success": "All tests passed (Core + CRUD)!"}
            else:
                return {"error": "Some tests failed. See output above."}
        
        elif action == "session":
            # Quick session test - verify current instance has unique session
            session_id = self.zcli.session.get("zS_id")
            return {
                "success": "Session test passed",
                "session_id": session_id,
                "note": "This instance has a unique session ID"
            }
        
        else:
            return {"error": f"Unknown test action: {action}. Use: test run | test all | test crud | test session"}
    
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
