#!/usr/bin/env python3
# tests/test_config.py — zConfig Test Suite
# ───────────────────────────────────────────────────────────────

"""
zConfig Test Suite

This test file validates:
1. Configuration loading from hierarchy
2. Environment-specific config switching
3. Cross-platform path resolution
4. Config merging and priority
5. Secret management
6. Dot-notation access
7. Environment variable overrides

Usage:
    python tests/test_config.py
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

from zCLI.subsystems.zConfig import ZConfig
from zCLI.subsystems.zConfig_modules import ZConfigPaths

# ANSI Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ConfigTestSuite:
    """Test suite for zConfig subsystem."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def assert_equal(self, actual, expected, test_name):
        """Assert that two values are equal."""
        if actual == expected:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = f"Expected {expected}, got {actual}"
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_not_none(self, value, test_name):
        """Assert that a value is not None."""
        if value is not None:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = "Expected non-None value, got None"
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_true(self, condition, test_name):
        """Assert that a condition is true."""
        if condition:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = "Expected True, got False"
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False
    
    def assert_in(self, item, container, test_name):
        """Assert that item is in container."""
        if item in container:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.tests.append((test_name, True, None))
            return True
        else:
            self.failed += 1
            error_msg = f"Expected {item} to be in {container}"
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
            print(f"   {error_msg}")
            self.tests.append((test_name, False, error_msg))
            return False


def test_config_initialization():
    """Test 1: zConfig initialization."""
    print("\n" + "=" * 70)
    print("Test 1: zConfig Initialization")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        # Create zConfig instance
        config = ZConfig()
        
        # Test basic attributes
        tester.assert_not_none(config, "zConfig instance created")
        tester.assert_not_none(config.config, "zConfig has config dict")
        tester.assert_not_none(config.paths, "zConfig has paths resolver")
        tester.assert_not_none(config.loader, "zConfig has loader")
        
        # Test environment
        tester.assert_equal(config.get_environment(), "dev",
                           "Default environment is dev")
        
        # Test config sources
        sources = config.get_config_sources()
        tester.assert_true(len(sources) >= 1,
                          "At least one config source loaded")
        tester.assert_in("package-defaults", sources,
                        "Package defaults loaded")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_config_values():
    """Test 2: Configuration value access."""
    print("\n" + "=" * 70)
    print("Test 2: Configuration Value Access")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        config = ZConfig()
        
        # Test dot-notation access
        host = config.get("zSocket.network.host")
        tester.assert_equal(host, "127.0.0.1",
                           "zSocket.network.host is 127.0.0.1")
        
        port = config.get("zSocket.network.port")
        tester.assert_equal(port, 56891,
                           "zSocket.network.port is 56891")
        
        # Test with default value
        nonexistent = config.get("nonexistent.path", "default_value")
        tester.assert_equal(nonexistent, "default_value",
                           "Returns default for nonexistent path")
        
        # Test section access
        socket_section = config.get_section("zSocket")
        tester.assert_not_none(socket_section,
                              "Can get zSocket section")
        tester.assert_in("network", socket_section,
                        "zSocket section has network key")
        
        # Test nested access
        max_conn = config.get("zSocket.limits.max_connections")
        tester.assert_not_none(max_conn,
                              "Can get nested config value")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_environment_switching():
    """Test 3: Environment-specific configuration."""
    print("\n" + "=" * 70)
    print("Test 3: Environment-Specific Configuration")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        # Load dev config
        dev_config = ZConfig("dev")
        tester.assert_equal(dev_config.get_environment(), "dev",
                           "Dev config has dev environment")
        
        dev_auth = dev_config.get("zSocket.security.require_auth")
        tester.assert_equal(dev_auth, False,
                           "Dev config has require_auth=False")
        
        dev_max_conn = dev_config.get("zSocket.limits.max_connections")
        tester.assert_equal(dev_max_conn, 50,
                           "Dev config overrides max_connections to 50")
        
        # Load prod config
        prod_config = ZConfig("prod")
        tester.assert_equal(prod_config.get_environment(), "prod",
                           "Prod config has prod environment")
        
        prod_auth = prod_config.get("zSocket.security.require_auth")
        tester.assert_equal(prod_auth, True,
                           "Prod config has require_auth=True")
        
        prod_max_conn = prod_config.get("zSocket.limits.max_connections")
        tester.assert_equal(prod_max_conn, 500,
                           "Prod config overrides max_connections to 500")
        
        # Verify they're different
        tester.assert_true(dev_max_conn != prod_max_conn,
                          "Dev and prod have different max_connections")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_cross_platform_paths():
    """Test 4: Cross-platform path resolution."""
    print("\n" + "=" * 70)
    print("Test 4: Cross-Platform Path Resolution")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        paths = ZConfigPaths()
        
        # Test OS detection
        tester.assert_not_none(paths.os_type,
                              "OS type detected")
        tester.assert_in(paths.os_type, ["Linux", "Darwin", "Windows"],
                        "OS type is valid")
        
        # Test system path
        system_path = paths.system_config_dir
        tester.assert_not_none(system_path,
                              "System config path exists")
        tester.assert_true(isinstance(system_path, Path),
                          "System path is Path object")
        
        # Test user paths
        user_native = paths.user_config_dir_native
        user_dotfile = paths.user_config_dir_dotfile
        
        tester.assert_not_none(user_native,
                              "User native path exists")
        tester.assert_not_none(user_dotfile,
                              "User dotfile path exists")
        
        # Test project paths
        project_path = paths.project_config_file
        tester.assert_not_none(project_path,
                              "Project config path exists")
        
        # Test path info
        info = paths.get_info()
        tester.assert_not_none(info,
                              "Path info dict exists")
        tester.assert_in("os", info,
                        "Path info contains OS")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_config_hierarchy():
    """Test 5: Configuration hierarchy and merging."""
    print("\n" + "=" * 70)
    print("Test 5: Configuration Hierarchy and Merging")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    temp_config = None
    
    try:
        # Create temporary project config
        temp_dir = tempfile.mkdtemp(prefix="zconfig_test_")
        temp_config = Path(temp_dir) / "config.yaml"
        
        # Write project config with overrides
        temp_config.write_text("""
zSocket:
  limits:
    max_connections: 999
  network:
    port: 12345
""")
        
        # Change to temp directory so project config is found
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Load config (should pick up project config)
        config = ZConfig()
        
        # Test that project config overrides package config
        max_conn = config.get("zSocket.limits.max_connections")
        tester.assert_equal(max_conn, 999,
                           "Project config overrides max_connections")
        
        port = config.get("zSocket.network.port")
        tester.assert_equal(port, 12345,
                           "Project config overrides port")
        
        # Test that non-overridden values still come from defaults
        host = config.get("zSocket.network.host")
        tester.assert_equal(host, "127.0.0.1",
                           "Non-overridden values from defaults")
        
        # Test config sources include project
        sources = config.get_config_sources()
        tester.assert_true(any("project" in s for s in sources),
                          "Project config in sources")
        
        # Restore directory
        os.chdir(original_cwd)
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if temp_config and temp_config.parent.exists():
            shutil.rmtree(temp_config.parent)
    
    return tester


def test_secret_management():
    """Test 6: Secret management from environment."""
    print("\n" + "=" * 70)
    print("Test 6: Secret Management")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        # Set test secret in environment
        os.environ["ZOLO_DB_PASSWORD"] = "test_secret_123"
        os.environ["ZOLO_JWT_SECRET"] = "test_jwt_secret"
        
        # Load config
        config = ZConfig()
        
        # Test secret access
        db_password = config.get_secret("db_password")
        tester.assert_equal(db_password, "test_secret_123",
                           "Can get secret from env var")
        
        jwt_secret = config.get_secret("jwt_secret")
        tester.assert_equal(jwt_secret, "test_jwt_secret",
                           "Can get JWT secret from env var")
        
        # Test has_secret
        tester.assert_true(config.has_secret("db_password"),
                          "has_secret returns True for set secret")
        
        tester.assert_true(not config.has_secret("nonexistent_secret"),
                          "has_secret returns False for unset secret")
        
        # Test that secrets are NOT in config dict
        tester.assert_true("db_password" not in str(config.get_all()),
                          "Secrets not in config dict")
        
        # Cleanup env vars
        del os.environ["ZOLO_DB_PASSWORD"]
        del os.environ["ZOLO_JWT_SECRET"]
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        
        # Cleanup env vars on error
        os.environ.pop("ZOLO_DB_PASSWORD", None)
        os.environ.pop("ZOLO_JWT_SECRET", None)
    
    return tester


def test_env_var_overrides():
    """Test 7: Environment variable overrides."""
    print("\n" + "=" * 70)
    print("Test 7: Environment Variable Overrides")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        # Set env var overrides
        os.environ["WEBSOCKET_HOST"] = "0.0.0.0"
        os.environ["WEBSOCKET_PORT"] = "8888"
        os.environ["WEBSOCKET_MAX_CONNECTIONS"] = "777"
        
        # Load config
        config = ZConfig()
        
        # Test that env vars override config files
        host = config.get("zSocket.network.host")
        tester.assert_equal(host, "0.0.0.0",
                           "Env var overrides host")
        
        port = config.get("zSocket.network.port")
        tester.assert_equal(port, 8888,
                           "Env var overrides port")
        
        max_conn = config.get("zSocket.limits.max_connections")
        tester.assert_equal(max_conn, 777,
                           "Env var overrides max_connections")
        
        # Test that env vars appear in sources
        sources = config.get_config_sources()
        tester.assert_in("environment-variables", sources,
                        "Environment variables in config sources")
        
        # Cleanup env vars
        del os.environ["WEBSOCKET_HOST"]
        del os.environ["WEBSOCKET_PORT"]
        del os.environ["WEBSOCKET_MAX_CONNECTIONS"]
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        
        # Cleanup env vars on error
        os.environ.pop("WEBSOCKET_HOST", None)
        os.environ.pop("WEBSOCKET_PORT", None)
        os.environ.pop("WEBSOCKET_MAX_CONNECTIONS", None)
    
    return tester


def test_paths_info():
    """Test 8: Path information and debugging."""
    print("\n" + "=" * 70)
    print("Test 8: Path Information")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        config = ZConfig()
        
        # Test paths info
        paths_info = config.get_paths_info()
        tester.assert_not_none(paths_info,
                              "Path info dict exists")
        
        tester.assert_in("os", paths_info,
                        "Path info contains OS")
        tester.assert_in("system_config", paths_info,
                        "Path info contains system_config")
        tester.assert_in("user_config_native", paths_info,
                        "Path info contains user_config_native")
        tester.assert_in("project_config", paths_info,
                        "Path info contains project_config")
        
        # Test config sources
        sources = config.get_config_sources()
        tester.assert_true(isinstance(sources, list),
                          "Config sources is a list")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_deep_merge():
    """Test 9: Deep merge functionality."""
    print("\n" + "=" * 70)
    print("Test 9: Deep Merge Functionality")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        # Dev config should merge with defaults
        dev_config = ZConfig("dev")
        
        # Test that dev overrides work
        require_auth = dev_config.get("zSocket.security.require_auth")
        tester.assert_equal(require_auth, False,
                           "Dev overrides require_auth to False")
        
        # Test that non-overridden values persist from defaults
        host = dev_config.get("zSocket.network.host")
        tester.assert_equal(host, "127.0.0.1",
                           "Non-overridden host from defaults")
        
        auth_schema = dev_config.get("zSocket.security.auth_schema")
        tester.assert_not_none(auth_schema,
                              "Auth schema persists from defaults")
        
        # Test nested merge
        network_section = dev_config.get_section("zSocket").get("network", {})
        tester.assert_in("host", network_section,
                        "Network section has host (from defaults)")
        tester.assert_in("port", network_section,
                        "Network section has port (from defaults)")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_config_all_sections():
    """Test 10: All expected config sections exist."""
    print("\n" + "=" * 70)
    print("Test 10: All Config Sections")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        config = ZConfig()
        all_config = config.get_all()
        
        # Test that main sections exist
        tester.assert_in("Meta", all_config,
                        "Config has Meta section")
        tester.assert_in("zSocket", all_config,
                        "Config has zSocket section")
        tester.assert_in("zData", all_config,
                        "Config has zData section")
        tester.assert_in("zLoader", all_config,
                        "Config has zLoader section")
        tester.assert_in("zSession", all_config,
                        "Config has zSession section")
        
        # Test zSocket subsections
        socket_config = all_config["zSocket"]
        tester.assert_in("network", socket_config,
                        "zSocket has network section")
        tester.assert_in("security", socket_config,
                        "zSocket has security section")
        tester.assert_in("limits", socket_config,
                        "zSocket has limits section")
        tester.assert_in("timeouts", socket_config,
                        "zSocket has timeouts section")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_machine_config():
    """Test 11: Machine configuration loading and access."""
    print("\n" + "=" * 70)
    print("Test 11: Machine Configuration")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        config = ZConfig()
        
        # Test machine config exists
        machine = config.get_machine()
        tester.assert_not_none(machine,
                              "Machine config exists")
        
        # Test machine attributes
        tester.assert_not_none(config.get_machine("os"),
                              "Machine has OS")
        tester.assert_not_none(config.get_machine("hostname"),
                              "Machine has hostname")
        tester.assert_not_none(config.get_machine("ide"),
                              "Machine has IDE")
        tester.assert_not_none(config.get_machine("browser"),
                              "Machine has browser")
        
        # Test machine values are reasonable
        os_type = config.get_machine("os")
        tester.assert_in(os_type, ["Linux", "Darwin", "Windows"],
                        "Machine OS is valid")
        
        # Test deployment from machine
        deployment = config.get_machine("deployment")
        tester.assert_not_none(deployment,
                              "Machine has deployment type")
        
        # Test tool preferences exist
        ide = config.get_machine("ide")
        tester.assert_true(isinstance(ide, str) and len(ide) > 0,
                          "Machine IDE is non-empty string")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def test_machine_file_creation():
    """Test 12: Machine YAML file creation on first run."""
    print("\n" + "=" * 70)
    print("Test 12: Machine YAML File Creation")
    print("=" * 70)
    
    tester = ConfigTestSuite()
    
    try:
        from zCLI.subsystems.zConfig_modules import ZConfigPaths
        
        paths = ZConfigPaths()
        
        # Check if user machine.yaml was created
        user_machine = paths.user_config_dir / "machine.yaml"
        
        # It should be created on first ZConfig() init
        config = ZConfig()
        
        # After init, machine.yaml should exist
        tester.assert_true(user_machine.exists(),
                          "User machine.yaml created on first run")
        
        # Test that machine config was loaded from file
        machine = config.get_machine()
        tester.assert_not_none(machine,
                              "Machine config loaded")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test crashed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    
    return tester


def run_all_tests():
    """Run all config tests."""
    print("\n" + "🧪 " * 40)
    print("RUNNING ZCONFIG TEST SUITE")
    print("🧪 " * 40)
    
    test_functions = [
        test_config_initialization,
        test_config_values,
        test_environment_switching,
        test_cross_platform_paths,
        test_config_hierarchy,
        test_secret_management,
        test_env_var_overrides,
        test_paths_info,
        test_deep_merge,
        test_config_all_sections,
        test_machine_config,
        test_machine_file_creation,
    ]
    
    all_passed = 0
    all_failed = 0
    
    for test_func in test_functions:
        try:
            tester = test_func()
            all_passed += tester.passed
            all_failed += tester.failed
        except Exception as e:
            print(f"\n{Colors.RED}❌ Test function {test_func.__name__} crashed: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            all_failed += 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("ZCONFIG TEST RESULTS")
    print("=" * 70)
    print(f"{Colors.GREEN}[OK]{Colors.RESET} Passed: {all_passed}")
    print(f"{Colors.RED}[X]{Colors.RESET} Failed: {all_failed}")
    print("=" * 70)
    
    if all_failed > 0:
        print(f"\n{Colors.YELLOW}[WARN]{Colors.RESET} {all_failed} test(s) failed. Please review the errors above.")
        return False
    else:
        print(f"\n{Colors.GREEN}✅ All zConfig tests passed!{Colors.RESET}")
        return True


def main():
    """Main entry point."""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

