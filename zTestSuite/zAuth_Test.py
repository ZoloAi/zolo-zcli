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
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
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
        """Test that session has proper three-tier zAuth structure."""
        auth = zAuth(self.mock_zcli)
        
        # Updated for three-tier authentication structure
        self.assertIn("zAuth", auth.session)
        self.assertIn("zSession", auth.session["zAuth"])
        self.assertIn("applications", auth.session["zAuth"])
        self.assertIn("active_app", auth.session["zAuth"])
        self.assertIn("active_context", auth.session["zAuth"])
        self.assertIn("dual_mode", auth.session["zAuth"])
        # Check zSession structure
        self.assertIn("id", auth.session["zAuth"]["zSession"])
        self.assertIn("username", auth.session["zAuth"]["zSession"])
        self.assertIn("role", auth.session["zAuth"]["zSession"])
        self.assertIn("api_key", auth.session["zAuth"]["zSession"])


class TestSessionOnlyAuthentication(unittest.TestCase):
    """Test session-only authentication (no persistence)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_is_authenticated_initially_false(self):
        """Test that user is not authenticated initially."""
        self.assertFalse(self.auth.is_authenticated())
    
    def test_is_authenticated_after_session_update(self):
        """Test authentication status after session update (updated for three-tier structure)."""
        # Simulate successful login by updating session in new nested structure
        self.mock_zcli.session["zAuth"]["zSession"].update({
            "authenticated": True,
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "user",
            "id": "zU_abc123"
        })
        
        self.assertTrue(self.auth.is_authenticated())
    
    def test_get_credentials_when_not_authenticated(self):
        """Test getting credentials when not authenticated."""
        creds = self.auth.get_credentials()
        self.assertIsNone(creds)
    
    def test_get_credentials_when_authenticated(self):
        """Test getting credentials when authenticated (updated for three-tier structure)."""
        # Simulate successful login in new nested structure
        session_auth = {
            "authenticated": True,
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "admin",
            "id": "zU_abc123"
        }
        self.mock_zcli.session["zAuth"]["zSession"].update(session_auth)
        
        creds = self.auth.get_credentials()
        self.assertIsNotNone(creds)
        self.assertEqual(creds["username"], "testuser")
        self.assertEqual(creds["api_key"], "test_key_12345")
        self.assertEqual(creds["role"], "admin")


class TestLogoutWorkflow(unittest.TestCase):
    """Test logout functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        self.auth = zAuth(self.mock_zcli)
    
    def test_logout_when_not_logged_in(self):
        """Test logout when not logged in."""
        result = self.auth.logout()
        
        self.assertEqual(result["status"], "success")
        # Updated for three-tier authentication structure
        self.assertFalse(self.mock_zcli.session["zAuth"]["zSession"]["authenticated"])
    
    def test_logout_when_logged_in(self):
        """Test logout when logged in (updated for three-tier structure)."""
        # Simulate logged in state in new nested structure
        self.mock_zcli.session["zAuth"]["zSession"].update({
            "authenticated": True,
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "user",
            "id": "zU_abc123"
        })
        
        result = self.auth.logout()
        
        self.assertEqual(result["status"], "success")
        # Updated for three-tier authentication structure
        self.assertFalse(self.mock_zcli.session["zAuth"]["zSession"]["authenticated"])
        self.assertIsNone(self.mock_zcli.session["zAuth"]["zSession"].get("api_key"))


class TestStatusDisplay(unittest.TestCase):
    """Test status display functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
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
        """Test status when authenticated (updated for three-tier structure)."""
        # Simulate logged in state in new nested structure
        session_auth = {
            "authenticated": True,
            "username": "testuser",
            "api_key": "test_key_12345",
            "role": "admin",
            "id": "zU_abc123"
        }
        self.mock_zcli.session["zAuth"]["zSession"].update(session_auth)
        
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
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
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
    @patch('zCLI.subsystems.zAuth.zAuth_modules.auth_authentication.Authentication.authenticate_remote')
    def test_login_with_remote_api_success(self, mock_remote_auth):
        """Test successful login with remote API (modular architecture)."""
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
        # Updated for three-tier authentication structure
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["username"], "testuser")
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["api_key"], "test_key_12345")
    
    @patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"})
    @patch('zCLI.subsystems.zAuth.zAuth_modules.auth_authentication.Authentication.authenticate_remote')
    def test_login_with_remote_api_failure(self, mock_remote_auth):
        """Test failed login with remote API (modular architecture)."""
        # Mock failed remote authentication
        mock_remote_auth.return_value = {
            "status": "fail",
            "reason": "Invalid credentials"
        }
        
        result = self.auth.login("testuser", "wrongpassword")
        
        self.assertEqual(result["status"], "fail")
        # Updated for three-tier authentication structure
        self.assertFalse(self.mock_zcli.session["zAuth"]["zSession"].get("authenticated", False))


class TestDualModeEvents(unittest.TestCase):
    """Test dual-mode (Terminal/GUI) event integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = Mock()
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
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
        """Should hash within acceptable time (< 1.0s for 12 rounds)"""
        password = "performance_test_password"
        
        # Hash should take < 1.0s (12 rounds - forgiving timeout for varying system load)
        start = time.time()
        hashed = self.auth.hash_password(password)
        hash_time = time.time() - start
        
        self.assertLess(hash_time, 1.0, f"Hashing took {hash_time:.3f}s (> 1.0s)")
        
        # Verify should also take < 1.0s
        start = time.time()
        result = self.auth.verify_password(password, hashed)
        verify_time = time.time() - start
        
        self.assertLess(verify_time, 1.0, f"Verification took {verify_time:.3f}s (> 1.0s)")
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


class TestPersistentSessions(unittest.TestCase):
    """Test persistent session functionality (Week 3.2).
    
    Tests the "Remember me" functionality - sessions that survive app restarts.
    """
    
    def setUp(self):
        """Set up test fixtures with zData mocking."""
        import tempfile
        
        # Create minimal zCLI mock with zData
        self.mock_zcli = Mock()
        # Updated for three-tier authentication structure
        self.mock_zcli.session = {
            "zMode": "Terminal",
            "zAuth": {
                "zSession": {
                    "authenticated": False,
                    "id": None,
                    "username": None,
                    "role": None,
                    "api_key": None,
                    "session_id": None
                },
                "applications": {},
                "active_app": None,
                "active_context": None,
                "dual_mode": False
            }
        }
        self.mock_zcli.logger = Mock()
        self.mock_zcli.display = zDisplay(self.mock_zcli)
        
        # Mock zData
        self.mock_zcli.data = Mock()
        self.mock_zcli.data.handler = Mock()
        self.mock_zcli.data.schema = {"Meta": {"Data_Label": "auth"}}  # Unified auth schema (v1.5.4+)
        self.mock_zcli.data.table_exists = Mock(return_value=False)
        self.mock_zcli.data.create_table = Mock()
        
        # Mock zParser (new modular architecture)
        self.mock_zcli.zparser = Mock()
        self.mock_zcli.zparser.parse_file_content = Mock(return_value={"Meta": {"Data_Label": "auth"}})
        
        # Mock load_schema to update handler
        def mock_load_schema(schema):
            self.mock_zcli.data.schema = schema
            self.mock_zcli.data.handler = Mock()
        self.mock_zcli.data.load_schema = Mock(side_effect=mock_load_schema)
        
        # Mock zLoader (kept for compatibility)
        self.mock_zcli.loader = Mock()
        self.mock_zcli.loader.handle = Mock(return_value=True)
        
        # Create temp directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="zauth_session_test_")
    
    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_ensure_sessions_db_success(self):
        """Should initialize sessions database successfully"""
        auth = zAuth(self.mock_zcli)
        
        # Trigger lazy loading by calling ensure_sessions_db
        auth.session_persistence.ensure_sessions_db()
        
        # Verify zparser.parse_file_content was called (new architecture)
        self.mock_zcli.zparser.parse_file_content.assert_called()
        
        # Verify it's loading zSchema.auth.yaml (unified schema)
        call_args = str(self.mock_zcli.zparser.parse_file_content.call_args)
        self.assertIn("auth", call_args.lower())
        
        # Verify table_exists was checked for both tables
        self.assertIn(
            unittest.mock.call("sessions"),
            self.mock_zcli.data.table_exists.call_args_list
        )
        
        # Verify create_table was called for both tables
        self.assertIn(
            unittest.mock.call("sessions"),
            self.mock_zcli.data.create_table.call_args_list
        )
    
    def test_save_session_creates_record(self):
        """Should save session to database with correct fields"""
        auth = zAuth(self.mock_zcli)
        
        # Mock successful insert and delete
        self.mock_zcli.data.insert = Mock()
        self.mock_zcli.data.delete = Mock()
        
        # Save session via the modular interface
        auth.session_persistence.save_session(
            username="testuser",
            password_hash="$2b$12$fakehash",
            user_id="123"
        )
        
        # Verify delete was called (cleanup + single session per user = 2 calls)
        self.assertGreaterEqual(self.mock_zcli.data.delete.call_count, 1)
        
        # Verify insert was called with correct fields
        self.mock_zcli.data.insert.assert_called_once()
        insert_args = self.mock_zcli.data.insert.call_args
        
        self.assertEqual(insert_args[1]["table"], "sessions")
        self.assertIn("session_id", insert_args[1]["fields"])
        self.assertIn("user_id", insert_args[1]["fields"])
        self.assertIn("username", insert_args[1]["fields"])
        self.assertIn("password_hash", insert_args[1]["fields"])
        self.assertIn("token", insert_args[1]["fields"])
        self.assertIn("created_at", insert_args[1]["fields"])
        self.assertIn("expires_at", insert_args[1]["fields"])
        self.assertIn("last_accessed", insert_args[1]["fields"])
        
        # Verify values
        values = insert_args[1]["values"]
        username_idx = insert_args[1]["fields"].index("username")
        user_id_idx = insert_args[1]["fields"].index("user_id")
        password_hash_idx = insert_args[1]["fields"].index("password_hash")
        
        self.assertEqual(values[username_idx], "testuser")
        self.assertEqual(values[user_id_idx], "123")
        self.assertEqual(values[password_hash_idx], "$2b$12$fakehash")
    
    def test_save_session_generates_unique_tokens(self):
        """Should generate unique session_id and token for each session"""
        auth = zAuth(self.mock_zcli)
        
        # Mock database operations
        self.mock_zcli.data.insert = Mock()
        self.mock_zcli.data.delete = Mock()
        
        # Save two sessions via modular interface
        auth.session_persistence.save_session("user1", "hash1")
        first_call_values = self.mock_zcli.data.insert.call_args_list[0][1]["values"]
        
        auth.session_persistence.save_session("user2", "hash2")
        second_call_values = self.mock_zcli.data.insert.call_args_list[1][1]["values"]
        
        # Get session_id and token indexes
        fields = self.mock_zcli.data.insert.call_args_list[0][1]["fields"]
        session_id_idx = fields.index("session_id")
        token_idx = fields.index("token")
        
        # Verify they're different
        self.assertNotEqual(first_call_values[session_id_idx], second_call_values[session_id_idx])
        self.assertNotEqual(first_call_values[token_idx], second_call_values[token_idx])
    
    def test_load_session_restores_valid_session(self):
        """Should restore valid session from database"""
        from datetime import datetime, timedelta
        
        auth = zAuth(self.mock_zcli)
        
        # Mock valid session in database
        future_expiry = (datetime.now() + timedelta(days=5)).isoformat()
        mock_session = {
            "session_id": "test_session_123",
            "user_id": "456",
            "username": "restored_user",
            "token": "test_token_abc",
            "expires_at": future_expiry,
            "role": "user"
        }
        
        self.mock_zcli.data.select = Mock(return_value=[mock_session])
        self.mock_zcli.data.update = Mock()
        
        # Load session via modular interface
        auth.session_persistence.load_session()
        
        # Verify session was restored (updated for three-tier authentication structure)
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["id"], "456")
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["username"], "restored_user")
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["api_key"], "test_token_abc")
        self.assertEqual(self.mock_zcli.session["zAuth"]["zSession"]["session_id"], "test_session_123")
        
        # Verify last_accessed was updated
        self.mock_zcli.data.update.assert_called_once()
        update_args = self.mock_zcli.data.update.call_args
        self.assertIn("last_accessed", update_args[1]["fields"])
    
    def test_load_session_ignores_expired_session(self):
        """Should not restore expired session"""
        from datetime import datetime, timedelta
        
        auth = zAuth(self.mock_zcli)
        
        # Mock expired session
        past_expiry = (datetime.now() - timedelta(days=1)).isoformat()
        
        self.mock_zcli.data.select = Mock(return_value=[])  # No valid sessions
        self.mock_zcli.data.update = Mock()
        
        # Load session
        auth.session_persistence.load_session()
        
        # Verify session was NOT restored (updated for three-tier authentication structure)
        self.assertFalse(self.mock_zcli.session["zAuth"]["zSession"].get("authenticated", False))
        self.mock_zcli.data.update.assert_not_called()
    
    def test_cleanup_expired_removes_old_sessions(self):
        """Should delete expired sessions"""
        auth = zAuth(self.mock_zcli)
        
        self.mock_zcli.data.delete = Mock(return_value=3)  # 3 sessions deleted
        
        # Cleanup via modular interface
        auth.session_persistence.cleanup_expired()
        
        # Verify delete was called with expiry check
        self.mock_zcli.data.delete.assert_called_once()
        delete_args = self.mock_zcli.data.delete.call_args
        self.assertEqual(delete_args[1]["table"], "sessions")
        self.assertIn("expires_at", delete_args[1]["where"])
    
    def test_logout_deletes_persistent_session(self):
        """Should delete persistent session on logout"""
        auth = zAuth(self.mock_zcli)
        
        # Simulate logged-in user (updated for three-tier authentication structure)
        self.mock_zcli.session["zAuth"]["zSession"]["username"] = "testuser"
        self.mock_zcli.session["zAuth"]["zSession"]["api_key"] = "test_key"
        self.mock_zcli.session["zAuth"]["zSession"]["authenticated"] = True
        
        self.mock_zcli.data.delete = Mock()
        
        # Logout
        auth.logout()
        
        # Verify persistent session was deleted
        self.mock_zcli.data.delete.assert_called_once()
        delete_args = self.mock_zcli.data.delete.call_args
        self.assertEqual(delete_args[1]["table"], "sessions")
        self.assertIn("testuser", delete_args[1]["where"])
        
        # Verify in-memory session was cleared (updated for three-tier authentication structure)
        self.assertFalse(self.mock_zcli.session["zAuth"]["zSession"]["authenticated"])
        self.assertIsNone(self.mock_zcli.session["zAuth"]["zSession"].get("api_key"))
        self.assertIsNone(self.mock_zcli.session["zAuth"]["zSession"].get("session_id"))
    
    def test_login_with_persist_saves_session(self):
        """Should save session when persist=True"""
        auth = zAuth(self.mock_zcli)
        
        # Mock remote authentication success
        with patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"}):
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "user": {
                    "id": "789",
                    "username": "persisted_user",
                    "api_key": "api_key_xyz",
                    "role": "admin"
                }
            }
            
            self.mock_zcli.comm = Mock()
            self.mock_zcli.comm.http_post = Mock(return_value=mock_response)
            
            self.mock_zcli.data.insert = Mock()
            self.mock_zcli.data.delete = Mock()
            
            # Login with persistence
            result = auth.login(username="persisted_user", password="mypassword", persist=True)
            
            # Verify login succeeded
            self.assertEqual(result["status"], "success")
            
            # Verify session was saved
            self.mock_zcli.data.insert.assert_called_once()
            insert_args = self.mock_zcli.data.insert.call_args
            self.assertEqual(insert_args[1]["table"], "sessions")
    
    def test_login_with_persist_false_skips_save(self):
        """Should not save session when persist=False"""
        auth = zAuth(self.mock_zcli)
        
        # Mock remote authentication success
        with patch.dict(os.environ, {"ZOLO_USE_REMOTE_API": "true"}):
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "user": {
                    "id": "789",
                    "username": "temp_user",
                    "api_key": "api_key_xyz",
                    "role": "user"
                }
            }
            
            self.mock_zcli.comm = Mock()
            self.mock_zcli.comm.http_post = Mock(return_value=mock_response)
            
            self.mock_zcli.data.insert = Mock()
            self.mock_zcli.data.delete = Mock()
            
            # Login without persistence
            result = auth.login(username="temp_user", password="mypassword", persist=False)
            
            # Verify login succeeded
            self.assertEqual(result["status"], "success")
            
            # Verify session was NOT saved
            self.mock_zcli.data.insert.assert_not_called()
    
    def test_session_duration_is_7_days(self):
        """Should set expiration to 7 days from now"""
        from datetime import datetime, timedelta
        
        auth = zAuth(self.mock_zcli)
        
        self.mock_zcli.data.insert = Mock()
        self.mock_zcli.data.delete = Mock()
        
        # Save session via modular interface
        before_save = datetime.now()
        auth.session_persistence.save_session("user", "hash")
        after_save = datetime.now()
        
        # Get expires_at value
        insert_args = self.mock_zcli.data.insert.call_args
        fields = insert_args[1]["fields"]
        values = insert_args[1]["values"]
        expires_at_idx = fields.index("expires_at")
        expires_at = datetime.fromisoformat(values[expires_at_idx])
        
        # Verify it's approximately 7 days from now
        expected_min = before_save + timedelta(days=7, seconds=-5)
        expected_max = after_save + timedelta(days=7, seconds=5)
        
        self.assertGreaterEqual(expires_at, expected_min)
        self.assertLessEqual(expires_at, expected_max)


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
    
    # NEW: Persistent sessions tests (Week 3.2)
    suite.addTests(loader.loadTestsFromTestCase(TestPersistentSessions))
    
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
