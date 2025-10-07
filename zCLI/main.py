# zCLI/main.py — Main Entry Point for zCLI Core
# ───────────────────────────────────────────────────────────────

import argparse

from zCLI.zCore.zCLI import zCLI
from zCLI.version import get_version, get_package_info
from zCLI.utils.logger import logger

def main():
    """Main entry point for zolo-zcli command."""

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
        logger.info("Starting zCLI Shell mode...")
        cli = zCLI()
        cli.run_shell()
    else:
        # Default: show help
        parser.print_help()

if __name__ == "__main__":
    main()
