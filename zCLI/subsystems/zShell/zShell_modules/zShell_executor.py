"""Command execution engine with wizard canvas mode support."""

from logger import Logger
from .executor_commands import (
    execute_data, execute_func, execute_session, execute_walker,
    execute_open, execute_test, execute_auth, execute_load, 
    execute_export, execute_utils, execute_config, execute_comm
)
from .executor_commands.config_persistence_executor import execute_config_persistence

logger = Logger.get_logger(__name__)

class CommandExecutor:
    """Command execution engine with wizard canvas mode support."""

    def __init__(self, zcli):
        """Initialize command executor."""
        self.zcli = zcli
        self.logger = Logger.get_logger()

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

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"Exited wizard canvas - {line_count} lines discarded",
            "style": "single",
            "color": "INFO",
            "indent": 0
        })
        return {"status": "stopped", "lines_discarded": line_count}

    def _wizard_show(self):
        """Display current buffer."""
        lines = self.zcli.session["wizard_mode"]["lines"]

        if not lines:
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": "Wizard buffer empty",
                "style": "single",
                "color": "INFO",
                "indent": 0
            })
            return {"status": "empty"}

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"Wizard Buffer ({len(lines)} lines):",
            "style": "full",
            "color": "INFO",
            "indent": 0
        })

        for i, line in enumerate(lines, 1):
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": f"{i:3}: {line}",
                "style": "single",
                "color": "DATA",
                "indent": 1
            })

        return {"status": "shown", "lines": len(lines)}

    def _wizard_clear(self):
        """Clear buffer without exiting wizard mode."""
        wizard_mode = self.zcli.session["wizard_mode"]
        line_count = len(wizard_mode["lines"])
        wizard_mode["lines"] = []

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"Buffer cleared - {line_count} lines removed",
            "style": "single",
            "color": "INFO",
            "indent": 0
        })
        return {"status": "cleared", "lines": line_count}

    def _wizard_run(self):
        """Execute wizard buffer with smart format detection."""
        wizard_mode = self.zcli.session["wizard_mode"]
        lines = wizard_mode["lines"]

        if not lines:
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": "Wizard buffer empty - nothing to run",
                "style": "single",
                "color": "WARNING",
                "indent": 0
            })
            return {"error": "empty_buffer"}

        buffer = "\n".join(lines)

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"Executing wizard buffer ({len(lines)} lines)...",
            "style": "full",
            "color": "EXTERNAL",
            "indent": 0
        })

        result = self._execute_wizard_buffer(buffer)

        if result.get("status") == "success":
            wizard_mode["lines"] = []
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": "Buffer cleared after execution",
                "style": "single",
                "color": "INFO",
                "indent": 0
            })

        return result

    def _execute_wizard_buffer(self, buffer):
        """Smart format detection and execution."""
        import yaml

        try:
            wizard_obj = yaml.safe_load(buffer)

            if isinstance(wizard_obj, dict):
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": "Detected YAML/Hybrid format",
                    "style": "single",
                    "color": "INFO",
                    "indent": 1
                })

                use_transaction = wizard_obj.get("_transaction", False)
                if use_transaction:
                    self.zcli.display.handle({
                        "event": "sysmsg",
                        "label": "Transaction mode: ENABLED",
                        "style": "single",
                        "color": "WARNING",
                        "indent": 1
                    })

                step_count = len([k for k in wizard_obj.keys() if not k.startswith("_")])
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"Executing {step_count} steps via zWizard...",
                    "style": "single",
                    "color": "EXTERNAL",
                    "indent": 1
                })

                result = self.zcli.wizard.handle(wizard_obj)

                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": "[OK] Wizard execution complete",
                    "style": "single",
                    "color": "SUCCESS",
                    "indent": 1
                })
                return {"status": "success", "format": "yaml", "result": result}

        except yaml.YAMLError as e:
            self.logger.debug("YAML parsing failed: %s - treating as shell commands", e)

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": "Detected shell command format",
            "style": "single",
            "color": "INFO",
            "indent": 1
        })
        lines = [line.strip() for line in buffer.split("\n") if line.strip()]

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"Executing {len(lines)} commands sequentially...",
            "style": "single",
            "color": "EXTERNAL",
            "indent": 1
        })
        results = []

        for i, command in enumerate(lines, 1):
            self.zcli.display.handle({
                "event": "sysmsg",
                "label": f"Step {i}/{len(lines)}: {command}",
                "style": "single",
                "color": "DATA",
                "indent": 2
            })

            parsed = self.zcli.zparser.parse_command(command)
            if "error" in parsed:
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"Parse error: {parsed['error']}",
                    "style": "single",
                    "color": "ERROR",
                    "indent": 2
                })
                return {"error": f"Failed at step {i}", "command": command, "parse_error": parsed["error"]}

            try:
                result = self._execute_parsed_command(parsed)
                results.append(result)
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"✓ Step {i} complete",
                    "style": "single",
                    "color": "SUCCESS",
                    "indent": 2
                })
            except Exception as e:
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": f"Execution error: {e}",
                    "style": "single",
                    "color": "ERROR",
                    "indent": 2
                })
                return {"error": f"Failed at step {i}", "command": command, "exception": str(e)}

        self.zcli.display.handle({
            "event": "sysmsg",
            "label": f"[OK] {len(lines)} commands executed successfully",
            "style": "full",
            "color": "SUCCESS",
            "indent": 1
        })
        return {"status": "success", "format": "commands", "results": results}

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
        }

        executor = command_map.get(command_type)
        if executor:
            return executor(self.zcli, parsed)

        return {"error": f"Unknown command type: {command_type}"}
