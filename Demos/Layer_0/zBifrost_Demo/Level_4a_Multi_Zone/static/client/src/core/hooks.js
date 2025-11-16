/**
 * ═══════════════════════════════════════════════════════════════
 * Hooks Module - Event Hook Management
 * ═══════════════════════════════════════════════════════════════
 */

export class HookManager {
  constructor(hooks = {}, logger = null) {
    this.hooks = hooks;
    this.logger = logger;
    this.errorHandler = null; // Can be set to display errors in UI
  }

  /**
   * Set error handler for displaying errors in UI
   */
  setErrorHandler(handler) {
    this.errorHandler = handler;
  }

  /**
   * Call a hook if it exists
   */
  call(hookName, ...args) {
    const hook = this.hooks[hookName];
    if (typeof hook === 'function') {
      try {
        return hook(...args);
      } catch (error) {
        // Log to console
        console.error(`[BifrostClient] Error in ${hookName} hook:`, error);
        
        // Log via logger if available
        if (this.logger) {
          this.logger.error(`Error in ${hookName} hook:`, error);
        }
        
        // Display in UI if error handler is set
        if (this.errorHandler) {
          try {
            this.errorHandler({
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
        if (hookName !== 'onError' && this.hooks.onError) {
          try {
            this.hooks.onError(error);
          } catch (onErrorError) {
            console.error('[BifrostClient] onError hook failed:', onErrorError);
          }
        }
      }
    }
  }

  /**
   * Check if a hook is registered
   */
  has(hookName) {
    return typeof this.hooks[hookName] === 'function';
  }

  /**
   * Register a new hook
   */
  register(hookName, fn) {
    if (typeof fn === 'function') {
      this.hooks[hookName] = fn;
    }
  }

  /**
   * Unregister a hook
   */
  unregister(hookName) {
    delete this.hooks[hookName];
  }

  /**
   * Get all registered hooks
   */
  list() {
    return Object.keys(this.hooks);
  }
}

