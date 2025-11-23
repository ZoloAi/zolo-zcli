# zCLI/subsystems/zConfig/zConfig_modules/helpers/config_helpers.py
"""Shared helper functions for configuration loading across zConfig subsystems."""

from zCLI import yaml, Path, Dict, Any, Callable, Optional
import shutil

# Module constants
SOURCE_USER = "user"
LOG_PREFIX = "[ConfigHelpers]"
ZUI_CLI_SYS_FILENAME = "zUI.zcli_sys.yaml"

def ensure_user_directories(paths: Any) -> None:
    """
    Ensure user configuration directories exist (zConfigs, zUIs).
    
    Creates user_config_dir/zConfigs/ and user_config_dir/zUIs/ directories
    if they don't already exist. These directories are essential for:
    - zConfigs: Configuration files (zConfig.machine.yaml, zConfig.environment.yaml)
    - zUIs: User-customized UI definition files
    
    Args:
        paths: zConfigPaths instance
        
    Notes:
        - Called during zConfig initialization
        - Uses exist_ok=True for safe repeated calls
        - Silently handles errors (non-critical operation)
    """
    try:
        # Ensure zConfigs directory exists
        paths.user_zconfigs_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure zUIs directory exists
        paths.user_zuis_dir.mkdir(parents=True, exist_ok=True)
        
    except Exception as e:
        print(f"{LOG_PREFIX} Warning: Failed to create user directories: {e}")

def initialize_system_ui(paths: Any) -> None:
    """
    Copy system UI file (zUI.zcli_sys.yaml) from package to user zUIs directory.
    
    Copies the system UI file containing help menus, traceback UI, and uninstall
    walker definitions on first run. This ensures system UI features work from any
    directory. Users can customize this file after initial copy.
    
    Args:
        paths: zConfigPaths instance
        
    Notes:
        - Only copies if file doesn't exist (preserves user customizations)
        - Source: zCLI/UI/zUI.zcli_sys.yaml (from installed package)
        - Target: user_zuis_dir/zUI.zcli_sys.yaml
        - Non-critical operation (silently handles errors)
    """
    try:
        target_file = paths.user_zuis_dir / ZUI_CLI_SYS_FILENAME
        
        # Skip if file already exists (user may have customized)
        if target_file.exists():
            return
        
        # Get source file from package (zCLI/UI/)
        import zCLI
        zcli_package_dir = Path(zCLI.__file__).parent
        source_file = zcli_package_dir / "UI" / ZUI_CLI_SYS_FILENAME
        
        # Copy file if source exists
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"{LOG_PREFIX} Initialized system UI: {ZUI_CLI_SYS_FILENAME}")
            print(f"{LOG_PREFIX} Location: {target_file}")
        else:
            print(f"{LOG_PREFIX} Warning: Source UI file not found: {source_file}")
            
    except Exception as e:
        print(f"{LOG_PREFIX} Warning: Failed to initialize system UI: {e}")

def load_config_with_override(
    paths: Any,  # zConfigPaths (avoid circular import)
    yaml_key: str,
    create_func: Callable[[Path, Dict[str, Any]], None],
    data_dict: Dict[str, Any],
    filename: str,
    subsystem_name: str,
    log_level: Optional[str] = None
) -> None:
    """Load config file from user directory, creating with defaults if missing."""
    user_config_path = paths.user_zconfigs_dir / filename

    if user_config_path.exists():
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, SOURCE_USER, log_level)
    else:
        create_func(user_config_path, data_dict)
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, SOURCE_USER, log_level)

def _load_and_override(
    path: Path,
    yaml_key: str,
    data_dict: Dict[str, Any],
    subsystem_name: str,
    source: str,
    log_level: Optional[str] = None
) -> None:
    """Load YAML config file and merge its contents into data_dict (log-level aware)."""
    from zCLI.utils import print_if_not_prod
    
    try:
        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if data and yaml_key in data:
                data_dict.update(data[yaml_key])
                print_if_not_prod(f"[{subsystem_name}] Overriding with {source} settings from: {path}", log_level)

    except Exception as e:
        print_if_not_prod(f"[{subsystem_name}] Failed to load {source} config: {e}", log_level)
