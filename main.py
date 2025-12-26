"""CLI entry point for the zolo-zcli package."""

import zCLI as zcli_package
from zCLI import argparse, Path, zCLI
from zCLI.version import get_version

def handle_shell_command():
    """Handle shell command."""
    cli = zCLI()
    cli.run_shell()


def shell_main() -> None:
    """Direct entry point for zShell command (simplified UX)."""
    cli = zCLI()
    cli.run_shell()


def ztests_main() -> None:
    """Direct entry point for zTests command (simplified UX)."""
    handle_ztests_command()


def handle_config_command(args):
    """Handle config command."""
    cli = zCLI()

    if args.config_type == "machine":
        if args.show:
            cli.config.persistence.show_machine_config()
        elif args.reset and args.key:
            cli.config.persistence.persist_machine(args.key, reset=True)
        elif args.key and args.value:
            cli.config.persistence.persist_machine(args.key, args.value)
        else:
            cli.display.text("Usage: zolo config machine [key] [value] | --show | --reset [key]")
    elif args.config_type == "environment":
        if args.show:
            cli.config.persistence.show_environment_config()
        elif args.key and args.value:
            cli.config.persistence.persist_environment(args.key, args.value)
        else:
            cli.display.text("Usage: zolo config environment [key] [value] | --show")
    else:
        cli.display.text("Usage: zolo config {machine|environment} ...")


def handle_ztests_command():
    """Handle zTests command (declarative test runner)."""
    # Get zTestRunner folder using __file__ to ensure we get the right location
    # Note: Path resolution here is acceptable for CLI entry point (before zCLI init)
    main_file = Path(__file__).resolve()
    project_root = main_file.parent
    test_runner_dir = project_root / "zTestRunner"
    
    # Verify directory exists
    if not test_runner_dir.exists():
        # Create minimal zCLI instance for display (no subsystem dependencies)
        temp_cli = zCLI({'zMode': 'Terminal'})
        temp_cli.display.text(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
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
    """
    Handle schema migration command - thin CLI wrapper.
    
    Delegates all migration logic to z.data.migrate_app() following
    Linux From Scratch separation of concerns. This function only handles:
    - File path validation (CLI layer)
    - Display banners (CLI UI)
    - Result formatting (CLI UI)
    """
    # Validate app file exists
    app_file = args.app_file
    if not Path(app_file).exists():
        # Create minimal zCLI for error display
        temp_z = zCLI({'zMode': 'Terminal'})
        temp_z.display.text(f"❌ Error: App file not found: {app_file}")
        return 1
    
    app_file_path = Path(app_file).resolve()
    
    # Initialize zCLI (auto-loads .zEnv from app directory)
    z = zCLI({'zMode': 'Terminal'})  # Prevent walker auto-execution
    
    # Display banner
    z.display.text("\n" + "=" * 70)
    z.display.text("🔄 zMigration: Schema Evolution System")
    z.display.text("=" * 70)
    z.display.text(f"   App: {app_file_path.name}")
    z.display.text(f"   Directory: {app_file_path.parent}")
    z.display.text("=" * 70 + "\n")
    
    z.display.text("1️⃣ Initializing zCLI...")
    z.display.text("   ✅ zCLI initialized\n")
    
    # Discover schemas
    z.display.text("2️⃣ Discovering schemas...")
    schemas_discovered = z.data.discover_schemas()
    
    if not schemas_discovered:
        z.display.text("   ⚠️  No schemas found with ZDATA_*_URL environment variables")
        z.display.text("\n💡 Tip: Add ZDATA_USERS_URL=@.Data to your .zEnv file")
        z.display.text("=" * 70 + "\n")
        return 0
    
    # Display discovered schemas
    migration_enabled = [s for s in schemas_discovered if s['migration_enabled']]
    z.display.text(f"   ✅ Found {len(schemas_discovered)} schema(s), {len(migration_enabled)} migration-enabled\n")
    
    z.display.text("📊 Discovered Schemas:")
    z.display.text("-" * 70)
    for schema_info in schemas_discovered:
        status_icon = "✓" if schema_info['migration_enabled'] else "✗"
        status_text = "enabled" if schema_info['migration_enabled'] else "disabled"
        z.display.text(f"   {status_icon} {schema_info['name']}")
        z.display.text(f"      Data Type: {schema_info['data_type']}")
        z.display.text(f"      Version: {schema_info['version']}")
        z.display.text(f"      zMigration: {status_text}")
        if not schema_info['migration_enabled']:
            z.display.text("      → SKIPPED")
        z.display.text("")
    
    z.display.text("=" * 70)
    z.display.text("✅ Schema Discovery Complete")
    z.display.text("=" * 70 + "\n")
    
    if not migration_enabled:
        z.display.text("   No schemas enabled for migration (zMigration: false)\n")
        return 0
    
    # Execute migrations (delegate to z.data.migrate_app)
    z.display.text("3️⃣ Applying Migrations...")
    z.display.text(f"   📌 {len(migration_enabled)} schema(s) ready\n")
    z.display.text("=" * 70 + "\n")
    
    result = z.data.migrate_app(
        app_file=str(app_file_path),
        auto_approve=getattr(args, 'auto_approve', False),
        dry_run=getattr(args, 'dry_run', False),
        specific_schema=getattr(args, 'schema', None),
        force_version=getattr(args, 'version', None)
    )
    
    # Display results summary
    z.display.text("\n" + "=" * 70)
    z.display.text("📊 Migration Results")
    z.display.text("=" * 70 + "\n")
    
    if result['success']:
        z.display.text(f"   ✅ {result['success']} migration(s) applied successfully")
    if result['up_to_date']:
        z.display.text(f"   ℹ️  {result['up_to_date']} schema(s) already up to date")
    if result['failed']:
        z.display.text(f"   ❌ {result['failed']} migration(s) failed")
    if result['skipped']:
        z.display.text(f"   ⏭️  {result['skipped']} schema(s) skipped")
    
    z.display.text("\n" + "=" * 70)
    
    total_processed = result['success'] + result['up_to_date']
    if result['failed'] == 0 and total_processed > 0:
        z.display.text("✅ All schemas processed successfully!")
    elif result['failed'] > 0:
        z.display.text("⚠️  Some migrations failed. Check logs for details.")
    else:
        z.display.text("ℹ️  No migrations were applied.")
    
    z.display.text("=" * 70 + "\n")
    
    return 0 if result['failed'] == 0 else 1


def handle_uninstall_command():
    """Handle uninstall command with interactive menu."""
    # Get zCLI package installation directory
    # Note: Path resolution here is acceptable for CLI entry point (needed for zCLI workspace init)
    zcli_package_dir = Path(zcli_package.__file__).parent
    
    # Launch uninstall walker from package UI
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
