#!/usr/bin/env python3
# zCLI/utils/uninstall.py

"""zCLI uninstall utilities - Walker UI only, no backward compatibility."""

from zCLI import sys, shutil, subprocess

# Constants
PACKAGE_NAME = "zolo-zcli"
OPTIONAL_DEPENDENCIES = ["pandas", "psycopg2-binary"]
CONFIRMATION_PROMPT = "\nType 'yes' to confirm: "
CONFIRMATION_VALUE = "yes"


def confirm_action(display, action_description: str = None) -> bool:  # pylint: disable=unused-argument
    """Helper to get user confirmation for destructive actions.
    
    Args:
        display: zDisplay instance for user interaction
        action_description: Description of the action (reserved for future logging)
    
    Returns:
        True if user confirms, False otherwise
    """
    response = display.read_string(CONFIRMATION_PROMPT).strip().lower()
    if response != CONFIRMATION_VALUE:
        display.error("Cancelled", indent=1)
        return False
    return True


def uninstall_package(zcli) -> bool:
    """Uninstall zolo-zcli package via pip.
    
    Args:
        zcli: zCLI instance
    
    Returns:
        True if successful, False otherwise
    """
    display = zcli.display
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", PACKAGE_NAME, "-y"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            display.success("Package removed", indent=1)
            return True
        
        display.error(f"Package removal failed: {result.stderr}", indent=1)
        return False
            
    except Exception as e:  # pylint: disable=broad-except
        display.error(f"Package removal error: {e}", indent=1)
        return False


def remove_user_data(zcli) -> bool:
    """Remove all user data directories (config, data, cache).
    
    Args:
        zcli: zCLI instance
    
    Returns:
        True if at least one directory was removed, False if all failed
    """
    display = zcli.display
    paths = zcli.config.sys_paths
    removed_count = 0
    failed_count = 0
    
    dirs_to_remove = [
        ("Config", paths.user_config_dir),
        ("Data", paths.user_data_dir),
        ("Cache", paths.user_cache_dir)
    ]
    
    for name, dir_path in dirs_to_remove:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                removed_count += 1
            except Exception as e:  # pylint: disable=broad-except
                display.error(f"{name} removal failed: {e}", indent=1)
                failed_count += 1
    
    if removed_count > 0:
        display.success(f"User data removed ({removed_count} directories)", indent=1)
    
    # Return True if we removed at least one directory successfully
    return removed_count > 0


def remove_dependencies(zcli) -> bool:
    """Remove zCLI optional dependencies (pandas, psycopg2).
    
    Args:
        zcli: zCLI instance
    
    Returns:
        True if at least one dependency was removed, False if all failed
    """
    display = zcli.display
    removed_count = 0
    
    for dep in OPTIONAL_DEPENDENCIES:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", dep, "-y"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                removed_count += 1
                
        except Exception as e:  # pylint: disable=broad-except
            display.error(f"{dep} removal failed: {e}", indent=1)
    
    if removed_count > 0:
        display.success(f"Dependencies removed ({removed_count} packages)", indent=1)
    
    # Return True if we removed at least one dependency successfully
    return removed_count > 0


def uninstall_clean(zcli):
    """Clean uninstall: Remove EVERYTHING (package + data + dependencies).
    
    Args:
        zcli: zCLI instance
    
    Returns:
        0 if successful, 1 if failed (caller should handle sys.exit)
    """
    display = zcli.display
    
    display.zDeclare("Clean Uninstall", color="MAIN", indent=0, style="full")
    display.warning("Removes EVERYTHING - package, data, dependencies", indent=1)
    
    if not confirm_action(display, "clean uninstall"):
        return 1
    
    # Remove in order: data -> dependencies -> package
    data_removed = remove_user_data(zcli)
    deps_removed = remove_dependencies(zcli)
    package_removed = uninstall_package(zcli)
    
    display.zDeclare("", color="MAIN", indent=0, style="full")
    
    if package_removed and data_removed and deps_removed:
        display.success("Complete removal successful", indent=1)
        sys.exit(0)
    
    display.warning("Completed with errors", indent=1)
    sys.exit(1)


def uninstall_framework_only(zcli):
    """Framework-only uninstall: Remove package, keep data + dependencies.
    
    Args:
        zcli: zCLI instance
    
    Returns:
        0 if successful, 1 if failed (caller should handle sys.exit)
    """
    display = zcli.display
    paths = zcli.config.sys_paths
    
    display.zDeclare("Framework Only", color="MAIN", indent=0, style="full")
    display.info("Removes package only - preserves data and dependencies", indent=1)
    
    display.list([
        f"Config: {paths.user_config_dir}",
        f"Data:   {paths.user_data_dir}",
        f"Cache:  {paths.user_cache_dir}"
    ], style="bullet", indent=2)
    
    if not confirm_action(display, "framework-only uninstall"):
        return 1
    
    package_removed = uninstall_package(zcli)
    
    display.zDeclare("", color="MAIN", indent=0, style="full")
    
    if package_removed:
        display.success("Framework removed - data preserved", indent=1)
        sys.exit(0)
    
    display.error("Removal failed", indent=1)
    sys.exit(1)


def uninstall_dependencies(zcli):
    """Dependencies-only uninstall: Remove optional dependencies only.
    
    Args:
        zcli: zCLI instance
    
    Returns:
        0 (always successful, caller should handle sys.exit)
    """
    display = zcli.display
    
    display.zDeclare("Dependencies Only", color="MAIN", indent=0, style="full")
    display.warning("Removes pandas and psycopg2 - may affect other apps", indent=1)
    
    if not confirm_action(display, "dependencies-only uninstall"):
        return 1
    
    deps_removed = remove_dependencies(zcli)
    
    display.zDeclare("", color="MAIN", indent=0, style="full")
    
    if deps_removed:
        display.success("Dependencies removed", indent=1)
        display.info("Reinstall: pip install 'zolo-zcli[csv,postgresql]'", indent=1)
    
    sys.exit(0)
