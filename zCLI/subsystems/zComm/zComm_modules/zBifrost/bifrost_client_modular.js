/**
 * ═══════════════════════════════════════════════════════════════
 * BifrostClient - Production JavaScript Client for zBifrost
 * ═══════════════════════════════════════════════════════════════
 * 
 * A production-ready WebSocket client for zCLI's zBifrost bridge.
 * Modular architecture with lazy loading and automatic zTheme integration.
 * 
 * @version 1.5.5
 * @author Gal Nachshon
 * @license MIT
 * 
 * ───────────────────────────────────────────────────────────────
 * Quick Start
 * ───────────────────────────────────────────────────────────────
 * 
 * // Via CDN (jsDelivr) - Now works with lazy loading!
 * <script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client_modular.js"></script>
 * 
 * // Initialize with hooks
 * const client = new BifrostClient('ws://localhost:8765', {
 *   autoTheme: true,  // Set to false to disable automatic zTheme loading
 *   autoReconnect: true,
 *   hooks: {
 *     onConnected: (info) => console.log('Connected!'),
 *     onDisconnected: (reason) => console.log('Disconnected:', reason),
 *     onMessage: (msg) => console.log('Message:', msg),
 *     onError: (error) => console.error('Error:', error),
 *     onBroadcast: (msg) => console.log('Broadcast:', msg),
 *     onDisplay: (data) => console.log('Display:', data),
 *     onInput: (request) => console.log('Input requested:', request)
 *   }
 * });
 * 
 * // Connect and use
 * await client.connect();
 * const users = await client.read('users');
 * client.renderTable(users, '#myContainer');
 * 
 * ───────────────────────────────────────────────────────────────
 * Lazy Loading Architecture
 * ───────────────────────────────────────────────────────────────
 * 
 * Modules are loaded dynamically only when needed:
 * - Logger/Hooks: Loaded immediately (lightweight)
 * - Connection: Loaded on connect()
 * - MessageHandler: Loaded on connect()
 * - Renderer: Loaded on first renderTable/renderMenu/etc call
 * - ThemeLoader: Loaded on connect() if autoTheme enabled
 * 
 * Benefits:
 * - CDN-friendly (no import resolution at load time)
 * - Progressive loading (only load what you use)
 * - Stays modular (source files remain separate)
 * 
 * ───────────────────────────────────────────────────────────────
 */

(function(root, factory) {
  // UMD (Universal Module Definition) for maximum compatibility
  if (typeof define === 'function' && define.amd) {
    // AMD
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS
    module.exports = factory();
  } else {
    // Browser globals
    root.BifrostClient = factory();
  }
}(typeof self !== 'undefined' ? self : this, function() {
  'use strict';

  /**
   * Get base URL for module imports
   */
  function getBaseUrl() {
    if (typeof document !== 'undefined') {
      const scripts = document.querySelectorAll('script[src*="bifrost_client"]');
      if (scripts.length > 0) {
        const src = scripts[scripts.length - 1].src;
        return src.substring(0, src.lastIndexOf('/') + 1);
      }
    }
    return './';
  }

  /**
   * BifrostClient - Main class for WebSocket communication with zBifrost
   */
  class BifrostClient {
    /**
     * Create a new BifrostClient instance
     * @param {string} url - WebSocket server URL (e.g., 'ws://localhost:8765')
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoTheme - Auto-load zTheme CSS (default: true, set to false for custom styling)
     * @param {boolean} options.autoReconnect - Auto-reconnect on disconnect (default: true)
     * @param {number} options.reconnectDelay - Delay between reconnect attempts in ms (default: 3000)
     * @param {number} options.timeout - Request timeout in ms (default: 30000)
     * @param {boolean} options.debug - Enable debug logging (default: false)
     * @param {string} options.token - Authentication token (optional)
     * @param {Object} options.hooks - Event hooks for customization
     */
    constructor(url = 'ws://localhost:8765', options = {}) {
      this.url = url;
      this.options = {
        autoTheme: options.autoTheme !== false, // Default true
        autoReconnect: options.autoReconnect !== false, // Default true
        reconnectDelay: options.reconnectDelay || 3000,
        timeout: options.timeout || 30000,
        debug: options.debug || false,
        token: options.token || null,
        hooks: options.hooks || {}
      };

      // Module cache (lazy loaded)
      this._modules = {};
      this._baseUrl = getBaseUrl();
      
      // Pre-initialize lightweight modules synchronously
      this._initLightweightModules();
    }

    /**
     * Initialize lightweight modules that don't require imports
     */
    _initLightweightModules() {
      // Inline Logger (lightweight, no dependencies)
      this.logger = {
        debug: this.options.debug,
        log: (message, ...args) => {
          if (this.logger.debug) {
            console.log(`[BifrostClient] ${message}`, ...args);
          }
        },
        enable: () => {
          this.logger.debug = true;
        },
        disable: () => {
          this.logger.debug = false;
        },
        isEnabled: () => {
          return this.logger.debug;
        }
      };

      // Inline HookManager (lightweight, no dependencies)
      this.hooks = {
        hooks: this.options.hooks || {},
        call: (hookName, ...args) => {
          const hook = this.hooks.hooks[hookName];
          if (typeof hook === 'function') {
            try {
              return hook(...args);
            } catch (error) {
              console.error(`[BifrostClient] Error in ${hookName} hook:`, error);
            }
          }
        },
        has: (hookName) => {
          return typeof this.hooks.hooks[hookName] === 'function';
        },
        register: (hookName, fn) => {
          if (typeof fn === 'function') {
            this.hooks.hooks[hookName] = fn;
          }
        },
        unregister: (hookName) => {
          delete this.hooks.hooks[hookName];
        },
        list: () => Object.keys(this.hooks.hooks)
      };

      this.logger.log('BifrostClient initialized', { url: this.url, options: this.options });
    }

    /**
     * Lazy load a module
     * @param {string} moduleName - Name of the module (connection, message_handler, renderer, theme_loader)
     * @returns {Promise<any>}
     */
    async _loadModule(moduleName) {
      if (this._modules[moduleName]) {
        return this._modules[moduleName];
      }

      const modulePath = `${this._baseUrl}_modules/${moduleName}.js`;
      this.logger.log(`Loading module: ${moduleName} from ${modulePath}`);

      try {
        const module = await import(modulePath);
        this._modules[moduleName] = module;
        return module;
      } catch (error) {
        this.logger.error(`Failed to load module ${moduleName}:`, error);
        throw new Error(`Failed to load BifrostClient module: ${moduleName}`);
      }
    }

    /**
     * Ensure connection module is loaded
     */
    async _ensureConnection() {
      if (!this.connection) {
        const { BifrostConnection } = await this._loadModule('connection');
        this.connection = new BifrostConnection(
          this.url,
          this.options,
          this.logger,
          this.hooks
        );
      }
      return this.connection;
    }

    /**
     * Ensure message handler module is loaded
     */
    async _ensureMessageHandler() {
      if (!this.messageHandler) {
        const { MessageHandler } = await this._loadModule('message_handler');
        this.messageHandler = new MessageHandler(this.logger, this.hooks);
        this.messageHandler.setTimeout(this.options.timeout);
      }
      return this.messageHandler;
    }

    /**
     * Ensure renderer module is loaded
     */
    async _ensureRenderer() {
      if (!this.renderer) {
        const { Renderer } = await this._loadModule('renderer');
        this.renderer = new Renderer(this.logger);
      }
      return this.renderer;
    }

    /**
     * Ensure theme loader module is loaded
     */
    async _ensureThemeLoader() {
      if (!this.themeLoader) {
        const { ThemeLoader } = await this._loadModule('theme_loader');
        this.themeLoader = new ThemeLoader(this.logger);
      }
      return this.themeLoader;
    }

    // ═══════════════════════════════════════════════════════════
    // Connection Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
      // Load required modules
      await this._ensureConnection();
      await this._ensureMessageHandler();
      
      await this.connection.connect();
      
      // Set up message handler
      this.connection.onMessage((event) => {
        this.messageHandler.handleMessage(event.data);
      });

      // Auto-load theme if enabled
      if (this.options.autoTheme) {
        await this._ensureThemeLoader();
        if (!this.themeLoader.isLoaded()) {
          this.themeLoader.load();
        }
      }
    }

    /**
     * Disconnect from the server
     */
    disconnect() {
      if (this.connection) {
        this.connection.disconnect();
      }
    }

    /**
     * Check if connected
     * @returns {boolean}
     */
    isConnected() {
      return this.connection ? this.connection.isConnected() : false;
    }

    // ═══════════════════════════════════════════════════════════
    // Message Sending
    // ═══════════════════════════════════════════════════════════

    /**
     * Send a message and wait for response
     * @param {Object} payload - Message payload
     * @param {number} timeout - Custom timeout (optional)
     * @returns {Promise<any>}
     */
    async send(payload, timeout = null) {
      if (!this.isConnected()) {
        throw new Error('Not connected to server. Call connect() first.');
      }

      await this._ensureMessageHandler();
      
      return this.messageHandler.send(
        payload,
        (msg) => this.connection.send(msg),
        timeout
      );
    }

    /**
     * Send input response to server
     * @param {string} requestId - Request ID from input event
     * @param {any} value - Input value
     */
    sendInputResponse(requestId, value) {
      if (!this.isConnected()) {
        this.logger.log('❌ Cannot send input response: not connected');
        return;
      }

      // Use new event protocol
      const message = JSON.stringify({
        event: 'input_response',
        requestId: requestId,
        value: value
      });
      
      this.connection.send(message);
    }

    // ═══════════════════════════════════════════════════════════
    // CRUD Operations
    // ═══════════════════════════════════════════════════════════

    /**
     * Create a new record
     * @param {string} model - Table/model name
     * @param {Object} data - Field values
     * @returns {Promise<Object>}
     */
    async create(model, data) {
      return this.send({
        event: 'dispatch',
        zKey: `^Create ${model}`,
        model: model,
        data: data
      });
    }

    /**
     * Read records
     * @param {string} model - Table/model name
     * @param {Object} filters - WHERE conditions (optional)
     * @param {Object} options - Additional options (fields, order_by, limit, offset)
     * @returns {Promise<Array>}
     */
    async read(model, filters = null, options = {}) {
      const payload = {
        event: 'dispatch',
        zKey: `^List ${model}`,
        model: model
      };

      if (filters) payload.where = filters;
      if (options.fields) payload.fields = options.fields;
      if (options.order_by) payload.order_by = options.order_by;
      if (options.limit !== undefined) payload.limit = options.limit;
      if (options.offset !== undefined) payload.offset = options.offset;

      return this.send(payload);
    }

    /**
     * Update record(s)
     * @param {string} model - Table/model name
     * @param {Object|number} filters - WHERE conditions or ID
     * @param {Object} data - Fields to update
     * @returns {Promise<Object>}
     */
    async update(model, filters, data) {
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        event: 'dispatch',
        zKey: `^Update ${model}`,
        model: model,
        where: filters,
        data: data
      });
    }

    /**
     * Delete record(s)
     * @param {string} model - Table/model name
     * @param {Object|number} filters - WHERE conditions or ID
     * @returns {Promise<Object>}
     */
    async delete(model, filters) {
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        event: 'dispatch',
        zKey: `^Delete ${model}`,
        model: model,
        where: filters
      });
    }

    // ═══════════════════════════════════════════════════════════
    // zCLI Operations
    // ═══════════════════════════════════════════════════════════

    /**
     * Execute a zFunc command
     * @param {string} command - zFunc command string
     * @returns {Promise<any>}
     */
    async zFunc(command) {
      return this.send({
        zKey: 'zFunc',
        zHorizontal: command
      });
    }

    /**
     * Navigate to a zLink path
     * @param {string} path - zLink navigation path
     * @returns {Promise<any>}
     */
    async zLink(path) {
      return this.send({
        zKey: 'zLink',
        zHorizontal: `zLink(${path})`
      });
    }

    /**
     * Execute a zOpen command
     * @param {string} command - zOpen command string
     * @returns {Promise<any>}
     */
    async zOpen(command) {
      return this.send({
        zKey: 'zOpen',
        zHorizontal: `zOpen(${command})`
      });
    }

    // ═══════════════════════════════════════════════════════════
    // zTheme Integration
    // ═══════════════════════════════════════════════════════════

    /**
     * Load zTheme CSS files (if autoTheme is disabled)
     * @param {string} baseUrl - Base URL for CSS files (optional, auto-detected)
     */
    async loadTheme(baseUrl = null) {
      await this._ensureThemeLoader();
      this.themeLoader.load(baseUrl);
    }

    // ═══════════════════════════════════════════════════════════
    // Auto-Rendering Methods (Using zTheme)
    // ═══════════════════════════════════════════════════════════

    /**
     * Render data as a table with zTheme styling
     * @param {Array} data - Array of objects to render
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Object} options - Rendering options
     */
    async renderTable(data, container, options = {}) {
      await this._ensureRenderer();
      this.renderer.renderTable(data, container, options);
    }

    /**
     * Render a menu with buttons
     * @param {Array} items - Array of menu items {label, action, icon, variant}
     * @param {string|HTMLElement} container - Container selector or element
     */
    async renderMenu(items, container) {
      await this._ensureRenderer();
      this.renderer.renderMenu(items, container);
    }

    /**
     * Render a form with zTheme styling
     * @param {Array} fields - Array of field definitions
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Function} onSubmit - Submit handler
     */
    async renderForm(fields, container, onSubmit) {
      await this._ensureRenderer();
      this.renderer.renderForm(fields, container, onSubmit);
    }

    /**
     * Render a message/alert
     * @param {string} text - Message text
     * @param {string} type - Message type (success, error, warning, info)
     * @param {string|HTMLElement} container - Container selector or element
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    async renderMessage(text, type = 'info', container, duration = 5000) {
      await this._ensureRenderer();
      this.renderer.renderMessage(text, type, container, duration);
    }

    // ═══════════════════════════════════════════════════════════
    // Hook Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Register a new hook at runtime
     * @param {string} hookName - Name of the hook
     * @param {Function} fn - Hook function
     */
    registerHook(hookName, fn) {
      this.hooks.register(hookName, fn);
    }

    /**
     * Unregister a hook
     * @param {string} hookName - Name of the hook
     */
    unregisterHook(hookName) {
      this.hooks.unregister(hookName);
    }

    /**
     * List all registered hooks
     * @returns {Array<string>}
     */
    listHooks() {
      return this.hooks.list();
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Export
  // ═══════════════════════════════════════════════════════════

  return BifrostClient;
}));
