/**
 * ═══════════════════════════════════════════════════════════════
 * BifrostClient - Production JavaScript Client for zBifrost
 * ═══════════════════════════════════════════════════════════════
 * 
 * A production-ready WebSocket client for zCLI's zBifrost bridge.
 * Handles all zBifrost protocol events with automatic zTheme integration.
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
 * <script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client.js"></script>
 * 
 * // Initialize with hooks
 * const client = new BifrostClient('ws://localhost:8765', {
 *   autoTheme: true,
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
   * BifrostClient - Main class for WebSocket communication with zBifrost
   */
  class BifrostClient {
    /**
     * Create a new BifrostClient instance
     * @param {string} url - WebSocket server URL (e.g., 'ws://localhost:8765')
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoTheme - Auto-load zTheme CSS (default: true)
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

      // WebSocket state
      this.ws = null;
      this.connected = false;
      this.reconnectAttempt = 0;

      // Request/response correlation
      this.requestId = 0;
      this.callbacks = new Map();

      // Theme loading state
      this.themeLoaded = false;

      // Client-side caches (v1.5.4+)
      this.schemaCache = new Map();  // Cache schemas from server
      this.serverInfo = null;         // Server connection info

      // Log initialization
      this._log('BifrostClient initialized', { url, options: this.options });
    }

    // ═══════════════════════════════════════════════════════════
    // Connection Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
      return new Promise((resolve, reject) => {
        this._log('Attempting to connect...', this.url);
        this._callHook('onConnecting', this.url);

        // Build connection URL with token if provided
        const connectUrl = this.options.token 
          ? `${this.url}?token=${this.options.token}` 
          : this.url;

        try {
          this.ws = new WebSocket(connectUrl);

          this.ws.onopen = () => {
            this.connected = true;
            this.reconnectAttempt = 0;
            this._log('✅ Connected to server');
            
            const info = {
              url: this.ws.url,
              protocol: this.ws.protocol,
              readyState: this.ws.readyState
            };
            
            this._callHook('onConnected', info);

            // Auto-load theme if enabled
            if (this.options.autoTheme && !this.themeLoaded) {
              this.loadTheme();
            }

            resolve();
          };

          this.ws.onmessage = (event) => {
            this._handleMessage(event.data);
          };

          this.ws.onerror = (error) => {
            this._log('❌ WebSocket error', error);
            this._callHook('onError', error);
            if (!this.connected) {
              reject(error);
            }
          };

          this.ws.onclose = (event) => {
            this.connected = false;
            this._log('⚠️ Disconnected', {
              code: event.code,
              reason: event.reason,
              wasClean: event.wasClean
            });

            const reason = {
              code: event.code,
              reason: event.reason,
              wasClean: event.wasClean
            };

            this._callHook('onDisconnected', reason);

            // Auto-reconnect if enabled
            if (this.options.autoReconnect && event.code !== 1000) {
              this._scheduleReconnect();
            }
          };

        } catch (error) {
          this._log('💥 Connection failed', error);
          this._callHook('onError', error);
          reject(error);
        }
      });
    }

    /**
     * Disconnect from the server
     */
    disconnect() {
      if (this.ws) {
        this.options.autoReconnect = false; // Disable auto-reconnect
        this.connected = false;
        this.ws.close(1000, 'Client disconnect');
        this._log('🔌 Disconnected by client');
      }
    }

    /**
     * Check if connected
     * @returns {boolean}
     */
    isConnected() {
      return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Schedule reconnection attempt
     * @private
     */
    _scheduleReconnect() {
      this.reconnectAttempt++;
      const delay = this.options.reconnectDelay;
      
      this._log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempt})...`);
      
      setTimeout(() => {
        this._log('🔄 Reconnecting...');
        this.connect().catch(err => {
          this._log('❌ Reconnect failed', err);
        });
      }, delay);
    }

    // ═══════════════════════════════════════════════════════════
    // Message Handling
    // ═══════════════════════════════════════════════════════════

    /**
     * Handle incoming message
     * @private
     */
    _handleMessage(data) {
      try {
        const message = JSON.parse(data);
        this._log('📨 Received message', message);

        // Call general message hook
        this._callHook('onMessage', message);

        // Check if this is a response to a request
        const requestId = message._requestId;
        if (requestId !== undefined && this.callbacks.has(requestId)) {
          const callback = this.callbacks.get(requestId);
          this.callbacks.delete(requestId);

          // Clear timeout
          if (callback.timeoutId) {
            clearTimeout(callback.timeoutId);
          }

          // Resolve or reject based on response
          if (message.error) {
            callback.reject(new Error(message.error));
          } else {
            callback.resolve(message.result);
          }
          return;
        }
        
        // If no requestId but has result/error, check if we have a pending callback
        // (for backends that don't echo requestId)
        if ((message.result !== undefined || message.error !== undefined) && this.callbacks.size > 0) {
          // Get the oldest pending callback (FIFO)
          const [oldestId, callback] = this.callbacks.entries().next().value;
          this.callbacks.delete(oldestId);
          
          // Clear timeout
          if (callback.timeoutId) {
            clearTimeout(callback.timeoutId);
          }
          
          // Resolve or reject
          if (message.error) {
            callback.reject(new Error(message.error));
          } else {
            callback.resolve(message.result);
          }
          return;
        }

        // Check for specific event types
        if (message.event === 'input_response') {
          // This is handled internally by zDisplay
          return;
        }

        // Handle connection info from server (v1.5.4+)
        if (message.event === 'connection_info') {
          this.serverInfo = message.data;
          this._log('✅ Server info received', this.serverInfo);
          this._callHook('onServerInfo', this.serverInfo);
          return;
        }

        // Check for display events
        if (message.event === 'display' || message.type === 'display') {
          this._callHook('onDisplay', message.data || message);
          return;
        }

        // Check for input requests
        if (message.event === 'input_request' || message.type === 'input_request') {
          this._callHook('onInput', message);
          return;
        }

        // Otherwise, treat as broadcast
        this._handleBroadcast(message);

      } catch (error) {
        this._log('❌ Failed to parse message', { data, error });
        this._callHook('onError', error);
      }
    }

    /**
     * Handle broadcast message
     * @private
     */
    _handleBroadcast(message) {
      this._log('📢 Broadcast received', message);
      this._callHook('onBroadcast', message);
    }

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

      const requestId = this.requestId++;
      payload._requestId = requestId;

      const timeoutMs = timeout || this.options.timeout;

      return new Promise((resolve, reject) => {
        // Store callback
        const callback = { resolve, reject };

        // Set timeout
        callback.timeoutId = setTimeout(() => {
          if (this.callbacks.has(requestId)) {
            this.callbacks.delete(requestId);
            reject(new Error(`Request timeout after ${timeoutMs}ms`));
          }
        }, timeoutMs);

        this.callbacks.set(requestId, callback);

        // Send message
        const message = JSON.stringify(payload);
        this._log('📤 Sending message', payload);
        this.ws.send(message);
      });
    }

    /**
     * Send input response to server
     * @param {string} requestId - Request ID from input event
     * @param {any} value - Input value
     */
    sendInputResponse(requestId, value) {
      if (!this.isConnected()) {
        this._log('❌ Cannot send input response: not connected');
        return;
      }

      const response = {
        event: 'input_response',
        requestId: requestId,
        value: value
      };

      this.ws.send(JSON.stringify(response));
      this._log('📤 Sent input response', response);
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
        zKey: `^Create ${model}`,
        action: 'create',
        model: model,
        data: data
      });
    }

    /**
     * Read records
     * @param {string} model - Table/model name
     * @param {Object} filters - WHERE conditions (optional)
     * @param {Object} options - Additional options (fields, order_by, limit, offset, cache_ttl, no_cache)
     * @returns {Promise<Array>}
     */
    async read(model, filters = null, options = {}) {
      const payload = {
        zKey: `^List ${model}`,
        action: 'read',
        model: model
      };

      if (filters) payload.where = filters;
      if (options.fields) payload.fields = options.fields;
      if (options.order_by) payload.order_by = options.order_by;
      if (options.limit !== undefined) payload.limit = options.limit;
      if (options.offset !== undefined) payload.offset = options.offset;
      
      // Query caching options (v1.5.4+)
      if (options.cache_ttl !== undefined) payload.cache_ttl = options.cache_ttl;
      if (options.no_cache) payload.no_cache = true;

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
      // Convert ID to filter dict
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        zKey: `^Update ${model}`,
        action: 'update',
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
      // Convert ID to filter dict
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        zKey: `^Delete ${model}`,
        action: 'delete',
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
    // Schema Caching & Server Info (v1.5.4+)
    // ═══════════════════════════════════════════════════════════

    /**
     * Get schema for a model (cached client-side)
     * @param {string} model - Model name
     * @returns {Promise<Object>} Schema object
     */
    async getSchema(model) {
      // Check client-side cache first
      if (this.schemaCache.has(model)) {
        this._log('📦 Schema cache hit:', model);
        return this.schemaCache.get(model);
      }

      // Request from server (which also uses cache)
      this._log('📥 Requesting schema from server:', model);
      const schema = await this.send({
        action: 'get_schema',
        model: model
      });

      // Cache on client side
      this.schemaCache.set(model, schema);
      return schema;
    }

    /**
     * Get cache statistics from server
     * @returns {Promise<Object>} Cache stats (schema_cache and query_cache)
     */
    async getCacheStats() {
      return this.send({ action: 'cache_stats' });
    }

    /**
     * Clear server-side cache (both schema and query caches)
     * @returns {Promise<Object>} Result with stats
     */
    async clearServerCache() {
      // Also clear client cache
      this.schemaCache.clear();
      return this.send({ action: 'clear_cache' });
    }
    
    /**
     * Set query cache TTL on server
     * @param {number} ttl - Time to live in seconds
     * @returns {Promise<string>} Confirmation message
     */
    async setQueryCacheTTL(ttl) {
      return this.send({ action: 'set_query_cache_ttl', ttl: ttl });
    }

    /**
     * Clear client-side cache only
     */
    clearClientCache() {
      this.schemaCache.clear();
      this._log('🗑️ Client cache cleared');
    }

    /**
     * Get server info (received on connection)
     * @returns {Object|null} Server info or null if not connected
     */
    getServerInfo() {
      return this.serverInfo;
    }

    // ═══════════════════════════════════════════════════════════
    // Auto-Discovery API (v1.5.4+)
    // ═══════════════════════════════════════════════════════════

    /**
     * Discover available models and operations
     * @returns {Promise<Object>} Discovery result with models array
     */
    async discover() {
      const result = await this.send({ action: 'discover' });
      this._log('📋 Discovered models:', result);
      return result;
    }

    /**
     * Introspect a specific model to get its schema
     * @param {string} model - Model name
     * @returns {Promise<Object>} Model metadata including schema
     */
    async introspect(model) {
      return this.send({ action: 'introspect', model: model });
    }

    /**
     * Auto-generate CRUD UI for a model
     * @param {string} model - Model name
     * @param {string|HTMLElement} container - Container for UI
     * @param {Object} options - Options (title, operations)
     * @returns {Promise<void>}
     */
    async autoUI(model, container, options = {}) {
      const element = typeof container === 'string' ? document.querySelector(container) : container;
      if (!element) {
        this._log('❌ Container not found:', container);
        return;
      }

      // Get model metadata
      const modelInfo = await this.introspect(model);
      const schema = modelInfo.schema || {};
      const fields = schema.fields || {};

      // Create UI title
      const title = options.title || `${model.charAt(0).toUpperCase() + model.slice(1)} Manager`;
      element.innerHTML = `<h2 style="font-size: 2em; margin-bottom: 1.5rem;">${title}</h2>`;

      // Create action buttons
      const operations = options.operations || ['list', 'create'];
      const buttonsDiv = document.createElement('div');
      buttonsDiv.className = 'zMenu';
      buttonsDiv.style.marginBottom = '2rem';

      if (operations.includes('list')) {
        const listBtn = document.createElement('button');
        listBtn.className = 'zoloButton zBtn-primary';
        listBtn.textContent = `📋 List ${model}`;
        listBtn.onclick = async () => {
          const data = await this.read(model);
          const tableDiv = document.createElement('div');
          element.appendChild(tableDiv);
          this.renderTable(data, tableDiv);
        };
        buttonsDiv.appendChild(listBtn);
      }

      if (operations.includes('create')) {
        const createBtn = document.createElement('button');
        createBtn.className = 'zoloButton zBtn-success';
        createBtn.textContent = `➕ Create ${model}`;
        createBtn.onclick = () => {
          // Auto-generate form from schema
          const formFields = Object.entries(fields).map(([name, fieldInfo]) => ({
            name: name,
            label: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            type: this._inferFieldType(fieldInfo),
            required: fieldInfo.required || false
          }));

          const formDiv = document.createElement('div');
          element.appendChild(formDiv);
          this.renderForm(formFields, formDiv, async (data) => {
            await this.create(model, data);
            this.renderMessage(`✅ ${model} created successfully!`, 'success', element);
          });
        };
        buttonsDiv.appendChild(createBtn);
      }

      element.appendChild(buttonsDiv);

      // Create content area
      const contentDiv = document.createElement('div');
      contentDiv.id = 'autoui-content';
      element.appendChild(contentDiv);

      this._log('✅ Auto-UI generated for:', model);
    }

    /**
     * Infer HTML input type from field info
     * @private
     */
    _inferFieldType(fieldInfo) {
      const type = (fieldInfo.type || '').toLowerCase();
      if (type.includes('int') || type.includes('number')) return 'number';
      if (type.includes('email')) return 'email';
      if (type.includes('date')) return 'date';
      if (type.includes('bool')) return 'checkbox';
      if (type.includes('text') || type.includes('long')) return 'textarea';
      return 'text';
    }

    // ═══════════════════════════════════════════════════════════
    // zTheme Integration
    // ═══════════════════════════════════════════════════════════

    /**
     * Load zTheme CSS files
     * @param {string} baseUrl - Base URL for CSS files (optional, auto-detected)
     */
    loadTheme(baseUrl = null) {
      if (this.themeLoaded) {
        this._log('⚠️ zTheme already loaded, skipping...');
        return;
      }

      const themeUrl = baseUrl || this._detectThemeBaseUrl();
      this._log('🎨 Loading zTheme from:', themeUrl);

      const cssFiles = [
        'css/css_vars.css',
        'css/zMain.css',
        'css/zButtons.css',
        'css/zTables.css',
        'css/zInputs.css',
        'css/zContainers.css',
        'css/zTypography.css',
        'css/zAlerts.css',
        'css/zModal.css',
        'css/zNav.css',
        'css/zPanels.css',
        'css/zSpacing.css',
        'css/zEffects.css'
      ];

      cssFiles.forEach(file => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${themeUrl}/${file}`;
        link.dataset.ztheme = 'true';
        link.onerror = () => {
          this._log(`⚠️ Failed to load: ${file}`);
        };
        document.head.appendChild(link);
      });

      this.themeLoaded = true;
      this._log('✅ zTheme loaded');
    }

    /**
     * Detect base URL for zTheme CSS files
     * @private
     * @returns {string}
     */
    _detectThemeBaseUrl() {
      // Try to detect from current script location
      const scripts = document.getElementsByTagName('script');
      for (let script of scripts) {
        if (script.src && script.src.includes('bifrost_client.js')) {
          // Extract base path and navigate to zTheme
          const basePath = script.src.substring(0, script.src.lastIndexOf('/'));
          return basePath.replace(
            '/zComm/zComm_modules/zBifrost',
            '/zTheme'
          );
        }
      }

      // Fallback to GitHub CDN
      return 'https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zTheme';
    }

    // ═══════════════════════════════════════════════════════════
    // Auto-Rendering Methods
    // ═══════════════════════════════════════════════════════════

    /**
     * Render data as a table with zTheme styling
     * @param {Array} data - Array of objects to render
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Object} options - Rendering options
     */
    renderTable(data, container, options = {}) {
      const element = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;

      if (!element) {
        this._log('❌ Container not found:', container);
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        element.innerHTML = '<p class="zEmpty">No data to display</p>';
        return;
      }

      // Extract columns from first row
      const columns = Object.keys(data[0]);

      let html = '<table class="zTable zTable-striped zTable-hover">';
      
      // Table header
      html += '<thead><tr>';
      columns.forEach(col => {
        html += `<th>${this._formatColumnName(col)}</th>`;
      });
      html += '</tr></thead>';

      // Table body
      html += '<tbody>';
      data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
          html += `<td>${this._escapeHtml(row[col])}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table>';

      element.innerHTML = html;
      this._log('✅ Table rendered', { rows: data.length, columns: columns.length });
    }

    /**
     * Render a menu with buttons
     * @param {Array} items - Array of menu items {label, action, icon}
     * @param {string|HTMLElement} container - Container selector or element
     */
    renderMenu(items, container) {
      const element = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;

      if (!element) {
        this._log('❌ Container not found:', container);
        return;
      }

      let html = '<div class="zMenu">';
      items.forEach((item, index) => {
        const icon = item.icon || '';
        const variant = item.variant || '';
        html += `<button class="zoloButton ${variant}" data-action="${index}">
          ${icon} ${item.label}
        </button>`;
      });
      html += '</div>';

      element.innerHTML = html;

      // Attach event listeners
      element.querySelectorAll('button[data-action]').forEach((btn, index) => {
        btn.addEventListener('click', () => {
          if (items[index].action) {
            items[index].action();
          }
        });
      });

      this._log('✅ Menu rendered', { items: items.length });
    }

    /**
     * Render a form with zTheme styling
     * @param {Array} fields - Array of field definitions
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Function} onSubmit - Submit handler
     */
    renderForm(fields, container, onSubmit) {
      const element = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;

      if (!element) {
        this._log('❌ Container not found:', container);
        return;
      }

      let html = '<form class="zForm">';
      
      fields.forEach(field => {
        html += '<div class="zForm-group">';
        html += `<label for="${field.name}">${field.label}</label>`;
        
        if (field.type === 'textarea') {
          html += `<textarea id="${field.name}" name="${field.name}" 
                    class="zInput" ${field.required ? 'required' : ''}
                    placeholder="${field.placeholder || ''}"></textarea>`;
        } else {
          html += `<input type="${field.type || 'text'}" id="${field.name}" 
                   name="${field.name}" class="zInput" 
                   ${field.required ? 'required' : ''}
                   placeholder="${field.placeholder || ''}">`;
        }
        
        html += '</div>';
      });

      html += '<button type="submit" class="zoloButton zBtn-primary">Submit</button>';
      html += '</form>';

      element.innerHTML = html;

      // Attach submit handler
      const form = element.querySelector('form');
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        if (onSubmit) {
          onSubmit(data);
        }
      });

      this._log('✅ Form rendered', { fields: fields.length });
    }

    /**
     * Render a message/alert
     * @param {string} text - Message text
     * @param {string} type - Message type (success, error, warning, info)
     * @param {string|HTMLElement} container - Container selector or element
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    renderMessage(text, type = 'info', container, duration = 5000) {
      const element = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;

      if (!element) {
        this._log('❌ Container not found:', container);
        return;
      }

      const typeClass = {
        'success': 'zAlert-success',
        'error': 'zAlert-danger',
        'warning': 'zAlert-warning',
        'info': 'zAlert-info'
      }[type] || 'zAlert-info';

      const msgDiv = document.createElement('div');
      msgDiv.className = `zAlert ${typeClass}`;
      msgDiv.textContent = text;

      element.insertBefore(msgDiv, element.firstChild);

      if (duration > 0) {
        setTimeout(() => msgDiv.remove(), duration);
      }

      this._log('✅ Message rendered', { type, text });
    }

    // ═══════════════════════════════════════════════════════════
    // Utility Methods
    // ═══════════════════════════════════════════════════════════

    /**
     * Format column name for display
     * @private
     */
    _formatColumnName(name) {
      return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Escape HTML to prevent XSS
     * @private
     */
    _escapeHtml(text) {
      if (text === null || text === undefined) return '';
      const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
      };
      return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Call a hook if it exists
     * @private
     */
    _callHook(hookName, ...args) {
      const hook = this.options.hooks[hookName];
      if (typeof hook === 'function') {
        try {
          hook(...args);
        } catch (error) {
          this._log(`❌ Error in ${hookName} hook:`, error);
        }
      }
    }

    /**
     * Log message if debug enabled
     * @private
     */
    _log(message, ...args) {
      if (this.options.debug) {
        console.log(`[BifrostClient] ${message}`, ...args);
      }
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Export
  // ═══════════════════════════════════════════════════════════

  return BifrostClient;
}));

