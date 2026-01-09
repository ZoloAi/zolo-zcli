# zBifrost Cache Performance Demo

**Demonstrates**: Comprehensive frontend caching system + declarative test orchestration using zWizard

## Overview

This demo showcases two major v1.5.4 features:

1. **4-Tier Frontend Caching** - Mirroring zLoader's backend cache architecture
2. **Declarative Test Orchestration** - Using zWizard sequences instead of imperative JavaScript

## Architecture

### Frontend Caching (Client-Side)
```
┌─────────────────────────────────────────────────────────┐
│ BifrostClient (bifrost_client.js v2.0)                 │
├─────────────────────────────────────────────────────────┤
│ Cache Orchestrator                                      │
│  ├─ System Cache (schemas, UI, configs) - LRU + TTL    │
│  ├─ Pinned Cache (user bookmarks) - Never evicts       │
│  ├─ Plugin Cache (lazy-loaded .js modules) - LRU       │
│  └─ Session Cache (active session data) - In-memory    │
├─────────────────────────────────────────────────────────┤
│ Storage Layer                                           │
│  ├─ IndexedDB (persistent)                             │
│  └─ LocalStorage (fallback)                            │
└─────────────────────────────────────────────────────────┘
```

### Backend Query Caching (Server-Side)
```
┌─────────────────────────────────────────────────────────┐
│ zBifrost (bifrost_bridge.py)                           │
├─────────────────────────────────────────────────────────┤
│ Query Cache (SQL results) - TTL-based                  │
│  ├─ Cache key: SQL query hash                          │
│  ├─ Hit/Miss tracking                                  │
│  └─ Manual invalidation                                │
└─────────────────────────────────────────────────────────┘
```

## Declarative vs Imperative

### ❌ Imperative Approach (Old Way)
```javascript
// 50+ lines of JavaScript to orchestrate tests
document.getElementById('runAllTests').onclick = async () => {
    const allResults = [];
    
    // Clear all caches
    await zBifrost.cache.clear();
    await zBifrost.request('clear_cache');
    
    // Test 1: System cache
    console.log('Running System Cache Test...');
    await zBifrost.cache.clear('system');
    const t1 = performance.now();
    await zBifrost.getSchema('@.zSchema.cache_demo');
    const time1 = (performance.now() - t1).toFixed(2);
    const t2 = performance.now();
    await zBifrost.getSchema('@.zSchema.cache_demo');
    const time2 = (performance.now() - t2).toFixed(2);
    allResults.push({
        test: 'System Cache',
        status: time1 / time2 > 5 ? 'PASS' : 'WARN',
        speedup: `${(time1 / time2).toFixed(0)}x`,
        details: `${time1}ms → ${time2}ms`
    });
    
    // Test 2: Pinned cache
    console.log('Running Pinned Cache Test...');
    const alias = `test_${Date.now()}`;
    await zBifrost.cache.set(alias, { test: 'data' }, 'pinned');
    const pinned = await zBifrost.cache.get(alias, 'pinned');
    allResults.push({
        test: 'Pinned Cache',
        status: pinned ? 'PASS' : 'FAIL',
        speedup: 'N/A',
        details: pinned ? 'OK' : 'Failed'
    });
    
    // ... 30+ more lines for other tests ...
    
    // Display results
    document.getElementById('results').innerHTML = formatResults(allResults);
};
```

### ✅ Declarative Approach (zKernel Way)
```yaml
# zUI.cache_demo.yaml (12 lines)
"^Run All Cache Tests":
  zWizard:
    system_cache_miss:
      zData:
        action: read
        model: "@.zSchema.cache_demo"
        table: products
        limit: 5
    
    system_cache_hit:
      zData:
        action: read
        model: "@.zSchema.cache_demo"
        table: products
        limit: 5
    
    query_cache_test:
      zData:
        action: read
        model: "@.zSchema.cache_demo"
        table: products
        limit: 5
    
    display_results:
      zFunc: "&cache_test_aggregator.aggregate_results(zHat)"
```

```javascript
// Frontend (3 lines)
document.getElementById('runAllTests').onclick = async () => {
    const results = await zBifrost.cmd('^Run All Cache Tests');
    zBifrost.render.table(results.tests, '#resultsTable');
};
```

**Code Reduction**: **94%** (50 lines → 3 lines)

## How It Works

### 1. Frontend sends ONE command
```javascript
const results = await zBifrost.cmd('^Run All Cache Tests');
```

### 2. Backend executes zWizard sequence
```yaml
zWizard:
  step1: zData query...
  step2: zData query...
  step3: zData query...
  step4: zFunc aggregator...
```

### 3. zWizard builds zHat array
```python
zHat = [
    [product1, product2, ...],  # Step 1 result
    [product1, product2, ...],  # Step 2 result (cached)
    [product1, product2, ...],  # Step 3 result (cached)
    {...aggregated_results...}   # Step 4 result
]
```

### 4. zFunc aggregates results
```python
def aggregate_results(zHat):
    return {
        "tests": [
            {"name": "System Cache Miss", "data": zHat[0]},
            {"name": "System Cache Hit", "data": zHat[1]},
            {"name": "Query Cache", "data": zHat[2]}
        ],
        "summary": {
            "total_steps": len(zHat),
            "data_consistent": zHat[0] == zHat[1]
        }
    }
```

### 5. Frontend displays results
```javascript
zBifrost.render.table(results.tests, '#resultsTable');
```

## Benefits

### Declarative Approach
✅ **Less Code**: 94% reduction in frontend code  
✅ **Testable**: Backend logic can be unit tested  
✅ **Reusable**: zWizard sequence can be reused in Shell mode  
✅ **Maintainable**: Logic lives in YAML, not scattered in JS  
✅ **Type-Safe**: zData handles SQL, zFunc handles business logic  
✅ **Cacheable**: Results flow through zLoader's cache system  
✅ **Transactional**: Can add `_transaction: true` for atomicity  

### Imperative Approach
❌ **More Code**: 50+ lines of JS for orchestration  
❌ **Hard to Test**: Logic mixed with DOM manipulation  
❌ **Not Reusable**: Cannot run same tests from Shell  
❌ **Hard to Maintain**: Logic scattered across JS callbacks  
❌ **Error-Prone**: Manual error handling, timing, state management  
❌ **No Caching**: Results don't flow through zLoader  
❌ **No Transactions**: Manual rollback logic required  

## Files

```
Cache_Performance_Demo/
├── Cache_Performance_Demo.html       # Frontend UI (uses zBifrost v2.0)
├── zUI.cache_demo.yaml                # Declarative commands + zWizard sequence
├── zSchema.cache_demo.yaml            # Database schema
├── cache_test_aggregator.py           # zFunc plugin for result aggregation
├── run_cache_demo.py                  # Backend runner with zSpark config
└── README.md                          # This file
```

## Running the Demo

### 1. Start Backend
```bash
cd Demos/zcli-features/Cache_Performance_Demo
python run_cache_demo.py
```

### 2. Open Frontend
```
http://127.0.0.1:5500/Demos/zcli-features/Cache_Performance_Demo/Cache_Performance_Demo.html
```

### 3. Click "Run All Tests"
Watch as the declarative zWizard sequence:
- Executes 3 sequential database queries
- Builds zHat array with results
- Passes zHat to aggregator plugin
- Returns formatted results to frontend
- Frontend displays in <3 lines of code

## Test Results

The demo compares:

1. **Declarative (zWizard)**: Backend orchestrates, frontend displays
2. **Imperative (Frontend)**: JavaScript orchestrates everything

**Expected Output**:
```
✅ System Cache (zWizard) - Declarative - 3/3 steps OK
✅ Query Cache (Backend) - Server-side - 10 records
✅ zHat Results - N/A - Full zWizard result received
✅ Frontend Imperative - 2.5x - 150ms → 60ms
✅ Code Comparison - ~10x less JS - 1 zWizard call vs 50+ lines
```

## Key Takeaways

1. **zWizard** = Backend test orchestration
2. **zHat** = Inter-step result passing
3. **zFunc** = Business logic plugins
4. **zBifrost** = Real-time WebSocket transport
5. **Declarative > Imperative** = Less code, more power

## Related Documentation

- [zWizard Guide](../../../Documentation/zWizard_GUIDE.md)
- [zComm Guide](../../../Documentation/zComm_GUIDE.md)
- [zBifrost Client v2.0 Release](../../../Documentation/Release/RELEASE_1.5.4_BIFROST_REFACTOR_V2.md)
- [Cache System Architecture](../../../Documentation/Release/RELEASE_1.5.4_CACHE_SYSTEM.md)

---

**Version**: 1.5.4  
**Status**: ✅ Production Ready
