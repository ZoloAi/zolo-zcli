# zSys/cli_handlers.py
"""
CLI command handlers (Layer 0 - System Foundation).

Provides handler functions for all zolo CLI commands. These handlers are called
from main.py after argument parsing and bootstrap logger initialization.

Each handler is responsible for:
- Initializing zCLI with appropriate zSpark configuration
- Flushing bootstrap logs to framework logger
- Executing the command logic (delegation to subsystems)
- Returning appropriate exit codes
"""

from pathlib import Path


def display_info(boot_logger, zcli_package, get_version, get_package_info, detect_installation_type):
    """
    Display zolo-zcli information banner.
    
    Args:
        boot_logger: BootstrapLogger instance
        zcli_package: Imported zCLI package
        get_version: Function to get package version
        get_package_info: Function to get package info dict
        detect_installation_type: Function to detect install type
    """
    boot_logger.debug("Displaying info banner")
    
    # Get simple installation type for banner (using portable detection)
    install_type = detect_installation_type(zcli_package, detailed=False)
    
    pkg_info = get_package_info()
    
    print(f"\n{pkg_info['name']} {get_version()} ({install_type})")
    print("A declarative based Framework")
    print(f"By {pkg_info['author']}")
    print("License: MIT\n")


def handle_shell_command(boot_logger, zCLI, verbose: bool = False):
    """
    Handle shell command.
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        verbose: If True, show bootstrap logs on stdout
    """
    boot_logger.info("Launching zShell...")
    cli = zCLI()
    boot_logger.flush_to_framework(cli.logger.framework, verbose=verbose)
    cli.run_shell()


def handle_config_command(boot_logger, zCLI, verbose: bool = False):
    """
    Handle config command - display only (read-only).
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        verbose: If True, show bootstrap logs on stdout
    """
    boot_logger.info("Loading config display...")
    cli = zCLI({'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'})
    boot_logger.flush_to_framework(cli.logger.framework, verbose=verbose)
    
    cli.config.persistence.show_machine_config()
    cli.config.persistence.show_environment_config()


def handle_ztests_command(boot_logger, zCLI, Path, zcli_package, verbose: bool = False):
    """
    Handle zTests command (declarative test runner).
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        Path: pathlib.Path class
        zcli_package: Imported zCLI package (for __file__ access)
        verbose: If True, show bootstrap logs on stdout
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    boot_logger.info("Launching zTestRunner...")
    
    # Resolve test runner directory relative to main.py location
    # Note: This assumes main.py is in project root
    try:
        import __main__
        main_file = Path(__main__.__file__).resolve()
        project_root = main_file.parent
        test_runner_dir = project_root / "zTestRunner"
    except Exception:
        # Fallback: use zCLI package location
        zcli_path = Path(zcli_package.__file__).resolve()
        project_root = zcli_path.parent.parent
        test_runner_dir = project_root / "zTestRunner"
    
    if not test_runner_dir.exists():
        boot_logger.error("zTestRunner directory not found: %s", test_runner_dir)
        temp_cli = zCLI({'zMode': 'Terminal'})
        boot_logger.flush_to_framework(temp_cli.logger.framework, verbose=verbose)
        temp_cli.display.text(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
    boot_logger.debug("zTestRunner directory: %s", test_runner_dir)
    test_cli = zCLI({
        "zSpace": str(test_runner_dir.absolute()),
        "zMode": "Terminal"
    })
    boot_logger.flush_to_framework(test_cli.logger.framework, verbose=verbose)
    
    test_cli.zspark_obj["zVaFile"] = "@.zUI.test_menu"
    test_cli.zspark_obj["zBlock"] = "zVaF"
    test_cli.walker.run()
    return 0


def handle_migrate_command(boot_logger, zCLI, Path, args, verbose: bool = False):
    """
    Handle schema migration command - thin CLI wrapper.
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        Path: pathlib.Path class
        args: Parsed arguments from argparse
        verbose: If True, show bootstrap logs on stdout
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    boot_logger.info("Preparing migration: %s", args.app_file)
    
    app_file = args.app_file
    if not Path(app_file).exists():
        boot_logger.error("App file not found: %s", app_file)
        temp_z = zCLI({'zMode': 'Terminal', 'logger': 'PROD', 'deployment': 'Production'})
        boot_logger.flush_to_framework(temp_z.logger.framework, verbose=verbose)
        temp_z.display.text(f"❌ Error: App file not found: {app_file}")
        return 1
    
    boot_logger.debug("Initializing zCLI for migration...")
    z = zCLI({'zMode': 'Terminal'})
    boot_logger.flush_to_framework(z.logger.framework, verbose=verbose)
    
    return z.data.cli_migrate(
        app_file=str(Path(app_file).resolve()),
        auto_approve=getattr(args, 'auto_approve', False),
        dry_run=getattr(args, 'dry_run', False),
        specific_schema=getattr(args, 'schema', None),
        force_version=getattr(args, 'version', None)
    )


def handle_uninstall_command(boot_logger, zCLI, Path, zcli_package, verbose: bool = False):
    """
    Handle uninstall command with interactive menu.
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        Path: pathlib.Path class
        zcli_package: Imported zCLI package (for __file__ access)
        verbose: If True, show bootstrap logs on stdout
    """
    boot_logger.info("Launching uninstall wizard...")
    
    zcli_package_dir = Path(zcli_package.__file__).parent
    boot_logger.debug("zCLI package directory: %s", zcli_package_dir)
    
    uninstall_cli = zCLI({
        "zWorkspace": str(zcli_package_dir),
        "zVaFile": "@.UI.zUI.zcli_sys",
        "zBlock": "Uninstall"
    })
    boot_logger.flush_to_framework(uninstall_cli.logger.framework, verbose=verbose)
    
    uninstall_cli.walker.run()

