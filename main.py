"""CLI entry point for the zolo-zcli package."""

from zSys.logger import BootstrapLogger
from zSys.install import detect_installation_type
import cli_commands

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
from zCLI import argparse, sys, Path, zCLI
from version import get_version, get_package_info

boot_logger.debug("Python: %s", sys.version.split()[0])

# Log installation type with details
boot_logger.debug("Installation: %s", detect_installation_type(zcli_package, detailed=True))
boot_logger.debug("Core zCLI imports completed")


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
        
        # Note: Positional script argument handled manually after parsing
        # (argparse doesn't support optional positional with subparsers well)
        
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
        
        # Special handling for direct .py file execution OR zSpark.*.zolo execution
        # Check if first arg (after flags) is a .py file or matches zSpark.*.zolo pattern
        script_file = None
        zspark_file = None
        import sys as sys_module
        argv = sys_module.argv[1:]  # Skip program name
        
        # Filter out flags to find positional args
        positional_args = [arg for arg in argv if not arg.startswith('-')]
        
        if positional_args:
            first_arg = positional_args[0]
            
            # Python script execution (e.g., zolo zTest.py)
            if first_arg.endswith('.py'):
                script_file = first_arg
                boot_logger.debug("Detected Python script: %s", script_file)
                filtered_argv = [arg for arg in argv if arg != first_arg]
                args = parser.parse_args(filtered_argv)
            
            # zSpark.*.zolo execution (e.g., zolo zCloud → zSpark.zCloud.zolo)
            elif '.' not in first_arg:
                # Check if zSpark.{app_name}.zolo exists in CWD
                potential_zspark = Path.cwd() / f"zSpark.{first_arg}.zolo"
                if potential_zspark.exists():
                    zspark_file = str(potential_zspark)
                    boot_logger.debug("Detected zSpark file: %s", zspark_file)
                    filtered_argv = [arg for arg in argv if arg != first_arg]
                    args = parser.parse_args(filtered_argv)
                else:
                    # Not a zSpark file - normal command parsing
                    args = parser.parse_args()
            else:
                # Normal command parsing
                args = parser.parse_args()
        else:
            # Normal command parsing
            args = parser.parse_args()
        
        # Get verbose flag (default False if not present - for info banner case)
        verbose = getattr(args, 'verbose', False)
        boot_logger.debug("Command: %s, Script: %s, Verbose: %s", args.command or "info", script_file, verbose)

        # Route to handlers (with verbose flag) - all handlers in cli_commands.py
        if script_file:
            # Direct Python script execution (e.g., zolo zTest.py)
            return cli_commands.handle_script_command(boot_logger, sys, Path, script_file, verbose=verbose)
        elif zspark_file:
            # zSpark.*.zolo execution (e.g., zolo zCloud)
            return cli_commands.handle_zspark_command(boot_logger, zCLI, Path, zspark_file, verbose=verbose)
        elif args.command == "shell":
            cli_commands.handle_shell_command(boot_logger, zCLI, verbose=verbose)
        elif args.command == "config":
            cli_commands.handle_config_command(boot_logger, zCLI, verbose=verbose)
        elif args.command == "ztests":
            return cli_commands.handle_ztests_command(boot_logger, zCLI, Path, zcli_package, verbose=verbose)
        elif args.command == "migrate":
            return cli_commands.handle_migrate_command(boot_logger, zCLI, Path, args, verbose=verbose)
        elif args.command == "uninstall":
            cli_commands.handle_uninstall_command(boot_logger, zCLI, Path, zcli_package, verbose=verbose)
        else:
            # Default: show info banner (no zCLI init needed)
            # If verbose, print bootstrap logs to stdout (no framework logger available)
            if verbose:
                boot_logger.print_buffered_logs()
            cli_commands.display_info(boot_logger, zcli_package, get_version, get_package_info, detect_installation_type)
    
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
