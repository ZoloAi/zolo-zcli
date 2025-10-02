# zCLI/zCore/CommandParser.py — Command Parsing System
# ───────────────────────────────────────────────────────────────

from zCLI.utils.logger import logger

class CommandParser:
    """
    Parses shell commands into structured format.
    
    Supports commands like:
    - crud read users --limit 10 --where "role=admin"
    - func generate_id zU
    - utils hash_password mypass
    - session set mode zGUI
    """
    
    def __init__(self, zcli_instance):
        self.zCLI = zcli_instance
        
        # Command patterns
        self.commands = {
            "crud": self._parse_crud_command,
            "func": self._parse_func_command,
            "utils": self._parse_utils_command,
            "session": self._parse_session_command,
            "walker": self._parse_walker_command,
            "open": self._parse_open_command,
            "test": self._parse_test_command,
            "auth": self._parse_auth_command,
        }
    
    def parse_command(self, command: str):
        """
        Parse a command string into structured format.
        
        Args:
            command: Raw command string
            
        Returns:
            Dict with parsed command structure
        """
        command = command.strip()
        
        # Split into parts
        parts = self._split_command(command)
        if not parts:
            return {"error": "Empty command"}
        
        command_type = parts[0].lower()
        
        if command_type not in self.commands:
            return {"error": f"Unknown command: {command_type}"}
        
        try:
            return self.commands[command_type](parts)
        except Exception as e:
            logger.error("Command parsing failed: %s", e)
            return {"error": f"Parse error: {str(e)}"}
    
    def _split_command(self, command: str):
        """
        Split command into parts, handling quotes and special characters.
        
        Args:
            command: Command string
            
        Returns:
            List of command parts
        """
        # Use regex to split while preserving quoted strings
        parts = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for char in command:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == ' ' and not in_quotes:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            parts.append(current.strip())
        
        return parts
    
    def _parse_crud_command(self, parts):
        """Parse CRUD commands like 'crud read users --limit 10'"""
        if len(parts) < 2:
            return {"error": "CRUD command requires action"}
        
        action = parts[1].lower()
        valid_actions = ["read", "create", "update", "delete", "search", "tables"]
        
        if action not in valid_actions:
            return {"error": f"Invalid CRUD action: {action}"}
        
        # Extract arguments and options
        args = []
        options = {}
        
        i = 2
        while i < len(parts):
            part = parts[i]
            
            if part.startswith("--"):
                # Option
                opt_name = part[2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                    options[opt_name] = parts[i + 1]
                    i += 2
                else:
                    options[opt_name] = True
                    i += 1
            else:
                # Argument
                args.append(part)
                i += 1
        
        return {
            "type": "crud",
            "action": action,
            "args": args,
            "options": options
        }
    
    def _parse_func_command(self, parts):
        """Parse function commands like 'func generate_id zU'"""
        if len(parts) < 2:
            return {"error": "Function command requires function name"}
        
        func_name = parts[1]
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "func",
            "action": func_name,
            "args": args,
            "options": {}
        }
    
    def _parse_utils_command(self, parts):
        """Parse utility commands like 'utils hash_password mypass'"""
        if len(parts) < 2:
            return {"error": "Utility command requires utility name"}
        
        util_name = parts[1]
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "utils",
            "action": util_name,
            "args": args,
            "options": {}
        }
    
    def _parse_session_command(self, parts):
        """Parse session commands like 'session info' or 'session set mode zGUI'"""
        if len(parts) < 2:
            return {"error": "Session command requires action"}
        
        action = parts[1]
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "session",
            "action": action,
            "args": args,
            "options": {}
        }
    
    def _parse_walker_command(self, parts):
        """Parse walker commands like 'walker load ui.zCloud.yaml'"""
        if len(parts) < 2:
            return {"error": "Walker command requires action"}
        
        action = parts[1]
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "walker",
            "action": action,
            "args": args,
            "options": {}
        }
    
    def _parse_open_command(self, parts):
        """Parse open commands like 'open @.zProducts.zTimer.index.html' or 'open https://example.com'"""
        if len(parts) < 2:
            return {"error": "Open command requires path"}
        
        # The path is everything after "open", rejoined if it was split
        path = " ".join(parts[1:])
        
        return {
            "type": "open",
            "action": "open",
            "args": [path],
            "options": {}
        }
    
    def _parse_test_command(self, parts):
        """Parse test commands like 'test run' or 'test session'"""
        action = "run" if len(parts) < 2 else parts[1]
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "test",
            "action": action,
            "args": args,
            "options": {}
        }
    
    def _parse_auth_command(self, parts):
        """Parse auth commands like 'auth login', 'auth logout', 'auth status'"""
        if len(parts) < 2:
            return {"error": "Auth command requires action (login, logout, status)"}
        
        action = parts[1].lower()
        valid_actions = ["login", "logout", "status"]
        
        if action not in valid_actions:
            return {"error": f"Invalid auth action: {action}. Use: {', '.join(valid_actions)}"}
        
        # Extract any additional arguments (e.g., username, server URL)
        args = parts[2:] if len(parts) > 2 else []
        
        return {
            "type": "auth",
            "action": action,
            "args": args,
            "options": {}
        }
