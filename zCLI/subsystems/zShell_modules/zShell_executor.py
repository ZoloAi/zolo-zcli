# zCLI/subsystems/zShell_modules/zShell_executor.py — Command Execution Engine
# ───────────────────────────────────────────────────────────────

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

# Import modular command executors
from .executor_commands import (
    execute_crud, execute_func, execute_session, execute_walker,
    execute_open, execute_test, execute_auth, execute_load, 
    execute_export, execute_utils, execute_config
)


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
        self.logger = Logger.get_logger()
    
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
                return execute_crud(self.zcli, parsed)
            elif command_type == "func":
                return execute_func(self.zcli, parsed)
            elif command_type == "utils":
                return execute_utils(self.zcli, parsed)
            elif command_type == "session":
                return execute_session(self.zcli, parsed)
            elif command_type == "walker":
                return execute_walker(self.zcli, parsed)
            elif command_type == "open":
                return execute_open(self.zcli, parsed)
            elif command_type == "test":
                return execute_test(self.zcli, parsed)
            elif command_type == "load":
                return execute_load(self.zcli, parsed)
            elif command_type == "auth":
                return execute_auth(self.zcli, parsed)
            elif command_type == "export":
                return execute_export(self.zcli, parsed)
            elif command_type == "config":
                return execute_config(self.zcli, parsed)
            else:
                return {"error": f"Unknown command type: {command_type}"}
        
        except Exception as e:
            self.logger.error("Command execution failed: %s", e)
            return {"error": str(e)}
