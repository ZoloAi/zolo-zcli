"""Interactive shell mode with REPL interface and command history."""

import os
from pathlib import Path
from logger import Logger
from .zShell_help import HelpSystem
from .zShell_executor import CommandExecutor

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

logger = Logger.get_logger(__name__)

class InteractiveShell:
    """Interactive shell mode with REPL interface and command history."""

    def __init__(self, zcli):
        """Initialize shell interface."""
        self.zcli = zcli
        self.logger = Logger.get_logger()
        self.executor = CommandExecutor(zcli)
        self.help_system = HelpSystem()
        self.running = False

        self.history_file = None
        if READLINE_AVAILABLE:
            self._setup_history()

    def run(self):
        """Main shell loop - handles user input and command execution."""
        logger.info("Starting zCLI shell...")
        self.zcli.display.handle({
            "event": "sysmsg",
            "label": self.help_system.get_welcome_message(),
            "style": "raw",
            "color": "INFO",
            "indent": 0
        })
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
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": "Goodbye!",
                    "style": "single",
                    "color": "INFO",
                    "indent": 0
                })
                break

            except EOFError:
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": "Goodbye!",
                    "style": "single",
                    "color": "INFO",
                    "indent": 0
                })
                break

            except Exception as e:
                logger.error("Shell error: %s", e)
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"Error: {e}",
                    "style": "single",
                    "color": "ERROR",
                    "indent": 0
                })

        logger.info("Exiting zCLI shell...")
        if READLINE_AVAILABLE and self.history_file:
            self._save_history()

    def _get_prompt(self):
        """Get the appropriate prompt based on current mode."""
        wizard_mode = self.zcli.session.get("wizard_mode", {})
        if wizard_mode.get("active"):
            return "> "
        return "zCLI> "

    def _setup_history(self):
        """Setup readline history file for persistent command history."""
        try:
            home = Path.home()
            history_dir = home / ".zolo"
            history_dir.mkdir(exist_ok=True)
            self.history_file = history_dir / ".zcli_history"

            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
                logger.debug("Loaded command history from %s", self.history_file)

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
        """Handle special built-in commands."""
        cmd_lower = command.lower()

        if cmd_lower in ["exit", "quit", "q"]:
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": "Goodbye!",
                "style": "single",
                "color": "INFO",
                "indent": 0
            })
            self.running = False
            return True

        if cmd_lower == "help":
            self.help_system.show_help()
            return True

        if cmd_lower.startswith("help "):
            topic = command[5:].strip()
            self.help_system.show_command_help(topic)
            return True

        if cmd_lower in ["clear", "cls"]:
            os.system('clear' if os.name == 'posix' else 'cls')
            return True

        if cmd_lower == "tips":
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": self.help_system.get_quick_tips(),
                "style": "raw",
                "color": "INFO",
                "indent": 0
            })
            return True

        return False

    def _display_result(self, result):
        """Display command execution result."""
        if result is None:
            return

        if isinstance(result, dict):
            if "error" in result:
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"Error: {result['error']}",
                    "style": "single",
                    "color": "ERROR",
                    "indent": 0
                })
            elif "success" in result:
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": result['success'],
                    "style": "single",
                    "color": "SUCCESS",
                    "indent": 0
                })
                if "note" in result:
                    self.zcli.display.handle({
                        "event": "sysmsg",
                        "label": result['note'],
                        "style": "single",
                        "color": "INFO",
                        "indent": 1
                    })
            else:
                self.zcli.display.handle({"event": "zJSON", "payload": result})

        elif isinstance(result, str):
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": result,
                "style": "single",
                "color": "DATA",
                "indent": 0
            })

        else:
            self.zcli.display.handle({"event": "zJSON", "payload": {"result": result}})

    def execute_command(self, command):
        """Execute a single command (useful for testing or scripting)."""
        return self.executor.execute(command)

def launch_zCLI_shell(zcli):
    """Launch zCLI shell from within the UI"""
    zcli.display.handle({
        "event": "sysmsg",
        "label": "Launching zCLI Shell from UI",
        "style": "full",
        "color": "EXTERNAL",
        "indent": 0
    })

    zcli.display.handle({
        "event": "sysmsg",
        "label": "Type 'exit' to return to UI menu",
        "style": "single",
        "color": "INFO",
        "indent": 0
    })

    zcli.run_shell()

    zcli.display.handle({
        "event": "sysmsg",
        "label": "Returning to UI menu",
        "style": "full",
        "color": "EXTERNAL",
        "indent": 0
    })

    return "Returned from zCLI shell"
