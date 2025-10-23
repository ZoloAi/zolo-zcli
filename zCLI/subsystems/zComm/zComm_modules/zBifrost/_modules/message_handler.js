/**
 * ═══════════════════════════════════════════════════════════════
 * Message Handler Module - Message Processing & Correlation
 * ═══════════════════════════════════════════════════════════════
 */

export class MessageHandler {
  constructor(logger, hooks) {
    this.logger = logger;
    this.hooks = hooks;
    
    this.requestId = 0;
    this.callbacks = new Map();
    this.timeout = 30000; // Default timeout
  }

  /**
   * Set timeout for requests
   */
  setTimeout(timeout) {
    this.timeout = timeout;
  }

  /**
   * Handle incoming message
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      this.logger.log('📨 Received message', message);

      // Call general message hook
      this.hooks.call('onMessage', message);

      // Check if this is a response to a request
      const requestId = message._requestId;
      if (requestId !== undefined && this.callbacks.has(requestId)) {
        this._handleResponse(requestId, message);
        return;
      }
      
      // If no requestId but has result/error, check if we have a pending callback (FIFO fallback)
      if ((message.result !== undefined || message.error !== undefined) && this.callbacks.size > 0) {
        const [oldestId, callback] = this.callbacks.entries().next().value;
        this._handleResponse(oldestId, message);
        return;
      }

      // Check for specific event types
      if (message.event === 'input_response') {
        return; // Handled internally by zDisplay
      }

      if (message.event === 'display' || message.type === 'display') {
        this.hooks.call('onDisplay', message.data || message);
        return;
      }

      if (message.event === 'input_request' || message.type === 'input_request') {
        this.hooks.call('onInput', message);
        return;
      }

      // Otherwise, treat as broadcast
      this._handleBroadcast(message);

    } catch (error) {
      this.logger.log('❌ Failed to parse message', { data, error });
      this.hooks.call('onError', error);
    }
  }

  /**
   * Send a message and wait for response
   */
  async send(payload, sendFn, timeout = null) {
    const requestId = this.requestId++;
    payload._requestId = requestId;

    const timeoutMs = timeout || this.timeout;

    return new Promise((resolve, reject) => {
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
      this.logger.log('📤 Sending message', payload);
      sendFn(message);
    });
  }

  /**
   * Handle response to a request
   * @private
   */
  _handleResponse(requestId, message) {
    const callback = this.callbacks.get(requestId);
    if (!callback) return;
    
    this.callbacks.delete(requestId);

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
  }

  /**
   * Handle broadcast message
   * @private
   */
  _handleBroadcast(message) {
    this.logger.log('📢 Broadcast received', message);
    this.hooks.call('onBroadcast', message);
  }

  /**
   * Send input response to server
   */
  sendInputResponse(requestId, value, sendFn) {
    const response = {
      event: 'input_response',
      requestId: requestId,
      value: value
    };

    sendFn(JSON.stringify(response));
    this.logger.log('📤 Sent input response', response);
  }
}

