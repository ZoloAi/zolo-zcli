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
    
    # Uninstall subcommand
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall zolo-zcli"
    )
    uninstall_group = uninstall_parser.add_mutually_exclusive_group()
    uninstall_group.add_argument(
        "--clean",
        action="store_true",
        help="Remove package AND all user data (complete removal)"
    )
    uninstall_group.add_argument(
        "--keep-data",
        action="store_true",
        help="Remove package but keep user data (default)"
    )

    args = parser.parse_args()

    # Handle subcommands
    if args.command == "shell":
        from zCLI import zCLI
        cli = zCLI()  # Modern zCLI with zLogger subsystem handles logging
        cli.run_shell()
    
    elif args.command == "uninstall":
        from zCLI.uninstall import uninstall_clean, uninstall_keep_data
        
        if args.clean:
            return uninstall_clean()
        else:
            # Default to keep-data
            return uninstall_keep_data()
    
    else:
        # No command specified - default to shell mode
        from zCLI import zCLI
        cli = zCLI()  # Modern zCLI with zLogger subsystem handles logging
        cli.run_shell()


if __name__ == "__main__":
    main()
