"""
Layer 0: zCache Demo (zBifrost Mode)
=====================================

The SAME caching demo as cache_demo_terminal.py, but rendered in a browser!

Key Innovation: z.display calls NOW BROADCAST automatically in zBifrost mode!
No manual JSON construction needed - just call z.display and it works everywhere.

How to run:
1. python3 cache_demo_bifrost.py
2. Open cache_client.html in your browser
3. Click "Run Cache Demo"
4. Watch the cache comparison in real-time!
"""

from zCLI import zCLI
import time

print("🌉 Starting zCache Demo Server (zBifrost mode)...")
print("📝 Goal: See cache performance comparison in a browser")
print()

# Initialize zCLI in zBifrost mode (WebSocket server)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

# Simulate expensive operation
def expensive_operation():
    """Simulates a slow database query or API call"""
    time.sleep(0.5)  # 500ms delay
    return {
        "result": "expensive data",
        "records": 1000,
        "timestamp": time.time()
    }

# Define the cache demo logic (SAME as terminal version!)
async def handle_run_cache_demo(_websocket, _message_data):
    """
    Run cache comparison demo - displays in browser!
    
    🎉 NEW: z.display calls now automatically broadcast to WebSocket!
    No manual JSON construction needed - the same code works everywhere.
    """
    
    # Initialize cache
    if 'zCache' not in z.session:
        z.session['zCache'] = {}
    
    # These z.display calls NOW BROADCAST to the browser automatically!
    z.display.header("Layer 0: Cache Performance Demo", color="CYAN")
    z.display.text("Comparing performance: WITH vs WITHOUT caching")
    z.display.text("", break_after=False)
    
    # ============================================
    # Part 1: WITHOUT Cache (Slow)
    # ============================================
    z.display.header("Part 1: WITHOUT Cache", color="RED")
    z.display.text("Every call runs the expensive operation...")
    z.display.text("", break_after=False)
    
    # First call
    z.display.info("Call 1: Running expensive operation...")
    start = time.time()
    expensive_operation()
    time1 = (time.time() - start) * 1000
    z.display.success(f"✓ Completed in {time1:.0f}ms")
    
    # Second call (no cache!)
    z.display.info("Call 2: Running expensive operation AGAIN...")
    start = time.time()
    expensive_operation()
    time2 = (time.time() - start) * 1000
    z.display.success(f"✓ Completed in {time2:.0f}ms")
    
    # Third call (still no cache!)
    z.display.info("Call 3: Running expensive operation AGAIN...")
    start = time.time()
    expensive_operation()
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
        """Same expensive operation, but with caching!"""
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
    cached_operation()
    time4 = (time.time() - start) * 1000
    z.display.success(f"✓ Completed in {time4:.0f}ms")
    
    # Second call (cache hit!)
    z.display.info("Call 2: Checking cache...")
    start = time.time()
    cached_operation()
    time5 = (time.time() - start) * 1000
    z.display.success(f"✓ Completed in {time5:.0f}ms")
    
    # Third call (cache hit!)
    z.display.info("Call 3: Checking cache...")
    start = time.time()
    cached_operation()
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
        f"Performance - Caching made this {speedup:.1f}x faster!",
        "🎉 z.display now broadcasts in zBifrost mode - same code, everywhere!"
    ]
    z.display.list(summary_points)
    
    z.display.text("", break_after=False)
    z.display.success("🎉 Cache demo complete! Same code, browser GUI!")

# Register the handler for the client to trigger demo
if z.comm.websocket:
    z.comm.websocket._event_map['run_cache_demo'] = handle_run_cache_demo  # noqa: SLF001
    print("✓ Cache demo handler registered!")
else:
    print("✗ Warning: Could not register cache demo handler")

print("✅ Server is running on ws://127.0.0.1:8765")
print("👉 Open cache_client.html in your browser")
print("👉 Click 'Run Cache Demo' to see the magic!")
print()
print("Press Ctrl+C to stop the server")
print()

# Start the WebSocket server
z.walker.run()

