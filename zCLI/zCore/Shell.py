# zCLI/zCore/Shell.py — Interactive Shell Mode
# ───────────────────────────────────────────────────────────────

from zCLI.utils.logger import logger
from zCLI.zCore.Help import HelpSystem
from zCLI.zCore.CommandExecutor import CommandExecutor


class InteractiveShell:
    """
    Interactive Shell Mode for zCLI.
    
    Provides a command-line interface with:
    - Command prompt
    - Command execution
    - History (within session)
    - Help system
    - Error handling
    """
    
    def __init__(self, zcli):
        """
        Initialize interactive shell.
        
        Args:
            zcli: Parent zCLI instance
        """
        self.zcli = zcli
        self.logger = logger
        self.executor = CommandExecutor(zcli)
        self.help_system = HelpSystem()
        self.running = False
    
    def run(self):
        """Main shell loop - handles user input and command execution."""
        logger.info("Starting zCLI interactive shell...")
        
        # Show welcome message
        print(self.help_system.get_welcome_message())
        
        self.running = True
        
        while self.running:
            try:
                # Get user input
                command = input("zCLI> ").strip()
                
                # Handle empty input
                if not command:
                    continue
                
                # Handle special commands
                if self._handle_special_commands(command):
                    continue
                
                # Execute command
                result = self.executor.execute(command)
                
                # Display result
                if result:
                    self._display_result(result)
            
            except KeyboardInterrupt:
                print("\n[~] Goodbye!")
                break
            
            except EOFError:
                print("\n[~] Goodbye!")
                break
            
            except Exception as e:
                logger.error("Shell error: %s", e)
                print(f"[X] Error: {e}")
        
        logger.info("Exiting zCLI shell...")
    
    def _handle_special_commands(self, command):
        """
        Handle special built-in commands.
        
        Args:
            command: User input command
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        cmd_lower = command.lower()
        
        # Exit commands
        if cmd_lower in ["exit", "quit", "q"]:
            print("[~] Goodbye!")
            self.running = False
            return True
        
        # Help commands
        if cmd_lower == "help":
            self.help_system.show_help()
            return True
        
        if cmd_lower.startswith("help "):
            # Context-specific help
            topic = command[5:].strip()
            self.help_system.show_command_help(topic)
            return True
        
        # Clear screen (optional)
        if cmd_lower in ["clear", "cls"]:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
            return True
        
        # Tips
        if cmd_lower == "tips":
            print(self.help_system.get_quick_tips())
            return True
        
        return False
    
    def _display_result(self, result):
        """
        Display command execution result.
        
        Args:
            result: Command execution result (dict, str, or other)
        """
        if result is None:
            return
        
        # Handle different result types
        if isinstance(result, dict):
            # Check for special keys
            if "error" in result:
                print(f"[X] Error: {result['error']}")
            elif "success" in result:
                print(f"[OK] {result['success']}")
                # Show additional info if present
                if "note" in result:
                    print(f"     [i] {result['note']}")
            else:
                # Display as JSON via display subsystem
                self.zcli.display.handle({"event": "zJSON", "payload": result})
        
        elif isinstance(result, str):
            print(result)
        
        else:
            # Try to display any other type
            self.zcli.display.handle({"event": "zJSON", "payload": {"result": result}})
    
    def execute_command(self, command):
        """
        Execute a single command (useful for testing or scripting).
        
        Args:
            command: Command string to execute
            
        Returns:
            Command execution result
        """
        return self.executor.execute(command)


def launch_zCLI_shell():
    """Launch zCLI shell from within the UI"""
    from zCLI.zCore.zCLI import zCLI
    
    print("\n[>>] Launching zCLI Shell from UI...")
    print("Type 'exit' to return to UI menu")
    print("=" * 50)
    
    # Create zCLI instance in shell mode
    cli = zCLI()
    cli.run_interactive()
    
    print("\n" + "=" * 50)
    print("🔄 Returning to UI menu...")
    return "Returned from zCLI shell"

