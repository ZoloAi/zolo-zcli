/**
 * ═══════════════════════════════════════════════════════════════
 * BifrostClient - Production JavaScript Client for zBifrost
 * ═══════════════════════════════════════════════════════════════
 * 
 * A production-ready WebSocket client for zCLI's zBifrost bridge.
 * Modular architecture with automatic zTheme integration.
 * 
 * @version 1.5.4
 * @author Gal Nachshon
 * @license MIT
 * 
 * ───────────────────────────────────────────────────────────────
 * Quick Start
 * ───────────────────────────────────────────────────────────────
 * 
 * // Via CDN (jsDelivr)
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
 * Custom Bifrost Events (Without zTheme)
 * ───────────────────────────────────────────────────────────────
 * 
 * // Disable autoTheme and handle rendering yourself
 * const client = new BifrostClient('ws://localhost:8765', {
 *   autoTheme: false,  // No automatic CSS loading
 *   hooks: {
 *     onDisplay: (data) => {
 *       // Custom rendering logic
 *       if (Array.isArray(data)) {
 *         myCustomTableRenderer(data);
 *       }
 *     },
 *     onMessage: (msg) => {
 *       // Custom message handling
 *       if (msg.type === 'notification') {
 *         myCustomNotificationSystem(msg);
 *       }
 *     }
 *   }
 * });
 * 
 * ───────────────────────────────────────────────────────────────
 */

import { BifrostConnection } from './_modules/connection.js';
import { MessageHandler } from './_modules/message_handler.js';
import { Renderer } from './_modules/renderer.js';
import { ThemeLoader } from './_modules/theme_loader.js';
import { Logger } from './_modules/logger.js';
import { HookManager } from './_modules/hooks.js';

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

      // Initialize modules
      this.logger = new Logger(this.options.debug);
      this.hooks = new HookManager(this.options.hooks);
      this.connection = new BifrostConnection(url, this.options, this.logger, this.hooks);
      this.messageHandler = new MessageHandler(this.logger, this.hooks);
      this.renderer = new Renderer(this.logger);
      this.themeLoader = new ThemeLoader(this.logger);

      // Set timeout for message handler
      this.messageHandler.setTimeout(this.options.timeout);

      this.logger.log('BifrostClient initialized', { url, options: this.options });
    }

    // ═══════════════════════════════════════════════════════════
    // Connection Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
      await this.connection.connect();
      
      // Set up message handler
      this.connection.onMessage((event) => {
        this.messageHandler.handleMessage(event.data);
      });

      // Auto-load theme if enabled
      if (this.options.autoTheme && !this.themeLoader.isLoaded()) {
        this.themeLoader.load();
      }
    }

    /**
     * Disconnect from the server
     */
    disconnect() {
      this.connection.disconnect();
    }

    /**
     * Check if connected
     * @returns {boolean}
     */
    isConnected() {
      return this.connection.isConnected();
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
    loadTheme(baseUrl = null) {
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
    renderTable(data, container, options = {}) {
      this.renderer.renderTable(data, container, options);
    }

    /**
     * Render a menu with buttons
     * @param {Array} items - Array of menu items {label, action, icon, variant}
     * @param {string|HTMLElement} container - Container selector or element
     */
    renderMenu(items, container) {
      this.renderer.renderMenu(items, container);
    }

    /**
     * Render a form with zTheme styling
     * @param {Array} fields - Array of field definitions
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Function} onSubmit - Submit handler
     */
    renderForm(fields, container, onSubmit) {
      this.renderer.renderForm(fields, container, onSubmit);
    }

    /**
     * Render a message/alert
     * @param {string} text - Message text
     * @param {string} type - Message type (success, error, warning, info)
     * @param {string|HTMLElement} container - Container selector or element
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    renderMessage(text, type = 'info', container, duration = 5000) {
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

