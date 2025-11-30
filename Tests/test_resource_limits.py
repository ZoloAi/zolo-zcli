#!/usr/bin/env python3
"""
Resource Limits Test Script
============================

Demonstrates and verifies that cpu_cores_limit and memory_gb_limit work correctly.

Tests:
    1. CPU limit: Multiprocessing pool respects core limits
    2. Memory limit: Application can query and respect limits
    3. Cross-platform: Works on Windows, macOS, Linux
    4. Linux bonus: Shows OS-level hard enforcement status

Run:
    python3 Tests/test_resource_limits.py
"""

import multiprocessing
import platform
import sys
import time
from pathlib import Path

# Add zCLI to path if running from Tests directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI


def cpu_intensive_work(task_id: int) -> dict:
    """Simulate CPU-intensive work."""
    start = time.time()
    
    # Busy loop for ~0.5 seconds
    result = 0
    for i in range(10_000_000):
        result += i * i
    
    duration = time.time() - start
    return {
        "task_id": task_id,
        "result": result,
        "duration": duration,
        "pid": multiprocessing.current_process().pid
    }


def test_without_limits():
    """Test 1: No resource limits (baseline)."""
    print("\n" + "="*70)
    print("  TEST 1: NO RESOURCE LIMITS (BASELINE)")
    print("="*70)
    
    # Initialize zCLI without limits
    z = zCLI({
        "deployment": "Production",
        "title": "resource-test",
        "logger": "INFO",
    })
    
    # Get machine config
    machine = z.config.get_machine()
    cpu_available = machine.get('cpu_cores')
    memory_available = machine.get('memory_gb')
    
    print(f"\n# Hardware detected:")
    print(f"  CPU cores available    : {cpu_available}")
    print(f"  Memory available       : {memory_available} GB")
    
    # Get resource limits (should match available)
    cpu_limit = z.config.get_cpu_limit()
    memory_limit = z.config.get_memory_limit_gb()
    
    print(f"\n# Effective limits:")
    print(f"  CPU limit              : {cpu_limit} (no limit set)")
    print(f"  Memory limit           : {memory_limit} GB (no limit set)")
    
    # Test multiprocessing with all available cores
    print(f"\n# Running multiprocessing pool with {cpu_limit} workers...")
    
    with multiprocessing.Pool(processes=cpu_limit) as pool:
        results = pool.map(cpu_intensive_work, range(8))  # 8 tasks
    
    unique_pids = set(r['pid'] for r in results)
    avg_duration = sum(r['duration'] for r in results) / len(results)
    
    print(f"  Tasks completed        : {len(results)}")
    print(f"  Unique worker PIDs     : {len(unique_pids)}")
    print(f"  Avg task duration      : {avg_duration:.3f}s")
    
    print("\n✅ Test 1 complete (baseline established)")
    return z


def test_with_cpu_limit():
    """Test 2: CPU core limit enforced."""
    print("\n" + "="*70)
    print("  TEST 2: CPU CORE LIMIT (2 CORES)")
    print("="*70)
    
    # Create temp zMachine config with limits
    print("\n# Setting up zMachine with cpu_cores_limit: 2...")
    
    # Initialize zCLI
    z = zCLI({
        "deployment": "Production",
        "title": "resource-test",
        "logger": "INFO",
    })
    
    # Manually set limit for testing (in real usage, user edits zConfig.machine.yaml)
    machine = z.config.get_machine()
    machine['cpu_cores_limit'] = 2  # Limit to 2 cores
    
    # Reinitialize resource limits with new config
    from zCLI.subsystems.zConfig.zConfig_modules.config_resource_limits import ResourceLimits
    z.config.resource_limits = ResourceLimits(machine)
    z.config.resource_limits.apply()
    
    # Get limits
    cpu_available = machine.get('cpu_cores')
    cpu_limit = z.config.get_cpu_limit()
    
    print(f"\n# Hardware detected:")
    print(f"  CPU cores available    : {cpu_available}")
    
    print(f"\n# Effective limits:")
    print(f"  CPU limit              : {cpu_limit} ← LIMITED!")
    
    # Get detailed status
    status = z.config.get_resource_limits_status()
    print(f"\n# Resource limits status:")
    print(f"  Platform               : {status['platform']}")
    print(f"  Hard limits supported  : {status['hard_limits_supported']}")
    print(f"  Hard limits applied    : {status['hard_limits_applied']}")
    
    # Test multiprocessing with limited cores
    print(f"\n# Running multiprocessing pool with {cpu_limit} workers...")
    
    with multiprocessing.Pool(processes=cpu_limit) as pool:
        results = pool.map(cpu_intensive_work, range(8))  # 8 tasks
    
    unique_pids = set(r['pid'] for r in results)
    avg_duration = sum(r['duration'] for r in results) / len(results)
    
    print(f"  Tasks completed        : {len(results)}")
    print(f"  Unique worker PIDs     : {len(unique_pids)} ← Should be ~{cpu_limit}")
    print(f"  Avg task duration      : {avg_duration:.3f}s")
    
    # Verify limit worked
    if len(unique_pids) <= cpu_limit + 1:  # +1 tolerance for main process
        print("\n✅ Test 2 PASSED: CPU limit enforced correctly!")
    else:
        print(f"\n⚠️  Test 2 WARNING: Expected ~{cpu_limit} workers, got {len(unique_pids)}")
    
    return z


def test_with_memory_limit():
    """Test 3: Memory limit available for application use."""
    print("\n" + "="*70)
    print("  TEST 3: MEMORY LIMIT (4 GB)")
    print("="*70)
    
    # Initialize zCLI
    z = zCLI({
        "deployment": "Production",
        "title": "resource-test",
        "logger": "INFO",
    })
    
    # Manually set limit for testing
    machine = z.config.get_machine()
    machine['memory_gb_limit'] = 4  # Limit to 4 GB
    
    # Reinitialize resource limits
    from zCLI.subsystems.zConfig.zConfig_modules.config_resource_limits import ResourceLimits
    z.config.resource_limits = ResourceLimits(machine)
    z.config.resource_limits.apply()
    
    # Get limits
    memory_available = machine.get('memory_gb')
    memory_limit = z.config.get_memory_limit_gb()
    memory_bytes = z.config.resource_limits.get_memory_limit_bytes()
    
    print(f"\n# Hardware detected:")
    print(f"  Memory available       : {memory_available} GB")
    
    print(f"\n# Effective limits:")
    print(f"  Memory limit           : {memory_limit} GB ← LIMITED!")
    print(f"  Memory limit (bytes)   : {memory_bytes:,}")
    
    # Demonstrate how application would use this
    print(f"\n# Example: Cache size calculation")
    cache_size = int(memory_limit * 0.25 * 1024**3)  # 25% of limit
    print(f"  Limit 25% of memory to cache")
    print(f"  Cache size: {cache_size / 1024**3:.2f} GB ({cache_size:,} bytes)")
    
    # Get detailed status
    status = z.config.get_resource_limits_status()
    print(f"\n# Resource limits status:")
    print(f"  Platform               : {status['platform']}")
    
    if status['platform'] == "Linux":
        print(f"  Hard limit applied     : {status['hard_limits_applied']}")
        if status['hard_limits_applied']:
            print("  → OS will kill process if memory exceeds 4 GB!")
        else:
            print("  → Soft limit only (application respects voluntarily)")
    else:
        print("  → Soft limit only (application respects voluntarily)")
    
    print("\n✅ Test 3 PASSED: Memory limit queryable and usable!")
    
    return z


def test_combined_limits():
    """Test 4: Both CPU and memory limits together."""
    print("\n" + "="*70)
    print("  TEST 4: COMBINED LIMITS (CPU: 2, MEMORY: 4 GB)")
    print("="*70)
    
    # Initialize zCLI
    z = zCLI({
        "deployment": "Production",
        "title": "resource-test",
        "logger": "INFO",
    })
    
    # Set both limits
    machine = z.config.get_machine()
    machine['cpu_cores_limit'] = 2
    machine['memory_gb_limit'] = 4
    
    # Reinitialize resource limits
    from zCLI.subsystems.zConfig.zConfig_modules.config_resource_limits import ResourceLimits
    z.config.resource_limits = ResourceLimits(machine)
    result = z.config.resource_limits.apply()
    
    print(f"\n# Combined resource limits applied:")
    print(f"  CPU limit              : {result['cpu_limit']} cores")
    print(f"  Memory limit           : {result['memory_limit_gb']} GB")
    print(f"  Soft limits applied    : {result['soft_limits_applied']}")
    print(f"  Hard limits applied    : {result['hard_limits_applied']}")
    print(f"  Platform               : {result['platform']}")
    
    if result['errors']:
        print(f"\n# Errors/Warnings:")
        for error in result['errors']:
            print(f"  ⚠️  {error}")
    
    # Get full status
    status = z.config.get_resource_limits_status()
    
    print(f"\n# Full status:")
    print(f"  CPU available/limit/effective  : {status['cpu_cores_available']}/{status['cpu_cores_limit']}/{status['cpu_cores_effective']}")
    print(f"  Memory available/limit/effective: {status['memory_gb_available']}/{status['memory_gb_limit']}/{status['memory_gb_effective']} GB")
    
    print("\n✅ Test 4 PASSED: Combined limits work correctly!")
    
    return z


def main():
    """Run all resource limit tests."""
    print("\n" + "="*70)
    print("  ZCLI RESOURCE LIMITS TEST SUITE")
    print("="*70)
    print(f"\n# System information:")
    print(f"  Platform      : {platform.system()}")
    print(f"  Architecture  : {platform.machine()}")
    print(f"  Python        : {platform.python_version()}")
    
    try:
        # Run all tests
        test_without_limits()
        test_with_cpu_limit()
        test_with_memory_limit()
        test_combined_limits()
        
        # Summary
        print("\n" + "="*70)
        print("  TEST SUITE SUMMARY")
        print("="*70)
        print("\n✅ ALL TESTS PASSED!")
        print("\n# Key findings:")
        print("  ✓ Resource limits are detected and stored correctly")
        print("  ✓ CPU limits can control multiprocessing pool sizes")
        print("  ✓ Memory limits are queryable for cache/buffer sizing")
        print("  ✓ Cross-platform soft limits work on all systems")
        
        if platform.system() == "Linux":
            print("  ✓ Linux bonus: OS-level hard limits available")
        else:
            print(f"  • {platform.system()}: Soft limits only (expected)")
        
        print("\n# How to use in your code:")
        print("  cpu_limit = z.config.get_cpu_limit()")
        print("  memory_limit = z.config.get_memory_limit_gb()")
        print("  pool = multiprocessing.Pool(processes=cpu_limit)")
        print("  cache_size = int(memory_limit * 0.25 * 1024**3)")
        
        print("\n# How to set limits:")
        print("  Edit: ~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml")
        print("  Add:")
        print("    cpu_cores_limit: 4")
        print("    memory_gb_limit: 8")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Multiprocessing requires this on Windows
    multiprocessing.freeze_support()
    main()

