# zCLI/subsystems/zConfig/zConfig_modules/helpers/config_helpers.py
"""Shared helper functions for configuration loading across zConfig subsystems."""

from zCLI import yaml, Path, Dict, Any, Callable

# Module constants
SOURCE_USER = "user"

def load_config_with_override(
    paths: Any,  # zConfigPaths (avoid circular import)
    yaml_key: str,
    create_func: Callable[[Path, Dict[str, Any]], None],
    data_dict: Dict[str, Any],
    filename: str,
    subsystem_name: str
) -> None:
    """Load config file from user directory, creating with defaults if missing."""
    user_config_path = paths.user_zconfigs_dir / filename

    if user_config_path.exists():
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, SOURCE_USER)
    else:
        create_func(user_config_path, data_dict)
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, SOURCE_USER)

def _load_and_override(
    path: Path,
    yaml_key: str,
    data_dict: Dict[str, Any],
    subsystem_name: str,
    source: str
) -> None:
    """Load YAML config file and merge its contents into data_dict."""
    try:
        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if data and yaml_key in data:
                data_dict.update(data[yaml_key])
                print(f"[{subsystem_name}] Overriding with {source} settings from: {path}")

    except Exception as e:
        print(f"[{subsystem_name}] Failed to load {source} config: {e}")
