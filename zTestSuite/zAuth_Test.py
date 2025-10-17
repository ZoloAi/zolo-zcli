#!/usr/bin/env python3
# zTestSuite/zAuth_Test.py

"""
Test Suite for zAuth Subsystem

Tests authentication, credential management, session handling,
local/remote authentication, and integration with zData.

Note: These tests assume zData subsystem is working correctly.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zAuth import zAuth
from zCLI.subsystems.zAuth.zAuth_modules.credentials import CredentialManager
from zCLI.subsystems.zAuth.zAuth_modules.local_auth import authenticate_local
from zCLI.subsystems.zAuth.zAuth_modules.validation import validate_api_key


class TestzAuthInitialization(unittest.TestCase):
    """Test zAuth subsystem initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create minimal zCLI mock
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.handle = Mock()
    
    def test_zauth_initialization(self):
        """Test that zAuth initializes correctly."""
        auth = zAuth(self.mock_zcli)
        
        self.assertIsNotNone(auth)
        self.assertEqual(auth.zcli, self.mock_zcli)
        self.assertEqual(auth.session, self.mock_zcli.session)
        self.assertIsNotNone(auth.credentials)
        self.assertIsInstance(auth.credentials, CredentialManager)
    
    def test_zauth_display_ready_message(self):
        """Test that zAuth displays ready message."""
        auth = zAuth(self.mock_zcli)
        
        # Verify display.handle was called
        self.mock_zcli.display.handle.assert_called()
        
        # Check that "zAuth Ready" message was sent
        calls = self.mock_zcli.display.handle.call_args_list
        ready_call = any("zAuth Ready" in str(call) for call in calls)
        self.assertTrue(ready_call, "zAuth Ready message should be displayed")
    
    def test_zauth_session_structure(self):
        """Test that session has proper zAuth structure."""
        auth = zAuth(self.mock_zcli)
        
        self.assertIn("zAuth", auth.session)
        self.assertIn("id", auth.session["zAuth"])
        self.assertIn("username", auth.session["zAuth"])
        self.assertIn("role", auth.session["zAuth"])
        self.assertIn("API_Key", auth.session["zAuth"])


class TestCredentialManager(unittest.TestCase):
    """Test credential management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cred_manager = CredentialManager()
        # Override credentials file path to use temp directory
        self.cred_manager.credentials_file = Path(self.temp_dir) / ".zolo_credentials"
        self.mock_logger = Mock()
    
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_credentials(self):
        """Test saving credentials to file."""
        credentials = {
            "username": "testuser",
            "api_key": "test_api_key_12345",
            "role": "admin",
            "user_id": "zU_abc123"
        }
        
        result = self.cred_manager.save(credentials, self.mock_logger)
        
        self.assertTrue(result)
        self.assertTrue(self.cred_manager.credentials_file.exists())
    
    def test_load_credentials(self):
        """Test loading credentials from file."""
        credentials = {
            "username": "testuser",
            "api_key": "test_api_key_12345",
            "role": "admin",
            "user_id": "zU_abc123"
        }
        
        # Save credentials first
        self.cred_manager.save(credentials, self.mock_logger)
        
        # Load them back
        loaded = self.cred_manager.load(self.mock_logger)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["username"], "testuser")
        self.assertEqual(loaded["api_key"], "test_api_key_12345")
        self.assertEqual(loaded["role"], "admin")
    
    def test_load_nonexistent_credentials(self):
        """Test loading when credentials file doesn't exist."""
        loaded = self.cred_manager.load(self.mock_logger)
        
        self.assertIsNone(loaded)
    
    def test_delete_credentials(self):
        """Test deleting credentials file."""
        credentials = {
            "username": "testuser",
            "api_key": "test_api_key_12345"
        }
        
        # Save credentials first
        self.cred_manager.save(credentials, self.mock_logger)
        self.assertTrue(self.cred_manager.credentials_file.exists())
        
        # Delete them
        result = self.cred_manager.delete(self.mock_logger)
        
        self.assertTrue(result)
        self.assertFalse(self.cred_manager.credentials_file.exists())
    
    def test_delete_nonexistent_credentials(self):
        """Test deleting when credentials file doesn't exist."""
        result = self.cred_manager.delete(self.mock_logger)
        
        # Should return False since file doesn't exist
        self.assertFalse(result)
    
    def test_credentials_file_permissions(self):
        """Test that credentials file has restricted permissions."""
        credentials = {
            "username": "testuser",
            "api_key": "test_api_key_12345"
        }
        
        self.cred_manager.save(credentials, self.mock_logger)
        
        # Check file exists
        self.assertTrue(self.cred_manager.credentials_file.exists())
        
        # On Unix systems, check permissions are restrictive
        if os.name != 'nt':  # Skip on Windows
            file_stat = os.stat(self.cred_manager.credentials_file)
            # File should be readable/writable only by owner (0o600)
            self.assertEqual(file_stat.st_mode & 0o777, 0o600)
    
    def test_restore_to_session(self):
        """Test restoring credentials to session."""
        credentials = {
            "username": "testuser",
            "api_key": "test_api_key_12345",
            "role": "admin",
            "user_id": "zU_abc123"
        }
        
        # Save credentials
        self.cred_manager.save(credentials, self.mock_logger)
        
        # Create mock session
        session = {
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        
        # Restore to session
        self.cred_manager.restore_to_session(session, self.mock_logger)
        
        # Verify session was updated
        self.assertEqual(session["zAuth"]["username"], "testuser")
        self.assertEqual(session["zAuth"]["API_Key"], "test_api_key_12345")
        self.assertEqual(session["zAuth"]["role"], "admin")
        self.assertEqual(session["zAuth"]["id"], "zU_abc123")


class TestLocalAuthentication(unittest.TestCase):
    """Test local authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
    
    def test_local_auth_returns_none_by_default(self):
        """Test that local auth returns None (no local users by default)."""
        result = authenticate_local("testuser", "password", self.mock_logger)
        
        # Default implementation returns None (no local users)
        self.assertIsNone(result)
    
    def test_local_auth_with_invalid_credentials(self):
        """Test local auth with invalid credentials."""
        result = authenticate_local("invalid", "wrong", self.mock_logger)
        
        self.assertIsNone(result)


class TestRemoteAuthentication(unittest.TestCase):
    """Test remote authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.handle = Mock()
        
        # Mock zComm
        self.mock_zcli.comm = Mock()
        
        self.auth = zAuth(self.mock_zcli)
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"})
    def test_remote_auth_uses_comm(self):
        """Test that remote auth uses zComm for HTTP communication."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "user": {
                "username": "testuser",
                "api_key": "test_key_12345",
                "role": "user",
                "id": "zU_abc123"
            }
        }
        
        self.mock_zcli.comm.http_post.return_value = mock_response
        
        result = self.auth.login("testuser", "password")
        
        # Verify comm.http_post was called
        self.mock_zcli.comm.http_post.assert_called_once()
        
        # Verify successful result
        self.assertEqual(result["status"], "success")
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"})
    def test_remote_auth_failure(self):
        """Test remote auth failure handling."""
        # Mock failed response
        self.mock_zcli.comm.http_post.return_value = None
        
        result = self.auth.login("testuser", "wrongpassword")
        
        self.assertEqual(result["status"], "fail")


class TestAuthenticationWorkflow(unittest.TestCase):
    """Test complete authentication workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.handle = Mock()
        self.mock_zcli.comm = Mock()
        
        self.auth = zAuth(self.mock_zcli)
        
        # Override credentials file path
        self.auth.credentials.credentials_file = Path(self.temp_dir) / ".zolo_credentials"
    
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_login_logout_cycle(self):
        """Test complete login and logout cycle."""
        # Mock successful local authentication
        with patch('zCLI.subsystems.zAuth.zAuth_modules.local_auth.authenticate_local') as mock_auth:
            mock_auth.return_value = {
                "username": "testuser",
                "api_key": "test_key_12345",
                "role": "admin",
                "user_id": "zU_abc123"
            }
            
            # Login
            result = self.auth.login("testuser", "password")
            
            self.assertEqual(result["status"], "success")
            self.assertTrue(self.auth.credentials.credentials_file.exists())
            
            # Verify session was updated
            self.assertEqual(self.mock_zcli.session["zAuth"]["username"], "testuser")
            self.assertEqual(self.mock_zcli.session["zAuth"]["role"], "admin")
        
        # Logout
        logout_result = self.auth.logout()
        
        self.assertEqual(logout_result["status"], "success")
        self.assertFalse(self.auth.credentials.credentials_file.exists())
        
        # Verify session was cleared
        self.assertIsNone(self.mock_zcli.session["zAuth"]["username"])
        self.assertIsNone(self.mock_zcli.session["zAuth"]["role"])
    
    def test_is_authenticated(self):
        """Test authentication status checking."""
        # Initially not authenticated
        self.assertFalse(self.auth.is_authenticated())
        
        # Save credentials
        credentials = {
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "user"
        }
        self.auth.credentials.save(credentials, self.mock_zcli.logger)
        
        # Now authenticated
        self.assertTrue(self.auth.is_authenticated())
    
    def test_get_credentials(self):
        """Test retrieving stored credentials."""
        # No credentials initially
        creds = self.auth.get_credentials()
        self.assertIsNone(creds)
        
        # Save credentials
        credentials = {
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "user"
        }
        self.auth.credentials.save(credentials, self.mock_zcli.logger)
        
        # Retrieve credentials
        creds = self.auth.get_credentials()
        self.assertIsNotNone(creds)
        self.assertEqual(creds["username"], "testuser")
    
    def test_status_authenticated(self):
        """Test status when authenticated."""
        # Save credentials
        credentials = {
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "admin",
            "user_id": "zU_abc123"
        }
        self.auth.credentials.save(credentials, self.mock_zcli.logger)
        
        # Check status
        status = self.auth.status()
        
        self.assertEqual(status["status"], "authenticated")
        self.assertIn("user", status)
    
    def test_status_not_authenticated(self):
        """Test status when not authenticated."""
        status = self.auth.status()
        
        self.assertEqual(status["status"], "not_authenticated")


class TestAPIKeyValidation(unittest.TestCase):
    """Test API key validation with zData integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zAuth": {}}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.handle = Mock()
        
        # Mock zData
        self.mock_zcli.data = Mock()
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_validate_api_key_success(self):
        """Test successful API key validation."""
        # Mock zData response
        self.mock_zcli.data.handle_request.return_value = [
            {
                "id": "zU_abc123",
                "username": "testuser",
                "role": "admin"
            }
        ]
        
        result = validate_api_key(self.mock_zcli, "test_api_key_12345")
        
        self.assertTrue(result["valid"])
        self.assertIn("user", result)
        self.assertEqual(result["user"]["username"], "testuser")
    
    def test_validate_api_key_invalid(self):
        """Test invalid API key validation."""
        # Mock zData response - no users found
        self.mock_zcli.data.handle_request.return_value = []
        
        result = validate_api_key(self.mock_zcli, "invalid_api_key")
        
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "Invalid API key")
    
    def test_validate_api_key_no_zcli(self):
        """Test API key validation without zCLI instance."""
        result = validate_api_key(None, "test_api_key")
        
        self.assertFalse(result["valid"])
        self.assertIn("reason", result)
    
    def test_validate_api_key_zdata_error(self):
        """Test API key validation with zData error."""
        # Mock zData exception
        self.mock_zcli.data.handle_request.side_effect = Exception("Database error")
        
        result = validate_api_key(self.mock_zcli, "test_api_key")
        
        self.assertFalse(result["valid"])
        self.assertIn("reason", result)
    
    def test_validate_current_credentials(self):
        """Test validating current stored credentials."""
        # Save credentials
        credentials = {
            "username": "testuser",
            "api_key": "test_key_12345",
            "server_url": "http://localhost:5000"
        }
        temp_dir = tempfile.mkdtemp()
        try:
            self.auth.credentials.credentials_file = Path(temp_dir) / ".zolo_credentials"
            self.auth.credentials.save(credentials, self.mock_zcli.logger)
            
            # Mock zData response
            self.mock_zcli.data.handle_request.return_value = [
                {
                    "id": "zU_abc123",
                    "username": "testuser",
                    "role": "user"
                }
            ]
            
            # Validate without providing API key (should use stored credentials)
            result = self.auth.validate_api_key()
            
            self.assertTrue(result["valid"])
        finally:
            shutil.rmtree(temp_dir)


class TestSessionRestoration(unittest.TestCase):
    """Test session restoration from saved credentials."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.mock_zcli.display.handle = Mock()
        
        self.auth = zAuth(self.mock_zcli)
        self.auth.credentials.credentials_file = Path(self.temp_dir) / ".zolo_credentials"
    
    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_restore_session(self):
        """Test restoring session from credentials file."""
        # Save credentials
        credentials = {
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "admin",
            "user_id": "zU_abc123"
        }
        self.auth.credentials.save(credentials, self.mock_zcli.logger)
        
        # Clear session
        self.mock_zcli.session["zAuth"] = {
            "id": None,
            "username": None,
            "role": None,
            "API_Key": None
        }
        
        # Restore session
        self.auth.restore_session()
        
        # Verify session was restored
        self.assertEqual(self.mock_zcli.session["zAuth"]["username"], "testuser")
        self.assertEqual(self.mock_zcli.session["zAuth"]["API_Key"], "test_key_12345")
        self.assertEqual(self.mock_zcli.session["zAuth"]["role"], "admin")
    
    def test_restore_session_no_credentials(self):
        """Test restore session when no credentials exist."""
        # Should not raise exception
        self.auth.restore_session()
        
        # Session should remain empty
        self.assertIsNone(self.mock_zcli.session["zAuth"]["username"])


def run_tests(verbose=True):
    """Run all zAuth tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes in logical order
    suite.addTests(loader.loadTestsFromTestCase(TestzAuthInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCredentialManager))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestRemoteAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIKeyValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionRestoration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zCLI Authentication Test Suite")
    print("=" * 70)
    print()
    
    result = run_tests(verbose=True)
    
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

