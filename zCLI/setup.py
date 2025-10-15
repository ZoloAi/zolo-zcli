#!/usr/bin/env python3
# zCLI/setup.py — Installation and Setup Utilities v1.4.0
# ───────────────────────────────────────────────────────────────

"""
zolo-zcli Setup Utilities

Handles first-run initialization:
- Creates OS-specific config directories
- Generates machine.yaml with auto-detected settings
- Sets up user config directory structure

This runs automatically on first import of zConfig.
Note: This module operates independently of zCLI subsystems for safety.
"""

# Path import removed - not needed in this version


def ensure_config_directories():
    """
    Ensure config directories exist.
    
    Creates:
    - User config directory (~/.zolo-zcli or OS-native)
    - User data directory
    - User cache directory
    
    Note: System directory (/etc/zolo-zcli) requires sudo, not created here.
    
    Returns:
        Boolean indicating success
    """
    try:
        from zCLI.subsystems.zConfig_modules import ZConfigPaths
    except ImportError:
        print("❌ Cannot import zConfig modules - setup may not be available")
        return False
        
    paths = ZConfigPaths()
    
    # Create user config directory
    user_config = paths.user_config_dir
    if not user_config.exists():
        user_config.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created user config directory: {user_config}")
    
    # Create user data directory with zMachine subdirectories
    user_data = paths.user_data_dir
    if not user_data.exists():
        user_data.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created user data directory: {user_data}")
    
    # Create zMachine subdirectories for organized storage
    # Config: User-specific configuration overrides
    # Cache: Temporary data and cache files (cache.csv for load command)
    zmachine_subdirs = ["Config", "Cache"]
    for subdir in zmachine_subdirs:
        subdir_path = user_data / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created zMachine.{subdir}: {subdir_path}")
    
    # Create user cache directory
    user_cache = paths.user_cache_dir
    if not user_cache.exists():
        user_cache.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created user cache directory: {user_cache}")
    
    print("✅ Config directories ensured")
    return True


def print_installation_info():
    """
    Print installation information for user.
    
    Shows:
    - Config directory locations
    - How to customize
    - Next steps
    """
    try:
        from zCLI.subsystems.zConfig_modules import ZConfigPaths
    except ImportError:
        print("❌ Cannot import zConfig modules - installation info not available")
        return
    
    paths = ZConfigPaths()
    
    print("\n" + "=" * 70)
    print("zolo-zcli Installation Complete!")
    print("=" * 70)
    print()
    print("Configuration Directories:")
    print(f"  User Config:  {paths.user_config_dir}")
    print(f"  User Data:    {paths.user_data_dir}")
    print(f"  User Cache:   {paths.user_cache_dir}")
    print()
    print("Machine Configuration:")
    machine_yaml = paths.user_config_dir / "machine.yaml"
    if machine_yaml.exists():
        print(f"  ✓ Created: {machine_yaml}")
        print()
        print("  Customize your tool preferences:")
        print(f"    {paths.user_config_dir / 'machine.yaml'}")
    print()
    print("Next Steps:")
    print("  1. Run: zolo shell")
    print("  2. Customize: Edit machine.yaml to set preferred editor/browser")
    print("  3. Learn: See Documentation/ for guides")
    print("=" * 70)
    print()


def main():
    """
    Main setup function (can be called from CLI).
    
    Usage:
        python -m zCLI.setup
    """
    print("\n🔧 Setting up zolo-zcli...")
    
    # Ensure directories
    if ensure_config_directories():
        print("✅ Config directories created")
    else:
        print("❌ Failed to create config directories")
        return 1
    
    # Print info
    print_installation_info()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

