# zTestSuite/zOpen_Test.py

"""
Comprehensive test suite for the zOpen subsystem.

Tests cover:
- Initialization and configuration
- File opening (HTML, text, unsupported types)
- URL opening (http, https, www)
- zPath resolution (workspace-relative, absolute)
- Hook execution (onSuccess, onFail)
- Error handling and edge cases
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zCLI.subsystems.zOpen.zOpen import zOpen


class TestzOpenInitialization(unittest.TestCase):
    """Test zOpen initialization and configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {
                "ide": "code",
                "browser": "chrome"
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
    
    def test_initialization_success(self):
        """Test successful zOpen initialization."""
        with patch('builtins.print'):
            zopen = zOpen(self.mock_zcli)
        
        self.assertEqual(zopen.zcli, self.mock_zcli)
        self.assertEqual(zopen.session, self.mock_zcli.session)
        self.assertEqual(zopen.mycolor, "ZOPEN")
        self.mock_zcli.display.zDeclare.assert_called_once()
    
    def test_initialization_no_zcli(self):
        """Test initialization fails without zcli."""
        with self.assertRaises(ValueError) as context:
            zOpen(None)
        self.assertIn("requires a zCLI instance", str(context.exception))
    
    def test_initialization_invalid_zcli(self):
        """Test initialization fails with invalid zcli."""
        invalid_zcli = Mock(spec=[])
        with self.assertRaises(ValueError) as context:
            zOpen(invalid_zcli)
        self.assertIn("missing 'session' attribute", str(context.exception))


class TestzOpenFileHandling(unittest.TestCase):
    """Test file opening operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {"ide": "code", "browser": "chrome"}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.webbrowser.open')
    def test_open_html_file_success(self, mock_webbrowser, mock_exists):
        """Test opening HTML file successfully."""
        mock_exists.return_value = True
        mock_webbrowser.return_value = True
        
        result = self.zopen._open_html("/test/file.html")
        
        self.assertEqual(result, "zBack")
        mock_webbrowser.assert_called_once_with("file:///test/file.html")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.webbrowser.open')
    def test_open_html_file_browser_fails(self, mock_webbrowser, mock_exists):
        """Test HTML file opening when browser fails."""
        mock_exists.return_value = True
        mock_webbrowser.return_value = False
        
        result = self.zopen._open_html("/test/file.html")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.subprocess.run')
    @patch('zCLI.subsystems.zOpen.zOpen.os.name', 'posix')
    def test_open_text_file_success(self, mock_subprocess, mock_exists):
        """Test opening text file with IDE."""
        mock_exists.return_value = True
        
        result = self.zopen._open_text("/test/file.py")
        
        self.assertEqual(result, "zBack")
        mock_subprocess.assert_called_once_with(["code", "/test/file.py"], check=False)
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.subprocess.run')
    def test_open_text_file_ide_fails(self, mock_subprocess, mock_exists):
        """Test text file opening when IDE fails."""
        mock_exists.return_value = True
        mock_subprocess.side_effect = Exception("IDE not found")
        
        # Mock file reading for fallback
        with patch('builtins.open', mock_open(read_data="test content")):
            result = self.zopen._open_text("/test/file.py")
        
        self.assertEqual(result, "zBack")
        self.mock_zcli.display.block.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    def test_open_file_not_found_no_dialog(self, mock_exists):
        """Test opening non-existent file without dialog."""
        mock_exists.return_value = False
        self.zopen.dialog = None
        
        result = self.zopen._open_file("/test/nonexistent.txt")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_open_file_not_found_create_with_dialog(self, mock_file, mock_makedirs, mock_exists):
        """Test creating file when not found with dialog."""
        mock_exists.side_effect = [False, False, True]  # Not exists, then exists after creation
        self.zopen.dialog.handle.return_value = {"action": "Create file"}
        
        with patch.object(self.zopen, '_open_html', return_value="zBack"):
            result = self.zopen._open_file("/test/newfile.html")
        
        mock_file.assert_called_once_with("/test/newfile.html", 'w', encoding='utf-8')
        self.assertEqual(result, "zBack")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    def test_open_file_not_found_cancel_dialog(self, mock_exists):
        """Test canceling file creation in dialog."""
        mock_exists.return_value = False
        self.zopen.dialog.handle.return_value = {"action": "Cancel"}
        
        result = self.zopen._open_file("/test/newfile.txt")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.exists')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.splitext')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.getsize')
    def test_open_unsupported_file_type(self, mock_getsize, mock_splitext, mock_exists):
        """Test opening file with unsupported extension."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".xyz")
        
        result = self.zopen._open_file("/test/file.xyz")
        
        self.assertEqual(result, "stop")
    
    @patch('builtins.open', mock_open(read_data="short content"))
    def test_display_file_content_short(self):
        """Test displaying short file content."""
        result = self.zopen._display_file_content("/test/file.txt")
        
        self.assertEqual(result, "zBack")
        self.mock_zcli.display.block.assert_called_once_with("short content")
    
    @patch('builtins.open', mock_open(read_data="x" * 2000))
    def test_display_file_content_long(self):
        """Test displaying long file content (truncated)."""
        result = self.zopen._display_file_content("/test/file.txt")
        
        self.assertEqual(result, "zBack")
        # Should truncate to 1000 chars
        call_args = self.mock_zcli.display.block.call_args[0][0]
        self.assertEqual(len(call_args), 1003)  # 1000 + "..."


class TestzOpenURLHandling(unittest.TestCase):
    """Test URL opening operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {"browser": "chrome"}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch('zCLI.subsystems.zOpen.zOpen.webbrowser.open')
    def test_open_url_success(self, mock_webbrowser):
        """Test opening URL successfully."""
        mock_webbrowser.return_value = True
        
        result = self.zopen._open_url("https://example.com")
        
        self.assertEqual(result, "zBack")
    
    @patch('zCLI.subsystems.zOpen.zOpen.webbrowser.open')
    def test_open_url_browser_fails(self, mock_webbrowser):
        """Test URL opening when browser fails."""
        mock_webbrowser.return_value = False
        
        result = self.zopen._open_url("https://example.com")
        
        self.assertEqual(result, "zBack")  # Falls back to displaying URL info
        self.mock_zcli.display.line.assert_called()
    
    @patch('zCLI.shutil.which')
    @patch('zCLI.subsystems.zOpen.zOpen.subprocess.run')
    def test_open_url_specific_browser(self, mock_subprocess, mock_which):
        """Test opening URL with specific browser."""
        mock_which.return_value = "/usr/bin/chrome"
        
        result = self.zopen._open_url_browser("https://example.com", "chrome")
        
        self.assertEqual(result, "zBack")
        mock_subprocess.assert_called_once_with(["chrome", "https://example.com"], check=False)
    
    @patch('zCLI.subsystems.zOpen.zOpen.webbrowser.open')
    def test_open_url_unknown_browser(self, mock_webbrowser):
        """Test opening URL with unknown browser (fallback to default)."""
        mock_webbrowser.return_value = True
        
        result = self.zopen._open_url_browser("https://example.com", "unknown")
        
        self.assertEqual(result, "zBack")
        mock_webbrowser.assert_called_once()
    
    def test_display_url_fallback(self):
        """Test displaying URL information as fallback."""
        result = self.zopen._display_url_fallback("https://example.com")
        
        self.assertEqual(result, "zBack")
        self.mock_zcli.display.line.assert_called()


class TestzOpenPathResolution(unittest.TestCase):
    """Test zPath resolution operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.join')
    def test_resolve_workspace_relative_path(self, mock_join, mock_abspath):
        """Test resolving workspace-relative zPath (@)."""
        mock_join.return_value = "/test/workspace/dir/file.txt"
        mock_abspath.return_value = "/test/workspace/dir/file.txt"
        
        result = self.zopen._resolve_zpath("@.dir.file.txt")
        
        self.assertEqual(result, "/test/workspace/dir/file.txt")
        mock_join.assert_called_once_with("/test/workspace", "dir", "file.txt")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.join')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.sep', '/')
    def test_resolve_absolute_path(self, mock_join, mock_abspath):
        """Test resolving absolute zPath (~)."""
        mock_join.return_value = "/home/user/file.txt"
        mock_abspath.return_value = "/home/user/file.txt"
        
        result = self.zopen._resolve_zpath("~.home.user.file.txt")
        
        self.assertEqual(result, "/home/user/file.txt")
    
    def test_resolve_path_no_workspace(self):
        """Test resolving workspace path when no workspace is set."""
        self.zopen.session["zWorkspace"] = None
        
        result = self.zopen._resolve_zpath("@.dir.file.txt")
        
        self.assertIsNone(result)
    
    def test_resolve_invalid_path(self):
        """Test resolving invalid zPath (too few parts)."""
        result = self.zopen._resolve_zpath("@.file")
        
        self.assertIsNone(result)
    
    @patch.object(zOpen, '_open_file')
    def test_open_zpath_success(self, mock_open_file):
        """Test opening file via zPath."""
        mock_open_file.return_value = "zBack"
        
        with patch.object(self.zopen, '_resolve_zpath', return_value="/test/file.txt"):
            result = self.zopen._open_zpath("@.test.file.txt")
        
        self.assertEqual(result, "zBack")
        mock_open_file.assert_called_once_with("/test/file.txt")
    
    def test_open_zpath_resolution_fails(self):
        """Test opening file when zPath resolution fails."""
        with patch.object(self.zopen, '_resolve_zpath', return_value=None):
            result = self.zopen._open_zpath("@.invalid.path")
        
        self.assertEqual(result, "stop")


class TestzOpenHandleMethod(unittest.TestCase):
    """Test main handle method and routing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch.object(zOpen, '_open_url')
    def test_handle_http_url(self, mock_open_url):
        """Test handling HTTP URL."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(http://example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("http://example.com")
    
    @patch.object(zOpen, '_open_url')
    def test_handle_https_url(self, mock_open_url):
        """Test handling HTTPS URL."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(https://example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("https://example.com")
    
    @patch.object(zOpen, '_open_url')
    def test_handle_www_url(self, mock_open_url):
        """Test handling www URL (adds https)."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(www.example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("https://www.example.com")
    
    @patch.object(zOpen, '_open_zpath')
    def test_handle_workspace_path(self, mock_open_zpath):
        """Test handling workspace-relative path."""
        mock_open_zpath.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(@.dir.file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_open_zpath.assert_called_once_with("@.dir.file.txt")
    
    @patch.object(zOpen, '_open_zpath')
    def test_handle_absolute_path(self, mock_open_zpath):
        """Test handling absolute path."""
        mock_open_zpath.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(~.home.user.file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_open_zpath.assert_called_once_with("~.home.user.file.txt")
    
    @patch.object(zOpen, '_open_file')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser')
    def test_handle_local_file(self, mock_expanduser, mock_abspath, mock_open_file):
        """Test handling local file path."""
        mock_expanduser.return_value = "/test/file.txt"
        mock_abspath.return_value = "/test/file.txt"
        mock_open_file.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(/test/file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_open_file.assert_called_once_with("/test/file.txt")
    
    @patch.object(zOpen, '_open_file')
    def test_handle_dict_format(self, mock_open_file):
        """Test handling dict format input."""
        mock_open_file.return_value = "zBack"
        
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                result = self.zopen.handle({
                    "zOpen": {
                        "path": "/test/file.txt"
                    }
                })
        
        self.assertEqual(result, "zBack")
    
    @patch.object(zOpen, '_open_file')
    def test_handle_with_on_success_hook(self, mock_open_file):
        """Test handling with onSuccess hook."""
        mock_open_file.return_value = "zBack"
        self.mock_zcli.zfunc.handle.return_value = "hook_result"
        
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                result = self.zopen.handle({
                    "zOpen": {
                        "path": "/test/file.txt",
                        "onSuccess": "zFunc(@utils.success_handler)"
                    }
                })
        
        self.assertEqual(result, "hook_result")
        self.mock_zcli.zfunc.handle.assert_called_once_with("zFunc(@utils.success_handler)")
    
    @patch.object(zOpen, '_open_file')
    def test_handle_with_on_fail_hook(self, mock_open_file):
        """Test handling with onFail hook."""
        mock_open_file.return_value = "stop"
        self.mock_zcli.zfunc.handle.return_value = "hook_result"
        
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                result = self.zopen.handle({
                    "zOpen": {
                        "path": "/test/file.txt",
                        "onFail": "zFunc(@utils.fail_handler)"
                    }
                })
        
        self.assertEqual(result, "hook_result")
        self.mock_zcli.zfunc.handle.assert_called_once_with("zFunc(@utils.fail_handler)")
    
    @patch.object(zOpen, '_open_file')
    def test_handle_no_hook_execution_on_success(self, mock_open_file):
        """Test that hooks don't execute when not provided."""
        mock_open_file.return_value = "zBack"
        
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                result = self.zopen.handle("zOpen(/test/file.txt)")
        
        self.assertEqual(result, "zBack")
        self.mock_zcli.zfunc.handle.assert_not_called()


class TestzOpenEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zWorkspace": "/test/workspace",
            "zMachine": {}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    def test_handle_empty_path(self):
        """Test handling empty path."""
        with patch.object(self.zopen, '_open_file', return_value="stop") as mock_open:
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value=""):
                with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value=""):
                    result = self.zopen.handle("zOpen()")
        
        self.assertEqual(result, "stop")
    
    def test_handle_path_with_quotes(self):
        """Test handling path with quotes."""
        with patch.object(self.zopen, '_open_file', return_value="zBack") as mock_open:
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
                with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                    result = self.zopen.handle('zOpen("/test/file.txt")')
        
        self.assertEqual(result, "zBack")
    
    @patch('builtins.open', side_effect=Exception("Read error"))
    def test_display_file_content_read_error(self, mock_file):
        """Test handling file read error."""
        result = self.zopen._display_file_content("/test/file.txt")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath')
    def test_resolve_zpath_exception(self, mock_abspath):
        """Test handling exception during zPath resolution."""
        mock_abspath.side_effect = Exception("Path error")
        
        result = self.zopen._resolve_zpath("@.test.file.txt")
        
        self.assertIsNone(result)


def run_tests(verbose=False):
    """Run all zOpen tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenFileHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenURLHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenPathResolution))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenHandleMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    import sys
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    result = run_tests(verbose=verbose)
    sys.exit(0 if result.wasSuccessful() else 1)

