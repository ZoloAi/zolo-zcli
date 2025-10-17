# zCLI/subsystems/zConfig/zConfig_modules/helpers/config_helpers.py
"""Shared helper functions for configuration loading across zConfig subsystems."""

from zCLI import yaml, Colors

def load_config_with_override(paths, yaml_key, create_func, data_dict, subsystem_name):
    """Load config file, creating if missing, and override data_dict with contents."""
    # Derive filename from subsystem name
    if subsystem_name == "MachineConfig":
        filename = "zConfig.machine.yaml"
    elif subsystem_name == "EnvironmentConfig":
        filename = "zConfig.zEnvironment.yaml"
    else:
        filename = f"zConfig.{subsystem_name.lower().replace('config', '')}.yaml"
    user_config_path = paths.user_zconfigs_dir / filename

    if user_config_path.exists():
        # Load existing config
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, "user")
    else:
        # Create user config on first run
        create_func(user_config_path, data_dict)
        # Load the newly created config
        _load_and_override(user_config_path, yaml_key, data_dict, subsystem_name, "user")

def _load_and_override(path, yaml_key, data_dict, subsystem_name, source):
    """Load config file and override data_dict with its contents."""
    try:
        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if data and yaml_key in data:
                data_dict.update(data[yaml_key])
                print(f"{Colors.CONFIG}[{subsystem_name}] Overriding with {source} settings "
                      f"from: {path}{Colors.RESET}")

    except Exception as e:
        print(f"[{subsystem_name}] Failed to load {source} config: {e}")
