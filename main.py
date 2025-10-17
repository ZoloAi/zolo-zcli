"""CLI entry point for the zolo-zcli package."""

import argparse
from zCLI.version import get_version


def main() -> None:
    """Main entry point for the zolo-zcli command."""

    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo",
    )
    
    # Global arguments
    parser.add_argument(
        "--version",
        action="version",
        version=f"zolo-zcli {get_version()}",
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell subcommand
    shell_parser = subparsers.add_parser(
        "shell",
        help="Start interactive zCLI shell"
    )
    shell_parser.add_argument(
        "--config",
        help="Path to custom config file (optional)"
    )
    
    # Config subcommand for persistence
    config_parser = subparsers.add_parser(
        "config",
        help="Manage zCLI configuration (machine, environment)"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_type", help="Configuration type")
    
    # Machine config subcommand
    machine_parser = config_subparsers.add_parser("machine", help="Manage machine configuration")
    machine_parser.add_argument("key", nargs="?", help="Configuration key to set/reset")
    machine_parser.add_argument("value", nargs="?", help="Value to set")
    machine_parser.add_argument("--show", action="store_true", help="Show current machine configuration")
    machine_parser.add_argument("--reset", action="store_true", help="Reset key to auto-detected default")
    
    # Environment config subcommand
    env_parser = config_subparsers.add_parser("environment", help="Manage environment configuration")
    env_parser.add_argument("key", nargs="?", help="Configuration key to set")
    env_parser.add_argument("value", nargs="?", help="Value to set")
    env_parser.add_argument("--show", action="store_true", help="Show current environment configuration")
    
    # Uninstall subcommand
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall zolo-zcli framework"
    )
    uninstall_group = uninstall_parser.add_mutually_exclusive_group()
    uninstall_group.add_argument(
        "--clean",
        action="store_true",
        help="Remove package AND user data (keep dependencies)"
    )
    uninstall_group.add_argument(
        "--dependencies",
        action="store_true",
        help="Remove only optional dependencies (pandas, psycopg2)"
    )

    args = parser.parse_args()

    # Handle subcommands
    if args.command == "shell":
        from zCLI import zCLI
        cli = zCLI()  # Modern zCLI with zLogger subsystem handles logging
        cli.run_shell()
    
    elif args.command == "config":
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
    
    elif args.command == "uninstall":
        from zCLI.uninstall import uninstall_clean, uninstall_framework_only, uninstall_dependencies
        
        if args.clean:
            return uninstall_clean()
        elif args.dependencies:
            return uninstall_dependencies()
        else:
            # Default: framework-only uninstall
            return uninstall_framework_only()
    
    else:
        # No command specified - default to shell mode
        from zCLI import zCLI
        cli = zCLI()  # Modern zCLI with zLogger subsystem handles logging
        cli.run_shell()


if __name__ == "__main__":
    main()
