"""
zCLI Custom Exceptions with Actionable Error Messages
Week 4.3 - Layer 1 Enhancement

These exceptions provide context-aware, actionable guidance to users.
They integrate seamlessly with zTraceback for logging and display.

Design Philosophy:
- Every exception includes a HINT for resolution
- Messages are context-aware (Python vs YAML vs Terminal)
- zPath syntax is consistent across all messages
- Integration with ExceptionContext for clean error handling

Usage:
    from zCLI.utils.zExceptions import SchemaNotFoundError
    
    # Raise with context-specific guidance
    raise SchemaNotFoundError("users", context_type="python")
    
    # Use with ExceptionContext for automatic logging
    with ExceptionContext(zcli.zTraceback, "schema loading"):
        if not schema:
            raise SchemaNotFoundError("users", context_type="yaml_zdata")
"""


class zCLIException(Exception):
    """Base exception for all zCLI errors with actionable messages."""
    
    def __init__(self, message: str, hint: str = None, context: dict = None):
        """
        Args:
            message: The error description
            hint: Actionable guidance (e.g., "Try: z.loader.handle('@.zSchema.users')")
            context: Additional context for debugging (stored in exception.context)
        """
        self.hint = hint
        self.context = context or {}
        
        # Build full message with hint
        full_message = message
        if hint:
            full_message += f"\n💡 {hint}"
        
        super().__init__(full_message)


class SchemaNotFoundError(zCLIException):
    """Raised when a schema file or loaded schema cannot be found."""
    
    def __init__(self, schema_name: str, context_type: str = "python", zpath: str = None):
        """
        Args:
            schema_name: Name of the missing schema (e.g., "users", "products")
            context_type: Where the error occurred:
                - "python": Python code calling z.loader.handle()
                - "yaml_zdata": zUI file with zData.model reference
                - "yaml_zdialog": zUI file with zDialog form model
            zpath: The full zPath that was attempted (optional)
        """
        if context_type == "python":
            hint = (
                f"Load it first: z.loader.handle('@.zSchema.{schema_name}')\n"
                f"   Expected file: zSchema.{schema_name}.yaml in workspace"
            )
        elif context_type == "yaml_zdata":
            hint = (
                f"In zUI files, use zPath syntax WITHOUT .yaml extension:\n"
                f"   zData:\n"
                f"     model: '@.zSchema.{schema_name}'  # NO .yaml!\n"
                f"     action: read\n"
                f"     table: your_table"
            )
        elif context_type == "yaml_zdialog":
            hint = (
                f"Ensure the schema is loaded AND the form model is defined:\n"
                f"   1. Load: z.loader.handle('@.zSchema.{schema_name}')\n"
                f"   2. Define in zSchema.{schema_name}.yaml:\n"
                f"      Models:\n"
                f"        YourFormName:\n"
                f"          fields:\n"
                f"            field1: {{type: string}}"
            )
        else:
            hint = f"Load the schema: z.loader.handle('@.zSchema.{schema_name}')"
        
        message = f"Schema '{schema_name}' not found"
        if zpath:
            message += f" (attempted: {zpath})"
        
        super().__init__(
            message,
            hint=hint,
            context={"schema": schema_name, "context_type": context_type, "zpath": zpath}
        )


class FormModelNotFoundError(zCLIException):
    """Raised when a form model is not defined in the loaded schema."""
    
    def __init__(self, model_name: str, schema_name: str = None, available_models: list = None):
        """
        Args:
            model_name: Name of the missing form model (e.g., "User", "SearchForm")
            schema_name: Name of the schema being searched (optional)
            available_models: List of available model names (optional)
        """
        available = ", ".join(available_models) if available_models else "None"
        
        schema_hint = f"zSchema.{schema_name}.yaml" if schema_name else "your schema file"
        hint = (
            f"Available models: {available}\n"
            f"   Define it in {schema_hint}:\n"
            f"   Models:\n"
            f"     {model_name}:\n"
            f"       fields:\n"
            f"         field1: {{type: string}}\n"
            f"         field2: {{type: integer}}"
        )
        
        super().__init__(
            f"Form model '{model_name}' not found in loaded schema",
            hint=hint,
            context={"model": model_name, "schema": schema_name, "available": available_models}
        )


class InvalidzPathError(zCLIException):
    """Raised when a zPath is malformed or cannot be resolved."""
    
    def __init__(self, zpath: str, reason: str = None):
        """
        Args:
            zpath: The invalid zPath that was attempted
            reason: Why the zPath is invalid (optional)
        """
        hint = (
            "zPath syntax:\n"
            "   '@.zSchema.name' - workspace-relative (NO .yaml extension)\n"
            "   '@.Schemas.zSchema.name' - subdirectory path\n"
            "   '~.zConfig.settings' - user config directory\n"
            "   'zMachine.zSchema.global' - platformdirs data directory\n\n"
            "Common mistakes:\n"
            "   ❌ '@.zSchema.users.yaml' - Don't include .yaml!\n"
            "   ✅ '@.zSchema.users' - Correct"
        )
        
        message = f"Invalid zPath: '{zpath}'"
        if reason:
            message += f" ({reason})"
        
        super().__init__(
            message,
            hint=hint,
            context={"zpath": zpath, "reason": reason}
        )


class DatabaseNotInitializedError(zCLIException):
    """Raised when attempting database operations without initialization."""
    
    def __init__(self, operation: str = None, table: str = None):
        """
        Args:
            operation: The operation that was attempted (e.g., "insert", "read")
            table: The table that was targeted (optional)
        """
        op_context = f" for operation '{operation}'" if operation else ""
        table_context = f" on table '{table}'" if table else ""
        
        hint = (
            "Initialize the database first:\n"
            "   Step 1: Create table structure\n"
            "   z.data.handle({\n"
            "       'action': 'create',\n"
            "       'model': '@.zSchema.your_schema'\n"
            "   })\n\n"
            "   Step 2: Then perform operations\n"
            "   z.data.handle({\n"
            "       'action': 'insert',\n"
            "       'table': 'your_table',\n"
            "       'data': {'field': 'value'}\n"
            "   })\n\n"
            "⚠️  Common mistake: INSERT before CREATE!"
        )
        
        super().__init__(
            f"Database not initialized{op_context}{table_context}",
            hint=hint,
            context={"operation": operation, "table": table}
        )


class TableNotFoundError(zCLIException):
    """Raised when a table doesn't exist in the database."""
    
    def __init__(self, table_name: str, schema_name: str = None):
        """
        Args:
            table_name: Name of the missing table
            schema_name: Name of the schema (optional)
        """
        schema_hint = f" in schema '{schema_name}'" if schema_name else ""
        hint = (
            f"Create the table first using zData 'create' action:\n"
            f"   z.data.handle({{\n"
            f"       'action': 'create',\n"
            f"       'model': '@.zSchema.{schema_name or 'your_schema'}'\n"
            f"   }})\n\n"
            f"Or check your schema file for table definitions."
        )
        
        super().__init__(
            f"Table '{table_name}' not found{schema_hint}",
            hint=hint,
            context={"table": table_name, "schema": schema_name}
        )


class zUIParseError(zCLIException):
    """Raised when a zUI file has syntax or structural errors."""
    
    def __init__(self, file_path: str, issue: str, suggestion: str = None):
        """
        Args:
            file_path: Path to the problematic zUI file
            issue: Description of the parsing issue
            suggestion: Specific suggestion for fixing (optional)
        """
        hint = suggestion or (
            "Check your zUI file structure:\n"
            "   zVaF:\n"
            "     ~Root*: ['Option 1', 'Option 2']\n"
            "     \n"
            "     'Option 1':\n"
            "       zDisplay:\n"
            "         event: text\n"
            "         content: 'Hello!'\n"
            "     \n"
            "     'Option 2':\n"
            "       zData:\n"
            "         model: '@.zSchema.users'\n"
            "         action: read\n\n"
            "See: Documentation/zUI_GUIDE.md for examples"
        )
        
        super().__init__(
            f"Error parsing zUI file '{file_path}': {issue}",
            hint=hint,
            context={"file": file_path, "issue": issue}
        )


class AuthenticationRequiredError(zCLIException):
    """Raised when attempting to access protected resources without authentication."""
    
    def __init__(self, resource: str = None, required_role: str = None, required_permission: str = None):
        """
        Args:
            resource: The resource being accessed (optional)
            required_role: Role required for access (optional)
            required_permission: Permission required for access (optional)
        """
        resource_msg = f" for '{resource}'" if resource else ""
        role_msg = f" (requires role: {required_role})" if required_role else ""
        perm_msg = f" (requires permission: {required_permission})" if required_permission else ""
        
        hint = (
            "Authenticate first:\n"
            "   Python: z.auth.login(username='user', password='pass')\n\n"
            "   Or in zUI:\n"
            "   'Login':\n"
            "     zDialog:\n"
            "       model: LoginForm\n"
            "       fields: [username, password]\n"
            "       onSubmit:\n"
            "         zFunc: '&auth_plugin.login(username=zConv.username, password=zConv.password)'"
        )
        
        super().__init__(
            f"Authentication required{resource_msg}{role_msg}{perm_msg}",
            hint=hint,
            context={
                "resource": resource,
                "required_role": required_role,
                "required_permission": required_permission
            }
        )


class PermissionDeniedError(zCLIException):
    """Raised when an authenticated user lacks required permissions."""
    
    def __init__(self, resource: str = None, user: str = None, required_role: str = None):
        """
        Args:
            resource: The resource being accessed
            user: Current user attempting access
            required_role: Role required for access
        """
        user_msg = f" User '{user}'" if user else "Current user"
        resource_msg = f" to '{resource}'" if resource else ""
        role_msg = f" (requires: {required_role})" if required_role else ""
        
        hint = (
            f"Contact an administrator to grant permissions.\n\n"
            f"Admins can grant permissions using:\n"
            f"   z.auth.grant_permission(user_id, permission='resource.action')\n"
            f"   z.auth.set_role(user_id, role='{required_role or 'admin'}')"
        )
        
        super().__init__(
            f"{user_msg} does not have permission{resource_msg}{role_msg}",
            hint=hint,
            context={"resource": resource, "user": user, "required_role": required_role}
        )


class ConfigurationError(zCLIException):
    """Raised when zCLI or subsystem configuration is invalid."""
    
    def __init__(self, setting: str, issue: str, example: str = None):
        """
        Args:
            setting: The configuration setting that's invalid
            issue: Description of what's wrong
            example: Example of correct configuration (optional)
        """
        hint_msg = f"Correct configuration:\n{example}" if example else (
            "Check your zSpark initialization:\n"
            "   z = zCLI({\n"
            "       'zWorkspace': '/path/to/project',\n"
            "       'zMode': 'Terminal',  # or 'zBifrost'\n"
            "       'zVerbose': True\n"
            "   })"
        )
        
        super().__init__(
            f"Configuration error for '{setting}': {issue}",
            hint=hint_msg,
            context={"setting": setting, "issue": issue}
        )


class PluginNotFoundError(zCLIException):
    """Raised when a plugin cannot be loaded or found."""
    
    def __init__(self, plugin_name: str, search_paths: list = None):
        """
        Args:
            plugin_name: Name of the missing plugin
            search_paths: Paths that were searched (optional)
        """
        paths_msg = ""
        if search_paths:
            paths_msg = f"\nSearched in: {', '.join(search_paths)}"
        
        hint = (
            f"Ensure plugin file exists:\n"
            f"   1. Create: {plugin_name}.py in workspace or utils/ directory\n"
            f"   2. Define functions with 'zcli' parameter:\n"
            f"      def my_function(zcli):\n"
            f"          zcli.display.text('Hello!')\n\n"
            f"   3. Call from zUI:\n"
            f"      zFunc: '&{plugin_name}.my_function()'"
        )
        
        super().__init__(
            f"Plugin '{plugin_name}' not found{paths_msg}",
            hint=hint,
            context={"plugin": plugin_name, "search_paths": search_paths}
        )


class ValidationError(zCLIException):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: any, constraint: str, schema_name: str = None):
        """
        Args:
            field: Field that failed validation
            value: The invalid value
            constraint: The validation constraint that failed
            schema_name: Name of the schema (optional)
        """
        schema_msg = f" in schema '{schema_name}'" if schema_name else ""
        hint = (
            f"Update the value to match constraints:\n"
            f"   Field '{field}' must satisfy: {constraint}\n\n"
            f"Check your schema definition for field constraints."
        )
        
        super().__init__(
            f"Validation failed for field '{field}'{schema_msg}: {constraint}",
            hint=hint,
            context={"field": field, "value": value, "constraint": constraint, "schema": schema_name}
        )


class zMachinePathError(zCLIException):
    """Raised when zMachine path resolution fails or file not found."""
    
    def __init__(self, zpath: str, resolved_path: str, context_type: str = "file"):
        """
        Args:
            zpath: The zMachine zPath that was attempted
            resolved_path: The actual OS-specific path it resolved to
            context_type: "file" (not found) or "syntax" (wrong format)
        """
        import platform
        os_name = platform.system()
        
        if context_type == "file":
            hint = (
                f"File not found at zMachine path.\n\n"
                f"🔍 Resolution on {os_name}:\n"
                f"   {zpath}\n"
                f"   → {resolved_path}\n\n"
                f"💡 Options:\n"
                f"   1. Create the file at the resolved path\n"
                f"   2. Use workspace path instead: '@.zSchema.users'\n"
                f"   3. Use absolute path: '~./path/to/file'\n\n"
                f"📁 Platform-Specific Paths:\n"
                f"   • macOS: ~/Library/Application Support/zolo-zcli/...\n"
                f"   • Linux: ~/.local/share/zolo-zcli/...\n"
                f"   • Windows: %LOCALAPPDATA%\\zolo-zcli\\...\n\n"
                f"🤔 When to use zMachine:\n"
                f"   ✅ User data that should persist across projects\n"
                f"   ✅ Global configuration files\n"
                f"   ✅ Cross-platform compatible storage\n"
                f"   ❌ Project-specific data (use '@' instead)"
            )
        else:  # syntax error
            hint = (
                f"zMachine syntax depends on context:\n\n"
                f"📝 In zSchema Data_Path (NO dot):\n"
                f"   Meta:\n"
                f"     Data_Path: \"zMachine\"  # ✅ Correct\n"
                f"     # NOT: \"zMachine.\" ❌\n\n"
                f"📝 In zVaFile references (WITH dot):\n"
                f"   zVaFile: \"zMachine.zSchema.users\"  # ✅ Correct\n"
                f"   # Also valid: \"~.zMachine.zSchema.users\"\n\n"
                f"🎯 Your OS resolves zMachine to:\n"
                f"   {resolved_path}"
            )
        
        super().__init__(
            f"zMachine path error: {zpath}",
            hint=hint,
            context={"zpath": zpath, "resolved": resolved_path, "os": os_name}
        )

