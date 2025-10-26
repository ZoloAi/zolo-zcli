#!/usr/bin/env python3
"""
zAuth Comprehensive Test Suite (v1.5.4 Week 3.4)

This test suite provides comprehensive coverage for all zAuth modules:
- password_security: bcrypt hashing edge cases
- session_persistence: SQLite session management edge cases
- authentication: Login/logout edge cases
- rbac: Role and permission edge cases

Goal: Make zAuth bulletproof before moving to Layer 1 display work.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from zCLI import zCLI


class TestPasswordSecurityEdgeCases(unittest.TestCase):
    """Comprehensive tests for password_security module edge cases."""
    
    def setUp(self):
        """Set up password security module for testing."""
        from zCLI.subsystems.zAuth.zAuth_modules import PasswordSecurity
        self.pwd_security = PasswordSecurity()
    
    def test_empty_password_raises_error(self):
        """Empty password should raise ValueError."""
        with self.assertRaises(ValueError):
            self.pwd_security.hash_password("")
    
    def test_none_password_raises_error(self):
        """None password should raise ValueError."""
        with self.assertRaises(ValueError):
            self.pwd_security.hash_password(None)
    
    def test_whitespace_only_password_is_valid(self):
        """Whitespace-only password should be valid (bcrypt accepts it)."""
        hashed = self.pwd_security.hash_password("   ")
        self.assertTrue(self.pwd_security.verify_password("   ", hashed))
    
    def test_password_with_unicode_characters(self):
        """Password with unicode characters should work."""
        password = "pass🔐word™"
        hashed = self.pwd_security.hash_password(password)
        self.assertTrue(self.pwd_security.verify_password(password, hashed))
    
    def test_password_with_special_characters(self):
        """Password with special characters should work."""
        password = "p@ss!w#rd$%^&*()"
        hashed = self.pwd_security.hash_password(password)
        self.assertTrue(self.pwd_security.verify_password(password, hashed))
    
    def test_very_long_password_truncated_to_72_bytes(self):
        """Password > 72 bytes should be truncated and still verify."""
        # Create password > 72 bytes
        password = "a" * 100  # 100 bytes
        hashed = self.pwd_security.hash_password(password)
        
        # First 72 bytes should match
        self.assertTrue(self.pwd_security.verify_password(password, hashed))
        
        # But different after 72 bytes should also match (both truncated)
        password_variant = ("a" * 72) + "b" * 28
        self.assertTrue(self.pwd_security.verify_password(password_variant, hashed))
    
    def test_utf8_multibyte_characters_truncation(self):
        """UTF-8 multibyte characters should be handled correctly at 72-byte boundary."""
        # Use 3-byte UTF-8 characters (e.g., emoji)
        # 24 emojis = 72 bytes exactly
        password = "🔐" * 24  # Each emoji is 3 bytes
        hashed = self.pwd_security.hash_password(password)
        self.assertTrue(self.pwd_security.verify_password(password, hashed))
    
    def test_case_sensitive_password(self):
        """Password verification should be case-sensitive."""
        hashed = self.pwd_security.hash_password("Password123")
        self.assertTrue(self.pwd_security.verify_password("Password123", hashed))
        self.assertFalse(self.pwd_security.verify_password("password123", hashed))
        self.assertFalse(self.pwd_security.verify_password("PASSWORD123", hashed))
    
    def test_verify_with_empty_password_returns_false(self):
        """Verifying with empty password should return False."""
        hashed = self.pwd_security.hash_password("test123")
        self.assertFalse(self.pwd_security.verify_password("", hashed))
    
    def test_verify_with_none_password_returns_false(self):
        """Verifying with None password should return False."""
        hashed = self.pwd_security.hash_password("test123")
        self.assertFalse(self.pwd_security.verify_password(None, hashed))
    
    def test_verify_with_invalid_hash_returns_false(self):
        """Verifying with invalid hash should return False (not raise)."""
        self.assertFalse(self.pwd_security.verify_password("password", "invalid_hash"))
    
    def test_verify_with_empty_hash_returns_false(self):
        """Verifying with empty hash should return False."""
        self.assertFalse(self.pwd_security.verify_password("password", ""))
    
    def test_hash_format_is_bcrypt(self):
        """Hashed password should follow bcrypt format."""
        hashed = self.pwd_security.hash_password("test123")
        self.assertTrue(hashed.startswith("$2b$"))  # bcrypt format
        self.assertEqual(len(hashed), 60)  # bcrypt hash length
    
    def test_same_password_produces_different_hashes(self):
        """Same password should produce different hashes (salted)."""
        hash1 = self.pwd_security.hash_password("test123")
        hash2 = self.pwd_security.hash_password("test123")
        self.assertNotEqual(hash1, hash2)
        
        # But both should verify correctly
        self.assertTrue(self.pwd_security.verify_password("test123", hash1))
        self.assertTrue(self.pwd_security.verify_password("test123", hash2))
    
    def test_password_hashing_is_slow_enough(self):
        """Password hashing should take reasonable time (security vs performance)."""
        import time
        start = time.time()
        self.pwd_security.hash_password("test123")
        duration = time.time() - start
        
        # Should take between 0.1s and 2s (12 rounds)
        self.assertGreater(duration, 0.05)  # Not too fast (security)
        self.assertLess(duration, 3.0)  # Not too slow (UX)


class TestSessionPersistenceEdgeCases(unittest.TestCase):
    """Comprehensive tests for session_persistence module edge cases."""
    
    def setUp(self):
        """Set up test workspace and zCLI instance."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
        
        self.z = zCLI({
            "zWorkspace": str(self.workspace_path),
            "zMode": "Terminal"
        })
        
        # Explicitly initialize sessions database (needed because during __init__, 
        # loader/data subsystems aren't ready yet)
        self.z.auth.session_persistence.ensure_sessions_db()
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_save_session_generates_unique_session_ids(self):
        """Each session should have a unique session ID."""
        session_id1 = self.z.auth.session_persistence.save_session(
            "user1", "hash1", "uid1"
        )
        session_id2 = self.z.auth.session_persistence.save_session(
            "user2", "hash2", "uid2"
        )
        
        self.assertIsNotNone(session_id1)
        self.assertIsNotNone(session_id2)
        self.assertNotEqual(session_id1, session_id2)
    
    def test_save_session_replaces_existing_session_for_user(self):
        """Saving a new session should replace existing session for same user."""
        # Save first session
        session_id1 = self.z.auth.session_persistence.save_session(
            "user1", "hash1", "uid1"
        )
        self.assertIsNotNone(session_id1)
        
        # Save second session for same user
        session_id2 = self.z.auth.session_persistence.save_session(
            "user1", "hash2", "uid1"
        )
        self.assertIsNotNone(session_id2)
        self.assertNotEqual(session_id1, session_id2)
        
        # Only one session should exist for user1
        results = self.z.data.select(table="sessions", where="username = 'user1'")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["session_id"], session_id2)
    
    def test_load_session_ignores_expired_sessions(self):
        """Expired sessions should not be loaded."""
        # Create an expired session manually
        from datetime import datetime, timedelta
        
        expired_time = (datetime.now() - timedelta(days=1)).isoformat()
        
        self.z.data.insert(
            table="sessions",
            fields=["session_id", "user_id", "username", "role", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
            values=["expired_id", "user1", "expired_user", "user", "hash", "token", expired_time, expired_time, expired_time]
        )
        
        # Clear session and try to load
        self.z.session["zAuth"] = {}
        self.z.auth.session_persistence.load_session()
        
        # Session should not be restored
        self.assertIsNone(self.z.session["zAuth"].get("username"))
    
    def test_cleanup_expired_removes_only_expired_sessions(self):
        """Cleanup should remove only expired sessions, not valid ones."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        expired_time = (now - timedelta(days=1)).isoformat()
        future_time = (now + timedelta(days=7)).isoformat()
        
        # Insert expired session
        self.z.data.insert(
            table="sessions",
            fields=["session_id", "user_id", "username", "role", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
            values=["expired_id", "user1", "expired_user", "user", "hash1", "token1", expired_time, expired_time, expired_time]
        )
        
        # Insert valid session
        self.z.data.insert(
            table="sessions",
            fields=["session_id", "user_id", "username", "role", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
            values=["valid_id", "user2", "valid_user", "user", "hash2", "token2", now.isoformat(), future_time, now.isoformat()]
        )
        
        # Run cleanup
        deleted = self.z.auth.session_persistence.cleanup_expired()
        
        # Should delete 1 expired session
        self.assertEqual(deleted, 1)
        
        # Valid session should still exist
        results = self.z.data.select(table="sessions", where="session_id = 'valid_id'")
        self.assertEqual(len(results), 1)
        
        # Expired session should be gone
        results = self.z.data.select(table="sessions", where="session_id = 'expired_id'")
        self.assertEqual(len(results), 0)
    
    def test_session_duration_is_7_days(self):
        """Session expiration should be set to 7 days from creation."""
        from datetime import datetime, timedelta
        
        before = datetime.now()
        session_id = self.z.auth.session_persistence.save_session(
            "user1", "hash1", "uid1"
        )
        after = datetime.now()
        
        # Get session
        results = self.z.data.select(table="sessions", where=f"session_id = '{session_id}'")
        self.assertEqual(len(results), 1)
        
        expires_at = datetime.fromisoformat(results[0]["expires_at"])
        
        # Expiration should be ~7 days from now (within 1 minute tolerance)
        expected_min = before + timedelta(days=7)
        expected_max = after + timedelta(days=7)
        
        self.assertGreater(expires_at, expected_min - timedelta(minutes=1))
        self.assertLess(expires_at, expected_max + timedelta(minutes=1))
    
    def test_save_session_with_custom_role(self):
        """Session should save custom role."""
        session_id = self.z.auth.session_persistence.save_session(
            "admin_user", "hash1", "admin_id", role="admin"
        )
        
        results = self.z.data.select(table="sessions", where=f"session_id = '{session_id}'")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "admin")
    
    def test_save_session_defaults_to_user_role(self):
        """Session should default to 'user' role if not specified."""
        session_id = self.z.auth.session_persistence.save_session(
            "regular_user", "hash1", "user_id"
        )
        
        results = self.z.data.select(table="sessions", where=f"session_id = '{session_id}'")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["role"], "user")
    
    def test_load_session_updates_last_accessed(self):
        """Loading a session should update last_accessed timestamp."""
        from datetime import datetime, timedelta
        import time
        
        # Create session with old last_accessed
        old_time = (datetime.now() - timedelta(hours=1)).isoformat()
        future_time = (datetime.now() + timedelta(days=7)).isoformat()
        
        self.z.data.insert(
            table="sessions",
            fields=["session_id", "user_id", "username", "role", "password_hash", "token", "created_at", "expires_at", "last_accessed"],
            values=["test_id", "user1", "test_user", "user", "hash", "token", old_time, future_time, old_time]
        )
        
        # Clear and load session
        self.z.session["zAuth"] = {}
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        self.z.auth.session_persistence.load_session()
        
        # Check last_accessed was updated
        results = self.z.data.select(table="sessions", where="session_id = 'test_id'")
        self.assertEqual(len(results), 1)
        
        last_accessed = datetime.fromisoformat(results[0]["last_accessed"])
        old_accessed = datetime.fromisoformat(old_time)
        
        # last_accessed should be newer than old_time
        self.assertGreater(last_accessed, old_accessed)


class TestAuthenticationEdgeCases(unittest.TestCase):
    """Comprehensive tests for authentication module edge cases."""
    
    def setUp(self):
        """Set up test workspace and zCLI instance."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
        
        self.z = zCLI({
            "zWorkspace": str(self.workspace_path),
            "zMode": "Terminal"
        })
        
        # Initialize sessions database for tests that need persistence
        self.z.auth.session_persistence.ensure_sessions_db()
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_is_authenticated_requires_both_username_and_token(self):
        """Authentication requires both username AND API key."""
        # Only username
        self.z.session["zAuth"] = {"username": "user1", "API_Key": None}
        self.assertFalse(self.z.auth.is_authenticated())
        
        # Only API key
        self.z.session["zAuth"] = {"username": None, "API_Key": "token"}
        self.assertFalse(self.z.auth.is_authenticated())
        
        # Both present
        self.z.session["zAuth"] = {"username": "user1", "API_Key": "token"}
        self.assertTrue(self.z.auth.is_authenticated())
    
    def test_get_credentials_returns_none_when_not_authenticated(self):
        """get_credentials should return None when not authenticated."""
        self.z.session["zAuth"] = {}
        self.assertIsNone(self.z.auth.get_credentials())
    
    def test_get_credentials_returns_session_data_when_authenticated(self):
        """get_credentials should return session data when authenticated."""
        self.z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "admin",
            "API_Key": "token123"
        }
        
        creds = self.z.auth.get_credentials()
        self.assertIsNotNone(creds)
        self.assertEqual(creds["username"], "testuser")
        self.assertEqual(creds["role"], "admin")
    
    def test_logout_clears_all_session_fields(self):
        """Logout should clear all zAuth session fields."""
        # Set up authenticated session
        self.z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "admin",
            "API_Key": "token123",
            "session_id": "session123"
        }
        
        # Logout
        result = self.z.auth.logout()
        
        # All fields should be None
        self.assertIsNone(self.z.session["zAuth"].get("id"))
        self.assertIsNone(self.z.session["zAuth"].get("username"))
        self.assertIsNone(self.z.session["zAuth"].get("role"))
        self.assertIsNone(self.z.session["zAuth"].get("API_Key"))
        self.assertIsNone(self.z.session["zAuth"].get("session_id"))
        
        self.assertEqual(result["status"], "success")
    
    def test_logout_deletes_persistent_session(self):
        """Logout should delete persistent session from database."""
        # Create persistent session
        session_id = self.z.auth.session_persistence.save_session(
            "testuser", "hash123", "user123"
        )
        
        # Set up session
        self.z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "user",
            "API_Key": "token123",
            "session_id": session_id
        }
        
        # Verify session exists
        results = self.z.data.select(table="sessions", where="username = 'testuser'")
        self.assertEqual(len(results), 1)
        
        # Logout
        self.z.auth.logout()
        
        # Session should be deleted
        results = self.z.data.select(table="sessions", where="username = 'testuser'")
        self.assertEqual(len(results), 0)
    
    def test_status_returns_correct_authenticated_status(self):
        """status() should return correct authentication status."""
        # Not authenticated
        self.z.session["zAuth"] = {}
        result = self.z.auth.status()
        self.assertEqual(result["status"], "not_authenticated")
        
        # Authenticated
        self.z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "admin",
            "API_Key": "token123"
        }
        result = self.z.auth.status()
        self.assertEqual(result["status"], "authenticated")
        self.assertIn("user", result)
        self.assertEqual(result["user"]["username"], "testuser")


class TestRBACEdgeCases(unittest.TestCase):
    """Additional edge cases for RBAC module (beyond existing 18 tests)."""
    
    def setUp(self):
        """Set up test workspace and zCLI instance."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
        
        self.z = zCLI({
            "zWorkspace": str(self.workspace_path),
            "zMode": "Terminal"
        })
        
        # Initialize permissions database for RBAC tests
        self.z.auth.rbac.ensure_permissions_db()
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_has_role_with_empty_string_returns_false(self):
        """has_role with empty string should return False."""
        self.z.session["zAuth"] = {"username": "user", "role": "admin", "API_Key": "token"}
        self.assertFalse(self.z.auth.has_role(""))
    
    def test_has_permission_with_empty_string_returns_false(self):
        """has_permission with empty string should return False."""
        self.z.session["zAuth"] = {"id": "user123", "username": "user", "API_Key": "token"}
        self.assertFalse(self.z.auth.has_permission(""))
    
    def test_grant_permission_to_nonexistent_user(self):
        """Granting permission to non-existent user should still work (DB allows it)."""
        result = self.z.auth.grant_permission("nonexistent_user", "test.permission")
        self.assertTrue(result)
        
        # Permission should be in DB
        self.z.session["zAuth"] = {"id": "nonexistent_user", "username": "test", "API_Key": "token"}
        self.assertTrue(self.z.auth.has_permission("test.permission"))
    
    def test_revoke_nonexistent_permission_succeeds(self):
        """Revoking non-existent permission should succeed (idempotent)."""
        result = self.z.auth.revoke_permission("user123", "nonexistent.permission")
        self.assertTrue(result)
    
    def test_grant_permission_idempotent(self):
        """Granting same permission twice should be idempotent."""
        result1 = self.z.auth.grant_permission("user123", "test.permission", "admin")
        result2 = self.z.auth.grant_permission("user123", "test.permission", "admin")
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        
        # Should only be one record
        self.z.auth.rbac.ensure_permissions_db()
        results = self.z.data.select(
            table="user_permissions",
            where="user_id = 'user123' AND permission = 'test.permission'"
        )
        self.assertEqual(len(results), 1)
    
    def test_permission_granted_by_tracking(self):
        """Permission grant should track who granted it."""
        self.z.session["zAuth"] = {"username": "admin_user", "API_Key": "token"}
        
        self.z.auth.grant_permission("user123", "test.permission", granted_by="admin_user")
        
        # Check granted_by is recorded
        self.z.auth.rbac.ensure_permissions_db()
        results = self.z.data.select(
            table="user_permissions",
            where="user_id = 'user123'"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["granted_by"], "admin_user")
    
    def test_permission_granted_at_timestamp(self):
        """Permission grant should record timestamp."""
        from datetime import datetime
        
        before = datetime.now()
        self.z.auth.grant_permission("user123", "test.permission")
        after = datetime.now()
        
        # Check granted_at timestamp
        self.z.auth.rbac.ensure_permissions_db()
        results = self.z.data.select(
            table="user_permissions",
            where="user_id = 'user123'"
        )
        self.assertEqual(len(results), 1)
        
        granted_at = datetime.fromisoformat(results[0]["granted_at"])
        self.assertGreater(granted_at, before - timedelta(seconds=1))
        self.assertLess(granted_at, after + timedelta(seconds=1))
    
    def test_multiple_permissions_for_same_user(self):
        """User can have multiple permissions."""
        self.z.auth.grant_permission("user123", "permission1")
        self.z.auth.grant_permission("user123", "permission2")
        self.z.auth.grant_permission("user123", "permission3")
        
        # Check all permissions exist
        self.z.session["zAuth"] = {"id": "user123", "username": "test", "API_Key": "token"}
        self.assertTrue(self.z.auth.has_permission("permission1"))
        self.assertTrue(self.z.auth.has_permission("permission2"))
        self.assertTrue(self.z.auth.has_permission("permission3"))
    
    def test_revoke_one_permission_keeps_others(self):
        """Revoking one permission should keep others intact."""
        self.z.auth.grant_permission("user123", "permission1")
        self.z.auth.grant_permission("user123", "permission2")
        
        # Revoke one
        self.z.auth.revoke_permission("user123", "permission1")
        
        # Check permissions
        self.z.session["zAuth"] = {"id": "user123", "username": "test", "API_Key": "token"}
        self.assertFalse(self.z.auth.has_permission("permission1"))
        self.assertTrue(self.z.auth.has_permission("permission2"))


def suite():
    """Create comprehensive test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordSecurityEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionPersistenceEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestRBACEdgeCases))
    
    return suite


def run_tests(verbose=False):
    """Run all comprehensive zAuth tests (for test_factory integration)."""
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    return runner.run(suite())


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())

