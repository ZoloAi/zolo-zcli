# zCLI/subsystems/zShell/shell_modules/shell_interactive.py

"""Interactive shell mode with REPL interface and command history."""

from zCLI import os, Path
from .shell_help import HelpSystem
from .shell_executor import CommandExecutor

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

class InteractiveShell:
    """Interactive shell mode with REPL interface and command history."""

    def __init__(self, zcli):
        """Initialize shell interface."""
        self.zcli = zcli
        self.logger = zcli.logger
        self.display = zcli.display
        self.executor = CommandExecutor(zcli)
        self.help_system = HelpSystem(display=self.display)
        self.running = False

        self.history_file = None
        if READLINE_AVAILABLE:
            self._setup_history()

    def run(self):
        """Main shell loop - handles user input and command execution."""
        self.logger.info("Starting zCLI shell...")
        self.zcli.display.write_block(self.help_system.get_welcome_message())
        self.running = True

        while self.running:
            try:
                prompt = self._get_prompt()
                raw_input = input(prompt)

                wizard_mode = self.zcli.session.get("wizard_mode", {})
                if wizard_mode.get("active"):
                    command = raw_input  # Preserve indentation
                else:
                    command = raw_input.strip()

                if not command:
                    continue

                if self._handle_special_commands(command):
                    continue

                result = self.executor.execute(command)
                if result:
                    self._display_result(result)

            except KeyboardInterrupt:
                self.zcli.display.zDeclare("Goodbye!", color="INFO", indent=0, style="single")
                break

            except EOFError:
                self.zcli.display.zDeclare("Goodbye!", color="INFO", indent=0, style="single")
                break

            except Exception as e:
                self.logger.error("Shell error: %s", e)
                self.zcli.display.zDeclare(f"Error: {e}", color="ERROR", indent=0, style="single")

        self.logger.info("Exiting zCLI shell...")
        if READLINE_AVAILABLE and self.history_file:
            self._save_history()

    def _get_prompt(self):
        """Get the appropriate prompt based on current mode."""
        wizard_mode = self.zcli.session.get("wizard_mode", {})
        if wizard_mode.get("active"):
            return "> "
        
        # Check if zPath display is enabled (via 'where on' command)
        show_zpath = self.zcli.session.get("zShowZPathInPrompt", False)
        if show_zpath:
            zpath = self._format_zpath_for_prompt()
            if zpath:
                return f"zCLI [{zpath}]> "
        
        return "zCLI> "
    
    def _format_zpath_for_prompt(self):
        """Format current OS working directory as zPath for prompt display."""
        try:
            # Get current OS working directory (not the constant workspace root)
            current_dir = os.getcwd()
            current_path = Path(current_dir).resolve()
            home_path = Path.home()
            
            # Check if under home directory
            if current_path.is_relative_to(home_path):
                relative_path = current_path.relative_to(home_path)
                if relative_path == Path("."):
                    return "~"  # User is at home directory
                else:
                    # Build zPath with dots
                    zpath_parts = relative_path.parts
                    return "~." + ".".join(zpath_parts)
            else:
                # Outside home, use absolute path
                return str(current_path)
        
        except (ValueError, AttributeError, OSError):
            # Invalid path, return None
            return None

    def _setup_history(self):
        """Setup readline history file for persistent command history."""
        try:
            home = Path.home()
            history_dir = home / ".zolo"
            history_dir.mkdir(exist_ok=True)
            self.history_file = history_dir / ".zcli_history"

            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
                self.logger.debug("Loaded command history from %s", self.history_file)

            readline.set_history_length(1000)
            self.logger.info("Command history enabled (up/down arrows to navigate)")

        except Exception as e:
            self.logger.warning("Could not setup command history: %s", e)
            self.history_file = None

    def _save_history(self):
        """Save command history to file."""
        try:
            readline.write_history_file(str(self.history_file))
            self.logger.debug("Saved command history to %s", self.history_file)
        except Exception as e:
            self.logger.warning("Could not save command history: %s", e)

    def _handle_special_commands(self, command):
        """Handle special built-in commands."""
        cmd_lower = command.lower()

        if cmd_lower in ["exit", "quit", "q"]:
            self.zcli.display.zDeclare("Goodbye!", color="INFO", indent=0, style="single")
            self.running = False
            return True

        if cmd_lower in ["clear", "cls"]:
            os.system('clear' if os.name == 'posix' else 'cls')
            return True

        if cmd_lower == "tips":
            self.zcli.display.write_block(self.help_system.get_quick_tips())
            return True

        return False

    def _display_result(self, result):
        """
        Display command execution result in terminal mode.
        
        Commands are UI adapters - they display friendly messages directly.
        This method handles fallback display for commands that only return data.
        
        Note: For programmatic access, bypass shell and use subsystems directly
        (e.g., zcli.data.read(), zcli.auth.login()). Shell is for interactive REPL.
        """
        if result is None:
            return

        if isinstance(result, dict):
            if "error" in result:
                self.zcli.display.zDeclare(
                    f"Error: {result['error']}",
                    color="ERROR", indent=0, style="single"
                )
            elif "success" in result:
                self.zcli.display.zDeclare(
                    result['success'],
                    color="SUCCESS", indent=0, style="single"
                )
                if "note" in result:
                    self.zcli.display.zDeclare(
                        result['note'],
                        color="INFO", indent=1, style="single"
                    )
            # Suppress JSON output if dict has no "error" or "success"
            # (commands already displayed friendly messages)

        elif isinstance(result, str):
            self.zcli.display.zDeclare(
                result,
                color="DATA", indent=0, style="single"
            )

        # Note: Removed automatic JSON fallback for dicts without error/success
        # Commands should display their own messages, not rely on JSON dumps

    def execute_command(self, command):
        """Execute a single command (useful for testing or scripting)."""
        return self.executor.execute(command)

def launch_zCLI_shell(zcli):
    """Launch zCLI shell from within the UI"""
    zcli.display.zDeclare(
        "Launching zCLI Shell from UI",
        color="EXTERNAL", indent=0, style="full"
    )

    zcli.display.zDeclare(
        "Type 'exit' to return to UI menu",
        color="INFO", indent=0, style="single"
    )

    zcli.run_shell()

    zcli.display.zDeclare(
        "Returning to UI menu",
        color="EXTERNAL", indent=0, style="full"
    )

    return "Returned from zCLI shell"
