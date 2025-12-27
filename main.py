"""CLI entry point for the zolo-zcli package."""

from zSys import BootstrapLogger

# ═══════════════════════════════════════════════════════════════════════════════
# BOOTSTRAP LOGGER - ALWAYS FIRST
# ═══════════════════════════════════════════════════════════════════════════════
# Initialize bootstrap logger before ANY other imports or operations.
# This ensures we capture the complete pre-boot process in framework.log.

boot_logger = BootstrapLogger()
boot_logger.info("zolo-zcli entry point started")

# Now safe to import zCLI (bootstrap logger will catch any import errors)
# Use centralized imports from zCLI package
import zCLI as zcli_package
from zCLI import argparse, os, sys, Path, zCLI
from version import get_version, get_package_info

boot_logger.debug("Python: %s", sys.version.split()[0])


def detect_installation_type(detailed: bool = False):
    """
    Detect zCLI installation type in a portable way.
    
    Args:
        detailed: If True, return detailed path info; if False, return simple type string
    
    Returns:
        str: Installation type ("editable", "standard", "uv", etc.)
    """
    try:
        zcli_path = Path(zcli_package.__file__).resolve()
        
        # Check if in site-packages (standard install)
        is_site_packages = 'site-packages' in str(zcli_path)
        
        # Check for virtual environment
        venv_path = os.getenv('VIRTUAL_ENV')
        in_venv = venv_path is not None
        
        # Determine installation type
        if not is_site_packages:
            # Editable install (pip install -e .)
            if detailed:
                return f"editable (pip -e) at {zcli_path.parent}"
            return "editable"
        
        elif in_venv:
            # Check if uv environment
            if 'uv' in venv_path.lower():
                if detailed:
                    return f"uv environment at {venv_path}"
                return "uv"
            else:
                if detailed:
                    return f"venv at {venv_path}"
                return "venv"
        
        else:
            # Standard system-wide install
            if detailed:
                return f"standard (site-packages) at {zcli_path.parent}"
            return "standard"
            
    except Exception as e:
        if detailed:
            return f"unknown (detection failed: {e})"
        return "unknown"


# Log installation type with details
boot_logger.debug("Installation: %s", detect_installation_type(detailed=True))
boot_logger.debug("Core zCLI imports completed")


def display_info():
    """Display zolo-zcli information banner."""
    boot_logger.debug("Displaying info banner")
    
    # Get simple installation type for banner (using portable detection)
    install_type = detect_installation_type(detailed=False)
    
    pkg_info = get_package_info()
    
    print(f"\n{pkg_info['name']} {get_version()} ({install_type})")
    print("A declarative based Framework")
    print(f"By {pkg_info['author']}")
    print("License: MIT\n")


def handle_shell_command(verbose: bool = False):
    """Handle shell command."""
    boot_logger.info("Launching zShell...")
    cli = zCLI()
    boot_logger.flush_to_framework(cli.logger.framework, verbose=verbose)
    cli.run_shell()


def handle_config_command(verbose: bool = False):
    """Handle config command - display only (read-only)."""
    boot_logger.info("Loading config display...")
    cli = zCLI({'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'})
    boot_logger.flush_to_framework(cli.logger.framework, verbose=verbose)
    
    cli.config.persistence.show_machine_config()
    cli.config.persistence.show_environment_config()


def handle_ztests_command(verbose: bool = False):
    """Handle zTests command (declarative test runner)."""
    boot_logger.info("Launching zTestRunner...")
    
    main_file = Path(__file__).resolve()
    project_root = main_file.parent
    test_runner_dir = project_root / "zTestRunner"
    
    if not test_runner_dir.exists():
        boot_logger.error("zTestRunner directory not found: %s", test_runner_dir)
        temp_cli = zCLI({'zMode': 'Terminal'})
        boot_logger.flush_to_framework(temp_cli.logger.framework, verbose=verbose)
        temp_cli.display.text(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
    boot_logger.debug("zTestRunner directory: %s", test_runner_dir)
    test_cli = zCLI({
        "zSpace": str(test_runner_dir.absolute()),
        "zMode": "Terminal"
    })
    boot_logger.flush_to_framework(test_cli.logger.framework, verbose=verbose)
    
    test_cli.zspark_obj["zVaFile"] = "@.zUI.test_menu"
    test_cli.zspark_obj["zBlock"] = "zVaF"
    test_cli.walker.run()


def handle_migrate_command(args, verbose: bool = False):
    """Handle schema migration command - thin CLI wrapper."""
    boot_logger.info("Preparing migration: %s", args.app_file)
    
    app_file = args.app_file
    if not Path(app_file).exists():
        boot_logger.error("App file not found: %s", app_file)
        temp_z = zCLI({'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'})
        boot_logger.flush_to_framework(temp_z.logger.framework, verbose=verbose)
        temp_z.display.text(f"❌ Error: App file not found: {app_file}")
        return 1
    
    boot_logger.debug("Initializing zCLI for migration...")
    z = zCLI({'zMode': 'Terminal'})
    boot_logger.flush_to_framework(z.logger.framework, verbose=verbose)
    
    return z.data.cli_migrate(
        app_file=str(Path(app_file).resolve()),
        auto_approve=getattr(args, 'auto_approve', False),
        dry_run=getattr(args, 'dry_run', False),
        specific_schema=getattr(args, 'schema', None),
        force_version=getattr(args, 'version', None)
    )


def handle_uninstall_command(verbose: bool = False):
    """Handle uninstall command with interactive menu."""
    boot_logger.info("Launching uninstall wizard...")
    
    zcli_package_dir = Path(zcli_package.__file__).parent
    boot_logger.debug("zCLI package directory: %s", zcli_package_dir)
    
    uninstall_cli = zCLI({
        "zWorkspace": str(zcli_package_dir),
        "zVaFile": "@.UI.zUI.zcli_sys",
        "zBlock": "Uninstall"
    })
    boot_logger.flush_to_framework(uninstall_cli.logger.framework, verbose=verbose)
    
    uninstall_cli.walker.run()


def main() -> None:
    """Main entry point for the zolo-zcli command."""
    boot_logger.info("Parsing command-line arguments")
    
    try:
        parser = argparse.ArgumentParser(
            description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
            prog="zolo",
        )
        
        # Global arguments (available for all commands)
        parser.add_argument("--version", action="version", version=f"zolo-zcli {get_version()}")
        parser.add_argument("--verbose", "-v", action="store_true", 
                          help="Show bootstrap process and detailed initialization")
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Shell subcommand
        shell_parser = subparsers.add_parser("shell", help="Start interactive zCLI shell")
        shell_parser.add_argument("--config", help="Path to custom config file (optional)")
        shell_parser.add_argument("--verbose", "-v", action="store_true", 
                                 help="Show bootstrap process and detailed initialization")
        
        # Config subcommand (read-only display)
        config_parser = subparsers.add_parser("config", help="Display zMachine and zEnvironment configuration")
        config_parser.add_argument("--verbose", "-v", action="store_true", 
                                  help="Show bootstrap process and detailed initialization")
        
        # zTests subcommand (declarative)
        ztests_parser = subparsers.add_parser("ztests", help="Run zCLI test suite")
        ztests_parser.add_argument("--verbose", "-v", action="store_true", 
                                  help="Show bootstrap process and detailed initialization")
        
        # Migrate subcommand (schema migrations)
        migrate_parser = subparsers.add_parser("migrate", help="Run schema migrations for an application")
        migrate_parser.add_argument("app_file", help="Path to application file (e.g., zTest.py or app.py)")
        migrate_parser.add_argument("--dry-run", action="store_true", help="Preview migrations without executing")
        migrate_parser.add_argument("--auto-approve", action="store_true", help="Skip confirmation prompts")
        migrate_parser.add_argument("--schema", help="Migrate specific schema only")
        migrate_parser.add_argument("--version", help="Force specific version (e.g., v2.0.0)")
        migrate_parser.add_argument("--history", action="store_true", help="Show migration history")
        migrate_parser.add_argument("--verbose", "-v", action="store_true", 
                                   help="Show bootstrap process and detailed initialization")
        
        # Uninstall subcommand
        uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall zolo-zcli framework")
        uninstall_group = uninstall_parser.add_mutually_exclusive_group()
        uninstall_group.add_argument("--clean", action="store_true", help="Remove package AND user data")
        uninstall_group.add_argument("--dependencies", action="store_true", help="Remove dependencies")
        uninstall_parser.add_argument("--verbose", "-v", action="store_true", 
                                     help="Show bootstrap process and detailed initialization")

        boot_logger.debug("Parsing arguments...")
        args = parser.parse_args()
        
        # Get verbose flag (default False if not present - for info banner case)
        verbose = getattr(args, 'verbose', False)
        boot_logger.debug("Command: %s, Verbose: %s", args.command or "info", verbose)

        # Route to handlers (with verbose flag)
        if args.command == "shell":
            handle_shell_command(verbose=verbose)
        elif args.command == "config":
            handle_config_command(verbose=verbose)
        elif args.command == "ztests":
            return handle_ztests_command(verbose=verbose)
        elif args.command == "migrate":
            return handle_migrate_command(args, verbose=verbose)
        elif args.command == "uninstall":
            return handle_uninstall_command(verbose=verbose)
        else:
            # Default: show info banner (no zCLI init needed)
            # If verbose, print bootstrap logs to stdout (no framework logger available)
            if verbose:
                boot_logger.print_buffered_logs()
            display_info()
    
    except KeyboardInterrupt:
        boot_logger.info("Interrupted by user (Ctrl+C)")
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        # Emergency dump: zCLI init failed or unexpected error
        boot_logger.critical("Unhandled exception: %s", str(e))
        boot_logger.emergency_dump(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
