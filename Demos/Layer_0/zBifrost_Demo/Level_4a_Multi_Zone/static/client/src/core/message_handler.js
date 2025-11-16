/**
 * ═══════════════════════════════════════════════════════════════
 * Message Handler Module - Message Processing & Correlation
 * ═══════════════════════════════════════════════════════════════
 */

export class MessageHandler {
  constructor(logger, hooks) {
    this.logger = logger;
    this.hooks = hooks;
    
    // Pass logger to hooks for better error handling
    if (this.hooks && typeof this.hooks.logger === 'undefined') {
      this.hooks.logger = logger;
    }
    
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
   * Validate outgoing message follows protocol
   * @private
   */
  _validateOutgoingMessage(payload) {
    // Warn if using deprecated 'action' field
    if (payload.action && !payload.event) {
      this.logger.warn(
        'Using deprecated "action" field. Please use "event" instead.',
        { action: payload.action }
      );
      // Auto-migrate: copy action to event
      payload.event = payload.action;
    }

    // Warn if message has both 'action' and 'event'
    if (payload.action && payload.event && payload.action !== payload.event) {
      this.logger.warn(
        'Message has both "action" and "event" fields with different values. Using "event".',
        { action: payload.action, event: payload.event }
      );
      delete payload.action;
    }
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
      
      // If message looks like a response but has no _requestId, log error
      if ((message.result !== undefined || message.error !== undefined) && this.callbacks.size > 0) {
        this.logger.error(
          'Received response without _requestId! Backend must echo _requestId in all responses.',
          { message, pendingRequests: this.callbacks.size }
        );
        // Don't try to correlate - this is a backend bug that must be fixed
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

      // Progress bar events
      if (message.event === 'progress_bar') {
        this.hooks.call('onProgressBar', message);
        return;
      }

      if (message.event === 'progress_update') {
        this.hooks.call('onProgressUpdate', message);
        return;
      }

      if (message.event === 'progress_complete') {
        this.hooks.call('onProgressComplete', message);
        return;
      }

      // Spinner events
      if (message.event === 'spinner_start') {
        this.hooks.call('onSpinnerStart', message);
        return;
      }

      if (message.event === 'spinner_stop') {
        this.hooks.call('onSpinnerStop', message);
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
    // Validate message follows protocol
    this._validateOutgoingMessage(payload);
    
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

