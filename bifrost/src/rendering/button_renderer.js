/**
 * ═══════════════════════════════════════════════════════════════
 * Button Renderer - Interactive Button Input Events
 * ═══════════════════════════════════════════════════════════════
 * 
 * ⚠️  NOTE: This renderer was created OUT OF ORDER during Sprint 2.
 *     It violates "primitives first" / "Terminal first" philosophy.
 *     Will be REVISITED and potentially REWORKED in Micro-Step 8
 *     after simpler renderers (text, header, alert, list, table)
 *     are complete and establish the proper patterns.
 * 
 * Renders button input events from zCLI backend. Creates interactive
 * button elements with zTheme styling and WebSocket response handling.
 * 
 * @module rendering/button_renderer
 * @layer 3
 * @pattern Strategy (single event type)
 * 
 * Dependencies:
 * - Layer 2: dom_utils.js, ztheme_utils.js
 * 
 * Exports:
 * - ButtonRenderer: Class for rendering button events
 * 
 * Example:
 * ```javascript
 * import ButtonRenderer from './button_renderer.js';
 * 
 * const renderer = new ButtonRenderer(logger, client);
 * renderer.render({
 *   label: 'Submit',
 *   action: 'process_form',
 *   color: 'primary',
 *   requestId: '123'
 * }, 'zVaF');
 * ```
 */

// ─────────────────────────────────────────────────────────────────
// Imports
// ─────────────────────────────────────────────────────────────────
import { 
  createElement, 
  createTextNode,
  appendChildren,
  replaceElement,
  setAttributes 
} from '../utils/dom_utils.js';

import { 
  getButtonColorClass,
  getButtonSizeClass,
  getButtonStyleClass,
  getButtonOutlineClass,
  getTextColorClass 
} from '../utils/ztheme_utils.js';

// ─────────────────────────────────────────────────────────────────
// Main Implementation
// ─────────────────────────────────────────────────────────────────

/**
 * Renders button input events for zDisplay
 * 
 * Handles the 'button' event type from zCLI backend, creating
 * interactive button elements with zTheme styling and WebSocket
 * response handling.
 * 
 * @class
 */
export default class ButtonRenderer {
  /**
   * Create a button renderer
   * @param {Object} logger - Logger instance for debugging
   * @param {Object} client - BifrostClient instance for sending responses
   */
  constructor(logger, client = null) {
    if (!logger) {
      throw new Error('[ButtonRenderer] logger is required');
    }
    
    this.logger = logger;
    this.client = client;
    this.defaultZone = 'zVaF-content';
  }

  /**
   * Render a button input request
   * 
   * @param {Object} data - Button configuration
   * @param {string} data.label - Button label text (or 'prompt')
   * @param {string} data.action - Action identifier (or '#' for placeholder)
   * @param {string} [data.color='primary'] - Button color (primary, danger, success, etc)
   * @param {string} [data.style='default'] - Button style variant (default, outline, text)
   * @param {string} [data.size='md'] - Button size (sm, md, lg)
   * @param {string} data.requestId - Request ID for response correlation
   * @param {string} zone - Target DOM element ID
   * @returns {HTMLElement|null} Created button container, or null if zone not found
   */
  render(data, zone) {
    // Validate inputs
    if (!data) {
      this.logger.error('[ButtonRenderer] data is required');
      return null;
    }

    // Extract data (support both direct and nested formats)
    const requestId = data.requestId || data.data?.requestId;
    const label = data.label || data.prompt || data.data?.prompt || 'Click Me';
    const action = data.action || data.data?.action || null;
    const color = data.color || data.data?.color || 'primary';
    const style = data.style || data.data?.style || 'default';
    const size = data.size || data.data?.size || 'md';
    
    // Resolve target zone
    const targetZone = zone || data.target || this.defaultZone;
    const container = document.getElementById(targetZone);
    
    if (!container) {
      this.logger.error(`[ButtonRenderer] Zone not found: ${targetZone}`);
      return null;
    }

    this.logger.log('[ButtonRenderer] Rendering button:', { requestId, label, action, color, style, size });

    // Create button container
    const buttonContainer = this._createButtonContainer();
    
    // Create primary button
    const primaryButton = this._createButton(label, color, style, size);
    this._attachClickHandler(primaryButton, requestId, label, true, buttonContainer);
    
    // Create cancel button
    const cancelButton = this._createButton('Cancel', 'secondary', 'outline', size);
    this._attachClickHandler(cancelButton, requestId, label, false, buttonContainer);
    
    // Append buttons to container
    appendChildren(buttonContainer, [primaryButton, cancelButton]);
    
    // Add to page
    container.appendChild(buttonContainer);
    
    this.logger.log('[ButtonRenderer] Button rendered successfully');
    return buttonContainer;
  }

  /**
   * Create button container element
   * @private
   * @returns {HTMLElement} Container div
   */
  _createButtonContainer() {
    // ✅ Use ONLY zTheme classes - NO inline styles!
    const container = createElement('div', ['zD-flex', 'zAlign-center', 'zGap-3', 'zmy-3', 'zp-3']);
    
    return container;
  }

  /**
   * Create a single button element with zTheme classes
   * @private
   * @param {string} label - Button text
   * @param {string} color - Button color
   * @param {string} style - Button style variant
   * @param {string} size - Button size
   * @returns {HTMLElement} Button element
   */
  _createButton(label, color, style, size) {
    // Build class list based on style
    const classes = ['zBtn']; // Base zTheme button class
    
    // Handle outline style (uses special outline classes)
    if (style === 'outline' || style === 'outlined' || style === 'ghost') {
      const outlineClass = getButtonOutlineClass(color);
      classes.push(outlineClass);
      this.logger.log(`[ButtonRenderer] Outline button - color: ${color}, class: ${outlineClass}`);
    } else {
      // Regular solid buttons
      const colorClass = getButtonColorClass(color);
      classes.push(colorClass);
      this.logger.log(`[ButtonRenderer] Solid button - color: ${color}, class: ${colorClass}`);
      
      // Link style
      const styleClass = getButtonStyleClass(style);
      if (styleClass) {
        classes.push(styleClass);
        this.logger.log(`[ButtonRenderer] Link style - class: ${styleClass}`);
      }
    }
    
    // Add size class
    const sizeClass = getButtonSizeClass(size);
    if (sizeClass) {
      classes.push(sizeClass);
      this.logger.log(`[ButtonRenderer] Size - size: ${size}, class: ${sizeClass}`);
    }
    
    // Log final classes
    this.logger.log(`[ButtonRenderer] Final classes for "${label}":`, classes.join(' '));
    
    // Create button
    const button = createElement('button', classes, {
      type: 'button'
    });
    
    button.textContent = label;
    
    // ✅ NO inline styles - zTheme handles ALL styling including hover effects!
    
    return button;
  }

  /**
   * Attach click handler to button
   * @private
   * @param {HTMLElement} button - Button element
   * @param {string} requestId - Request ID for response
   * @param {string} originalLabel - Original button label
   * @param {boolean} value - Response value (true for primary, false for cancel)
   * @param {HTMLElement} container - Button container to replace
   */
  _attachClickHandler(button, requestId, originalLabel, value, container) {
    button.addEventListener('click', () => {
      this.logger.log(`[ButtonRenderer] Button clicked: ${button.textContent} (value: ${value})`);
      
      // Send response to backend via WebSocket
      this._sendResponse(requestId, value);
      
      // Show confirmation message
      const confirmation = this._createConfirmation(originalLabel, value);
      replaceElement(container, confirmation);
    });
  }

  /**
   * Send button response to backend
   * @private
   * @param {string} requestId - Request ID
   * @param {boolean} value - Response value
   */
  _sendResponse(requestId, value) {
    // Try to get connection from client or global window object
    const connection = this.client?.connection || window.bifrostClient?.connection;
    
    if (!connection) {
      this.logger.error('[ButtonRenderer] No WebSocket connection available');
      return;
    }
    
    try {
      connection.send(JSON.stringify({
        event: 'input_response',
        requestId: requestId,
        value: value
      }));
      
      this.logger.log('[ButtonRenderer] Response sent:', { requestId, value });
    } catch (error) {
      this.logger.error('[ButtonRenderer] Failed to send response:', error);
    }
  }

  /**
   * Create confirmation message after button click
   * @private
   * @param {string} label - Original button label
   * @param {boolean} value - Response value (true = clicked, false = cancelled)
   * @returns {HTMLElement} Confirmation paragraph
   */
  _createConfirmation(label, value) {
    // Get appropriate text color class
    const colorClass = value ? getTextColorClass('success') : getTextColorClass('info');
    
    // ✅ Use ONLY zTheme classes - NO inline styles!
    const confirmation = createElement('p', [colorClass, 'zm-0', 'zpy-2', 'zpx-3', 'zFw-bold']);
    
    // Set confirmation text
    const icon = value ? '✓' : '○';
    const action = value ? 'clicked' : 'cancelled';
    confirmation.textContent = `${icon} ${label} ${action}!`;
    
    return confirmation;
  }
}
