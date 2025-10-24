/**
 * ═══════════════════════════════════════════════════════════════
 * Storage Adapters - IndexedDB with localStorage fallback
 * ═══════════════════════════════════════════════════════════════
 * 
 * Provides persistent storage for BifrostClient cache system.
 * Uses IndexedDB (async, 50MB+) with graceful fallback to localStorage.
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 */

/**
 * IndexedDB Storage Adapter (Primary)
 * - Async API (non-blocking)
 * - Large capacity (50MB+, browser dependent)
 * - Structured data with indexing
 */
class IndexedDBStorage {
    /**
     * Initialize IndexedDB connection
     * @param {string} dbName - Database name
     * @param {number} version - Database version
     * @returns {Promise<IndexedDBStorage>} Initialized storage adapter
     */
    static async init(dbName, version) {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(dbName, version);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                const adapter = new IndexedDBStorage(request.result);
                resolve(adapter);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('cache')) {
                    db.createObjectStore('cache');
                }
            };
        });
    }
    
    constructor(db) {
        this.db = db;
    }
    
    /**
     * Get value from IndexedDB
     * @param {string} key - Cache key
     * @returns {Promise<any>} Cached value or undefined
     */
    async get(key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cache'], 'readonly');
            const store = transaction.objectStore('cache');
            const request = store.get(key);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    /**
     * Set value in IndexedDB
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     * @returns {Promise<void>}
     */
    async set(key, value) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            const request = store.put(value, key);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
    
    /**
     * Delete value from IndexedDB
     * @param {string} key - Cache key
     * @returns {Promise<void>}
     */
    async delete(key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            const request = store.delete(key);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
    
    /**
     * Get all keys matching prefix
     * @param {string} prefix - Key prefix to match
     * @returns {Promise<string[]>} Array of matching keys
     */
    async getAllKeys(prefix = '') {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['cache'], 'readonly');
            const store = transaction.objectStore('cache');
            const request = store.getAllKeys();
            
            request.onsuccess = () => {
                const keys = request.result.filter(k => k.startsWith(prefix));
                resolve(keys);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    /**
     * Get all entries matching prefix
     * @param {string} prefix - Key prefix to match
     * @returns {Promise<Array<[string, any]>>} Array of [key, value] tuples
     */
    async getAll(prefix = '') {
        const keys = await this.getAllKeys(prefix);
        const entries = await Promise.all(keys.map(async k => [k, await this.get(k)]));
        return entries;
    }
}

/**
 * LocalStorage Fallback Adapter
 * - Sync API (blocking)
 * - Limited capacity (5-10MB)
 * - Simple key-value storage
 */
class LocalStorageAdapter {
    /**
     * Get value from localStorage
     * @param {string} key - Cache key
     * @returns {Promise<any>} Cached value or null
     */
    async get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('[LocalStorage] Parse error:', e);
            return null;
        }
    }
    
    /**
     * Set value in localStorage
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     * @returns {Promise<void>}
     */
    async set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            // Quota exceeded or other error
            console.warn('[LocalStorage] Quota exceeded or error:', e);
        }
    }
    
    /**
     * Delete value from localStorage
     * @param {string} key - Cache key
     * @returns {Promise<void>}
     */
    async delete(key) {
        localStorage.removeItem(key);
    }
    
    /**
     * Get all keys matching prefix
     * @param {string} prefix - Key prefix to match
     * @returns {Promise<string[]>} Array of matching keys
     */
    async getAllKeys(prefix = '') {
        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(prefix)) {
                keys.push(key);
            }
        }
        return keys;
    }
    
    /**
     * Get all entries matching prefix
     * @param {string} prefix - Key prefix to match
     * @returns {Promise<Array<[string, any]>>} Array of [key, value] tuples
     */
    async getAll(prefix = '') {
        const keys = await this.getAllKeys(prefix);
        const entries = await Promise.all(keys.map(async k => [k, await this.get(k)]));
        return entries;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { IndexedDBStorage, LocalStorageAdapter };
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.IndexedDBStorage = IndexedDBStorage;
    window.LocalStorageAdapter = LocalStorageAdapter;
}
