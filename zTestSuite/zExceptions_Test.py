"""
Tests for zCLI Custom Exceptions (Week 4.3)

Tests actionable error messages across all exception types.
Verifies hint messages are context-aware and helpful.
"""

import sys
import unittest
from zCLI.utils.zExceptions import (
    zCLIException,
    SchemaNotFoundError,
    FormModelNotFoundError,
    InvalidzPathError,
    DatabaseNotInitializedError,
    TableNotFoundError,
    zUIParseError,
    AuthenticationRequiredError,
    PermissionDeniedError,
    ConfigurationError,
    PluginNotFoundError,
    ValidationError,
    zMachinePathError
)


class TestBaseException(unittest.TestCase):
    """Test base zCLIException class."""
    
    def test_basic_exception(self):
        """Test exception with message only."""
        exc = zCLIException("Something went wrong")
        self.assertEqual(str(exc), "Something went wrong")
    
    def test_exception_with_hint(self):
        """Test exception includes hint in message."""
        exc = zCLIException("Error occurred", hint="Try this fix")
        self.assertIn("Error occurred", str(exc))
        self.assertIn("💡 Try this fix", str(exc))
    
    def test_exception_with_context(self):
        """Test context is stored but not in message."""
        exc = zCLIException(
            "Error",
            hint="Fix it",
            context={"key": "value", "number": 42}
        )
        self.assertEqual(exc.context["key"], "value")
        self.assertEqual(exc.context["number"], 42)


class TestSchemaNotFoundError(unittest.TestCase):
    """Test SchemaNotFoundError with different contexts."""
    
    def test_python_context(self):
        """Test error message for Python code context."""
        exc = SchemaNotFoundError("users", context_type="python")
        error_msg = str(exc)
        
        # Check main message
        self.assertIn("Schema 'users' not found", error_msg)
        
        # Check Python-specific hint
        self.assertIn("z.loader.handle('@.zSchema.users')", error_msg)
        self.assertIn("zSchema.users.yaml", error_msg)
        self.assertIn("💡", error_msg)
    
    def test_yaml_zdata_context(self):
        """Test error message for YAML zData context."""
        exc = SchemaNotFoundError("products", context_type="yaml_zdata")
        error_msg = str(exc)
        
        # Check YAML-specific guidance
        self.assertIn("model: '@.zSchema.products'", error_msg)
        self.assertIn("NO .yaml", error_msg)
        self.assertIn("zData:", error_msg)
        self.assertIn("action: read", error_msg)
    
    def test_yaml_zdialog_context(self):
        """Test error message for YAML zDialog context."""
        exc = SchemaNotFoundError("contacts", context_type="yaml_zdialog")
        error_msg = str(exc)
        
        # Check zDialog-specific guidance
        self.assertIn("form model", error_msg)
        self.assertIn("Models:", error_msg)
        self.assertIn("fields:", error_msg)
    
    def test_with_zpath(self):
        """Test error includes attempted zPath."""
        exc = SchemaNotFoundError("users", zpath="@.wrong.path.zSchema.users")
        error_msg = str(exc)
        
        self.assertIn("@.wrong.path.zSchema.users", error_msg)
        self.assertIn("attempted:", error_msg)
    
    def test_context_storage(self):
        """Test that context dict is populated."""
        exc = SchemaNotFoundError("users", context_type="python", zpath="@.zSchema.users")
        
        self.assertEqual(exc.context['schema'], 'users')
        self.assertEqual(exc.context['context_type'], 'python')
        self.assertEqual(exc.context['zpath'], '@.zSchema.users')


class TestFormModelNotFoundError(unittest.TestCase):
    """Test FormModelNotFoundError with model suggestions."""
    
    def test_with_available_models(self):
        """Test error includes list of available models."""
        exc = FormModelNotFoundError(
            "NonExistent",
            schema_name="users",
            available_models=["User", "SearchForm", "DeleteForm"]
        )
        error_msg = str(exc)
        
        # Check error message
        self.assertIn("Form model 'NonExistent' not found", error_msg)
        self.assertIn("User, SearchForm, DeleteForm", error_msg)
        self.assertIn("zSchema.users.yaml", error_msg)
        
        # Check guidance shows how to define model
        self.assertIn("Models:", error_msg)
        self.assertIn("NonExistent:", error_msg)
        self.assertIn("fields:", error_msg)
    
    def test_without_schema_name(self):
        """Test error when schema name is unknown."""
        exc = FormModelNotFoundError("MyForm")
        error_msg = str(exc)
        
        self.assertIn("your schema file", error_msg)
        self.assertIn("Available models: None", error_msg)
    
    def test_context_storage(self):
        """Test context dict is populated."""
        exc = FormModelNotFoundError(
            "TestForm",
            schema_name="test",
            available_models=["Form1", "Form2"]
        )
        
        self.assertEqual(exc.context['model'], 'TestForm')
        self.assertEqual(exc.context['schema'], 'test')
        self.assertEqual(exc.context['available'], ["Form1", "Form2"])


class TestInvalidzPathError(unittest.TestCase):
    """Test InvalidzPathError with path syntax guidance."""
    
    def test_basic_invalid_path(self):
        """Test error with invalid zPath."""
        exc = InvalidzPathError("@.wrong/path/format")
        error_msg = str(exc)
        
        self.assertIn("Invalid zPath: '@.wrong/path/format'", error_msg)
        self.assertIn("zPath syntax:", error_msg)
        self.assertIn("@.zSchema.name", error_msg)
        self.assertIn("workspace-relative", error_msg)
    
    def test_with_reason(self):
        """Test error includes reason for invalidity."""
        exc = InvalidzPathError("@.zSchema.users.yaml", reason="Double extension")
        error_msg = str(exc)
        
        self.assertIn("Double extension", error_msg)
        self.assertIn("@.zSchema.users.yaml", error_msg)
    
    def test_shows_common_mistakes(self):
        """Test error shows common mistakes."""
        exc = InvalidzPathError("@.wrong")
        error_msg = str(exc)
        
        # Should show examples of correct and incorrect
        self.assertIn("❌", error_msg)
        self.assertIn("✅", error_msg)
        self.assertIn("Don't include .yaml", error_msg)


class TestDatabaseNotInitializedError(unittest.TestCase):
    """Test DatabaseNotInitializedError with initialization guidance."""
    
    def test_basic_error(self):
        """Test basic database not initialized error."""
        exc = DatabaseNotInitializedError()
        error_msg = str(exc)
        
        self.assertIn("Database not initialized", error_msg)
        self.assertIn("z.data.handle", error_msg)
        self.assertIn("'action': 'create'", error_msg)
    
    def test_with_operation(self):
        """Test error specifies which operation failed."""
        exc = DatabaseNotInitializedError(operation="insert")
        error_msg = str(exc)
        
        self.assertIn("for operation 'insert'", error_msg)
    
    def test_with_table(self):
        """Test error specifies which table was targeted."""
        exc = DatabaseNotInitializedError(operation="read", table="users")
        error_msg = str(exc)
        
        self.assertIn("on table 'users'", error_msg)
    
    def test_shows_common_mistake(self):
        """Test error highlights INSERT before CREATE mistake."""
        exc = DatabaseNotInitializedError()
        error_msg = str(exc)
        
        self.assertIn("INSERT before CREATE", error_msg)
        self.assertIn("⚠️", error_msg)


class TestTableNotFoundError(unittest.TestCase):
    """Test TableNotFoundError."""
    
    def test_basic_table_error(self):
        """Test basic table not found error."""
        exc = TableNotFoundError("users")
        error_msg = str(exc)
        
        self.assertIn("Table 'users' not found", error_msg)
        self.assertIn("Create the table first", error_msg)
    
    def test_with_schema_name(self):
        """Test error includes schema name."""
        exc = TableNotFoundError("products", schema_name="inventory")
        error_msg = str(exc)
        
        self.assertIn("in schema 'inventory'", error_msg)
        self.assertIn("zSchema.inventory", error_msg)


class TestzUIParseError(unittest.TestCase):
    """Test zUIParseError."""
    
    def test_basic_parse_error(self):
        """Test basic zUI parsing error."""
        exc = zUIParseError("zUI.test.yaml", "Missing ~Root* key")
        error_msg = str(exc)
        
        self.assertIn("zUI.test.yaml", error_msg)
        self.assertIn("Missing ~Root* key", error_msg)
        self.assertIn("~Root*:", error_msg)
    
    def test_with_custom_suggestion(self):
        """Test error with custom suggestion."""
        exc = zUIParseError(
            "zUI.broken.yaml",
            "Invalid event type",
            suggestion="Use 'zDisplay', 'zData', or 'zDialog' events"
        )
        error_msg = str(exc)
        
        self.assertIn("Use 'zDisplay', 'zData', or 'zDialog'", error_msg)


class TestAuthenticationRequiredError(unittest.TestCase):
    """Test AuthenticationRequiredError."""
    
    def test_basic_auth_required(self):
        """Test basic authentication required error."""
        exc = AuthenticationRequiredError()
        error_msg = str(exc)
        
        self.assertIn("Authentication required", error_msg)
        self.assertIn("z.auth.login", error_msg)
    
    def test_with_resource(self):
        """Test error specifies resource."""
        exc = AuthenticationRequiredError(resource="Admin Panel")
        error_msg = str(exc)
        
        self.assertIn("for 'Admin Panel'", error_msg)
    
    def test_with_role(self):
        """Test error specifies required role."""
        exc = AuthenticationRequiredError(required_role="admin")
        error_msg = str(exc)
        
        self.assertIn("requires role: admin", error_msg)
    
    def test_with_permission(self):
        """Test error specifies required permission."""
        exc = AuthenticationRequiredError(required_permission="users.delete")
        error_msg = str(exc)
        
        self.assertIn("requires permission: users.delete", error_msg)
    
    def test_shows_yaml_example(self):
        """Test error shows zUI authentication example."""
        exc = AuthenticationRequiredError()
        error_msg = str(exc)
        
        self.assertIn("zDialog:", error_msg)
        self.assertIn("onSubmit:", error_msg)


class TestPermissionDeniedError(unittest.TestCase):
    """Test PermissionDeniedError."""
    
    def test_basic_permission_denied(self):
        """Test basic permission denied error."""
        exc = PermissionDeniedError()
        error_msg = str(exc)
        
        self.assertIn("does not have permission", error_msg)
        self.assertIn("grant_permission", error_msg)
    
    def test_with_user_and_resource(self):
        """Test error includes user and resource."""
        exc = PermissionDeniedError(user="john", resource="Delete Users")
        error_msg = str(exc)
        
        self.assertIn("User 'john'", error_msg)
        self.assertIn("to 'Delete Users'", error_msg)
    
    def test_with_required_role(self):
        """Test error includes required role."""
        exc = PermissionDeniedError(required_role="admin")
        error_msg = str(exc)
        
        self.assertIn("requires: admin", error_msg)


class TestConfigurationError(unittest.TestCase):
    """Test ConfigurationError."""
    
    def test_basic_config_error(self):
        """Test basic configuration error."""
        exc = ConfigurationError("zMode", "Invalid value 'Unknown'")
        error_msg = str(exc)
        
        self.assertIn("Configuration error for 'zMode'", error_msg)
        self.assertIn("Invalid value 'Unknown'", error_msg)
    
    def test_with_example(self):
        """Test error with example configuration."""
        exc = ConfigurationError(
            "websocket",
            "Port must be integer",
            example="websocket: {'host': '127.0.0.1', 'port': 8765}"
        )
        error_msg = str(exc)
        
        self.assertIn("Correct configuration:", error_msg)
        self.assertIn("'port': 8765", error_msg)


class TestPluginNotFoundError(unittest.TestCase):
    """Test PluginNotFoundError."""
    
    def test_basic_plugin_error(self):
        """Test basic plugin not found error."""
        exc = PluginNotFoundError("my_plugin")
        error_msg = str(exc)
        
        self.assertIn("Plugin 'my_plugin' not found", error_msg)
        self.assertIn("my_plugin.py", error_msg)
        self.assertIn("zFunc:", error_msg)
    
    def test_with_search_paths(self):
        """Test error includes searched paths."""
        exc = PluginNotFoundError("test", search_paths=["/path1", "/path2"])
        error_msg = str(exc)
        
        self.assertIn("Searched in:", error_msg)
        self.assertIn("/path1", error_msg)
        self.assertIn("/path2", error_msg)


class TestValidationError(unittest.TestCase):
    """Test ValidationError."""
    
    def test_basic_validation_error(self):
        """Test basic validation error."""
        exc = ValidationError("email", "not-an-email", "must be valid email")
        error_msg = str(exc)
        
        self.assertIn("Validation failed for field 'email'", error_msg)
        self.assertIn("must be valid email", error_msg)
    
    def test_with_schema_name(self):
        """Test error includes schema name."""
        exc = ValidationError("age", -5, "must be positive", schema_name="users")
        error_msg = str(exc)
        
        self.assertIn("in schema 'users'", error_msg)
    
    def test_context_storage(self):
        """Test validation context is stored."""
        exc = ValidationError("name", "", "required", schema_name="test")
        
        self.assertEqual(exc.context['field'], 'name')
        self.assertEqual(exc.context['value'], '')
        self.assertEqual(exc.context['constraint'], 'required')
        self.assertEqual(exc.context['schema'], 'test')


class TestzMachinePathError(unittest.TestCase):
    """Test zMachinePathError with different contexts."""
    
    def test_file_not_found_context(self):
        """Test error message for file not found context."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/Users/test/Library/Application Support/zolo-zcli/zSchema/users.yaml",
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("zMachine path error: zMachine.zSchema.users", error_msg)
        self.assertIn("File not found at zMachine path", error_msg)
        self.assertIn("zMachine.zSchema.users", error_msg)
        self.assertIn("Application Support/zolo-zcli/zSchema/users.yaml", error_msg)
        self.assertIn("Options:", error_msg)
    
    def test_syntax_error_context(self):
        """Test error message for syntax error context."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.",
                resolved_path="/Users/test/Library/Application Support/zolo-zcli",
                context_type="syntax"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("zMachine path error: zMachine.", error_msg)
        self.assertIn("zMachine syntax depends on context", error_msg)
        self.assertIn("In zSchema Data_Path (NO dot)", error_msg)
        self.assertIn('Data_Path: "zMachine"', error_msg)
    
    def test_context_storage(self):
        """Test that context is stored for debugging."""
        try:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/path/to/users.yaml",
                context_type="file"
            )
        except zMachinePathError as e:
            self.assertEqual(e.context['zpath'], 'zMachine.zSchema.users')
            self.assertEqual(e.context['resolved'], '/path/to/users.yaml')
            self.assertIn('os', e.context)
    
    def test_platform_specific_hints(self):
        """Test that platform-specific paths are shown."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/path/to/file",
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        # Check that all platforms are mentioned
        self.assertIn("macOS:", error_msg)
        self.assertIn("Linux:", error_msg)
        self.assertIn("Windows:", error_msg)
    
    def test_when_to_use_guidance(self):
        """Test that usage guidance is provided."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/path/to/file",
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("When to use zMachine:", error_msg)
        self.assertIn("User data that should persist across projects", error_msg)
        self.assertIn('Project-specific data (use \'@\' instead)', error_msg)
    
    def test_alternatives_provided(self):
        """Test that alternative solutions are provided."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/path/to/file",
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("Create the file at the resolved path", error_msg)
        self.assertIn("Use workspace path instead", error_msg)
        self.assertIn("Use absolute path", error_msg)
    
    def test_syntax_context_shows_correct_usage(self):
        """Test syntax error shows correct vs incorrect usage."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.",
                resolved_path="/path/to/base",
                context_type="syntax"
            )
        
        error_msg = str(cm.exception)
        self.assertIn('Data_Path: "zMachine"  # ✅ Correct', error_msg)
        self.assertIn('NOT: "zMachine." ❌', error_msg)
        self.assertIn('zVaFile: "zMachine.zSchema.users"', error_msg)
    
    def test_resolved_path_shown(self):
        """Test that the actual resolved path is shown."""
        test_path = "/Users/test/Library/Application Support/zolo-zcli/zSchema/users.yaml"
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path=test_path,
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("zMachine.zSchema.users", error_msg)
        self.assertIn("→", error_msg)  # Shows arrow to resolved path
        self.assertIn("users.yaml", error_msg)
    
    def test_actionable_hint_present(self):
        """Test that the 💡 actionable hint is present."""
        with self.assertRaises(zMachinePathError) as cm:
            raise zMachinePathError(
                zpath="zMachine.zSchema.users",
                resolved_path="/path/to/file",
                context_type="file"
            )
        
        error_msg = str(cm.exception)
        self.assertIn("💡", error_msg)  # Emoji hint indicator


class TestExceptionHierarchy(unittest.TestCase):
    """Test exception class hierarchy."""
    
    def test_all_inherit_from_base(self):
        """Test all custom exceptions inherit from zCLIException."""
        exceptions = [
            SchemaNotFoundError("test"),
            FormModelNotFoundError("test"),
            InvalidzPathError("test"),
            DatabaseNotInitializedError(),
            TableNotFoundError("test"),
            zUIParseError("test.yaml", "issue"),
            AuthenticationRequiredError(),
            PermissionDeniedError(),
            ConfigurationError("setting", "issue"),
            PluginNotFoundError("test"),
            ValidationError("field", "value", "constraint"),
            zMachinePathError("zMachine.test", "/path/to/test")
        ]
        
        for exc in exceptions:
            self.assertIsInstance(exc, zCLIException)
            self.assertIsInstance(exc, Exception)
    
    def test_all_have_hint_attribute(self):
        """Test all exceptions have hint attribute."""
        exceptions = [
            SchemaNotFoundError("test"),
            FormModelNotFoundError("test"),
            InvalidzPathError("test"),
            DatabaseNotInitializedError(),
        ]
        
        for exc in exceptions:
            self.assertTrue(hasattr(exc, 'hint'))
            self.assertIsNotNone(exc.hint)
    
    def test_all_have_context_attribute(self):
        """Test all exceptions have context dict."""
        exceptions = [
            SchemaNotFoundError("test"),
            FormModelNotFoundError("test"),
        ]
        
        for exc in exceptions:
            self.assertTrue(hasattr(exc, 'context'))
            self.assertIsInstance(exc.context, dict)


def run_tests(verbose=False):
    """Run all zExceptions tests with proper test discovery."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBaseException))
    suite.addTests(loader.loadTestsFromTestCase(TestSchemaNotFoundError))
    suite.addTests(loader.loadTestsFromTestCase(TestFormModelNotFoundError))
    suite.addTests(loader.loadTestsFromTestCase(TestInvalidzPathError))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseNotInitializedError))
    suite.addTests(loader.loadTestsFromTestCase(TestTableNotFoundError))
    suite.addTests(loader.loadTestsFromTestCase(TestzUIParseError))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationRequiredError))
    suite.addTests(loader.loadTestsFromTestCase(TestPermissionDeniedError))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationError))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginNotFoundError))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationError))
    suite.addTests(loader.loadTestsFromTestCase(TestzMachinePathError))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionHierarchy))

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

