/**
 * ═══════════════════════════════════════════════════════════════
 * zBifrost Client - Global AJAX-like Request Handler v2.0
 * ═══════════════════════════════════════════════════════════════
 * 
 * Streamlined, event-driven WebSocket client for zCLI's zBifrost.
 * Inspired by jQuery's AJAX API and zDisplay's event architecture.
 * 
 * @version 2.0.0 (v1.5.4 refactor)
 * @author Gal Nachshon
 * @license MIT
 * 
 * ───────────────────────────────────────────────────────────────
 * Quick Start
 * ───────────────────────────────────────────────────────────────
 * 
 * // Simple CRUD operations (auto-connects on first request)
 * const users = await zBifrost.get('@.zSchema.users');
 * await zBifrost.post('@.zSchema.users', { name: 'John' });
 * await zBifrost.put('@.zSchema.users', { id: 1 }, { name: 'Jane' });
 * await zBifrost.delete('@.zSchema.users', { id: 1 });
 * 
 * // Auto-render UI
 * zBifrost.render.table(users, '#userList');
 * zBifrost.render.menu(['Home', 'About'], '#nav');
 * 
 * // Event-driven hooks
 * zBifrost.on('connected', () => console.log('Ready!'));
 * zBifrost.on('error', (err) => console.error(err));
 * 
 * // Manual connection (optional - auto-connects on first request)
 * await zBifrost.connect('ws://localhost:8765');
 * 
 * ───────────────────────────────────────────────────────────────
 */

(function(root) {
  'use strict';

  // ═══════════════════════════════════════════════════════════
  // EventBus - Central event system (like zDisplay's dispatch)
  // ═══════════════════════════════════════════════════════════
  
  class EventBus {
    constructor() {
      this.listeners = new Map();
    }
    
    on(event, handler) {
      if (!this.listeners.has(event)) {
        this.listeners.set(event, []);
      }
      this.listeners.get(event).push(handler);
    }
    
    off(event, handler) {
      if (!this.listeners.has(event)) return;
      const handlers = this.listeners.get(event);
      const index = handlers.indexOf(handler);
      if (index > -1) handlers.splice(index, 1);
    }
    
    emit(event, data) {
      if (!this.listeners.has(event)) return;
      this.listeners.get(event).forEach(handler => {
        try {
          handler(data);
        } catch (e) {
          console.error(`[EventBus] Error in ${event} handler:`, e);
        }
      });
    }
    
    once(event, handler) {
      const onceHandler = (data) => {
        handler(data);
        this.off(event, onceHandler);
      };
      this.on(event, onceHandler);
    }
  }

  // ═══════════════════════════════════════════════════════════
  // BifrostCore - Minimal WebSocket wrapper
  // ═══════════════════════════════════════════════════════════
  
  class BifrostCore {
    constructor() {
      this.ws = null;
      this.url = null;
      this.connected = false;
      this.requestId = 0;
      this.callbacks = new Map();
      this.reconnectAttempt = 0;
      this.reconnectDelay = 3000;
      this.maxReconnectAttempts = 10;
      this.eventBus = new EventBus();
      
      // Auto-connect flag
      this.autoConnecting = false;
    }
    
    async connect(url = 'ws://localhost:8765', options = {}) {
      if (this.connected) return;
      if (this.autoConnecting) {
        // Wait for existing connection attempt
        return new Promise((resolve) => {
          this.eventBus.once('connected', resolve);
        });
      }
      
      this.autoConnecting = true;
      this.url = url;
      this.reconnectDelay = options.reconnectDelay || 3000;
      this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
      
      return new Promise((resolve, reject) => {
        try {
          this.ws = new WebSocket(url);
          
          this.ws.onopen = () => {
            this.connected = true;
            this.reconnectAttempt = 0;
            this.autoConnecting = false;
            this.eventBus.emit('connected', { url });
            resolve();
          };
          
          this.ws.onmessage = (event) => {
            this._handleMessage(event.data);
          };
          
          this.ws.onclose = () => {
            this.connected = false;
            this.eventBus.emit('disconnected', { reason: 'closed' });
            this._attemptReconnect();
          };
          
          this.ws.onerror = (error) => {
            this.eventBus.emit('error', error);
            if (!this.connected) {
              this.autoConnecting = false;
              reject(error);
            }
          };
        } catch (error) {
          this.autoConnecting = false;
          reject(error);
        }
      });
    }
    
    async send(payload, timeout = 30000) {
      // Auto-connect if not connected
      if (!this.connected) {
        await this.connect();
      }

      return new Promise((resolve, reject) => {
        const requestId = this.requestId++;
        payload._requestId = requestId;

        const normalizedPayload = { ...payload };
        if (!normalizedPayload.event) {
          if (normalizedPayload.zKey || normalizedPayload.cmd) {
            normalizedPayload.event = 'dispatch';
          } else if (normalizedPayload.action) {
            normalizedPayload.event = normalizedPayload.action;
          }
        }

        // Set up timeout
        const timeoutId = setTimeout(() => {
          this.callbacks.delete(requestId);
          reject(new Error(`Request timeout after ${timeout}ms`));
        }, timeout);
        
        // Store callback
        this.callbacks.set(requestId, {
          resolve: (data) => {
            clearTimeout(timeoutId);
            resolve(data);
          },
          reject: (error) => {
            clearTimeout(timeoutId);
            reject(error);
          }
        });
        
        // Send request
        try {
          this.ws.send(JSON.stringify(normalizedPayload));
          this.eventBus.emit('request', normalizedPayload);
        } catch (error) {
          this.callbacks.delete(requestId);
          clearTimeout(timeoutId);
          reject(error);
        }
      });
    }
    
    _handleMessage(data) {
      try {
        const message = JSON.parse(data);
        this.eventBus.emit('message', message);
        
        // Handle connection info
        if (message.event === 'connection_info') {
          this.eventBus.emit('connection_info', message.data);
          return;
        }
        
        // Handle display events
        if (message.event === 'display') {
          this.eventBus.emit('display', message.data);
          return;
        }
        
        // Handle input requests
        if (message.event === 'input_request') {
          this.eventBus.emit('input_request', message.data);
          return;
        }
        
        // Handle broadcast
        if (message.event === 'broadcast') {
          this.eventBus.emit('broadcast', message.data);
          return;
        }
        
        // Handle response correlation
        const requestId = message._requestId;
        if (requestId !== undefined && this.callbacks.has(requestId)) {
          const callback = this.callbacks.get(requestId);
          this.callbacks.delete(requestId);
          
          if (message.error) {
            callback.reject(new Error(message.error));
          } else {
            callback.resolve(message.result);
          }
        }
      } catch (e) {
        console.error('[BifrostCore] Message parse error:', e);
      }
    }
    
    _attemptReconnect() {
      if (this.reconnectAttempt >= this.maxReconnectAttempts) {
        this.eventBus.emit('reconnect_failed', { attempts: this.reconnectAttempt });
        return;
      }
      
      this.reconnectAttempt++;
      this.eventBus.emit('reconnecting', { attempt: this.reconnectAttempt });
      
      setTimeout(() => {
        this.connect(this.url);
      }, this.reconnectDelay);
    }
    
    disconnect() {
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
      this.connected = false;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // CacheManager - Transparent caching (integrates with existing cache system)
  // ═══════════════════════════════════════════════════════════
  
  class CacheManager {
    constructor() {
      this.cache = null;
      this._initCache();
    }
    
    async _initCache() {
      try {
        if (typeof window !== 'undefined' && window.CacheOrchestrator) {
          this.cache = new window.CacheOrchestrator({
            debug: false,
            persistCache: true,
            maxSize: 100,
            defaultTTL: 3600000 // 1 hour
          });
        }
      } catch (e) {
        console.warn('[CacheManager] Cache system unavailable:', e);
      }
    }
    
    async get(key, type = 'system') {
      if (!this.cache) return null;
      return await this.cache.get(key, type);
    }
    
    async set(key, value, type = 'system', options = {}) {
      if (!this.cache) return;
      await this.cache.set(key, value, type, options);
    }
    
    async clear(type = null) {
      if (!this.cache) return;
      if (type) {
        await this.cache.clear(type);
      } else {
        await this.cache.clearAll();
      }
    }
    
    getStats() {
      if (!this.cache) return {};
      return this.cache.getStats();
    }
  }

  // ═══════════════════════════════════════════════════════════
  // RenderUtilities - Auto-render UI (like zDisplay)
  // ═══════════════════════════════════════════════════════════
  
  class RenderUtilities {
    constructor(core) {
      this.core = core;
    }
    
    table(data, selector, options = {}) {
      const container = typeof selector === 'string' 
        ? document.querySelector(selector) 
        : selector;
      
      if (!container) {
        console.error('[Render] Container not found:', selector);
        return;
      }
      
      if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = '<div class="zAlert zAlert-info">No data to display</div>';
        return;
      }
      
      const keys = Object.keys(data[0]);
      const thead = keys.map(k => `<th>${k}</th>`).join('');
      const tbody = data.map(row => 
        `<tr>${keys.map(k => `<td>${row[k] ?? ''}</td>`).join('')}</tr>`
      ).join('');
      
      container.innerHTML = `
        <table class="zTable">
          <thead><tr>${thead}</tr></thead>
          <tbody>${tbody}</tbody>
        </table>
      `;
    }
    
    menu(items, selector) {
      const container = typeof selector === 'string' 
        ? document.querySelector(selector) 
        : selector;
      
      if (!container) {
        console.error('[Render] Container not found:', selector);
        return;
      }
      
      const buttons = items.map(item => {
        const label = typeof item === 'string' ? item : item.label;
        const action = typeof item === 'string' ? null : item.action;
        const btnClass = typeof item === 'string' ? 'zBtn-primary' : (item.class || 'zBtn-primary');
        
        return `<button class="zoloButton ${btnClass}" data-action="${action || label}">${label}</button>`;
      }).join('');
      
      container.innerHTML = `<div class="zMenu">${buttons}</div>`;
      
      // Attach event handlers
      container.querySelectorAll('button').forEach((btn, idx) => {
        btn.onclick = () => {
          const item = items[idx];
          const action = typeof item === 'string' ? null : item.action;
          if (action && typeof action === 'function') {
            action();
          }
          this.core.eventBus.emit('menu_click', { label: btn.textContent, action: btn.dataset.action });
        };
      });
    }
    
    form(schema, selector, options = {}) {
      const container = typeof selector === 'string' 
        ? document.querySelector(selector) 
        : selector;
      
      if (!container) {
        console.error('[Render] Container not found:', selector);
        return;
      }
      
      const fields = Object.entries(schema).map(([key, config]) => {
        const type = config.type || 'text';
        const required = config.required ? 'required' : '';
        const label = config.label || key;
        
        return `
          <div class="zFormGroup">
            <label for="${key}">${label}${config.required ? ' *' : ''}</label>
            <input type="${type}" id="${key}" name="${key}" ${required} class="zInput" />
          </div>
        `;
      }).join('');
      
      container.innerHTML = `
        <form class="zForm">
          ${fields}
          <div class="zMenu">
            <button type="submit" class="zoloButton zBtn-primary">Submit</button>
            <button type="reset" class="zoloButton zBtn-secondary">Reset</button>
          </div>
        </form>
      `;
      
      // Attach submit handler
      const form = container.querySelector('form');
      form.onsubmit = (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        this.core.eventBus.emit('form_submit', data);
        if (options.onSubmit) options.onSubmit(data);
      };
    }
    
    message(text, type = 'info', selector = null) {
      const container = selector 
        ? (typeof selector === 'string' ? document.querySelector(selector) : selector)
        : document.body;
      
      const alert = document.createElement('div');
      alert.className = `zAlert zAlert-${type}`;
      alert.textContent = text;
      
      if (selector) {
        container.innerHTML = '';
        container.appendChild(alert);
      } else {
        container.insertBefore(alert, container.firstChild);
        setTimeout(() => alert.remove(), 5000);
      }
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Global zBifrost API - Main interface
  // ═══════════════════════════════════════════════════════════
  
  const core = new BifrostCore();
  const cacheManager = new CacheManager();
  const renderUtils = new RenderUtilities(core);
  
  // Load zTheme automatically using zTheme_loader
  // Note: zTheme_loader.js should be loaded before bifrost_client.js
  // Or it will auto-load on its own if available
  if (typeof window !== 'undefined' && typeof window.zThemeLoader !== 'undefined') {
    // zTheme loader is available, it will auto-load
    console.log('[BifrostClient] zTheme loader detected, theme will auto-load');
  } else {
    // Fallback: Try to load zTheme_loader.js dynamically
    if (typeof document !== 'undefined') {
      const loaderScript = document.createElement('script');
      loaderScript.src = '/zCLI/utils/zTheme/zTheme_loader.js';
      loaderScript.async = true;
      loaderScript.onerror = () => {
        console.warn('[BifrostClient] Could not load zTheme_loader.js - theme will not auto-load');
      };
      document.head.appendChild(loaderScript);
    }
  }
  
  const zBifrost = {
    // ═══════════════════════════════════════════════════════════
    // Core API
    // ═══════════════════════════════════════════════════════════
    
    /**
     * Connect to WebSocket server (optional - auto-connects on first request)
     */
    async connect(url = 'ws://localhost:8765', options = {}) {
      await core.connect(url, options);
    },
    
    /**
     * Disconnect from server
     */
    disconnect() {
      core.disconnect();
    },
    
    /**
     * Send raw request to server
     */
    async request(event, data = {}) {
      return await core.send({ event, action: data.action ?? event, ...data });
    },

    /**
     * Send with zKey (command dispatch)
     */
    async cmd(zKey, data = {}) {
      return await core.send({ event: 'dispatch', zKey, ...data });
    },
    
    // ═══════════════════════════════════════════════════════════
    // CRUD Shortcuts (like $.get, $.post)
    // ═══════════════════════════════════════════════════════════
    
    /**
     * Read data (GET equivalent)
     */
    async get(model, filters = null, options = {}) {
      // Check cache first
      if (!options.noCache) {
        const cacheKey = `${model}:${JSON.stringify(filters)}`;
        const cached = await cacheManager.get(cacheKey);
        if (cached) return cached;
      }
      
      const result = await core.send({
        event: 'dispatch',
        action: 'read',
        model,
        filters,
        ...options
      });
      
      // Cache result
      if (!options.noCache && result) {
        const cacheKey = `${model}:${JSON.stringify(filters)}`;
        await cacheManager.set(cacheKey, result, 'system', { ttl: 3600000 });
      }
      
      return result;
    },
    
    /**
     * Create data (POST equivalent)
     */
    async post(model, data) {
      return await core.send({ event: 'dispatch', action: 'create', model, data });
    },
    
    /**
     * Update data (PUT equivalent)
     */
    async put(model, filters, data) {
      return await core.send({ event: 'dispatch', action: 'update', model, filters, data });
    },
    
    /**
     * Delete data (DELETE equivalent)
     */
    async delete(model, filters) {
      return await core.send({ event: 'dispatch', action: 'delete', model, filters });
    },
    
    // ═══════════════════════════════════════════════════════════
    // Schema & Metadata
    // ═══════════════════════════════════════════════════════════
    
    /**
     * Get schema for model
     */
    async getSchema(model) {
      // Check cache first
      const cached = await cacheManager.get(model, 'system');
      if (cached) return cached;
      
      const schema = await core.send({ event: 'get_schema', action: 'get_schema', model });
      
      // Cache schema
      await cacheManager.set(model, schema, 'system', { 
        ttl: 3600000,
        metadata: { type: 'schema', model }
      });
      
      return schema;
    },
    
    /**
     * Discover available models
     */
    async discover() {
      return await core.send({ event: 'discover', action: 'discover' });
    },
    
    // ═══════════════════════════════════════════════════════════
    // Event System (like zDisplay)
    // ═══════════════════════════════════════════════════════════
    
    /**
     * Subscribe to event
     */
    on(event, handler) {
      core.eventBus.on(event, handler);
    },
    
    /**
     * Unsubscribe from event
     */
    off(event, handler) {
      core.eventBus.off(event, handler);
    },
    
    /**
     * Subscribe to event once
     */
    once(event, handler) {
      core.eventBus.once(event, handler);
    },
    
    /**
     * Emit custom event
     */
    emit(event, data) {
      core.eventBus.emit(event, data);
    },
    
    // ═══════════════════════════════════════════════════════════
    // Auto-Render Utilities
    // ═══════════════════════════════════════════════════════════
    
    render: {
      /**
       * Render data as table
       */
      table(data, selector, options) {
        renderUtils.table(data, selector, options);
      },
      
      /**
       * Render menu buttons
       */
      menu(items, selector) {
        renderUtils.menu(items, selector);
      },
      
      /**
       * Render form from schema
       */
      form(schema, selector, options) {
        renderUtils.form(schema, selector, options);
      },
      
      /**
       * Show message/alert
       */
      message(text, type, selector) {
        renderUtils.message(text, type, selector);
      }
    },
    
    // ═══════════════════════════════════════════════════════════
    // Cache Management
    // ═══════════════════════════════════════════════════════════
    
    cache: {
      /**
       * Get from cache
       */
      async get(key, type) {
        return await cacheManager.get(key, type);
      },
      
      /**
       * Set in cache
       */
      async set(key, value, type, options) {
        await cacheManager.set(key, value, type, options);
      },
      
      /**
       * Clear cache
       */
      async clear(type) {
        await cacheManager.clear(type);
      },
      
      /**
       * Get cache statistics
       */
      stats() {
        return cacheManager.getStats();
      },
      
      /**
       * Direct access to cache orchestrator
       */
      get orchestrator() {
        return cacheManager.cache;
      }
    },
    
    // ═══════════════════════════════════════════════════════════
    // Utilities
    // ═══════════════════════════════════════════════════════════
    
    /**
     * Check if connected
     */
    get connected() {
      return core.connected;
    },
    
    /**
     * Get current URL
     */
    get url() {
      return core.url;
    },
    
    /**
     * Get version
     */
    version: '2.0.0'
  };
  
  // Export to global scope
  root.zBifrost = zBifrost;
  
  // Also export BifrostClient for backward compatibility
  root.BifrostClient = class BifrostClient {
    constructor(url, options = {}) {
      console.warn('[BifrostClient] Legacy API - Use global zBifrost object instead');
      this.url = url;
      zBifrost.connect(url, options);
    }
    
    async connect() {
      await zBifrost.connect(this.url);
    }
    
    async send(payload) {
      const event = payload.event || payload.action || 'custom';
      return await zBifrost.request(event, payload);
    }
    
    async getSchema(model) {
      return await zBifrost.getSchema(model);
    }
    
    render(type, ...args) {
      if (zBifrost.render[type]) {
        zBifrost.render[type](...args);
      }
    }
    
    on(event, handler) {
      zBifrost.on(event, handler);
    }
    
    get connected() {
      return zBifrost.connected;
    }
    
    get cache() {
      return zBifrost.cache.orchestrator;
    }
    
    getAllCacheStats() {
      return zBifrost.cache.stats();
    }
    
    clearClientCache() {
      zBifrost.cache.clear();
    }
  };
  
  // Auto-connect on first interaction if console.log detected
  if (typeof window !== 'undefined' && window.console) {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║  zBifrost v2.0 - Global AJAX-like Request Handler            ║
║  ───────────────────────────────────────────────────────────  ║
║  Usage:                                                       ║
║    const users = await zBifrost.get('@.zSchema.users');      ║
║    zBifrost.render.table(users, '#userList');                ║
║                                                               ║
║  Events:                                                      ║
║    zBifrost.on('connected', () => console.log('Ready!'));    ║
║                                                               ║
║  Docs: /Documentation/zComm_GUIDE.md                         ║
╚═══════════════════════════════════════════════════════════════╝
    `);
  }
  
})(typeof self !== 'undefined' ? self : this);
