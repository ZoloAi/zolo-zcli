#!/usr/bin/env python3
"""
zRBAC Test Suite - Comprehensive RBAC Testing (v1.5.4 Week 3.3)

Tests:
- RBAC parsing (inline _rbac directives)
- Access control enforcement (require_auth, require_role, require_permission)
- Public access (default behavior)
- Role inheritance and permission checks
- Access denied handling
"""

import unittest
from pathlib import Path
import tempfile
import shutil
from zCLI import zCLI


class TestRBACParsing(unittest.TestCase):
    """Test RBAC directive parsing and extraction."""
    
    def setUp(self):
        """Set up test workspace."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_public_access_default(self):
        """No _rbac should result in public access (no restrictions)."""
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Public Action"]
  
  "^Public Action":
    zDisplay:
      event: text
      content: "Public content"
""")
        
        z = zCLI({"zSpace": str(self.workspace_path)})
        data = z.loader.handle("@.zUI.test")
        
        self.assertIn("zVaF", data)
        public_action = data["zVaF"].get("^Public Action")
        self.assertIsNotNone(public_action)
        self.assertNotIn("_rbac", public_action)
    
    def test_inline_rbac_require_auth(self):
        """Inline _rbac with require_auth should be extracted."""
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Protected Action"]
  
  "^Protected Action":
    _rbac:
      require_auth: true
    zDisplay:
      event: text
      content: "Protected content"
""")
        
        z = zCLI({"zSpace": str(self.workspace_path)})
        data = z.loader.handle("@.zUI.test")
        
        protected = data["zVaF"].get("^Protected Action")
        self.assertIsNotNone(protected)
        self.assertIn("_rbac", protected)
        self.assertEqual(protected["_rbac"]["require_auth"], True)
    
    def test_inline_rbac_require_role(self):
        """Inline _rbac with require_role should be extracted."""
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Admin Action"]
  
  "^Admin Action":
    _rbac:
      require_role: "admin"
    zDisplay:
      event: text
      content: "Admin content"
""")
        
        z = zCLI({"zSpace": str(self.workspace_path)})
        data = z.loader.handle("@.zUI.test")
        
        admin_action = data["zVaF"].get("^Admin Action")
        self.assertIn("_rbac", admin_action)
        self.assertEqual(admin_action["_rbac"]["require_role"], "admin")
    
    def test_inline_rbac_multiple_roles(self):
        """Inline _rbac with multiple roles (list) should be extracted."""
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Mod Action"]
  
  "^Mod Action":
    _rbac:
      require_role: ["admin", "moderator"]
    zDisplay:
      event: text
      content: "Moderator content"
""")
        
        z = zCLI({"zSpace": str(self.workspace_path)})
        data = z.loader.handle("@.zUI.test")
        
        mod_action = data["zVaF"].get("^Mod Action")
        self.assertIn("_rbac", mod_action)
        self.assertEqual(mod_action["_rbac"]["require_role"], ["admin", "moderator"])
    
    def test_inline_rbac_permission(self):
        """Inline _rbac with require_permission should be extracted."""
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Delete Action"]
  
  "^Delete Action":
    _rbac:
      require_role: "admin"
      require_permission: "data.delete"
    zDisplay:
      event: text
      content: "Delete content"
""")
        
        z = zCLI({"zSpace": str(self.workspace_path)})
        data = z.loader.handle("@.zUI.test")
        
        delete_action = data["zVaF"].get("^Delete Action")
        self.assertIn("_rbac", delete_action)
        self.assertEqual(delete_action["_rbac"]["require_role"], "admin")
        self.assertEqual(delete_action["_rbac"]["require_permission"], "data.delete")


class TestRBACEnforcement(unittest.TestCase):
    """Test RBAC access control enforcement."""
    
    def setUp(self):
        """Set up test workspace and zCLI instance."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
        
        # Create test UI file
        ui_file = self.workspace_path / "zUI.rbac.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^Public", "^AuthOnly", "^UserRole", "^AdminRole", "^AdminPerm"]
  
  "^Public":
    zDisplay:
      event: text
      content: "Public"
      break_after: false
  
  "^AuthOnly":
    _rbac:
      require_auth: true
    zDisplay:
      event: text
      content: "Auth only"
      break_after: false
  
  "^UserRole":
    _rbac:
      require_role: "user"
    zDisplay:
      event: text
      content: "User role"
      break_after: false
  
  "^AdminRole":
    _rbac:
      require_role: "admin"
    zDisplay:
      event: text
      content: "Admin role"
      break_after: false
  
  "^AdminPerm":
    _rbac:
      require_role: "admin"
      require_permission: "system.manage"
    zDisplay:
      event: text
      content: "Admin + permission"
      break_after: false
""")
        
        self.z = zCLI({
            "zSpace": str(self.workspace_path),
            "zVaFile": "@.zUI.rbac",
            "zBlock": "zVaF",
            "zMode": "Terminal"
        })
        
        # Load UI data
        self.ui_data = self.z.loader.handle("@.zUI.rbac")
        self.zblock = self.ui_data["zVaF"]
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_public_access_anonymous(self):
        """Anonymous users should access public items."""
        self.z.session["zAuth"] = {}
        
        result = self.z.wizard._check_rbac_access("^Public", self.zblock.get("^Public"))
        self.assertEqual(result, "access_granted")
    
    def test_auth_required_anonymous_denied(self):
        """Anonymous users should be denied auth-required items."""
        self.z.session["zAuth"] = {}
        
        result = self.z.wizard._check_rbac_access("^AuthOnly", self.zblock.get("^AuthOnly"))
        self.assertEqual(result, "access_denied")
    
    def test_auth_required_authenticated_granted(self):
        """Authenticated users should access auth-only items (updated for three-tier structure)."""
        # Updated for three-tier authentication structure with active_context
        self.z.session["zAuth"] = {
            "active_context": "zSession",  # Required for context-aware RBAC
            "zSession": {
                "authenticated": True,
                "id": "user123",
                "username": "testuser",
                "role": "user",
                "api_key": "token"
            }
        }
        
        result = self.z.wizard._check_rbac_access("^AuthOnly", self.zblock.get("^AuthOnly"))
        self.assertEqual(result, "access_granted")
    
    def test_role_required_correct_role_granted(self):
        """Users with correct role should be granted access (updated for three-tier structure)."""
        # Updated for three-tier authentication structure with active_context
        self.z.session["zAuth"] = {
            "active_context": "zSession",  # Required for context-aware RBAC
            "zSession": {
                "authenticated": True,
                "id": "user123",
                "username": "testuser",
                "role": "user",
                "api_key": "token"
            }
        }
        
        result = self.z.wizard._check_rbac_access("^UserRole", self.zblock.get("^UserRole"))
        self.assertEqual(result, "access_granted")
    
    def test_role_required_wrong_role_denied(self):
        """Users with wrong role should be denied access."""
        self.z.session["zAuth"] = {
            "id": "user123",
            "username": "testuser",
            "role": "user",
            "API_Key": "token"
        }
        
        result = self.z.wizard._check_rbac_access("^AdminRole", self.zblock.get("^AdminRole"))
        self.assertEqual(result, "access_denied")
    
    def test_role_required_anonymous_denied(self):
        """Anonymous users should be denied role-required items."""
        self.z.session["zAuth"] = {}
        
        result = self.z.wizard._check_rbac_access("^UserRole", self.zblock.get("^UserRole"))
        self.assertEqual(result, "access_denied")
    
    def test_multiple_roles_or_logic(self):
        """Users with ANY of the required roles should be granted access."""
        ui_file = self.workspace_path / "zUI.multi.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^MultiRole"]
  
  "^MultiRole":
    _rbac:
      require_role: ["admin", "moderator"]
    zDisplay:
      event: text
      content: "Multi role"
      break_after: false
""")
        
        data = self.z.loader.handle("@.zUI.multi")
        
        # Test with admin role (updated for three-tier structure with active_context)
        self.z.session["zAuth"] = {
            "active_context": "zSession",  # Required for context-aware RBAC
            "zSession": {"authenticated": True, "id": "u1", "username": "admin", "role": "admin", "api_key": "t"}
        }
        result = self.z.wizard._check_rbac_access("^MultiRole", data["zVaF"].get("^MultiRole"))
        self.assertEqual(result, "access_granted")
        
        # Test with moderator role (updated for three-tier structure with active_context)
        self.z.session["zAuth"] = {
            "active_context": "zSession",
            "zSession": {"authenticated": True, "id": "u2", "username": "mod", "role": "moderator", "api_key": "t"}
        }
        result = self.z.wizard._check_rbac_access("^MultiRole", data["zVaF"].get("^MultiRole"))
        self.assertEqual(result, "access_granted")
        
        # Test with user role (not in list, updated for three-tier structure with active_context)
        self.z.session["zAuth"] = {
            "active_context": "zSession",
            "zSession": {"authenticated": True, "id": "u3", "username": "user", "role": "user", "api_key": "t"}
        }
        result = self.z.wizard._check_rbac_access("^MultiRole", data["zVaF"].get("^MultiRole"))
        self.assertEqual(result, "access_denied")
    
    def test_permission_without_permission_denied(self):
        """Users without required permission should be denied."""
        self.z.session["zAuth"] = {
            "id": "admin123",
            "username": "adminuser",
            "role": "admin",
            "API_Key": "token"
        }
        
        # No permission granted yet - should be denied
        result = self.z.wizard._check_rbac_access("^AdminPerm", self.zblock.get("^AdminPerm"))
        self.assertEqual(result, "access_denied")
    
    def test_permission_role_check_passes_without_permission(self):
        """Role check should pass even if permission check fails (separate concern)."""
        # This tests that role requirement is met, but permission is not
        # The overall result should be "access_denied" due to missing permission
        self.z.session["zAuth"] = {
            "id": "admin123",
            "username": "adminuser",
            "role": "admin",
            "API_Key": "token"
        }
        
        # Has admin role, but lacks permission
        result = self.z.wizard._check_rbac_access("^AdminPerm", self.zblock.get("^AdminPerm"))
        self.assertEqual(result, "access_denied")


class TestRBACIntegration(unittest.TestCase):
    """Integration tests for RBAC with real zCLI operations."""
    
    def setUp(self):
        """Set up test workspace."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_rbac_with_zdata(self):
        """RBAC should work with zData operations."""
        # Create schema
        schema_file = self.workspace_path / "zSchema.test.yaml"
        schema_file.write_text("""
Meta:
  Data_Type: sqlite
  Data_Label: "test_rbac"
  Data_Path: "zMachine"
  Data_Paradigm: classical

users:
  id:
    type: int
    pk: true
    auto_increment: true
  name:
    type: str
    required: true
""")
        
        # Create UI with RBAC
        ui_file = self.workspace_path / "zUI.test.yaml"
        ui_file.write_text("""
zVaF:
  ~Root*: ["^View Users", "^Add User"]
  
  "^View Users":
    _rbac:
      require_auth: true
    zData:
      model: "@.zSchema.test"
      action: read
      table: users
  
  "^Add User":
    _rbac:
      require_role: "admin"
    zData:
      model: "@.zSchema.test"
      action: insert
      table: users
      fields: ["name"]
      values: ["Test User"]
""")
        
        z = zCLI({
            "zSpace": str(self.workspace_path),
            "zVaFile": "@.zUI.test",
            "zBlock": "zVaF",
            "zMode": "Terminal"
        })
        
        data = z.loader.handle("@.zUI.test")
        
        # Verify RBAC is attached
        self.assertIn("_rbac", data["zVaF"]["^View Users"])
        self.assertIn("_rbac", data["zVaF"]["^Add User"])
        
        # Test access control (updated for three-tier structure with active_context)
        z.session["zAuth"] = {
            "active_context": "zSession",  # Required for context-aware RBAC
            "zSession": {"authenticated": True, "id": "u1", "username": "user", "role": "user", "api_key": "t"}
        }
        
        # User should access View
        result = z.wizard._check_rbac_access("^View Users", data["zVaF"]["^View Users"])
        self.assertEqual(result, "access_granted")
        
        # User should NOT access Add (needs admin)
        result = z.wizard._check_rbac_access("^Add User", data["zVaF"]["^Add User"])
        self.assertEqual(result, "access_denied")


class TestRBACEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test workspace."""
        self.workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.workspace)
    
    def tearDown(self):
        """Clean up test workspace."""
        if Path(self.workspace).exists():
            shutil.rmtree(self.workspace)
    
    def test_rbac_with_non_dict_value(self):
        """RBAC check with non-dict value should return granted (no restrictions)."""
        z = zCLI({"zSpace": str(self.workspace_path), "zMode": "Terminal"})
        
        # String value (no _rbac possible)
        result = z.wizard._check_rbac_access("^StringKey", "string_value")
        self.assertEqual(result, "access_granted")
        
        # List value (no _rbac possible)
        result = z.wizard._check_rbac_access("^ListKey", ["item1", "item2"])
        self.assertEqual(result, "access_granted")
    
    def test_rbac_empty_dict(self):
        """Empty _rbac dict should not restrict access."""
        z = zCLI({"zSpace": str(self.workspace_path), "zMode": "Terminal"})
        
        value = {"_rbac": {}, "zDisplay": {"event": "text", "content": "test"}}
        result = z.wizard._check_rbac_access("^EmptyRBAC", value)
        self.assertEqual(result, "access_granted")
    
    def test_rbac_no_auth_subsystem(self):
        """RBAC without auth subsystem should deny access (safety fallback)."""
        z = zCLI({"zSpace": str(self.workspace_path), "zMode": "Terminal"})
        
        # Temporarily remove auth
        original_auth = z.auth
        delattr(z, 'auth')
        
        value = {"_rbac": {"require_auth": True}}
        result = z.wizard._check_rbac_access("^NoAuth", value)
        self.assertEqual(result, "access_denied")
        
        # Restore auth
        z.auth = original_auth


def suite():
    """Create test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestRBACParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestRBACEnforcement))
    suite.addTests(loader.loadTestsFromTestCase(TestRBACIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRBACEdgeCases))
    
    return suite


def run_tests(verbose=False):
    """Run all RBAC tests (for test_factory integration)."""
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    return runner.run(suite())


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())

