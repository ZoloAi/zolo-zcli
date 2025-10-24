# BifrostClient Cache System v1.5.4

## Overview

The BifrostClient cache system mirrors **zLoader's 4-tier cache architecture** on the frontend, providing fast, persistent client-side caching for schemas, UI files, user aliases, plugins, and session data.

This enables **50-100x faster** cache hits (no network roundtrip) and prepares the foundation for advanced features like declarative menus and offline mode.

## Architecture

### 4 Cache Types

| Cache Type | Purpose | Storage | Eviction | Persistence |
|------------|---------|---------|----------|-------------|
| **System** | Schemas, UI files, configs | IndexedDB | LRU + TTL | ✅ Cross-session |
| **Pinned** | User bookmarks/aliases | IndexedDB | Never | ✅ Cross-session |
| **Plugin** | JS modules | In-memory | LRU | ❌ Session-only |
| **Session** | Active session data | In-memory | Manual | ❌ Lost on refresh |

### Storage Adapters

- **IndexedDB** (primary): Async, 50MB+ capacity, structured data
- **localStorage** (fallback): Sync, 5-10MB capacity, simple key-value

## Usage

### Basic Usage

```javascript
const client = new BifrostClient('ws://localhost:8765', {
  autoTheme: true,
  persistCache: true,  // Enable persistent caching (default: true)
  maxCacheSize: 100,   // Max system cache size (default: 100)
  defaultCacheTTL: 3600000  // Default TTL: 1 hour
});

await client.connect();
```

### System Cache - Schemas, UI Files, Configs

```javascript
// Get schema (auto-cached)
const schema = await client.getSchema('@.zSchema.users');

// Manually cache data
await client.cache.set('myKey', data, 'system', {
  ttl: 3600000,  // 1 hour
  metadata: { type: 'schema', model: 'users' }
});

// Get from cache
const cached = await client.cache.get('myKey', 'system');

// Clear system cache
await client.clearCache('system');
```

### Pinned Cache - User Bookmarks

```javascript
// Pin a resource
await client.pinResource('myConfig', '@.zConfig.user');

// Get pinned resource
const config = await client.getPinnedResource('myConfig');

// List all pinned resources
const list = client.cache.pinnedCache.listAll();

// Clear pinned cache
await client.clearCache('pinned');
```

### Plugin Cache - JS Modules

```javascript
// Load plugin (auto-cached)
const plugin = await client.loadPlugin('myPlugin', './plugins/my-plugin.js');

// Collision detection
await client.loadPlugin('myPlugin', './other-url.js');
// ❌ Throws: Plugin collision error

// Clear plugin cache
client.cache.pluginCache.clear();
```

### Session Cache - Active Session Data

```javascript
// Store session data
client.cache.sessionCache.set('activeUser', { id: 123, name: 'John' });
client.cache.sessionCache.set('theme', 'dark');

// Get session data
const user = client.cache.sessionCache.get('activeUser');

// Clear session cache
client.cache.sessionCache.clear();
```

### Cache Statistics

```javascript
// Get all cache stats
const stats = client.getAllCacheStats();
console.log(stats);
/*
{
  system: { 
    hits: 10, misses: 2, size: 15, hitRate: 83.3, 
    evictions: 0, invalidations: 0 
  },
  pinned: { 
    size: 3, 
    aliases: ['myData', 'config', 'userPrefs'] 
  },
  plugin: { 
    hits: 5, misses: 1, loads: 3, size: 3, 
    collisions: 0 
  },
  session: { 
    size: 5, 
    keys: ['activeUser', 'theme', 'lastAction', ...] 
  }
}
*/

// Clear all caches
client.clearClientCache();

// Clear specific cache
await client.clearCache('system');
```

## Features Enabled

### Performance
- **50-100x faster** cache hits (no network roundtrip)
- **Persistent** across page refreshes (IndexedDB)
- **Large capacity** (50MB+ vs 5-10MB localStorage)

### Future Features
- **Declarative menus**: Cache menu definitions for instant rendering
- **Offline mode**: Pre-cache schemas, UI files for offline use
- **User preferences**: Pin frequently used resources
- **Plugin ecosystem**: Lazy-load JS extensions

## Files

### Core Modules
- `cache_orchestrator.js` - Main orchestrator managing all 4 caches
- `system_cache.js` - UI files, schemas, configs (LRU + TTL)
- `pinned_cache.js` - User aliases/bookmarks (never evicts)
- `plugin_cache.js` - JS modules with collision detection
- `session_cache.js` - Active session data (in-memory)
- `storage_adapters.js` - IndexedDB and localStorage adapters

### Integration
- `../bifrost_client.js` - Main BifrostClient with cache integration

## Demo

Test all 4 cache types with the comprehensive demo:

```bash
cd Demos/zcli-features/Cache_Performance_Demo
python3 run_cache_demo.py
```

Then open: http://127.0.0.1:5500/Demos/zcli-features/Cache_Performance_Demo/Cache_Performance_Demo.html

## Backend Changes (v1.5.4)

### bifrost_bridge.py
- Removed redundant `schema_cache` (schemas now loaded via `walker.loader.handle()`)
- Schema caching handled by zLoader on backend, mirrored by SystemCache on frontend
- Updated `get_connection_info()` to report `query_cache_stats` instead of `schema_cache`

### Backend Benefits
- Single source of truth: zLoader handles all backend caching
- No duplicate cache layers
- Frontend and backend caching architectures now aligned

## Migration from Legacy

The cache system includes automatic migration from the legacy `schemaCache` (simple Map):

```javascript
// Old (deprecated)
if (this.schemaCache.has(model)) {
  return this.schemaCache.get(model);
}

// New (v1.5.4+)
const cached = await this.cache.get(model, 'system');
if (cached) return cached;
```

Both APIs work during transition, but new code should use the cache orchestrator.

## Version History

- **v1.5.4** - Full 4-tier cache system mirroring zLoader
- **v1.5.3** - Simple in-memory schema cache (Map)
- **v1.5.2** - No client-side caching

---

**Author**: Gal Nachshon  
**License**: MIT  
**Version**: 1.5.4

