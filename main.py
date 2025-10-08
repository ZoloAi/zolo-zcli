"""CLI entry point for the zolo-zcli package."""

import argparse

from logger import Logger, set_log_level
from zCLI.version import get_version


def main() -> None:
    """Main entry point for the ``zolo-zcli`` command."""

    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo",
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell command (default if no subcommand)
    parser.add_argument("--shell", action="store_true", help="Start zCLI shell mode")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set log level (default: INFO)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"zolo-zcli {get_version()}",
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

    # Initialize logging first so it applies to main and everything that follows
    set_log_level(args.log_level)

    # Get logger instance for main
    main_logger = Logger.get_logger("main")

    # Handle subcommands
    if args.command == "uninstall":
        from zCLI.uninstall import uninstall_clean, uninstall_keep_data
        
        if args.clean:
            return uninstall_clean()
        else:
            # Default to keep-data
            return uninstall_keep_data()
    
    # Default behavior: shell mode
    if args.shell:
        main_logger.info("Starting zCLI Shell mode...")
        from zCLI import zCLI  # Import after logging init
        cli = zCLI()
        cli.run_shell()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
