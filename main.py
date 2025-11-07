"""CLI entry point for the zolo-zcli package."""

import argparse
from zCLI.version import get_version

def handle_shell_command():
    """Handle shell command."""
    from zCLI import zCLI
    cli = zCLI()
    cli.run_shell()


def shell_main() -> None:
    """Direct entry point for zShell command (simplified UX)."""
    from zCLI import zCLI
    cli = zCLI()
    cli.run_shell()


def handle_config_command(args):
    """Handle config command."""
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


def handle_test_command():
    """Handle test command (legacy)."""
    from zTestSuite.run_all_tests import show_test_menu, run_selected_tests
    choice = show_test_menu()
    if choice is None:
        return 1
    success = run_selected_tests(choice)
    return 0 if success else 1


def handle_ztests_command():
    """Handle zTests command (declarative test runner)."""
    from pathlib import Path
    import os
    
    # Get zTestRunner folder using __file__ to ensure we get the right location
    main_file = Path(__file__).resolve()
    project_root = main_file.parent
    test_runner_dir = project_root / "zTestRunner"
    
    # Verify directory exists
    if not test_runner_dir.exists():
        print(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
    # Import zCLI after setting up paths
    from zCLI import zCLI
    
    # Launch declarative test runner following shell_cmd_help pattern
    test_cli = zCLI({
        "zSpace": str(test_runner_dir.absolute()),
        "zMode": "Terminal"
    })
    
    # Set walker configuration in zspark_obj (like shell_cmd_help does)
    test_cli.zspark_obj["zVaFile"] = "@.zUI.test_menu"
    test_cli.zspark_obj["zBlock"] = "zVaF"
    
    # Launch walker
    test_cli.walker.run()


def handle_uninstall_command():
    """Handle uninstall command with interactive menu."""
    from pathlib import Path
    from zCLI import zCLI
    
    # Get zCLI package installation directory
    import zCLI as zcli_module
    zcli_package_dir = Path(zcli_module.__file__).parent
    
    uninstall_cli = zCLI({
        "zWorkspace": str(zcli_package_dir),
        "zVaFile": "@.UI.zUI.zcli_sys",
        "zBlock": "Uninstall"
    })
    uninstall_cli.walker.run()


def main() -> None:
    """Main entry point for the zolo-zcli command."""
    parser = argparse.ArgumentParser(
        description="Zolo zCLI Framework - YAML-driven CLI for interactive applications",
        prog="zolo",
    )
    
    parser.add_argument("--version", action="version", version=f"zolo-zcli {get_version()}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Shell subcommand
    shell_parser = subparsers.add_parser("shell", help="Start interactive zCLI shell")
    shell_parser.add_argument("--config", help="Path to custom config file (optional)")
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage zCLI configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_type")
    machine_parser = config_subparsers.add_parser("machine", help="Manage machine configuration")
    machine_parser.add_argument("key", nargs="?", help="Configuration key")
    machine_parser.add_argument("value", nargs="?", help="Value to set")
    machine_parser.add_argument("--show", action="store_true", help="Show configuration")
    machine_parser.add_argument("--reset", action="store_true", help="Reset to default")
    env_parser = config_subparsers.add_parser("environment", help="Manage environment configuration")
    env_parser.add_argument("key", nargs="?", help="Configuration key")
    env_parser.add_argument("value", nargs="?", help="Value to set")
    env_parser.add_argument("--show", action="store_true", help="Show configuration")
    
    # Test subcommand (legacy)
    subparsers.add_parser("test", help="Run zCLI test suite (legacy)")
    
    # zTests subcommand (declarative)
    subparsers.add_parser("ztests", help="Run zCLI test suite (declarative)")
    
    # Uninstall subcommand
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall zolo-zcli framework")
    uninstall_group = uninstall_parser.add_mutually_exclusive_group()
    uninstall_group.add_argument("--clean", action="store_true", help="Remove package AND user data")
    uninstall_group.add_argument("--dependencies", action="store_true", help="Remove dependencies")

    args = parser.parse_args()

    # Route to handlers
    if args.command == "shell":
        handle_shell_command()
    elif args.command == "config":
        handle_config_command(args)
    elif args.command == "test":
        return handle_test_command()
    elif args.command == "ztests":
        return handle_ztests_command()
    elif args.command == "uninstall":
        return handle_uninstall_command()
    else:
        handle_shell_command()


if __name__ == "__main__":
    main()
