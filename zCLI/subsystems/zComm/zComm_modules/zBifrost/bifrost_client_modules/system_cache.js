/**
 * ═══════════════════════════════════════════════════════════════
 * SystemCache - UI files, schemas, configs with LRU and TTL
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mirrors zLoader's system_cache for UI files, schemas, and configs.
 * Implements LRU eviction, TTL expiration, and persistent storage.
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

class SystemCache {
    constructor(options = {}) {
        this.maxSize = options.maxSize || 100;
        this.defaultTTL = options.defaultTTL || 3600000; // 1 hour
        this.cache = new Map(); // In-memory cache
        this.storage = options.storage; // Persistent storage (IndexedDB/localStorage)
        this.debug = options.debug || false;
        
        this.stats = {
            hits: 0,
            misses: 0,
            evictions: 0,
            invalidations: 0
        };
        
        // Load from persistent storage on init
        if (this.storage) {
            this._loadFromStorage();
        }
    }
    
    /**
     * Get value from cache
     * @param {string} key - Cache key
     * @returns {Promise<any>} Cached value or null
     */
    async get(key) {
        // Check in-memory first (fast path)
        if (this.cache.has(key)) {
            const entry = this.cache.get(key);
            
            // Check TTL
            if (entry.expiresAt && Date.now() > entry.expiresAt) {
                this.cache.delete(key);
                if (this.storage) {
                    await this.storage.delete(`system:${key}`);
                }
                this.stats.invalidations++;
                if (this.debug) {
                    console.log(`[SystemCache] EXPIRED ${key}`);
                }
                return null;
            }
            
            // Update access time and move to end (LRU)
            entry.accessedAt = Date.now();
            entry.hits++;
            this.cache.delete(key);
            this.cache.set(key, entry);
            
            this.stats.hits++;
            if (this.debug) {
                console.log(`[SystemCache] HIT ${key} (hits: ${entry.hits})`);
            }
            
            return entry.data;
        }
        
        // Check persistent storage (slow path)
        if (this.storage) {
            const entry = await this.storage.get(`system:${key}`);
            if (entry) {
                // Check TTL
                if (entry.expiresAt && Date.now() > entry.expiresAt) {
                    await this.storage.delete(`system:${key}`);
                    this.stats.invalidations++;
                    if (this.debug) {
                        console.log(`[SystemCache] EXPIRED (storage) ${key}`);
                    }
                    return null;
                }
                
                // Load into memory
                this.cache.set(key, entry);
                this.stats.hits++;
                if (this.debug) {
                    console.log(`[SystemCache] HIT (storage) ${key}`);
                }
                return entry.data;
            }
        }
        
        this.stats.misses++;
        if (this.debug) {
            console.log(`[SystemCache] MISS ${key}`);
        }
        
        return null;
    }
    
    /**
     * Set value in cache
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     * @param {Object} options - Cache options
     * @param {number} options.ttl - Time to live in milliseconds
     * @param {Object} options.metadata - Additional metadata
     * @returns {Promise<any>} The cached value
     */
    async set(key, value, options = {}) {
        const ttl = options.ttl || this.defaultTTL;
        const entry = {
            data: value,
            cachedAt: Date.now(),
            accessedAt: Date.now(),
            expiresAt: ttl ? Date.now() + ttl : null,
            hits: 0,
            metadata: options.metadata || {}
        };
        
        // Store in memory
        this.cache.set(key, entry);
        
        // Persist to storage
        if (this.storage) {
            await this.storage.set(`system:${key}`, entry);
        }
        
        if (this.debug) {
            const ttlStr = ttl ? `${Math.round(ttl / 1000)}s TTL` : 'no TTL';
            console.log(`[SystemCache] SET ${key} (${ttlStr})`);
        }
        
        // LRU eviction if over max size
        while (this.cache.size > this.maxSize) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
            if (this.storage) {
                await this.storage.delete(`system:${oldestKey}`);
            }
            this.stats.evictions++;
            if (this.debug) {
                console.log(`[SystemCache] EVICT ${oldestKey} (LRU)`);
            }
        }
        
        return value;
    }
    
    /**
     * Invalidate specific key
     * @param {string} key - Cache key
     */
    async invalidate(key) {
        this.cache.delete(key);
        if (this.storage) {
            await this.storage.delete(`system:${key}`);
        }
        this.stats.invalidations++;
        if (this.debug) {
            console.log(`[SystemCache] INVALIDATE ${key}`);
        }
    }
    
    /**
     * Clear all system cache
     */
    async clear() {
        const size = this.cache.size;
        this.cache.clear();
        
        if (this.storage) {
            const keys = await this.storage.getAllKeys('system:');
            await Promise.all(keys.map(k => this.storage.delete(k)));
        }
        
        if (this.debug) {
            console.log(`[SystemCache] CLEAR (${size} entries removed)`);
        }
    }
    
    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getStats() {
        const totalRequests = this.stats.hits + this.stats.misses;
        const hitRate = totalRequests > 0 ? (this.stats.hits / totalRequests) : 0;
        
        return {
            ...this.stats,
            size: this.cache.size,
            maxSize: this.maxSize,
            hitRate: Math.round(hitRate * 1000) / 10 // Percentage with 1 decimal
        };
    }
    
    /**
     * Load cache from persistent storage
     * @private
     */
    async _loadFromStorage() {
        if (!this.storage) return;
        
        try {
            const entries = await this.storage.getAll('system:');
            let loaded = 0;
            
            for (const [key, entry] of entries) {
                // Skip expired entries
                if (entry.expiresAt && Date.now() > entry.expiresAt) {
                    await this.storage.delete(key);
                    continue;
                }
                
                const cacheKey = key.replace('system:', '');
                this.cache.set(cacheKey, entry);
                loaded++;
            }
            
            if (this.debug && loaded > 0) {
                console.log(`[SystemCache] Loaded ${loaded} entries from storage`);
            }
        } catch (e) {
            console.warn('[SystemCache] Failed to load from storage:', e);
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemCache;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.SystemCache = SystemCache;
}
