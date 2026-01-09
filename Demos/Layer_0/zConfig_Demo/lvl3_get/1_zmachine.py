#!/usr/bin/env python3
"""Level 3: Get - Machine Configuration

Learn to read auto-detected machine configuration values.
zCLI automatically detects your hardware, OS, Python runtime, and tools.

Run:
    python3 Demos/Layer_0/zConfig_Demo/lvl3_get/1_zmachine.py

Key Discovery:
  - Access machine config with z.config.get_machine()
  - 42 properties organized by category (metal-aware + network-aware!)
  - CPU architecture details (P-cores, E-cores on Apple Silicon)
  - GPU detection (type, vendor, memory, compute APIs)
  - Network detection (6 essential properties: interfaces, IPs, MAC, gateway)
  - Optional resource limits (cpu_cores_limit, memory_gb_limit)
  - Copy-paste any accessor line you need
"""

from zKernel import zKernel


def run_demo():
    print("\n" + "="*60)
    print("  YOUR MACHINE CONFIGURATION")
    print("="*60)

    zSpark = {
        "deployment": "Production",  # Clean output
        "title": "machine-demo",
        "logger": "INFO",
        "logger_path": "./logs",
    }
    z = zKernel(zSpark)

    # Get all machine values at once (copy this pattern)
    machine = z.config.get_machine()

    print("\n# SYSTEM IDENTITY:")
    print(f"  os                : {machine.get('os')}")
    print(f"  os_name           : {machine.get('os_name')}")
    print(f"  os_version        : {machine.get('os_version')}")
    print(f"  architecture      : {machine.get('architecture')}")
    print(f"  processor         : {machine.get('processor')}")
    print(f"  hostname          : {machine.get('hostname')}")

    print("\n# CPU ARCHITECTURE:")
    print(f"  cpu_cores         : {machine.get('cpu_cores')} (total, backward compat)")
    print(f"  cpu_physical      : {machine.get('cpu_physical')} (physical cores)")
    print(f"  cpu_logical       : {machine.get('cpu_logical')} (with hyperthreading)")
    print(f"  cpu_performance   : {machine.get('cpu_performance')} (P-cores, Apple Silicon)")
    print(f"  cpu_efficiency    : {machine.get('cpu_efficiency')} (E-cores, Apple Silicon)")

    print("\n# MEMORY:")
    print(f"  memory_gb         : {machine.get('memory_gb')}")

    print("\n# GPU:")
    print(f"  gpu_available     : {machine.get('gpu_available')}")
    print(f"  gpu_type          : {machine.get('gpu_type')}")
    print(f"  gpu_vendor        : {machine.get('gpu_vendor')}")
    print(f"  gpu_memory_gb     : {machine.get('gpu_memory_gb')}")
    print(f"  gpu_compute       : {machine.get('gpu_compute')}")
    
    print("\n# NETWORK:")
    print(f"  network_interfaces     : {machine.get('network_interfaces')}")
    print(f"  network_primary        : {machine.get('network_primary')}")
    print(f"  network_ip_local       : {machine.get('network_ip_local')}")
    print(f"  network_mac_address    : {machine.get('network_mac_address')}")
    print(f"  network_gateway        : {machine.get('network_gateway')}")
    print(f"  network_ip_public      : {machine.get('network_ip_public')}")

    print("\n# USER & PATHS:")
    print(f"  username          : {machine.get('username')}")
    print(f"  home              : {machine.get('home')}")
    print(f"  cwd               : {machine.get('cwd')}")
    print(f"  user_data_dir     : {machine.get('user_data_dir')}")

    print("\n# DEVELOPMENT TOOLS:")
    print(f"  browser           : {machine.get('browser')}")
    print(f"  ide               : {machine.get('ide')}")
    print(f"  terminal          : {machine.get('terminal')}")
    print(f"  shell             : {machine.get('shell')}")

    print("\n# PYTHON RUNTIME:")
    print(f"  python_version    : {machine.get('python_version')}")
    print(f"  python_impl       : {machine.get('python_impl')}")
    print(f"  python_build      : {machine.get('python_build')}")
    print(f"  python_compiler   : {machine.get('python_compiler')}")
    print(f"  python_executable : {machine.get('python_executable')}")
    print(f"  libc_ver          : {machine.get('libc_ver')}")

    print("\n# zCLI INSTALLATION:")
    print(f"  zcli_install_path : {machine.get('zcli_install_path')}")
    print(f"  zcli_install_type : {machine.get('zcli_install_type')}")

    print("\n# SYSTEM SETTINGS:")
    print(f"  lang              : {machine.get('lang')}")
    print(f"  timezone          : {machine.get('timezone')}")
    print(f"  path              : {machine.get('path')[:60]}...")  # Truncate for readability

    print("\n# What you discovered:")
    print("  ✓ zCLI auto-detects your machine on first run")
    print("  ✓ 42 properties available across 10 categories")
    print("  ✓ Metal-aware: P-cores, E-cores on Apple Silicon")
    print("  ✓ GPU detection: type, vendor, memory, compute APIs")
    print("  ✓ Network detection: 6 essential properties (interfaces, IPs, MAC, gateway)")
    print("  ✓ Resource limits: cpu_cores_limit, memory_gb_limit (optional)")
    print("  ✓ Production-ready for ML/compute/network-intensive apps")
    print("  ✓ Copy-paste any accessor line you need")
    print("  ✓ Stored persistently (no re-detection needed)")

    print("\n# Usage pattern:")
    print("  machine = z.config.get_machine()  # Get all values")
    print("  os = machine.get('os')            # Get single value")

if __name__ == "__main__":
    run_demo()
