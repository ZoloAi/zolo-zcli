/**
 * ═══════════════════════════════════════════════════════════════
 * PinnedCache - User aliases/bookmarks (never auto-evicts)
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mirrors zLoader's pinned_cache for user-loaded aliases.
 * Resources pinned by user are never automatically evicted.
 * Persists to IndexedDB/localStorage for cross-session use.
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

class PinnedCache {
    constructor(options = {}) {
        this.cache = new Map();
        this.storage = options.storage;
        this.debug = options.debug || false;
        
        // Load from persistent storage on init
        if (this.storage) {
            this._loadFromStorage();
        }
    }
    
    /**
     * Load/pin a resource with alias
     * @param {string} alias - User-defined alias
     * @param {any} data - Data to pin
     * @param {Object} metadata - Optional metadata
     * @returns {Promise<any>} The pinned data
     */
    async load(alias, data, metadata = {}) {
        const entry = {
            data: data,
            loadedAt: Date.now(),
            metadata: metadata
        };
        
        this.cache.set(alias, entry);
        
        if (this.storage) {
            await this.storage.set(`pinned:${alias}`, entry);
        }
        
        if (this.debug) {
            console.log(`[PinnedCache] LOAD ${alias}`, metadata);
        }
        
        return data;
    }
    
    /**
     * Get pinned resource by alias
     * @param {string} alias - User-defined alias
     * @returns {any} Pinned data or null
     */
    get(alias) {
        const entry = this.cache.get(alias);
        if (this.debug && entry) {
            console.log(`[PinnedCache] HIT ${alias}`);
        }
        return entry ? entry.data : null;
    }
    
    /**
     * Check if alias exists
     * @param {string} alias - User-defined alias
     * @returns {boolean} True if alias exists
     */
    has(alias) {
        return this.cache.has(alias);
    }
    
    /**
     * Remove/unpin specific alias
     * @param {string} alias - User-defined alias
     */
    async remove(alias) {
        this.cache.delete(alias);
        
        if (this.storage) {
            await this.storage.delete(`pinned:${alias}`);
        }
        
        if (this.debug) {
            console.log(`[PinnedCache] REMOVE ${alias}`);
        }
    }
    
    /**
     * Clear all pinned resources
     */
    async clear() {
        const size = this.cache.size;
        this.cache.clear();
        
        if (this.storage) {
            const keys = await this.storage.getAllKeys('pinned:');
            await Promise.all(keys.map(k => this.storage.delete(k)));
        }
        
        if (this.debug) {
            console.log(`[PinnedCache] CLEAR (${size} aliases removed)`);
        }
    }
    
    /**
     * List all pinned aliases
     * @returns {Array} Array of alias info
     */
    listAll() {
        return Array.from(this.cache.entries()).map(([alias, entry]) => ({
            alias,
            loadedAt: entry.loadedAt,
            metadata: entry.metadata,
            age: Date.now() - entry.loadedAt
        }));
    }
    
    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getStats() {
        return {
            size: this.cache.size,
            aliases: Array.from(this.cache.keys())
        };
    }
    
    /**
     * Load pinned resources from persistent storage
     * @private
     */
    async _loadFromStorage() {
        if (!this.storage) return;
        
        try {
            const entries = await this.storage.getAll('pinned:');
            for (const [key, entry] of entries) {
                const alias = key.replace('pinned:', '');
                this.cache.set(alias, entry);
            }
            
            if (this.debug && entries.length > 0) {
                console.log(`[PinnedCache] Loaded ${entries.length} aliases from storage`);
            }
        } catch (e) {
            console.warn('[PinnedCache] Failed to load from storage:', e);
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PinnedCache;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.PinnedCache = PinnedCache;
}
