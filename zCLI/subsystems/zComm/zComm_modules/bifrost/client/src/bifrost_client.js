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
 * // Swiper-Style Elegance (One declaration, everything happens automatically):
 * const client = new BifrostClient('ws://localhost:8765', {
 *   autoConnect: true,        // Auto-connect on instantiation
 *   zTheme: true,             // Enable zTheme CSS & rendering
 *   // targetElement: 'zVaF', // Optional: default is 'zVaF' (zView and Function)
 *   autoRequest: 'show_hello',// Auto-send on connect
 *   onConnected: (info) => console.log('✅ Connected!', info)
 * });
 * 
 * // Traditional (More control):
 * const client = new BifrostClient('ws://localhost:8765', {
 *   zTheme: true,
 *   hooks: {
 *     onConnected: (info) => console.log('Connected!'),
 *     onDisconnected: (reason) => console.log('Disconnected:', reason),
 *     onMessage: (msg) => console.log('Message:', msg),
 *     onError: (error) => console.error('Error:', error)
 *   }
 * });
 * await client.connect();
 * client.send({event: 'my_event'});
 * const users = await client.read('users');
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
 * - ThemeLoader: Loaded on connect() if zTheme enabled
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
     * @param {boolean} options.autoConnect - Auto-connect on instantiation (default: false)
     * @param {boolean} options.zTheme - Enable zTheme CSS & auto-rendering (default: true)
     * @param {string} options.targetElement - Target DOM selector for rendering (default: 'zVaF')
     * @param {string|Object} options.autoRequest - Auto-send request on connect (event name or full request object)
     * @param {boolean} options.autoReconnect - Auto-reconnect on disconnect (default: true)
     * @param {number} options.reconnectDelay - Delay between reconnect attempts in ms (default: 3000)
     * @param {number} options.timeout - Request timeout in ms (default: 30000)
     * @param {boolean} options.debug - Enable debug logging (default: false)
     * @param {string} options.token - Authentication token (optional)
     * @param {Object} options.hooks - Event hooks for customization
     */
    constructor(url = 'ws://localhost:8765', options = {}) {
      // Validate URL
      if (typeof url !== 'string' || url.trim() === '') {
        throw new Error('BifrostClient: URL must be a non-empty string');
      }
      if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
        throw new Error('BifrostClient: URL must start with ws:// or wss://');
      }

      this.url = url;

      // Validate and set options
      const reconnectDelay = options.reconnectDelay || 3000;
      const timeout = options.timeout || 30000;

      if (typeof reconnectDelay !== 'number' || reconnectDelay <= 0) {
        throw new Error('BifrostClient: reconnectDelay must be a positive number');
      }
      if (typeof timeout !== 'number' || timeout <= 0) {
        throw new Error('BifrostClient: timeout must be a positive number');
      }

      this.options = {
        autoConnect: options.autoConnect || false, // Default false
        zTheme: options.zTheme !== false && options.autoTheme !== false, // Support both names, default true
        targetElement: options.targetElement || 'zVaF', // Default zCLI container
        autoRequest: options.autoRequest || null, // Auto-send on connect
        autoReconnect: options.autoReconnect !== false, // Default true
        reconnectDelay: reconnectDelay,
        timeout: timeout,
        debug: options.debug || false,
        token: options.token || null,
        hooks: options.hooks || {}
      };

      // Module cache (lazy loaded)
      this._modules = {};
      this._baseUrl = getBaseUrl();
      
      // Pre-initialize lightweight modules synchronously
      this._initLightweightModules();
      
      // Auto-connect if requested (Swiper-style elegance!)
      if (this.options.autoConnect) {
        this.connect().catch(err => {
          this.logger.error('Auto-connect failed:', err);
          this.hooks.call('onError', { type: 'autoconnect_failed', error: err });
        });
      }
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
        error: (message, ...args) => {
          // Always show errors, regardless of debug mode
          console.error(`[BifrostClient ERROR] ${message}`, ...args);
        },
        warn: (message, ...args) => {
          if (this.logger.debug) {
            console.warn(`[BifrostClient WARN] ${message}`, ...args);
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
        errorHandler: null, // Set by _initErrorDisplay()
        call: (hookName, ...args) => {
          const hook = this.hooks.hooks[hookName];
          if (typeof hook === 'function') {
            try {
              return hook(...args);
            } catch (error) {
              // Log to console
              console.error(`[BifrostClient] Error in ${hookName} hook:`, error);
              
              // Log via logger
              this.logger.error(`Error in ${hookName} hook:`, error);
              
              // Display in UI if error handler is set
              if (this.hooks.errorHandler) {
                try {
                  this.hooks.errorHandler({
                    type: 'hook_error',
                    hookName,
                    error,
                    message: error.message,
                    stack: error.stack
                  });
                } catch (displayError) {
                  console.error('[BifrostClient] Error handler itself failed:', displayError);
                }
              }
              
              // Call onError hook if it exists and isn't the one that failed
              if (hookName !== 'onError' && this.hooks.hooks.onError) {
                try {
                  this.hooks.hooks.onError(error);
                } catch (onErrorError) {
                  console.error('[BifrostClient] onError hook failed:', onErrorError);
                }
              }
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

      // Register default widget hooks (Week 4.2)
      this._registerDefaultWidgetHooks();

      this.logger.log('BifrostClient initialized', { url: this.url, options: this.options });
    }

    /**
     * Register default hooks for widget events
     * 
     * NOTE: Progress bar and spinner hooks removed as the renderer methods
     * (renderProgressBar, updateProgress, removeProgress, renderSpinner, removeSpinner)
     * are not yet implemented. These will be added back in Task 9 when we implement
     * and test the auto-rendering methods.
     * 
     * For now, users can implement these hooks manually if needed.
     */
    _registerDefaultWidgetHooks() {
      // Placeholder for future widget hooks
      // Will be implemented in Task 9: Test Auto-Rendering Methods
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

      // Determine module subfolder based on module type
      const coreModules = ['connection', 'hooks', 'logger', 'message_handler', 'error_display'];
      const renderingModules = ['renderer', 'theme_loader', 'zdisplay_renderer'];
      
      let subfolder = '';
      if (coreModules.includes(moduleName)) {
        subfolder = 'core/';
      } else if (renderingModules.includes(moduleName)) {
        subfolder = 'rendering/';
      }

      const modulePath = `${this._baseUrl}${subfolder}${moduleName}.js`;
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
     * Ensure zDisplay renderer module is loaded
     */
    async _ensureZDisplayRenderer() {
      if (!this.zDisplayRenderer) {
        const { ZDisplayRenderer } = await this._loadModule('zdisplay_renderer');
        this.zDisplayRenderer = new ZDisplayRenderer(this.logger);
        
        // Set target element from options (strip # prefix if present)
        const targetElement = this.options.targetElement || '#zui-content';
        this.zDisplayRenderer.defaultZone = targetElement.startsWith('#') 
          ? targetElement.substring(1) 
          : targetElement;
        
        this.logger.log(`[BifrostClient] zDisplay target set to: ${this.zDisplayRenderer.defaultZone}`);
        
        // Register default onDisplay hook if not already set
        if (!this.hooks.has('onDisplay')) {
          this.hooks.register('onDisplay', (event) => {
            this.logger.log('[BifrostClient] Auto-rendering zDisplay event:', event);
            this.zDisplayRenderer.render(event);
          });
          this.logger.log('[BifrostClient] Registered default onDisplay hook for auto-rendering');
        }
      }
      return this.zDisplayRenderer;
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
     * Initialize error display (if not disabled)
     */
    async _ensureErrorDisplay() {
      if (this.options.showErrors === false) return; // Allow disabling
      
      if (!this.errorDisplay) {
        const { ErrorDisplay } = await this._loadModule('error_display');
        this.errorDisplay = new ErrorDisplay({
          position: this.options.errorPosition || 'top-right',
          maxErrors: this.options.maxErrors || 5,
          autoDismiss: this.options.autoDismiss || 10000
        });
        
        // Set error handler for hooks
        this.hooks.errorHandler = (errorInfo) => {
          this.errorDisplay.show(errorInfo);
        };
        
        this.logger.log('Error display initialized');
      }
      return this.errorDisplay;
    }

    /**
     * Check if running on file:// protocol (which doesn't support ES6 module imports)
     * @private
     */
    _isFileProtocol() {
      return typeof window !== 'undefined' && window.location.protocol === 'file:';
    }

    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
      // Skip module loading for file:// protocol (ES6 imports not supported)
      const isFileProtocol = this._isFileProtocol();
      
      if (isFileProtocol) {
        this.logger.log('[BifrostClient] Running on file:// protocol - skipping module loading');
        this.logger.log('[BifrostClient] Error display and auto-rendering disabled (use HTTP server to enable)');
      }
      
      // Initialize error display (for visual error boundaries) - skip on file://
      if (!isFileProtocol && this.options.showErrors !== false) {
        try {
          await this._ensureErrorDisplay();
        } catch (error) {
          this.logger.warn('[BifrostClient] Error display failed to load:', error.message);
        }
      }
      
      // Initialize zDisplay renderer (for auto-rendering zDisplay events) - skip on file://
      if (!isFileProtocol) {
        try {
          await this._ensureZDisplayRenderer();
        } catch (error) {
          this.logger.warn('[BifrostClient] zDisplay renderer failed to load:', error.message);
        }
      }
      
      // Load theme BEFORE connecting to prevent FOUC (Flash of Unstyled Content)
      if (this.options.zTheme && !isFileProtocol) {
        try {
          await this._ensureThemeLoader();
          if (!this.themeLoader.isLoaded()) {
            this.themeLoader.load();
          }
        } catch (error) {
          this.logger.warn('[BifrostClient] Theme loader failed to load:', error.message);
        }
      }

      // Load required modules
      await this._ensureConnection();
      await this._ensureMessageHandler();
      
      await this.connection.connect();
      
      // Set up message handler
      this.connection.onMessage((event) => {
        this.messageHandler.handleMessage(event.data);
      });
      
      // Auto-send request if specified (Swiper-style elegance!)
      if (this.options.autoRequest) {
        const request = typeof this.options.autoRequest === 'string'
          ? { event: this.options.autoRequest }
          : this.options.autoRequest;
        
        this.logger.log('📤 Auto-sending request:', request);
        this.send(request);
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
     * Load zTheme CSS files (manual override if zTheme is disabled)
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
