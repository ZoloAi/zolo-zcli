/**
 * ═══════════════════════════════════════════════════════════════
 * CacheOrchestrator - Manages all 4 cache types for BifrostClient
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mirrors zLoader's 4-tier cache architecture on the frontend:
 * - SystemCache: UI files, schemas, configs (LRU, TTL, persistent)
 * - PinnedCache: User aliases/bookmarks (never evicts, persistent)
 * - PluginCache: JS modules/plugins (collision detection, in-memory)
 * - SessionCache: Active session data (in-memory only)
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

class CacheOrchestrator {
    constructor(options = {}) {
        this.debug = options.debug || false;
        this.storage = null;
        
        // Initialize storage backend (async, but start immediately)
        this._initStorage(options);
        
        // Initialize all 4 cache types (they'll get storage when ready)
        this.systemCache = new SystemCache({
            ...options,
            storage: this.storage
        });
        
        this.pinnedCache = new PinnedCache({
            ...options,
            storage: this.storage
        });
        
        this.pluginCache = new PluginCache(options);
        
        this.sessionCache = new SessionCache(options);
        
        if (this.debug) {
            console.log('[CacheOrchestrator] Initialized with 4 cache types');
        }
    }
    
    /**
     * Initialize storage backend (IndexedDB with localStorage fallback)
     * @private
     */
    async _initStorage(options) {
        // Skip storage if explicitly disabled
        if (options.persistCache === false) {
            if (this.debug) {
                console.log('[CacheOrchestrator] Persistent cache disabled');
            }
            return;
        }
        
        try {
            // Try IndexedDB first (best option)
            const { IndexedDBStorage } = await import('./storage_adapters.js');
            this.storage = await IndexedDBStorage.init('zBifrostCache', 1);
            
            // Update caches with storage
            this.systemCache.storage = this.storage;
            this.pinnedCache.storage = this.storage;
            
            // Reload from storage
            await this.systemCache._loadFromStorage();
            await this.pinnedCache._loadFromStorage();
            
            if (this.debug) {
                console.log('[CacheOrchestrator] Using IndexedDB for persistent storage');
            }
        } catch (e) {
            // Fallback to localStorage
            try {
                const { LocalStorageAdapter } = await import('./storage_adapters.js');
                this.storage = new LocalStorageAdapter();
                
                // Update caches with storage
                this.systemCache.storage = this.storage;
                this.pinnedCache.storage = this.storage;
                
                // Reload from storage
                await this.systemCache._loadFromStorage();
                await this.pinnedCache._loadFromStorage();
                
                if (this.debug) {
                    console.warn('[CacheOrchestrator] IndexedDB unavailable, using localStorage', e);
                }
            } catch (e2) {
                console.warn('[CacheOrchestrator] No persistent storage available, using memory only', e2);
            }
        }
    }
    
    /**
     * Get value from cache
     * @param {string} key - Cache key
     * @param {string} cacheType - Cache type (system, pinned, plugin, session)
     * @returns {Promise<any>} Cached value or null
     */
    async get(key, cacheType = 'system') {
        const cache = this._getCache(cacheType);
        return await cache.get(key);
    }
    
    /**
     * Set value in cache
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     * @param {string} cacheType - Cache type (system, pinned, plugin, session)
     * @param {Object} options - Cache-specific options
     * @returns {Promise<any>} The cached value
     */
    async set(key, value, cacheType = 'system', options = {}) {
        const cache = this._getCache(cacheType);
        
        // Different caches have different APIs
        if (cacheType === 'pinned') {
            return await cache.load(key, value, options.metadata || {});
        } else if (cacheType === 'session') {
            cache.set(key, value);
            return value;
        } else {
            return await cache.set(key, value, options);
        }
    }
    
    /**
     * Check if key exists in cache
     * @param {string} key - Cache key
     * @param {string} cacheType - Cache type
     * @returns {boolean} True if key exists
     */
    has(key, cacheType = 'system') {
        const cache = this._getCache(cacheType);
        return cache.has(key);
    }
    
    /**
     * Delete specific key from cache
     * @param {string} key - Cache key
     * @param {string} cacheType - Cache type
     */
    async delete(key, cacheType = 'system') {
        const cache = this._getCache(cacheType);
        
        if (cacheType === 'pinned') {
            await cache.remove(key);
        } else if (cacheType === 'system') {
            await cache.invalidate(key);
        } else {
            cache.delete(key);
        }
    }
    
    /**
     * Get specific cache instance
     * @private
     */
    _getCache(type) {
        switch(type) {
            case 'system': return this.systemCache;
            case 'pinned': return this.pinnedCache;
            case 'plugin': return this.pluginCache;
            case 'session': return this.sessionCache;
            default: throw new Error(`Unknown cache type: ${type}`);
        }
    }
    
    /**
     * Get statistics for all caches
     * @returns {Object} Cache statistics
     */
    getStats() {
        return {
            system: this.systemCache.getStats(),
            pinned: this.pinnedCache.getStats(),
            plugin: this.pluginCache.getStats(),
            session: this.sessionCache.getStats()
        };
    }
    
    /**
     * Clear all caches
     */
    async clearAll() {
        await Promise.all([
            this.systemCache.clear(),
            this.pinnedCache.clear(),
            this.pluginCache.clear(),
            this.sessionCache.clear()
        ]);
        
        if (this.debug) {
            console.log('[CacheOrchestrator] All caches cleared');
        }
    }
    
    /**
     * Clear specific cache type
     * @param {string} cacheType - Cache type to clear
     */
    async clear(cacheType = 'system') {
        const cache = this._getCache(cacheType);
        await cache.clear();
        
        if (this.debug) {
            console.log(`[CacheOrchestrator] ${cacheType} cache cleared`);
        }
    }
}

// Export for module systems (ES6, CommonJS, and browser global)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheOrchestrator;
}

// Browser global export
if (typeof window !== 'undefined') {
    window.CacheOrchestrator = CacheOrchestrator;
}

