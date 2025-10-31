#!/usr/bin/env python3
# zTestSuite/zAuth_Comprehensive_Test.py

"""
Comprehensive Test Suite for Three-Tier zAuth Architecture (v1.5.4+)

Tests the complete three-tier authentication system:
- Layer 1: zSession Auth (Internal zCLI users)
- Layer 2: Application Auth (External app users, multi-app support)
- Layer 3: Dual-Auth (Both contexts active simultaneously)

Includes:
- Updated session structure tests (nested zAuth)
- Multi-app support tests (Scenario B)
- Context switching tests
- Concurrent user tests (Scenario A)
- Authentication failure tests
"""

import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import sys

# Add parent directory to path to import zCLI
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zAuth.zAuth import zAuth
from zCLI.subsystems.zAuth.zAuth_modules.auth_authentication import Authentication
from zCLI.subsystems.zDisplay.zDisplay import zDisplay
from zCLI.subsystems.zConfig.zConfig_modules import (
    ZAUTH_KEY_ZSESSION,
    ZAUTH_KEY_APPLICATIONS,
    ZAUTH_KEY_ACTIVE_APP,
    ZAUTH_KEY_AUTHENTICATED,
    ZAUTH_KEY_ID,
    ZAUTH_KEY_USERNAME,
    ZAUTH_KEY_ROLE,
    ZAUTH_KEY_API_KEY,
    ZAUTH_KEY_ACTIVE_CONTEXT,
    ZAUTH_KEY_DUAL_MODE,
    CONTEXT_ZSESSION,
    CONTEXT_APPLICATION,
    CONTEXT_DUAL
)


# ═══════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════

def create_mock_session():
    """Create a mock session with new nested zAuth structure."""
    return {
        "zMode": "Terminal",
        "zAuth": {
            ZAUTH_KEY_ZSESSION: {
                ZAUTH_KEY_AUTHENTICATED: False,
                ZAUTH_KEY_ID: None,
                ZAUTH_KEY_USERNAME: None,
                ZAUTH_KEY_ROLE: None,
                ZAUTH_KEY_API_KEY: None
            },
            ZAUTH_KEY_APPLICATIONS: {},
            ZAUTH_KEY_ACTIVE_APP: None,
            ZAUTH_KEY_ACTIVE_CONTEXT: None,
            ZAUTH_KEY_DUAL_MODE: False
        }
    }


def create_mock_zcli_with_session():
    """Create a mock zCLI instance with display and session."""
    mock_zcli = Mock()
    mock_zcli.session = create_mock_session()
    mock_zcli.logger = Mock()
    mock_zcli.display = zDisplay(mock_zcli)
    return mock_zcli


# ═══════════════════════════════════════════════════════════
# Test Class 1: Updated Initialization Tests
# ═══════════════════════════════════════════════════════════

class TestzAuthInitializationUpdated(unittest.TestCase):
    """Test zAuth subsystem initialization with new nested structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
    
    def test_zauth_initialization(self):
        """Test that zAuth initializes correctly."""
        auth = zAuth(self.mock_zcli)
        
        self.assertIsNotNone(auth)
        self.assertEqual(auth.zcli, self.mock_zcli)
        self.assertEqual(auth.session, self.mock_zcli.session)
    
    def test_session_structure_three_tier(self):
        """Test that session has proper three-tier zAuth structure."""
        auth = zAuth(self.mock_zcli)
        
        # Check top-level zAuth
        self.assertIn("zAuth", auth.session)
        
        # Check Layer 1 (zSession)
        self.assertIn(ZAUTH_KEY_ZSESSION, auth.session["zAuth"])
        self.assertIn(ZAUTH_KEY_AUTHENTICATED, auth.session["zAuth"][ZAUTH_KEY_ZSESSION])
        self.assertIn(ZAUTH_KEY_USERNAME, auth.session["zAuth"][ZAUTH_KEY_ZSESSION])
        
        # Check Layer 2 (Applications - multi-app support)
        self.assertIn(ZAUTH_KEY_APPLICATIONS, auth.session["zAuth"])
        self.assertEqual(auth.session["zAuth"][ZAUTH_KEY_APPLICATIONS], {})
        
        # Check context management
        self.assertIn(ZAUTH_KEY_ACTIVE_APP, auth.session["zAuth"])
        self.assertIn(ZAUTH_KEY_ACTIVE_CONTEXT, auth.session["zAuth"])
        self.assertIn(ZAUTH_KEY_DUAL_MODE, auth.session["zAuth"])


# ═══════════════════════════════════════════════════════════
# Test Class 2: Layer 1 (zSession) Authentication Tests
# ═══════════════════════════════════════════════════════════

class TestzSessionAuthentication(unittest.TestCase):
    """Test Layer 1: zSession authentication (internal zCLI users)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
        self.auth = Authentication(self.mock_zcli)
    
    def test_is_authenticated_initially_false(self):
        """Test that user is not authenticated initially."""
        self.assertFalse(self.auth.is_authenticated())
    
    def test_is_authenticated_after_zsession_login(self):
        """Test authentication status after zSession login."""
        # Simulate successful zSession login
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice@company.com",
            ZAUTH_KEY_API_KEY: "zcli_token_123",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "zcli_user_001"
        })
        
        self.assertTrue(self.auth.is_authenticated())
    
    def test_get_credentials_zsession(self):
        """Test getting zSession credentials."""
        # Login
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "bob@company.com",
            ZAUTH_KEY_API_KEY: "zcli_token_456",
            ZAUTH_KEY_ROLE: "user",
            ZAUTH_KEY_ID: "zcli_user_002"
        })
        
        creds = self.auth.get_credentials()
        self.assertIsNotNone(creds)
        self.assertEqual(creds[ZAUTH_KEY_USERNAME], "bob@company.com")
        self.assertEqual(creds[ZAUTH_KEY_ROLE], "user")
        self.assertTrue(creds[ZAUTH_KEY_AUTHENTICATED])
    
    def test_logout_zsession_only(self):
        """Test logout from zSession only."""
        # Login to zSession
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "charlie@company.com",
            ZAUTH_KEY_API_KEY: "zcli_token_789",
            ZAUTH_KEY_ROLE: "user",
            ZAUTH_KEY_ID: "zcli_user_003"
        })
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_ZSESSION
        
        # Logout
        result = self.auth.logout(context="zSession")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("zSession", result["cleared"][0])
        self.assertFalse(self.auth.is_authenticated())


# ═══════════════════════════════════════════════════════════
# Test Class 3: Layer 2 (Application) Multi-App Tests
# ═══════════════════════════════════════════════════════════

class TestMultiAppAuthentication(unittest.TestCase):
    """Test Layer 2: Application authentication with multi-app support (Scenario B)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
        self.auth = Authentication(self.mock_zcli)
    
    def test_authenticate_single_app(self):
        """Test authenticating to a single application."""
        # Authenticate to ecommerce app
        result = self.auth.authenticate_app_user(
            "ecommerce_store",
            "store_token_abc",
            {"user_model": "@.store_users.users"}
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["app_name"], "ecommerce_store")
        self.assertIn(ZAUTH_KEY_USERNAME, result["user"])
        
        # Check session structure
        self.assertIn("ecommerce_store", self.mock_zcli.session["zAuth"][ZAUTH_KEY_APPLICATIONS])
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_APP], "ecommerce_store")
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT], CONTEXT_APPLICATION)
    
    def test_authenticate_multiple_apps_simultaneously(self):
        """Test authenticating to multiple apps simultaneously (Scenario B)."""
        # Authenticate to app 1
        result1 = self.auth.authenticate_app_user(
            "ecommerce_store",
            "store_token_abc"
        )
        self.assertEqual(result1["status"], "success")
        
        # Authenticate to app 2
        result2 = self.auth.authenticate_app_user(
            "analytics_dashboard",
            "analytics_token_xyz"
        )
        self.assertEqual(result2["status"], "success")
        
        # Authenticate to app 3
        result3 = self.auth.authenticate_app_user(
            "admin_panel",
            "admin_token_123"
        )
        self.assertEqual(result3["status"], "success")
        
        # Verify all 3 apps are authenticated simultaneously
        apps = self.mock_zcli.session["zAuth"][ZAUTH_KEY_APPLICATIONS]
        self.assertEqual(len(apps), 3)
        self.assertIn("ecommerce_store", apps)
        self.assertIn("analytics_dashboard", apps)
        self.assertIn("admin_panel", apps)
        
        # Active app should be the last authenticated
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_APP], "admin_panel")
    
    def test_switch_between_apps(self):
        """Test switching between authenticated apps."""
        # Authenticate to 2 apps
        self.auth.authenticate_app_user("store", "token1")
        self.auth.authenticate_app_user("analytics", "token2")
        
        # Switch to store
        success = self.auth.switch_app("store")
        self.assertTrue(success)
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_APP], "store")
        
        # Switch to analytics
        success = self.auth.switch_app("analytics")
        self.assertTrue(success)
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_APP], "analytics")
        
        # Try switching to non-authenticated app
        success = self.auth.switch_app("non_existent")
        self.assertFalse(success)
    
    def test_get_app_user_for_each_app(self):
        """Test retrieving different app user identities."""
        # Authenticate to 2 apps
        self.auth.authenticate_app_user("store", "token1")
        self.auth.authenticate_app_user("analytics", "token2")
        
        # Get store user
        store_user = self.auth.get_app_user("store")
        self.assertIsNotNone(store_user)
        self.assertIn(ZAUTH_KEY_USERNAME, store_user)
        
        # Get analytics user
        analytics_user = self.auth.get_app_user("analytics")
        self.assertIsNotNone(analytics_user)
        self.assertIn(ZAUTH_KEY_USERNAME, analytics_user)
        
        # Get non-existent app
        none_user = self.auth.get_app_user("non_existent")
        self.assertIsNone(none_user)
    
    def test_logout_from_single_app_keeps_others(self):
        """Test logging out from one app keeps other apps authenticated."""
        # Authenticate to 3 apps
        self.auth.authenticate_app_user("app1", "token1")
        self.auth.authenticate_app_user("app2", "token2")
        self.auth.authenticate_app_user("app3", "token3")
        
        # Logout from app2
        result = self.auth.logout(context="application", app_name="app2")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("application/app2", result["cleared"][0])
        
        # Verify app1 and app3 still authenticated
        apps = self.mock_zcli.session["zAuth"][ZAUTH_KEY_APPLICATIONS]
        self.assertEqual(len(apps), 2)
        self.assertIn("app1", apps)
        self.assertIn("app3", apps)
        self.assertNotIn("app2", apps)
    
    def test_logout_all_apps(self):
        """Test logging out from all apps."""
        # Authenticate to 3 apps
        self.auth.authenticate_app_user("app1", "token1")
        self.auth.authenticate_app_user("app2", "token2")
        self.auth.authenticate_app_user("app3", "token3")
        
        # Logout from all apps
        result = self.auth.logout(context="all_apps")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["cleared"]), 3)
        
        # Verify all apps cleared
        apps = self.mock_zcli.session["zAuth"][ZAUTH_KEY_APPLICATIONS]
        self.assertEqual(len(apps), 0)
        self.assertIsNone(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_APP])


# ═══════════════════════════════════════════════════════════
# Test Class 4: Layer 3 (Dual-Auth) Tests
# ═══════════════════════════════════════════════════════════

class TestDualAuthentication(unittest.TestCase):
    """Test Layer 3: Dual-auth (zSession + Application simultaneously)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
        self.auth = Authentication(self.mock_zcli)
    
    def test_dual_auth_zsession_then_app(self):
        """Test dual-auth: login to zSession then authenticate to app."""
        # First: zSession login
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice@company.com",
            ZAUTH_KEY_API_KEY: "zcli_token",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "zcli_001"
        })
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_ZSESSION
        
        # Then: Authenticate to app
        result = self.auth.authenticate_app_user("store", "store_token")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["context"], CONTEXT_DUAL)
        self.assertTrue(self.mock_zcli.session["zAuth"][ZAUTH_KEY_DUAL_MODE])
    
    def test_get_active_user_in_dual_mode(self):
        """Test get_active_user returns both contexts in dual mode."""
        # Setup dual-auth
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice@company.com",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "zcli_001",
            ZAUTH_KEY_API_KEY: "zcli_token"
        })
        self.auth.authenticate_app_user("store", "store_token")
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_DUAL
        
        # Get active user
        user = self.auth.get_active_user()
        
        self.assertIn("zSession", user)
        self.assertIn("application", user)
        self.assertEqual(user["zSession"][ZAUTH_KEY_USERNAME], "alice@company.com")
        self.assertIsNotNone(user["application"])
    
    def test_logout_zsession_in_dual_mode_switches_to_app(self):
        """Test logging out zSession in dual mode switches to application context."""
        # Setup dual-auth
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice@company.com",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "zcli_001",
            ZAUTH_KEY_API_KEY: "zcli_token"
        })
        self.auth.authenticate_app_user("store", "store_token")
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT] = CONTEXT_DUAL
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_DUAL_MODE] = True
        
        # Logout zSession
        self.auth.logout(context="zSession")
        
        # Should switch to application context
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT], CONTEXT_APPLICATION)
        self.assertFalse(self.mock_zcli.session["zAuth"][ZAUTH_KEY_DUAL_MODE])
        
        # Application should still be authenticated
        self.assertIn("store", self.mock_zcli.session["zAuth"][ZAUTH_KEY_APPLICATIONS])


# ═══════════════════════════════════════════════════════════
# Test Class 5: Context Switching Tests
# ═══════════════════════════════════════════════════════════

class TestContextSwitching(unittest.TestCase):
    """Test context switching between zSession, application, and dual modes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
        self.auth = Authentication(self.mock_zcli)
    
    def test_set_active_context_zsession(self):
        """Test switching to zSession context."""
        # Login to zSession
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "001",
            ZAUTH_KEY_API_KEY: "token"
        })
        
        success = self.auth.set_active_context(CONTEXT_ZSESSION)
        
        self.assertTrue(success)
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT], CONTEXT_ZSESSION)
    
    def test_set_active_context_application(self):
        """Test switching to application context."""
        # Authenticate to app
        self.auth.authenticate_app_user("store", "token")
        
        success = self.auth.set_active_context(CONTEXT_APPLICATION)
        
        self.assertTrue(success)
        self.assertEqual(self.mock_zcli.session["zAuth"][ZAUTH_KEY_ACTIVE_CONTEXT], CONTEXT_APPLICATION)
    
    def test_set_active_context_dual_requires_both(self):
        """Test dual context requires both zSession and application authenticated."""
        # Only zSession authenticated
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "001",
            ZAUTH_KEY_API_KEY: "token"
        })
        
        # Try to set dual mode → should fail
        success = self.auth.set_active_context(CONTEXT_DUAL)
        self.assertFalse(success)
        
        # Now authenticate to app
        self.auth.authenticate_app_user("store", "token")
        
        # Try again → should succeed
        success = self.auth.set_active_context(CONTEXT_DUAL)
        self.assertTrue(success)
        self.assertTrue(self.mock_zcli.session["zAuth"][ZAUTH_KEY_DUAL_MODE])
    
    def test_get_active_user_respects_context(self):
        """Test get_active_user returns correct user based on active context."""
        # Setup: Login to zSession and app
        self.mock_zcli.session["zAuth"][ZAUTH_KEY_ZSESSION].update({
            ZAUTH_KEY_AUTHENTICATED: True,
            ZAUTH_KEY_USERNAME: "alice@company.com",
            ZAUTH_KEY_ROLE: "admin",
            ZAUTH_KEY_ID: "zcli_001",
            ZAUTH_KEY_API_KEY: "zcli_token"
        })
        self.auth.authenticate_app_user("store", "store_token")
        
        # Set context to zSession
        self.auth.set_active_context(CONTEXT_ZSESSION)
        user = self.auth.get_active_user()
        self.assertEqual(user[ZAUTH_KEY_USERNAME], "alice@company.com")
        
        # Set context to application
        self.auth.set_active_context(CONTEXT_APPLICATION)
        user = self.auth.get_active_user()
        self.assertIn(ZAUTH_KEY_USERNAME, user)  # App user
        
        # Set context to dual
        self.auth.set_active_context(CONTEXT_DUAL)
        user = self.auth.get_active_user()
        self.assertIn("zSession", user)
        self.assertIn("application", user)


# ═══════════════════════════════════════════════════════════
# Test Class 6: Authentication Failure Tests
# ═══════════════════════════════════════════════════════════

class TestAuthenticationFailures(unittest.TestCase):
    """Test authentication failure scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_zcli = create_mock_zcli_with_session()
        self.auth = Authentication(self.mock_zcli)
    
    def test_get_credentials_when_not_authenticated(self):
        """Test getting credentials when not authenticated returns None."""
        creds = self.auth.get_credentials()
        self.assertIsNone(creds)
    
    def test_switch_app_fails_for_non_authenticated_app(self):
        """Test switching to non-authenticated app fails."""
        success = self.auth.switch_app("non_existent_app")
        self.assertFalse(success)
    
    def test_set_context_zsession_fails_without_auth(self):
        """Test setting zSession context fails without authentication."""
        success = self.auth.set_active_context(CONTEXT_ZSESSION)
        self.assertFalse(success)
    
    def test_set_context_application_fails_without_auth(self):
        """Test setting application context fails without authentication."""
        success = self.auth.set_active_context(CONTEXT_APPLICATION)
        self.assertFalse(success)
    
    def test_logout_application_without_app_name_fails(self):
        """Test logging out from application without app_name fails."""
        result = self.auth.logout(context="application", app_name=None)
        self.assertEqual(result["status"], "error")
        self.assertIn("app_name required", result["reason"])
    
    def test_logout_specific_app_not_authenticated_fails(self):
        """Test logging out from non-authenticated app fails."""
        result = self.auth.logout(context="application", app_name="non_existent")
        self.assertEqual(result["status"], "error")
        self.assertIn("Not authenticated", result["reason"])


# ═══════════════════════════════════════════════════════════
# Main Test Runner
# ═══════════════════════════════════════════════════════════

def run_tests(verbose=True):
    """Run all comprehensive three-tier authentication tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes in logical order
    suite.addTests(loader.loadTestsFromTestCase(TestzAuthInitializationUpdated))
    suite.addTests(loader.loadTestsFromTestCase(TestzSessionAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAppAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestDualAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestContextSwitching))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationFailures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("zAuth Comprehensive Three-Tier Authentication Test Suite (v1.5.4+)")
    print("=" * 70)
    print()
    
    # Run tests
    result = run_tests(verbose=True)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
