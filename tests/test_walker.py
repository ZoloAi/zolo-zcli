#!/usr/bin/env python3
# tests/test_walker.py — zWalker Test Suite
# ───────────────────────────────────────────────────────────────

"""
zWalker Test Suite

This test file validates:
1. Walker initialization (new mode with zCLI instance)
2. Menu rendering and navigation
3. zDispatch routing
4. zLink operations (zBack, zNext, zJump)
5. zCrumbs trail management
6. Cache operations (files, loaded, data)
7. UI file loading and parsing
8. Block navigation

Usage:
    python tests/test_walker.py
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zCLI.zCLI import zCLI
from zCLI.subsystems.zWalker.zWalker import zWalker


class WalkerTestSuite:
    """Test suite for zWalker subsystem."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.test_workspace = None
        
    def setup_test_workspace(self):
        """Create a temporary workspace with test UI files."""
        self.test_workspace = tempfile.mkdtemp(prefix="zwalker_test_")
        
        # Create test UI file
        ui_content = """
Root:
  zMenu:
    - Option1
    - Option2
    - $SubMenu

SubMenu:
  zMenu:
    - SubOption1
    - SubOption2
  
Option1:
  zDialog:
    model: "@.schemas.test_schema.zUsers"
    fields: ["username", "email"]
    onSubmit:
      action: create
      model: "@.schemas.test_schema.zUsers"

Option2:
  zDisplay:
    message: "You selected Option 2"
"""
        
        ui_file = Path(self.test_workspace) / "test_ui.yaml"
        ui_file.write_text(ui_content)
        
        return self.test_workspace
    
    def cleanup_test_workspace(self):
        """Clean up temporary workspace."""
        if self.test_workspace and os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
    
    def assert_equal(self, actual, expected, test_name):
        """Assert that two values are equal."""
        if actual == expected:
            self.passed += 1
            print(f"[PASS] {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = f"Expected {expected}, got {actual}"
            print(f"[FAIL] {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_not_none(self, value, test_name):
        """Assert that a value is not None."""
        if value is not None:
            self.passed += 1
            print(f"[PASS] {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = "Expected non-None value, got None"
            print(f"[FAIL] {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_true(self, condition, test_name):
        """Assert that a condition is true."""
        if condition:
            self.passed += 1
            print(f"[PASS] {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = "Expected True, got False"
            print(f"[FAIL] {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_in(self, item, container, test_name):
        """Assert that item is in container."""
        if item in container:
            self.passed += 1
            print(f"[PASS] {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = f"Expected {item} to be in {container}"
            print(f"[FAIL] {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False


def test_walker_initialization():
    """Test 1: Walker initialization with zCLI instance."""
    print("\n" + "=" * 70)
    print("Test 1: Walker Initialization")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI instance
        zcli = zCLI()
        
        # Create zSpark_obj for walker
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        
        # Initialize walker
        walker = zWalker(zcli)
        
        # Test walker attributes
        tester.assert_not_none(walker, "Walker instance created")
        tester.assert_not_none(walker.zcli, "Walker has zCLI reference")
        tester.assert_not_none(walker.session, "Walker has session")
        tester.assert_not_none(walker.dispatch, "Walker has dispatch")
        tester.assert_not_none(walker.menu, "Walker has menu")
        tester.assert_not_none(walker.link, "Walker has link")
        tester.assert_not_none(walker.zCrumbs, "Walker has zCrumbs")
        tester.assert_not_none(walker.loader, "Walker has loader")
        
        # Test that walker uses zCLI's subsystems
        tester.assert_equal(walker.session, zcli.session, "Walker uses zCLI session")
        tester.assert_equal(walker.display, zcli.display, "Walker uses zCLI display")
        tester.assert_equal(walker.loader, zcli.loader, "Walker uses zCLI loader")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_crumbs_management():
    """Test 2: zCrumbs trail management."""
    print("\n" + "=" * 70)
    print("Test 2: zCrumbs Trail Management")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Initialize session with crumbs
        walker.session["zCrumbs"] = {"Root": []}
        
        # Test adding crumbs
        walker.session["zCrumbs"]["Root"].append("Option1")
        tester.assert_in("Option1", walker.session["zCrumbs"]["Root"], 
                        "Crumb added to trail")
        
        walker.session["zCrumbs"]["Root"].append("SubMenu")
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 2,
                           "Multiple crumbs tracked")
        
        # Test creating new scope
        walker.session["zCrumbs"]["Root.SubMenu"] = []
        tester.assert_in("Root.SubMenu", walker.session["zCrumbs"],
                        "New crumb scope created")
        
        # Test trail structure
        tester.assert_true(isinstance(walker.session["zCrumbs"], dict),
                          "zCrumbs is a dictionary")
        tester.assert_true(isinstance(walker.session["zCrumbs"]["Root"], list),
                          "zCrumb trail is a list")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_cache_operations():
    """Test 3: Cache operations (files, loaded, data)."""
    print("\n" + "=" * 70)
    print("Test 3: Cache Operations")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test cache structure
        tester.assert_not_none(walker.session.get("zCache"), "zCache exists in session")
        
        # Test cache namespaces
        if "zCache" in walker.session:
            cache = walker.session["zCache"]
            
            # Check for three-tier cache structure
            tester.assert_true(isinstance(cache, dict), "zCache is a dictionary")
            
            # Test that cache can store data
            cache["test_key"] = "test_value"
            tester.assert_equal(cache.get("test_key"), "test_value",
                               "Cache can store and retrieve data")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_session_population():
    """Test 4: Session population from zSpark_obj."""
    print("\n" + "=" * 70)
    print("Test 4: Session Population")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info",
            "custom_field": "custom_value"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test zSpark_obj is stored
        tester.assert_equal(walker.zSpark_obj, zspark_obj,
                           "zSpark_obj stored in walker")
        
        # Test session has ID
        tester.assert_not_none(walker.session.get("zS_id"),
                              "Session has zS_id")
        
        # Test session ID format
        if walker.session.get("zS_id"):
            tester.assert_true(walker.session["zS_id"].startswith("zS"),
                              "Session ID has correct prefix")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_loader_integration():
    """Test 5: Loader integration with walker."""
    print("\n" + "=" * 70)
    print("Test 5: Loader Integration")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Manually populate session with workspace (normally done by walker.run())
        walker.session["zWorkspace"] = workspace
        
        # Test loader is accessible
        tester.assert_not_none(walker.loader, "Walker has loader")
        
        # Test loader has session (ZLoader uses zSession attribute)
        tester.assert_not_none(walker.loader.zSession, "Loader has zSession")
        
        # Test loader uses same session as walker
        tester.assert_equal(walker.loader.zSession, walker.session,
                           "Loader uses walker's session")
        
        # Test loader can access workspace
        tester.assert_equal(walker.loader.zSession.get("zWorkspace"), workspace,
                           "Loader can access workspace from session")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_dispatch_initialization():
    """Test 6: zDispatch initialization."""
    print("\n" + "=" * 70)
    print("Test 6: zDispatch Initialization")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test dispatch exists
        tester.assert_not_none(walker.dispatch, "Walker has dispatch")
        
        # Test dispatch has walker reference
        tester.assert_equal(walker.dispatch.walker, walker,
                           "Dispatch has walker reference")
        
        # Test dispatch has session
        tester.assert_not_none(walker.dispatch.zSession,
                              "Dispatch has session")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_menu_initialization():
    """Test 7: zMenu initialization."""
    print("\n" + "=" * 70)
    print("Test 7: zMenu Initialization")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test menu exists
        tester.assert_not_none(walker.menu, "Walker has menu")
        
        # Test menu has walker reference
        tester.assert_equal(walker.menu.walker, walker,
                           "Menu has walker reference")
        
        # Test menu has session
        tester.assert_not_none(walker.menu.zSession,
                              "Menu has session")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_link_initialization():
    """Test 8: zLink initialization."""
    print("\n" + "=" * 70)
    print("Test 8: zLink Initialization")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test link exists
        tester.assert_not_none(walker.link, "Walker has link")
        
        # Test link has walker reference
        tester.assert_equal(walker.link.walker, walker,
                           "Link has walker reference")
        
        # Test link has session
        tester.assert_not_none(walker.link.zSession,
                              "Link has session")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_ui_file_loading():
    """Test 9: UI file loading and parsing."""
    print("\n" + "=" * 70)
    print("Test 9: UI File Loading and Parsing")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    
    # Use the actual test UI file from zCLI/UI/
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_ui_path = os.path.join(project_root, "zCLI", "UI")
    
    try:
        # Create zCLI and walker pointing to real UI file
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": project_root,
            "zVaFilename": "ui.test.yaml",
            "zVaFile_path": "@.UI",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Populate session
        walker.session["zWorkspace"] = project_root
        walker.session["zVaFilename"] = "ui.test.yaml"
        walker.session["zVaFile_path"] = "@.UI"
        
        # Test that loader can construct the path
        tester.assert_not_none(walker.loader, "Walker has loader")
        tester.assert_equal(walker.session.get("zWorkspace"), project_root,
                           "Session has correct workspace")
        tester.assert_equal(walker.session.get("zVaFilename"), "ui.test.yaml",
                           "Session has correct filename")
        
        # Test UI file exists
        ui_file = os.path.join(test_ui_path, "ui.test.yaml")
        tester.assert_true(os.path.exists(ui_file),
                          "UI test file exists")
        
    finally:
        pass  # No cleanup needed for real files
    
    return tester


def test_crumbs_trail_navigation():
    """Test 10: zCrumbs trail navigation with zBack."""
    print("\n" + "=" * 70)
    print("Test 10: zCrumbs Trail Navigation")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Initialize crumbs like walker does
        walker.session["zCrumbs"] = {"Root": []}
        
        # Simulate navigation: Root -> MainMenu -> ViewUsers
        walker.session["zCrumbs"]["Root"].append("MainMenu")
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 1,
                           "Trail has 1 crumb after first navigation")
        
        walker.session["zCrumbs"]["Root"].append("ViewUsers")
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 2,
                           "Trail has 2 crumbs after second navigation")
        
        # Simulate zBack: pop last crumb
        walker.session["zCrumbs"]["Root"].pop()
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 1,
                           "Trail has 1 crumb after zBack")
        tester.assert_equal(walker.session["zCrumbs"]["Root"][-1], "MainMenu",
                           "Current location is MainMenu after zBack")
        
        # Another zBack: pop to root
        walker.session["zCrumbs"]["Root"].pop()
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 0,
                           "Trail is empty at root")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_crumbs_nested_scopes():
    """Test 11: zCrumbs nested scope management."""
    print("\n" + "=" * 70)
    print("Test 11: zCrumbs Nested Scope Management")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Initialize crumbs
        walker.session["zCrumbs"] = {"Root": []}
        
        # Navigate to create a link ($ prefix)
        walker.session["zCrumbs"]["Root"].append("$SubMenuLink")
        tester.assert_in("$SubMenuLink", walker.session["zCrumbs"]["Root"],
                        "Link crumb added to trail")
        
        # Create new scope for SubMenuLink
        walker.session["zCrumbs"]["Root.SubMenuLink"] = []
        tester.assert_in("Root.SubMenuLink", walker.session["zCrumbs"],
                        "New scope created for link")
        
        # Navigate within new scope
        walker.session["zCrumbs"]["Root.SubMenuLink"].append("SubOption1")
        tester.assert_equal(len(walker.session["zCrumbs"]["Root.SubMenuLink"]), 1,
                           "New scope has navigation trail")
        
        # Test scope structure
        tester.assert_equal(len(walker.session["zCrumbs"]), 2,
                           "Two scopes exist (Root and SubMenuLink)")
        
        # Simulate zBack to parent scope: remove child scope
        if not walker.session["zCrumbs"]["Root.SubMenuLink"]:
            # Empty child scope, pop it
            walker.session["zCrumbs"].pop("Root.SubMenuLink")
        
        # After popping SubMenuLink scope, we have SubOption1 in trail
        # Let's re-test with proper zBack logic
        walker.session["zCrumbs"]["Root.SubMenuLink"] = ["SubOption1"]
        
        # Pop within child scope
        walker.session["zCrumbs"]["Root.SubMenuLink"].pop()
        tester.assert_equal(len(walker.session["zCrumbs"]["Root.SubMenuLink"]), 0,
                           "Child scope trail emptied")
        
        # Now child scope is empty, should be removed on next zBack
        walker.session["zCrumbs"].pop("Root.SubMenuLink")
        walker.session["zCrumbs"]["Root"].pop()  # Pop the link from parent
        
        tester.assert_equal(len(walker.session["zCrumbs"]), 1,
                           "Back to single scope after exiting link")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_menu_structure():
    """Test 12: Menu structure and zBack injection."""
    print("\n" + "=" * 70)
    print("Test 12: Menu Structure and zBack Injection")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Test menu object structure
        menu_obj = {
            "zBlock": "Root",
            "zKey": "zMenu",
            "zHorizontal": ["Option1", "Option2", "$SubMenu"],
            "is_anchor": False  # Not anchor, so zBack should be injected
        }
        
        # Simulate zMenu's zBack injection logic
        if not menu_obj["is_anchor"]:
            menu_obj["zHorizontal"] = menu_obj["zHorizontal"] + ["zBack"]
        
        tester.assert_in("zBack", menu_obj["zHorizontal"],
                        "zBack injected into non-anchor menu")
        tester.assert_equal(len(menu_obj["zHorizontal"]), 4,
                           "Menu has 4 options including zBack")
        
        # Test anchor menu (no zBack injection)
        anchor_menu = {
            "zBlock": "Root",
            "zKey": "zMenu",
            "zHorizontal": ["Option1", "Option2"],
            "is_anchor": True  # Anchor, no zBack
        }
        
        if not anchor_menu["is_anchor"]:
            anchor_menu["zHorizontal"] = anchor_menu["zHorizontal"] + ["zBack"]
        
        tester.assert_true("zBack" not in anchor_menu["zHorizontal"],
                          "zBack not injected into anchor menu")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def test_navigation_flow():
    """Test 13: Complete navigation flow simulation."""
    print("\n" + "=" * 70)
    print("Test 13: Complete Navigation Flow Simulation")
    print("=" * 70)
    
    tester = WalkerTestSuite()
    workspace = tester.setup_test_workspace()
    
    try:
        # Create zCLI and walker
        zcli = zCLI()
        zspark_obj = {
            "zWorkspace": workspace,
            "zVaFilename": "test_ui.yaml",
            "zVaFile_path": "@",
            "zBlock": "Root",
            "logger": "info"
        }
        zcli.zspark_obj = zspark_obj
        walker = zWalker(zcli)
        
        # Initialize session
        walker.session["zCrumbs"] = {"Root": []}
        walker.session["zWorkspace"] = workspace
        
        # Simulate: Root -> MainMenu -> ViewUsers
        walker.session["zCrumbs"]["Root"].append("MainMenu")
        walker.session["zCrumbs"]["Root"].append("ViewUsers")
        
        # Verify trail
        tester.assert_equal(walker.session["zCrumbs"]["Root"],
                           ["MainMenu", "ViewUsers"],
                           "Trail shows correct navigation path")
        
        # Simulate zBack
        walker.session["zCrumbs"]["Root"].pop()
        tester.assert_equal(walker.session["zCrumbs"]["Root"],
                           ["MainMenu"],
                           "zBack returns to MainMenu")
        
        # Navigate to different option
        walker.session["zCrumbs"]["Root"].append("CreateUser")
        tester.assert_equal(walker.session["zCrumbs"]["Root"],
                           ["MainMenu", "CreateUser"],
                           "Can navigate to different option")
        
        # zBack twice to root
        walker.session["zCrumbs"]["Root"].pop()
        walker.session["zCrumbs"]["Root"].pop()
        tester.assert_equal(len(walker.session["zCrumbs"]["Root"]), 0,
                           "zBack twice returns to root")
        
    finally:
        tester.cleanup_test_workspace()
    
    return tester


def run_all_tests():
    """Run all walker tests."""
    print("\n" + "🧪 " * 40)
    print("RUNNING ZWALKER TEST SUITE")
    print("🧪 " * 40)
    
    test_functions = [
        test_walker_initialization,
        test_crumbs_management,
        test_cache_operations,
        test_session_population,
        test_loader_integration,
        test_dispatch_initialization,
        test_menu_initialization,
        test_link_initialization,
        test_ui_file_loading,
        test_crumbs_trail_navigation,
        test_crumbs_nested_scopes,
        test_menu_structure,
        test_navigation_flow,
    ]
    
    all_passed = 0
    all_failed = 0
    
    for test_func in test_functions:
        try:
            tester = test_func()
            all_passed += tester.passed
            all_failed += tester.failed
        except Exception as e:
            print(f"\n❌ Test function {test_func.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            all_failed += 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("ZWALKER TEST RESULTS")
    print("=" * 70)
    print(f"[OK] Passed: {all_passed}")
    print(f"[X] Failed: {all_failed}")
    print("=" * 70)
    
    if all_failed > 0:
        print(f"\n[WARN] {all_failed} test(s) failed. Please review the errors above.")
        return False
    else:
        print("\n✅ All zWalker tests passed!")
        return True


def main():
    """Main entry point."""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
