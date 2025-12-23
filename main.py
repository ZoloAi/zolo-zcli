"""CLI entry point for the zolo-zcli package."""

import argparse
from zCLI.version import get_version

def handle_shell_command():
    """Handle shell command."""
    from zCLI import zCLI
    cli = zCLI()
    cli.run_shell()


def shell_main() -> None:
    """Direct entry point for zShell command (simplified UX)."""
    from zCLI import zCLI
    cli = zCLI()
    cli.run_shell()


def ztests_main() -> None:
    """Direct entry point for zTests command (simplified UX)."""
    handle_ztests_command()


def handle_config_command(args):
    """Handle config command."""
    from zCLI import zCLI
    cli = zCLI()

    if args.config_type == "machine":
        if args.show:
            cli.config.persistence.show_machine_config()
        elif args.reset and args.key:
            cli.config.persistence.persist_machine(args.key, reset=True)
        elif args.key and args.value:
            cli.config.persistence.persist_machine(args.key, args.value)
        else:
            print("Usage: zolo config machine [key] [value] | --show | --reset [key]")
    elif args.config_type == "environment":
        if args.show:
            cli.config.persistence.show_environment_config()
        elif args.key and args.value:
            cli.config.persistence.persist_environment(args.key, args.value)
        else:
            print("Usage: zolo config environment [key] [value] | --show")
    else:
        print("Usage: zolo config {machine|environment} ...")


def handle_ztests_command():
    """Handle zTests command (declarative test runner)."""
    from pathlib import Path
    import os
    
    # Get zTestRunner folder using __file__ to ensure we get the right location
    main_file = Path(__file__).resolve()
    project_root = main_file.parent
    test_runner_dir = project_root / "zTestRunner"
    
    # Verify directory exists
    if not test_runner_dir.exists():
        print(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
    # Import zCLI after setting up paths
    from zCLI import zCLI
    
    # Launch declarative test runner following shell_cmd_help pattern
    test_cli = zCLI({
        "zSpace": str(test_runner_dir.absolute()),
        "zMode": "Terminal"
    })
    
    # Set walker configuration in zspark_obj (like shell_cmd_help does)
    test_cli.zspark_obj["zVaFile"] = "@.zUI.test_menu"
    test_cli.zspark_obj["zBlock"] = "zVaF"
    
    # Launch walker
    test_cli.walker.run()


def handle_migrate_command(args):
    """Handle schema migration command (zolo migrate)."""
    from pathlib import Path
    from zCLI import zCLI
    import os
    
    # Get app file path
    app_file = args.app_file
    if not Path(app_file).exists():
        print(f"❌ Error: App file not found: {app_file}")
        return 1
    
    # Resolve absolute path
    app_file_path = Path(app_file).resolve()
    app_dir = app_file_path.parent
    
    print("\n" + "=" * 70)
    print("🔄 zMigration: Schema Evolution System")
    print("=" * 70)
    print(f"   App: {app_file_path.name}")
    print(f"   Directory: {app_dir}")
    print("=" * 70 + "\n")
    
    # Load zSpark from app file (without executing zCLI.run())
    print("1️⃣ Loading application configuration...")
    import ast
    
    # Parse the Python file to extract zSpark
    with open(app_file_path, 'r') as f:
        file_content = f.read()
    
    try:
        tree = ast.parse(file_content)
        zspark = None
        
        # Find zSpark assignment
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'zSpark':
                        # Evaluate the zSpark dictionary
                        zspark = ast.literal_eval(node.value)
                        break
                if zspark:
                    break
        
        if not zspark:
            print(f"❌ Error: No zSpark configuration found in {app_file}")
            return 1
        
        app_name = zspark.get('title', 'Unknown')
        print(f"   ✅ Loaded zSpark for: {app_name}")
        
    except Exception as e:
        print(f"❌ Error parsing {app_file}: {e}")
        return 1
    
    # Initialize zCLI with app's zSpark
    print("\n2️⃣ Initializing zCLI...")
    # Override to prevent walker auto-execution
    migration_spark = zspark.copy()
    migration_spark['zMode'] = 'Terminal'
    
    # Remove walker keys to prevent auto-execution
    migration_spark.pop('zVaFile', None)
    migration_spark.pop('zVaFolder', None)
    migration_spark.pop('zBlock', None)
    
    # Note: User should run from app directory (cd zCloud && zolo migrate zTest.py)
    # This ensures .zEnv is loaded automatically by zCLI
    
    z = zCLI(migration_spark)
    print(f"   ✅ zCLI initialized")
    
    # Discover schemas from environment
    print("\n3️⃣ Discovering schemas...")
    print(f"   Workspace: {z.config.sys_paths.workspace_dir}")
    print(f"   Environment variables loaded: {len(z.config.environment.env)}")
    
    # Debug: Show what's in environment
    print(f"   Environment keys sample: {list(z.config.environment.env.keys())[:5]}")
    
    # Try multiple sources for ZDATA variables
    import os
    zdata_from_env = {k: v for k, v in z.config.environment.env.items() if k.startswith('ZDATA_')}
    zdata_from_os = {k: v for k, v in os.environ.items() if k.startswith('ZDATA_')}
    
    print(f"   ZDATA_* in z.config.environment.env: {len(zdata_from_env)}")
    print(f"   ZDATA_* in os.environ: {len(zdata_from_os)}")
    
    # Use os.environ as fallback
    zdata_vars = zdata_from_env if zdata_from_env else zdata_from_os
    
    print(f"   Using: {'z.config.environment.env' if zdata_from_env else 'os.environ'}")
    print(f"   ZDATA_* variables found: {len(zdata_vars)}")
    if zdata_vars:
        for key in sorted(zdata_vars.keys()):
            print(f"      • {key}")
    
    schemas_discovered = discover_schemas(z)
    
    if not schemas_discovered:
        print("   ⚠️  No schemas found with zMigration enabled")
        print("\n" + "=" * 70)
        print("💡 Tip: Add 'zMigration: true' to your schema Meta section")
        print("=" * 70 + "\n")
        return 0
    
    print(f"   ✅ Found {len(schemas_discovered)} schema(s)\n")
    
    # Display discovered schemas
    print("📊 Discovered Schemas:")
    print("-" * 70)
    for schema_info in schemas_discovered:
        status_icon = "✓" if schema_info['migration_enabled'] else "✗"
        status_text = "zMigration: enabled" if schema_info['migration_enabled'] else "zMigration: disabled"
        print(f"   {status_icon} {schema_info['name']}")
        print(f"      Data Type: {schema_info['data_type']}")
        print(f"      Version: {schema_info['version']}")
        print(f"      Status: {status_text}")
        if not schema_info['migration_enabled']:
            print(f"      → SKIPPED (migration not enabled)")
        print()
    
    print("=" * 70)
    print("✅ Schema Discovery Complete")
    print("=" * 70 + "\n")
    
    # Count schemas to migrate
    to_migrate = [s for s in schemas_discovered if s['migration_enabled']]
    if not to_migrate:
        print("   No schemas enabled for migration")
        print()
        return 0
    
    print(f"📌 {len(to_migrate)} schema(s) ready for migration\n")
    
    # Phase 4: Use zCLI's declarative migration system
    print("=" * 70)
    print("4️⃣ Applying Migrations (Declarative)")
    print("=" * 70 + "\n")
    
    auto_approve = args.auto_approve if hasattr(args, 'auto_approve') else False
    
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'up_to_date': 0
    }
    
    for schema_info in to_migrate:
        schema_name = schema_info['name']
        table_name = schema_name.split('.')[-1]
        schema_path = f"@.models.{schema_name}"
        current_version = schema_info['version']
        
        print(f"Migrating {schema_name}...")
        print(f"   Version: {current_version}")
        
        try:
            # Use zCLI's built-in migrate() - it handles everything!
            # First load the current schema, then migrate to it (establishes baseline)
            result = z.data.migrate(
                new_schema_path=schema_path,
                auto_approve=auto_approve,
                schema_version=current_version if current_version != 'none' else None
            )
            
            if result['success']:
                ops_executed = result.get('operations_executed', 0)
                if ops_executed == 0:
                    print(f"   ✅ Up to date (no changes)")
                    results['up_to_date'] += 1
                else:
                    print(f"   ✅ Migration complete ({ops_executed} operation(s))")
                    results['success'] += 1
            else:
                error = result.get('error', 'Unknown error')
                print(f"   ❌ Migration failed: {error}")
                results['failed'] += 1
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            z.logger.error(f"[zMigration] Exception for {schema_name}: {e}")
            results['failed'] += 1
        
        print()
    
    # Display results
    print("=" * 70)
    print("📊 Migration Results")
    print("=" * 70 + "\n")
    
    if results['success']:
        print(f"   ✅ {results['success']} migration(s) applied successfully")
    if results['up_to_date']:
        print(f"   ℹ️  {results['up_to_date']} schema(s) already up to date")
    if results['failed']:
        print(f"   ❌ {results['failed']} migration(s) failed")
    if results['skipped']:
        print(f"   ⏭️  {results['skipped']} migration(s) skipped")
    
    print("\n" + "=" * 70)
    
    total_processed = results['success'] + results['up_to_date']
    if results['failed'] == 0 and total_processed > 0:
        print("✅ All schemas processed successfully!")
    elif results['failed'] > 0:
        print("⚠️  Some migrations failed. Check logs for details.")
    else:
        print("ℹ️  No migrations were applied.")
    
    print("=" * 70 + "\n")
    
    return 0 if results['failed'] == 0 else 1


def discover_schemas(z):
    """
    Discover all schemas from environment variables.
    
    Scans for ZDATA_*_URL environment variables and loads corresponding schemas.
    Uses the zCLI instance's environment which includes .zEnv from app directory.
    
    Returns:
        List of schema info dicts with keys:
        - name: Schema name
        - path: Environment variable name
        - data_type: Backend type (csv, sqlite, postgresql)
        - version: zMigrationVersion (if present)
        - migration_enabled: Whether zMigration is enabled
    """
    import os
    schemas = []
    
    # Get environment from zCLI (includes .zEnv from app directory)
    env = z.config.environment.env
    
    # Fallback to os.environ if zCLI env doesn't have ZDATA vars
    if not any(k.startswith('ZDATA_') for k in env.keys()):
        env = os.environ
    
    # Scan environment for ZDATA_*_URL variables
    for key, value in env.items():
        if key.startswith('ZDATA_') and key.endswith('_URL'):
            # Extract schema name (e.g., ZDATA_USERS_URL → users)
            schema_name_upper = key[6:-4]  # Remove ZDATA_ and _URL
            schema_name = schema_name_upper.lower()
            
            # Try to load the schema
            try:
                # Construct likely schema path
                # Convention: ZDATA_USERS_URL → zSchema.users.yaml
                schema_path = f"@.models.zSchema.{schema_name}"
                
                # Load schema via zLoader
                schema = z.loader.handle(schema_path)
                
                if schema:
                    meta = schema.get('Meta', {})
                    
                    # Get migration flag (defaults to True per design decision)
                    migration_enabled = meta.get('zMigration', True)
                    
                    schemas.append({
                        'name': f"zSchema.{schema_name}",
                        'env_var': key,
                        'data_type': meta.get('Data_Type', 'unknown'),
                        'version': meta.get('zMigrationVersion', 'none'),
                        'migration_enabled': migration_enabled,
                        'schema': schema
                    })
            except Exception as e:
                # Schema not found or error loading - skip with debug info
                print(f"   [DEBUG] Skipped {key}: {e}")
    
    return schemas


def handle_uninstall_command():
    """Handle uninstall command with interactive menu."""
    from pathlib import Path
    from zCLI import zCLI
    
    # Get zCLI package installation directory
    import zCLI as zcli_module
    zcli_package_dir = Path(zcli_module.__file__).parent
    
    uninstall_cli = zCLI({
        "zWorkspace": str(zcli_package_dir),
        "zVaFile": "@.UI.zUI.zcli_sys",
        "zBlock": "Uninstall"
    })
    uninstall_cli.walker.run()


def main() -> None:
    """Main entry point for the zolo-zcli command."""
    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo",
    )
    
    parser.add_argument("--version", action="version", version=f"zolo-zcli {get_version()}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell subcommand
    shell_parser = subparsers.add_parser("shell", help="Start interactive zCLI shell")
    shell_parser.add_argument("--config", help="Path to custom config file (optional)")
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage zCLI configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_type")
    machine_parser = config_subparsers.add_parser("machine", help="Manage machine configuration")
    machine_parser.add_argument("key", nargs="?", help="Configuration key")
    machine_parser.add_argument("value", nargs="?", help="Value to set")
    machine_parser.add_argument("--show", action="store_true", help="Show configuration")
    machine_parser.add_argument("--reset", action="store_true", help="Reset to default")
    env_parser = config_subparsers.add_parser("environment", help="Manage environment configuration")
    env_parser.add_argument("key", nargs="?", help="Configuration key")
    env_parser.add_argument("value", nargs="?", help="Value to set")
    env_parser.add_argument("--show", action="store_true", help="Show configuration")
    
    # zTests subcommand (declarative)
    subparsers.add_parser("ztests", help="Run zCLI test suite")
    
    # Migrate subcommand (schema migrations)
    migrate_parser = subparsers.add_parser("migrate", help="Run schema migrations for an application")
    migrate_parser.add_argument("app_file", help="Path to application file (e.g., zTest.py or app.py)")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Preview migrations without executing")
    migrate_parser.add_argument("--auto-approve", action="store_true", help="Skip confirmation prompts")
    migrate_parser.add_argument("--schema", help="Migrate specific schema only")
    migrate_parser.add_argument("--version", help="Force specific version (e.g., v2.0.0)")
    migrate_parser.add_argument("--history", action="store_true", help="Show migration history")
    
    # Uninstall subcommand
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall zolo-zcli framework")
    uninstall_group = uninstall_parser.add_mutually_exclusive_group()
    uninstall_group.add_argument("--clean", action="store_true", help="Remove package AND user data")
    uninstall_group.add_argument("--dependencies", action="store_true", help="Remove dependencies")

    args = parser.parse_args()

    # Route to handlers
    if args.command == "shell":
        handle_shell_command()
    elif args.command == "config":
        handle_config_command(args)
    elif args.command == "ztests":
        return handle_ztests_command()
    elif args.command == "migrate":
        return handle_migrate_command(args)
    elif args.command == "uninstall":
        return handle_uninstall_command()
    else:
        handle_shell_command()


if __name__ == "__main__":
    main()
