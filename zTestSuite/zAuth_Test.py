#!/usr/bin/env python3
# zTestSuite/zAuth_Test.py

"""
Test Suite for zAuth Subsystem

Tests session-only authentication, bcrypt password hashing,
remote authentication, and integration with zDisplay dual-mode events.

v1.5.4+: Added comprehensive bcrypt password hashing tests (Week 3.1)
"""

import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import os
import time

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zAuth.zAuth import zAuth
from zCLI.subsystems.zDisplay.zDisplay import zDisplay


class TestzAuthInitialization(unittest.TestCase):
    """Test zAuth subsystem initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create minimal zCLI mock with zDisplay
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        # Initialize real zDisplay for dual-mode support
        self.mock_zcli.display = zDisplay(self.mock_zcli)
    
    def test_zauth_initialization(self):
        """Test that zAuth initializes correctly."""
        auth = zAuth(self.mock_zcli)
        
        self.assertIsNotNone(auth)
        self.assertEqual(auth.zcli, self.mock_zcli)
        self.assertEqual(auth.session, self.mock_zcli.session)
        self.assertEqual(auth.mycolor, "ZAUTH")
    
    def test_zauth_display_events_available(self):
        """Test that zAuth has access to zDisplay events."""
        auth = zAuth(self.mock_zcli)
        
        # Verify zDisplay.zEvents.zAuth is available
        self.assertTrue(hasattr(self.mock_zcli.display, 'zEvents'))
        self.assertTrue(hasattr(self.mock_zcli.display.zEvents, 'zAuth'))
        
        # Verify zAuth events exist
        zauth_events = self.mock_zcli.display.zEvents.zAuth
        self.assertTrue(hasattr(zauth_events, 'login_prompt'))
        self.assertTrue(hasattr(zauth_events, 'login_success'))
        self.assertTrue(hasattr(zauth_events, 'login_failure'))
        self.assertTrue(hasattr(zauth_events, 'logout_success'))
        self.assertTrue(hasattr(zauth_events, 'status_display'))
    
    def test_zauth_session_structure(self):
        """Test that session has proper zAuth structure."""
        auth = zAuth(self.mock_zcli)
        
        self.assertIn("zAuth", auth.session)
        self.assertIn("id", auth.session["zAuth"])
        self.assertIn("username", auth.session["zAuth"])
        self.assertIn("role", auth.session["zAuth"])
        self.assertIn("API_Key", auth.session["zAuth"])


class TestSessionOnlyAuthentication(unittest.TestCase):
    """Test session-only authentication (no persistence)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_is_authenticated_initially_false(self):
        """Test that user is not authenticated initially."""
        self.assertFalse(self.auth.is_authenticated())
    
    def test_is_authenticated_after_session_update(self):
        """Test authentication status after session update."""
        # Simulate successful login by updating session
        self.mock_zcli.session["zAuth"].update({
            "username": "testuser",
            "API_Key": "test_key_12345",
            "role": "user",
            "id": "zU_abc123"
        })
        
        self.assertTrue(self.auth.is_authenticated())
    
    def test_get_credentials_when_not_authenticated(self):
        """Test getting credentials when not authenticated."""
        creds = self.auth.get_credentials()
        self.assertIsNone(creds)
    
    def test_get_credentials_when_authenticated(self):
        """Test getting credentials when authenticated."""
        # Simulate successful login
        session_auth = {
            "username": "testuser",
            "API_Key": "test_key_12345",
            "role": "admin",
            "id": "zU_abc123"
        }
        self.mock_zcli.session["zAuth"].update(session_auth)
        
        creds = self.auth.get_credentials()
        self.assertIsNotNone(creds)
        self.assertEqual(creds["username"], "testuser")
        self.assertEqual(creds["API_Key"], "test_key_12345")
        self.assertEqual(creds["role"], "admin")


class TestLogoutWorkflow(unittest.TestCase):
    """Test logout functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_logout_when_not_logged_in(self):
        """Test logout when not logged in."""
        result = self.auth.logout()
        
        self.assertEqual(result["status"], "success")
        self.assertIsNone(self.mock_zcli.session["zAuth"]["username"])
    
    def test_logout_when_logged_in(self):
        """Test logout when logged in."""
        # Simulate logged in state
        self.mock_zcli.session["zAuth"].update({
            "username": "testuser",
            "API_Key": "test_key_12345",
            "role": "user",
            "id": "zU_abc123"
        })
        
        result = self.auth.logout()
        
        self.assertEqual(result["status"], "success")
        self.assertIsNone(self.mock_zcli.session["zAuth"]["username"])
        self.assertIsNone(self.mock_zcli.session["zAuth"]["API_Key"])


class TestStatusDisplay(unittest.TestCase):
    """Test status display functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_status_not_authenticated(self):
        """Test status when not authenticated."""
        result = self.auth.status()
        
        self.assertEqual(result["status"], "not_authenticated")
    
    def test_status_authenticated(self):
        """Test status when authenticated."""
        # Simulate logged in state
        session_auth = {
            "username": "testuser",
            "API_Key": "test_key_12345",
            "role": "admin",
            "id": "zU_abc123"
        }
        self.mock_zcli.session["zAuth"].update(session_auth)
        
        result = self.auth.status()
        
        self.assertEqual(result["status"], "authenticated")
        self.assertIn("user", result)
        self.assertEqual(result["user"]["username"], "testuser")
        self.assertEqual(result["user"]["role"], "admin")


class TestRemoteAuthentication(unittest.TestCase):
    """Test remote authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "false"})
    def test_login_without_remote_api(self):
        """Test login when remote API is disabled."""
        result = self.auth.login("testuser", "password")
        
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["reason"], "Invalid credentials")
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"})
    @patch.object(zAuth, '_authenticate_remote')
    def test_login_with_remote_api_success(self, mock_remote_auth):
        """Test successful login with remote API."""
        # Mock successful remote authentication
        mock_remote_auth.return_value = {
            "status": "success",
            "credentials": {
                "username": "testuser",
                "api_key": "test_key_12345",
                "role": "user",
                "user_id": "zU_abc123"
            }
        }
        
        result = self.auth.login("testuser", "password")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.mock_zcli.session["zAuth"]["username"], "testuser")
        self.assertEqual(self.mock_zcli.session["zAuth"]["API_Key"], "test_key_12345")
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"})
    @patch.object(zAuth, '_authenticate_remote')
    def test_login_with_remote_api_failure(self, mock_remote_auth):
        """Test failed login with remote API."""
        # Mock failed remote authentication
        mock_remote_auth.return_value = {
            "status": "fail",
            "reason": "Invalid credentials"
        }
        
        result = self.auth.login("testuser", "wrongpassword")
        
        self.assertEqual(result["status"], "fail")
        self.assertIsNone(self.mock_zcli.session["zAuth"]["username"])


class TestDualModeEvents(unittest.TestCase):
    """Test dual-mode (Terminal/GUI) event integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "id": None,
                "username": None,
                "role": None,
                "API_Key": None
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_zauth_events_package_exists(self):
        """Test that zAuth events package exists in zDisplay."""
        self.assertTrue(hasattr(self.mock_zcli.display.zEvents, 'zAuth'))
    
    def test_zauth_events_have_primitives(self):
        """Test that zAuth events have access to primitives."""
        zauth_events = self.mock_zcli.display.zEvents.zAuth
        self.assertTrue(hasattr(zauth_events, 'zPrimitives'))
        self.assertTrue(hasattr(zauth_events, 'zColors'))
    
    def test_zauth_events_have_composition(self):
        """Test that zAuth events can compose other events."""
        zauth_events = self.mock_zcli.display.zEvents.zAuth
        self.assertTrue(hasattr(zauth_events, 'BasicOutputs'))
        self.assertTrue(hasattr(zauth_events, 'Signals'))


# ═══════════════════════════════════════════════════════════════
# NEW: Password Hashing Tests (bcrypt) - Week 3.1
# ═══════════════════════════════════════════════════════════════

class TestPasswordHashing(unittest.TestCase):
    """Test bcrypt password hashing and verification (v1.5.4+)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        self.mock_zcli.session = {"zAuth": {}}
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = Mock()
        self.auth = zAuth(self.mock_zcli)
    
    def test_hash_password_returns_bcrypt_hash(self):
        """Should return valid bcrypt hash starting with $2b$"""
        password = "test_password_123"
        hashed = self.auth.hash_password(password)
        
        # bcrypt hashes start with $2b$ (version identifier)
        self.assertTrue(hashed.startswith("$2b$"))
        self.assertEqual(len(hashed), 60)  # bcrypt hashes are always 60 chars
    
    def test_hash_password_different_each_time(self):
        """Should generate different hashes for same password (random salt)"""
        password = "same_password"
        hash1 = self.auth.hash_password(password)
        hash2 = self.auth.hash_password(password)
        
        # Same password, different hashes (due to random salt)
        self.assertNotEqual(hash1, hash2)
        # But both should be valid bcrypt hashes
        self.assertTrue(hash1.startswith("$2b$"))
        self.assertTrue(hash2.startswith("$2b$"))
    
    def test_verify_password_correct(self):
        """Should verify correct password"""
        password = "correct_password"
        hashed = self.auth.hash_password(password)
        
        result = self.auth.verify_password(password, hashed)
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        """Should reject incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = self.auth.hash_password(password)
        
        result = self.auth.verify_password(wrong_password, hashed)
        self.assertFalse(result)
    
    def test_verify_password_empty_plain_password(self):
        """Should handle empty plaintext password gracefully"""
        hashed = self.auth.hash_password("test")
        
        result = self.auth.verify_password("", hashed)
        self.assertFalse(result)
    
    def test_verify_password_empty_hash(self):
        """Should handle empty hash gracefully"""
        result = self.auth.verify_password("test", "")
        self.assertFalse(result)
    
    def test_verify_password_both_empty(self):
        """Should handle both empty inputs gracefully"""
        result = self.auth.verify_password("", "")
        self.assertFalse(result)
    
    def test_hash_password_empty_raises_error(self):
        """Should raise ValueError for empty password"""
        with self.assertRaises(ValueError) as context:
            self.auth.hash_password("")
        
        self.assertIn("Password cannot be empty", str(context.exception))
    
    def test_hash_password_none_raises_error(self):
        """Should raise ValueError for None password"""
        with self.assertRaises(ValueError) as context:
            self.auth.hash_password(None)
        
        self.assertIn("Password cannot be empty", str(context.exception))
    
    def test_verify_password_invalid_hash_format(self):
        """Should return False for invalid hash format"""
        result = self.auth.verify_password("password", "not_a_valid_bcrypt_hash")
        self.assertFalse(result)
        
        # Should log error
        self.mock_zcli.logger.error.assert_called_once()
        self.assertIn("Password verification error", 
                     str(self.mock_zcli.logger.error.call_args))
    
    def test_bcrypt_hash_performance(self):
        """Should hash within acceptable time (< 0.5s for 12 rounds)"""
        password = "performance_test_password"
        
        # Hash should take < 0.5s (12 rounds on modern hardware)
        start = time.time()
        hashed = self.auth.hash_password(password)
        hash_time = time.time() - start
        
        self.assertLess(hash_time, 0.5, f"Hashing took {hash_time:.3f}s (> 0.5s)")
        
        # Verify should also take < 0.5s
        start = time.time()
        result = self.auth.verify_password(password, hashed)
        verify_time = time.time() - start
        
        self.assertLess(verify_time, 0.5, f"Verification took {verify_time:.3f}s (> 0.5s)")
        self.assertTrue(result)
    
    def test_bcrypt_handles_special_characters(self):
        """Should handle passwords with special characters"""
        special_passwords = [
            "p@ssw0rd!",
            "über_secure",
            "emoji_😀_password",
            "spaces in password",
            "quotes'and\"double",
            "\ttabs\nand\nnewlines"
        ]
        
        for password in special_passwords:
            hashed = self.auth.hash_password(password)
            result = self.auth.verify_password(password, hashed)
            self.assertTrue(result, f"Failed for password: {repr(password)}")
    
    def test_bcrypt_handles_long_passwords(self):
        """Should handle long passwords (72 bytes is bcrypt limit)"""
        # bcrypt truncates at 72 bytes, but should still work
        long_password = "a" * 100
        hashed = self.auth.hash_password(long_password)
        
        result = self.auth.verify_password(long_password, hashed)
        self.assertTrue(result)
    
    def test_verify_password_case_sensitive(self):
        """Should be case-sensitive"""
        password = "Password123"
        hashed = self.auth.hash_password(password)
        
        # Exact match
        self.assertTrue(self.auth.verify_password("Password123", hashed))
        
        # Wrong case
        self.assertFalse(self.auth.verify_password("password123", hashed))
        self.assertFalse(self.auth.verify_password("PASSWORD123", hashed))


def run_tests(verbose=True):
    """Run all zAuth tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes in logical order
    suite.addTests(loader.loadTestsFromTestCase(TestzAuthInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionOnlyAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestLogoutWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusDisplay))
    suite.addTests(loader.loadTestsFromTestCase(TestRemoteAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestDualModeEvents))
    
    # NEW: Password hashing tests (Week 3.1)
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordHashing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = runner.run(suite)
    
    return test_result


if __name__ == "__main__":
    print("=" * 70)
    print("zCLI Authentication Test Suite (Streamlined)")
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
