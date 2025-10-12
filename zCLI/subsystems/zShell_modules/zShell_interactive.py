# zCLI/zCore/Shell.py — Interactive Shell Mode
# ───────────────────────────────────────────────────────────────

import os
from pathlib import Path
from logger import Logger
from .zShell_help import HelpSystem
from .zShell_executor import CommandExecutor

# Enable command history with readline (Unix/Linux/Mac)
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    # Windows doesn't have readline by default
    # Could use pyreadline3 as alternative
    READLINE_AVAILABLE = False

# Logger instance
logger = Logger.get_logger(__name__)


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
        Initialize shell interface.
        
        Args:
            zcli: Parent zCLI instance
        """
        self.zcli = zcli
        self.logger = Logger.get_logger()
        self.executor = CommandExecutor(zcli)
        self.help_system = HelpSystem()
        self.running = False
        
        # Setup command history
        self.history_file = None
        if READLINE_AVAILABLE:
            self._setup_history()
    
    def run(self):
        """Main shell loop - handles user input and command execution."""
        logger.info("Starting zCLI shell...")
        
        # Show welcome message
        print(self.help_system.get_welcome_message())
        
        self.running = True
        
        while self.running:
            try:
                # Get user input with dynamic prompt
                prompt = self._get_prompt()
                raw_input = input(prompt)
                
                # In wizard mode, preserve whitespace for YAML indentation
                # In normal mode, strip whitespace
                wizard_mode = self.zcli.session.get("wizard_mode", {})
                if wizard_mode.get("active"):
                    command = raw_input  # Preserve indentation
                else:
                    command = raw_input.strip()  # Strip in normal mode
                
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
        
        # Save command history
        if READLINE_AVAILABLE and self.history_file:
            self._save_history()
    
    def _get_prompt(self):
        """
        Get the appropriate prompt based on current mode.
        
        Returns:
            str: Prompt string
        """
        wizard_mode = self.zcli.session.get("wizard_mode", {})
        if wizard_mode.get("active"):
            return "> "  # Wizard canvas mode
        return "zCLI> "  # Normal mode
    
    def _setup_history(self):
        """Setup readline history file for persistent command history."""
        try:
            # Store history in user's home directory
            home = Path.home()
            history_dir = home / ".zolo"
            history_dir.mkdir(exist_ok=True)
            self.history_file = history_dir / ".zcli_history"
            
            # Load existing history if available
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
                logger.debug("Loaded command history from %s", self.history_file)
            
            # Set history size
            readline.set_history_length(1000)
            
            logger.info("Command history enabled (↑/↓ arrows to navigate)")
            
        except Exception as e:
            logger.warning("Could not setup command history: %s", e)
            self.history_file = None
    
    def _save_history(self):
        """Save command history to file."""
        try:
            readline.write_history_file(str(self.history_file))
            logger.debug("Saved command history to %s", self.history_file)
        except Exception as e:
            logger.warning("Could not save command history: %s", e)
    
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
    from zCLI.zCLI import zCLI
    
    print("\n[>>] Launching zCLI Shell from UI...")
    print("Type 'exit' to return to UI menu")
    print("=" * 50)
    
    # Create zCLI instance in shell mode
    cli = zCLI()
    cli.run_shell()
    
    print("\n" + "=" * 50)
    print("🔄 Returning to UI menu...")
    return "Returned from zCLI shell"

