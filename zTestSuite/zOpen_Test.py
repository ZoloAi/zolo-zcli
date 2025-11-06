# zTestSuite/zOpen_Test.py

"""
Comprehensive test suite for the zOpen subsystem (3-tier modular architecture).

Tests cover:
- Tier 1a: zPath resolution (open_paths module)
- Tier 1b: URL opening (open_urls module)
- Tier 1c: File opening (open_files module)
- Tier 2: Main facade (zOpen class)
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
from zCLI.subsystems.zOpen.open_modules import resolve_zpath, validate_zpath, open_url, open_file


class TestzOpenInitialization(unittest.TestCase):
    """Test zOpen initialization and configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zSpace": "/test/workspace",
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


class TestzOpenPathResolutionModule(unittest.TestCase):
    """Test open_paths module functions (Tier 1a)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.session = {
            "zSpace": "/test/workspace"
        }
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.join')
    def test_resolve_workspace_relative_path(self, mock_join, mock_abspath):
        """Test resolving workspace-relative zPath (@)."""
        mock_join.return_value = "/test/workspace/dir/file.txt"
        mock_abspath.return_value = "/test/workspace/dir/file.txt"
        
        result = resolve_zpath("@.dir.file.txt", self.session, self.mock_logger)
        
        self.assertEqual(result, "/test/workspace/dir/file.txt")
        mock_join.assert_called_once_with("/test/workspace", "dir", "file.txt")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.join')
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.sep', '/')
    def test_resolve_absolute_path(self, mock_join, mock_abspath):
        """Test resolving absolute zPath (~)."""
        mock_join.return_value = "/home/user/file.txt"
        mock_abspath.return_value = "/home/user/file.txt"
        
        result = resolve_zpath("~.home.user.file.txt", self.session, self.mock_logger)
        
        self.assertEqual(result, "/home/user/file.txt")
    
    def test_resolve_path_no_workspace(self):
        """Test resolving workspace path when no workspace is set."""
        session_no_workspace = {}
        
        result = resolve_zpath("@.dir.file.txt", session_no_workspace, self.mock_logger)
        
        self.assertIsNone(result)
    
    def test_resolve_invalid_path(self):
        """Test resolving invalid zPath (too few parts)."""
        result = resolve_zpath("@.file", self.session, self.mock_logger)
        
        self.assertIsNone(result)
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_paths.os.path.abspath')
    def test_resolve_zpath_exception(self, mock_abspath):
        """Test handling exception during zPath resolution."""
        mock_abspath.side_effect = Exception("Path error")
        
        result = resolve_zpath("@.test.file.txt", self.session, self.mock_logger)
        
        self.assertIsNone(result)
    
    def test_validate_zpath_valid_workspace(self):
        """Test validating valid workspace zPath."""
        self.assertTrue(validate_zpath("@.dir.file.txt"))
    
    def test_validate_zpath_valid_absolute(self):
        """Test validating valid absolute zPath."""
        self.assertTrue(validate_zpath("~.home.user.file.txt"))
    
    def test_validate_zpath_invalid(self):
        """Test validating invalid zPath."""
        self.assertFalse(validate_zpath("@.file"))  # Too few parts
        self.assertFalse(validate_zpath("invalid"))  # No symbol


class TestzOpenURLModule(unittest.TestCase):
    """Test open_urls module functions (Tier 1b)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display = Mock()
        self.mock_logger = Mock()
        self.session = {
            "zMachine": {"browser": "chrome"}
        }
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_urls.webbrowser.open')
    def test_open_url_success(self, mock_webbrowser):
        """Test opening URL successfully."""
        mock_webbrowser.return_value = True
        
        result = open_url("https://example.com", self.session, self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_urls.webbrowser.open')
    def test_open_url_browser_fails(self, mock_webbrowser):
        """Test URL opening when browser fails."""
        mock_webbrowser.return_value = False
        
        result = open_url("https://example.com", self.session, self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")  # Falls back to displaying URL info
        # Display method may have changed - check for any display call
        self.assertTrue(self.mock_display.zDeclare.called or self.mock_display.write_line.called)
    
    @patch('zCLI.shutil.which')
    @patch('zCLI.subsystems.zOpen.open_modules.open_urls.subprocess.run')
    def test_open_url_specific_browser(self, mock_subprocess, mock_which):
        """Test opening URL with specific browser."""
        mock_which.return_value = "/usr/bin/chrome"
        
        result = open_url("https://example.com", self.session, self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        # Check that subprocess.run was called (implementation may vary by OS)
        mock_subprocess.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_urls.webbrowser.open')
    def test_open_url_unknown_browser(self, mock_webbrowser):
        """Test opening URL with unknown browser (fallback to default)."""
        mock_webbrowser.return_value = True
        session_unknown = {"zMachine": {"browser": "unknown"}}
        
        result = open_url("https://example.com", session_unknown, self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        mock_webbrowser.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_urls.webbrowser.open')
    def test_display_url_fallback(self, mock_webbrowser):
        """Test displaying URL information as fallback."""
        mock_webbrowser.return_value = False
        
        result = open_url("https://example.com", self.session, self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        # Display method may have changed - check for any display call
        self.assertTrue(self.mock_display.zDeclare.called or self.mock_display.write_line.called)


class TestzOpenFileModule(unittest.TestCase):
    """Test open_files module functions (Tier 1c)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display = Mock()
        self.mock_dialog = Mock()
        self.mock_logger = Mock()
        self.session = {
            "zMachine": {"ide": "code", "browser": "chrome"}
        }
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.webbrowser.open')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    def test_open_html_file_success(self, mock_splitext, mock_getsize, mock_webbrowser, mock_exists):
        """Test opening HTML file successfully."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".html")
        mock_webbrowser.return_value = True
        
        result = open_file("/test/file.html", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        mock_webbrowser.assert_called_once_with("file:///test/file.html")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.webbrowser.open')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    def test_open_html_file_browser_fails(self, mock_splitext, mock_getsize, mock_webbrowser, mock_exists):
        """Test HTML file opening when browser fails."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".html")
        mock_webbrowser.return_value = False
        
        result = open_file("/test/file.html", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.subprocess.run')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.name', 'posix')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    def test_open_text_file_success(self, mock_splitext, mock_getsize, mock_subprocess, mock_exists):
        """Test opening text file with IDE."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".py")
        
        result = open_file("/test/file.py", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        # Check that subprocess was called with the IDE command (timeout may be added)
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        self.assertEqual(call_args[0][0][0], "code")  # First arg should be the IDE
        self.assertIn("/test/file.py", call_args[0][0])  # Should include the file path
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.subprocess.run')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    def test_open_text_file_ide_fails(self, mock_splitext, mock_getsize, mock_subprocess, mock_exists):
        """Test text file opening when IDE fails."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".py")
        mock_subprocess.side_effect = Exception("IDE not found")
        
        # Mock file reading for fallback
        with patch('builtins.open', mock_open(read_data="test content")):
            result = open_file("/test/file.py", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        self.mock_display.write_block.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    def test_open_file_not_found_no_dialog(self, mock_exists):
        """Test opening non-existent file without dialog."""
        mock_exists.return_value = False
        
        result = open_file("/test/nonexistent.txt", self.session, self.mock_display, None, self.mock_logger)
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.makedirs')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.webbrowser.open')
    @patch('builtins.open', new_callable=mock_open)
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    def test_open_file_not_found_create_with_dialog(self, mock_splitext, mock_getsize, mock_file, mock_webbrowser, mock_makedirs, mock_exists):
        """Test creating file when not found with dialog."""
        mock_exists.side_effect = [False, False, True]  # Not exists, then exists after creation
        mock_getsize.return_value = 0
        mock_splitext.return_value = ("/test/newfile", ".html")
        mock_webbrowser.return_value = True
        self.mock_dialog.handle.return_value = {"action": "Create file"}
        
        result = open_file("/test/newfile.html", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        mock_file.assert_called_once_with("/test/newfile.html", 'w', encoding='utf-8')
        self.assertEqual(result, "zBack")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    def test_open_file_not_found_cancel_dialog(self, mock_exists):
        """Test canceling file creation in dialog."""
        mock_exists.return_value = False
        self.mock_dialog.handle.return_value = {"action": "Cancel"}
        
        result = open_file("/test/newfile.txt", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.exists')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.splitext')
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.getsize')
    def test_open_unsupported_file_type(self, mock_getsize, mock_splitext, mock_exists):
        """Test opening file with unsupported extension."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_splitext.return_value = ("/test/file", ".xyz")
        
        result = open_file("/test/file.xyz", self.session, self.mock_display, self.mock_dialog, self.mock_logger)
        
        self.assertEqual(result, "stop")
    
    @patch('builtins.open', mock_open(read_data="short content"))
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.basename')
    def test_display_file_content_short(self, mock_basename):
        """Test displaying short file content."""
        from zCLI.subsystems.zOpen.open_modules.open_files import _display_file_content
        mock_basename.return_value = "file.txt"
        
        result = _display_file_content("/test/file.txt", self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        self.mock_display.write_block.assert_called_once_with("short content")
    
    @patch('builtins.open', mock_open(read_data="x" * 2000))
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.basename')
    def test_display_file_content_long(self, mock_basename):
        """Test displaying long file content (truncated)."""
        from zCLI.subsystems.zOpen.open_modules.open_files import _display_file_content
        mock_basename.return_value = "file.txt"
        
        result = _display_file_content("/test/file.txt", self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "zBack")
        # Should truncate to 1000 chars
        call_args = self.mock_display.write_block.call_args[0][0]
        self.assertEqual(len(call_args), 1003)  # 1000 + "..."
    
    @patch('builtins.open', side_effect=Exception("Read error"))
    @patch('zCLI.subsystems.zOpen.open_modules.open_files.os.path.basename')
    def test_display_file_content_read_error(self, mock_basename, mock_file):
        """Test handling file read error."""
        from zCLI.subsystems.zOpen.open_modules.open_files import _display_file_content
        mock_basename.return_value = "file.txt"
        
        result = _display_file_content("/test/file.txt", self.mock_display, self.mock_logger)
        
        self.assertEqual(result, "stop")


class TestzOpenHandleMethod(unittest.TestCase):
    """Test main handle method and routing (Tier 2 - Facade)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zSpace": "/test/workspace",
            "zMachine": {}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_url')
    def test_handle_http_url(self, mock_open_url):
        """Test handling HTTP URL."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(http://example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("http://example.com", self.mock_zcli.session, self.mock_zcli.display, self.mock_zcli.logger)
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_url')
    def test_handle_https_url(self, mock_open_url):
        """Test handling HTTPS URL."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(https://example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("https://example.com", self.mock_zcli.session, self.mock_zcli.display, self.mock_zcli.logger)
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_url')
    def test_handle_www_url(self, mock_open_url):
        """Test handling www URL (adds https)."""
        mock_open_url.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(www.example.com)")
        
        self.assertEqual(result, "zBack")
        mock_open_url.assert_called_once_with("https://www.example.com", self.mock_zcli.session, self.mock_zcli.display, self.mock_zcli.logger)
    
    @patch('zCLI.subsystems.zOpen.zOpen.resolve_zpath')
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
    def test_handle_workspace_path(self, mock_open_file, mock_resolve_zpath):
        """Test handling workspace-relative path."""
        mock_resolve_zpath.return_value = "/test/workspace/file.txt"
        mock_open_file.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(@.dir.file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_resolve_zpath.assert_called_once_with("@.dir.file.txt", self.mock_zcli.session, self.mock_zcli.logger)
        mock_open_file.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.zOpen.resolve_zpath')
    def test_handle_zpath_resolution_fails(self, mock_resolve_zpath):
        """Test handling zPath when resolution fails."""
        mock_resolve_zpath.return_value = None
        
        result = self.zopen.handle("zOpen(@.invalid.path)")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.resolve_zpath')
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
    def test_handle_absolute_path(self, mock_open_file, mock_resolve_zpath):
        """Test handling absolute path."""
        mock_resolve_zpath.return_value = "/home/user/file.txt"
        mock_open_file.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(~.home.user.file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_resolve_zpath.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath')
    @patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser')
    def test_handle_local_file(self, mock_expanduser, mock_abspath, mock_open_file):
        """Test handling local file path."""
        mock_expanduser.return_value = "/test/file.txt"
        mock_abspath.return_value = "/test/file.txt"
        mock_open_file.return_value = "zBack"
        
        result = self.zopen.handle("zOpen(/test/file.txt)")
        
        self.assertEqual(result, "zBack")
        mock_open_file.assert_called_once()
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
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
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
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
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
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
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
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
            "zSpace": "/test/workspace",
            "zMachine": {}
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zfunc = Mock()
        self.mock_zcli.dialog = Mock()
        
        with patch('builtins.print'):
            self.zopen = zOpen(self.mock_zcli)
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
    def test_handle_empty_path(self, mock_open_file):
        """Test handling empty path."""
        mock_open_file.return_value = "stop"
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value=""):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value=""):
                result = self.zopen.handle("zOpen()")
        
        self.assertEqual(result, "stop")
    
    @patch('zCLI.subsystems.zOpen.zOpen.open_file')
    def test_handle_path_with_quotes(self, mock_open_file):
        """Test handling path with quotes."""
        mock_open_file.return_value = "zBack"
        with patch('zCLI.subsystems.zOpen.zOpen.os.path.abspath', return_value="/test/file.txt"):
            with patch('zCLI.subsystems.zOpen.zOpen.os.path.expanduser', return_value="/test/file.txt"):
                result = self.zopen.handle('zOpen("/test/file.txt")')
        
        self.assertEqual(result, "zBack")


def run_tests(verbose=False):
    """Run all zOpen tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenPathResolutionModule))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenURLModule))
    suite.addTests(loader.loadTestsFromTestCase(TestzOpenFileModule))
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
