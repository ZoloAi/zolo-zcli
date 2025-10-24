/**
 * ═══════════════════════════════════════════════════════════════
 * PluginCache - JS modules/plugins with collision detection
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mirrors zLoader's plugin_cache for lazy-loaded JS modules.
 * Detects name collisions and provides LRU eviction.
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

class PluginCache {
    constructor(options = {}) {
        this.cache = new Map();
        this.maxSize = options.maxSize || 50;
        this.debug = options.debug || false;
        
        this.stats = {
            hits: 0,
            misses: 0,
            loads: 0,
            collisions: 0
        };
    }
    
    /**
     * Get plugin module from cache
     * @param {string} pluginName - Plugin name
     * @returns {Promise<any>} Cached module or null
     */
    async get(pluginName) {
        if (this.cache.has(pluginName)) {
            this.stats.hits++;
            const entry = this.cache.get(pluginName);
            
            if (this.debug) {
                console.log(`[PluginCache] HIT ${pluginName}`);
            }
            
            return entry;
        }
        
        this.stats.misses++;
        if (this.debug) {
            console.log(`[PluginCache] MISS ${pluginName}`);
        }
        
        return null;
    }
    
    /**
     * Load and cache a JS plugin module
     * @param {string} pluginName - Plugin name (cache key)
     * @param {string} url - Plugin URL for dynamic import
     * @returns {Promise<any>} Loaded module
     * @throws {Error} If collision detected or load fails
     */
    async loadAndCache(pluginName, url) {
        // Check for collision
        if (this.cache.has(pluginName)) {
            const existing = this.cache.get(pluginName);
            if (existing.url !== url) {
                this.stats.collisions++;
                throw new Error(
                    `[PluginCache] Collision: '${pluginName}' already loaded from ${existing.url}\n` +
                    `Attempted to load from: ${url}\n` +
                    `Hint: Rename one of the plugins to avoid collision`
                );
            }
            // Same URL - return cached version
            if (this.debug) {
                console.log(`[PluginCache] Collision check passed: ${pluginName}`);
            }
            return existing.module;
        }
        
        // Dynamic import
        try {
            if (this.debug) {
                console.log(`[PluginCache] LOAD ${pluginName} from ${url}`);
            }
            
            const module = await import(url);
            const entry = {
                module,
                url,
                loadedAt: Date.now()
            };
            
            this.cache.set(pluginName, entry);
            this.stats.loads++;
            
            // LRU eviction if over max size
            while (this.cache.size > this.maxSize) {
                const oldestKey = this.cache.keys().next().value;
                this.cache.delete(oldestKey);
                if (this.debug) {
                    console.log(`[PluginCache] EVICT ${oldestKey} (LRU)`);
                }
            }
            
            return module;
        } catch (e) {
            throw new Error(
                `[PluginCache] Failed to load plugin '${pluginName}' from ${url}\n` +
                `Error: ${e.message}`
            );
        }
    }
    
    /**
     * Clear all cached plugins
     */
    clear() {
        const size = this.cache.size;
        this.cache.clear();
        if (this.debug) {
            console.log(`[PluginCache] CLEAR (${size} plugins removed)`);
        }
    }
    
    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getStats() {
        return {
            ...this.stats,
            size: this.cache.size,
            maxSize: this.maxSize
        };
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PluginCache;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.PluginCache = PluginCache;
}
