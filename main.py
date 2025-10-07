"""CLI entry point for the zolo-zcli package."""

import argparse

from logger import logger, set_log_level
from zCLI.version import get_version


def main() -> None:
    """Main entry point for the ``zolo-zcli`` command."""

    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo",
    )
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

    args = parser.parse_args()

    # Initialize logging first so it applies to main and everything that follows
    set_log_level(args.log_level)

    if args.shell:
        logger.info("Starting zCLI Shell mode...")
        from zCLI.zCore.zCLI import zCLI  # Import after logging init
        cli = zCLI()
        cli.run_shell()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
