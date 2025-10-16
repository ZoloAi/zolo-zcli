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
    Clean uninstall: Remove package AND system files (but keep dependencies).
    
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
    print("\n✅ This will KEEP:")
    print("  • Optional dependencies (pandas, psycopg2)")
    print("  • Other Python packages")
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
        print("Optional dependencies (pandas, psycopg2) were preserved.")
    else:
        print("⚠️  Uninstall completed with errors")
        print("Some components may still be present on your system.")
    print("=" * 70 + "\n")
    
    return 0 if (package_removed and data_removed) else 1


def uninstall_framework_only():
    """
    Framework-only uninstall: Remove package but KEEP user data and dependencies.
    
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
    print("zolo-zcli Framework Uninstall")
    print("=" * 70)
    print("\n📦 This will remove the zolo-zcli framework package")
    print("\n✅ This will KEEP:")
    print("  • User configuration files")
    print("  • User databases and CSVs")
    print("  • Cached data")
    print("  • Optional dependencies (pandas, psycopg2)")
    print("\nYour data will be preserved at:")
    print(f"  • Config: {paths.user_config_dir}")
    print(f"  • Data:   {paths.user_data_dir}")
    print(f"  • Cache:  {paths.user_cache_dir}")
    
    # Confirm
    response = input("\nProceed with framework uninstall? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Uninstall cancelled")
        return 1
    
    # Remove package only
    package_removed = uninstall_package()
    
    # Summary
    print("\n" + "=" * 70)
    if package_removed:
        print("✅ Framework uninstalled successfully!")
        print("\nYour data and dependencies have been preserved.")
        print("To remove user data, run: zolo uninstall --clean")
        print("To remove dependencies, run: zolo uninstall --dependencies")
    else:
        print("❌ Uninstall failed")
    print("=" * 70 + "\n")
    
    return 0 if package_removed else 1


def uninstall_dependencies():
    """
    Dependencies uninstall: Remove only zCLI-specific optional dependencies.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("\n" + "=" * 70)
    print("zolo-zcli Dependencies Uninstall")
    print("=" * 70)
    print("\n⚠️  WARNING: This will remove:")
    print("  • pandas (CSV backend support)")
    print("  • psycopg2-binary (PostgreSQL backend support)")
    print("\n✅ This will KEEP:")
    print("  • zolo-zcli framework package")
    print("  • User configuration and data")
    print("  • Other Python packages")
    print("\n⚠️  WARNING: This may break other applications that use these packages!")
    
    # Confirm
    response = input("\nType 'yes' to confirm dependency removal: ").strip().lower()
    
    if response != "yes":
        print("\n❌ Uninstall cancelled")
        return 1
    
    # Remove optional dependencies
    import subprocess
    
    dependencies_to_remove = ["pandas", "psycopg2-binary"]
    removed_count = 0
    
    print("\n🗑️  Removing optional dependencies...")
    
    for dep in dependencies_to_remove:
        try:
            print(f"\n📦 Removing {dep}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", dep, "-y"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"  ✅ {dep} removed successfully")
                removed_count += 1
            else:
                print(f"  ⊘ {dep} not installed or already removed")
                
        except Exception as e:
            print(f"  ❌ Failed to remove {dep}: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    if removed_count > 0:
        print(f"✅ Removed {removed_count} optional dependencies!")
        print("\nzCLI CSV and PostgreSQL backends will no longer work.")
        print("To reinstall: pip install zolo-zcli[csv postgresql]")
    else:
        print("⊘ No optional dependencies were removed.")
        print("They may not be installed or may be used by other packages.")
    print("=" * 70 + "\n")
    
    return 0


def main():
    """
    Main uninstall function.
    
    Usage:
        python -m zCLI.uninstall [--clean|--dependencies]
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Uninstall zolo-zcli framework",
        prog="zolo uninstall"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove package AND user data (but keep dependencies)"
    )
    parser.add_argument(
        "--dependencies",
        action="store_true",
        help="Remove only optional dependencies (pandas, psycopg2)"
    )
    
    args = parser.parse_args()
    
    # Route to appropriate uninstall mode
    if args.clean:
        return uninstall_clean()
    elif args.dependencies:
        return uninstall_dependencies()
    else:
        # Default: framework-only uninstall
        return uninstall_framework_only()


if __name__ == '__main__':
    sys.exit(main())
