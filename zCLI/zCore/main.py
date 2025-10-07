# zCLI/zCore/main.py — Main Entry Point for zCLI Core
# ───────────────────────────────────────────────────────────────

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from zCLI.version import get_version
from zCLI.utils.logger import get_logger, init_logging


def main():
    """Main entry point for zolo-zcli command."""

    init_logging()
    main_logger = get_logger(__name__)

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Zolo zCLI Framework - YAML-driven CLI for interactive applications',
        prog='zolo-zcli'
    )
    parser.add_argument('--shell', action='store_true',
                       help='Start zCLI shell mode')
    parser.add_argument('--version', action='version',
                       version=f'zolo-zcli {get_version()}')

    # Parse arguments
    args = parser.parse_args()

    if args.shell:
        # Shell mode - start shell
        main_logger.info("Starting zCLI Shell mode...")
        from zCLI.zCore.zCLI import zCLI

        cli_logger = get_logger("zCLI")
        cli = zCLI(logger=cli_logger)
        cli.run_shell()
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
