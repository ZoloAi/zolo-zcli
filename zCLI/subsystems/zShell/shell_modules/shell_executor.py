# zCLI/subsystems/zShell/shell_modules/shell_executor.py

"""Command execution engine with wizard canvas mode support."""

from .commands import (
    execute_data, execute_func, execute_session, execute_walker,
    execute_open, execute_test, execute_auth, execute_load,
    execute_export, execute_utils, execute_config, execute_comm,
    execute_wizard_step, execute_plugin,
    execute_ls, execute_cd, execute_pwd, execute_shortcut, execute_where, execute_help
)
from .commands.shell_cmd_config_persistence import execute_config_persistence

class CommandExecutor:
    """Command execution engine with wizard canvas mode support."""

    def __init__(self, zcli):
        """Initialize command executor."""
        self.zcli = zcli
        self.logger = zcli.logger

    def execute(self, command: str):
        """Parse and execute a shell command."""
        if not command.strip():
            return None

        wizard_mode = self.zcli.session.get("wizard_mode", {})
        if wizard_mode.get("active"):
            return self._handle_wizard_command(command, wizard_mode)

        try:
            parsed = self.zcli.zparser.parse_command(command)

            if "error" in parsed:
                return parsed

            return self._execute_parsed_command(parsed)

        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Command execution failed: %s", e)
            return {"error": str(e)}

    def _handle_wizard_command(self, command, wizard_mode):
        """Handle wizard canvas mode commands."""
        if command.strip() == "wizard --stop":
            return self._wizard_stop()

        if command.strip() == "wizard --run":
            return self._wizard_run()

        if command.strip() == "wizard --show":
            return self._wizard_show()

        if command.strip() == "wizard --clear":
            return self._wizard_clear()

        wizard_mode["lines"].append(command)
        return None

    def _wizard_stop(self):
        """Exit wizard mode and discard buffer."""
        wizard_mode = self.zcli.session["wizard_mode"]
        line_count = len(wizard_mode["lines"])

        wizard_mode["active"] = False
        wizard_mode["lines"] = []
        wizard_mode["format"] = None

        self.zcli.display.zDeclare(
            f"Exited wizard canvas - {line_count} lines discarded",
            color="INFO", indent=0, style="single"
        )
        return {"status": "stopped", "lines_discarded": line_count}

    def _wizard_show(self):
        """Display current buffer."""
        lines = self.zcli.session["wizard_mode"]["lines"]

        if not lines:
            self.zcli.display.zDeclare(
                "Wizard buffer empty",
                color="INFO", indent=0, style="single"
            )
            return {"status": "empty"}

        self.zcli.display.zDeclare(
            f"Wizard Buffer ({len(lines)} lines):",
            color="INFO", indent=0, style="full"
        )

        for i, line in enumerate(lines, 1):
            self.zcli.display.zDeclare(
                f"{i:3}: {line}",
                color="DATA", indent=1, style="single"
            )

        return {"status": "shown", "lines": len(lines)}

    def _wizard_clear(self):
        """Clear buffer without exiting wizard mode."""
        wizard_mode = self.zcli.session["wizard_mode"]
        line_count = len(wizard_mode["lines"])
        wizard_mode["lines"] = []

        self.zcli.display.zDeclare(
            f"Buffer cleared - {line_count} lines removed",
            color="INFO", indent=0, style="single"
        )
        return {"status": "cleared", "lines": line_count}

    def _wizard_run(self):
        """Execute wizard buffer with smart format detection."""
        wizard_mode = self.zcli.session["wizard_mode"]
        lines = wizard_mode["lines"]

        if not lines:
            self.zcli.display.zDeclare(
                "Wizard buffer empty - nothing to run",
                color="WARNING", indent=0, style="single"
            )
            return {"error": "empty_buffer"}

        buffer = "\n".join(lines)

        self.zcli.display.zDeclare(
            f"Executing wizard buffer ({len(lines)} lines)...",
            color="EXTERNAL", indent=0, style="full"
        )

        result = self._execute_wizard_buffer(buffer)

        if result.get("status") == "success":
            wizard_mode["lines"] = []
            self.zcli.display.zDeclare(
                "Buffer cleared after execution",
                color="INFO", indent=0, style="single"
            )

        return result

    def _execute_wizard_buffer(self, buffer):
        """Smart format detection and execution."""
        import yaml

        try:
            wizard_obj = yaml.safe_load(buffer)

            if isinstance(wizard_obj, dict):
                self.zcli.display.zDeclare(
                    "Detected YAML/Hybrid format",
                    color="INFO", indent=1, style="single"
                )

                use_transaction = wizard_obj.get("_transaction", False)
                if use_transaction:
                    self.zcli.display.zDeclare(
                        "Transaction mode: ENABLED",
                        color="WARNING", indent=1, style="single"
                    )

                step_count = len([k for k in wizard_obj.keys() if not k.startswith("_")])
                self.zcli.display.zDeclare(
                    f"Executing {step_count} steps via zWizard...",
                    color="EXTERNAL", indent=1, style="single"
                )

                result = self.zcli.wizard.handle(wizard_obj)

                self.zcli.display.zDeclare(
                    "[OK] Wizard execution complete",
                    color="SUCCESS", indent=1, style="single"
                )
                return {"status": "success", "format": "yaml", "result": result}

        except yaml.YAMLError as e:
            self.logger.debug("YAML parsing failed: %s - treating as shell commands", e)

        self.zcli.display.zDeclare(
            "Detected shell command format",
            color="INFO", indent=1, style="single"
        )
        lines = [line.strip() for line in buffer.split("\n") if line.strip()]

        self.zcli.display.zDeclare(
            f"Executing {len(lines)} commands via zWizard...",
            color="EXTERNAL", indent=1, style="single"
        )

        # Convert shell commands to wizard format for transaction support
        wizard_obj = {}
        for i, command in enumerate(lines, 1):
            wizard_obj[f"step_{i}"] = command

        # Execute via zWizard (provides transaction support and error handling)
        try:
            result = self.zcli.wizard.handle(wizard_obj)

            self.zcli.display.zDeclare(
                f"[OK] {len(lines)} commands executed successfully",
                color="SUCCESS", indent=1, style="full"
            )
            return {"status": "success", "format": "commands", "result": result}
        except Exception as e:
            self.zcli.display.zDeclare(
                f"Execution error: {e}",
                color="ERROR", indent=2, style="single"
            )
            return {"error": "Wizard execution failed", "exception": str(e)}

    def _execute_parsed_command(self, parsed):
        """Execute a pre-parsed command."""
        command_type = parsed.get("type")

        command_map = {
            "data": execute_data,
            "func": execute_func,
            "utils": execute_utils,
            "session": execute_session,
            "walker": execute_walker,
            "open": execute_open,
            "test": execute_test,
            "auth": execute_auth,
            "export": execute_export,
            "config": execute_config,
            "config_persistence": execute_config_persistence,
            "comm": execute_comm,
            "load": execute_load,
            "plugin": execute_plugin,
            "ls": execute_ls,
            "list": execute_ls,  # Modern alias for ls (beginner-friendly)
            "dir": execute_ls,   # Windows alias for ls
            "cd": execute_cd,
            "cwd": execute_pwd,       # Primary: Current Working Directory
            "pwd": execute_pwd,       # Alias: Unix compatibility (Print Working Directory)
            "shortcut": execute_shortcut,
            "where": execute_where,
            "help": execute_help,
        }

        executor = command_map.get(command_type)
        if executor:
            return executor(self.zcli, parsed)

        return {"error": f"Unknown command type: {command_type}"}

    def execute_wizard_step(self, step_key, step_value, step_context):
        """Execute a wizard step via the shell's wizard step executor."""
        return execute_wizard_step(self.zcli, step_key, step_value, self.logger, step_context)
