"""CLI entry point for the zolo-zcli package."""

import argparse

from zCLI.utils.logger import logger
from zCLI.version import get_version
from zCLI.zCore.zCLI import zCLI


def main() -> None:
    """Main entry point for the ``zolo-zcli`` command."""

    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo-zcli",
    )
    parser.add_argument("--shell", action="store_true", help="Start zCLI shell mode")
    parser.add_argument(
        "--version",
        action="version",
        version=f"zolo-zcli {get_version()}",
    )

    args = parser.parse_args()

    if args.shell:
        logger.info("Starting zCLI Shell mode...")
        cli = zCLI()
        cli.run_shell()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
