# zCLI/subsystems/zShell_modules/zShell_executor.py — Command Execution Engine
# ───────────────────────────────────────────────────────────────

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

# Import modular command executors
from .executor_commands import (
    execute_data, execute_func, execute_session, execute_walker,
    execute_open, execute_test, execute_auth, execute_load, 
    execute_export, execute_utils, execute_config, execute_comm, execute_wizard
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
            command: Command string like "data read users --limit 10"
        
        Returns:
            Command execution result
        """
        if not command.strip():
            return None
        
        # Check if in wizard canvas mode
        wizard_mode = self.zcli.session.get("wizard_mode", {})
        if wizard_mode.get("active"):
            # In wizard canvas mode - accumulate lines silently
            
            # Handle wizard control commands
            if command.strip() == "wizard --stop":
                return self._wizard_stop()
            
            if command.strip() == "wizard --run":
                return self._wizard_run()
            
            if command.strip() == "wizard --show":
                return self._wizard_show()
            
            if command.strip() == "wizard --clear":
                return self._wizard_clear()
            
            # Accumulate line silently (preserve indentation for YAML)
            # Don't strip() - need to preserve whitespace for YAML parsing
            wizard_mode["lines"].append(command)
            return None
        
        try:
            # Parse the command using zParser
            parsed = self.zcli.zparser.parse_command(command)
            
            # Check for parsing errors
            if "error" in parsed:
                return parsed
            
            # Execute based on command type
            command_type = parsed.get("type")
            
            if command_type == "data":
                return execute_data(self.zcli, parsed)
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
            elif command_type == "comm":
                return execute_comm(self.zcli, parsed)
            elif command_type == "wizard":
                return execute_wizard(self.zcli, parsed)
            else:
                return {"error": f"Unknown command type: {command_type}"}
        
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Command execution failed: %s", e)
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════
    # Wizard Canvas Control Methods
    # ═══════════════════════════════════════════════════════════
    
    def _wizard_stop(self):
        """Exit wizard mode and discard buffer."""
        wizard_mode = self.zcli.session["wizard_mode"]
        line_count = len(wizard_mode["lines"])
        
        wizard_mode["active"] = False
        wizard_mode["lines"] = []
        wizard_mode["format"] = None
        
        print(f"[Exited wizard canvas - {line_count} lines discarded]")
        return {"status": "stopped", "lines_discarded": line_count}
    
    def _wizard_show(self):
        """Display current buffer."""
        lines = self.zcli.session["wizard_mode"]["lines"]
        
        if not lines:
            print("Wizard buffer empty")
            return {"status": "empty"}
        
        print(f"\nWizard Buffer ({len(lines)} lines):")
        print("─" * 70)
        for i, line in enumerate(lines, 1):
            print(f"{i:3}: {line}")
        print("─" * 70)
        
        return {"status": "shown", "lines": len(lines)}
    
    def _wizard_clear(self):
        """Clear buffer without exiting wizard mode."""
        wizard_mode = self.zcli.session["wizard_mode"]
        line_count = len(wizard_mode["lines"])
        wizard_mode["lines"] = []
        
        print(f"[Buffer cleared - {line_count} lines removed]")
        return {"status": "cleared", "lines": line_count}
    
    def _wizard_run(self):
        """Execute wizard buffer with smart format detection."""
        wizard_mode = self.zcli.session["wizard_mode"]
        lines = wizard_mode["lines"]
        
        if not lines:
            print("Wizard buffer empty - nothing to run")
            return {"error": "empty_buffer"}
        
        # Join lines into single string
        buffer = "\n".join(lines)
        
        print(f"\n[Executing wizard buffer ({len(lines)} lines)...]")
        print("─" * 70)
        
        # Detect format and execute
        result = self._execute_wizard_buffer(buffer)
        
        # Clear buffer after successful execution
        if result.get("status") == "success":
            wizard_mode["lines"] = []
            print("─" * 70)
            print("[Buffer cleared after execution]")
        
        return result
    
    def _execute_wizard_buffer(self, buffer):
        """
        Smart format detection and execution.
        
        Detects three formats:
        1. YAML structure (step1:, zData:, etc.) → Execute via zWizard
        2. Shell commands (data read, func, etc.) → Execute sequentially
        3. Hybrid (YAML with embedded shell commands) → Execute via zWizard with preprocessing
        """
        import yaml
        
        # Try YAML parsing first
        try:
            wizard_obj = yaml.safe_load(buffer)
            
            if isinstance(wizard_obj, dict):
                # Valid YAML structure - execute via zWizard
                print("[Detected YAML/Hybrid format]")
                
                # Check for transaction flag
                use_transaction = wizard_obj.get("_transaction", False)
                if use_transaction:
                    print("[Transaction mode: ENABLED]")
                
                # Count actual steps (non-meta keys)
                step_count = len([k for k in wizard_obj.keys() if not k.startswith("_")])
                print(f"[Executing {step_count} steps via zWizard...]")
                
                # Execute via zWizard (already has transaction support)
                result = self.zcli.wizard.handle(wizard_obj)
                
                print("[✅ Wizard execution complete]")
                return {"status": "success", "format": "yaml", "result": result}
        
        except yaml.YAMLError as e:
            # Not valid YAML - treat as shell commands
            self.logger.debug("YAML parsing failed: %s - treating as shell commands", e)
        
        # Execute as sequential shell commands
        print("[Detected shell command format]")
        lines = [line.strip() for line in buffer.split("\n") if line.strip()]
        
        print(f"[Executing {len(lines)} commands sequentially...]")
        results = []
        
        for i, command in enumerate(lines, 1):
            print(f"\n[Step {i}/{len(lines)}] {command}")
            
            # Parse command
            parsed = self.zcli.zparser.parse_command(command)
            if "error" in parsed:
                print(f"[X] Parse error: {parsed['error']}")
                return {"error": f"Failed at step {i}", "command": command, "parse_error": parsed["error"]}
            
            # Execute command
            try:
                result = self._execute_parsed_command(parsed)
                results.append(result)
                print(f"[✓] Step {i} complete")
            except Exception as e:
                print(f"[X] Execution error: {e}")
                return {"error": f"Failed at step {i}", "command": command, "exception": str(e)}
        
        print(f"\n[✅ {len(lines)} commands executed successfully]")
        return {"status": "success", "format": "commands", "results": results}
    
    def _execute_parsed_command(self, parsed):
        """Execute a pre-parsed command (extracted from execute method)."""
        command_type = parsed.get("type")
        
        if command_type == "data":
            return execute_data(self.zcli, parsed)
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
        elif command_type == "auth":
            return execute_auth(self.zcli, parsed)
        elif command_type == "export":
            return execute_export(self.zcli, parsed)
        elif command_type == "config":
            return execute_config(self.zcli, parsed)
        elif command_type == "comm":
            return execute_comm(self.zcli, parsed)
        elif command_type == "load":
            return execute_load(self.zcli, parsed)
        else:
            return {"error": f"Unknown command type: {command_type}"}
