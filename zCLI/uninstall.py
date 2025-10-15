#!/usr/bin/env python3
# zCLI/uninstall.py — Uninstallation Utilities v1.4.0
# ───────────────────────────────────────────────────────────────

"""
zolo-zcli Uninstallation Utilities

Provides safe uninstallation with options to:
- Remove package only (keep user data)
- Remove package + user data (clean uninstall)

Note: This module operates independently of zCLI subsystems for safety.
"""

import sys
import shutil


def uninstall_package():
    """
    Uninstall the zolo-zcli package using pip.
    
    Returns:
        Boolean indicating success
    """
    import subprocess
    
    print("\n🗑️  Uninstalling zolo-zcli package...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "zolo-zcli", "-y"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Package uninstalled successfully")
            return True
        else:
            print(f"❌ Failed to uninstall package: {result.stderr}")
            return False
            
    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Error during uninstall: {e}")
        return False


def remove_user_data():
    """
    Remove all user data directories.
    
    Removes:
    - User config directory
    - User data directory (includes Data/, Config/, Cache/)
    - User cache directory
    
    Returns:
        Boolean indicating success
    """
    try:
        from zCLI.subsystems.zConfig_modules import ZConfigPaths
    except ImportError:
        print("❌ Cannot import zConfig modules - package may already be uninstalled")
        return False
    
    paths = ZConfigPaths()
    removed_count = 0
    
    print("\n🧹 Removing user data directories...")
    
    # Directories to remove
    dirs_to_remove = [
        ("User Config", paths.user_config_dir),
        ("User Data", paths.user_data_dir),
        ("User Cache", paths.user_cache_dir)
    ]
    
    for name, dir_path in dirs_to_remove:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed {name}: {dir_path}")
                removed_count += 1
            except Exception as e:  # pylint: disable=broad-except
                print(f"  ❌ Failed to remove {name}: {e}")
        else:
            print(f"  ⊘ {name} not found: {dir_path}")
    
    if removed_count > 0:
        print(f"\n✅ Removed {removed_count} user directories")
        return True
    else:
        print("\n⊘ No user directories found to remove")
        return True


def uninstall_clean():
    """
    Complete uninstall: Remove package AND user data.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("\n" + "=" * 70)
    print("zolo-zcli Clean Uninstall")
    print("=" * 70)
    print("\n⚠️  WARNING: This will remove:")
    print("  • zolo-zcli Python package")
    print("  • All user configuration files")
    print("  • All user databases and CSVs")
    print("  • All cached data")
    print("\nThis action CANNOT be undone!")
    
    # Confirm
    response = input("\nType 'yes' to confirm clean uninstall: ").strip().lower()
    
    if response != "yes":
        print("\n❌ Uninstall cancelled")
        return 1
    
    # Remove user data first (before package is gone)
    data_removed = remove_user_data()
    
    # Remove package
    package_removed = uninstall_package()
    
    # Summary
    print("\n" + "=" * 70)
    if package_removed and data_removed:
        print("✅ Clean uninstall complete!")
        print("\nzolo-zcli has been completely removed from your system.")
    else:
        print("⚠️  Uninstall completed with errors")
        print("Some components may still be present on your system.")
    print("=" * 70 + "\n")
    
    return 0 if (package_removed and data_removed) else 1


def uninstall_keep_data():
    """
    Standard uninstall: Remove package but KEEP user data.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    try:
        from zCLI.subsystems.zConfig_modules import ZConfigPaths
    except ImportError:
        print("❌ Cannot import zConfig modules - package may already be uninstalled")
        print("Proceeding with package removal only...")
        return uninstall_package()
    
    paths = ZConfigPaths()
    
    print("\n" + "=" * 70)
    print("zolo-zcli Uninstall (Keep Data)")
    print("=" * 70)
    print("\n📦 This will remove the zolo-zcli package")
    print("✅ Your data will be preserved at:")
    print(f"  • Config: {paths.user_config_dir}")
    print(f"  • Data:   {paths.user_data_dir}")
    print(f"  • Cache:  {paths.user_cache_dir}")
    
    # Confirm
    response = input("\nProceed with uninstall? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Uninstall cancelled")
        return 1
    
    # Remove package only
    package_removed = uninstall_package()
    
    # Summary
    print("\n" + "=" * 70)
    if package_removed:
        print("✅ Package uninstalled successfully!")
        print("\nYour data has been preserved.")
        print("To remove user data, run:")
        print(f"  rm -rf '{paths.user_config_dir}'")
        print(f"  rm -rf '{paths.user_data_dir}'")
        print(f"  rm -rf '{paths.user_cache_dir}'")
    else:
        print("❌ Uninstall failed")
    print("=" * 70 + "\n")
    
    return 0 if package_removed else 1


def main():
    """
    Main uninstall function.
    
    Usage:
        python -m zCLI.uninstall [--clean|--keep-data]
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Uninstall zolo-zcli",
        prog="zolo uninstall"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove package AND all user data (complete removal)"
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Remove package but keep user data (default)"
    )
    
    args = parser.parse_args()
    
    # Default to keep-data if no flag specified
    if args.clean:
        return uninstall_clean()
    else:
        return uninstall_keep_data()


if __name__ == '__main__':
    sys.exit(main())
