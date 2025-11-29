#!/usr/bin/env python3
"""Level 2: Smart Defaults - Deployment Affects Logger

Discover how deployment mode automatically sets smart logger defaults.
Experience the relationship between deployment and logging through action!

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/2_smart_defaults.py

Key Discovery:
    Deployment modes control both banners AND logger defaults:
    - Development → Full output (banners + INFO logs)
    - Testing → Clean logs only (no banners + INFO logs)
    - Production → Minimal (no banners + ERROR logs only)
    
    But they're INDEPENDENT - you can override either one!
"""

from zCLI import zCLI


def demo_with_deployment(mode):
    """Run the same code with different deployment modes."""
    print(f"\n{'='*60}")
    print(f"  DEPLOYMENT MODE: {mode}")
    print(f"{'='*60}")
    
    zSpark = {"deployment": mode}  # Development, Testing, Production
    z = zCLI(zSpark)
    
    print(f"\n📊 Configuration:")
    print(f"   Deployment : {z.config.get_environment('deployment')}")
    print(f"   Logger     : {z.session.get('zLogger')} (auto-default)")
    print(f"   Production?: {z.config.is_production()}")
    
    print(f"\n📝 Logger output:")
    z.logger.debug("DEBUG: Detailed diagnostic information")
    z.logger.info("INFO: Application status update")
    z.logger.warning("WARNING: Something needs attention")
    z.logger.error("ERROR: Something failed")
    
    print()


def run_demo():
    print("\n" + "="*60)
    print("  COMPARING DEPLOYMENT MODES")
    print("="*60)
    print("\nWatch how the same logger calls produce different output")
    print("based on deployment mode!")
    
    # Demo 1: Development mode (verbose)
    demo_with_deployment("Development")
    
    # Demo 2: Production mode (minimal)
    demo_with_deployment("Production")
    
    print("="*60)
    print("\n💡 What you discovered:")
    print("   • Development → INFO logging (shows info, warning, error)")
    print("   • Production → ERROR logging (shows only errors)")
    print("   • Same code, different behavior based on deployment!")
    print("\n💡 Key insight:")
    print("   Deployment and logger are SEPARATE concerns:")
    print("   • Deployment = WHAT environment (behavior)")
    print("   • Logger = HOW MUCH logging (verbosity)")
    print("\n🔧 Next step:")
    print("   Learn to OVERRIDE these smart defaults when needed!")
    print("   (See 3_logger_override.py)\n")


if __name__ == "__main__":
    run_demo()

