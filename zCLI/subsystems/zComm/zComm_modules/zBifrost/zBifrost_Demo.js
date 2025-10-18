class zBifrost {
  /**
   * Create a new zBifrost client.
   * @param {string} url - WebSocket server URL (default: ws://127.0.0.1:56891)
   * @param {string|null} token - Authentication token (optional)
   * @param {Object} options - Additional options
   */
  constructor(url = 'ws://127.0.0.1:56891', token = null, options = {}) {
    this.url = url;
    this.token = token;
    this.options = options;
    
    this.ws = null;
    this.connected = false;
    this.callbacks = new Map();
    this.broadcastListeners = [];
    this.requestId = 0;
  }

  // ═══════════════════════════════════════════════════════════
  // Connection Management
  // ═══════════════════════════════════════════════════════════

  /**
   * Connect to zBifrost WebSocket server.
   * @returns {Promise<void>}
   */
  async connect() {
    return new Promise((resolve, reject) => {
      // Add token to URL if provided
      const connectUrl = this.token 
        ? `${this.url}?token=${this.token}` 
        : this.url;
      
      console.log(`[zBifrost] 🌈 Connecting to ${this.url}...`);
      
      this.ws = new WebSocket(connectUrl);
      
      this.ws.onopen = () => {
        this.connected = true;
        console.log('[zBifrost] ✅ Connected to server');
        resolve();
      };
      
      this.ws.onerror = (error) => {
        console.error('[zBifrost] ❌ Connection error:', error);
        reject(error);
      };
      
      this.ws.onmessage = (event) => {
        this._handleMessage(event.data);
      };
      
      this.ws.onclose = (event) => {
        this.connected = false;
        console.log(`[zBifrost] 🚪 Disconnected (code: ${event.code})`);
        
        if (this.options.autoReconnect) {
          console.log('[zBifrost] 🔄 Reconnecting...');
          setTimeout(() => this.connect(), 2000);
        }
      };
    });
  }

  /**
   * Disconnect from server.
   */
  disconnect() {
    if (this.ws) {
      this.connected = false;
      this.ws.close();
      console.log('[zBifrost] 🚪 Disconnected');
    }
  }

  // ═══════════════════════════════════════════════════════════
  // CRUD Operations - Simplified API
  // ═══════════════════════════════════════════════════════════

  /**
   * Create a new record.
   * @param {string} model - Table/model name (e.g., 'Users')
   * @param {Object} values - Field values
   * @returns {Promise<Object>} Created record
   */
  async create(model, values) {
    return this.send({
      zKey: `create_${model}`,
      zHorizontal: {
        action: 'create',
        model: model,
        values: values
      }
    });
  }

  /**
   * Read records from database.
   * @param {string} model - Table/model name
   * @param {Object} filters - WHERE conditions (optional)
   * @param {Object} options - Additional options (fields, order_by, limit, offset)
   * @returns {Promise<Array>} List of records
   */
  async read(model, filters = null, options = {}) {
    const horizontal = {
      action: 'read',
      model: model
    };
    
    if (filters) horizontal.where = filters;
    if (options.fields) horizontal.fields = options.fields;
    if (options.order_by) horizontal.order_by = options.order_by;
    if (options.limit !== undefined) horizontal.limit = options.limit;
    if (options.offset !== undefined) horizontal.offset = options.offset;
    
    return this.send({
      zKey: `read_${model}`,
      zHorizontal: horizontal
    });
  }

  /**
   * Update record(s).
   * @param {string} model - Table/model name
   * @param {number|Object} filters - ID or WHERE conditions
   * @param {Object} values - Fields to update
   * @returns {Promise<Object>} Update result
   */
  async update(model, filters, values) {
    // Convert ID to filter dict
    if (typeof filters === 'number') {
      filters = {id: filters};
    }
    
    return this.send({
      zKey: `update_${model}`,
      zHorizontal: {
        action: 'update',
        model: model,
        where: filters,
        values: values
      }
    });
  }

  /**
   * Delete record(s).
   * @param {string} model - Table/model name
   * @param {number|Object} filters - ID or WHERE conditions
   * @returns {Promise<Object>} Delete result
   */
  async delete(model, filters) {
    // Convert ID to filter dict
    if (typeof filters === 'number') {
      filters = {id: filters};
    }
    
    return this.send({
      zKey: `delete_${model}`,
      zHorizontal: {
        action: 'delete',
        model: model,
        where: filters
      }
    });
  }

  /**
   * Upsert (insert or update) a record.
   * @param {string} model - Table/model name
   * @param {Object} values - Field values
   * @param {Array} conflictFields - Fields to check for conflicts
   * @returns {Promise<Object>} Upserted record
   */
  async upsert(model, values, conflictFields = null) {
    const horizontal = {
      action: 'upsert',
      model: model,
      values: values
    };
    
    if (conflictFields) {
      horizontal.conflict_fields = conflictFields;
    }
    
    return this.send({
      zKey: `upsert_${model}`,
      zHorizontal: horizontal
    });
  }

  // ═══════════════════════════════════════════════════════════
  // Advanced Operations
  // ═══════════════════════════════════════════════════════════

  /**
   * Execute a zFunc command.
   * @param {string} funcCall - zFunc command string
   * @returns {Promise<any>} Function execution result
   */
  async zFunc(funcCall) {
    return this.send({
      zKey: 'zFunc',
      zHorizontal: funcCall
    });
  }

  /**
   * Navigate to a zLink path.
   * @param {string} linkPath - zLink navigation path
   * @returns {Promise<any>} Navigation result
   */
  async zLink(linkPath) {
    return this.send({
      zKey: 'zLink',
      zHorizontal: `zLink(${linkPath})`
    });
  }

  /**
   * Execute a zOpen command.
   * @param {string} openCommand - zOpen command string
   * @returns {Promise<any>} Command execution result
   */
  async zOpen(openCommand) {
    return this.send({
      zKey: 'zOpen',
      zHorizontal: `zOpen(${openCommand})`
    });
  }

  // ═══════════════════════════════════════════════════════════
  // Raw Send/Receive
  // ═══════════════════════════════════════════════════════════

  /**
   * Send a message and wait for response.
   * @param {Object} payload - Message payload (must include zKey and zHorizontal)
   * @param {number} timeout - Response timeout in milliseconds (default: 30000)
   * @returns {Promise<any>} Server response result
   */
  async send(payload, timeout = 30000) {
    if (!this.connected || !this.ws) {
      throw new Error('Not connected to server. Call connect() first.');
    }
    
    // Add request ID for correlation
    const requestId = this.requestId++;
    payload._requestId = requestId;
    
    return new Promise((resolve, reject) => {
      // Store callback
      this.callbacks.set(requestId, {resolve, reject});
      
      // Set timeout
      const timeoutId = setTimeout(() => {
        if (this.callbacks.has(requestId)) {
          this.callbacks.delete(requestId);
          reject(new Error(`Request timeout after ${timeout}ms`));
        }
      }, timeout);
      
      // Store timeout ID to clear it on response
      this.callbacks.get(requestId).timeoutId = timeoutId;
      
      // Send message
      const message = JSON.stringify(payload);
      if (this.options.debug) {
        console.log('[zBifrost] 📤 Sending:', message);
      }
      this.ws.send(message);
    });
  }

  // ═══════════════════════════════════════════════════════════
  // Broadcast Listening
  // ═══════════════════════════════════════════════════════════

  /**
   * Register a callback for broadcast messages.
   * @param {Function} callback - Function to call when broadcast received
   */
  onBroadcast(callback) {
    this.broadcastListeners.push(callback);
    if (this.options.debug) {
      console.log('[zBifrost] 📻 Broadcast listener registered');
    }
  }

  /**
   * Remove a broadcast listener.
   * @param {Function} callback - Callback to remove
   */
  removeBroadcastListener(callback) {
    const index = this.broadcastListeners.indexOf(callback);
    if (index > -1) {
      this.broadcastListeners.splice(index, 1);
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Internal Methods
  // ═══════════════════════════════════════════════════════════

  /**
   * Handle incoming message.
   * @private
   */
  _handleMessage(data) {
    try {
      const message = JSON.parse(data);
      
      if (this.options.debug) {
        console.log('[zBifrost] 📥 Received:', data);
      }
      
      // Check if it's a response to our request
      const requestId = message._requestId;
      if (requestId !== undefined && this.callbacks.has(requestId)) {
        const callback = this.callbacks.get(requestId);
        this.callbacks.delete(requestId);
        
        // Clear timeout
        if (callback.timeoutId) {
          clearTimeout(callback.timeoutId);
        }
        
        if (message.error) {
          callback.reject(new Error(message.error));
        } else {
          callback.resolve(message.result);
        }
      } else {
        // It's a broadcast message
        this._handleBroadcast(message);
      }
    } catch (e) {
      console.error('[zBifrost] ❌ Failed to parse message:', e);
    }
  }

  /**
   * Handle broadcast message.
   * @private
   */
  _handleBroadcast(message) {
    if (this.options.debug) {
      console.log('[zBifrost] 📻 Broadcast:', message);
    }
    
    for (const listener of this.broadcastListeners) {
      try {
        listener(message);
      } catch (e) {
        console.error('[zBifrost] ❌ Broadcast listener error:', e);
      }
    }
  }
}

// ═══════════════════════════════════════════════════════════
// Convenience function
// ═══════════════════════════════════════════════════════════

/**
 * Create and connect a zBifrost client.
 * @param {string} url - WebSocket server URL
 * @param {string|null} token - Authentication token
 * @param {Object} options - Additional options
 * @returns {Promise<zBifrost>} Connected client
 */
async function createClient(url = 'ws://127.0.0.1:56891', token = null, options = {}) {
  const client = new zBifrost(url, token, options);
  await client.connect();
  return client;
}

// ═══════════════════════════════════════════════════════════
// Export for different module systems
// ═══════════════════════════════════════════════════════════

// ES6 modules
export { zBifrost, createClient };
export default zBifrost;

// CommonJS (Node.js)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { zBifrost, createClient };
  module.exports.default = zBifrost;
}

// Global browser variable
if (typeof window !== 'undefined') {
  window.zBifrost = zBifrost;
  window.createClient = createClient;
}
