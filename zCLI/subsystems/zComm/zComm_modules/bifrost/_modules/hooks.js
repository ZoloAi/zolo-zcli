/**
 * ═══════════════════════════════════════════════════════════════
 * Hooks Module - Event Hook Management
 * ═══════════════════════════════════════════════════════════════
 */

export class HookManager {
  constructor(hooks = {}) {
    this.hooks = hooks;
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
        console.error(`[BifrostClient] Error in ${hookName} hook:`, error);
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

