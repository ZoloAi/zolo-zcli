"""
Layer 0: zCache Demo (Terminal Mode)
=====================================

Demonstrates zCLI's foundation caching system:
- Session-level cache (z.session['zCache'])
- Cache hit/miss patterns
- Performance comparison
- Basic cache operations

Key Concept: Simple in-memory caching speeds up expensive operations
"""

from zCLI import zCLI
import time

# Initialize zCLI
z = zCLI()

# Initialize cache (if not exists)
if 'zCache' not in z.session:
    z.session['zCache'] = {}

z.display.header("Layer 0: Cache Performance Demo", color="CYAN")
z.display.text("Comparing performance: WITH vs WITHOUT caching")
z.display.text("", break_after=False)

# ============================================
# Simulate Expensive Operation
# ============================================
def expensive_operation():
    """
    Simulates a slow operation (database query, API call, file I/O).
    In real apps, this could be:
    - Database query (SELECT * FROM users WHERE complex_condition)
    - API call (requests.get('https://api.example.com/data'))
    - File processing (pd.read_csv('huge_file.csv'))
    - Complex computation (machine learning inference)
    """
    time.sleep(0.5)  # 500ms delay
    return {
        "result": "expensive data", 
        "records": 1000,
        "timestamp": time.time()
    }

# ============================================
# Part 1: WITHOUT Cache (Slow)
# ============================================
z.display.header("Part 1: WITHOUT Cache", color="RED")
z.display.text("Every call runs the expensive operation...")
z.display.text("", break_after=False)

# First call
z.display.info("Call 1: Running expensive operation...")
start = time.time()
data1 = expensive_operation()
time1 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time1:.0f}ms")

# Second call (no cache!)
z.display.info("Call 2: Running expensive operation AGAIN...")
start = time.time()
data2 = expensive_operation()
time2 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time2:.0f}ms")

# Third call (still no cache!)
z.display.info("Call 3: Running expensive operation AGAIN...")
start = time.time()
data3 = expensive_operation()
time3 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time3:.0f}ms")

total_without_cache = time1 + time2 + time3
z.display.warning(f"⚠️  Total time: {total_without_cache:.0f}ms ({total_without_cache/1000:.1f} seconds)")
z.display.text("", break_after=False)

# ============================================
# Part 2: WITH Cache (Fast!)
# ============================================
z.display.header("Part 2: WITH Cache", color="GREEN")
z.display.text("First call caches result, subsequent calls reuse it...")
z.display.text("", break_after=False)

def cached_operation():
    """
    Same expensive operation, but with caching!
    Pattern:
    1. Check if data is in cache
    2. If yes (cache HIT): return immediately
    3. If no (cache MISS): run operation and save to cache
    """
    cache_key = 'expensive_data'
    
    # Check cache first
    if cache_key in z.session['zCache']:
        z.display.success("✅ Cache HIT! (returning cached data)")
        return z.session['zCache'][cache_key]
    
    # Cache miss - run expensive operation
    z.display.warning("⚠️  Cache MISS (loading from source...)")
    result = expensive_operation()
    
    # Save to cache for next time
    z.session['zCache'][cache_key] = result
    return result

# First call (cache miss)
z.display.info("Call 1: Checking cache...")
start = time.time()
data4 = cached_operation()
time4 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time4:.0f}ms")

# Second call (cache hit!)
z.display.info("Call 2: Checking cache...")
start = time.time()
data5 = cached_operation()
time5 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time5:.0f}ms")

# Third call (cache hit!)
z.display.info("Call 3: Checking cache...")
start = time.time()
data6 = cached_operation()
time6 = (time.time() - start) * 1000
z.display.success(f"✓ Completed in {time6:.0f}ms")

total_with_cache = time4 + time5 + time6
z.display.success(f"✅ Total time: {total_with_cache:.0f}ms ({total_with_cache/1000:.1f} seconds)")
z.display.text("", break_after=False)

# ============================================
# Part 3: Performance Comparison
# ============================================
z.display.header("Performance Comparison", color="MAGENTA")

speedup = total_without_cache / total_with_cache
time_saved = total_without_cache - total_with_cache

comparison = [
    f"WITHOUT cache: {total_without_cache:.0f}ms",
    f"WITH cache:    {total_with_cache:.0f}ms",
    f"Time saved:    {time_saved:.0f}ms",
    f"Speedup:       {speedup:.1f}x faster!"
]

for line in comparison:
    z.display.text(f"  • {line}", indent=1, break_after=False)

z.display.text("", break_after=False)

if speedup >= 2:
    z.display.success(f"🚀 Caching made this {speedup:.1f}x faster!")
else:
    z.display.info("ℹ️  Caching helps, but operation is already fast")

# ============================================
# Part 4: Cache Inspection
# ============================================
z.display.text("", break_after=False)
z.display.header("Cache Contents", color="BLUE")
z.display.text("Current cache state:")
z.display.json_data(z.session.get('zCache', {}))

# ============================================
# Part 5: Cache Operations
# ============================================
z.display.text("", break_after=False)
z.display.header("Cache Operations", color="YELLOW")

# Check operation
cache_exists = 'expensive_data' in z.session['zCache']
z.display.info(f"Check: 'expensive_data' in cache? {cache_exists}")

# Clear operation
z.display.warning("Clearing cache...")
z.session['zCache'] = {}
cache_exists_after = 'expensive_data' in z.session['zCache']
z.display.success(f"After clear: 'expensive_data' in cache? {cache_exists_after}")

# ============================================
# Summary
# ============================================
z.display.text("", break_after=False)
z.display.header("Summary", color="CYAN")
z.display.success("You've learned about:")
summary_points = [
    "z.session['zCache'] - Where zCLI stores cached data",
    "Cache HIT - Data found in cache (fast!)",
    "Cache MISS - Data not in cache (slow, then cached)",
    "get/set/check/clear - Basic cache operations",
    f"Performance - Caching made this {speedup:.1f}x faster!"
]
z.display.list(summary_points)

z.display.text("", break_after=False)
z.display.info("💡 Next: Try the zBifrost version to see this in a browser!")
z.display.text("Run: python3 cache_demo_bifrost.py")

