# zSys/cli/parser.py
"""Argument parser configuration for zolo CLI."""

import argparse


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Zolo Ecosystem - Declarative framework for Terminal and Web applications",
        prog="zolo",
    )
    
    parser.add_argument("--version", action="version", version=_format_version_string())
    parser.add_argument("--verbose", "-v", action="store_true", 
                      help="Show bootstrap process and detailed initialization")
    parser.add_argument("--dev", action="store_true",
                      help="Enable Development mode (show framework banners and internal flow)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell subcommand
    shell_parser = subparsers.add_parser("shell", help="Start interactive zKernel shell")
    shell_parser.add_argument("--config", help="Path to custom config file (optional)")
    shell_parser.add_argument("--verbose", "-v", action="store_true", 
                             help="Show bootstrap process and detailed initialization")
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Display zMachine and zEnvironment configuration")
    config_parser.add_argument("--verbose", "-v", action="store_true", 
                              help="Show bootstrap process and detailed initialization")
    
    # zTests subcommand
    ztests_parser = subparsers.add_parser("ztests", help="Run zKernel test suite")
    ztests_parser.add_argument("--verbose", "-v", action="store_true", 
                              help="Show bootstrap process and detailed initialization")
    
    # Migrate subcommand
    migrate_parser = subparsers.add_parser("migrate", help="Run schema migrations for an application")
    migrate_parser.add_argument("app_file", help="Path to application file (e.g., zTest.py or app.py)")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Preview migrations without executing")
    migrate_parser.add_argument("--auto-approve", action="store_true", help="Skip confirmation prompts")
    migrate_parser.add_argument("--schema", help="Migrate specific schema only")
    migrate_parser.add_argument("--version", help="Force specific version (e.g., v2.0.0)")
    migrate_parser.add_argument("--history", action="store_true", help="Show migration history")
    migrate_parser.add_argument("--verbose", "-v", action="store_true", 
                               help="Show bootstrap process and detailed initialization")
    
    # Install subcommand
    install_parser = subparsers.add_parser("install", help="Install Zolo ecosystem packages")
    install_parser.add_argument(
        "package", 
        choices=["zKernel", "zLSP", "zTheme", "bifrost"],
        help="Package to install"
    )
    
    # Source selection (mutually exclusive)
    source_group = install_parser.add_mutually_exclusive_group()
    source_group.add_argument("--local", action="store_true",
                             help="Install from local folder (./package)")
    source_group.add_argument("--git", action="store_true",
                             help="Install from GitHub repository")
    install_parser.add_argument(
        "--branch", 
        default="main",
        metavar="VERSION",
        help="Git branch/version to install (e.g., main, v1.5.8, dev). Only with --git"
    )
    
    # Mode selection
    install_parser.add_argument("--editable", "-e", action="store_true",
                               help="Install in editable mode (symlink)")
    
    # Extras (for zKernel)
    install_parser.add_argument("--postgres", action="store_true",
                               help="Include PostgreSQL support")
    install_parser.add_argument("--csv", action="store_true",
                               help="Include CSV support")
    install_parser.add_argument("--all-extras", action="store_true",
                               help="Install all optional features")
    
    install_parser.add_argument("--verbose", "-v", action="store_true",
                               help="Show bootstrap process and detailed initialization")
    
    # Uninstall subcommand
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall zKernel framework")
    uninstall_group = uninstall_parser.add_mutually_exclusive_group()
    uninstall_group.add_argument("--clean", action="store_true", help="Remove package AND user data")
    uninstall_group.add_argument("--dependencies", action="store_true", help="Remove dependencies")
    uninstall_parser.add_argument("--verbose", "-v", action="store_true", 
                                 help="Show bootstrap process and detailed initialization")
    
    return parser


def _get_ecosystem_version():
    """Get version info for all ecosystem packages."""
    versions = {}
    
    # Try to get each package version
    packages = ['zKernel', 'zolo', 'zSys']
    
    for name in packages:
        try:
            if name == 'zKernel':
                # Import zKernel version module
                from zKernel.version import __version__  # pylint: disable=import-outside-toplevel
                versions[name] = __version__
            elif name == 'zolo':
                # Import zolo (LSP) package
                import zolo  # pylint: disable=import-outside-toplevel
                versions[name] = getattr(zolo, '__version__', '1.0.0')
            elif name == 'zSys':
                # Import zSys package
                import zSys  # pylint: disable=import-outside-toplevel
                versions[name] = getattr(zSys, '__version__', '1.0.0')
        except (ImportError, AttributeError):
            versions[name] = 'not installed'
    
    return versions


def _format_version_string():
    """Format ecosystem version string."""
    versions = _get_ecosystem_version()
    lines = ["zolo ecosystem"]
    for name, version in versions.items():
        lines.append(f"  {name}: {version}")
    return "\n".join(lines)
