# zTestSuite/zShell_Test.py

"""
Comprehensive test suite for the zShell subsystem.

Tests cover:
- Initialization and configuration
- Command execution (parsed commands, special commands)
- Interactive shell mode (REPL, history, prompts)
- Wizard canvas mode (buffer management, execution)
- Help system (welcome message, command help, tips)
- Result display (errors, success, JSON)
- Error handling and edge cases
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zShell.zShell import zShell
from zCLI.subsystems.zShell.zShell_modules.zShell_interactive import InteractiveShell
from zCLI.subsystems.zShell.zShell_modules.zShell_executor import CommandExecutor
from zCLI.subsystems.zShell.zShell_modules.zShell_help import HelpSystem


class TestzShellInitialization(unittest.TestCase):
    """Test zShell initialization and configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
    
    def test_initialization_success(self):
        """Test successful zShell initialization."""
        shell = zShell(self.mock_zcli)
        
        self.assertEqual(shell.zcli, self.mock_zcli)
        self.assertEqual(shell.logger, self.mock_zcli.logger)
        self.assertEqual(shell.display, self.mock_zcli.display)
        self.assertEqual(shell.mycolor, "SHELL")
        self.assertIsNotNone(shell.interactive)
        self.assertIsNotNone(shell.executor)
        self.assertIsNotNone(shell.help_system)
    
    def test_initialization_displays_ready_message(self):
        """Test that initialization displays ready message."""
        shell = zShell(self.mock_zcli)
        
        self.mock_zcli.display.zDeclare.assert_called_with(
            "zShell Ready",
            color="SHELL",
            indent=0,
            style="full"
        )
    
    def test_has_required_methods(self):
        """Test that zShell has all required methods."""
        shell = zShell(self.mock_zcli)
        
        self.assertTrue(hasattr(shell, 'run_shell'))
        self.assertTrue(hasattr(shell, 'execute_command'))
        self.assertTrue(hasattr(shell, 'show_help'))
        self.assertTrue(callable(shell.run_shell))
        self.assertTrue(callable(shell.execute_command))
        self.assertTrue(callable(shell.show_help))


class TestCommandExecutor(unittest.TestCase):
    """Test CommandExecutor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.executor = CommandExecutor(self.mock_zcli)
    
    def test_execute_empty_command(self):
        """Test executing empty command returns None."""
        result = self.executor.execute("")
        self.assertIsNone(result)
        
        result = self.executor.execute("   ")
        self.assertIsNone(result)
    
    def test_execute_parsed_command(self):
        """Test executing a parsed command."""
        self.mock_zcli.zparser.parse_command.return_value = {
            "type": "session",
            "action": "info",
            "args": []
        }
        self.mock_zcli.display.handle.return_value = None
        self.mock_zcli.display.zSession.return_value = None
        
        result = self.executor.execute("session info")
        
        # Session info returns None (display.zSession returns None)
        self.assertIsNone(result)
    
    def test_execute_command_with_error(self):
        """Test executing command that returns error."""
        self.mock_zcli.zparser.parse_command.return_value = {
            "error": "Invalid command"
        }
        
        result = self.executor.execute("invalid command")
        
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid command")
    
    def test_execute_unknown_command_type(self):
        """Test executing unknown command type."""
        self.mock_zcli.zparser.parse_command.return_value = {
            "type": "unknown_type"
        }
        
        result = self.executor.execute("unknown command")
        
        self.assertIn("error", result)
        self.assertIn("Unknown command type", result["error"])


class TestWizardMode(unittest.TestCase):
    """Test wizard canvas mode functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.wizard = Mock()
        self.executor = CommandExecutor(self.mock_zcli)
    
    def test_wizard_show_empty_buffer(self):
        """Test showing empty wizard buffer."""
        result = self.executor._wizard_show()
        
        self.assertEqual(result["status"], "empty")
        self.mock_zcli.display.zDeclare.assert_called_with(
            "Wizard buffer empty",
            color="INFO",
            indent=0,
            style="single"
        )
    
    def test_wizard_show_with_lines(self):
        """Test showing wizard buffer with lines."""
        self.mock_zcli.session["wizard_mode"]["lines"] = ["line1", "line2", "line3"]
        
        result = self.executor._wizard_show()
        
        self.assertEqual(result["status"], "shown")
        self.assertEqual(result["lines"], 3)
        # Should display header + 3 lines
        self.assertEqual(self.mock_zcli.display.zDeclare.call_count, 4)
    
    def test_wizard_clear(self):
        """Test clearing wizard buffer."""
        self.mock_zcli.session["wizard_mode"]["lines"] = ["line1", "line2"]
        
        result = self.executor._wizard_clear()
        
        self.assertEqual(result["status"], "cleared")
        self.assertEqual(result["lines"], 2)
        self.assertEqual(len(self.mock_zcli.session["wizard_mode"]["lines"]), 0)
    
    def test_wizard_stop(self):
        """Test stopping wizard mode."""
        self.mock_zcli.session["wizard_mode"]["active"] = True
        self.mock_zcli.session["wizard_mode"]["lines"] = ["line1", "line2"]
        
        result = self.executor._wizard_stop()
        
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["lines_discarded"], 2)
        self.assertFalse(self.mock_zcli.session["wizard_mode"]["active"])
        self.assertEqual(len(self.mock_zcli.session["wizard_mode"]["lines"]), 0)
    
    def test_wizard_run_empty_buffer(self):
        """Test running empty wizard buffer."""
        result = self.executor._wizard_run()
        
        self.assertIn("error", result)
        self.assertEqual(result["error"], "empty_buffer")
    
    def test_wizard_run_yaml_format(self):
        """Test running wizard buffer with YAML format."""
        self.mock_zcli.session["wizard_mode"]["lines"] = [
            "step1: command1",
            "step2: command2"
        ]
        self.mock_zcli.wizard.handle.return_value = ["result1", "result2"]
        
        result = self.executor._wizard_run()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["format"], "yaml")
        self.mock_zcli.wizard.handle.assert_called_once()
    
    def test_wizard_run_shell_commands(self):
        """Test running wizard buffer with shell commands."""
        self.mock_zcli.session["wizard_mode"]["lines"] = [
            "data read users",
            "data read posts"
        ]
        self.mock_zcli.wizard.handle.return_value = ["result1", "result2"]
        
        result = self.executor._wizard_run()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["format"], "commands")
        self.mock_zcli.wizard.handle.assert_called_once()
    
    def test_wizard_run_clears_buffer_on_success(self):
        """Test that wizard run clears buffer on success."""
        self.mock_zcli.session["wizard_mode"]["lines"] = ["command1"]
        self.mock_zcli.wizard.handle.return_value = ["result"]
        
        self.executor._wizard_run()
        
        self.assertEqual(len(self.mock_zcli.session["wizard_mode"]["lines"]), 0)
    
    def test_wizard_run_handles_exception(self):
        """Test wizard run handles exceptions."""
        self.mock_zcli.session["wizard_mode"]["lines"] = ["command1"]
        self.mock_zcli.wizard.handle.side_effect = Exception("Test error")
        
        result = self.executor._wizard_run()
        
        self.assertIn("error", result)


class TestInteractiveShell(unittest.TestCase):
    """Test InteractiveShell functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.shell = InteractiveShell(self.mock_zcli)
    
    def test_get_prompt_normal_mode(self):
        """Test getting prompt in normal mode."""
        prompt = self.shell._get_prompt()
        
        self.assertIn("zCLI", prompt)
        self.assertIn(">", prompt)
    
    def test_get_prompt_wizard_mode(self):
        """Test getting prompt in wizard mode."""
        self.mock_zcli.session["wizard_mode"]["active"] = True
        
        prompt = self.shell._get_prompt()
        
        self.assertEqual(prompt, "> ")
    
    def test_handle_special_command_exit(self):
        """Test handling exit command."""
        result = self.shell._handle_special_commands("exit")
        
        self.assertTrue(result)
        self.assertFalse(self.shell.running)
    
    def test_handle_special_command_quit(self):
        """Test handling quit command."""
        result = self.shell._handle_special_commands("quit")
        
        self.assertTrue(result)
        self.assertFalse(self.shell.running)
    
    def test_handle_special_command_help(self):
        """Test handling help command."""
        with patch.object(self.shell.help_system, 'show_help') as mock_help:
            result = self.shell._handle_special_commands("help")
        
        self.assertTrue(result)
        mock_help.assert_called_once()
    
    def test_handle_special_command_tips(self):
        """Test handling tips command."""
        result = self.shell._handle_special_commands("tips")
        
        self.assertTrue(result)
        self.mock_zcli.display.block.assert_called_once()
    
    def test_display_result_with_error(self):
        """Test displaying result with error."""
        result = {"error": "Test error message"}
        
        self.shell._display_result(result)
        
        self.mock_zcli.display.zDeclare.assert_called_with(
            "Error: Test error message",
            color="ERROR",
            indent=0,
            style="single"
        )
    
    def test_display_result_with_success(self):
        """Test displaying result with success."""
        result = {"success": "Operation completed"}
        
        self.shell._display_result(result)
        
        self.mock_zcli.display.zDeclare.assert_called_with(
            "Operation completed",
            color="SUCCESS",
            indent=0,
            style="single"
        )
    
    def test_display_result_with_success_and_note(self):
        """Test displaying result with success and note."""
        result = {"success": "Operation completed", "note": "Additional info"}
        
        self.shell._display_result(result)
        
        self.assertEqual(self.mock_zcli.display.zDeclare.call_count, 2)
    
    def test_display_result_with_dict(self):
        """Test displaying dict result as JSON."""
        result = {"data": "value", "count": 42}
        
        self.shell._display_result(result)
        
        self.mock_zcli.display.json.assert_called_once_with(result)
    
    def test_display_result_with_string(self):
        """Test displaying string result."""
        result = "Simple string result"
        
        self.shell._display_result(result)
        
        self.mock_zcli.display.zDeclare.assert_called_with(
            "Simple string result",
            color="DATA",
            indent=0,
            style="single"
        )
    
    def test_display_result_with_none(self):
        """Test displaying None result (should do nothing)."""
        self.shell._display_result(None)
        
        self.mock_zcli.display.zDeclare.assert_not_called()
        self.mock_zcli.display.json.assert_not_called()


class TestHelpSystem(unittest.TestCase):
    """Test HelpSystem functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.help_system = HelpSystem()
    
    def test_get_welcome_message(self):
        """Test getting welcome message."""
        message = self.help_system.get_welcome_message()
        
        self.assertIsInstance(message, str)
        self.assertIn("zCLI", message)
        self.assertGreater(len(message), 50)
    
    def test_get_quick_tips(self):
        """Test getting quick tips."""
        tips = self.help_system.get_quick_tips()
        
        self.assertIsInstance(tips, str)
        self.assertGreater(len(tips), 50)
    
    def test_show_help_displays_content(self):
        """Test that show_help displays content."""
        with patch('builtins.print') as mock_print:
            self.help_system.show_help()
        
        mock_print.assert_called()
    
    def test_show_command_help_with_valid_command(self):
        """Test showing help for valid command."""
        with patch('builtins.print') as mock_print:
            self.help_system.show_command_help("data")
        
        mock_print.assert_called()
    
    def test_show_command_help_with_invalid_command(self):
        """Test showing help for invalid command."""
        with patch('builtins.print') as mock_print:
            self.help_system.show_command_help("nonexistent_command")
        
        mock_print.assert_called()


class TestzShellIntegration(unittest.TestCase):
    """Test zShell integration with other subsystems."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
    
    def test_run_shell_calls_interactive(self):
        """Test that run_shell calls interactive.run()."""
        shell = zShell(self.mock_zcli)
        
        with patch.object(shell.interactive, 'run') as mock_run:
            mock_run.return_value = "shell_result"
            result = shell.run_shell()
        
        self.assertEqual(result, "shell_result")
        mock_run.assert_called_once()
    
    def test_execute_command_calls_executor(self):
        """Test that execute_command calls executor.execute()."""
        shell = zShell(self.mock_zcli)
        
        with patch.object(shell.executor, 'execute') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            result = shell.execute_command("test command")
        
        self.assertEqual(result, {"status": "success"})
        mock_execute.assert_called_once_with("test command")
    
    def test_show_help_calls_help_system(self):
        """Test that show_help calls help_system.show_help()."""
        shell = zShell(self.mock_zcli)
        
        with patch.object(shell.help_system, 'show_help') as mock_help:
            shell.show_help()
        
        mock_help.assert_called_once()


class TestNewCommands(unittest.TestCase):
    """Test new shell commands (history, echo, ls, cd, pwd, alias)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None},
            "command_history": [],
            "aliases": {},
            "zWorkspace": "/test/workspace"
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.info = Mock()
        self.mock_zcli.display.success = Mock()
        self.mock_zcli.display.error = Mock()
        self.mock_zcli.display.text = Mock()
        self.mock_zcli.display.zDeclare = Mock()
        self.mock_zcli.zparser = Mock()
    
    def test_history_command_show(self):
        """Test history command shows command history."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.history_executor import execute_history
        
        self.mock_zcli.session["command_history"] = ["cmd1", "cmd2", "cmd3"]
        parsed = {"action": "show", "args": [], "options": {}}
        
        result = execute_history(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total"], 3)
    
    def test_history_command_clear(self):
        """Test history clear command."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.history_executor import execute_history
        
        self.mock_zcli.session["command_history"] = ["cmd1", "cmd2"]
        parsed = {"action": "clear", "args": [], "options": {}}
        
        result = execute_history(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "cleared")
        self.assertEqual(len(self.mock_zcli.session["command_history"]), 0)
    
    def test_echo_command_simple(self):
        """Test echo command with simple message."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.echo_executor import execute_echo
        
        parsed = {"action": "echo", "args": ["Hello", "World"], "options": {}}
        
        result = execute_echo(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "Hello World")
        self.mock_zcli.display.text.assert_called_once_with("Hello World")
    
    def test_echo_command_with_variable(self):
        """Test echo command with variable expansion."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.echo_executor import execute_echo
        
        parsed = {"action": "echo", "args": ["$zWorkspace"], "options": {}}
        
        result = execute_echo(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("/test/workspace", result["output"])
    
    def test_pwd_command(self):
        """Test pwd command shows working directory."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.cd_executor import execute_pwd
        
        parsed = {"action": "pwd", "args": [], "options": {}}
        
        result = execute_pwd(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("path", result)
    
    def test_alias_command_list(self):
        """Test alias command lists aliases."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.alias_executor import execute_alias
        
        self.mock_zcli.session["aliases"] = {"ll": "ls --long"}
        parsed = {"action": "list", "args": [], "options": {}}
        
        result = execute_alias(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 1)
    
    def test_alias_command_create(self):
        """Test alias command creates new alias."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.alias_executor import execute_alias
        
        parsed = {"action": "create", "args": ["ll=\"ls --long\""], "options": {}}
        
        result = execute_alias(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["name"], "ll")
        self.assertEqual(self.mock_zcli.session["aliases"]["ll"], "ls --long")
    
    def test_alias_command_remove(self):
        """Test alias command removes alias."""
        from zCLI.subsystems.zShell.zShell_modules.executor_commands.alias_executor import execute_alias
        
        self.mock_zcli.session["aliases"] = {"ll": "ls --long"}
        parsed = {"action": "create", "args": ["ll"], "options": {"remove": True}}
        
        result = execute_alias(self.mock_zcli, parsed)
        
        self.assertEqual(result["status"], "removed")
        self.assertNotIn("ll", self.mock_zcli.session["aliases"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "wizard_mode": {"active": False, "lines": [], "format": None}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
    
    def test_executor_handles_parse_exception(self):
        """Test executor handles parsing exceptions."""
        executor = CommandExecutor(self.mock_zcli)
        self.mock_zcli.zparser.parse_command.side_effect = Exception("Parse error")
        
        result = executor.execute("bad command")
        
        self.assertIn("error", result)
    
    def test_wizard_mode_with_invalid_yaml(self):
        """Test wizard mode with invalid YAML."""
        executor = CommandExecutor(self.mock_zcli)
        self.mock_zcli.session["wizard_mode"]["lines"] = [
            "invalid: yaml: syntax: error:"
        ]
        self.mock_zcli.wizard.handle.return_value = ["result"]
        
        # Should fallback to shell commands
        result = executor._wizard_run()
        
        self.assertEqual(result["format"], "commands")
    
    def test_display_result_with_other_types(self):
        """Test displaying result with other types (int, list, etc)."""
        shell = InteractiveShell(self.mock_zcli)
        
        # Test with integer
        shell._display_result(42)
        self.mock_zcli.display.json.assert_called_with({"result": 42})
        
        # Test with list
        self.mock_zcli.display.json.reset_mock()
        shell._display_result([1, 2, 3])
        self.mock_zcli.display.json.assert_called_with({"result": [1, 2, 3]})


def run_tests(verbose=False):
    """Run all zShell tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzShellInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestWizardMode))
    suite.addTests(loader.loadTestsFromTestCase(TestInteractiveShell))
    suite.addTests(loader.loadTestsFromTestCase(TestHelpSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestzShellIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestNewCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    import sys
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

