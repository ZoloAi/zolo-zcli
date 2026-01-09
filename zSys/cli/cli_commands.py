# zSys/cli/cli_commands.py
"""
CLI command handlers for zolo entry point.

This module provides handler functions for all `zolo` CLI commands. These handlers
are called from main.py after argument parsing and bootstrap logger initialization.

Architecture Context
--------------------
**Location**: zSys/cli/ (system-level CLI utilities)
**Purpose**: CLI command orchestration and zCLI initialization
**Layer**: System layer (peer to logger, install, formatting)

This module bridges the gap between the CLI entry point (main.py) and the zCLI
framework. It handles:
- zCLI initialization with appropriate zSpark configurations
- Bootstrap log flushing to framework logger
- Command delegation to subsystems
- Exit code management

Handler Responsibilities
------------------------
Each handler function follows this pattern:
1. Log command initiation (via boot_logger)
2. Initialize zCLI with command-specific zSpark configuration
3. Flush bootstrap logs to framework logger (with optional verbose stdout)
4. Delegate to appropriate zCLI subsystem
5. Return appropriate exit code (if applicable)

Available Handlers
------------------
- display_info(): Show version and installation info (no zCLI init)
- handle_shell_command(): Launch interactive zShell
- handle_config_command(): Display machine/environment config (read-only)
- handle_ztests_command(): Run declarative test suite
- handle_migrate_command(): Execute schema migrations
- handle_uninstall_command(): Interactive uninstall wizard

Usage from main.py
------------------
```python
from cli_commands import handle_shell_command, display_info
# ... argparse setup ...
if args.command == "shell":
    handle_shell_command(boot_logger, zCLI, verbose=args.verbose)
```

Dependencies
------------
- zSys.BootstrapLogger: Pre-boot logging (injected from main.py)
- zCLI: Framework class (injected from main.py)
- pathlib.Path: File path operations (injected from main.py)

See Also
--------
- main.py: CLI entry point and argument parsing
- zSys/logger/bootstrap.py: BootstrapLogger implementation
- zCLI/zCLI.py: Main framework class

Version History
---------------
- v1.5.9.1: Moved back to zSys/cli/ for better organization (consistency with logger, install, etc.)
- v1.5.9: Moved from zSys/ to root level (temporary)
- v1.5.8: Original implementation in zSys/cli_handlers.py
"""

from pathlib import Path
import subprocess
import os


def display_info(boot_logger, zcli_package, get_version, get_package_info, detect_install_type):
    """
    Display zolo-zcli information banner.
    
    Args:
        boot_logger: BootstrapLogger instance
        zcli_package: Imported zCLI package
        get_version: Function to get package version
        get_package_info: Function to get package info dict
        detect_install_type: Function to detect install type
    """
    boot_logger.debug("Displaying info banner")
    
    # Get simple installation type for banner (using portable detection)
    install_type = detect_install_type(zcli_package, detailed=False)
    
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
    boot_logger.flush_to_framework(cli.logger, verbose=verbose)
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
    boot_logger.flush_to_framework(cli.logger, verbose=verbose)
    
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
        boot_logger.flush_to_framework(temp_cli.logger, verbose=verbose)
        temp_cli.display.text(f"Error: zTestRunner directory not found at {test_runner_dir}")
        return 1
    
    boot_logger.debug("zTestRunner directory: %s", test_runner_dir)
    test_cli = zCLI({
        "zSpace": str(test_runner_dir.absolute()),
        "zMode": "Terminal"
    })
    boot_logger.flush_to_framework(test_cli.logger, verbose=verbose)
    
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
        boot_logger.flush_to_framework(temp_z.logger, verbose=verbose)
        temp_z.display.text(f"❌ Error: App file not found: {app_file}")
        return 1
    
    boot_logger.debug("Initializing zCLI for migration...")
    z = zCLI({'zMode': 'Terminal'})
    boot_logger.flush_to_framework(z.logger, verbose=verbose)
    
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
    boot_logger.flush_to_framework(uninstall_cli.logger, verbose=verbose)
    
    uninstall_cli.walker.run()


def handle_script_command(boot_logger, sys, Path, script_path: str, verbose: bool = False):
    """
    Execute a Python script using the current Python interpreter.
    
    This handler runs Python files directly through the zolo CLI, solving
    the "python vs python3" ambiguity by using sys.executable (the same
    interpreter that's running zolo).
    
    Benefits:
        - Consistent UX: `zolo script.py` instead of `python script.py`
        - Solves python/python3 ambiguity (uses same interpreter as zolo)
        - Works with any Python script in any directory
        - Bootstrap logging captures execution context
    
    Args:
        boot_logger: BootstrapLogger instance
        sys: sys module (for sys.executable)
        Path: pathlib.Path class
        script_path: Path to Python script (e.g., "zTest.py")
        verbose: If True, show bootstrap logs on stdout
    
    Returns:
        int: Exit code from script execution (0 = success, non-zero = error)
    
    Examples:
        >>> # From zCloud directory
        >>> zolo zTest.py
        # Executes using sys.executable, runs in script's directory
        
        >>> # With verbose logging
        >>> zolo zTest.py --verbose
        # Shows bootstrap process before execution
        
        >>> # From any directory
        >>> zolo ./scripts/setup.py
        >>> zolo ~/projects/app/initialize.py
    """
    boot_logger.info("Executing Python script: %s", script_path)
    
    # Validate file exists
    script = Path(script_path).resolve()
    if not script.exists():
        boot_logger.error("Script not found: %s", script_path)
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: Script not found: {script_path}\n")
        return 1
    
    # Validate it's a .py file
    if script.suffix != ".py":
        boot_logger.error("Not a Python file: %s (suffix: %s)", script_path, script.suffix)
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: File must be a .py file: {script_path}\n")
        return 1
    
    # Log execution details
    boot_logger.debug("Using interpreter: %s", sys.executable)
    boot_logger.debug("Script directory: %s", script.parent)
    boot_logger.debug("Resolved path: %s", script.absolute())
    
    # Show bootstrap logs if verbose
    if verbose:
        boot_logger.print_buffered_logs()
    
    # Execute using sys.executable (solves python vs python3)
    try:
        result = subprocess.run(
            [sys.executable, str(script.absolute())],
            cwd=str(script.parent),  # Run in script's directory
            env=os.environ.copy()
        )
        
        boot_logger.info("Script exited with code: %s", result.returncode)
        return result.returncode
        
    except Exception as e:
        boot_logger.error("Failed to execute script: %s", str(e))
        print(f"\n❌ Error executing script: {e}\n")
        return 1


def handle_zspark_command(boot_logger, zCLI, Path, zspark_path: str, verbose: bool = False, dev_mode: bool = False):
    """
    Execute a zSpark configuration file (.zolo format).
    
    This handler enables declarative zCLI execution via .zolo files containing
    a zSpark configuration dictionary. Instead of writing Python scripts with
    inline zSpark dicts, applications can use pure declarative .zolo files.
    
    Benefits:
        - Declarative UX: `zolo zCloud` instead of `python zTest.py`
        - Native zolo syntax: Comment blocks, @ paths, zolo-specific features
        - LSP support: Syntax highlighting and validation in editors
        - Clean separation: Config in .zolo, logic in Python modules
    
    Args:
        boot_logger: BootstrapLogger instance
        zCLI: zCLI class
        Path: pathlib.Path class
        zspark_path: Path to zSpark.*.zolo file (e.g., "zSpark.zCloud.zolo")
        verbose: If True, show bootstrap logs on stdout
        dev_mode: If True, override deployment to Development (show banners)
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    
    Examples:
        >>> # From zCloud directory
        >>> zolo zCloud
        # Loads zSpark.zCloud.zolo, extracts zSpark dict, runs zCLI
        
        >>> # With verbose logging
        >>> zolo zCloud --verbose
        # Shows bootstrap process and parsing details
        
        >>> # With development mode (show banners)
        >>> zolo zCloud --dev
        # Forces Development deployment (shows framework flow)
        
        >>> # Full visibility
        >>> zolo zCloud --dev --verbose
        # Development mode + verbose bootstrap logs
    
    File Format:
        zSpark.*.zolo files must contain a root 'zSpark' key with configuration:
        
        ```zolo
        #>
        Comment block (optional)
        <#
        zSpark:
          deployment: Development
          logger: DEBUG
          logger_path: @.logs
          zVaFolder: @.UI.zProducts
          zVaFile: zUI.main
          zBlock: Main_Page
        ```
    """
    boot_logger.info("Executing zSpark configuration: %s", zspark_path)
    
    # Validate file exists
    zspark_file = Path(zspark_path).resolve()
    if not zspark_file.exists():
        boot_logger.error("zSpark file not found: %s", zspark_path)
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: zSpark file not found: {zspark_path}\n")
        return 1
    
    # Validate it's a .zolo file
    if zspark_file.suffix != ".zolo":
        boot_logger.error("Not a .zolo file: %s (suffix: %s)", zspark_path, zspark_file.suffix)
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: File must be a .zolo file: {zspark_path}\n")
        return 1
    
    # Log parsing details
    boot_logger.debug("Parsing .zolo file: %s", zspark_file.absolute())
    boot_logger.debug("Using zolo parser (native @ paths, comment blocks)")
    
    try:
        # Import zolo parser
        import sys
        # Add project root to sys.path so 'zolo' package can be imported
        # __file__ is in zSys/cli/cli_commands.py, so go up 3 levels to get project root
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from zolo.parser import tokenize
        
        # Read and parse the .zolo file
        with open(zspark_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        boot_logger.debug("Tokenizing .zolo content...")
        result = tokenize(content, str(zspark_file))
        
        # Check for parsing errors
        if result.diagnostics:
            boot_logger.error("Parsing errors in zSpark file:")
            for diag in result.diagnostics:
                severity_map = {1: 'ERROR', 2: 'WARNING', 3: 'INFO', 4: 'HINT'}
                severity = severity_map.get(diag.severity, 'UNKNOWN')
                boot_logger.error("  [%s] Line %d:%d - %s", 
                                severity, 
                                diag.range.start.line + 1, 
                                diag.range.start.character,
                                diag.message)
            
            if verbose:
                boot_logger.print_buffered_logs()
            
            print(f"\n❌ Error: Failed to parse zSpark file:\n")
            for diag in result.diagnostics:
                severity_map = {1: 'ERROR', 2: 'WARNING', 3: 'INFO', 4: 'HINT'}
                severity = severity_map.get(diag.severity, 'UNKNOWN')
                print(f"  [{severity}] Line {diag.range.start.line + 1}: {diag.message}")
            print()
            return 1
        
        boot_logger.debug("Parsing successful: %d tokens generated", len(result.tokens))
        
        # Extract zSpark dictionary
        if not isinstance(result.data, dict) or 'zSpark' not in result.data:
            boot_logger.error("Invalid zSpark file: missing 'zSpark' root key")
            if verbose:
                boot_logger.print_buffered_logs()
            print(f"\n❌ Error: Invalid zSpark file format\n")
            print("zSpark.*.zolo files must contain a root 'zSpark' key with configuration dictionary.\n")
            return 1
        
        zspark_config = result.data['zSpark']
        boot_logger.debug("Extracted zSpark configuration: %d keys", len(zspark_config))
        
        # Override deployment if --dev flag is set
        if dev_mode:
            original_deployment = zspark_config.get('deployment', 'N/A')
            zspark_config['deployment'] = 'Development'
            boot_logger.debug("Dev mode: Overriding deployment '%s' → 'Development'", original_deployment)
        
        # Override logger level if --verbose flag is set
        if verbose:
            original_logger = zspark_config.get('logger', 'N/A')
            zspark_config['logger'] = 'DEBUG'
            boot_logger.debug("Verbose mode: Overriding logger '%s' → 'DEBUG'", original_logger)
        
        # Display execution banner
        from zSys.formatting.colors import Colors
        colors = Colors()
        
        print(f"\n{'=' * 60}")
        print(f"  {colors.CONFIG}zSpark Configuration{colors.RESET}")
        print(f"{'=' * 60}")
        print(f"  File:       {zspark_file.name}")
        print(f"  Keys:       {len(zspark_config)}")
        
        # Show deployment (with override indicator)
        deployment = zspark_config.get('deployment', 'Production (default)')
        if dev_mode:
            print(f"  Deployment: {deployment} (--dev override)")
        else:
            print(f"  Deployment: {deployment}")
        
        print(f"  Mode:       {zspark_config.get('zMode', 'N/A')}")
        
        # Show logger (with override indicator)
        if verbose:
            print(f"  Logger:     DEBUG (--verbose override)")
        else:
            logger_level = zspark_config.get('logger', 'INFO (default)')
            print(f"  Logger:     {logger_level}")
        
        print(f"{'=' * 60}\n")
        
        # Show bootstrap logs if verbose (before zCLI init)
        if verbose:
            boot_logger.print_buffered_logs()
        
        # Initialize zCLI with parsed zSpark configuration
        boot_logger.info("Initializing zCLI with zSpark configuration...")
        zcli = zCLI(zspark_config)
        
        # Flush remaining bootstrap logs with semantic routing
        if hasattr(zcli, 'logger'):
            boot_logger.flush_to_framework(zcli.logger, verbose=False)
        
        # Run zCLI application
        boot_logger.info("Running zCLI application...")
        zcli.run()
        
        return 0
        
    except KeyError as e:
        boot_logger.error("Missing required key in zSpark: %s", str(e))
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: Missing required key in zSpark configuration: {e}\n")
        return 1
    
    except Exception as e:
        boot_logger.error("Failed to execute zSpark file: %s", str(e))
        if verbose:
            boot_logger.print_buffered_logs()
        print(f"\n❌ Error: Failed to execute zSpark file:\n{e}\n")
        import traceback
        traceback.print_exc()
        return 1

