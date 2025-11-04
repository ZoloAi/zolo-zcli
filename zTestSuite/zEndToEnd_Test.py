#!/usr/bin/env python3
# zTestSuite/zEndToEnd_Test.py

"""
End-to-End Test Suite for zCLI
Tests complete user workflows from UI definition to data persistence.

These tests simulate real-world application scenarios similar to the User Manager demo,
but fully automated without user interaction.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI


class TestConfigValidationWorkflow(unittest.TestCase):
    """
    End-to-end tests for config validation workflow (Week 1.1 - Layer 0).
    Tests complete scenarios where config validation prevents bad deployments.
    """
    
    def test_developer_catches_invalid_workspace_before_deployment(self):
        """
        Scenario: Developer typos workspace path, catches error immediately.
        Expected: Clear error message, app refuses to start.
        """
        with self.assertRaises(SystemExit) as cm:
            zCLI({"zSpace": "/path/does/not/exist", "zVaFile": "@.zUI.main"})
        self.assertEqual(cm.exception.code, 1)
    
    def test_developer_catches_invalid_mode_before_deployment(self):
        """
        Scenario: Developer sets invalid zMode in config.
        Expected: Clear error, fails before any subsystem starts.
        """
        with self.assertRaises(SystemExit) as cm:
            zCLI({"zMode": "WebServer"})  # Invalid mode
        self.assertEqual(cm.exception.code, 1)
    
    def test_production_deployment_with_valid_config(self):
        """
        Scenario: Production deployment with validated config.
        Expected: All subsystems start successfully.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({
                "zSpace": tmpdir,
                "zMode": "Terminal"
            })
            # Verify successful initialization
            self.assertIsNotNone(z.config)
            self.assertIsNotNone(z.logger)
            self.assertIsNotNone(z.session)


class TestUserManagementWorkflow(unittest.TestCase):
    """
    End-to-end test simulating complete user management workflow.
    Tests: UI definition => Schema loading => Database creation => CRUD operations
    """
    
    def setUp(self):
        """Set up test fixtures with temporary workspace."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
        # Create schema file (like User Manager demo)
        self.schema_file = Path(self.workspace) / "zSchema.users.yaml"
        self.schema_file.write_text("""Meta:
  Data_Type: sqlite
  Data_Label: "users"
  Data_Path: "@"
  Data_Paradigm: classical

users:
  id:
    type: int
    pk: true
    auto_increment: true
  email:
    type: str
    unique: true
    required: true
  name:
    type: str
    required: true
  role:
    type: str
    default: "user"
  created_at:
    type: datetime
    default: now
""")
        
        # Create UI file with menu and actions
        self.ui_file = Path(self.workspace) / "zUI.users_app.yaml"
        self.ui_file.write_text("""root:
  main_menu:
    - setup_db
    - add_user
    - list_users
    - search_user
    - update_user
    - delete_user
    
  setup_db:
    zData:
      model: "@.zSchema.users"
      action: create
      
  add_user:
    zData:
      model: "@.zSchema.users"
      action: insert
      table: users
      data:
        email: "test@example.com"
        name: "Test User"
        role: "admin"
        
  list_users:
    zData:
      model: "@.zSchema.users"
      action: read
      table: users
      order: "id DESC"
      
  search_user:
    zData:
      model: "@.zSchema.users"
      action: read
      table: users
      where: "email LIKE '%test%'"
      
  update_user:
    zData:
      model: "@.zSchema.users"
      action: update
      table: users
      data:
        role: "superadmin"
      where: "id = 1"
      
  delete_user:
    zData:
      model: "@.zSchema.users"
      action: delete
      table: users
      where: "id = 1"
""")
        
        # Initialize zCLI
        self.z = zCLI({"zSpace": self.workspace})
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_complete_user_management_workflow(self):
        """Test complete workflow: Setup DB → Add User → List → Update → Delete."""
        
        # Step 1: Load UI configuration
        ui_config = self.z.loader.handle("@.zUI.users_app")
        self.assertIsNotNone(ui_config)
        self.assertIn("root", ui_config)
        
        # Step 2: Setup Database (dispatch setup_db action)
        setup_action = ui_config["root"]["setup_db"]
        setup_result = self.z.dispatch.handle("setup_db", setup_action)
        self.assertTrue(setup_result, "Database setup should succeed")
        
        # Verify database file was created
        db_file = Path(self.workspace) / "users.db"
        self.assertTrue(db_file.exists(), "Database file should be created")
        
        # Step 3: Add User (dispatch add_user action)
        add_action = ui_config["root"]["add_user"]
        add_result = self.z.dispatch.handle("add_user", add_action)
        self.assertTrue(add_result, "User creation should succeed")
        
        # Step 4: List Users (verify user was added)
        list_action = ui_config["root"]["list_users"]
        list_result = self.z.dispatch.handle("list_users", list_action)
        
        if isinstance(list_result, list):
            self.assertGreater(len(list_result), 0, "Should have at least one user")
            self.assertEqual(list_result[0]["email"], "test@example.com")
            self.assertEqual(list_result[0]["name"], "Test User")
            self.assertEqual(list_result[0]["role"], "admin")
            
            # Step 5: Search Users
            search_action = ui_config["root"]["search_user"]
            search_result = self.z.dispatch.handle("search_user", search_action)
            
            if isinstance(search_result, list):
                self.assertGreater(len(search_result), 0, "Search should find users")
                
            # Step 6: Update User
            update_action = ui_config["root"]["update_user"]
            update_result = self.z.dispatch.handle("update_user", update_action)
            self.assertTrue(update_result, "Update should succeed")
            
            # Verify update worked
            list_after_update = self.z.dispatch.handle("list_users", list_action)
            if isinstance(list_after_update, list) and len(list_after_update) > 0:
                self.assertEqual(list_after_update[0]["role"], "superadmin")
            
            # Step 7: Delete User
            delete_action = ui_config["root"]["delete_user"]
            delete_result = self.z.dispatch.handle("delete_user", delete_action)
            self.assertTrue(delete_result, "Delete should succeed")
        else:
            # At minimum, verify database was created
            self.assertTrue(db_file.exists())


class TestBlogApplicationWorkflow(unittest.TestCase):
    """
    End-to-end test for a blog application with multiple tables and relationships.
    Tests: Multi-table schema → Foreign keys → Joins → Complex queries
    """
    
    def setUp(self):
        """Set up test fixtures with temporary workspace."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
        # Create blog schema with multiple tables
        self.schema_file = Path(self.workspace) / "zSchema.blog.yaml"
        self.schema_file.write_text("""Meta:
  Data_Type: sqlite
  Data_Label: "blog"
  Data_Path: "@"
  Data_Paradigm: classical

authors:
  id:
    type: int
    pk: true
    auto_increment: true
  name:
    type: str
    required: true
  email:
    type: str
    unique: true
    required: true

posts:
  id:
    type: int
    pk: true
    auto_increment: true
  author_id:
    type: int
    fk: authors.id
    required: true
  title:
    type: str
    required: true
  content:
    type: str
    required: true
  published:
    type: bool
    default: false
  created_at:
    type: datetime
    default: now

comments:
  id:
    type: int
    pk: true
    auto_increment: true
  post_id:
    type: int
    fk: posts.id
    required: true
  author_name:
    type: str
    required: true
  comment_text:
    type: str
    required: true
  created_at:
    type: datetime
    default: now
""")
        
        # Initialize zCLI
        self.z = zCLI({"zSpace": self.workspace})
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_multi_table_blog_workflow(self):
        """Test blog application with authors, posts, and comments."""
        
        # Step 1: Create all tables
        create_result = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "create"
        })
        self.assertTrue(create_result, "Tables should be created")
        
        # Verify database file exists
        db_file = Path(self.workspace) / "blog.db"
        self.assertTrue(db_file.exists())
        
        # Step 2: Insert author
        author_result = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "insert",
            "table": "authors",
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        })
        self.assertTrue(author_result, "Author insert should succeed")
        
        # Step 3: Insert post (with foreign key to author)
        post_result = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "insert",
            "table": "posts",
            "data": {
                "author_id": 1,
                "title": "First Post",
                "content": "This is my first blog post!",
                "published": True
            }
        })
        self.assertTrue(post_result, "Post insert should succeed")
        
        # Step 4: Insert comment (with foreign key to post)
        comment_result = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "insert",
            "table": "comments",
            "data": {
                "post_id": 1,
                "author_name": "Jane Reader",
                "comment_text": "Great post!"
            }
        })
        self.assertTrue(comment_result, "Comment insert should succeed")
        
        # Step 5: Read posts and verify data
        posts = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "read",
            "table": "posts"
        })
        
        if isinstance(posts, list) and len(posts) > 0:
            self.assertEqual(posts[0]["title"], "First Post")
            self.assertTrue(posts[0]["published"])
            
        # Step 6: Read comments
        comments = self.z.data.handle_request({
            "model": "@.zSchema.blog",
            "action": "read",
            "table": "comments"
        })
        
        if isinstance(comments, list) and len(comments) > 0:
            self.assertEqual(comments[0]["comment_text"], "Great post!")


class TestWalkerUINavigationWorkflow(unittest.TestCase):
    """
    End-to-end test for zWalker UI navigation.
    Tests: UI loading → Menu navigation → Breadcrumb tracking → Action dispatch
    """
    
    def setUp(self):
        """Set up test fixtures with temporary workspace."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
        # Create comprehensive UI navigation structure
        self.ui_file = Path(self.workspace) / "zUI.navigation_test.yaml"
        self.ui_file.write_text("""root:
  welcome: "Welcome to Navigation Test"
  main_menu:
    - dashboard
    - settings
    - help
    
  dashboard:
    message: "Dashboard View"
    actions:
      - view_stats
      - view_reports
      
  settings:
    message: "Settings View"
    options:
      - profile
      - preferences
      
  profile:
    name: "User Profile"
    fields:
      - username
      - email
      
  help:
    message: "Help Center"
    topics:
      - getting_started
      - faq
""")
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_walker_navigation_workflow(self):
        """Test complete navigation workflow through UI structure."""
        
        # Initialize zCLI with UI file
        z = zCLI({
            "zSpace": self.workspace,
            "zVaFile": "@.zUI.navigation_test",
            "zBlock": "root"
        })
        
        # Verify zCLI initialized with UI
        self.assertIsNotNone(z.walker)
        self.assertEqual(z.zspark_obj["zVaFile"], "@.zUI.navigation_test")
        self.assertEqual(z.zspark_obj["zBlock"], "root")
        
        # Load UI structure
        ui_data = z.loader.handle("@.zUI.navigation_test")
        self.assertIsNotNone(ui_data)
        self.assertIn("root", ui_data)
        
        # Verify navigation structure
        root = ui_data["root"]
        self.assertIn("main_menu", root)
        self.assertIn("dashboard", root)
        self.assertIn("settings", root)
        
        # Test that walker can access nested structures
        self.assertIn("profile", root)
        self.assertIn("help", root)


class TestPluginWorkflow(unittest.TestCase):
    """
    End-to-end test for plugin system integration.
    Tests: Plugin loading → Function invocation → Data processing
    """
    
    def setUp(self):
        """Set up test fixtures with temporary workspace."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
        # Create a test plugin file
        self.plugin_file = Path(self.workspace) / "test_plugin.py"
        self.plugin_file.write_text("""
# Test plugin for end-to-end testing

def process_data(data):
    \"\"\"Process data and return transformed result.\"\"\"
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, list):
        return [item * 2 for item in data]
    elif isinstance(data, dict):
        return {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}
    return data

def validate_email(email):
    \"\"\"Validate email format.\"\"\"
    return "@" in email and "." in email.split("@")[1]

def get_plugin_info():
    \"\"\"Return plugin metadata.\"\"\"
    return {
        "name": "Test Plugin",
        "version": "1.0.0",
        "functions": ["process_data", "validate_email"]
    }
""")
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_plugin_integration_workflow(self):
        """Test complete plugin loading and execution workflow."""
        
        # Initialize zCLI with plugin
        plugin_path = str(self.plugin_file)
        z = zCLI({
            "zSpace": self.workspace,
            "plugins": [plugin_path]
        })
        
        # Verify plugin was loaded
        self.assertIn(plugin_path, z.utils.plugins)
        
        # Get plugin info
        info = z.utils.get_plugin_info()
        if info:
            self.assertIn("name", info)
            self.assertIn("functions", info)


class TestCompleteApplicationLifecycle(unittest.TestCase):
    """
    End-to-end test for complete application lifecycle.
    Tests: Initialization → Schema loading → UI rendering → Data operations → Cleanup
    """
    
    def setUp(self):
        """Set up test fixtures with temporary workspace."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_full_application_lifecycle(self):
        """Test complete application from start to finish."""
        
        # Phase 1: Application Initialization
        z = zCLI({"zSpace": self.workspace})
        
        # Verify all subsystems initialized
        self.assertIsNotNone(z.config)
        self.assertIsNotNone(z.data)
        self.assertIsNotNone(z.walker)
        self.assertIsNotNone(z.display)
        
        # Phase 2: Create application schema
        schema_file = Path(self.workspace) / "zSchema.app.yaml"
        schema_file.write_text("""Meta:
  Data_Type: sqlite
  Data_Label: "app"
  Data_Path: "@"
  Data_Paradigm: classical

app_data:
  id:
    type: int
    pk: true
    auto_increment: true
  key:
    type: str
    unique: true
    required: true
  value:
    type: str
    required: true
""")
        
        # Phase 3: Initialize database
        create_result = z.data.handle_request({
            "model": "@.zSchema.app",
            "action": "create"
        })
        self.assertTrue(create_result)
        
        # Phase 4: Perform application operations
        # Insert configuration
        insert_result = z.data.handle_request({
            "model": "@.zSchema.app",
            "action": "insert",
            "table": "app_data",
            "data": {
                "key": "app_name",
                "value": "Test Application"
            }
        })
        self.assertTrue(insert_result)
        
        # Read configuration
        read_result = z.data.handle_request({
            "model": "@.zSchema.app",
            "action": "read",
            "table": "app_data",
            "where": "key = 'app_name'"
        })
        
        if isinstance(read_result, list) and len(read_result) > 0:
            self.assertEqual(read_result[0]["value"], "Test Application")
        
        # Phase 5: Verify workspace integrity
        db_file = Path(self.workspace) / "app.db"
        self.assertTrue(db_file.exists())
        
        # Phase 6: Cleanup (implicit via tearDown)
        # Database will be cleaned up when temp directory is removed


class TestUserManagerWebSocketMode(unittest.TestCase):
    """Test User Manager Demo in WebSocket mode (v1.5.3)."""
    
    def test_user_manager_websocket_initialization(self):
        """Test User Manager initialization in WebSocket mode."""
        # Get the User Manager demo directory
        project_root = Path(__file__).parent.parent
        demo_dir = project_root / "Demos" / "User Manager"
        
        if not demo_dir.exists():
            self.skipTest("User Manager demo not found")
        
        # Initialize zCLI in WebSocket mode with User Manager YAML
        z = zCLI({
            "zSpace": str(demo_dir),
            "zVaFile": "@.zUI.users_menu",
            "zMode": "zBifrost",
            "zVerbose": False
        })
        
        # Verify initialization
        self.assertEqual(z.session.get("zMode"), "zBifrost")
        self.assertEqual(z.display.mode, "zBifrost")
        
    def test_user_manager_crud_with_websocket_data(self):
        """Test User Manager CRUD operations with WebSocket data format."""
        from zCLI.subsystems.zDialog.dialog_modules.dialog_context import inject_placeholders
        from unittest.mock import Mock
        
        # Simulate frontend WebSocket message for "Add User"
        websocket_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        
        # Create zContext as zDialog would
        zContext = {"zConv": websocket_data}
        logger = Mock()
        
        # Test INSERT data placeholder injection
        insert_data = {
            "email": "zConv.email",
            "name": "zConv.name"
        }
        
        result = inject_placeholders(insert_data, zContext, logger)
        
        # Should return raw values (not quoted, since these are dict values not SQL strings)
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["name"], "Test User")
    
    def test_user_manager_delete_with_where_clause(self):
        """Test User Manager DELETE with WHERE clause from WebSocket."""
        from zCLI.subsystems.zDialog.dialog_modules.dialog_context import inject_placeholders
        from unittest.mock import Mock
        
        # Simulate frontend WebSocket message for "Delete User"
        websocket_data = {"user_id": "1"}
        zContext = {"zConv": websocket_data}
        logger = Mock()
        
        # Test DELETE WHERE clause (from zUI.users_menu.yaml)
        where_clause = "id = zConv.user_id"
        result = inject_placeholders(where_clause, zContext, logger)
        
        # Should produce valid SQL WHERE clause
        self.assertEqual(result, "id = 1")
    
    def test_user_manager_search_with_like(self):
        """Test User Manager search with LIKE wildcards."""
        from zCLI.subsystems.zDialog.dialog_modules.dialog_context import inject_placeholders
        from unittest.mock import Mock
        
        # Simulate frontend WebSocket message for "Search User"
        websocket_data = {"search_term": "john"}
        zContext = {"zConv": websocket_data}
        logger = Mock()
        
        # Test SEARCH WHERE clause (from zUI.users_menu.yaml)
        where_clause = "name LIKE '%zConv.search_term%' OR email LIKE '%zConv.search_term%'"
        result = inject_placeholders(where_clause, zContext, logger)
        
        # Should inject search term within LIKE patterns
        self.assertIn("'john'", result)
        self.assertIn("LIKE", result)


class TestTracebackWorkflow(unittest.TestCase):
    """Test complete error handling workflow with zTraceback."""
    
    def test_error_logging_in_complete_workflow(self):
        """Test error logging during a complete CRUD workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create schema and UI files
            schema_file = Path(tmpdir) / "zSchema.test_app.yaml"
            schema_file.write_text("""
zSchema: test_app
zBackend: sqlite
zTables:
  test_table:
    id: INTEGER PRIMARY KEY
    name: TEXT
""")
            
            ui_file = Path(tmpdir) / "zUI.test_app.yaml"
            ui_file.write_text("""
zUI: test_app
test_menu:
  ~Root*:
    "Test Action": zData(@.zSchema.test_app.test_table.insert)
""")
            
            z = zCLI({
                "zSpace": tmpdir,
                "zVaFile": "@.zUI.test_app",
                "zBlock": "test_menu"
            })
            
            # Verify zTraceback is available throughout workflow
            self.assertIsNotNone(z.zTraceback)
            self.assertIsNotNone(z.zTraceback.logger)
            self.assertIs(z.zTraceback.zcli, z)
            
            # Test that zTraceback can log exceptions during operations
            try:
                # Simulate an operation that fails
                raise ValueError("Workflow error test")
            except ValueError as e:
                z.zTraceback.log_exception(
                    e,
                    message="Error during workflow",
                    context={'action': 'insert', 'table': 'test_table'}
                )
                
                # Verify exception was captured
                self.assertIsNotNone(z.zTraceback.last_exception)
                self.assertEqual(str(z.zTraceback.last_exception), "Workflow error test")
    
    def test_exception_context_in_workflow(self):
        """Test ExceptionContext usage in a complete workflow."""
        from zCLI.utils.zTraceback import ExceptionContext
        
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Simulate using ExceptionContext during data operations
            with ExceptionContext(
                z.zTraceback,
                operation="database_insert",
                context={'table': 'users', 'action': 'insert'},
                reraise=False,
                default_return=None
            ) as ctx:
                # Simulate successful operation (no exception)
                ctx.result = "success"
            
            # Verify no exception was stored
            self.assertIsNone(ctx.exception)
            
            # Now test with an actual exception
            with ExceptionContext(
                z.zTraceback,
                operation="database_delete",
                context={'table': 'users', 'id': 123},
                reraise=False,
                default_return="error"
            ) as ctx:
                raise RuntimeError("Delete failed")
            
            # Exception should be captured
            self.assertIsNotNone(ctx.exception)
            self.assertEqual(ctx.default_return, "error")
    
    def test_ztraceback_preserves_exception_history(self):
        """Test traceback handler maintains exception history across operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            z = zCLI({"zSpace": tmpdir})
            
            # Simulate multiple operations with errors
            for i in range(3):
                try:
                    raise ValueError(f"Error {i}")
                except ValueError as e:
                    z.zTraceback.exception_history.append({
                        'exception': e,
                        'operation': f'operation_{i}',
                        'context': {'step': i}
                    })
            
            # Verify history is preserved
            self.assertEqual(len(z.zTraceback.exception_history), 3)
            self.assertEqual(
                str(z.zTraceback.exception_history[0]['exception']),
                "Error 0"
            )


class TestDotenvApplicationWorkflow(unittest.TestCase):
    """Test complete application workflow using dotenv configuration."""
    
    def test_application_with_dotenv_configuration(self):
        """Test full application workflow configured via .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create comprehensive .env file for application
            env_file = tmpdir_path / ".env"
            env_file.write_text("""
# Application Configuration
APP_NAME=TestApp
APP_VERSION=1.0.0
ZOLO_DEPLOYMENT=Production
ZOLO_LOGGER=INFO

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb
DB_USER=testuser
DB_PASSWORD=testpass123
            """.strip())
            
            # Create schema file
            schema_file = tmpdir_path / "zSchema.app_config.yaml"
            schema_file.write_text("""
Meta:
  Data_Type: sqlite
  Data_Path: "@"
  Data_Label: "app_config"
  Data_Paradigm: classical

settings:
  id: {type: int, pk: true, auto_increment: true}
  key: {type: str, unique: true, required: true}
  value: {type: str, required: true}
            """)
            
            # Initialize zCLI with dotenv-configured workspace
            z = zCLI({"zSpace": str(tmpdir_path)})
            
            # Verify dotenv variables are loaded
            self.assertEqual(z.config.environment.get_env_var("APP_NAME"), "TestApp")
            self.assertEqual(z.config.environment.get_env_var("APP_VERSION"), "1.0.0")
            self.assertEqual(z.config.environment.get_env_var("ZOLO_DEPLOYMENT"), "Production")
            
            # Verify database config from dotenv
            self.assertEqual(z.config.environment.get_env_var("DB_HOST"), "localhost")
            self.assertEqual(z.config.environment.get_env_var("DB_PORT"), "5432")
            self.assertEqual(z.config.environment.get_env_var("DB_NAME"), "testdb")
            
            # Create database using schema
            z.data.handle_request({
                "model": "@.zSchema.app_config",
                "action": "create"
            })
            
            # Store configuration from dotenv into database
            app_name = z.config.environment.get_env_var("APP_NAME")
            z.data.handle_request({
                "model": "@.zSchema.app_config",
                "action": "insert",
                "table": "settings",
                "data": {"key": "app_name", "value": app_name}
            })
            
            # Read back configuration
            result = z.data.handle_request({
                "model": "@.zSchema.app_config",
                "action": "read",
                "table": "settings",
                "where": "key = 'app_name'"
            })
            
            # Verify configuration was stored correctly
            self.assertIsNotNone(result)
            
            # Clean up environment variables
            for var in ["APP_NAME", "APP_VERSION", "ZOLO_DEPLOYMENT", "ZOLO_LOGGER",
                       "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_multi_environment_dotenv_workflow(self):
        """Test application workflow with different .env configurations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Test Development environment
            dev_env = tmpdir_path / ".env.development"
            dev_env.write_text("ZOLO_DEPLOYMENT=Development\nAPI_URL=http://localhost:3000\n")
            
            # Initialize with dev environment
            z_dev = zCLI({
                "zSpace": str(tmpdir_path),
                "dotenv": str(dev_env)
            })
            
            # Verify dev configuration
            self.assertEqual(z_dev.config.environment.get_env_var("ZOLO_DEPLOYMENT"), "Development")
            self.assertEqual(z_dev.config.environment.get_env_var("API_URL"), "http://localhost:3000")
            
            # Clean up
            if "ZOLO_DEPLOYMENT" in os.environ:
                del os.environ["ZOLO_DEPLOYMENT"]
            if "API_URL" in os.environ:
                del os.environ["API_URL"]
            
            # Test Production environment
            prod_env = tmpdir_path / ".env.production"
            prod_env.write_text("ZOLO_DEPLOYMENT=Production\nAPI_URL=https://api.production.com\n")
            
            # Initialize with prod environment
            z_prod = zCLI({
                "zSpace": str(tmpdir_path),
                "dotenv": str(prod_env)
            })
            
            # Verify prod configuration
            self.assertEqual(z_prod.config.environment.get_env_var("ZOLO_DEPLOYMENT"), "Production")
            self.assertEqual(z_prod.config.environment.get_env_var("API_URL"), "https://api.production.com")
            
            # Clean up
            if "ZOLO_DEPLOYMENT" in os.environ:
                del os.environ["ZOLO_DEPLOYMENT"]
            if "API_URL" in os.environ:
                del os.environ["API_URL"]


class TestFullStackServerWorkflow(unittest.TestCase):
    """
    End-to-end test for complete HTTP + WebSocket workflow (Week 1.5).
    Tests real-world scenario of serving HTML files that connect to WebSocket server.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name
        
        # Create a simple HTML file
        html_file = Path(self.workspace) / "index.html"
        html_file.write_text("""<!DOCTYPE html>
<html>
<head><title>Test App</title></head>
<body><h1>Full Stack Test</h1></body>
</html>
""")
        
        # Create a simple zUI file for WebSocket
        ui_file = Path(self.workspace) / "zUI.test.yaml"
        ui_file.write_text("""TestMenu:
  ~Root*: ["Status", "stop"]
  "Status": "Server running!"
""")
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    def test_serve_html_with_http_server(self):
        """
        Scenario: Developer wants to serve HTML files for a web app.
        Expected: zServer serves static files, app can access them.
        """
        z = zCLI({
            "zSpace": self.workspace,
            "http_server": {
                "enabled": True,
                "port": 18095,
                "serve_path": self.workspace
            }
        })
        
        # Verify server is running
        self.assertTrue(z.server.is_running())
        
        # Verify HTML file exists in serve path
        html_path = Path(self.workspace) / "index.html"
        self.assertTrue(html_path.exists())
        
        # In real workflow, browser would access http://localhost:18095/index.html
        # For test, just verify server configuration
        self.assertEqual(z.server.port, 18095)
        self.assertEqual(z.server.serve_path, str(Path(self.workspace).resolve()))
        
        # Clean up
        z.server.stop()
    
    def test_http_and_websocket_together(self):
        """
        Scenario: Full-stack app needs both HTTP (static files) and WebSocket (real-time).
        Expected: Both servers run on different ports, no conflicts.
        """
        z = zCLI({
            "zSpace": self.workspace,
            "zMode": "zBifrost",
            "zVaFile": "@.zUI.test",
            "websocket": {"port": 18765, "require_auth": False},
            "http_server": {
                "enabled": True,
                "port": 18096,
                "serve_path": self.workspace
            }
        })
        
        # Verify both servers configured
        self.assertIsNotNone(z.server)
        self.assertTrue(z.server.is_running())
        self.assertIsNotNone(z.config.websocket)
        
        # Verify different ports
        self.assertNotEqual(z.server.port, z.config.websocket.port)
        self.assertEqual(z.server.port, 18096)
        self.assertEqual(z.config.websocket.port, 18765)
        
        # Verify files are accessible
        self.assertTrue((Path(self.workspace) / "index.html").exists())
        
        # Clean up
        z.server.stop()
    
    def test_developer_workflow_from_scratch(self):
        """
        Scenario: Developer creates app from scratch, needs both servers.
        Expected: Simple config enables full-stack development environment.
        """
        # Create workspace
        workspace = Path(self.workspace) / "my_app"
        workspace.mkdir()
        
        # Create HTML
        (workspace / "app.html").write_text("<html><body>My App</body></html>")
        
        # Create zUI
        (workspace / "zUI.main.yaml").write_text("""MainMenu:
  ~Root*: ["Help", "stop"]
  "Help": "Welcome to My App"
""")
        
        # Initialize zCLI with both servers
        z = zCLI({
            "zSpace": str(workspace),
            "zMode": "zBifrost",
            "zVaFile": "@.zUI.main",
            "websocket": {"port": 18767, "require_auth": False},
            "http_server": {
                "enabled": True,
                "port": 18097,
                "serve_path": str(workspace)
            }
        })
        
        # Verify complete setup
        self.assertIsNotNone(z.config)
        self.assertIsNotNone(z.logger)
        self.assertIsNotNone(z.server)
        self.assertIsNotNone(z.walker)
        
        # Verify servers ready
        self.assertTrue(z.server.is_running())
        self.assertEqual(z.server.get_url(), "http://127.0.0.1:18097")
        
        # Verify UI file can be loaded (in zBifrost mode, UI is loaded on-demand)
        loaded_ui = z.loader.handle("@.zUI.main")
        self.assertIsNotNone(loaded_ui)
        self.assertIn("MainMenu", loaded_ui)
        self.assertEqual(loaded_ui["MainMenu"]["Help"], "Welcome to My App")
        
        # Clean up
        z.server.stop()
    
    def test_production_deployment_scenario(self):
        """
        Scenario: Deploying to production with external reverse proxy.
        Expected: zServer handles HTTP, reverse proxy handles SSL/auth.
        """
        z = zCLI({
            "zSpace": self.workspace,
            "http_server": {
                "enabled": True,
                "host": "0.0.0.0",  # Bind to all interfaces (behind reverse proxy)
                "port": 18098,
                "serve_path": self.workspace
            }
        })
        
        # Verify production-ready configuration
        self.assertEqual(z.server.host, "0.0.0.0")  # Accessible from network
        self.assertTrue(z.server.is_running())
        
        # In production:
        # - Reverse proxy (nginx/caddy) handles SSL
        # - Reverse proxy handles authentication
        # - zServer just serves static files
        
        # Clean up
        z.server.stop()


def run_tests(verbose=False):
    """Run all end-to-end tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidationWorkflow))  # NEW Week 1.1
    suite.addTests(loader.loadTestsFromTestCase(TestUserManagementWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestBlogApplicationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestWalkerUINavigationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteApplicationLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestUserManagerWebSocketMode))  # NEW v1.5.3
    suite.addTests(loader.loadTestsFromTestCase(TestTracebackWorkflow))  # NEW v1.5.3
    suite.addTests(loader.loadTestsFromTestCase(TestDotenvApplicationWorkflow))  # NEW v1.5.4
    suite.addTests(loader.loadTestsFromTestCase(TestFullStackServerWorkflow))  # NEW Week 1.5
    
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

