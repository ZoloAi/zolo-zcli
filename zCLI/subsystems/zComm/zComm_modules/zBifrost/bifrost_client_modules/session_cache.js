/**
 * ═══════════════════════════════════════════════════════════════
 * SessionCache - Active session data (in-memory only)
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mirrors zLoader's schema_cache for active session data.
 * Data is lost on page refresh (intentional for security/freshness).
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

class SessionCache {
    constructor(options = {}) {
        this.cache = new Map();
        this.debug = options.debug || false;
    }
    
    /**
     * Set value in session cache
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     */
    set(key, value) {
        this.cache.set(key, {
            data: value,
            setAt: Date.now()
        });
        
        if (this.debug) {
            console.log(`[SessionCache] SET ${key}`);
        }
    }
    
    /**
     * Get value from session cache
     * @param {string} key - Cache key
     * @returns {any} Cached value or null
     */
    get(key) {
        const entry = this.cache.get(key);
        if (this.debug && entry) {
            console.log(`[SessionCache] HIT ${key}`);
        }
        return entry ? entry.data : null;
    }
    
    /**
     * Check if key exists
     * @param {string} key - Cache key
     * @returns {boolean} True if key exists
     */
    has(key) {
        return this.cache.has(key);
    }
    
    /**
     * Delete specific key
     * @param {string} key - Cache key
     */
    delete(key) {
        this.cache.delete(key);
        if (this.debug) {
            console.log(`[SessionCache] DELETE ${key}`);
        }
    }
    
    /**
     * Clear all session data
     */
    clear() {
        const size = this.cache.size;
        this.cache.clear();
        if (this.debug) {
            console.log(`[SessionCache] CLEAR (${size} entries removed)`);
        }
    }
    
    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionCache;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.SessionCache = SessionCache;
}
